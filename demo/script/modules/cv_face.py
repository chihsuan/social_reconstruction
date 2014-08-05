import cv2
import cv2.cv as cv
#from numpy import *
import numpy as np
FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing
FLANN_INDEX_LSH    = 6

matcher_set = {}
detector_set = {}

def init_feature(detectorType):

    global detector, matcher

    if detectorType == 'orb':
        detector = cv2.ORB(400)
        flann_params= dict(algorithm = FLANN_INDEX_LSH,
                           table_number = 6, # 12
                           key_size = 12,     # 20
                           multi_probe_level = 1) #2

    elif detectorType == 'sift':
        detector = cv2.SIFT()
        flann_params = dict(algorithm = FLANN_INDEX_KDTREE, tress = 5)

    matcher = cv2.FlannBasedMatcher(flann_params, {})  # bug : need to pass empty dict (#1329)'''    

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

def list_match(threshold, face_list1, face_list2, detector, matcher):
    
    for face1 in face_list1:
        for face2 in face_list2:
            if match(threshold,face1['img'], face2['img'], face1['ID'], face2['ID'], detector, matcher):
                return True
        
    return False

    
def get_list_match_rate(face_list1, face_list2):
    
    global detector_set
    global matcher_set

    match_rate = {}
    detector_set = {}
    matcher_set = {}
    for face1 in face_list1:
        for face2 in face_list2:
            match_rate[face1['ID']] = {}
            match_rate[face1['ID']][face2['ID']] = get_match_rate(face1['img'], face2['img'])
    
    return match_rate

def match(minCount, img1, img2, id_1, id_2, detector, matcher):

    # store kp desc
    if id_1 in detector_set:
        kp1 = matcher_set[id_1]
        desc1 = detector_set[id_1]
    else:
        kp1, desc1 = detector.detectAndCompute(img1, None)
    if id_2 in detector_set:
        kp2 = matcher_set[id_2]
        desc2 = detector_set[id_2]
    else:
        kp2, desc2 = detector.detectAndCompute(img2, None)


    if len(kp1) < 2 or len(kp2) < 2:
        return False

    raw_matches = matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2)
    p1, p2, kp_pairs = filter_matches(kp1, kp2, raw_matches)

    if len(p1) >= 4:
        H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
        print len(status),
        if len(status) >= minCount:
            print 'Match'
            return True

    return False


def get_match_rate(face1, face2):
    
    
    kp1, desc1 = detector.detectAndCompute(face1, None)
    kp2, desc2 = detector.detectAndCompute(face2, None)
    
    if len(kp1) < 1 or len(kp2) < 1:
        return 0
   
    raw_matches = matcher.knnMatch(desc1, trainDescriptors=desc2, k=2) 
    p1, p2, kp_pairs = filter_matches(kp1, kp2, raw_matches)
    if len(p1) > 4:
        H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
        print len(status)
        return len(status)
    else:
        return 0

def cropImg(img, cropNumber):
    cropped = []
    height, width = img.shape
    corY = float(height/2)
    corX = float(width/2)

    #for i in range(0, cropNumber):
    cropped.append( img[0:corY*1, 0:corX*1]  )
    cropped.append( img[0:corY*1, corX*1:width]  )
    cropped.append( img[corY*1:height, 0:corX*1]  )
    cropped.append( img[corY*1:height, corX*1:width]  )

    return cropped
