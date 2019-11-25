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
admin_uid = pwd.getpwnam("admin").pw_uid
admin_gid = grp.getgrnam("admin").gr_gid
authorizedKeys = open("/home/admin/.ssh/authorized_keys","w")
authorizedKeys.write("""${authorized_keys}""")
authorizedKeys.close()
os.chmod("/home/admin/.ssh/authorized_keys", 0o600)
os.chown("/home/admin/.ssh/authorized_keys", admin_uid, admin_gid)

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
    payload = {'text': "VPN instance (${hostname}) has come up."}
    response = requests.post(url, data=json.dumps(payload), headers=headers)

