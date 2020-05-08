#!/bin/bash

function fail {
    printf '%s\n' "$1" >&2
    exit 1
}


echo "Install invenio-cli"
pip3 install invenio-cli || fail "Could not install invenio-cli"
export PATH=$PATH:~/.local/bin

echo "Init invenio"
invenio-cli init --flavour=RDM || fail "Could not init invenio"

# get invenio base directory in $directory
echo "Please select invenio directory:"
select directory in */; do break; done

echo "Copy certificate"
cp cert/* $directory/docker/nginx/

echo "Modify docker setup files"
chmod +x ./setup/docker/modify-docker-compose.py
python3 setup/docker/modify-docker-compose.py $directory || fail "Could not modify docker-compose"

cd $directory

echo "Fix dependency versions"
pip3 uninstall -y Werkzeug
pip3 install Werkzeug==0.16.1 jsonresolver==0.2.1

echo "Invenio start"
invenio-cli containerize || fail "Could not generate containers"
echo "Adding demo data"
invenio-cli demo --containers || fail "Could not add demo data"

echo "Setup finished"
