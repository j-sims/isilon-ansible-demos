#!/usr/bin/env python

import json
import yaml

sharesFilename = 'simple-exports.json'

with open(sharesFilename, 'r') as f:
    shares = json.load(f)

### For Loop to write out playbook for each cluster
for cluster in shares['clusters']:
    playbookFilename = 'playbook-simple-exports-%s.yml' % cluster['name']
    with open(playbookFilename, 'w') as playbook:
        play = [
            {
                'hosts': 'localhost',
                'name': 'Isilon New NFS Export with URI module',
                'tasks': [],
            }
        ]
        startsession = {
            'name': 'get isilon API session IDs',
            'register': 'results_login',
            'uri': {
                'body': {'password': cluster['password'],
                'services': ['platform', 'namespace'],
                'username': cluster['username']},
            'body_format': 'json',
            'method': 'POST',
            'status_code': 201,
            'url': 'https://' + cluster['name'] +':8080/session/1/session',
            'validate_certs': False }
            }
        play[0]['tasks'].append(startsession)
        for export in cluster['exports']:
            createexport = {
                 'name': 'make NFS Export',
                 'uri': {
                     'body': {
                         'description': export['description'],
                         'paths': export['paths'],
                         'zone': export['zone']},
                     'body_format': 'json',
                     'headers': {'Cookie': 'isisessid={{ results_login.cookies.isisessid }}',
                     'X-CSRF-Token': '{{ results_login.cookies.isicsrf }}',
                     'referer': 'https://'+cluster['name']+':8080'},
                     'method': 'POST',
                     'status_code': 201,
                     'url': 'https://'+cluster['name']+':8080/platform/4/protocols/nfs/exports',
                     'validate_certs': False,
                     }
                 }
            play[0]['tasks'].append(createexport)
        endsession = {
            'name': 'Delete isilon API session IDs',
            'register': 'results_DEL_cookie',
            'uri': {
                'headers': {
                    'Cookie': 'isisessid={{ results_login.cookies.isisessid }}',
                    'X-CSRF-Token': '{{ results_login.cookies.isicsrf }}',
                    'referer': 'https://'+cluster['name']+':8080',
                    },
                'method': 'DELETE',
                'status_code': 204,
                'url': 'https://'+cluster['name']+':8080/session/1/session',
                'validate_certs': False,
                }
            }
        play[0]['tasks'].append(endsession)
        yaml.safe_dump(play, playbook, default_flow_style=False)
