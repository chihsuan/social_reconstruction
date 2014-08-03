'''
movie preprocessing
input: movie / subtitle / keyword
output: face image / face position / frame / keyword
description: main operation -- 1. keyword search 2. face detection'''

import sys
import cv2
import cv2.cv as cv
import datetime
import time
import urllib2    
import threading
import os.path
import numpy as np
import itertools
import re
import csv
import json

from lib.Frame import *
from lib.Keyword import *
from lib.MovieData import *


OUTPUT_PATH = 'output/'

#face detection learning data source
HAAR_CASCADE_PATH = "input/haarcascades/haarcascade_frontalface_alt.xml"


#thread imporve image processes efficient 
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

def keywordSearch(keywordPath, subtitlePath):

    #search result
    searchResult = []

    #Read keyword file and store as list
    keywords = readKeyword(keywordPath)
    subtitle = readSubtitle(subtitlePath)    

    sentences = []
    time = []
    hasMatch = False
    count = -1

    #start search keyword 
    for eachLine in subtitle:

        matchWords = []
        #empty line(end block)
        if not eachLine.strip():
            #use regular expression find the match word
            for sentence in sentences:
                for word in keywords[0]:
                    pattern = '\\b' + word.lower() + '\\b'
                    match = re.search(pattern,sentence.lower())
                    if match:
                        matchWords.append(word)

            hasMatch = False
            # if match the keyword then save it
            if len(matchWords) > 0:
                searchResult.append( Keyword(matchWords, time[count]) )
                hasMatch = True

            sentences = []
            continue

        #Time information
        if eachLine[0] == '0':
            time.append(eachLine[:len(eachLine)-3])

            if  hasMatch and len(time) > 1:
                searchResult[len(searchResult)-1].insertLastTime(time[count-1])
                searchResult[len(searchResult)-1].insertNextTime(time[count+1])
            elif hasMatch:
                searchResult[len(searchResult)-1].insertNextTime(time[count+1])

            count += 1
        else:
            #content
            sentences.append(eachLine)


    count = 0
    for result in searchResult:
        print result.word

    return searchResult, keywords        


def readSubtitle(subtitlePath):
    #Read movie subtitle 
    with open(subtitlePath, "r") as subtitleFile:
        subtitle = subtitleFile.readlines()    
    return subtitle
#Read keyword file and store as list


def readKeyword(keywordPath):

    #Read keyword file and store as list
    keywords = []
    with open(keywordPath, "r") as keywordsFile:
        lines = csv.reader(keywordsFile)
        for row in lines:
            keywords.append(row)
    keywords[0] += keywords[1]

    return keywords


def frameCapture(searchResult):

    # load video
    videoInput = cv2.VideoCapture(sys.argv[1])
    keywordID = 1
    faceID = 1

    for keyword in searchResult:

        #tansfer time to frame
        startFrame, finishFrame = getFrameInterval(keyword.lastTime, keyword.currTime, keyword.nextTime)

        #set up framePosition
        framePosition = startFrame

        # detect between startFrame and finishFrame
        while framePosition <= finishFrame: 

            #if framePosition not in framesDic:

            videoInput.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, framePosition)
            flag, frame = videoInput.read()
            mutiPosition = []

            #cv2.imwrite( OUTPUT_PATH + 'img/0.jpg', frame)
            #cv2.imshow('frame', frame)
            mutiPosition = faceDetection(frame, framePosition)

            if len(mutiPosition) == 1:
                print keyword.word
                if framePosition in frame:
                    for facePosition in mutiPosition:
                        frames[framePosition].append( Face(facePosition, faceID, framePosition, '', keyword.word, keywordID) )
                        faceID += 1
                else:
                    frames[framePosition] = []
                    for facePosition in mutiPosition:
                        frames[framePosition].append( Face(facePosition, faceID, framePosition, '', keyword.word, keywordID) )
                        faceID += 1

            '''else:
                if framePosition not in frames and len(framesDic[framePosition]) >= 1: #face number >= 1
                    frames[framePosition] = []
                    for face in framesDic[framePosition]:
                        frames[framePosition].append( Face(face.getPosition(), faceID, framePosition, '', keyword.word, keywordID) )
                        faceID += 1 '''
            framePosition += 12
        keywordID += 1
    #close video  
    videoInput.release()


