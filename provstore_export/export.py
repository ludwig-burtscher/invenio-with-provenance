#!/usr/bin/env python3

import argparse
import requests


class ProvStoreExport:
    def __init__(self, username, apikey):
        self.baseurl = "https://openprovenance.org"
        self.username = username
        self.authorization = "ApiKey {}:{}".format(username, apikey)

    def __get_all_own_document_uris(self):
        url = self.baseurl + "/store/api/v0/documents?owner={}".format(self.username)
        uris = []
        # we have pagination
        while True:
            r_json = requests.get(url, headers={"Authorization": self.authorization}).json()
            next_url = r_json["meta"]["next"]
            uris.extend([ d["resource_uri"] for d in r_json["objects"]])
            if not next_url:
                break
            url = self.baseurl + next_url
        # remove duplicates and sort (duplicates should not occur, but sometimes do)
        uris = list(set(uris))
        uris.sort()
        return uris

    def __get_documents(self, uris):
        documents = []
        for uri in uris:
            # ttl: Turtle format
            url = (self.baseurl + uri)[:-1] + ".ttl"
            r = requests.get(url, headers={"Authorization": self.authorization})
            documents.append(r.text)
        return documents

    def __write_documents_to_file(self, documents, outfile):
        with open(outfile, "a") as file:
            file.truncate(0)
            for document in documents:
                file.write(document)

    def export(self, outfile):
        uris = self.__get_all_own_document_uris()
        documents = self.__get_documents(uris)
        self.__write_documents_to_file(documents, outfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export Turtle RDF from ProvStore")
    parser.add_argument("--username", dest="username", help="The username for accessing ProvStore", required=True)
    parser.add_argument("--apikey", dest="apikey", help="The API key for accessing ProvStore", required=True)
    parser.add_argument("--out", dest="outputfile", help="The file where the output should be saved", required=True)
    args = parser.parse_args()

    provstore_export = ProvStoreExport(args.username, args.apikey)
    provstore_export.export(args.outputfile)
