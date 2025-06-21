import cv2 as cv
import numpy as np
import mediapipe as mp
import math
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

class handDetector:
    """
    Class to detect and draw
    hands, fingers, and swiping gestures.
    """

    def __init__(
        self,
        mode=False,
        maxHands=2,
        modelComplexity=1,
        minDetectionConf=0.5,
        minTrackingConf=0.5,
    ):
        """
        HandDetector constructor to set up mediapipe library
        and initialize cursor state.
        """
        self.mode = mode
        self.max_num_hands = maxHands
        self.model_complexity = modelComplexity
        self.min_detection_confidence = minDetectionConf
        self.min_tracking_confidence = minTrackingConf

        # Set up mediapipe library and tools
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            self.mode,
            self.max_num_hands,
            self.model_complexity,
            self.min_detection_confidence,
            self.min_tracking_confidence,
        )

        self.mpDraw = mp.solutions.drawing_utils 

        # Set up cursor state
        self.starting_x = 0
        self.starting_y = 0
        self.cursorState = "none"
        self.cursorGesture = "none"

    def drawHands(self, frame):
        """
        Draws hand nodes and connections of any detectable
        hand.

        :param: A Matlike frame read from video capture
        :return: A Matlike frame with hand nodes and connections drawn on it
        """
        # Mediapipe works in RGB
        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        # Using Mediapipe Hands module to detect hands
        hands_detected = self.hands.process(rgb)

        if hands_detected:
            for handLms in hands_detected:
                # Using Mediapipe Hands module to draw nodes and connections
                self.mpDraw.draw_landmarks(
                    frame, handLms, self.mpHands.HAND_CONNECTIONS
                )

        return frame

    def isValidId(self, id: int) -> bool:
        """
        Filters hand node ID's.
        A complete list of hand nodes may be found here:
        https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker

        :return: Boolean
        """

        return (
            id == 3  # Thumb Base
            or id == 4  # Thumb Tip
            or id == 6  # Index Base
            or id == 8  # Index Tip
            or id == 10  # Middle Base
            or id == 12  # Middle Tip
            or id == 14  # Ring Base
            or id == 16  # Ring Tip
            or id == 18  # Pinky Base
            or id == 20  # Pinky Tip
        )

    def find2Hands(self, frame, draw=True):
        """
        Finds the center-x and center-y locations of filtered hand nodes,
        and a bounding box each hand.

        :return: Tuple of List of List of hand node id and location,
        and List of bounding box boundary coordinates for each hand
        """
        # Mediapipe works in RGB
        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        # Using Hands module in Media Pipe to detect hands
        hands_detected = self.hands.process(rgb)

        height, width, _ = frame.shape
        bothLmList = []
        bbList = []

        if hands_detected.multi_hand_landmarks:
            for hand in hands_detected.multi_hand_landmarks:
                singleLmList = []

                xMin = 0
                xMax = width
                yMin = 0
                yMax = height

                for id, lm in enumerate(hand.landmark):
                    if id == 0:  # Palm Bottom
                        yMin = int(lm.y * height)
                    elif id == 4:  # Thumb
                        xMin = int(lm.x * width)
                    elif id == 12:  # Middle Tip
                        yMax = int(lm.y * height)
                    elif id == 20:  # Pinky Tip
                        xMax = int(lm.x * width)

                    if self.isValidId(id):
                        singleLmList.append([id, int(lm.x * width), int(lm.y * height)])

                bbList.append((xMin, yMin, xMax, yMax))
                bothLmList.append(singleLmList)

                if draw:
                    cv.rectangle(
                        frame,
                        (xMin, yMin),
                        (xMax, yMax),
                        (0, 255, 0),
                        1,
                    )

        return bothLmList, bbList

    def findHandLocations(self, frame, hand=0, draw=False):
        """
        Private Legacy
        """
        lmLocList = []
        boundingBox = []
        # Mediapipe works in RGB
        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        # Using Hands module in Media Pipe to detect hands
        hands_detected = self.hands.process(rgb)
        if hands_detected.multi_hand_landmarks:
            myHand = hands_detected.multi_hand_landmarks[hand]
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
                cv.rectangle(
                    frame,
                    (boundingBox[0] - buffer, boundingBox[1] - buffer),
                    (boundingBox[2] + buffer, boundingBox[3] + buffer),
                    (0, 255, 0),
                    1,
                )

        return lmLocList, boundingBox

    def findBothHandLocations(self, frame, draw=False):
        """
        Private Legacy
        """
        # Mediapipe works in RGB
        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        # Using Hands module in Media Pipe to detect hands
        hands_detected = self.hands.process(rgb)
        lmBothLocList = []
        bBoxList = []
        if hands_detected.multi_hand_landmarks:

            for myHand in hands_detected.multi_hand_landmarks:
                xList = []
                yList = []
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
                    cv.rectangle(
                        frame,
                        (boundingBox[0] - buffer, boundingBox[1] - buffer),
                        (boundingBox[2] + buffer, boundingBox[3] + buffer),
                        (0, 255, 0),
                        1,
                    )

                bBoxList.append(boundingBox)
                lmBothLocList.append(singleLocList)

        return lmBothLocList, bBoxList

    def findDistance(self, frm, lmList, point1, point2, draw=False):
        """
        Gets the distance, center x-coord, and center-y coord
        of two given hand nodes.

        :return: Tuple of Float distance, center x-coord, and center y-coord
        """
        # Find distance between the given hand nodes
        first_x, first_y = lmList[point1][1], lmList[point1][2]
        second_x, second_y = lmList[point2][1], lmList[point2][2]
        center_x, center_y = (first_x + second_x) // 2, (first_y + second_y) // 2

        gapLength = math.hypot(second_x - first_x, second_y - first_y)

        if draw:
            cv.line(frm, (first_x, first_y), (second_x, second_y), (110, 170, 255), 1)
            cv.circle(frm, (center_x, center_y), 10, (0, 106, 255), cv.FILLED)
            # if the distance is between the hand nodes is practically zero
            # hand must be in the upper half of the screen to be detectable
            if gapLength < 30 and center_y < 180:
                cv.circle(frm, (center_x, center_y), 10, (204, 255, 0), cv.FILLED)

        return gapLength, center_x, center_y

    def setCursorState(self, gapIndex, center_x, center_y) -> None:
        """
        Detects clicks and hand swipes, and
        sets the cursor state and cursor gesture
        """

        gesture = "none"

        # initialize values
        if gapIndex < 30 and self.cursorState == "none":
            self.starting_x = center_x
            self.starting_y = center_y
            self.cursorState = "hover"
        elif gapIndex > 30 and self.cursorState == "hover":
            x_difference = center_x - self.starting_x
            y_difference = center_y - self.starting_y

            if x_difference > 15:
                gesture = "rightswipe"
            elif x_difference < -15:
                gesture = "leftswipe"
            elif y_difference > 15:
                gesture = "downswipe"
            elif y_difference < -15:
                gesture = "upswipe"
            else:
                gesture = "click"

            self.cursorGesture = gesture
            self.cursorState = "none"

    def getCursorGesture(self) -> str:
        """
        Gets the current gesture detected.

        :return: String
        """
        result = self.cursorGesture
        self.cursorGesture = "none"
        return result

    def detectThumb(self, orientation, res, thumbTip, thumbBase):
        """
        Detects thumb orientation and whether the
        thumb is "opened" or "closed"
        """
        if not orientation:
            return []

        # right means thumb is more right than pinky
        if orientation == "right":
            # x position of less is more left
            if thumbBase < thumbTip:
                res.append(1)
            else:
                res.append(0)
        # left means thumb is more left than pinky
        else:  # orientation == "left"
            # x position of less is more left
            if thumbBase > thumbTip:
                res.append(1)
            else:
                res.append(0)

        return res

    def isLeft(self, lmList):
        """
        Detects if a hand, given its hand node list,
        is left or right.

        :return: Boolean
        """
        if not lmList or len(lmList) <= 0:
            return False

        pinkyTipLoc_x = lmList[9][1]
        thumbTipLoc_x = lmList[1][1]

        return thumbTipLoc_x < pinkyTipLoc_x

    def detect(self, lmList, res):
        """
        Detects if fingers of one given hand
        are up (1) or down (0). Used as a helper.
        """
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
        for id in range(2, 9, 2):
            tipLoc = lmList[id + 1][2]
            baseLoc = lmList[id][2]

            if (baseLoc - tipLoc) > 0:
                res.append(1)
            else:
                res.append(0)

        return res

    def getBothFingersUp(self, lmBoth) -> tuple[list[int], list[int]]:
        """
        Detects how many fingers are up.

        Requires that lmBoth is not None
        Requires that len(lmBoth) > 0
        """
        # Initialize the hand landmark location lists of each hand
        firstDetected: list[int] = []
        secondDetected: list[int] = []

        if len(lmBoth) > 0:
            firstDetected = self.detect(lmBoth[0], firstDetected)

        if len(lmBoth) > 1:
            secondDetected = self.detect(lmBoth[1], secondDetected)

        return firstDetected, secondDetected
