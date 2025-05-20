import cv2 as cv
import mediapipe as mp
import time

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

    '''
    Draws nodes and connections on frame
    Returns frame
    '''
    def findHands(self, frame, draw = True):
        # Mediapipe works in RGB
        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        # Using Hands module in Media Pipe to detect hands
        self.results = self.hands.process(rgb)

        # Using Hands Landmarks to find each node and connections
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                # id marks which finger node
                # landmark specifies the location as a ratio of the window size
                if draw:
                    self.mpDraw.draw_landmarks(frame, handLms, self.mpHands.HAND_CONNECTIONS)
                    
                    # TODO optimize
                    # for id, lm in enumerate(handLms.landmark):
                    #     height, width, channel = frame.shape
                    #     # multiplies the ratio with frame size
                    #     center_x, center_y = int(lm.x * width), int(lm.y * height)
                        
                    #     # returns a list of 
                    #     # node number : center_x, center_y           
        
        return frame
    
    '''
    Finds the center-x and center-y locations of a specified hand.
    Intuitively, this function may serve well if the user is trying
    to track one hand at a time.
    Returns a list comprised of the [node id, center_x, center_y]
    '''
    def findHandLocations(self, frame, hand=0, draw=False):
        lmLocList = []
        
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[hand]
            for id, lm in enumerate(myHand.landmark):
                height, width, channel = frame.shape
                # multiplies the ratio with frame size
                center_x, center_y = int(lm.x * width), int(lm.y * height)

                lmLocList.append([id, center_x, center_y])

                if draw:
                    cv.circle(frame, (center_x, center_y), 15, (255, 0, 255), cv.FILLED)

        return lmLocList
    
    '''
    Finds the center-x and center-y locations of both hands.
    Returns a list comprised of a list of two elements of format : [node id, center_x, center_y]
    Each index of the returned list are the node id and locations of one hand.
    '''
    def findBothHandLocations(self, frame, draw=False):
        lmBothLocList = []
        
        if self.results.multi_hand_landmarks:
            
            for myHand in self.results.multi_hand_landmarks:
                singleLocList = []
                for id, lm in enumerate(myHand.landmark):
                    height, width, channel = frame.shape
                    # multiplies the ratio with frame size
                    center_x, center_y = int(lm.x * width), int(lm.y * height)

                    singleLocList.append([id, center_x, center_y])

                    if draw:
                        cv.circle(frame, (center_x, center_y), 15, (255, 0, 255), cv.FILLED)
                
                lmBothLocList.append(singleLocList)

        return lmBothLocList


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
        handLocList = detector.findHandLocations(frame)
        bothHandLocList = detector.findBothHandLocations(frame)

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