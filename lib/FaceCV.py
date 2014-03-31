import cv2
import cv2.cv as cv
from numpy import *
import numpy as np
FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing
FLANN_INDEX_LSH    = 6


class FaceCV(object):
    
    global featureSet
    global descripterSet
    global matchSet
    featureSet = {}
    descripterSet = {}

    def  __init__(self, faceNumber):
        global matchSet 
        matchSet = [[0 for x in xrange(faceNumber+1)] for x in xrange(faceNumber+1)] 

    def init_feature(self):

        # Initiate ORB detector
        self.detector = cv2.ORB(400)
        flann_params= dict(algorithm = FLANN_INDEX_LSH,
                           table_number = 6, # 12
                           key_size = 12,     # 20
                          multi_probe_level = 1) #2
        self.matcher = cv2.FlannBasedMatcher(flann_params, {})  # bug : need to pass empty dict (#1329)
        return self.detector, self.matcher

    def filter_matches(self, kp1, kp2, matches, ratio = 0.75):

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

    def cropImg(self, img, cropNumber):
        cropped = []
        height, width = img.shape
        height = height/3

        #for i in range(0, cropNumber):
        cropped.append( img[0:height*1, 0:width]  )
        cropped.append( img[height*1:height*3, 0:width]  )

        return cropped
        
    def faceMatch(self, minCount, face1, face2):
       

        if matchSet[face1.getID()][face2.getID()] == 1:
            return False
        else:
            matchSet[face1.getID()][face2.getID()] = 1

        cropFaceList1 = self.cropImg(face1.getImg(), 2)
        cropFaceList2 = self.cropImg(face2.getImg(), 2)

        matchNumber = 0
        for i in range(0, len(cropFaceList1)):
       
            #cv2.imwrite('output/crop/' + str(face1.getID()) + str(i) +'.jpg', cropFaceList1[i])
            kp1, desc1 = self.detector.detectAndCompute(cropFaceList1[i], None)
            kp2, desc2 = self.detector.detectAndCompute(cropFaceList2[i], None)


            #print 'img1 - %d features, img2 - %d features' % (len(kp1), len(kp2))
            if len(kp1) < 1 or len(kp2) < 1: #120 110
                continue

            raw_matches = self.matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2) #2
            
            p1, p2, kp_pairs = self.filter_matches(kp1, kp2, raw_matches)
            if len(p1) >= 4:
                    H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
                    #print  'findHomography' 
                    if len(status) > 0:
                        #print face1.getFrame(), face2.getFrame()
                        #print '%d / %d  inliers/matched' % (np.sum(status), len(status))
                        matchNumber += len(status) 
                   # print '%d matches found, not enough for homography estimation' % len(p1)
        
        if matchNumber >= minCount:
            print 'Match!'
            return True
        
        
        return False


    def match(self, minCount, face1, face2):
       
        if matchSet[face1.getID()][face2.getID()] == 1:
            return False
        else:
            matchSet[face1.getID()][face2.getID()] = 1
    
        if face1.getID() not in descripterSet or face1.getID() not in featureSet:
            kp1, desc1 = self.detector.detectAndCompute(face1.getImg(), None)
            descripterSet[face1.getID()] = desc1
            featureSet[face1.getID()] = kp1
        else:
            kp1 = featureSet[face1.getID()]
            desc1 = descripterSet[face1.getID()]

        if face2.getID() not in descripterSet or face2.getID() not in featureSet:
            kp2, desc2 = self.detector.detectAndCompute(face2.getImg(), None)
            descripterSet[face2.getID()] = desc2
            featureSet[face2.getID()] = kp2
        else:
            kp2 = featureSet[face2.getID()]
            desc2 = descripterSet[face2.getID()]

        if len(kp1) < 50 or len(kp2) < 50: #120 110
            #print 'img1 - %d features, img2 - %d features' % (len(kp1), len(kp2))
            return False

        raw_matches = self.matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2) #2
        
        p1, p2, kp_pairs = self.filter_matches(kp1, kp2, raw_matches)
        if len(p1) >= 4:
                H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
                #print  'findHomography' 
                if len(status) > minCount:
                    #print face1.getFrame(), face2.getFrame()
                    #print '%d / %d  inliers/matched' % (np.sum(status), len(status))
                    print 'Match' 
                    return True
        #print '%d matches found, not enough for homography estimation' % len(p1)
        return False



    def getMatchRate(self,  face1, face2):
            kp1, desc1 = self.detector.detectAndCompute(face1.getImg(), None)
            kp2, desc2 = self.detector.detectAndCompute(face2.getImg(), None)
            raw_matches = self.matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2) #2
            p1, p2, kp_pairs = self.filter_matches(kp1, kp2, raw_matches)
            if len(p1) > 4 and len(p2) > 4:
                H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
                if len(status) > 36:
                    print face1.getFrame(), face2.getFrame()
                    print '%d / %d  inliers/matched' % (np.sum(status), len(status))
                return len(status)
            else:
                return 0
