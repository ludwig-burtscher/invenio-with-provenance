#!/usr/bin/env python3

# Provstore credentials over ENV variables:
# Provstore username: PROVSTORE_USERNAME
# Provstore apikey: PROVSTORE_APIKEY

# exit codes:
# 0: All good - provstore document created successfully
# 1: No provstore credentials
# 2: Provstore document upload failed
# 3: No JSON command line arguments

import requests
import uuid
import json
import os
import sys


def push_json(prov_dict, username, apikey):
    url = "https://openprovenance.org/store/api/v0/documents/"
    authorization = "ApiKey {}:{}".format(username, apikey)
    body = {"rec_id": str(uuid.uuid4()), "public": False, "content": prov_dict}

    r = requests.post(url, headers={"Authorization": authorization}, json=body)
    if r.status_code is not 201:
        eprint("Statuscode: {}".format(r.status_code))
        eprint("Response:{}".format(r.text))
        exit(2)


def build_prov_json(session, permission, optional=None):
    #TODO implement
    #returns single dict representing the prov_json
    print(session)
    print(permission)
    print(optional)
    return {}


def eprint(*args, **kwargs):
    print(*args, file=open("/tmp/error.txt", "a+"), **kwargs)


if __name__ == "__main__":
    arglen = len(sys.argv)
    if arglen < 3 or arglen > 4:
        eprint("Two or three command line arguments are required")
        exit(3)

    with open("/tmp/test.txt", "a+") as f:
        f.write(str(sys.argv) + "\n")

    try:
        session = json.loads(sys.argv[1])
        permission = json.loads(sys.argv[2])
        optional = json.loads(sys.argv[3]) if arglen == 4 else None
    except:
        eprint("Command line arguments are not JSON")
        exit(3)

    provstore_username = os.getenv("PROVSTORE_USERNAME")
    provstore_apikey = os.getenv("PROVSTORE_APIKEY")
    if not provstore_username or not provstore_apikey:
        eprint("No PROVSTORE credentials found in env variables")
        exit(1)

    push_json(build_prov_json(session, permission, optional), provstore_username, provstore_apikey)
