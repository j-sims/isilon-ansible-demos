#!/usr/bin/env python

import json
import yaml

snapshotschedulesFilename = 'simple-snapshotschedules.json'

with open(snapshotschedulesFilename, 'r') as f:
    snapshotschedules = json.load(f)

### For Loop to write out playbook for each cluster
for cluster in snapshotschedules['clusters']:
    playbookFilename = 'playbook-simple-snapshotschedules-%s.yml' % cluster['name']
    with open(playbookFilename, 'w') as playbook:
        play = [
            {
                'hosts': 'localhost',
                'name': 'Isilon New SMB schedule with URI module',
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
