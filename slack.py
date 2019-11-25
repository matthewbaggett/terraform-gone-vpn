#!/usr/bin/env python
import json
import requests

webhook = None

def set_webhook(new_webhook):
    if new_webhook:
        webhook = new_webhook

def message(message):
    if webhook:
        print "Sending slack message: " + message
        headers = {'Content-type': 'application/json'}
        payload = {'text': message}
        response = requests.post(webhook, data=json.dumps(payload), headers=headers)
    else:
        print "Skipping sending slack message: " + message
