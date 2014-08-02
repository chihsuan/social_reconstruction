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
MIN_INTETVAL = 3

def find_two_entity(keyword_list_file, search_result_file):

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
    
    # Find two entity with leadingKeword
    leading_entity_set, relation_set = get_adjacent(leading_keyword, frame_list, frame_to_keyword, 24 * 60 * MIN_INTETVAL)

    # Add leading_keyword list
    leading_entity_set.update(leading_keword_filter(leading_keyword, frame_list, frame_to_keyword, 24 * 60 * 1 ))

    # Add keywords that not found in last step 
    keyword_frames = {}
    for frame in frame_to_keyword:
        keyword = frame_to_keyword[frame]
        if frame_to_keyword[frame] not in relation_set and frame_to_keyword[frame] != leading_keyword:
            if keyword not in keyword_frames:
                keyword_frames[keyword] = []
            keyword_frames[keyword].append(frame)

    leading_entity_set.update(keyword_frames)

    json_io.write_json( OUTPUT_PAHT + 'entity_set.json',leading_entity_set)


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
        find_two_entity(sys.argv[1], sys.argv[2])
    else:
        reconstruct_role('output/keyword_list.csv', 'output/search_result.csv')
