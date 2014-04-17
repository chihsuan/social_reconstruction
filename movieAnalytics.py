'''
movieAnalytic.py

Read movie face data / keyword data / image to find relation between characters
'''
import sys
import cv2
import cv2.cv as cv
import csv
import json
import time
import threading
import numpy as np
import copy
from lib.Frame import *
from lib.Keyword import *
from lib.Face import *
from lib.Point import *
from lib.MovieData import *
from lib.FaceCV import *
from lib.faceMatch import *


FLANN_INDEX_KDTREE = 1
FLANN_INDEX_LSH    = 6

#which directory the result to output
OUTPUT_PATH = 'output/'


# mutithread for increase speed
class Pthread (threading.Thread):
    
    
    def __init__(self, threadID, name, keyword,startPoint, finishPoint, minCount, mergeCount):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.startPoint = startPoint
        self.finishPoint = finishPoint
        self.minCount = minCount
        self.mergeCount = mergeCount
        self.keyword = keyword

    def run(self):
        global faceLists
        print self.name + ' start'
        
        #merge faceLists
        mergeByFaceMatch(self.keyword, self.startPoint, self.finishPoint, self.minCount, self.mergeCount) 



# merge different face but maybe same character
def mergeByPosition(face1, face2):

    if( abs(face1.getFrame() - face2.getFrame()) > (24*30) ) or face1.character == face2.character:
        return False
    else: 
        # near frame
        Pos1 = face1.getPoint()   
        Pos2 = face2.getPoint()
        
        #tolerate distance for merge
        if abs(Pos1.x1 - Pos2.x1) < 20 and abs(Pos1.x2 - Pos2.x2) < 25 and abs(Pos1.y1 - Pos2.y1) < 25 and abs(Pos1.y2 - Pos2.y2) < 20:
            face2.character = face1.character
            return True
    return False

#output the above result for not do the same thing when we dont' change the code 
def outputCharacter(faceList):

    #Output character in bipartiteGraph as file
    with open ( OUTPUT_PATH+ 'character.txt', 'w') as outputResult:
        for face in faceList:
            outputResult.write( str(face.character) + "\n")

#read the above result
def readCharacter(faceList):

    characters = []
    with open(OUTPUT_PATH + 'character.txt', 'r') as readFile:
        lines = readFile.readlines()
        for line in lines:
            characters.append(line[:len(line)-1])

    i = 0
    for face in faceList:
        face.character = int(characters[i])
        i+=1


#merge by Imaging Technology
def mergeByFaceMatch(keyword, startPoint, endPoint, minCount, mergeCount):
  
    remove = []
    key = []
    for character in faceLists[keyword]:
        key.append(character)
    
    endPoint = len(faceLists[keyword]) 
    try:
        matchCount = 0
        for i in range(startPoint, endPoint):
            for j in range(startPoint, endPoint):
                if i == j:
                    continue
                for face1 in faceLists[keyword][key[i]]:
                    for face2 in faceLists[keyword][key[j]]:
                        if faceCV.match(minCount, face1, face2) and faceCV.match(minCount, face2, face1):
                            print 'merge!'
                            print keyword
                            matchCount += 1  
                            if matchCount == mergeCount:
                                faceLists[keyword][key[i]] += faceLists[keyword][key[j]]
                                faceLists[keyword][key[j]] = []
                                remove.append(j)
                                break
                    if matchCount == mergeCount:
                        matchCount = 0
                        break
    except:
        tp, val, tb = sys.exc_info()
        print  sys.stderr, str(tp), str(val)
    for j in remove:
        del faceLists[keyword][key[j]]

def outputMergeResult(faceLists, fileName):

    with open (OUTPUT_PATH + str(fileName), 'w') as outputResult:
        for keyword in faceLists:
            for character in faceLists[keyword]:
                if  len(faceLists[keyword][character]) >= 1 :
                    outputResult.write( str(faceLists[keyword][character][0].character) + "\n")
                    for face in faceLists[keyword][character]: 
                        outputResult.write( str(face.getID()) + "\n" )
                    outputResult.write( "\n" )

def readMergeResult(mergeList, store, fileName):
    
    with open(OUTPUT_PATH +fileName, 'r') as readFile:
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
                 

