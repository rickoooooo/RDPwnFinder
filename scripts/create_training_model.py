# This script creates an AdaBoostClassifier training model and saves it to disk.
# Run this script from inside a directory where all of the subdirectories contain your training images.
# Hacked images should be in a folder called "hacked", clean in "clean".
# Example usage: python create_training_model.py outputmodel.mdl

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
import random

filename = sys.argv[1]

print "Loading images..."

path="./"
Xlist=[]
Ylist=[]
for directory in os.listdir(path):
    if os.path.isdir(path + directory):
        for f in os.listdir(path+directory):
            #print(path+directory+"/"+file)
            img=Image.open(path+directory+"/"+f)
            featurevector=numpy.array(img).flatten()
            Xlist.append(featurevector)
            Ylist.append(directory)

# Shuffle lists so they aren't in any particular order
Zlist = list(zip(Xlist, Ylist))
random.shuffle(Zlist)
Xlist, Ylist = zip(*Zlist)

# Create ADABoostClassifier
classifier = AdaBoostClassifier(n_estimators=100)

print "Training model..."
# We learn the classifications
classifier.fit(Xlist, Ylist)

print "Saving model..."
# Save classifier to disk
dump(classifier, filename)
print "Model saved."

print "Running tests..."
scores = cross_val_score(classifier, Xlist, Ylist)

print "Scores: " + str(scores)
print "Mean score: " + str(scores.mean())
