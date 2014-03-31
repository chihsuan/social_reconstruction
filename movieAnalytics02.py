import sys
import cv2
import cv2.cv as cv
import csv
import time
import threading
import numpy as np
from lib.Frame import *
from lib.Keyword import *
from lib.Face import *
from lib.Point import *
from lib.MovieData import *
from lib.FaceCV import *


FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing
FLANN_INDEX_LSH    = 6


# mutithread for increase speed
class Pthread (threading.Thread):
    
    threadLock = threading.Lock()
    
    def __init__(self, threadID, name, startPoint, finishPoint, minCount, mergeCount):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.startPoint = startPoint
        self.finishPoint = finishPoint
        self.minCount = minCount
        self.mergeCount = mergeCount

    def run(self):
        global faceLists
        print self.name + ' start'
        
        #merge faceLists
        mergeByFaceMatch(faceLists, self.startPoint, self.finishPoint, self.minCount, self.mergeCount) 


def mergeByPosition(face1, face2):

    if( abs(face1.getFrame() - face2.getFrame()) > 120 ) or face1.character == face2.character:
        return False
    else:
        Pos1 = face1.getPoint()   
        Pos2 = face2.getPoint()
        #print Pos1, Pos2
        if abs(Pos1.x1 - Pos2.x1) < 25 and abs(Pos1.x2 - Pos2.x2) < 25 and abs(Pos1.y1 - Pos2.y1) < 25 and abs(Pos1.y2 - Pos2.y2) < 25:
            face2.character = face1.character
            return True
    return False


def outputCharacter(faceList):

    #Ouput character in bipartiteGraph as file
    with open ('output/character.txt', 'w') as outputResult:
        for face in faceList:
            outputResult.write( str(face.character) + "\n")

def readCharacter(faceList):

    characters = []
    with open('output/character.txt', 'r') as readFile:
        lines = readFile.readlines()
        for line in lines:
            characters.append(line[:len(line)-1])

    i = 0
    for face in faceList:
        face.character = int(characters[i])
        i+=1

def mergeByFaceMatch(faceLists, startPoint, endPoint, minCount, mergeCount):
   
    matchCount = 0
    for i in range(startPoint, endPoint):
        for j in range(i+1, endPoint):
            for face1 in faceLists[ key[i] ]:
                for face2 in faceLists[ key[j] ]:
                    if faceCV.faceMatch(minCount, face1, face2):
                        matchCount += 1   
                        if matchCount == mergeCount:
                            weightDic[ key2[i] ] += weightDic[ key2[j] ] 
                            weightDic[ key2[j] ] = []
                            faceLists[ key[i] ] += faceLists[ key[j] ]
                            faceLists[ key[j] ] = []
                            break
                if matchCount == mergeCount:
                    matchCount = 0
                    break


def outputMergeResult(faceLists, fileName):

    with open ('output/' + str(fileName), 'w') as outputResult:
        for key in faceLists:
            if  len(faceLists[key]) >= 1 :
                outputResult.write( str(faceLists[key][0].character) + "\n")
                for face in faceLists[key]: 
                    outputResult.write( str(face.getID()) + "\n" )
                outputResult.write( "\n" )

def readMergeResult(mergeList, store, fileName):
    
    with open('output/'+fileName, 'r') as readFile:
        lines = readFile.readlines()

        i = 0
        while i < len(lines)-1:
            line = lines[i]
            character = line[:len(line)-1]        
            while lines[i].strip():
                line = lines[i]
                mergeList[ int(line[:len(line)-1]) ] = store[int(line[: len(line)-1])]
                mergeList[ int(line[:len(line)-1]) ].character = character  
                i += 1
            i += 1
                  
