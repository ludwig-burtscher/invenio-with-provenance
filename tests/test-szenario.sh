#!/usr/bin/env bash

source ./invenio-api.sh
check_deps

set_invenio_host "https://10.0.0.160"
set_curl_opts "--insecure"

# use a user
set_session $(signup "test${RANDOM}@test.it" "passdfsdfgsdfg")

# to logout use:
# set_session ""

id=$(create_record_simple "Testdata" "10.9999/rdm.9999999")
echo "Created test record with new key: $id"

querystr="Testdata"
echo "Searching for '$querystr'"
# search_records "$querystr"

testfilename="test_upload_file.txt"
touch ${testfilename}
echo -e "# This is Test content\n[Maybe]\nItsA = ini" > ${testfilename}
upload_file_to_record ${id} ${testfilename}

echo "Reading file"
read_file_for_record ${id} ${testfilename}
echo
