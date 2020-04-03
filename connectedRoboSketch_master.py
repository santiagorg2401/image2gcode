# Python Master Script to Call Functions

import cv2 as cv2
import numpy as np
import serial
import time
from connectedRoboSketch_lib import initSerial, sendFullGcode, closeSerial, getImage, getImageScaleFact, edgeDetect, vectorizeEdges, scaleVectors, scaleDimensions, generateGcode

MAX_WIDTH = 100
MAX_HEIGHT = 150

pNum = '/dev/ttyUSB0'

ser = initSerial(pNum) # initialize serial connection

img, height, width = getImage() # get input image, will be changed for Bluetooth

scale_fact_x, scale_fact_y = getImageScaleFact(img) # scale factor for input image

edges = edgeDetect(img) # peform canny edge detection on the image

contours = vectorizeEdges(edges) # vectorization of edges and cleanup of vectors

cnt_scaled = scaleVectors(contours, scale_fact_x, scale_fact_y) # scales vectors by whichever scaling factor is larger

width, height = scaleDimensions(width, height, scale_fact_x, scale_fact_y) # scales width and height of original image

generateGcode(cnt_scaled, width, height) # generate the G-Code instructions for the plotter to accept

sendFullGcode(ser) # send G-Code instructions over serial

closeSerial(ser) # close serial connection
