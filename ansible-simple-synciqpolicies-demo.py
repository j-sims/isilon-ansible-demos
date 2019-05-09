#!/usr/bin/env python

import json
import yaml

syncpoliciesFilename = 'simple-synciqpolicies.json'

with open(syncpoliciesFilename, 'r') as f:
    syncpolicies = json.load(f)

### For Loop to write out playbook for each cluster
for cluster in syncpolicies['clusters']:
    playbookFilename = 'playbook-simple-synciqpolicies-%s.yml' % cluster['name']
    with open(playbookFilename, 'w') as playbook:
        play = [
            {
                'hosts': 'localhost',
                'name': 'Isilon New syniq policy with URI module',
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
        for policy in cluster['syncpolicies']:
            createpolicy = {
                 'name': 'Create Policy',
                 'uri': {
                     'body': {
                           "source_root_path": policy["source_root_path"],
                           "target_host": policy["target_host"],
                           "name": policy["name"],
                           "target_path": policy["target_path"],
                           "action": policy["action"],
                           "schedule": policy["schedule"],
                         },
                     'body_format': 'json',
                     'headers': {'Cookie': 'isisessid={{ results_login.cookies.isisessid }}',
                     'X-CSRF-Token': '{{ results_login.cookies.isicsrf }}',
                     'referer': 'https://'+cluster['name']+':8080'},
                     'method': 'POST',
                     'status_code': 201,
                     'url': 'https://'+cluster['name']+':8080/platform/3/sync/policies',
                     'validate_certs': False,
                     }
                 }
            play[0]['tasks'].append(createpolicy)
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
