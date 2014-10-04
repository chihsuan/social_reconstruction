#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''
This program is to reconstruct roles in movie 
input: 1.face_recongition.json 2.keword_list_file
output: role.json

'''

import sys
import cv2
import cv2.cv as cv

from modules import json_io
from modules import csv_io
from modules import cv_face

OUTPUT_PATH = 'output/'
MIN_MATCH = 5

def reconstruct_role(recongition_merge_file, keword_list_file):

    keyword_to_frame = json_io.read_json(recongition_merge_file)
    keword_list = csv_io.read_csv(keword_list_file)

    leading_keyword = keword_list[0]

    for keyword, frame_list in keyword_to_frame.iteritems():
        for frame in frame_list:
            for face in frame_list[frame]:
                name = keyword + str(face['frame_position']) + '.jpg'
                face['img'] = cv2.imread(OUTPUT_PATH + '/img/' + name)

    detector, matcher =  cv_face.init_feature('orb')
    # Find other characters
    face_list = {}
    character_list = {}
    for keyword, frame_list in keyword_to_frame.iteritems():
        print keyword 
        for frame in frame_list:
            for face in frame_list[frame]:
                if face and face['face_id'] not in face_list:
                    face_list[face['face_id']] = []
                if face:
                    face_list[face['face_id']].append(face)
        rank  = sorted(face_list, key=lambda k: len(face_list[k]), reverse=True)
        character_list[keyword] = [face_list[rank[0]]]
        i=0
        #for face in face_list[rank[5]]:
         #   i+=1
'''
This program is to find relation between keywords
input: 1. keyword_list_file, 2.search_result_file
output: relation.json
'''

import sys
from modules import csv_io
from modules import json_io
from modules import time_format

INTERVAL = 24 * 60 * 7

def find_relation(keyword_list_file, search_result_file, time_interval):
 
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
        relations.update( {keyword_list[i] : count_ralation(keyword_list[i], frame_list, frame_to_keyword, time_interval)} )

    count = 0
    proper_relation = {}
    for name, relation in relations.iteritems():
        total = sum(relation.values())
        proper_relation[name] = {}
        print name, 
        for person in relation:
            if proper_test(total, leading_keyword, person, relation):
                proper_relation[name][person] = relation[person]
                print person , relation[person],
                count += 1
        print


    print str(time_interval/(24*60)) + ',' + str(count)
    json_io.write_json('output/relations.json', proper_relation)


def count_ralation(keyword, keys, frame_to_keyword, INTERVAL): 
    
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
        if (float(relation[person]) / total > (1.0/len(relation) )) and  relation[person] >= relation[leading_keyword]:
            return True
    return False

if __name__ == '__main__':
    if len(sys.argv) == 3:
        find_relation(sys.argv[1], sys.argv[2], sys.argv[3], 4.5*60)
    else:
        find_relation('output/keyword_list.csv', 'output/search_result.csv', 24*60*4.5)