def getFrameInterval(lastTime, currTime, nextTime):

    startFrame = convertTimeToframe(lastTime[:8])

    lastEnd = convertTimeToframe(lastTime[17:])
    currFrame1 = convertTimeToframe(currTime[:8])
    currFrame2 = convertTimeToframe(currTime[17:])

    nextStart = convertTimeToframe(nextTime[:8])
    finishFrame = convertTimeToframe(nextTime[17:])

    print startFrame, finishFrame

    if (currFrame1 - lastEnd) > 24*30:
        startFrame = currFrame1
        print "-curr1-"
    if (nextStart - currFrame2) > 24*30:
        finishFrame = currFrame2
        print "-curr2-"

    return startFrame, finishFrame


def convertTimeToframe(theTime):

    tmp = time.strptime(theTime.split(',')[0], '%H:%M:%S' )
    frame = int(datetime.timedelta( hours = tmp.tm_hour, minutes = 
        tmp.tm_min, seconds = tmp.tm_sec).total_seconds() * 24)

    return frame


def faceDetection(image, framePosition):

    faces = []

    frame = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
    detected = frame.detectMultiScale(image, 1.1, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20, 140) )  #40 150  #25, 160 #20 140

    if len(detected) == 0 or len(detected) > 1:
        return []

    detected[:, 2:] += detected[:, :2]
    name = str(framePosition)
    if not os.path.isfile( OUTPUT_PATH + 'img/'+ name + '-1.jpg'):
        outputFaceImage(detected, image, name)
    for rect in detected:
        faces.append(rect)

    return faces


# save the face detection result
def outputFaceImage(rects, img, name):

    round = cv2.imread( OUTPUT_PATH + 'img/0.jpg' )
    show = img.copy()
    count = 1
    for (x1, y1, x2, y2) in rects:
        cv2.rectangle(show, (x1-10, y1-10), (x2+5, y2+5), (127, 255, 0), 2) 
        #saveImage = background.copy()
        face = img[y1:y2, x1:x2]
        #saveImage[y1:y2, x1:x2] = face
        #cv2.bitwise_and(saveImage, saveImage, face)
        #cv2.imshow("detected", show)
        #cv2.waitKey()
        saveImage = cv2.resize(face, (300, 300), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite( OUTPUT_PATH + 'img/'+ name + '-' + str(count) + '.jpg', saveImage)
        count +=1


if __name__=='__main__':

    frames = {}

    movieData  = MovieData(OUTPUT_PATH + 'preprocessedData.txt')

    faceList, key = movieData.getFaceAndKeyword(0, OUTPUT_PATH)
    framesDic = {}
    for face in  faceList:
        if face.getFrame() not in framesDic:
            framesDic[face.getFrame()] = []
            framesDic[face.getFrame()].append(face)
        else:
            framesDic[face.getFrame()].append(face)

    if len(sys.argv) > 3:

        #keyword search
        print 'keyword search start'
        searchResult, keywords  = keywordSearch(sys.argv[3], sys.argv[2]) #keyword path, .srt path

        #synchronous mutithred
        threadLock = threading.Lock() 
        threads = []
        threadNumber = 3

        for i in range(0, threadNumber):
            thread = Pthread(i, 'Thread-'+str(i), searchResult[ len(searchResult)/threadNumber*i : len(searchResult)/threadNumber*(i+1)-1 ] )
            thread.start()
            threads.append(thread)

        frameCapture(searchResult[ len(searchResult)/threadNumber*(threadNumber-1) : len(searchResult) ])   

        #wait all threads complete 
        for thread in threads:
            thread.join()

        tojson = { }
        print 'success.'
        #Ouput preprocessed data as file
        with open (OUTPUT_PATH + 'preprocessedData.txt', 'w') as outputResult:
            for framePosition in frames:
                tojson[ framePosition ] = []
                for face in frames[framePosition]:
                    tojson[facePosition].append( { 'keyword': str(face.keyword), 'keywordID': str( face.keywordID ), 'position': str(facePosition) } )
            json.dump( [tojson ], outputResult, indent = 4)
    else:
        print "argv[1] is movie input path for face detection"
