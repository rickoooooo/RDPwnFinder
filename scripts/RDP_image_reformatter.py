# import the necessary packages
# The purpose of this script is to reformat previously captured images for creating a dataset for AI
# Original images must have been captured at 640x480, otherwise the resize scale is incorrect below.

from PIL import Image
import sys
import cv2
import os

filename = sys.argv[1]

# load the example image and convert it to grayscale
image = cv2.imread(filename)

#Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Shrink to the smallest size where we can still recognize features
image2 = cv2.resize(gray, None, fx=.2, fy=.2)

# write the reformatted image to disk
cv2.imwrite("reformatted/" + filename, image2)
