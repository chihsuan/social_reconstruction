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

class Pthread (threading.Thread):
    
    threadLock = threading.Lock()
    
    def __init__(self, threadID, name, characterID, startPoint, finishPoint, minCount, mergeCount):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.startPoint = startPoint
        self.finishPoint = finishPoint
        self.minCount = minCount
        self.mergeCount = mergeCount
        self.characterID = characterID
    def run(self):
        global faceLists
        # doing
        print self.name + ' start'
        mergeByFaceMatch(self.characterID, faceLists, self.startPoint, self.finishPoint, self.minCount, self.mergeCount) 
        # Free lock to release next thread

def loadCharacter():
    
    characterImg = []
    with open('input/ch.txt', "r") as keywordsFile:
        lines = csv.reader(keywordsFile)
        for row in lines:
            for character in row:
                characterImg.append( cv2.imread( 'input/' + str(character) + '.jpg', 0))

    return characterImg, len(characterImg)


def mergeByPosition(face1, face2):

    if( abs(face1.getFrame() - face2.getFrame()) > 120 ) or face1.character == face2.character:
        return False
    else:
        Pos1 = face1.getPoint()   
        Pos2 = face2.getPoint()
        #print Pos1, Pos2
        if abs(Pos1.x1 - Pos2.x1) < 20 and abs(Pos1.x2 - Pos2.x2) < 20 and abs(Pos1.y1 - Pos2.y1) < 20 and abs(Pos1.y2 - Pos2.y2) < 20:
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
        face.character = i #int(characters[i])
        i+=1

def mergeByFaceMatch( characterID, faceLists, startPoint, endPoint, minCount, mergeCount):
    
    matchCount = 0
    i   = characterID
    print 'ID =', characterID
    #for i in range(0, 5):
    
    face1 = faceLists[characterID][0]
    cv2.imwrite('output/'+ str(characterID) + '.jpg', face1.getImg())
    for j in range(startPoint, endPoint):
        if j > 4:
            for face2 in faceLists[ key[j] ]:
                if faceCV.faceMatch(minCount, face1, face2):
                    matchCount += 1   
                    if matchCount == mergeCount:
                        weightDic[ key2[i] ] += weightDic[ key2[j] ] 
                        #print key[i], key[j]
                        weightDic[ key2[j] ] = []
                        faceLists[ key[i] ] += faceLists[ key[j] ]
                        faceLists[ key[j] ] = []
                        matchCount = 0
                        break
           # if matchCount == mergeCount:
            #    matchCount = 0
             #   break


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
    characterImg, characterNumber = loadCharacter()
    #get data from preprocessing.py ouputfile
    faceList, keywords = movieData.getFaceAndKeyword(characterNumber)
    tmpe = []
    for i in range(0, characterNumber):
        tmpe.append(Face([0,0,0,0], i, -1, characterImg[i], -1, -1))
        
    print tmpe

    faceList = tmpe + faceList
    faceCV = FaceCV(len(faceList)+1)

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
    
        faceCV.init_feature()
        
        for i in range(0 ,characterNumber):
            
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
            thread = Pthread(characterNumber, 'Thread-1', (i)%characterNumber, 0, len(faceLists)/characterNumber, minCount, mergeCount)
            thread.start()
            threads.append(thread)
            
            for n in range(1, characterNumber-1):
                print n
                thread = Pthread(n, 'Thread-' + str(n+1), (i+n)%characterNumber, len(faceLists)/(characterNumber)*n+1, len(faceLists)/(characterNumber)*(n+1), minCount, mergeCount)
                thread.start()
                threads.append(thread)
        
            print 'In main'
            mergeByFaceMatch((i+4)%characterNumber, faceLists, len(faceLists)/(i+1)*(i-1)+1 , len(faceLists)-1, minCount, mergeCount) 

            #wait all threads complete 
            for thread in threads:
                thread.join()
            print 'round' + str(i)

        #mergeByFaceMatch(faceLists, characterNumber , len(faceLists)-1, 20, 1) 
        #print weightDic
        outputMergeResult(weightDic, 'mergeResult.txt')
        outputMergeResult(faceLists, 'faceLists.txt')
        
    
    print 'Read mergeResult'
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


    #find relation
    for word in bipartitleGraph: 
        print word
        if word == -1:
            continue
        sortList =  sorted(bipartitleGraph[word], key = lambda k: len(bipartitleGraph[word][k]), reverse = True) 
        #print  bipartitleGraph[word][sortList[0]][0].getFrame()
        #print  bipartitleGraph[word][sortList[1]][0].getFrame()
        first = int(bipartitleGraph[word][sortList[0]][0].character)
        second = int(bipartitleGraph[word][sortList[1]][0].character)
        img1 = faceList[first].getImg()
        img2 = faceList[second].getImg()
        print len(bipartitleGraph[word][sortList[0]])
        cv2.imwrite('output/' + word+'1.jpg', img1)
        cv2.imwrite('output/' + word+'2.jpg', img2)
    
    
    #cv2.imshow(word+'1',img1)
    #cv2.imshow(word+'2',img2)
    #while cv2.waitKey(10)  != 27:
        #pass
   
   
