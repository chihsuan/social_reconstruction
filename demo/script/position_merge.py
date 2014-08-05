#!/usr/bin/env python2.7
'''
This program is to merge face by near frame and near face position 
input: 1. frame.json
output: 2. merge_position.json
'''

import sys

from modules import json_io

NEAR_FRAME = 24 * 60 * 10
NEAR_POSITION = 18

OUTPUT_PATH = 'output/'

def position_merge(frame_file):

    frame = json_io.read_json(frame_file)
    
    keys = frame.keys()
    
    for i in range(0, len(frame)):
        for j in range(i+1, len(frame)):
            if is_near( frame[keys[i]], frame[keys[j]] ):
                frame[keys[j]]['face_id'] = frame[keys[i]]['face_id']
                print 111
    
    json_io.write_json(OUTPUT_PATH + 'merge_position.json', frame)


def is_near(frame1, frame2):

    if( abs(frame1['frame_position'] - frame2['frame_position']) > NEAR_FRAME ) or frame1['face_id'] == frame2['face_id']:
        return False
    else:
        for i in range(4):
           distance = abs(frame1['face_position'][i] - frame2['face_position'][i])
           less =  0 if (i % 2 == 0) else 1
           if distance > (NEAR_POSITION - less ):
               return False
    return True

if __name__=='__main__':
    if len(sys.argv) == 2:
        position_merge(sys.argv[1])
    else:
        position_merge('output/frame.json')
