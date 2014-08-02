#!/usr/bin/env python2.7
import cv2
import cv2.cv as cv

HAAR_CASCADE_PATH = "input/haarcascades/haarcascade_frontalface_alt.xml"

OUTPUT_PATH = 'output/'

def face_detect(img, framePosition, size):

    cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
    #rects = cascade.detectMultiScale(img, 1.1, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,140))  #40 150  #25, 160 #20 140

    #frame = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
    #rects = frame.detectMultiScale(img, 1.1, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20, 20) )  #40 150  #25, 160 #20 140
    rects = cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=4, minSize=(85, 85), flags = cv.CV_HAAR_SCALE_IMAGE)
    
    cv2.imshow("movie", img)
    if len(rects) == 0:
        return [], []
    rects[:,2:] += rects[:,:2]
    face_position_list = []
    for rect in rects:
        face_position_list.append(rect)
    
    return face_position_list, rects

    #if not os.path.isfile( OUTPUT_PATH + 'img/'+ name + '-1.jpg'):
        #output_image(detected, image, name)

def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

def output_image(rects, img, file_name):
    show = img.copy()
    for x1, y1, x2, y2 in rects:
        face = img[y1:y2, x1:x2]
        cv2.rectangle(show, (x1-10, y1-10), (x2+5, y2+5), (127, 255, 0), 2) 
        cv2.imshow("detected", show)
        resize_face = cv2.resize(face, (150, 150), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite( file_name, resize_face)
    #background = cv2.imread( OUTPUT_PATH + 'img/0.jpg' )
    #show = img.copy()
    #saveImage = background.copy()
    #saveImage[y1:y2, x1:x2] = face
    #cv2.bitwise_and(saveImage, saveImage, face)
    #cv2.imshow("detected", show)
    #cv2.waitKey()
