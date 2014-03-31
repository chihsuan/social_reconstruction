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


#read  data that was already proceessed
def getFaceAndKeyword(characterNumber, characterImg):

    faceList = []
    keywords = []

    for i in range(0, characterNumber):
        faceList.append(Face([1,2,3,4], i, '0', characterImg[i],  -1, -1))
    print faceList

    with open('output/preprocessedData.txt', 'r') as graph:

        lines = graph.readlines()
        
        flag = 0
        faceID = characterNumber
        for line in lines:
            
            #get keyword
            if line[1] == '[':
                if ',' in line:
                    keyword = line[4: len(line)-3].split('\'')
                    flag = 1
                else:
                    keyword = line[3:len(line)-3]

                if flag!=1 and keyword not in keywords:
                    keywords.append(keyword)
                
            #get keywordID
            elif line[0] == '[':
                keywordID = line[1:len(line)-1]
            
            #get frameNumber
            elif line[0] == '{':
                frameNumber = line[1:len(line)-1]
                faceCount = 0
            #get face position
            else:
                                # string to list
                facePosition = line[1:len(line)-2].split(',')
                
                faceCount += 1
                #read image
                img = cv2.imread("output/img/" + str(frameNumber) + 
                        "-" + str(faceCount)  + ".jpg" ,0)
                if type(keyword) == list:
                    for key in keyword:
                        if ',' not in key:
                            faceList.append(Face(facePosition, faceID, frameNumber, img, key, int(keywordID)))
                            faceID += 1
                else:
                    faceList.append(Face(facePosition, faceID, frameNumber, img, keyword, int(keywordID)))
                    faceID += 1
    
    return faceList, keywords

def mergeByPosition(face1, face2):

    if( abs(face1.getFrame() - face2.getFrame()) > 120 ) or face1.character == face2.character:
        return False
    else:
        Pos1 = face1.getPoint()   
        Pos2 = face2.getPoint()
        #print Pos1, Pos2
        if abs(Pos1.x1 - Pos2.x1) < 10 and abs(Pos1.x2 - Pos2.x2) < 10 and abs(Pos1.y1 - Pos2.y1) < 10 and abs(Pos1.y2 - Pos2.y2) < 10:
            face2.character = face1.character
            return True
    return False


def init_feature():

    # Initiate ORB detector
    #detector = cv2.ORB(400)
    #norm = cv2.NORM_HAMMING
    detector = cv2.SIFT()

    #flann_params= dict(algorithm = FLANN_INDEX_LSH,
     #                  table_number = 6, # 12
      #                 key_size = 12,     # 20
       #               multi_probe_level = 1) #2
    #matcher = cv2.FlannBasedMatcher(flann_params, {})  # bug : need to pass empty dict (#1329)
    
    flann_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    matcher = cv2.FlannBasedMatcher(flann_params, {})
    #matcher = cv2.BFMatcher(norm) 
    return detector, matcher

def filter_matches(kp1, kp2, matches, ratio = 0.75):

    mkp1, mkp2 = [], []
    for m in matches:
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            m = m[0]
            mkp1.append( kp1[m.queryIdx] )
            mkp2.append( kp2[m.trainIdx] )
    p1 = np.float32([kp.pt for kp in mkp1])
    p2 = np.float32([kp.pt for kp in mkp2])
    kp_pairs = zip(mkp1, mkp2)
    
    return p1, p2, kp_pairs



