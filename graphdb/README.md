# GraphDB instance to analyse invenio provenance data

Provenance data from invenio is imported into GraphDB to query with SPARQL.

## Building a docker image based on the free edition

You will need docker and docker-compose installed on your machine.

1. Register on the Ontotext website for the GraphDB Free edition. Download the zip file and place it in this directory (https://www.ontotext.com/products/graphdb/graphdb-free/)
1. Adjust version in docker-compose.yml file
1. `docker-compose up`
1. Access GraphDB on port 7200