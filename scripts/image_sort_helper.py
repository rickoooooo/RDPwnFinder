#!/usr/bin/python
# This script helps you manually sort training data into the classifications of "hacked" and "clean".
# Run this script from isnide a directory containing your training images. This script will flash an image on screen.
# Press Left Arrow if it's clean, press Right Arrow if it's hacked. The script will then move the image into the corresponding
# "clean" or "hacked" directory.

import cv2 as cv
import os


cur_char = -1
prev_char = -1

c = -1

for filename in os.listdir("."):
    c = -1
    print filename
    if filename.endswith(".jpg"):
        while c < 81 or c > 84: # arrow keys
            imgFile = cv.imread(filename)
            cv.imshow('dst_rt', imgFile)
            c = cv.waitKey(0)
            print c
            if c == 81:
                print "Clean"
                filename2 = "./clean/" + filename
            elif c == 83:
                print "Hacked"
                filename2 = "./hacked/" + filename
            cv.destroyAllWindows()
            os.rename(filename, filename2)
        continue
