# This script will allow you to test a single image against a training model. It will move the image into the corresponding Directory
# Example usage: python test_and_sort_against_training_model.py testmodel.mdl 192.168.1.1.jpg

from PIL import Image
import numpy, os
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import cross_val_score
# Import datasets, classifiers and performance metrics
from sklearn import datasets, svm, metrics
# Standard scientific Python imports
import matplotlib.pyplot as plt
import sys
# For saving training model
from joblib import dump, load

def createDirectory(dirName):
    if not os.path.exists(dirName):
        os.mkdir(dirName)
        print "Directory " + dirName + " Created "
    else:
        print "Directory " + dirName + " already exists"

# Get arguments
trainingModel = sys.argv[1]
sampleImage = sys.argv[2]

categories = ["hacked", "clean"]

# create all the directories for sorting
for cat in categories:
    createDirectory(cat)

# Load classifier from file
classifier = load(trainingModel)

Xlist2 = []
img=Image.open(sampleImage)
featurevector2=numpy.array(img).flatten()
Xlist2.append(featurevector2)

predicted = classifier.predict(Xlist2)

for prediction in predicted:
    os.rename(sampleImage, str(prediction) + "/" + sampleImage)
    print str(prediction)
