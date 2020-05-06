#!/bin/bash


# install invenio-cli and setup dependencies
pip install pyyaml
pipenv install invenio-cli

# init invenio
invenio-cli init --flavour=RDM

# get invenio base directory in $directory
echo "Please select invenio directory:"
select directory in */; do break; done

# copy certificate
cp cert/* $directory/docker/nginx/

# modify docker setup files
chmod +x ./setup/docker/modify-docker-compose.py
./setup/docker/modify-docker-compose.py $directory

cd $directory

# invenio start
invenio-cli containerize
invenio-cli demo --containers
