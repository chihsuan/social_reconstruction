'''

This program is to reconstruct roles in movie 
input: recongition_merge.json
output: role.json

'''

import sys
import cv2
import cv2.cv as cv

from modules import json_io

OUTPUT_PATH = 'output/'

def recongition_merge(recongition_merge_file):

    keyword_list = json_io.read_json(recongition_merge_file)


    # Find leading role


    # Find other characters
    face_list = {}
    for keyword, frame_list in keyword_list.iteritems():
        for frame in frame_list:
            for face in frame_list[frame]:
                if face and face['face_id'] not in face_list:
                    face_list[face['face_id']] = []
                if face:
                    face_list[face['face_id']].append(face)
        print keyword 
        sort_list  = sorted(face_list, key=lambda k: len(face_list[k]), reverse=True)
        print sort_list
        face = face_list[sort_list[3]][0]
        name = keyword + str(face['frame_position']) + '.jpg'
        print name
        img = cv2.imread(OUTPUT_PATH + '/img/' + name )
        cv2.imwrite(OUTPUT_PATH + '/result/' + keyword  + '.jpg', img)
        face_list = {}
        # Use leading role image to check
        

    # Output


if __name__=='__main__':
    recongition_merge(sys.argv[1])
