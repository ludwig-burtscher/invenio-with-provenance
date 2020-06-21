#!/usr/bin/env python3

# Provstore credentials over ENV variables:
# Provstore username: PROVSTORE_USERNAME
# Provstore apikey: PROVSTORE_APIKEY

# exit codes:
# 0: All good - provstore document created successfully
# 1: No provstore credentials
# 2: Provstore document upload failed
# 3: Invalid command line arguments

import requests
import uuid
import json
import os
import sys
import time
import uuid
import datetime
from prov.model import ProvDocument


def push_json(prov_dict, username, apikey):
    url = "https://openprovenance.org/store/api/v0/documents/"
    authorization = "ApiKey {}:{}".format(username, apikey)
    body = {"rec_id": str(uuid.uuid4()), "public": False, "content": prov_dict}

    r = requests.post(url, headers={"Authorization": authorization}, json=body)
    if r.status_code is not 201:
        eprint("Statuscode: {}".format(r.status_code))
        eprint("Response:{}".format(r.text))
        exit(2)


def build_prov_json(o_user, s_action, o_record_before, o_record_after, args, kwargs):
    #returns single dict representing the prov_json
    
    user = parse_user(o_user)
    action = parse_action(s_action)
    action_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now()
    
    d = get_base_prov_document()
    
    
    if action == "read":
        record_id = parse_record_id_before(o_record_before)
        u = d.agent("user:{}".format(user))
        e = d.entity("record:{}".format(get_prov_record_id(record_id, parse_revision_after(o_record_after))))
        a = d.activity("action:{}_{}".format(action, action_id), timestamp)
        d.wasAssociatedWith(a, u)
        d.used(a, e)
    elif action == "create":
        record_id = parse_record_id_after(o_record_after)
        u = d.agent("user:{}".format(user))
        e = d.entity("record:{}".format(get_prov_record_id(record_id, "0")))
        a = d.activity("action:{}_{}".format(action, action_id), timestamp)
        d.wasAssociatedWith(a, u)
        d.wasGeneratedBy(e, a)
    elif action == "update":
        old_record_id = parse_record_id_before(o_record_before)
        new_record_id = parse_record_id_after(o_record_after)
        new_revision = parse_revision_after(o_record_after)
        old_revision = str(int(new_revision) - 1)
        u = d.agent("user:{}".format(user))
        old_e = d.entity("record:{}".format(get_prov_record_id(old_record_id, old_revision)))
        new_e = d.entity("record:{}".format(get_prov_record_id(new_record_id, new_revision)))
        a = d.activity("action:{}_{}".format(action, action_id), timestamp)
        d.wasAssociatedWith(a, u)
        d.wasDerivedFrom(new_e, old_e)
    elif action == "list":
        u = d.agent("user:{}".format(user))
        a = d.activity("action:{}_{}".format(action, action_id), timestamp)
        hits = json.loads(o_record_after["response"][0].replace("'", "").replace("\\", "")[1:])["hits"]["hits"]
        for hit in hits:
            recid = hit["id"]
            e = d.entity("record:{}".format(get_prov_record_id(hit["id"], hit["revision"])))
            d.used(a,e)
        d.wasAssociatedWith(a, u)
        
    
    return d.serialize(indent=2)

    
def parse_user(o_user):
    anonymous_user = "anonymous"
    if not o_user:
        return anonymous_user
    return o_user.get("email", anonymous_user)
     
def parse_action(action):
    no_action = "noop"
    if not action:
        return no_action
    return action[:-19] #trim _permission_factory
    
def parse_record_id_before(o_record_before):
    no_record_id = "unidentified-record"
    if not o_record_before:
        return no_record_id
    return o_record_before.get("recid", no_record_id)
    
def parse_record_id_after(o_record_after):
    no_record_id = "unidentified-record"
    if not o_record_after:
        return no_record_id
    return o_record_after["response"][0].split("recid")[1][3:].split("\",\"")[0]
    
def parse_revision_after(o_record_after):
    # only takes first occurence of "revision" into account
    no_revision = get_timestamp_now()
    if not o_record_after:
        return no_revision
    return o_record_after["response"][0].split("revision")[1][2:].split(",")[0]
    
    
def get_timestamp_now():
    return str(int(time.time()))
    
def get_base_prov_document():
    d = ProvDocument()
    d.add_namespace("user", "http://example.org/users/")
    d.add_namespace("record", " http://example.org/records/")
    d.add_namespace("action", "http://example.org/actions/")
    return d
    
def get_prov_record_id(record_id, revision):
    return "{}_{}".format(record_id, revision)
    

def eprint(*args, **kwargs):
    print(*args, file=open("/tmp/error.txt", "a+"), **kwargs)


if __name__ == "__main__":
    arglen = len(sys.argv)
    if arglen is not 7:
        eprint("Exactly 7 command line arguments are required")
        exit(3)

    try:
        o_user = json.loads(sys.argv[1])
        s_action = sys.argv[2]
        o_record_after = json.loads(sys.argv[3]) if sys.argv[3] != "null" else None
        o_record_before = json.loads(sys.argv[4]) if sys.argv[4] != "null" else None
        args = json.loads(sys.argv[5])
        kwargs = json.loads(sys.argv[6])
    except:
        eprint("Command line arguments are not valid")
        exit(3)

    provstore_username = os.getenv("PROVSTORE_USERNAME")
    provstore_apikey = os.getenv("PROVSTORE_APIKEY")
    if not provstore_username or not provstore_apikey:
        eprint("No PROVSTORE credentials found in env variables")
        exit(1)

    push_json(build_prov_json(o_user, s_action, o_record_before, o_record_after, args, kwargs), provstore_username, provstore_apikey)
