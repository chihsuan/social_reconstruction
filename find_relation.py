'''
This program is to find relation between keywords
input: 1. keyword_list_file, 2.search_result_file
output: relation.json
'''

import sys
from modules import csv_io
from modules import time_format

INTERVAL = 24 * 60 * 10

def find_relation(keyword_list_file, search_result_file):
 
    time_to_keyword = csv_io.read_csv(search_result_file)
    keyword_list = csv_io.read_csv(keyword_list_file)
    leading_keyword = keyword_list[0]
    
    frame_to_keyword = {}
    for row in time_to_keyword:
        start_frame, end_frame = time_format.to_frame(row)
        frame_to_keyword[start_frame] = row[1]
    # Transfrom to timeline format
    frame_list = frame_to_keyword.keys()
    frame_list.sort()
    
    relations = {}
    for i in range(1, len(keyword_list)):
        relations.update( {keyword_list[i] : count_ralation(keyword_list[i], frame_list, frame_to_keyword)} )
  
    for name, relation in relations.iteritems():
        total = sum(relation.values())
        print name,
        for person in relation:
            #print person, relation[person],
            if total != 0 and (float(relation[person]) / total > (1.0/len(relation)) - 0.03 ):
                print person , relation[person],
        print

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

if __name__ == '__main__':
    find_relation(sys.argv[1], sys.argv[2])
