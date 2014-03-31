import hcluster
import os
from PIL import Image
from numpy import *
import hcluster


#create a list of images
imlist = []
for filename in os.listdir('./'):
    if os.path.splitext(filename)[1] == '.jpg':
        imlist.append(filename)
n = len(imlist)

#extract feature vector for each image
features = zeros((n,3))
#kp1, desc1 = self.detector.detectAndCompute(face1.getImg(), None)

for i in range(n):
    im = array(Image.open(imlist[i]))
    R = mean(im[:,:,0].flatten())
    G = mean(im[:,:,1].flatten())
    B = mean(im[:,:,2].flatten())
    features[i] = array([R,G,B])


tree = hcluster.hcluster(features)
hcluster.drawdendrogram(tree,imlist,jpeg='sunset.jpg')
