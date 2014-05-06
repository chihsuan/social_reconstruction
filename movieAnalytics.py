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
        threadLock.acquire() 
        #merge faceLists
        mergeByFaceMatch(self.keyword, self.startPoint, self.finishPoint, self.minCount, self.mergeCount) 
        threadLock.release()


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


def findRelationship():
   
    relationList = {}
    wordClassified.append(leadingKeyword)
    exclude = [leadingKeyword]
    for keyword in keywordDic:
            tmpList, tmpClassified = faceClassification(faceList, keyword, 3, exclude)
            exclude.append(keyword)
            relationList[keyword] = tmpClassified[:]
            print keyword, relationList[keyword]
    
    return relationList

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



def outputJson(characterList):
   
    #for record pair of character and node ID
    characterNode = {}

    #bulid nodes
    nodes = []
    i = 0
    for character in characterList:
        if character.keyword in characterNode:
            continue
        else:
            nodes.append({'group':i, 'name': character.keyword, 'ID': i })
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

    #json dumps
    print json.dumps({ 'nodes':nodes, 'links': edges})
 
    #output json file
    with open(OUTPUT_PATH + '/result/data.json', 'w') as outfile:
        json.dump({'nodes':nodes, 'links': edges}, outfile, indent = 4)



def outputResultImage(characterList, characterSort):

    for word in characterSort:
        count = -1
        if '-' in word:
            keyword = word.split('-')[1]
        else:
            keyword = word
       
        for character in characterSort[word]:
            if count >= 1:
                img = cv2.imread(OUTPUT_PATH + '/img/' + str(character.getFrame()) + '-' + '1.jpg' )
                cv2.imwrite(OUTPUT_PATH + '/result/' + keyword + str(count) + '.jpg', img)
            count += 1

    for character in characterList:
        point = character.getPoint()
        img = character.getImg()
        face = img
        face = cv2.imread(OUTPUT_PATH + '/img/' + str(character.getFrame()) + '-' + '1.jpg' )
        #face = img[point.y1:point.y2, point.x1:point.x2]
        cv2.imwrite(OUTPUT_PATH + '/result/' + str(character.keyword) + '0.jpg', face)
        cv2.imwrite(OUTPUT_PATH + '/character/' + str(character.keyword) + '.jpg', face)


if __name__ == '__main__':


    #initailize data object
    movieData  = MovieData( OUTPUT_PATH + 'preprocessedData.txt')
    #get data from preprocessing.py ouputfile
    faceList, keywords = movieData.getFaceAndKeyword(0, OUTPUT_PATH)
    print 'Face Number=', len(faceList)   
    
    #initailize faceCV object
    faceCV = FaceCV(len(faceList))
    detector, matcher = faceCV.init_feature('sift')
    

   
    # see whether the face keyword and image are matched
    store = {}
    for face in faceList:
        store[face.getID()] = face 
        cv2.imwrite(OUTPUT_PATH + '/tmp/' + face.keyword + str(face.getID()) + '.jpg', face.getImg() )
     
     
    #step1 find face in near position
    print 'Step1 merge faceList by position'
    for i in range(0, len(faceList) ):
        for j in range(i, len(faceList) ):
            mergeByPosition(faceList[i], faceList[j])

    
    #step2 find the leadingRole's keyword
    print 'step2 find the leadingRole\'s keyword'
    keywordDic = {}
    for face in faceList:
        if face.keyword not in keywordDic:
            keywordDic[face.keyword] = []
        keywordDic[face.keyword].append(face)
   
    # get the leadingRole's keyword
    tmp = 0
    for key in keywordDic:
        if len(keywordDic[key]) > tmp:
            tmp = len(keywordDic[key])
            leadingKeyword = key
    
    print leadingKeyword 

    print 'step3 start find the relation graph'

    #sort face by frame position
    faceList.sort(key = lambda x: x.getFrame())

    #classfiy if a time interval only has keyword and leadingKeyword (relation)
    classifiedList, wordClassified =  faceClassification(faceList, leadingKeyword, 0.5, [])
    
    #add leadingRoleList to list
    classifiedList[leadingKeyword] = keywordDic[leadingKeyword]
    
    #add keyword that did not add before
    for key in keywordDic:
        if key not in wordClassified:
            print key
            classifiedList[key] = keywordDic[key]
    
    #find other character and another character's relation
    relationList = findRelationship()

    #build a faceLists (graph) by keyword and characterID
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


    print 'Step4 merge faceList by match'
    #initailize mutithread
    minCount = 5
    mergeCount = 1
    threadID = 0

    
    keywords = keywordDic.keys()
    threadLock = threading.Lock()
    threads = []
    for keyword in faceLists:
        if keyword == leadingKeyword:
            continue
        thread = Pthread(threadID, 'Thread-'+ str(threadID), keyword, 0, len(faceLists[keyword].keys()), minCount, mergeCount)
        threadID += 1
        thread.start()
        threads.append(thread)
  
    mergeByFaceMatch(leadingKeyword, 0, len(faceLists[leadingKeyword].keys()), 15, mergeCount)

    #wait all threads complete 
    for thread in threads:
        thread.join()

    #step5 start anlaytic
    print 'step5 start anlaytic find character'
    bipartitleGraph = faceLists
    characterList = []
    
    #find leading role
    sortList =  sorted(bipartitleGraph[leadingKeyword], key = lambda k: len(bipartitleGraph[leadingKeyword][k]), reverse = True) 
    leadingRole = bipartitleGraph[leadingKeyword][sortList[0]] + bipartitleGraph[leadingKeyword][sortList[1]] 
   
    #output leadingRole img
    for i in range(0, len(leadingRole)):
        cv2.imwrite(OUTPUT_PATH + '/leadingRole/' + leadingKeyword + str(i) + '.jpg'  , leadingRole[i].getImg())

    
    characterSort = {}
    #find the keyword relation top2 (character1 character2)
    for word in bipartitleGraph:
        if word == leadingKeyword:
            continue
        print word,
        sortList =  sorted(bipartitleGraph[word], key = lambda k: len(bipartitleGraph[word][k]), reverse = True) 
       
        characterSort[word] = []
        for i in sortList:
            if len(bipartitleGraph[word][i]) > 0:
                characterSort[word].append( bipartitleGraph[word][i][0] )


        if len(characterSort[word]) > 1:
            
            #add character1
            character1 = characterSort[word][0]
            characterList.append(character1)
           
            #add character2 who is not similarity to character1
            move = 1
            while move < len(sortList):
                character2 = characterSort[word][move]
                move += 1
                if faceCV.match(20, character1, character2) or faceCV.match(20, character1, character2):
                    continue
                else:
                    break
            if move != len(sortList):
                characterList.append(character2)
            else:
                characterList.append(characterSort[word][1])
            if move != 1:
                temp = characterSort[word][1]
                characterSort[word][1] = characterSort[word][move-1]
                characterSort[word][move-1] = temp
            print move

    
    #use leadingRole face match rate to decide character1 and character2 which is leadingRole
    detector, matcher = faceCV.init_feature('orb') 
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

    print 'output result...'
    #output the final result
    outputJson(characterList)
    outputResultImage(characterList, characterSort)
