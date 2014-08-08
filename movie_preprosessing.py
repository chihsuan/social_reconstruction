#!/usr/bin/env python2.7

'''
This program is to detect the face in movie with two_entity_file and keyword_search_result (detect in specific frame)
input: 1.movie_file (video format) 2.two_entity_file 3. search_result_file

'''

import sys
import threading

import cv2
import cv2.cv as cv

from modules import json_io
from modules import csv_io
from modules import time_format
from modules import cv_image

OUTPUT_PATH = 'output/'

class Pthread (threading.Thread):

    def __init__(self, threadID, name, searchResult):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.searchResult = searchResult

    def run(self):
        print self.name + ' start'
        threadLock.acquire()
        frameCapture(self.searchResult)
        threadLock.release()


def movie_prosessing(movie_file, two_entity_file, search_result_file):
    two_entity_set = json_io.read_json(two_entity_file)
    keyword_search_result = csv_io.read_csv(search_result_file)

    # load video
    videoInput = cv2.VideoCapture(movie_file)

    # crate a start_frame to end_frame dictionary for two_entity_set look up
    start_end = {}
    for row in keyword_search_result:
        start_frame, end_frame = time_format.to_frame(row)
        while start_frame in start_end:
            start_frame = start_frame + 0.001
        while end_frame in start_end:
            end_frame = end_frame + 0.001
        start_end[start_frame] = end_frame 

    frame = {}
    face_count = 0
    for keyword in two_entity_set:
        for start_frame in two_entity_set[keyword]:
            frame_position = int(start_frame) - 24 * 10
            finish_frame = start_end[start_frame] + 24 * 10
            while frame_position <= finish_frame: 
                print keyword
                videoInput.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, frame_position)
                flag, img = videoInput.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)
                face_position_list, rects = cv_image.face_detect(gray, frame_position, (85, 85))
                #face_position_list, rects =  faceDetection(gray, frame_position)
                if 0xFF & cv2.waitKey(5) == 27:
                    cv2.destroyAllWindows()
                    sys.exit(1)
                
                if len(face_position_list) == 1:
                    print 'detected'
                    image_name = keyword + str(frame_position) + '.jpg'
                    cv_image.output_image(rects, img, OUTPUT_PATH + '/img/' + image_name)
                    for face_position in face_position_list:
                        face_count += 1
                        print face_count
                        frame[face_count] = { 'keyword' : keyword, 
                                                  'face_position': face_position.tolist(),
                                                  'ID' : face_count,
                                                  'frame_position': frame_position,
                                                  'face_id': face_count} 
                frame_position += 12
    #close video  
    videoInput.release()

    json_io.write_json(OUTPUT_PATH + 'frame.json', frame) 


if __name__ == '__main__':
    movie_prosessing(sys.argv[1], sys.argv[2], sys.argv[3])
