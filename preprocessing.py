'''
preprocessing...
output path

'''
import sys
import cv2
import cv2.cv as cv
import csv
import datetime
import time
import urllib2    
import threading
import os.path
import numpy as np
import itertools
import re
from lib.Frame import *
from lib.Keyword import *
from lib.MovieData import *


OUTPUT_PATH = 'output/'

HAAR_CASCADE_PATH = "input/haarcascades/haarcascade_frontalface_alt.xml"

class Pthread (threading.Thread):
    
    threadLock = threading.Lock()
    
    def __init__(self, threadID, name, searchResult):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.searchResult = searchResult

    def run(self):
        # Get lock to synchronize threads
        # doing
        print self.name + ' start'
        frameCapture(self.searchResult)


def keywordSearch(keywordPath, subtitlePath):
    
    #search result
    searchResult = []

    #Read keyword file and store as list
    keywords = []

    with open(keywordPath, "r") as keywordsFile:
        lines = csv.reader(keywordsFile)
        for row in lines:
            keywords.append(row)
   
    #Read movie subtitle 
    with open(subtitlePath, "r") as subtitleFile:
        subtitle = subtitleFile.readlines()    

    #search keyword 
    sentences = []   # every sentences in time interval
    matchWords = []  
    times = []      # save all time 
    count = -1       # count the match number
    timeID = -1
    flag = 0

    for line in subtitle:
        
        # is empty line (go to next subtitle)
        if not line.strip():

            #regular expression find the match word
            for sentence in sentences:
                for word in keywords[0]:
                    pattern = word.lower()
                    match = re.search(pattern,sentence.lower())
                    if match:
                        matchWords.append(word)
                for word in keywords[1]:
                    pattern = re.compile( word.lower())
                    match = pattern.search(sentence.lower())
                    if match:
                        matchWords.append(word)
            
            # if match the keyword then save it
            if len(matchWords) > 0:
               searchResult.append( Keyword(matchWords, times[timeID]) )
               count += 1
               flag = 1
            matchWords = []
            sentences = []
            continue
    
        # is time interval
        if line[0] == '0':
            times.append(line[:len(line)-3])
            if timeID > 0 and flag == 1:
                searchResult[count].insertLastTime(times[timeID-1])
                searchResult[count].insertNextTime(times[timeID+1])
            elif flag == 1:
                searchResult[count].insertNextTime(time[timeID+1])
            flag = 0
            timeID += 1 
        else:
            sentences.append(line)

    for result in searchResult:
        print result.word,


    return searchResult, keywords        



def get_range(dictionary, begin, end):
      return dict(itertools.islice(dictionary.iteritems(), begin, end+1)) 


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
            
            if framePosition not in framesDic:
                
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
                
            else:
                if framePosition not in frames and len(framesDic[framePosition]) >= 1: #face number >= 1
                    frames[framePosition] = []
                    for face in framesDic[framePosition]:
                        frames[framePosition].append( Face(face.getPosition(), faceID, framePosition, '', keyword.word, keywordID) )
                        faceID += 1 
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

    #if currFrame1 - lastEnd > 24*30*1:
     #   startFrame = currFrame1
      #  print "curr1"
    #if nextStart - currFrame2 > 24*30*1:
     #   finishFrame = currFrame2
      #  print "curr2"

    return startFrame, finishFrame


def convertTimeToframe(theTime):
    
    tmp = time.strptime(theTime.split(',')[0], '%H:%M:%S' )
    frame = int(datetime.timedelta( hours = tmp.tm_hour, minutes = 
                tmp.tm_min, seconds = tmp.tm_sec).total_seconds() * 24)
    
    return frame




def faceDetection(image, framePosition):
    
    faces = []
    
    frame = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
    detected = frame.detectMultiScale(image, 1.1, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (15, 140) )  #40 150  #25, 160
    
    if len(detected) == 0:
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

    print 1
    #background = cv2.imread( OUTPUT_PATH + 'img/0.jpg' )
    
    show = img.copy()
    count = 1
    for (x1, y1, x2, y2) in rects:
        cv2.rectangle(show, (x1-10, y1-10), (x2+5, y2+5), (127, 255, 0), 2) 
        #saveImage = background.copy()
        face = img[y1:y2, x1:x2]
        #saveImage[y1:y2, x1:x2] = face
        #cv2.bitwise_and(saveImage, saveImage, face)
        #cv2.imshow("detected", show)
        saveImage = cv2.resize(face, (150, 150), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite( OUTPUT_PATH + 'img/'+ name + '-' + str(count) + '.jpg', saveImage)
        count +=1

    #cv2.imshow('detected', img)

if __name__=='__main__':
    
    global frames
    global framesDic
    frames = {}
    framesDic = {}
    searchResult = []
    keywords = []
    
    movieData  = MovieData(OUTPUT_PATH + 'preprocessedData.txt')
   
    faceList, key = movieData.getFaceAndKeyword(0, OUTPUT_PATH)
    for face in  faceList:
        if face.getFrame() not in framesDic:
            framesDic[face.getFrame()] = []
            framesDic[face.getFrame()].append(face)
        else:
            framesDic[face.getFrame()].append(face)

    if len(sys.argv) > 3:
        
        #keyword search
        print 'keyword search start'
        searchResult, keywords  = keywordSearch(sys.argv[2], sys.argv[3]) #keyword path, .srt path

        if len(sys.argv) > 2:
           
            threads = []
            for i in range(0, 10):
                thread = Pthread(i, 'Thread-'+str(i), searchResult[ len(searchResult)/10*i : len(searchResult)/10*(i+1)-1 ] )
                thread.start()
                threads.append(thread)
                 
               
            frameCapture(searchResult[ len(searchResult)/10*9 : len(searchResult) ])   

            #wait all threads complete 
            for thread in threads:
                thread.join()
            
            
            print 'success.'
            #Ouput preprocessed data as file
            with open (OUTPUT_PATH + 'preprocessedData.txt', 'w') as outputResult:
                for framePosition in frames:
                    outputResult.write('{' + str(framePosition) + '\n')
                    for face in frames[framePosition]:
                        outputResult.write( 'k' + str(face.keyword) + '\n')
                        outputResult.write( '(' +str(face.keywordID) + '\n')
                        outputResult.write( str(face.getPosition()) + '\n')
    else:
        print "argv[1] is movie input path for face detection" 
