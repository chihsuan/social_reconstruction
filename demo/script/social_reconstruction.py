'''
This program will reconstruct the social relation between movie role-net
input: 1. keyword_list.json 2. relations.json
output: relation_graph

'''

import sys

from modules import json_io
from modules import csv_io

OUTPUT_PAHT = 'output/'

def social_reconstruction(keyword_list_file, relations_file):
    
    keyword_list = csv_io.read_csv(keyword_list_file)
    relations = json_io.read_json(relations_file)

    relation_graph = {'nodes': [], 'links': []}

    node_index = {}
    index = 0
    for keyword in keyword_list:
        if keyword not in node_index:
            relation_graph['nodes'].append({'name': keyword, 'group': index, 'ID': index})
            node_index[keyword] = index
            index += 1

    for name, relation in relations.iteritems():
        #total = sum(relation.values())
        for person in relation:
            #if total != 0 and (float(relation[person]) / total > (1.0/len(relation)) - 0.03 ):
            relation_graph['links'].append({'source': node_index[name], 'target': node_index[person],
                                           'value': relation[person], 'label': person })
            relation_graph['links'].append({'source': node_index[person], 'target': node_index[name],
                                           'value': relation[person], 'label': name })
    print relation_graph
    json_io.write_json( OUTPUT_PAHT  + 'relation_graph.json', relation_graph)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        social_reconstruction(sys.argv[1], sys.argv[2])
    else:
        social_reconstruction('output/keyword_list.csv', 'output/relations.json')
