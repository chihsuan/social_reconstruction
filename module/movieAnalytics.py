import sys
import cv2
import cv2.cv as cv
import time
import numpy as np
from lib.Frame import *
from lib.Keyword import *
from lib.Face import *
from lib.Point import *
from lib.Pthread import *


FLANN_INDEX_KDTREE = 0

def getFaceAndKeyword():

    faceList = []
    keywords = []
    frameNumber = 0
    faceCount = 1
    faceID = 0
    count = 1

    with open('output/bipartiteGraph.txt', 'r') as graph:

        lines = graph.readlines()

        for line in lines:
                #before go to next frame
            if not line.strip():
                frameNumber = 0
                count = 1
                continue
            if count == 1:
                keyword = line[0:len(line)-1]
                keywords.append(keyword)
                #get frame
            elif line[0] != '[':
                frameNumber = line[0:len(line)-1]
                #frames.append( Frame(line[0:len(line)-1]) )
                faceCount = 1
            else:
                #get face position
                facePosition = line[1:len(line)-2].split()
                #read image
                img = cv2.imread("output/img/" + str(frameNumber) + 
                        "-" + str(faceCount)  + ".jpg" ,0)
                
                faceList.append(Face(facePosition, faceID, frameNumber, img, keyword))
                faceCount += 1
                faceID += 1
            count += 1
  
    return faceList, keywords


def mergeByPosition(face1, face2):

    if( abs(face1.getFrame() - face2.getFrame()) > 24 ) or face1.character == face2.character:
        return False
    else:
        Pos1 = face1.getPosition()
        Pos2 = face2.getPosition()
        #print Pos1, Pos2
        if abs(Pos1.x1 - Pos2.x1) < 5 and abs(Pos1.x2 - Pos2.x2) < 5 and abs(Pos1.y1 - Pos2.y1) < 5 and abs(Pos1.y2 - Pos2.y2) < 5:
            face2.character = face1.character
            return True
    return False



def init_feature():

    # Initiate ORB detector
    detector = cv2.ORB(400)
    norm = cv2.NORM_HAMMING
    flann_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    matcher = cv2.FlannBasedMatcher(flann_params, {})
    return detector, matcher


def faceMatch(match_count, face1, face2):
    
    #cv2.imshow("1", face1)
    #cv2.imshow("2", face2)
    #time.sleep(1)
    if cv2.waitKey(10)  == 27:
         sys.exit(1)
         
    detector, matcher = init_feature()

    kp1, desc1 = detector.detectAndCompute(face1, None)
    kp2, desc2 = detector.detectAndCompute(face2, None)


    matches = matcher.knnMatch(np.asarray(desc1,np.float32),np.asarray(desc2,np.float32), 2)
    #matches = matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2) #2

    # store all the good matches as per Lowe's ratio test.
    good = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)

    if len(good) > match_count:
        print "match!"
        return True
    else:
        #print "Not enough matches are found - %d/%d" % (len(good), match_count)
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

def mergeByFaceMatch(faceLists, startPoint, endPoint):

    for i in range(startPoint, endPoint):
        print i
        for j in range(i+1, endPoint):
            matchCount = 0
            for face1 in faceLists[ key[i] ]:
                for face2 in faceLists[ key[j] ]:
                    if faceMatch(10, face1.getImg(), face2.getImg()):
                        matchCount += 1   
                        if matchCount == 2:
                            faceLists[ key[i] ] += faceLists[ key[j] ] 
                            faceLists[ key[j] ] = []
                            break
                if matchCount == 2:
                    break

if __name__ == '__main__':

    count = 0
    faceList, keywords = getFaceAndKeyword()


    #step1 find face in near position
    if len(sys.argv) > 1:
        for i in range(0, len(faceList) - 1):
            for j in range(i, len(faceList) - 1):
                if mergeByPosition(faceList[i], faceList[j]):
                        count += 1
                else:
                    continue
        outputCharacter(faceList)
    else:    
        readCharacter(faceList)

    
    #step2 merge faceList by above result
    global faceLists
    faceLists = {}
    key = []
    for face in faceList:
        if face.character not in faceLists:
            faceLists[face.character] = []
        faceLists[face.character].append(face)
        key.append(face.character)

    global threadLock 
    threadLock = threading.Lock()
    threads = []
    thread1 = Pthread(1, 'Thread-1', 0, (len(faceLists)/2) )
    thread2 = Pthread(2, 'Thread-2', (len(faceLists)/2+1), (len(faceLists)-1))
    #step3 merge faceList by face match
    thread1.start()
    thread2.start()

    threads.append(thread1)
    threads.append(thread2)

    for thread in threads:
        thread.join()
    '''
    count = 0
    for facelist in faceLists:
        if len(facelist) > 0:
            count +=1
    print count
    #start find relation
    '''
    
    '''
    for keyword in bipartiteGraph:

        #sort frame by frame position
        bipartiteGraph[keyword].sort(key=lambda frame: frame.framePosition)
        #frames = bipartiteGraph[keyword]
        frames = bipartiteGraph[keyword]
        for i in range(0, len(frames)-1):
            cv2.imshow("1", frames[i].getFaces()[0].getImg())
            cv2.imshow("2", frames[i+1].getFaces()[0].getImg())
            time.sleep(1)
            print faceMatch(10, frames[i].getFaces()[0].getImg(), frames[i+1].getFaces()[0].getImg()) 
            if cv2.waitKey(10)  != 27:
                break
    '''

