'''write data to neo4j'''

import sys

from neo4jrestclient.client import GraphDatabase

from modules import json_io
from modules import csv_io

def neo4j_db(neo4j_url, data_path):

    gdb = GraphDatabase(neo4j_url)
    data = json_io.read_json(data_path)

    if 'nodes' in data and 'links' in data:
        nodes = []
        for node in data['nodes']:
            nodes.append(gdb.nodes.create(name=node['name'])) 

        for edge in data['links']:
            source = nodes[edge['source']]
            target = nodes[edge['target']]
            source.relationships.create('Knows', target)

if __name__=='__main__':
    neo4j_db("http://localhost:7474/db/data/", sys.argv[1])
