#!/usr/bin/env python3

import configparser
from datetime import datetime, timedelta
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

def create_invite(config, expire, fixed_data={}):
    '''
    Creates an enrollment invite using the Authentik API. The `fixed_data`
    parameter should contain `username`, `name` and email fields.
    '''

    obj = {
       "expires" : expire,
       "fixed_data" : fixed_data,
       "flow" : config['authentik']['InviteFlow'],
       "name" : f"enroll-{fixed_data['username']}",
       "single_use" : True,
    }
    x = requests.post(
        get_url(config, '/api/v3/stages/invitation/invitations/'),
        headers=get_headers(config),
        json=obj)

    if x.ok:
        print(f"{fixed_data['username']}\t{x.status_code}: {x.reason}", file=sys.stderr)
        return x.json().get('pk')
    else:
        print(f"{fixed_data['username']}\t{x.status_code}: {x.reason} {x.text}", file=sys.stderr)
        return None

def main():
    config = configparser.ConfigParser()
    config.read('enroll.ini')
    config.read('tokens.ini')

    expire = datetime.now() + timedelta(days=1+int(config['authentik']['ExpireDays']))
    expire = expire.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"

    for line in sys.stdin:
        line = line.rstrip()
        m = re.match('^([^,]+),([^,]+),([^,]+)$', line)
        if m:
            enroll_data = {
                "username": m.group(1),
                "name": m.group(2),
                "email": m.group(3),
            }
            invite_token = create_invite(config, expire, enroll_data)
            if invite_token:
                print(f"{line},{invite_token},{expire}")
        else:
            print(f"ignoring line: {line}", file=sys.stderr)

if __name__ == '__main__':
    main()
