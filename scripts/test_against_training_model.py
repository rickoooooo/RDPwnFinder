# This script allows you to provide a training model and an image, and see how the model classifies the single image.
# Example usage: python test_against_training_model.py testmodel.mdl 192.168.1.1.jpg

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

trainingModel = sys.argv[1]
sampleImage = sys.argv[2]

classifier = load(trainingModel)

Xlist2 = []
img2=Image.open(sampleImage)
featurevector2=numpy.array(img2).flatten()
Xlist2.append(featurevector2)

predicted = classifier.predict(Xlist2)

for prediction in predicted:
    print str(prediction)
