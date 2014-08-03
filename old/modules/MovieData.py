import cv2
import cv2.cv as cv
from Face import *



def getFaceAndKeyword(characterNumber, outputPath):

    print 'Start getFaceAndKeyword'
    faceList = []
    keywords = []
    if characterNumber > 0:
        faceID = characterNumber
    else:
        faceID = 0

    with open( self.preprcessedFile, 'r') as graph:

        lines = graph.readlines()
        if len(lines) > 1:     
            flag = 0
            for line in lines:
                #get keyword
                if line[1] == '[':
                    if ',' in line:
                        keyword = line[3: len(line)-3].split('\'')
                        flag = 1
                    else:
                        keyword = line[3:len(line)-3]

                    if flag!=1 and keyword not in keywords:
                        keywords.append(keyword)

                #get keywordID
            elif line[0] == '(':
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
                    img = cv2.imread( outputPath + "img/" + str(frameNumber) + 
                            "-" + str(faceCount)  + ".jpg", 0)
                    if type(keyword) == list:
                        for key in keyword:
                            if ',' not in key:
                                faceList.append(Face(facePosition, faceID, frameNumber, img, key, int(keywordID)))
                                cv2.imwrite('other/' + str(faceID) + key + '.jpg', img)
                                faceID += 1
                    else:
                        faceList.append(Face(facePosition, faceID, frameNumber, img, keyword, int(keywordID)))
                        cv2.imwrite('other/' + str(faceID) + keyword + '.jpg', img)
                        faceID += 1

    return faceList, keywords

def loadCharacter(characterFile):

    i = -1
    characters = {}
    img = []
    with open('input/' + characterFile, "r") as keywordsFile:
        lines = csv.reader(keywordsFile)
        for row in lines:
            for character in row:
                img.append(cv2.imread( 'input/' + str(character) + '.jpg'), 0)
    for i in range(0, len(img)):
        characters[i] = []
        characters[i].append(Face([1,1,1,1], i, -1, img[i], -1, -1))

    return characters
