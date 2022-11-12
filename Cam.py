import cv2
import numpy as np
from collections import deque
import time
import math

#Define HSV colour range for threshold colour objects
thresholdLower = (29, 86, 6)
thresholdUpper = (64, 255, 255)


center = (0,0)

#Start video capture
video_capture = cv2.VideoCapture(0)
ret, frame = video_capture.read()
frame = cv2.flip(frame,1)

def cam():
    global frame
    if not video_capture.isOpened():
        video_capture.open(0)
    #Store the readed frame in frame, ret defines return value
    ret, frame = video_capture.read()
    #Flip the frame to avoid mirroring effect
    frame = cv2.flip(frame,1)
    #Blur the frame using Gaussian Filter of kernel size 5, to remove excessivve noise
    blurred_frame = cv2.GaussianBlur(frame, (5,5), 0)
    #Convert the frame to HSV, as HSV allow better segmentation.
    hsv_converted_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

    #Create a mask for the frame, showing threshold values
    mask = cv2.inRange(hsv_converted_frame, thresholdLower, thresholdUpper)
    #Erode the masked output to delete small white dots present in the masked image
    mask = cv2.erode(mask, None, iterations = 5)
    #Dilate the resultant image to restore our target
    mask = cv2.dilate(mask, None, iterations = 5)

    #Display the masked output in a different window
    cv2.imshow('Masked Output', mask)

    #Find all contours in the masked image
    cnts,_ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #Define center of the ball to be detected as None
    global center
    center = None

    #If any object is detected, then only proceed
    if(len(cnts)) > 0:
        #Find the contour with maximum area
        c = max(cnts, key = cv2.contourArea)
        #Find the center of the circle, and its radius of the largest detected contour.
        ((x,y), radius) = cv2.minEnclosingCircle(c)

        #Calculate the centroid of the ball, as we need to draw a circle around it.
        M = cv2.moments(c)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        #Proceed only if a ball of considerable size is detected
        if radius > 0:
            #Draw circles around the object as well as its centre
            cv2.circle(frame, (int(x), int(y)), int(radius), (0,255,255), 2)
            cv2.circle(frame, center, 5, (0,255,255), -1)
            
    #Show the output frame
    cv2.imshow('Frame', frame)
    cv2.setMouseCallback('Frame',mouseTreshold)

def mouseTreshold(event,x,y,flags,param):
    global thresholdLower
    global thresholdUpper

    if event == cv2.EVENT_LBUTTONDOWN: #checks mouse left button down condition
        # convert rgb to hsv format
        colorsHSV = cv2.cvtColor(np.uint8([[[frame[y,x,0] ,frame[y,x,1],frame[y,x,2] ]]]),cv2.COLOR_BGR2HSV)
        
        # create a treshold based on the color values
        tempLower = colorsHSV[0][0][0]  - 10, 100, 100
        tempUpper = colorsHSV[0][0][0] + 10, 255, 255
        
        # set the threshold
        thresholdLower = np.array(tempLower)
        thresholdUpper = np.array(tempUpper)

def main():
    while(1):
        cam()
        if cv2.waitKey(20) & 0xFF == 27:
            break
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()