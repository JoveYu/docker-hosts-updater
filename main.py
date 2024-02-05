import docker
import re
import os

FORMAT = '%s.docker'
MARKER = '#### DOCKER HOSTS UPDATER ####'
HOSTS_PATH = '/opt/hosts'


def listen():
    for event in docker.events(decode=True):
        if 'container' == event.get('Type') and event.get('Action') in ["start", "stop", "die"]:
            handle()


def scan():
    containers = []
    for container in docker.containers.list():
        ip = next(iter(container.attrs.get('NetworkSettings').get('Networks').values())).get('IPAddress')
        if container.status == 'running':
            containers.append({
                'ip': ip,
                'hosts': FORMAT % container.name,
            })

    return containers

def update():
    items = scan()
    f = open(HOSTS_PATH, 'r+')
    lines = []
    skip_lines = False
    for line in f.read().split('\n'):
        if line == MARKER:
            skip_lines = not skip_lines
            continue

        if not skip_lines:
            lines.append(line)

    if items:
        lines.append(MARKER)
        for item in items:
            line = '{} {}'.format(item['ip'], item['hosts'])
            lines.append(line)
            print(line)
        lines.append(MARKER)

    summary = '\n'.join(lines)

    f.seek(0)
    f.truncate()
    f.write(summary)
    f.close()


docker = docker.from_env()
update()
listen()
