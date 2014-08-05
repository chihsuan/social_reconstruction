'''
This program is to find relation between keywords
input: 1. keyword_list_file, 2.search_result_file
output: relation.json
'''

import sys
from modules import csv_io
from modules import json_io
from modules import time_format

INTERVAL = 24 * 60 * 4.5

def find_relation(keyword_list_file, search_result_file):
 
    time_to_keyword = csv_io.read_csv(search_result_file)
    keyword_list = csv_io.read_csv(keyword_list_file)
    leading_keyword = keyword_list[0]
    
    frame_to_keyword = {}
    for row in time_to_keyword:
        start_frame, end_frame = time_format.to_frame(row)
        while start_frame in frame_to_keyword:
            start_frame = start_frame + 0.001
        while end_frame in frame_to_keyword:
            end_frame = end_frame + 0.001
        frame_to_keyword[start_frame] = row[1]
        
    # Transfrom to timeline format
    frame_list = frame_to_keyword.keys()
    frame_list.sort()
    
    relations = {}
    for i in range(1, len(keyword_list)):
        relations.update( {keyword_list[i] : count_ralation(keyword_list[i], frame_list, frame_to_keyword)} )
 
    proper_relation = {}
    for name, relation in relations.iteritems():
        total = sum(relation.values())
        proper_relation[name] = {}
        print name, 
        for person in relation:
            if proper_test(total, leading_keyword, person, relation):
                proper_relation[name][person] = relation[person]
                print person , relation[person],

        print

    json_io.write_json('output/relations.json', proper_relation)


def count_ralation(keyword, keys, frame_to_keyword): 
    
    relation = {}
    lower_bound  = -1
    for pivot in range(0, len(frame_to_keyword)):
        current_keyword = frame_to_keyword[keys[pivot]]
        if current_keyword == keyword:
            backward = pivot - 1
            forward = pivot + 1
            while 0 < backward and keys[backward] > (keys[pivot] - INTERVAL):
                current_keyword = frame_to_keyword[keys[backward]]
                if current_keyword != keyword:
                    if current_keyword not in relation:
                        relation[current_keyword] = 0 
                    relation[current_keyword] += 1
                backward -= 1
            
            while forward < len(frame_to_keyword) and  keys[forward] < (keys[pivot] + INTERVAL):
                current_keyword = frame_to_keyword[keys[forward]]
                if current_keyword != keyword:
                    if current_keyword not in relation:
                        relation[current_keyword] = 0 
                    relation[current_keyword] += 1
                forward += 1
            lower_bound = pivot + INTERVAL
    
    return relation


def proper_test(total, leading_keyword, person, relation):
    if total == 0:
        return False
    
    important_person = max(relation, key=relation.get)

    if important_person == leading_keyword or leading_keyword not in relation:
        if (float(relation[person]) / total > (1.0/len(relation) )):
            return True
    else:
        if (float(relation[person]) / total > (1.0/len(relation) )) and  relation[person] > relation[leading_keyword]:
            return True
    return False

if __name__ == '__main__':
    if len(sys.argv) == 3:
        find_relation(sys.argv[1], sys.argv[2])
    else:
        find_relation('output/keyword_list.csv', 'output/search_result.csv')
