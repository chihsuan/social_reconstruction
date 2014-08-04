#!/usr/bin/env python2.7

'''
This program is to find two entity set in movie

Define: n-entity set means there is only n keywords adjacent in a specific time interval 

input: 1.keyword_list.csv 2. search_result.csv  (time_to_keyword pair in subtitle)
output: two_entity_set.csv

'''

import sys

from modules import csv_io
from modules import json_io
from modules import time_format

OUTPUT_PAHT = 'output/'

def find_two_entity(keyword_list_file, search_result_file, relations_file):

    time_to_keyword = csv_io.read_csv(search_result_file)
    keyword_list = csv_io.read_csv(keyword_list_file)
    relation_list = json_io.read_json(relations_file)

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
    
    entity_set = {}

    # Find two entity with leadingKeword
    for name, relations in relation_list.iteritems():
        min_interval = 5
        if name != leading_keyword:
            role_set = {}
            important_person = max(relation_list[name], key=relation_list[name].get)
            key = name + '-' + important_person
            while min_interval >= 0.5 and key not in role_set: 
                role_set, relation_set = get_adjacent(name, frame_list, frame_to_keyword, 24 * 60 * min_interval)
                min_interval -= 0.5
            if key in role_set:
                entity_set.update({key : role_set[key]})
            else:
                important_person = max(role_set, key=role_set.get)
                entity_set.update({important_person: role_set[important_person]})
    # Add leading_keyword list
    entity_set.update(leading_keword_filter(leading_keyword, frame_list, frame_to_keyword, 24 * 60 * 1 ))
    relation_set.append(leading_keyword)
  
    '''add_role = []
    # Add other important roles
    for name, relations in relation_list.iteritems():
        if name in relation_set:
            for relation in relations:
                if relation not in relation_set and relation not in add_role:
                    add_role.append(relation)

    for role in add_role:
        important_person = max(relation_list[role], key=relation_list[role].get)
        role_set, rel_set = get_adjacent(important_person, frame_list, frame_to_keyword, 24 * 60 * (MIN_INTETVAL-1) )
        entity_set.update(role_set)
    
    # Add supporting role who are not imporant in movie
    for keyword in keyword_list:
        if keyword not in relation_set and keyword not in add_role:
            role_set, rel_set = get_adjacent(keyword, frame_list, frame_to_keyword, 24 * 60)
            important_person = max(role_set, key=role_set.get)
            entity_set.update({important_person : role_set[important_person]})
   
    print entity_set'''

    '''keyword_frames = {}
    for frame in frame_to_keyword:
        keyword = frame_to_keyword[frame]
        if frame_to_keyword[frame] not in relation_set and frame_to_keyword[frame] != leading_keyword:
            if keyword not in keyword_frames:
                keyword_frames[keyword] = []
            keyword_frames[keyword].append(frame)'''


    json_io.write_json( OUTPUT_PAHT + 'entity_set.json', entity_set)


def get_adjacent(pivot_keyword, frame_list, frame_to_keyword, interval):

    adjacent_set = {}
    record_list = []
    current_frame = frame_list[0]
    pivot_exist = False
    adjacent_exist = False
    previous_keyword = frame_to_keyword[frame_list[0]]
    relation_set = []

    for frame in frame_list:
        # is previous_keyword or pivot_keyword 
        if frame_to_keyword[frame] == previous_keyword and frame_to_keyword[frame]:
            record_list.append(frame)
            adjacent_exist = True
        elif frame_to_keyword[frame] == pivot_keyword and frame_to_keyword[frame]:
            pivot_exist = True
            record_list.append(frame)
        else:
            previous_keyword = frame_to_keyword[frame]
            current_frame = frame
            adjacent_exist = True
            pivot_exist = False
            record_list = []

        # Fulfillment of the conditions
        if frame >= (current_frame + interval) and adjacent_exist and pivot_exist: 
            keyword = pivot_keyword + '-' + previous_keyword

            if previous_keyword not in relation_set:
                relation_set.append(previous_keyword)

            for key in record_list:
                if keyword not in adjacent_set:
                    adjacent_set[keyword] = []
                adjacent_set[keyword].append(key)
            record_list = []

    return adjacent_set, relation_set

def leading_keword_filter(leading_keyword, frame_list, frame_to_keyword, interval):

    pivot_number = 0
    current_frame = frame_list[0]
    record_list = []
    leading_keyword_list = { leading_keyword: [] }
    
    for frame in frame_list:
        # is previous_keyword or pivot_keyword 
        if frame_to_keyword[frame] == leading_keyword:
            record_list.append(frame)
            pivot_number += 1
        else:
            previous_keyword = frame_to_keyword[frame]
            current_frame = frame
            pivot_number = 0
            record_list = []

        # Fulfillment of the conditions
        if frame >= (current_frame + interval) and pivot_number > 0: 
            for key in record_list:
                leading_keyword_list[leading_keyword].append(key)
            record_list = []

    return leading_keyword_list


if __name__=='__main__':
    if len(sys.argv) == 3:
        find_two_entity(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        find_two_entity('output/keyword_list.csv', 'output/search_result.csv', 'output/relations.json')
