import cv2
import numpy as np

# initialize HSV color range for green colored objects
thresholdLower = (50, 100, 100)
thresholdUpper = (70, 255, 255)

# Start capturing the video from webcam
video_capture = cv2.VideoCapture(0)

def cam():
    global frame # global frame so it can be used in mouse_get_threshold()
    if not video_capture.isOpened():
        video_capture.open(0)
    # Store the current frame of the video in the variable frame
    ret, frame = video_capture.read()
    # Flip the image to make it right
    frame = cv2.flip(frame,1)
    
    # Blur the frame using a Gaussian Filter of kernel size 5, to remove excessive noise
    frame_blurred = cv2.GaussianBlur(frame, (5,5), 0)
    # Convert the frame to HSV as it allows better segmentation.
    frame_hsv = cv2.cvtColor(frame_blurred, cv2.COLOR_BGR2HSV)

    # Create a mask for the frame, showing threshold values
    frame_segmented = cv2.inRange(frame_hsv, thresholdLower, thresholdUpper)
    # Erode the masked output to delete small white dots present in the masked image
    frame_eroded  = cv2.erode(frame_segmented, None, 10)
    # Dilate the resultant image to restore our target
    frame_masked = cv2.dilate(frame_eroded, None, 10)

    # Display the masked output in a different window
    cv2.imshow('Masked Output', frame_masked)

    # Find all contours in the masked image
    contours,_ = cv2.findContours(frame_masked.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Define center of the object to be detected as None
    center = None

    # check if there's at least 1 object with the segmented color
    if len(contours) > 0:
        # Find the contour with maximum area
        contours_max = max(contours, key = cv2.contourArea)

        #  rotated bounding rectangle (https://docs.opencv.org/3.4/dd/d49/tutorial_py_contour_features.html)
        rect = cv2.minAreaRect(contours_max)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(frame,[box],0,(0,0,255),2)

        # Calculate the centroid of the object
        # "formula from (https://learnopencv.com/find-center-of-blob-centroid-using-opencv-cpp-python/)"
        M = cv2.moments(contours_max)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
            
    # Show the output frame
    cv2.imshow('Camera Output', frame)
    cv2.setMouseCallback('Camera Output',mouse_get_threshold)
    return center

def mouse_get_threshold(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN: # checks mouse left button down condition
        # convert rgb to hsv format
        colorsHSV = cv2.cvtColor(np.uint8([[[frame[y,x,0] ,frame[y,x,1],frame[y,x,2] ]]]),cv2.COLOR_BGR2HSV)
        
        # create a threshold based on the color values
        tempLower = colorsHSV[0][0][0]  - 10, 100, 100
        tempUpper = colorsHSV[0][0][0] + 10, 255, 255
        
        global thresholdLower
        global thresholdUpper
        # set the threshold
        thresholdLower = np.array(tempLower)
        thresholdUpper = np.array(tempUpper)
    
def main(): # used for debugging the segmentation without the breakout game running
    while(1):
        cam()
        if cv2.waitKey(20) & 0xFF == 27: #  wait for Esc key
            break
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__': # only run main() if executing directly from it's file and not being imported
    main()