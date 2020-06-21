#!/usr/bin/env bash

source ./invenio-api.sh
check_deps

set_invenio_host "https://10.0.0.160"
set_curl_opts "--insecure"

create_update_get_record () {
  title="$1"
  doi="$2"

  id=$(create_record_simple ${title} ${doi})
  echo "Created test record with new key: $id" >&2

  echo "Doing an update..." >&2
  read -d '' update << EOF
[{
  "op": "replace",
  "path": "/identifiers/arXiv",
  "value": "88888"
}]
EOF
  update_record ${id} "$update" > /dev/null
  echo >&2


  echo "Getting record ${id}" >&2
  get_record ${id} > /dev/null
  echo >&2

  echo ${id}
}

# use a user
echo "Using a user"
set_session $(signup "test${RANDOM}@test.it" "passdfsdfgsdfg")

# to logout use:
# set_session ""

create_update_get_record "Testdata" "10.9999/rdm.9999998"
create_update_get_record "Testdata2" "10.9999/rdm.9999997"
create_update_get_record "Testdata3" "10.9999/rdm.9999996"
id1=$(create_update_get_record "Testdata4" "10.9999/rdm.9999995")
id12=$(create_update_get_record "Testdata5" "10.9999/rdm.9999994")

querystr="Testdata"
echo "Searching for '$querystr'"
search_records "$querystr"

delete_record ${id1}
get_record ${id12}

# Anonymous user
echo "Using the anonymous user"
set_session ""
create_update_get_record "Testdata" "10.9999/rdm.9999998"
create_update_get_record "Testdata2" "10.9999/rdm.9999997"
create_update_get_record "Testdata3" "10.9999/rdm.9999996"
id1=$(create_update_get_record "Testdata4" "10.9999/rdm.9999995")
id2=$(create_update_get_record "Testdata5" "10.9999/rdm.9999994")
get_record ${id2}

# Another User
echo "Using another user"
set_session $(signup "admin${RANDOM}@test.it" "passdfsdfgsdfg")
id1=$(create_update_get_record "Testdata4" "10.9999/rdm.9999995")
id2=$(create_update_get_record "Testdata5" "10.9999/rdm.9999994")
delete_record ${id1}
delete_record ${id2}

get_record ${id12}