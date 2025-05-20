import cv2 as cv
import time
import os
import handTrackingModule as htm

widthCam, heightCam = 640, 480

cap = cv.VideoCapture(0)
cap.set(3, widthCam)
cap.set(4, heightCam)

folderPath = "images"
myList = os.listdir(folderPath)
overlayList = []

# create a list of images to be overlayed
for imPath in myList:
    image = cv.imread(f"{folderPath}/{imPath}")
    overlayList.append(image)

detector = htm.handDetector()

tipIds = [4, 8, 12, 16, 20]

pTime = 0
while True:

    success, frame = cap.read()


    frame = detector.findHands(frame)
    lmList = detector.findHandLocations(frame, draw=False)

    if lmList and len(lmList) > 0:
        fingersDetect = []
        # lmList is a list of lists of format: [node number, center_x, center_y]
        for id in range(0,5):
            tipLoc = lmList[tipIds[id]][2]
            baseLoc = lmList[tipIds[id]-2][2]
            
            # y position of 500 is reality lower than 200
            
            if (baseLoc - tipLoc) > 0:
                fingersDetect.append(1)
            else:
                fingersDetect.append(0)

        print(fingersDetect)

    img_h, img_w, img_c = overlayList[0].shape

    frame[0:img_h, 0:img_w] = overlayList[0]

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv.putText(frame, f'FPS: {int(fps)}', (400,70), cv.FONT_HERSHEY_PLAIN, 2, (255,0,0), 3)
    cv.imshow("frame", frame)
    if cv.waitKey(1) == ord("q"):
        break


cap.release()
cv.destroyAllWindows()
