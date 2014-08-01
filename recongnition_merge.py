'''
This programe is to merge frame by openCV face recongnition
input: position_merge.json
output: recongnition_merge.json
'''
import sys
import threading

import cv2
import cv2.cv as cv

from modules import json_io
from modules import cv_face 

OUTPUT_PATH = 'output/'

class Pthread (threading.Thread):

    def __init__(self, threadID, name, frame_list, threadLock):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.frame_list = frame_list
        self.threadLock = threadLock

    def run(self):
        print 'Thread ' +  self.name + ' start'
        self.threadLock.acquire()
        face_recongnition(self.frame_list)
        self.threadLock.release()


def recongnition_merge(position_merge_file):
    
    frame_list = json_io.read_json(position_merge_file) 

    # Read face image
    for frame in frame_list:
       img_name = frame_list[frame]['keyword'].encode('utf8') + str(frame_list[frame]['frame_position']) + '.jpg'
       frame_list[frame]['img'] = cv2.imread( OUTPUT_PATH + "img/" + img_name , 0)
   
    # transforamt to keyword as key 
    keyword_list = {}
    for frame in frame_list:
        keyword = frame_list[frame]['keyword']
        face_id = frame_list[frame]['face_id']
        if keyword not in keyword_list:
            keyword_list[keyword] = {}
        
        if face_id not in keyword_list[keyword]:
            keyword_list[keyword][face_id] = []
        keyword_list[keyword][face_id].append(frame_list[frame])
    
    for keyword, frame_list in keyword_list.iteritems():
        print keyword
        for frame in frame_list:
            for face in frame_list[frame]:
                print face['ID'],
                print face['img'],
            print 

    threadLock = threading.Lock() 
    thread_count = 0 
    threads = []
    match_rate = {}

    for keyword, frame_list in keyword_list.iteritems():
        thread = Pthread(thread_count, 'Thread-'+str(thread_count), frame_list, threadLock)
        thread.start()
        threads.append(thread)
        thread_count += 1


    #wait all threads complete 
    for thread in threads:
        thread.join()


    for keyword, frame_list in keyword_list.iteritems():
        print keyword
        for frame in frame_list:
            for face in frame_list[frame]:
                if face:
                    print face['ID'],
                    del face['img']
            print 

    json_io.write_json('recongnition_merge.json', keyword_list)


def face_recongnition(frame_list):

    keys = frame_list.keys()
    for i in range(0, len(frame_list)):
        for j in range(i + 1, len(frame_list)):
            face_list1 = frame_list[keys[i]]
            face_list2 = frame_list[keys[j]]
            if cv_face.list_match(10, face_list1, face_list2):
                face_list1 += face_list2
                face_list2 = []
                print keys[i], keys[j]
                print face_list1


if __name__ == '__main__':
    recongnition_merge(sys.argv[1])
