import cv2 as cv
import mediapipe as mp
import time
import math

class handDetector():
    def __init__(self, mode = False, 
                 maxHands = 2, 
                 modelComplexity = 1,
                 minDetectionConf = 0.5, 
                 minTrackingConf = 0.5):
        
        self.mode = mode
        self.max_num_hands = maxHands
        self.model_complexity = modelComplexity
        self.min_detection_confidence = minDetectionConf
        self.min_tracking_confidence = minTrackingConf
        

        # Set up mediapipe library and tools
        self.mpHands = mp.solutions.hands # type: ignore
        self.hands = self.mpHands.Hands(self.mode, 
                                        self.max_num_hands, 
                                        self.model_complexity,
                                        self.min_detection_confidence, 
                                        self.min_tracking_confidence)
        
        self.mpDraw = mp.solutions.drawing_utils #type: ignore
        
        # Set up State
        self.starting_x = 0
        self.starting_y = 0
        self.cursorState = 'none'
        self.cursorGesture = 'none'
    '''
    Draws nodes and connections on frame
    Returns frame
    '''
    def findHands(self, frame, draw = True):
        # Mediapipe works in RGB
        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        # Using Hands module in Media Pipe to detect hands

        self.results = self.hands.process(rgb)
        self.lmList = []

        # Using Hands Landmarks to find each node and connections
        if draw:
            if self.results:
                for handLms in self.results:
                    # id marks which finger node
                    # landmark specifies the location as a ratio of the window size
                    self.mpDraw.draw_landmarks(frame, handLms, self.mpHands.HAND_CONNECTIONS)       
            
        return frame
    
    def isValidId(self, id: int) -> bool:
        return (id == 4 or
            id == 8 or
            id == 12 or
            id == 16 or
            id == 20 or
            id == 3 or
            id == 6 or
            id == 10 or
            id == 14 or
            id == 18)
    
    def getBoundaries(self, id: int, lm, width, height):
        xMin = 0
        xMax = width 
        yMin = 0
        yMax = height
        if id == 0:
            yMin = int(lm.y * height)
        if id == 4:
            xMin = int(lm.x * width)
        if id == 12:
            yMax = int(lm.y * height)
        if id == 20:
            xMax = int(lm.x * width)
        
        return xMin, yMin, xMax, yMax


    def find2Hands(self, frame, draw = True):
        '''
        Finds the center-x and center-y locations of both hands.
        Returns a list comprised of a list of two elements of format : [node id, center_x, center_y]
        '''
        # Mediapipe works in RGB
        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        # Using Hands module in Media Pipe to detect hands

        self.results = self.hands.process(rgb)
        
        height, width, _ = frame.shape
        bothLmList = []
        bbList= []

        if self.results.multi_hand_landmarks:
            for hand in self.results.multi_hand_landmarks:
                singleLmList = []

                xMin = 0
                xMax = width 
                yMin = 0
                yMax = height

                for id, lm in enumerate(hand.landmark):
                    if id == 0:
                        yMin = int(lm.y * height)
                    if id == 4:
                        xMin = int(lm.x * width)
                    if id == 12:
                        yMax = int(lm.y * height)
                    if id == 20:
                        xMax = int(lm.x * width)

                    if self.isValidId(id):
                        singleLmList.append([id, int(lm.x * width), int(lm.y * height)])
                
                bbList.append((xMin, yMin, xMax, yMax))
                bothLmList.append(singleLmList)


        return bothLmList, bbList

    '''
    Finds the center-x and center-y locations of a specified hand.
    Intuitively, this function may serve well if the user is trying
    to track one hand at a time.
    Returns a list comprised of the [node id, center_x, center_y]
    '''
    def findHandLocations(self, frame, hand=0, draw=False):
        lmLocList = []
        boundingBox = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[hand]
            xList = []
            yList = []
            
            for id, lm in enumerate(myHand.landmark):
                height, width, channel = frame.shape
                # multiplies the ratio with frame size
                center_x, center_y = int(lm.x * width), int(lm.y * height)

                xList.append(center_x)
                yList.append(center_y)
                
                lmLocList.append([id, center_x, center_y])

                if draw:
                    cv.circle(frame, (center_x, center_y), 2, (255, 0, 255), cv.FILLED)
            
            xMin, xMax = min(xList), max(xList)
            yMin, yMax = min(yList), max(yList)
            boundingBox = xMin, yMin, xMax, yMax
            buffer = 10

            if draw:
                cv.rectangle(frame, (boundingBox[0]-buffer, boundingBox[1]-buffer), 
                             (boundingBox[2]+buffer, boundingBox[3]+buffer), (0,255,0), 1)
        

        return lmLocList, boundingBox
    
    '''
    Finds the center-x and center-y locations of both hands.
    Returns a list comprised of a list of two elements of format : [node id, center_x, center_y]
    Each index of the returned list are the node id and locations of one hand.
    '''
    def findBothHandLocations(self, frame, draw=False):
        lmBothLocList = []
        bBoxList = []
        if self.results.multi_hand_landmarks:
            
            for myHand in self.results.multi_hand_landmarks:
                xList  = []
                yList= []
                boundingBox = []
                singleLocList = []

                for id, lm in enumerate(myHand.landmark):
                    height, width, channel = frame.shape
                    # multiplies the ratio with frame size
                    center_x, center_y = int(lm.x * width), int(lm.y * height)
                    
                    xList.append(center_x)
                    yList.append(center_y)
                    
                    singleLocList.append([id, center_x, center_y])

                xMin, xMax = min(xList), max(xList)
                yMin, yMax = min(yList), max(yList)
                boundingBox = xMin, yMin, xMax, yMax
                
                
                if draw:
                    buffer = 10
                    cv.rectangle(frame, (boundingBox[0]-buffer, boundingBox[1]-buffer), 
                                (boundingBox[2]+buffer, boundingBox[3]+buffer), (0,255,0), 1)
                    
                bBoxList.append(boundingBox)
                lmBothLocList.append(singleLocList)

        return lmBothLocList, bBoxList

    '''
    Given a hand node landmark list, and the index of two hand nodes,
    returns:
         an integer that is the distance between the two points
         center x of activation point
         center y of activation point
    '''
    def findDistance(self, frm, lmList, point1, point2, draw=False):
        # Find distance between index and first
        first_x, first_y= lmList[point1][1], lmList[point1][2]
        second_x, second_y = lmList[point2][1], lmList[point2][2]
        center_x, center_y = (first_x + second_x) // 2, (first_y + second_y) // 2

        gapLength = math.hypot(second_x - first_x, second_y - first_y)

        if draw:
            cv.line(frm, (first_x, first_y), (second_x, second_y), (110, 170, 255), 1)
            cv.circle(frm, (center_x, center_y), 10, (0, 106, 255), cv.FILLED)
            # if the distance is practically zero and some pinky is down
            if gapLength < 30 and center_y < 180:
                cv.circle(frm, (center_x, center_y), 10, (204, 255, 0), cv.FILLED)

        return gapLength, center_x, center_y


    def setCursorState(self, gapIndex, center_x, center_y) -> None:
        '''
        Detects clicks and hand swipes, and sets the cursor state
        accordingly
        '''
        gesture = 'none'

        # initialize values
        if gapIndex < 30 and self.cursorState == 'none':
            self.starting_x = center_x
            self.starting_y = center_y
            self.cursorState = 'hover'
        elif gapIndex > 30 and self.cursorState == 'hover':
            x_difference = center_x - self.starting_x
            y_difference = center_y - self.starting_y

            if x_difference > 15:
                gesture = 'rightswipe'
            elif x_difference < -15:
                gesture = 'leftswipe'
            elif y_difference > 15:
                gesture = 'downswipe'
            elif y_difference < -15:
                gesture = 'upswipe'
            else:
                gesture = 'click'

            self.cursorGesture = gesture
            self.cursorState = 'none'

        

    def getCursorGesture(self) -> str:
        result = self.cursorGesture
        self.cursorGesture = 'none'
        return result

    '''
    Helper Function to detect thumb orientation and whether the
    thumb is "opened" or "closed"
    '''
    def detectThumb(self, orientation, res, thumbTip, thumbBase):
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

    '''
    input: lmList
    output: bool
    '''
    def isLeft(self, lmList):
        if not lmList or len(lmList) <= 0:
            return False

        pinkyTipLoc_x = lmList[9][1]
        thumbTipLoc_x = lmList[1][1]

        return thumbTipLoc_x < pinkyTipLoc_x

    '''
    Helper function to detect remaining four fingers and whether
    the fingers or "opened" (1) or "closed" (0)
    '''
    def detect(self, lmList, res):
        if not lmList or len(lmList) <= 0:
            return res

        pinkyTipLoc_x = lmList[9][1]
        thumbTipLoc_x = lmList[1][1]
        thumbBaseLoc_x = lmList[0][1]

        # Process the thumb
        if thumbTipLoc_x > pinkyTipLoc_x:
            res = self.detectThumb("right", res, thumbTipLoc_x, thumbBaseLoc_x)
        else:
            res = self.detectThumb("left", res, thumbTipLoc_x, thumbBaseLoc_x)

        # Process other fingers
        # lmList is a list of lists of format: [node number, center_x, center_y]
        for id in range(2,9,2):
            tipLoc = lmList[id+1][2]
            baseLoc = lmList[id][2]
            
            # y position of greater is more down
            if (baseLoc - tipLoc) > 0:
                res.append(1)
            else:
                res.append(0)
        
        return res

    '''
    Single Frame Function
    At any frame, get the count of fingers up from both hands

    Requires that lmBoth is not None
    Requires that len(lmBoth) > 0
    '''
    def getBothFingersUp(self, lmBoth) -> tuple[list[int], list[int]]:
        # Initialize the hand landmark location lists of each hand
        firstDetected: list[int] = []
        secondDetected: list[int] = []

        if len(lmBoth) > 0:
            firstDetected = self.detect(lmBoth[0], firstDetected)

        if len(lmBoth) > 1:
            secondDetected = self.detect(lmBoth[1], secondDetected)    
        
        '''
        Process Return Element
        '''
        totalFirst = 0
        totalSecond = 0

        if firstDetected:
            totalFirst = firstDetected.count(1)
        if secondDetected:
            totalSecond = secondDetected.count(1)
        
        return firstDetected, secondDetected


"""
---------------
Dummy Main Code
Will use this class' functions
"""
def main():
    # Set up time to calculate frames per second
    pTime = 0
       
    # Begins video capture and takes in which camera to be activated
    cap = cv.VideoCapture(0)

    # Construct a new handDetector object
    detector = handDetector()

    # Continously takes frames from video input
    while True:
        # Reading returns bool, image
        # if the bool is false, that means there is an issue with video input
        success, frame = cap.read()
        newFrame = detector.findHands(frame)
        handLocList, _ = detector.findHandLocations(frame)
        bothHandLocList, _ = detector.findBothHandLocations(frame)

        # if bothHandLocList and len(bothHandLocList) > 0:
        #     print(bothHandLocList)

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

if __name__ == "__main__":
    main()