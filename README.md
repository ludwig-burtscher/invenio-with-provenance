[![DOI](https://zenodo.org/badge/260191196.svg)](https://zenodo.org/badge/latestdoi/260191196)

# invenio-with-provenance proof-of-concept

This project is a proof-of-concept of how the Research Data Management Repository [InvenioRDM](https://inveniordm.docs.cern.ch/) can be extended to provide provenance data for records.  
Though the used approach does not scale well, it shows that such modifications are possible and do work as expected.

## Architecture

The architecture of our project basically consists of three key components:
1. modified InvenioRDM
1. [ProvStore](https://openprovenance.org/store/)
1. ProvStore export and analysis of data

We use a standard installation of InvenioRDM, but add a hook to it that is always triggered when an event occurs on a record. Currently, creation, update/modification and deletion of records are supported in addition to events when a record is read/displayed or appears in a search result.

The hook calls a script (provstore-push.py) that receives event data as arguments and generates provenance data according to the [W3C PROV standard](https://www.w3.org/TR/prov-overview/). The Provenance data structure for all events is described in [Provenance data](#provenance-data).  
These audit fragments are then uploaded to the ProvStore and for storage as individual provenance documents. Each event results in a separate document.

When provenance data should be analyzed, they have to be exported from the ProvStore. Since the [API of ProvStore](https://openprovenance.org/store/help/api/#documents-list) does not provide means to download a single file containing all relevant provenance documents, we developed a script (export.py) that fetches the documents individually and generates a single RDF/Turtle file.  
This file can then be used in further tools such as GraphDB to answer further questions.


## Provenance data

This section shows the provenance data model that is used for the various events. We differentiate three concepts: users, activities and records that are custom terminology for the PROV concepts of agents, activities (same name) and entities.

Users are identified by their email address (`<<user email>>`) or "anonymous" if the user is not logged in into InvenioRDM.
Activities have a type (create, update, etc.) and are assigned a random UUID (`<<activity uuid>>`) to distinguish between different events of the same type. They also include a timestamp of when the activity happened.
Records are identified by an immutable `<<record id>>` that is assigned by InvenioRDM and therefore directly links a record in the provenance data model to the corresponding record in InvenioRDM. Additionally, a record contains a `<<record revision>>` that identifies different versions of the same record. If a record is updated, the ID stays the same, but the revision is incremented.

The following sections show diagrams of the provenance data model for each event. The semantics of the relationships can be seen in the [W3C PROV Data Model](https://www.w3.org/TR/2013/REC-prov-dm-20130430/).

### Create

![Create PROV data model](https://raw.githubusercontent.com/ludwig-burtscher/invenio-with-provenance/master/documentation/create.png)

### Read / Displayed

![Read PROV data model](https://raw.githubusercontent.com/ludwig-burtscher/invenio-with-provenance/master/documentation/read.png)

### Update

![Update PROV data model](https://raw.githubusercontent.com/ludwig-burtscher/invenio-with-provenance/master/documentation/update.png)

### Delete

![Delete PROV data model](https://raw.githubusercontent.com/ludwig-burtscher/invenio-with-provenance/master/documentation/delete.png)

### List / Appears in search result

![List PROV data model](https://raw.githubusercontent.com/ludwig-burtscher/invenio-with-provenance/master/documentation/list.png)
In this example, two records appeared as results to a search.


## How to reproduce

### Prerequisites

A Linux machine with Docker and Python 3 (with pip) is needed.  
We provide a Vagrantfile that can be used to spin up a clean Ubuntu VM with those tools installed and will further use this VM for explanations. Similar setups should work too, of course.  
Ports 80 and 443 of the VM are forwarded to ports 8080 and 4443 on the local machine. The InvenioRDM UI is therefore accessible at https://localhost:4443.

### Installing modified InvenioRDM

Once the VM is up an running, the `invenio-rdm` directory has to be copied to the VM. Since the directory with the Vagrantfile is mounted at `/vagrant` in the VM, the `invenio-rdm` directory can be copied to the VM's file system with `cp -r /vagrant/invenio-rdm <<destination>>`.  
To install the modified InvenioRDM, the `setup-invenio.sh` script in the copied directory has to be called. If necessary, the TLS certificate/key for the InvenioRDM UI in the `cert` directory can be replaced before starting the installation process. The setup script asks some self-explaining questions that have to be answered interactively. For the PROVSTORE username and API key, a free ProvStore is needed. It can be registered [here](https://openprovenance.org/store/account/signup/).  
The installation then continues without further user interaction, but can take a lot of time. Once the script has finished, InvenioRDM is installed and running successfully.

### Simulating events to generate provenance

The directory `simulation` contains the shell script `test-scenario.sh` that can be executed to simulate events. This script is called from outside the InvenioRDM installation. It might be necessary to change the hostname/port of the InvenioRDM installation at the beginning of the script, depending on the chosen setup.  
Generated events will change the state of InvenioRDM, so do not use this script on a production instance of InvenioRDM! Provenance data of the generated events will be automatically sent to the ProvStore (if the credentials entered during setup are valid).

### Export of provenance data from ProvStore

The directory `provstore_export` contains the Python script `export.py` that downloads a single RDF/Turtle file with all captured provenance in ProvStore (with valid credentials). Because all data in the ProvStore account is retrieved, a ProvStore account is necessary, where only data from InvenioRDM is stored.

### Analysis in graph query engines

The provenance data is exported as RDF/Turtle. This format allows for easy analysis of the recorded data with SparQL queries.
These queries can be executed with common libraries such as RDFLib or Eclipse RDF4J or complete graphical applications such as Ontotext GraphDB.

These engines allow to define a pattern in SparQL that is matched against the data graph outlined [Provenance data](#provenance-data).
The PROV data model allows to write a variety of useful queries. 
In the next section we will present a few possible questions that can be answered with this data model.


## Results of simulation test data

The directory `simulation/results` contains the RDF/Turtle file with provenance data captured from executing the `test-scenario.sh` script twice. It was created like described above.
The `simulation` directory also contains possible queries that could be executed on the retrieved data.

Each query is ran on the included provenance data and the output is stored together with a short description together with the query.
To perform the query any SparQL query engine could be used. In our case we used GraphDB to host and query the data.

### Importing the data
To import the data into GraphDB go to `Import` in the left side menu and choose `RDF`. 
You might need to create a new repository. 
You can use the default settings for the repository creation.
Upload the file generated by the ProvStore export tool. 
In the table below import the file you just uploaded.
You can use an arbitrary `Base IRI` for the import.
In this repository we used `http://example.org/indeniordm-prov#`.
All other settings can be left on default.

### Running queries

To run the queries stored in the `simulation/` directory you can copy them into the query box in the `SPARQL` menu entry.
On the right hand side of the text box you have a `Run` button to execute the query.
The result will be displayed below the query box.
The results for the testdata set in `simulation/results/` is provided in each query file as a comment.

Included queries are:
* Give me a list of users who have seen the file
* Give me all people who modified the file
* Was the file used after a specific timestamp?
* Give me all files seen be the given user on the specific day
* Which user has created the most records?
* Which record has been changed the most?
* Had a user any access to a file?


## Modifications of InvenioRDM

This section describes, what files are modified compared to a standard InvenioRDM installation.

First of all, the `setup-invenio.sh` script acts as a wrapper around the standard `invenio-cli init` way of installing InvenioRDM (see [here](https://inveniordm.docs.cern.ch/install/)). It automates installation as far as possible (some user interaction is required though) and provides an entrypoint for all necessary modifications. Because a couple of version errors occurred during development, the setup script also fixes the versions of some dependencies.

Through the `modify-docker-compose.py` script in `invenio-rdm/setup/docker`, the `docker-compose.yml` file created during InvenioRDM installation is adapted. Along with changes to make InvenioRDM even work (set number of proxies, add allowed hosts), which are not related to provenance data, the environment variables holding the ProvStore credentials are set here.

Also, the Dockerfile created during InvenioRDM installation has to be modified. The content of the file `invenio-rdm/setup/docker/extra-dockerfile-lines.txt` is appended to the Dockerfile. With these changes, the `provstore-push.py` script is copied to the docker image during the build process and a needed Python package is installed. This script handles generation of provenance data from events and uploads them to the ProvStore.

A trigger to call this script is still missing. This trigger is added by patching the file `/opt/invenio/src/src/invenio-records-rest/invenio_records_rest/views.py` inside the docker image with the diff file provided at `invenio-rdm/setup/diff/records-view-file.patch`. It modifies original InvenioRDM code so that the `provstore-push.py` script is called with appropriate parameters whenever an event involving a record occurs.


## Contributers

* Roland Wallner <a itemprop="sameAs" content="https://orcid.org/0000-0002-2932-9892" href="https://orcid.org/0000-0002-2932-9892" target="orcid.widget" rel="me noopener noreferrer" style="vertical-align:top;"><img src="https://orcid.org/sites/default/files/images/orcid_16x16.png" style="width:1em;margin-right:.5em;" alt="ORCID iD icon">https://orcid.org/0000-0002-2932-9892</a>
* Ludwig Burtscher <a itemprop="sameAs" content="https://orcid.org/0000-0001-5453-8074" href="https://orcid.org/0000-0001-5453-8074" target="orcid.widget" rel="me noopener noreferrer" style="vertical-align:top;"><img src="https://orcid.org/sites/default/files/images/orcid_16x16.png" style="width:1em;margin-right:.5em;" alt="ORCID iD icon">https://orcid.org/0000-0001-5453-8074</a>


## Disclaimer

This project was implemented for the Data Stewardship lecture in summer term 2020 at TU Wien. It is a proof of concept and should not be used in production without adaptions. Only requests to the InvenioRDM REST API are guaranteed to create provenance data, since the user interface is not fully functional yet.
 


