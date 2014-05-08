import cv2
import cv2.cv as cv
from Point import *

class Face(object):

    character = -1
    #keyword = ''
    keywordID = 0
    matchID = 0


    def copy(self):
        return Face(self.getPosition(), self.ID, self.frame, self.img, self.keyword, self.keywordID )

    def  __init__(self, position, ID, frame, img, keyword, keywordID):
        self.character = ID
        self.ID = ID
        self.position = Point(position)
        self.frame = frame
        self.img = img
        self.keyword = keyword
        self.keywordID = keywordID

    def __repr__(self):
        return str(self.ID)

    def setID(self, ID):
        self.ID = ID
    
    def getID(self):
        return  int(self.ID)

    def getFrame(self):
        return int(self.frame)

    def getPosition(self):
        return [self.position.x1, self.position.y1, self.position.x2, self.position.y2]

    def getPoint(self):
        return self.position

    def getImg(self):
        return self.img

    def getCharacter(self):
        return self.character

    def getKeywordID(self):
        return self.keywordID

    def getPoint(self):
        return self.position

    def setKeyword(self, keyword):
        self.keyword = keyword
