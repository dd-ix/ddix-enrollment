#!/usr/bin/env python3

import configparser
import json
import re
import requests
import sys
from urllib.parse import urljoin

def get_headers(config):
    return {
        "authorization": f"Bearer {config['authentik']['APIToken']}",
    }

def get_url(config, path):
    return urljoin(config['authentik']['BaseURL'], path)

def create_invite(config, fixed_data={}):
    '''
    Creates an enrollment invite using the Authentik API. The `fixed_data`
    parameter should contain `username`, `name` and email fields.
    '''
    
    obj = {
       "expires" : "2024-02-05T14:40:00.000Z",
       "fixed_data" : fixed_data,
       "flow" : config['authentik']['InviteFlow'],
       "name" : f"enroll-{fixed_data['username']}",
       "single_use" : True,
    }
    x = requests.post(
        get_url(config, '/api/v3/stages/invitation/invitations/'),
        headers=get_headers(config),
        json=obj)
    print(f"{fixed_data['username']}\t{x.status_code}: {x.reason}", file=sys.stderr)

    if x.ok:
        # return invite UUID
        return x.json().get('pk')
    return None

def main():
    config = configparser.ConfigParser()
    config.read('enroll.ini')

    for line in sys.stdin:
        line = line.rstrip()
        m = re.match('^([^,]+),([^,]+),([^,]+)$', line)
        if m:
            enroll_data = {
                "username": m.group(1),
                "name": m.group(2),
                "email": m.group(3),
            }
            invite_uuid = create_invite(config, enroll_data)
            if invite_uuid:
                print(f"{line},{invite_uuid}")

if __name__ == '__main__':
    main()