def faceClassification(faceList, pivotKeyword, minute, exclude):
    
    hasPivotKeyword = False
    currentWord = pivotKeyword
    currentFrame = faceList[0].getFrame()
    faceLists = {}
    addIndex = []
    currentWordCount = 0
    wordClassified = []

    for i in range(0, len(faceList)):
        if faceList[i].keyword in exclude:
            continue

        if faceList[i].keyword == pivotKeyword:
            hasPivotKeyword = True
            #addIndex.append(i)
        elif faceList[i].keyword == currentWord:
            addIndex.append(i)
            currentWordCount += 1

        if faceList[i].getFrame() > (currentFrame + 24*60*minute) and hasPivotKeyword and currentWord != pivotKeyword and currentWordCount > 1:
            if  (pivotKeyword + '-' +  currentWord) not in faceLists:
                faceLists[pivotKeyword + '-' + currentWord] = []
            if currentWord not in wordClassified:
                wordClassified.append(currentWord)

            for index in addIndex:
                face = faceList[index].copy()
                face.keyword = pivotKeyword + '-' + currentWord
                faceLists[pivotKeyword + '-' + currentWord].append(face)
            #print pivotKeyword + '-' + currentWord
            #print faceLists[ pivotKeyword + '-' + currentWord]
            addIndex = []


        if faceList[i].keyword != pivotKeyword \
                and faceList[i].keyword != currentWord:
            currentWord = faceList[i].keyword
            currentFrame = faceList[i].getFrame()
            if currentWord != pivotKeyword:
                hasPivotKeyword= False
                addIndex = []
                currentWordCount = 0 


    '''for key in faceLists:
        for face in faceLists[key]:
            face.keyword = key'''

    return faceLists, wordClassified    


def findCharacter(faceList, nameKeyword, sec):

    addIndex = []
    nameList = []
    currentFrame = faceList[0].getFrame()
    hasNameKeyword = False

    for i in range(0, len(faceList)):
        if faceList[i].keyword != nameKeyword:
            addIndex = []
            currentFrame = faceList[i].getFrame()
            hasNameKeyword = False
            continue
        elif faceList[i].keyword == nameKeyword:
            addIndex.append(i) 
            hasNameKeyword = True
        
        if faceList[i].getFrame() > (24*sec + currentFrame) and hasNameKeyword:
            print 'Add face to', nameKeyword
            for index in addIndex:
                face = faceList[index].copy()
                nameList.append(face)
            #print nameList 
            currentFrame = faceList[i].getFrame()
            addIndex = []
    return nameList  


