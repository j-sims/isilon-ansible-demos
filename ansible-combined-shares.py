#!/usr/bin/env python

import json
import yaml

sharesFilename = 'combined-shares.json'

with open(sharesFilename, 'r') as f:
    shares = json.load(f)

### For Loop to write out playbook for each cluster
for cluster in shares['clusters']:
    playbookFilename = 'playbook-combined-shares-%s.yml' % cluster['name']
    with open(playbookFilename, 'w') as playbook:
        play = [
            {
                'hosts': 'localhost',
                'name': 'Isilon New SMB share with URI module',
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
        for share in cluster['shares']:
            createshare = {
                 'name': 'make SMB share',
                 'uri': {
                     'body': {
                         'browsable': True,
                         'description': share['description'],
                         'name': share['name'],
                         'path': share['path'],
                         'create_path': True,
                         'permissions': share['permissions'],
                         'zone': share['zone']},
                     'body_format': 'json',
                     'headers': {'Cookie': 'isisessid={{ results_login.cookies.isisessid }}',
                     'X-CSRF-Token': '{{ results_login.cookies.isicsrf }}',
                     'referer': 'https://'+cluster['name']+':8080'},
                     'method': 'POST',
                     'status_code': 201,
                     'url': 'https://'+cluster['name']+':8080/platform/4/protocols/smb/shares',
                     'validate_certs': False,
                     }
                 }
            play[0]['tasks'].append(createshare)
        for quota in cluster['quotas']:
            createquota = {
                 'name': 'Create Quota',
                 'uri': {
                     'body': {
                         'include_snapshots': False,
                         'path': quota['path'],
                         'type': 'directory',
                         'force': False,
                         'thresholds_include_overhead': False,
                         'type': 'directory',
                         'thresholds': {
                             'hard': quota['thresholds']['hard'],
                             'soft': quota['thresholds']['soft'],
                             'soft_grace': quota['thresholds']['soft_grace']
                         }
                         },
                     'body_format': 'json',
                     'headers': {'Cookie': 'isisessid={{ results_login.cookies.isisessid }}',
                     'X-CSRF-Token': '{{ results_login.cookies.isicsrf }}',
                     'referer': 'https://'+cluster['name']+':8080'},
                     'method': 'POST',
                     'status_code': 201,
                     'url': 'https://'+cluster['name']+':8080/platform/1/quota/quotas',
                     'validate_certs': False,
                     }
                 }
            play[0]['tasks'].append(createquota)
        for schedule in cluster['snapshotschedules']:
            createschedule = {
                 'name': 'create snapshot schedule',
                 'uri': {
                     'body': {
                         'name': schedule['name'],
                         'path': schedule['path'],
                         'duration': schedule['duration'],
                         'pattern': schedule['pattern'],
                         'schedule': schedule['schedule'],
                         },
                     'body_format': 'json',
                     'headers': {'Cookie': 'isisessid={{ results_login.cookies.isisessid }}',
                     'X-CSRF-Token': '{{ results_login.cookies.isicsrf }}',
                     'referer': 'https://'+cluster['name']+':8080'},
                     'method': 'POST',
                     'status_code': 201,
                     'url': 'https://'+cluster['name']+':8080/platform/3/snapshot/schedules',
                     'validate_certs': False,
                     }
                 }
            play[0]['tasks'].append(createschedule)
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
