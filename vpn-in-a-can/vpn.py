#!/usr/bin/env python
import boto3
from botocore.exceptions import NoCredentialsError
import os
import subprocess
import time
import json
import requests
import pwd
import grp

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])

    return int(uptime_seconds)

# Send a message to slack to announce that we've come up.
url = '${slack_hook}'
if url:
    headers = {'Content-type': 'application/json'}
    payload = {'text': "VPN instance (${hostname}) is trying to come up."}
    response = requests.post(url, data=json.dumps(payload), headers=headers)

# Load system daemons
subprocess.check_call(["systemctl", "daemon-reload"])
subprocess.check_call(["systemctl", "enable", "docker.service"])
subprocess.check_call(["systemctl", "start", "docker.service"])

# Add admin to docker group to call docker without sudo.
subprocess.check_call(["usermod", "-a", "-G", "docker", "admin"])

# Set values loaded by the template
swapsize = int('${swapsize}')

# Set the host name
subprocess.check_call(["hostnamectl", "set-hostname", '${hostname}'])

# Create Authorized Keys
adminUID = pwd.getpwnam("admin").pw_uid
adminGID = grp.getgrnam("admin").gr_gid
adminSSHDir = "/home/admin/.ssh"
fileAuthorizedKeys = adminSSHDir + "/authorized_keys.new"
if not os.path.isdir(adminSSHDir):
    os.mkdir(adminSSHDir)
    os.chown(adminSSHDir, adminUID, adminGID)
authorizedKeys = open(fileAuthorizedKeys,"w")
authorizedKeys.write("""${authorized_keys}""")
authorizedKeys.close()
os.chmod(fileAuthorizedKeys, 0o600)
os.chown(fileAuthorizedKeys, adminUID, adminGID)
os.rename(adminSSHDir + "/authorized_keys", adminSSHDir + "/authorized_keys.bak")
os.rename(adminSSHDir + "/authorized_keys.new", adminSSHDir + "/authorized_keys")

# Create Swap
if not os.path.isfile("/swapfile"):
    f = open("/swapfile", "wb")
    for i in xrange(swapsize * 1024):
        f.write("\0" * 1024 * 1024)
    f.close()
    os.chmod("/swapfile", 0o600)
    subprocess.check_output(["mkswap", "/swapfile"])
    f = open("/etc/fstab", "a")
    f.write("/swapfile none swap defaults 0 0\n")
    f.close()
    subprocess.check_output(["swapon", "-a"])

# Set up Docker Daemon with a label
daemonSettings = {
    "labels": [
        "node-purpose=vpn"
    ]
}
daemon = open("/etc/docker/daemon.json", "w")
daemon.write(json.dumps(daemonSettings, sort_keys=True, indent=4))
daemon.close()

# And restart docker
subprocess.check_call(["systemctl", "restart", "docker.service"])

# Send a message to slack to announce that we've come up.
url = '${slack_hook}'
if url:
    headers = {'Content-type': 'application/json'}
    payload = {'text': "VPN instance (${hostname}) has come up in " + str(get_uptime()) + " seconds."}
    response = requests.post(url, data=json.dumps(payload), headers=headers)

