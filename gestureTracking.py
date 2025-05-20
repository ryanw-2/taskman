import cv2 as cv
import mediapipe as mp
import time

import handTrackingModule as htm

# Set up time to calculate frames per second
pTime = 0
cTime = 0

# Begins video capture and takes in which camera to be activated
cap = cv.VideoCapture(0)

# Construct a new handDetector object
detector = htm.handDetector()

# Continously takes frames from video input
while True:
    # Reading returns bool, image
    # if the bool is false, that means there is an issue with video input
    success, frame = cap.read()
    newFrame = detector.findHands(frame)
    handLocList = detector.findHandLocations(frame, draw=False)
    
    if handLocList:
        print(handLocList[12])
    
    # Calculate FPS
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime


    # Screen/GUI Set up
    cv.putText(newFrame, str(int(fps)), (10,70), cv.FONT_HERSHEY_SIMPLEX, 3, (255,255,255), 3)

    cv.imshow('frame', newFrame)
    if cv.waitKey(1) == ord('q'):
        break  

cap.release()
cv.destroyAllWindows()