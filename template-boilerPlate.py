import cv2 as cv
import time
import os
import handTrackingModule as htm

widthCam, heightCam = 1280, 720

cap = cv.VideoCapture(0)
cap.set(3, widthCam)
cap.set(4, heightCam)
# higher detection confidence
detector = htm.handDetector(minDetectionConf=0.5)
pTime = 0
while True:
    success, frame = cap.read()
    if not success:
        break

    frame = detector.findHands(frame)
    lmList = detector.findHandLocations(frame)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    
    cv.putText(
        frame, f"FPS: {int(fps)}", (35, 45), cv.FONT_HERSHEY_PLAIN, 1, (255, 0, 20), 1
    )

    cv.imshow("frame", frame)
    if cv.waitKey(1) == ord("q"):
        break

cap.release()
cv.destroyAllWindows()
