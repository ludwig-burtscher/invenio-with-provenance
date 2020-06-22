#!/usr/bin/env bash

# This file contains function to interact with an invenio installation
# Dependencies curl

HOST="http://localhost"
CURL_OPTS=""
SESSION=""

fail () {
  printf '%s\n' "$1" >&2
  exit 1
}

check_deps () {
  [ -x "$(command -v curl)" ] || fail "curl is not installed; try: apt install curl"
  [ -x "$(command -v jq)" ] || fail "jq is not installed; try: apt install jq"
  [ -x "$(command -v grep)" ] || fail "grep is not installed"
  [ -x "$(command -v cut)" ] || fail "cut is not installed"
}

set_invenio_host () {
  HOST="$1"
}

set_curl_opts () {
  CURL_OPTS="$1"
}

set_session () {
  SESSION="$1"
}

create_record () {
  record_model="$1"
  curl ${CURL_OPTS} -s -b session=${SESSION} --header "Content-Type: application/json" \
    --request POST \
    --data "$record_model" \
    "$HOST/api/records/" | jq -r ".id"
}

create_record_simple () {
   title="$1"
   doi="$2"
   read -d '' txt << EOF
{
  "_access": {
        "metadata_restricted": false,
        "files_restricted": false
    },
    "_owners": [1],
    "_created_by": 1,
    "community": {
      "primary": "Maincom",
      "secondary": ["Subcom One","Subcom Two"]
    },
    "access_right": "open",
    "resource_type": {
        "type": "publication",
        "subtype": "publication-article"
    },
    "identifiers": {
        "DOI": "${doi}",
        "arXiv": "9999.99999"
    },
    "creators": [
        {
            "name": "Julio Cesar",
            "type": "Personal",
            "given_name": "Julio",
            "family_name": "Cesar",
            "identifiers": {
                "Orcid": "9999-9999-9999-9999"
            },
            "affiliations": [
                {
                    "name": "Entity One",
                    "identifier": "entity-one",
                    "scheme": "entity-id-scheme"
                }
            ]
        }
    ],
    "titles": [
        {
            "title": "$title",
            "type": "Other",
            "lang": "eng"
        }
    ],
    "descriptions": [
        {
            "description": "A story on how Julio Cesar relates to Gladiator.",
            "type": "Abstract",
            "lang": "eng"
        }
    ],
    "licenses": [
        {
            "license": "Berkeley Software Distribution 3",
            "uri": "https://opensource.org/licenses/BSD-3-Clause",
            "identifier": "BSD-3",
            "scheme": "BSD-3"
        }
    ]
}
EOF
create_record "$txt"
}

update_record () {
  record_id="$1"
  update="$2"

  curl ${CURL_OPTS} -s -b session=${SESSION} --header "Content-Type: application/json" \
    --request PATCH \
    --data "$update" \
    "${HOST}/api/records/${record_id}"
}

get_record () {
  record_id="$1"

  curl ${CURL_OPTS} -s -b session=${SESSION} \
    "${HOST}/api/records/${record_id}"
}

delete_record () {
  record_id="$1"

  curl ${CURL_OPTS} -s -b session=${SESSION} \
    -X DELETE \
    "${HOST}/api/records/${record_id}"
}

search_records () {
  querystr="$1"

  curl ${CURL_OPTS} -s -b session=${SESSION} "$HOST/api/records/?q=$querystr" | jq -r ".hits.hits | map(.id) | .[]"
}

upload_file_to_record () {
  record_id="$1"
  filename="$2"

  curl ${CURL_OPTS} -s -b session=${SESSION} -H "Content-Type: application/octet-stream" \
    --request PUT \
    --data-binary @${filename} \
    "$HOST/api/records/$record_id/files/$filename" > /dev/null
}

read_file_for_record () {
  record_id="$1"
  filename="$2"
  curl ${CURL_OPTS} -b session=${SESSION} "$HOST/api/records/$record_id/files/$filename"
}

signup () {
  email="$1"
  password="$2"

  cookiefile=$(mktemp)

  csrf_token=$(curl -c ${cookiefile} -s ${CURL_OPTS} "$HOST/signup/" | grep -e "csrf_token" | grep -oE "[A-Za-z0-9._/-]{30,}")
  curl -b ${cookiefile} -c ${cookiefile} -s ${CURL_OPTS} -X POST --data "csrf_token=${csrf_token}&email=${email}&password=${password}" "$HOST/signup/" > /dev/null

  cat $cookiefile | grep "HttpOnly" | grep "session" | cut -f7 # Return session cookie
  rm ${cookiefile}
}