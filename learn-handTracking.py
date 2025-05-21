import cv2 as cv
import mediapipe as mp
import time


# Begins video capture and takes in which camera to be activated
cap = cv.VideoCapture(0)


# Set up mediapipe library and tools
mpHands = mp.solutions.hands # type: ignore
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils #type: ignore

# Set up time to calculate frames per second
pTime = 0
cTime = 0

# Continously takes frames from video input
while True:
    # Reading returns bool, image
    # if the bool is false, that means there is an issue with video input
    success, frame = cap.read()

    # Mediapipe works in RGB
    rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    # Using Hands module in Media Pipe to detect hands
    results = hands.process(rgb)

    # Using Hands Landmarks to find each node and connections
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            # id marks which finger node
            # landmark specifies the location as a ratio of the window size
            for id, lm in enumerate(handLms.landmark):
                height, width, channel = frame.shape
                # multiplies the ratio with frame size
                center_x, center_y = int(lm.x * width), int(lm.y * height)
                
                # returns a list of 
                # node number : center_x, center_y


            mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)

    # Calculate FPS
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime


    # Screen/GUI Set up
    cv.putText(frame, str(int(fps)), (10,70), cv.FONT_HERSHEY_SIMPLEX, 3, (255,255,255), 3)

    cv.imshow('frame', frame)
    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()