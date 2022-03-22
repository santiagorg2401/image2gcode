import cv2 as cv
import numpy as np

def getImageScaleFact(img, MAX_WIDTH, MAX_HEIGHT): # Gets the scale factor for the image
    height, width  = img.shape[:2] # Grab the dimensions of the image
    scale_fact_x = width/MAX_WIDTH # Determine how much wider the image is than max width
    scale_fact_y = height/MAX_HEIGHT # Determine how much taller the image is than max height
    return scale_fact_x, scale_fact_y

def edgeDetect(img): # Performs canny edge detection on the image
    edges = cv.Canny(img, 100, 200)
    return edges

def vectorizeEdges(edges): # Performs the vectorization and cleanup of the vectors
    ret, thresh = cv.threshold(edges, 127, 255, 0)
    contours0, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    contours = [cv.approxPolyDP(cnt, 3, True) for cnt in contours0] # Reduce points
    i = 0
    while i < len(contours): # Further reduce points by removing single point lines
        if(len(contours[i]) < 2):
            del(contours[i])
        else:
            i = i + 1
    return contours

def scaleVectors(contours, scale_fact_x, scale_fact_y): # Scales the vectors by whichever scaling factor is larger
    cnt_scaled = []
    cnt_scaled_int = []
    for i in range(0, len(contours)):
        cnt_norm = contours[i]
        if(scale_fact_x > 1.0 or scale_fact_y > 1.0): # If it needs scaled
            if(scale_fact_x > scale_fact_y): # If width is proportionately larger
                cnt_scaled.append(cnt_norm*(1.0/scale_fact_x))
            else:
                cnt_scaled.append(cnt_norm*(1.0/scale_fact_y))
    return cnt_scaled

def scaleDimensions(width, height, scale_fact_x, scale_fact_y): # Scales width and heights of original image to new size
    if(scale_fact_x > scale_fact_y):
        width /= scale_fact_x
        height /= scale_fact_x
    if(scale_fact_y > scale_fact_x):
        width /= scale_fact_y
        height /= scale_fact_y
    return width, height

def generateGcode(cnt_scaled, width, height):
    f = open("generated_gcode.txt", mode="w", encoding="ascii")
    
    maxX = 0
    minX = 0
    maxY = 0
    minY = 0

    # Go home with pen up
    f.write("M3\n")
    f.write("S0\n")
    f.write("G0 X0 Y0\n")
    
    for i in range(0, len(cnt_scaled)):
        if(cnt_scaled[i][0][0][0]-(width/2) > maxX):
            maxX = cnt_scaled[i][0][0][0]-(width/2)
        if(cnt_scaled[i][0][0][0]-(width/2) < minX):
            minX = cnt_scaled[i][0][0][0]-(width/2)
        if(cnt_scaled[i][0][0][1]-(height/2) > maxY):
            maxY = cnt_scaled[i][0][0][1]-(height/2)
        if(cnt_scaled[i][0][0][1]-(height/2) < minY):
            minY = cnt_scaled[i][0][0][1]-(height/2)

    # Set movement speed
    f.write("F2000\n")

    # Convert vectors (contours) to G-Code
    for i in range(0, len(cnt_scaled)):
        # Move quickly to starting point
        f.write("G0 X" + str(cnt_scaled[i][0][0][0]-(width/2)) + " Y" + str(cnt_scaled[i][0][0][1]-(height/2)) + "\n")
        # Lower the pen
        f.write("S65\n")
        # Move at the given movement speed through each point with pen down
        for j in range(0, len(cnt_scaled[i])):
            # Move to next point in list
            f.write("G1 X"+ str(cnt_scaled[i][j][0][0]-(width/2)) + " Y" + str(cnt_scaled[i][j][0][1]-(height/2)) + "\n")
        # Raise pen
        f.write("S0\n")

    # Go back to home position
    f.write("S0\n")
    f.write("G0 X0 Y0\n")
    f.write("M5\n")
    f.close()
