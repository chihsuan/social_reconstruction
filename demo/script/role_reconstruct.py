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

OUTPUT_PATH = 'public/images/'

def reconstruct_role(recongition_merge_file, keword_list_file):

    keyword_to_frame = json_io.read_json(recongition_merge_file)
    keword_list = csv_io.read_csv(keword_list_file)

    leading_keyword = keword_list[0]

    for keyword, frame_list in keyword_to_frame.iteritems():
        for frame in frame_list:
            for face in frame_list[frame]:
                name = keyword + str(face['frame_position']) + '.jpg'
                face['img'] = cv2.imread( 'output' + '/img/' + name)
                print face['frame_position'], keyword

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
        for j in rank:
            face = face_list[j][0]
            cv2.imwrite(OUTPUT_PATH + '/result2/' + keyword + str(i) + '.jpg', face['img'])
            i += 1
        if len(rank) > 1 and '-' in keyword:
            for i in range(1, len(rank)):
                print len(character_list[keyword][0])
                print 
                print len(face_list[rank[i]])
                if cv_face.list_match(4, character_list[keyword][0], face_list[rank[i]], detector, matcher):
                    continue
                else:
                    character_list[keyword].append(face_list[rank[i]])
                    break 
            if len(character_list[keyword]) == 1:
                character_list[keyword].append(face_list[rank[1]])
        face_list = {}


    # Use leading role image to check
    lead_role_list = character_list[leading_keyword]
    for keyword, characters in character_list.iteritems():
        if leading_keyword in keyword and keyword != leading_keyword:
            match_count1 = 0
            match_count2 = 0
            for face in character_list[leading_keyword][0]:
                match_count1 += cv_face.get_match_rate(face['img'], characters[0][0]['img'])
            for face in character_list[leading_keyword][0]:
                match_count1 += cv_face.get_match_rate(face['img'], characters[1][0]['img'])
            if match_count1 >= match_count2:
                del characters[1]
            else:
                del characters[0]
    
    # Output
    for keyword, characters in character_list.iteritems():
        for character in characters:
            if '-' in keyword:
                keyword = keyword.split('-')[0]
            cv2.imwrite(OUTPUT_PATH + keyword + '.jpg', character[0]['img'])
            print keyword,
        print
    
def similar_select(role_list, character_list):
    pass

if __name__=='__main__':
    if len(sys.argv) == 3:
        reconstruct_role(sys.argv[1], sys.argv[2])
    else:
        reconstruct_role('output/face_recongnition.json', 'output/keyword_list.csv')
