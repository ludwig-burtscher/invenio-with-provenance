#!/usr/bin/python

import io
import yaml
import sys
import os


invenio_base = sys.argv[1]
docker_services_file = os.path.join(invenio_base, "docker-services.yml")

with open(docker_services_file, "r") as file:
    data = yaml.safe_load(file)

environment = data["services"]["app"]["environment"]

# set number of proxies to 1
for i, env in enumerate(environment):
    if env.startswith("INVENIO_WSGI_PROXIES"):
        environment[i] = "INVENIO_WSGI_PROXIES=1"
    if env.startswith("INVENIO_APP_ALLOWED_HOSTS"):
        environment.pop(i)
        
# add allowed hosts
with open("setup/docker/allowed_hosts.txt") as file:
    hosts = file.read().splitlines()
hostline = "INVENIO_APP_ALLOWED_HOSTS=" + "['" + "','".join(hosts) + "']"
environment.append(hostline)

with open(docker_services_file, "w") as file:
    yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
