#!/usr/bin/env python3

import configparser
import json
import re
import requests
from requests.auth import HTTPBasicAuth
import sys
from urllib.parse import urljoin

def get_auth(config):
    return HTTPBasicAuth(config['listmonk']['APIUser'], config['listmonk']['APIPass'])

def get_url(config, path):
    return urljoin(config['listmonk']['BaseURL'], path)

def create_subscriber(config, data):
    '''
    Uses the listmonk api to create the subscriber.
    '''
    
    if 'SubscribeLists' in config['listmonk']:
        lists = [int(x) for x in config['listmonk']['SubscribeLists'].split(',')]
    else:
        lists = []
    
    obj = {
        "email": data['email'],
        "name": data['name'],
        "lists": lists,
        "status": "enabled",
    }
    x = requests.post(
        get_url(config, '/api/subscribers'),
        auth=get_auth(config),
        headers={"Content-Type": "application/json; charset=utf-8"},
        json=obj)
   
def send_invite(config, data):
    '''
    Uses the listmonk api to send a transactional mail.
    '''

    create_subscriber(config, data)

    obj = {
       "subscriber_email": data['email'],
        "from_email": config['listmonk']['FromEmail'],
        "template_id": int(config['listmonk']['TemplateID']),
        "data": data,
        "content_type": "html"
    }
    x = requests.post(
        get_url(config, '/api/tx'),
        auth=get_auth(config),
        headers={"Content-Type": "application/json; charset=utf-8"},
        json=obj)
    if x.ok:
        print(f"{data['username']}\t{x.status_code}: {x.reason}", file=sys.stderr)
    else:
        print(f"{data['username']}\t{x.status_code}: {x.reason} {x.text}", file=sys.stderr)

def main():
    config = configparser.ConfigParser()
    config.read('enroll.ini')
    config.read('tokens.ini')

    for line in sys.stdin:
        line = line.rstrip()
        m = re.match('^([^,]+),([^,]+),([^,]+),([^,]+),([^,]+)$', line)
        if m:
            invite_data = {
                "username": m.group(1),
                "name": m.group(2),
                "email": m.group(3),
                "itoken": m.group(4),
                "expire": m.group(5),
            }
            send_invite(config, invite_data)
        else:
            print(f"ignoring line: {line}", file=sys.stderr)

if __name__ == '__main__':
    main()