def faceMatch(minCount, face1, face2):
    
    
    if face1.getID() not in descripterSet:
        kp1, desc1 = detector.detectAndCompute(face1.getImg(), None)
        descripterSet[face1.getID()] = desc1
        featureSet[face1.getID()] = kp1
    else:    
        desc1 = descripterSet[face1.getID()]
        kp1 = featureSet[face1.getID()]
    
    if face2.getID() not in descripterSet: 
        kp2, desc2 = detector.detectAndCompute(face2.getImg(), None)
        descripterSet[face2.getID()] = desc2
        featureSet[face2.getID()] = kp2
    else:
        desc2 = descripterSet[face2.getID()]
        kp2 = featureSet[face2.getID()]
    

    #kp1, desc1 = detector.detectAndCompute(face1.getImg(), None)
    #kp2, desc2 = detector.detectAndCompute(face2.getImg(), None)
    #print 'img1 - %d features, img2 - %d features' % (len(kp1), len(kp2))

    raw_matches = matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2) #2
    #raw_matches = matcher.knnMatch(np.asarray(desc1,np.float32),np.asarray(desc2,np.float32), 2)
    p1, p2, kp_pairs = filter_matches(kp1, kp2, raw_matches)
    if len(p1) >= 4:
            H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
            #print '%d / %d  inliers/matched' % (np.sum(status), len(status))
            if len(status) > minCount:
                print 'Match', face1.getID(), face2.getFrame()
                return True
            else:
                return False
    else:
            H, status = None, None
            #print '%d matches found, not enough for homography estimation' % len(p1)
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

'''
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
                if faceMatch(minCount, face1, face2):
                    matchCount += 1   
                    if matchCount == mergeCount:
                        print j
                        weightDic[ key[i] ] += weightDic[ key[j] ] 
                        #print key[i], key[j]
                        weightDic[ key[j] ] = []
                        faceLists[ key[i] ] += faceLists[ key[j] ]
                        faceLists[ key[j] ] = []
                        matchCount = 0
                        break
           # if matchCount == mergeCount:
            #    matchCount = 0
             #   break
'''

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
            #if character!= '' and int(character) < 5:
            while lines[i].strip():
                    line = lines[i]
                    mergeList[ int(line[:len(line)-1])] = store[int(line[: len(line)-1])]
                    mergeList[ int(line[:len(line)-1]) ].character = character  
                    i += 1
            i += 1
                  
if __name__ == '__main__':

    global faceLists, detector, matcher 
    global descripterSet, featureSet
    global key
    global weightDic
    weightDic = {}
    descripterSet = {}
    featureSet = {}
    mergeList = {}
  
    characterImg, characterNumber = loadCharacter()

    
    #get data from preprocessing.py ouputfile
    faceList, keywords = getFaceAndKeyword(characterNumber, characterImg)

    store = {}
    for face in faceList:
        store[face.getID()] = face 

    print 'start'

    #step1 find face in near position
    if len(sys.argv) > 3:
        #print 'Step1 find face in near position'
        print 'Step1 merge faceList by position'
        for i in range(characterNumber, len(faceList) - 1):
            for j in range(i, len(faceList) - 1):
                mergeByPosition(faceList[i], faceList[j])
        outputCharacter(faceList)
    else:  
        print 'read'
        readCharacter(faceList)

    if len(sys.argv) > 1:
        #print 'Step2 merge faceList by position'
        #step2 merge faceList -> faceLists by above result
        
        
        faceLists = {}
        #key = []
        
        '''
        for face in faceList:
            if face.character not in faceLists:
                faceLists[face.character] = []
            if face.character not in weightDic:
                weightDic[face.character] = []
                weightDic[face.character].append(face)
            else:
                flag = 0
                for character in weightDic[face.character]:
                    if face.keywordID == character.keywordID:
                        flag = 1  # already in list
                if flag == 0:
                    weightDic[face.character].append(face)
            faceLists[face.character].append(face)
            key.append(face.character)
        '''
        
        for face in faceList:
            if face.keyword not in faceLists:
                faceLists[face.keyword] = []
            faceLists[face.keyword].append(face)      

        print len(faceLists)

    if len(sys.argv) > 2: 

        print 'Step3 merge faceList by match'
        detector, matcher = init_feature()
        
        #initailize mutithread
        for i in range(0 ,characterNumber):
            
            if i >= 10:
                minCount = 23
                mergeCount = 1
            elif i >= 5:
                minCount = 12
                mergeCount = 1
            
            elif i >= 2 :
                minCount = 12
                mergeCount = 1
            else:
                minCount = 12
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

        mergeByFaceMatch(faceLists, characterNumber , len(faceLists)-1, 20, 1) 
        #print weightDic
        outputMergeResult(weightDic, 'mergeResult.txt')
        outputMergeResult(faceLists, 'faceLists.txt')
        
    
    print 'Read mergeResult'
    readMergeResult(mergeList, store, 'mergeResult.txt')
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
   
