import cv2 as cv
import numpy as np
import time
import os
import math
import handTrackingModule as htm

'''
This module is able to read the location of the index and thumb tips,
then calculate the gap between them. Upon movement of these two fingers,
the gap length will change and a normalized value between 0-100 is returned.
This module can be applied to control some sort of slider or zoom. 

Note: the distance of the hand from the camera distorts the result of the
gap. Needs to be calibrated
'''


widthCam, heightCam = 1080, 720

cap = cv.VideoCapture(0)
cap.set(3, widthCam)
cap.set(4, heightCam)

# higher detection confidence
detector = htm.handDetector(minDetectionConf=0.5)
# pTime = 0

slider = 300
norm = 0

while True:
    # webcam set up
    success, frame = cap.read()
    if not success:
        break
    
    frame = cv.flip(frame, 1)
    frame = cv.addWeighted(frame, 1.5, np.zeros(frame.shape, frame.dtype), 0, 0)
    # frame = detector.findHands(frame, draw=False)
    # lmBothList, bb = detector.findBothHandLocations(frame)
    lmBothList, bb = detector.find2Hands(frame)

    if lmBothList and len(lmBothList) > 0:
        firstDetected, secondDetected = detector.getBothFingersUp(lmBothList)

        for i in range(len(lmBothList)):
            lmList = lmBothList[i]
            boundingBox = bb[i]
            if lmList and detector.isLeft(lmList):
                # Resolve distance by filtering based on size
                widthBox = abs(boundingBox[2] - boundingBox[0])
                heightBox = abs(boundingBox[3] - boundingBox[1])
                area = widthBox * heightBox

                drawFlag = False
                if 10000 < area < 40000:
                    drawFlag = True
                    gapIndex, center_x, center_y = detector.findDistance(frame, lmList, 1, 3, draw=drawFlag)
                    if center_y < 150:
                        detector.setCursorState(gapIndex, center_x, center_y)
                        slider = np.interp(gapIndex, [20, 200], [300, 150])
                        norm = np.interp(gapIndex, [20, 200], [0, 100])
                else:
                    drawFlag = False
                 
            
        


    # creates a sudo gui system
    cv.rectangle(frame, (50, 150), (85, 300), (0, 255, 0), 1)
    cv.rectangle(frame, (50, int(slider)), (85, 300), (0, 255, 0), cv.FILLED)
    cv.putText(frame, f'{int(norm)} %', (50, 320), cv.FONT_HERSHEY_PLAIN, 1, (0,255,0), 1)
    
    # # gui set up
    # cTime = time.time()
    # fps = 1 / (cTime - pTime)
    # pTime = cTime

    # cv.putText(
    #     frame, f"FPS: {int(fps)}", (35, 45), cv.FONT_HERSHEY_PLAIN, 1, (255, 0, 20), 1
    # )

    cv.imshow("frame", frame)
    if cv.waitKey(1) == ord("q"):
        break

cap.release()
cv.destroyAllWindows()
