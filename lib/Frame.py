from Face import *
import cv2
import cv2.cv as cv


class Frame(object):
    
    faceID = 1

    def __init__(self, framePosition):
        self.framePosition = framePosition
        self.faceList = []
        self.faceNumber = 0

    def __repr__(self):
        return str(self.framePosition)

    def insertKeywords(self, keywords, keywordID):
        self.keywords = keywords
        self.keywordID = keywordID

    def insertFace(self, face):
        self.faceList.append(Face(face, self.faceID, self.framePosition)) 
        self.faceID +=1
        self.faceNumber += 1
    
    
    def insertFace(self, face, img):
        self.faceList.append( Face(face, self.faceID, self.framePosition, img) ) 
        self.faceID +=1
        self.faceNumber += 1

    def insertFaces(self, faces):
        for face in faces:
            self.faceList.append(Face(face, self.faceID, self.framePosition, '', self.keywords, self.keywordID)) 
            self.faceID +=1
        self.faceNumber += len(faces)

    
    def getFacePosition(self, faceID):
        return self.faceList[faceID].getPosition()
    
    def getFaces(self):
        return self.faceList 
    
    def getKeywords(self):
        return self.keywords

    def getFramePosition(self):
        return self.framePosition
