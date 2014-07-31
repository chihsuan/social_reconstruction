import cv2
import cv2.cv as cv

class Point(object):

    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0

    def  __init__(self, position):
        self.x1 = int(position[0])
        self.y1 = int(position[1])
        self.x2 = int(position[2])
        self.y2 = int(position[3])
    
    def __repr__(self):
        return '(' + str(self.x1) + ',' + str(self.y1) + ',' +str(self.x2) + ',' + str(self.y2) + ')'