if __name__ == '__main__':

    global faceLists, detector, matcher 
    
    global key
    global weightDic
    weightDic = {}
    mergeList = {}
    global faceCV 

    movieData  = MovieData('preprocessedData.txt')
    #get data from preprocessing.py ouputfile
    faceList, keywords = movieData.getFaceAndKeyword(0)
    
    faceCV = FaceCV(len(faceList))
    detector = faceCV.init_feature()


    store = {}
    for face in faceList:
        store[face.getID()] = face 
        
    #step1 find face in near position
    if len(sys.argv) > 3:
        print 'Step1 merge faceList by position'
        for i in range(0, len(faceList) - 1):
            for j in range(i, len(faceList) - 1):
                mergeByPosition(faceList[i], faceList[j])
        outputCharacter(faceList)
    else:    
        readCharacter(faceList)
   

    if len(sys.argv) > 1:
        
        print 'Step2 merge faceList by position'
        #step2 merge faceList -> faceLists by above result
        faceLists = {}
        key = []
        key2 = []
 
        for face in faceList:
            if face.character not in faceLists:
                faceLists[face.character] = []
                key.append(face.character)
            if face.character not in weightDic:
                weightDic[face.character] = []
                weightDic[face.character].append(face)
                key2.append(face.character)
            else:
                flag = 0
                for character in weightDic[face.character]:
                    if face.keywordID == character.keywordID:
                        flag = 1  # already in list
                if flag == 0:
                    weightDic[face.character].append(face)
                    key2.append(face.character)
            faceLists[face.character].append(face)
        '''
        for face in faceList:
            if face.keyword not in faceLists:
                faceLists[face.keyword] = []
            faceLists[face.keyword].append(face)      
        '''
    if len(sys.argv) > 2: 

        print 'Step3 merge faceList by match'
    
        
        #initailize mutithread
        for i in range(24, 0, -6):

            if i >= 10:
                minCount = 45
                mergeCount = 1
            elif i >= 5:
                minCount = 45
                mergeCount = 1
            elif i >= 2 :
                minCount = 45
                mergeCount = 1
            else:
                minCount = 45
                mergeCount = 1

            threads = []
            thread = Pthread(0, 'Thread-1', 0, len(faceLists)/(i+1), minCount, mergeCount)
            thread.start()
            threads.append(thread)
            
            for n in range(1, i-1):
                print n
                thread = Pthread(n, 'Thread-' + str(n+1), len(faceLists)/(i+1)*n+1, len(faceLists)/(i+1)*(n+1), minCount, mergeCount)
                thread.start()
                threads.append(thread)
        
            print 'In main'
            mergeByFaceMatch(faceLists, len(faceLists)/(i+1)*(i-1)+1 , len(faceLists)-1, minCount, mergeCount) 

            #wait all threads complete 
            for thread in threads:
                thread.join()
            print 'round' + str(i)
        
        mergeByFaceMatch(faceLists, 0 , len(faceLists)-1, minCount, mergeCount=1)
        outputMergeResult(weightDic, 'mergeResult.txt')
        outputMergeResult(faceLists, 'faceLists.txt')
    
    readMergeResult(mergeList, store, 'faceLists.txt')
    print len(mergeList)

    #step4 start anlaytic
    print 'step4 start anlaytic'


    #build bipartitleGraph
    bipartitleGraph = {}
    for key in mergeList:
        face = mergeList[key]
        if face.keyword not in bipartitleGraph:
            bipartitleGraph[face.keyword] = {}
        if face.character not in bipartitleGraph[face.keyword]:
            bipartitleGraph[face.keyword][face.character] = []
            bipartitleGraph[face.keyword][face.character].append(face)
        else:
            bipartitleGraph[face.keyword][face.character].append(face)


    print 'step55555 find character'
    for word in bipartitleGraph: 
        print word
        sortList =  sorted(bipartitleGraph[word], key = lambda k: len(bipartitleGraph[word][k]), reverse = True) 
        #print  bipartitleGraph[word][sortList[0]][0].getFrame()
        #print  bipartitleGraph[word][sortList[1]][0].getFrame()

        i = 0
        character1 = bipartitleGraph[word][sortList[0]]
        while i < len(character1):
            kp2, desc2 = detector.detectAndCompute(character1[i].getImg(), None)
            if len(kp2) > 140:
                i+=1
                break    
            i+=1
        
        i-=1
        img1 = character1[i].getImg()

        for j in range(1, len(sortList)):
            character2 = bipartitleGraph[word][sortList[j]][0]
            if not faceCV.faceMatch(40, character1[i], character2):
                img2 = character2.getImg()
                break
            #if len(bipartitleGraph[word][face]) > 1:
                #img = bipartitleGraph[word][face][0].getImg()
                #print len(bipartitleGraph[word][face])
                #print  bipartitleGraph[word][face][0].character          
            
        cv2.imwrite('output/' + word + str(1) + '.jpg', img1)
        cv2.imwrite('output/' + word + str(2) + '.jpg', img2)

        #first = bipartitleGraph[word][sortList[2]][0]
        #sec   = bipartitleGraph[word][sortList[3]][0]
        #img1 = first.getImg()#bipartitleGraph[word][sortList[0]][0].getImg()
        #img2 = sec.getImg()#bipartitleGraph[word][sortList[1]][0].getImg()
        #print len(bipartitleGraph[word][sortList[0]])
        #cv2.imwrite('output/' + word+'1.jpg', img1)
        #cv2.imwrite('output/' + word+'2.jpg', img2)
    
    #cv2.imshow(word+'1',img1)
    #cv2.imshow(word+'2',img2)
    #while cv2.waitKey(10)  != 27:
        #pass
   
