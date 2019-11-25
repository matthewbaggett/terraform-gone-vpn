#!/usr/bin/env python
import subprocess
import os
import pwd, grp

def init():
    subprocess.check_call(["systemctl", "daemon-reload"])
    subprocess.check_call(["systemctl", "enable", "docker.service"])
    subprocess.check_call(["systemctl", "start", "docker.service"])

def add_docker_user(user = 'admin'):
    subprocess.check_call(["usermod", "-a", "-G", "docker", user])

def create_swap(swapsize = 1):
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

def create_authorized_keys(keys, user = 'admin'):
    adminUID = pwd.getpwnam(user).pw_uid
    adminGID = grp.getgrnam(user).gr_gid
    adminSSHDir = "/home/" + user + "/.ssh"
    fileAuthorizedKeys = adminSSHDir + "/authorized_keys"
    if not os.path.isdir(adminSSHDir):
        os.mkdir(adminSSHDir)
        os.chown(adminSSHDir, adminUID, adminGID)
    authorizedKeys = open(fileAuthorizedKeys,"w")
    authorizedKeys.write(keys)
    authorizedKeys.close()
    os.chmod(fileAuthorizedKeys, 0o600)
    os.chown(fileAuthorizedKeys, adminUID, adminGID)

def set_hostname(hostname):
    subprocess.check_call(["hostnamectl", "set-hostname", hostname])
