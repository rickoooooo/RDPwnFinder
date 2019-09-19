#!/usr/bin/python
#
# Copyright (c) 2014-2015 Sylvain Peyrefitte
#
# This file is part of rdpy.
#
# rdpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""
example of use rdpy
take screenshot of login page
"""

import sys, os, getopt, time
import cv2

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QTimer
from rdpy.protocol.rdp import rdp
from rdpy.ui.qt4 import RDPBitmapToQtImage
import rdpy.core.log as log
from rdpy.core.error import RDPSecurityNegoFail
from twisted.internet import task
import threading
from PIL import Image
import numpy, os
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import cross_val_score
# Import datasets, classifiers and performance metrics
from sklearn import datasets, svm, metrics
# Standard scientific Python imports
import matplotlib.pyplot as plt
# For saving training model
from joblib import dump, load
from colorama import Fore, Style

method = cv2.TM_SQDIFF_NORMED
THREAD_COUNTER = 0

#set log level
#log._LOG_LEVEL = log.Level.INFO
log._LOG_LEVEL = 7

class RDPScreenShotFactory(rdp.ClientFactory):
    """
    @summary: Factory for screenshot exemple
    """
    __INSTANCE__ = 0
    __STATE__ = []
    def __init__(self, reactor, app, width, height, ssColorPath, ssGrayPath, timeout):
        """
        @param reactor: twisted reactor
        @param width: {integer} width of screen
        @param height: {integer} height of screen
        @param path: {str} path of output screenshot
        @param timeout: {float} close connection after timeout s without any updating
        """
        RDPScreenShotFactory.__INSTANCE__ += 1
        self._reactor = reactor
        self._app = app
        self._width = width
        self._height = height
        self._ssColorPath = ssColorPath
        self._ssGrayPath = ssGrayPath
        self._timeout = timeout
        #NLA server can't be screenshooting
        self._security = rdp.SecurityLevel.RDP_LEVEL_SSL

    def clientConnectionLost(self, connector, reason):
        """
        @summary: Connection lost event
        @param connector: twisted connector use for rdp connection (use reconnect to restart connection)
        @param reason: str use to advertise reason of lost connection
        """
        global THREAD_COUNTER

        if reason.type == RDPSecurityNegoFail and self._security != "rdp":
            log.info("due to RDPSecurityNegoFail try standard security layer")
            self._security = rdp.SecurityLevel.RDP_LEVEL_RDP
            try:
                connector.connect()
            except:
                print "Unable to connect due to security negotiation failure"
            return

        log.info("connection lost : %s"%reason)
        RDPScreenShotFactory.__STATE__.append((connector.host, connector.port, reason))
        RDPScreenShotFactory.__INSTANCE__ -= 1
        if(RDPScreenShotFactory.__INSTANCE__ == 0):
            self._reactor.stop()
            self._app.exit()
        #THREAD_COUNTER = THREAD_COUNTER - 1

    def clientConnectionFailed(self, connector, reason):
        """
        @summary: Connection failed event
        @param connector: twisted connector use for rdp connection (use reconnect to restart connection)
        @param reason: str use to advertise reason of lost connection
        """
        log.info("connection failed : %s"%reason)
        RDPScreenShotFactory.__STATE__.append((connector.host, connector.port, reason))
        RDPScreenShotFactory.__INSTANCE__ -= 1
        if(RDPScreenShotFactory.__INSTANCE__ == 0):
            self._reactor.stop()
            self._app.exit()


    def buildObserver(self, controller, addr):
        """
        @summary: build ScreenShot observer
        @param controller: RDPClientController
        @param addr: address of target
        """
        class ScreenShotObserver(rdp.RDPClientObserver):
            """
            @summary: observer that connect, cache every image received and save at deconnection
            """
            def __init__(self, controller, width, height, ssColorPath, ssGrayPath, timeout, reactor):
                """
                @param controller: {RDPClientController}
                @param width: {integer} width of screen
                @param height: {integer} height of screen
                @param path: {str} path of output screenshot
                @param timeout: {float} close connection after timeout s without any updating
                @param reactor: twisted reactor
                """
                rdp.RDPClientObserver.__init__(self, controller)
                self._buffer = QtGui.QImage(width, height, QtGui.QImage.Format_RGB32)
                self._ssColorPath = ssColorPath
                self._ssGrayPath = ssGrayPath
                self._timeout = timeout
                self._startTimeout = False
                self._reactor = reactor
                self._controller = controller

            def _send_keypress(self, scancode, extended=False):
                for pressed in (True, False):
                    #self._reactor.callLater(0, self._controller.sendKeyEventScancode, scancode, pressed, extended)
                    self._controller.sendKeyEventScancode(scancode, pressed, extended)

            def onUpdate(self, destLeft, destTop, destRight, destBottom, width, height, bitsPerPixel, isCompress, data):
                """
                @summary: callback use when bitmap is received
                """
                #pass
                image = RDPBitmapToQtImage(width, height, bitsPerPixel, isCompress, data);
                with QtGui.QPainter(self._buffer) as qp:
                #draw image
                    qp.drawImage(destLeft, destTop, image, 0, 0, destRight - destLeft + 1, destBottom - destTop + 1)
                if not self._startTimeout:
                    self._startTimeout = False
                    self._reactor.callLater(self._timeout, self.checkUpdate)

            def onReady(self):
                """
                @summary: callback use when RDP stack is connected (just before received bitmap)
                """
                log.info("connected " + str(addr))

                log.info("Waiting 3 seconds")
                time.sleep(3)
                log.info("Pressing SHIFT 5 times")
                for x in range(5):
                    time.sleep(.25)
                    self._send_keypress(0x2a)
                log.info("Waiting 3 more seconds")
                time.sleep(3)

            def onSessionReady(self):
                """
                @summary: Windows session is ready
                @see: rdp.RDPClientObserver.onSessionReady
                """
                print "onSessionReady"
                #pass

            def onClose(self):
                """
                @summary: callback use when RDP stack is closed
                """
                log.info("save color screenshot into %s"%self._ssColorPath)
                try:
                    self._buffer.save(self._ssColorPath)

                    # load the image and convert it to grayscale
                    image = cv2.imread(self._ssColorPath)
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                    # Make it just big enough that we can recognize features
                    gray = cv2.resize(gray, None, fx=.2, fy=.2)

                    # write the grayscale image to disk
                    filename = self._ssGrayPath
                    cv2.imwrite(filename, gray)

                    log.info("Got screenshot for " + self._ssGrayPath)
                except:
                    print "Failed to capture screenshots"


            def checkUpdate(self):
                self._controller.close();

        controller.setScreen(width, height);
        controller.setSecurityLevel(self._security)

        return ScreenShotObserver(controller, self._width, self._height, self._ssColorPath, self._ssGrayPath, self._timeout, self._reactor)

def main(width, height, ssColorPath, ssGrayPath, pwnedPath, timeout, targetFile, trainingModel, hosts):
    """
    @summary: main algorithm
    @param height: {integer} height of screenshot
    @param width: {integer} width of screenshot
    @param timeout: {float} in sec
    @param hosts: {list(str(ip[:port]))}
    @return: {list(tuple(ip, port, Failure instance)} list of connection state
    """
    #create application
    app = QtGui.QApplication(sys.argv)

    #add qt4 reactor
    import qt4reactor
    qt4reactor.install()

    from twisted.internet import reactor

    targetList = []

    if targetFile != "":
        for line in open(targetFile):
            targetList = [line.rstrip('\n') for line in open(targetFile)]
        print targetList
    # If there was no input list
    else:
        for host in hosts:
            targetList.append(host)

    for host in targetList:
        if ':' in host:
            ip, port = host.split(':')
        else:
            ip, port = host, "3389"

        reactor.connectTCP(ip, int(port), RDPScreenShotFactory(reactor, app, width, height, ssColorPath + "%s.jpg"%ip, ssGrayPath + "%s_gray.jpg"%ip, timeout))

    reactor.runReturn()
    app.exec_()

    # Create hacked directory if not already exists
    if not os.path.exists(ssColorPath + "/" + pwnedPath):
        os.mkdir(ssColorPath + "/" + pwnedPath)
        print "Directory " + pwnedPath + " created."
    if not os.path.exists(ssGrayPath + "/" + pwnedPath):
        os.mkdir(ssGrayPath + "/" + pwnedPath)
        print "Directory " + pwnedPath + " created."

    classifier = load(trainingModel)

    Xlist2 = []
    grayFileName = ssGrayPath + "%s_gray.jpg"%ip
    try:
        img2=Image.open(grayFileName)
        featurevector2=numpy.array(img2).flatten()
        Xlist2.append(featurevector2)
        img2.close()

        predicted = classifier.predict(Xlist2)

        for prediction in predicted:
            if str(prediction) == "hacked":
                print "Result:" + str(ip) + ":" + Fore.RED + str(prediction) + Style.RESET_ALL
                os.rename(grayFileName, ssGrayPath + "/" + pwnedPath + "/%s_gray.jpg"%ip)
                os.rename(ssColorPath + "/%s.jpg"%ip, ssColorPath + "/" + pwnedPath + "/%s.jpg"%ip)
            else:
                print "Result:" + str(ip) + ":" + Fore.GREEN + str(prediction) + Style.RESET_ALL
    except:
        log.info("Something went wrong with the screenshot")

    return RDPScreenShotFactory.__STATE__

def createDirectory(dirName):
    if not os.path.exists(dirName):
        os.mkdir(dirName)
        print "Directory " + dirName + " Created "
    else:
        print "Directory " + dirName + " already exists"

def loadTargetsFromFile(fileName):
    list = []
    try:
        list = [line.rstrip('\n') for line in open(fileName)]
    except:
        print "Unable to load file " + filename
        exit()
    return list

def printHeader():
    print "##################"
    print "# RDPwnFinder.py #"
    print "##################"
    print ""

def help():
    print "Usage: rdpy-rdpscreenshot [options] ip[:port]"
    print "\t-w: width of screen default value is 1024"
    print "\t-l: height of screen default value is 800"
    print "\t-t: timeout of connection without any updating order (default is 2s)"
    print "\t-c: Directory to store color images (default is current directory)"
    print "\t-g: Directory to store grayscale/resized images (default is current directory)"
    print "\t-n: Training model"
    print "\t-p: Subdirectory to store images identified as pwned"

if __name__ == '__main__':
    #default script argument
    width = 640
    height = 480
    path = "/tmp/"
    timeout = 5.0
    ssColorPath = "./"
    ssGrayPath = "./"
    targetFile = ""
    trainingModel = ""
    pwnedPath = "./"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hw:l:t:c:g:i:n:p:")
    except getopt.GetoptError:
        help()
    for opt, arg in opts:
        if opt == "-h":
            help()
            sys.exit()
        elif opt == "-w":
            width = int(arg)
        elif opt == "-l":
            height = int(arg)
        elif opt == "-t":
            timeout = float(arg)
        elif opt == '-c':
            ssColorPath = arg + "/"
        elif opt == '-g':
            ssGrayPath = arg + "/"
        elif opt == '-i':
            #targetList = loadTargetsFromFile(arg)
            targetFile = arg
        elif opt == '-n':
            trainingModel = arg
        elif opt == '-p':
            pwnedPath = arg

    main(width, height, ssColorPath, ssGrayPath, pwnedPath, timeout, targetFile, trainingModel, args)
