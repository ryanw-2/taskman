import cv2 as cv
import time
import os
import handTrackingModule as htm


def detectThumb(orientation, res, thumbTip, thumbBase):
    if not orientation: return []

    # right means thumb is more right than pinky
    if orientation == "right":
        # x position of less is more left 
        if (thumbBase < thumbTip):
            res.append(1)
        else:
            res.append(0)
    # left means thumb is more left than pinky
    else: # orientation == "left"
        # x position of less is more left 
        if (thumbBase > thumbTip):
            res.append(1)
        else:
            res.append(0)

    return res

def detect(lmList, res):
    if not lmList or len(lmList) <= 0:
        return res
    
    tipIds = [4, 8, 12, 16, 20]

    pinkyTipLoc_x = lmList[tipIds[4]][1]
    thumbTipLoc_x = lmList[tipIds[0]][1]
    thumbBaseLoc_x = lmList[tipIds[0] - 1][1]

    # Process the thumb
    if thumbTipLoc_x > pinkyTipLoc_x:
        res = detectThumb("right", res, thumbTipLoc_x, thumbBaseLoc_x)
    else:
        res = detectThumb("left", res, thumbTipLoc_x, thumbBaseLoc_x)

    # Process other fingers
    # lmList is a list of lists of format: [node number, center_x, center_y]
    for id in range(1,5):
        tipLoc = lmList[tipIds[id]][2]
        baseLoc = lmList[tipIds[id]-2][2]
        
        # y position of greater is more down
        if (baseLoc - tipLoc) > 0:
            res.append(1)
        else:
            res.append(0)
    
    return res

def main():
    # Set up webcame
    widthCam, heightCam = 640, 480

    cap = cv.VideoCapture(0)
    cap.set(3, widthCam)
    cap.set(4, heightCam)

    detector = htm.handDetector()
    pTime = 0

    while True:
        success, frame = cap.read()
        frame = detector.findHands(frame)

        '''
        The order of the landmark list is unspecified. Note:
        it doesn't matter which hand is processed first.
        '''
        # Hand node landmark locations of both hands
        lmBothList = detector.findBothHandLocations(frame)
        
        # Initialize the hand landmark location lists of each hand
        if lmBothList and len(lmBothList) > 0:
            firstDetected = []
            secondDetected = []

            if len(lmBothList) > 0:
                firstDetected = detect(lmBothList[0], firstDetected)

            if len(lmBothList) > 1:
                print("got here")
                secondDetected = detect(lmBothList[1], secondDetected)    
            
            '''
            Process Return Element
            '''
            totalFirst = 0
            totalSecond = 0

            if firstDetected:
                totalFirst = firstDetected.count(1)
            if secondDetected:
                totalSecond = secondDetected.count(1)
            
            print("first hand finger count is: ", totalFirst)
            print("second hand finger count is: ", totalSecond)
        
        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime

        cv.putText(frame, f'FPS: {int(fps)}', (400,70), cv.FONT_HERSHEY_PLAIN, 2, (255,0,0), 3)
        cv.imshow("frame", frame)
        if cv.waitKey(1) == ord("q"):
            break
    
    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()