if __name__ == '__main__':


    global faceLists 
    global faceCV 
    mergeList = {}

    #initailize
    movieData  = MovieData( OUTPUT_PATH + 'preprocessedData.txt')
    
    #get data from preprocessing.py ouputfile
    faceList, keywords = movieData.getFaceAndKeyword(0, OUTPUT_PATH)
    print 'Face Number=', len(faceList)   
    
    faceCV = FaceCV(len(faceList))
    detector, matcher = faceCV.init_feature('sift')
    

    store = {}
    for face in faceList:
        store[face.getID()] = face 
        cv2.imwrite(OUTPUT_PATH + '/tmp/' + face.keyword + str(face.getID()) + '.jpg', face.getImg() )
        
    keywordDic = {}
    for face in faceList:
        if face.keyword not in keywordDic:
            keywordDic[face.keyword] = []
        keywordDic[face.keyword].append(face)
   
    tmp = 0
    for key in keywordDic:
        if len(keywordDic[key]) > tmp:
            tmp = len(keywordDic[key])
            leadingKeyword = key
    keywords = keywordDic.keys()


    #keywords.sort( key = keywordDic.__getitem__)
    print leadingKeyword 
   
    #step1 find face in near position
    if len(sys.argv) > 3:
        print 'Step1 merge faceList by position'
        for i in range(0, len(faceList) ):
            for j in range(i, len(faceList) ):
                mergeByPosition(faceList[i], faceList[j])
        outputCharacter(faceList)
    else:    
        readCharacter(faceList)

    if len(sys.argv) > 1:
        
        #print 'Step2 merge faceList by position'
        #step2 merge faceList -> faceLists by above result

        #sort face by frame position
        faceList.sort(key = lambda x: x.getFrame())
        for face in faceList:
            print face.getFrame(),
 

        #classfiy if a time interval only has keyword and leadingKeyword 
        classifiedList, wordClassified =  faceClassification(faceList, leadingKeyword, 0.5, [])
        
        #add leadingRoleList to list
        classifiedList[leadingKeyword] = keywordDic[leadingKeyword]
        
        
        relationList = {}
        wordClassified.append(leadingKeyword)
        exclude = [leadingKeyword]

        for keyword in keywordDic:
                tmpList, tmpClassified = faceClassification(faceList, keyword, 3, exclude)
                exclude.append(keyword)
                relationList[keyword] = tmpClassified[:]
                print keyword, relationList[keyword]

        #add keyword that did not add before
        for key in keywordDic:
            if key not in wordClassified:
                print key
                classifiedList[key] = keywordDic[key]

        #build a faceLists dictionary by keyword and characterID
        faceLists = {}
        for key in classifiedList:
            for face in classifiedList[key]:
                if face.keyword not in faceLists:
                    faceLists[face.keyword] = {}
                if face.character not in faceLists[face.keyword]:
                    faceLists[face.keyword][face.character] = []
                    faceLists[face.keyword][face.character].append(face)
                else:
                     faceLists[face.keyword][face.character].append(face)


    if len(sys.argv) > 2: 

        print 'Step3 merge faceList by match'
    
        
        #initailize mutithread
        minCount = 5
        mergeCount = 1
        threadID = 0

        
        threads = []
        for keyword in faceLists:
            if keyword == leadingKeyword:
                continue
            thread = Pthread(threadID, 'Thread-'+ str(threadID), keyword, 0, len(faceLists[keyword].keys()), minCount, mergeCount)
            threadID += 1
            thread.start()
            threads.append(thread)
      
        mergeByFaceMatch(leadingKeyword, 0, len(faceLists[leadingKeyword].keys()), 20, mergeCount)

        #wait all threads complete 
        for thread in threads:
            thread.join()
         

        outputMergeResult(faceLists, 'faceLists.txt')

    readMergeResult(mergeList, store, 'faceLists.txt')
    print len(mergeList)

    #step4 start anlaytic
    print 'step4 start anlaytic'


    #build bipartitleGraph
    '''
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
    '''

    bipartitleGraph = faceLists

    characterList = []
    print 'step5 find character'
    
    #find leading role
    sortList =  sorted(bipartitleGraph[leadingKeyword], key = lambda k: len(bipartitleGraph[leadingKeyword][k]), reverse = True) 
    leadingRole = bipartitleGraph[leadingKeyword][sortList[0]] + bipartitleGraph[leadingKeyword][sortList[1]] 
   
    #output leadingRole img
    for i in range(0, len(leadingRole)):
        cv2.imwrite(OUTPUT_PATH + '/leadingRole/' + leadingKeyword + str(i) + '.jpg'  , leadingRole[i].getImg())
   
    
    #find the keyword relation top2 (character1 character2)
    for word in bipartitleGraph:
        if word == leadingKeyword:
            continue
        print word,
        sortList =  sorted(bipartitleGraph[word], key = lambda k: len(bipartitleGraph[word][k]), reverse = True) 
        print len(bipartitleGraph[word]), len(bipartitleGraph[word][sortList[0]]), len(sortList)

        #output img for refine the result
        name = 0
        for character in sortList:
            if len(bipartitleGraph[word][character]) > 0:
                cv2.imwrite(OUTPUT_PATH + '/sort/' + word + str(name) + '.jpg'  ,bipartitleGraph[word][character][0].getImg())
                name +=1
            

        if len(sortList) > 1 and len(bipartitleGraph[word][sortList[1]]) > 0:
            
            #add character1
            character1 = bipartitleGraph[word][sortList[0]][0]
            characterList.append(character1)
           
            #add character2 who is not similarity to character1
            move = 1
            while move < len(sortList):
                character2 = bipartitleGraph[word][sortList[move]][0]
                move += 1
                if faceCV.match(20, character1, character2) or faceCV.match(20, character1, character2):
                    continue
            if move != len(sortList):
                characterList.append(character2)
            else:
                characterList.append(bipartitleGraph[word][sortList[1]][0])
    
    detector, matcher = faceCV.init_feature('orb') 
    

    #use leadingRole face match rate to decide character1 and character2 which is leadingRole
    for i in range(0, len(characterList), 2):
        print i
        matchCount1 = 0
        matchCount2 = 0
        for face in leadingRole:
            matchCount1 += faceCV.getMatchRate(face, characterList[i])
        for face in leadingRole:
            matchCount2 += faceCV.getMatchRate(face, characterList[i+1])
        

        keywords = characterList[i].keyword.split('-')
        if len(keywords) != 2:
            keywords.append(leadingKeyword)
            keywords.append(keywords[0])
            del keywords[0]
        print keywords
        if matchCount1 > matchCount2:
            characterList[i] = leadingRole[0].copy()
            characterList[i+1].keyword = keywords[1]
        else:
            characterList[i].keyword = keywords[1]
            characterList[i+1] = leadingRole[0].copy()

    # way2
    '''mergeList = {}
    key = []
    ord = {}
    for character in characterList:
        if character.character not in mergeList:
            mergeList[character.character] = []
            mergeList[character.character].append(character)
            key.append(character.character)
            word[character.character] = []
            word[character.character].append(character.keyword)
        else:
            mergeList[character.character].append(character)
            word[character.character].append(character.keyword)

    for i in range(0, len(mergeList)):
        for j in range(i+1, len(mergeList)):
            for face1 in  mergeList[key[i]]:
                for face2 in mergeList[key[j]]:
                    if face1.keyword in word[key[j]] or face1.character == face2.character:        
                        #print face1.keyword, face2.keyword, face1.character, face2.character
                        continue
                    if faceCV.match(5,face1, face2) or faceCV.match(5, face2, face1):
                        print 'same2 character'            
                        mergeList[key[i]] += mergeList[key[j]]
                        mergeList[key[j]] = []
                        #cv2.imwrite(OUTPUT_PATH  + str(face1.keyword) + '-' + str(face1.character) + '.jpg', face1.getImg())
                        #cv2.imwrite(OUTPUT_PATH  + str(face2.keyword) + '-' + str(face2.character) + '.jpg', face2.getImg())''' 

    '''
    hasMatch = []
    characterNumber = len(characterList)
    for i in range(0, len(characterList)):
        for j in range(i+1, len(characterList)):
            if  characterList[i].keyword != characterList[j].keyword and characterList[i].character!= characterList[j].character and \
                    faceCV.getMatchRate(characterList[i], characterList[j]) > 45: #faceCV.faceMatch(24, characterList[i], characterList[j]):
                print 'same character', characterList[i].character, characterList[j].character
                #cv2.imwrite(OUTPUT_PATH  + str(characterList[i].keyword) + '-' + str(characterList[i].character) + '.jpg', characterList[i].getImg())
                #cv2.imwrite(OUTPUT_PATH  + str(characterList[j].keyword) + '-' + str(characterList[j].character) + '.jpg', characterList[j].getImg())
                if characterList[j].character in hasMatch:
                    characterList[i].character = characterList[j].character
                else:
                    characterList[j].character = characterList[i].character
                    hasMatch.append(characterList[i].character)
                characterNumber -= 1
    '''
   
    '''characterList = []
    for character in mergeList:
        for face in  mergeList[character]:
            face.character = character
            characterList.append(face)
    
    characterList.sort(key = lambda x : x.keyword, reverse = True)

    print'''    

    #bulid nodes
    nodes = []
    characterNode = {}
    
    i = 0
    for character in characterList:
        if character.keyword in characterNode:
            continue
        else:
            nodes.append({'group':i, 'name': character.keyword })
            characterNode[character.keyword] = i
            i += 1

    #bulid edges
    edges = []
    for i in range(0, len(characterList), 2):
        edges.append( {'source': characterNode[characterList[i].keyword], 'target':characterNode[characterList[i+1].keyword], 'value': 5, 'label': characterList[i+1].keyword } ) 
        edges.append( {'source': characterNode[characterList[i+1].keyword], 'target':characterNode[characterList[i].keyword], 'value': 5, 'label': characterList[i].keyword } ) 

    for source in relationList:
        for target in relationList[source]:
            edges.append( {'source': characterNode[source], 'target': characterNode[target], 'value': 5, 'label': target }  )
            edges.append( {'source': characterNode[target], 'target': characterNode[source], 'value': 5, 'label': source }  )


    print json.dumps({ 'nodes':nodes, 'links': edges})
 
    with open(OUTPUT_PATH + '/result/data.json', 'w') as outfile:
        json.dump({'nodes':nodes, 'links': edges}, outfile, indent = 4)


    for character in characterList:
        point = character.getPoint()
        img = character.getImg()
        face = img
        face = cv2.imread(OUTPUT_PATH + '/img/' + str(character.getFrame()) + '-' + '1.jpg' )
        #face = img[point.y1:point.y2, point.x1:point.x2]
        cv2.imwrite(OUTPUT_PATH + '/result/' + str(character.keyword) + '.jpg', face)
    
       # cv2.imwrite(OUTPUT_PATH + '/result/' + str(character.keyword) + '-' + str(character.character) + '2.jpg', img)
       
