#!/usr/bin/env python
import os
import subprocess
import time
import json
import sys
import docker

client = docker.from_env()

def restart():
    subprocess.check_call(["systemctl", "restart", "docker.service"])

def is_dockerd_up():
    return int(subprocess.check_output("docker ps 2>/dev/null | grep IMAGE | wc -l", shell=True)) > 0

def wait_for_dockerd_up():
    sys.stdout.write('Waiting for dockerd to come up ...')
    while not is_dockerd_up():
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write(" [DONE]\n")

def set_engine_label(label):
    daemonSettings = {
        "labels": [
            "node-purpose=" + label
        ]
    }
    daemon = open("/etc/docker/daemon.json", "w")
    daemon.write(json.dumps(daemonSettings, sort_keys=True, indent=4))
    daemon.close()
