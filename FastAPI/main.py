import asyncio
import numpy as np
import cv2
import uvicorn
import threading

from typing import List, Optional, Annotated, Tuple, AsyncGenerator

from fastapi import FastAPI, Response, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
# from database import SessionLocal, engine, get_db
# import models

import handTrackingModule as htm

@asynccontextmanager
async def lifespan(app: FastAPI):
    '''
    Lifespan denotes the events that will occur before the 
    application starts taking any requests and right after 
    it finishes handling requests.
    '''
    try:
        yield
    except asyncio.exceptions.CancelledError as error:
        print(error.args)
    finally:
        camera.release()
        print("Camera resource released.")

'''
Create database tables and initialize app
'''
# db_dependency = Annotated[Session, Depends(get_db)]
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(lifespan=lifespan)
detector = htm.handDetector(minDetectionConf=0.5)

'''
Allows React website, which is hosted to localhost3000
to call FastAPI backend. Origins may include more urls.
'''
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

class Camera:
    """
    A class to handle video capture from a camera.
    """

    def __init__(self, cam_id) -> None:
        """
        Initialize the camera.

        :param cam_id: Index of the camera to use.
        """
        self.cap = cv2.VideoCapture(cam_id)
        self.lock = threading.Lock()

    def get_frame(self) -> bytes:
        """
        Capture a frame from the camera.

        :return: JPEG encoded image bytes.
        """
        with self.lock:
            ret, frame = self.cap.read()
            if not ret:
                return b''

            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                return b''

            return jpeg.tobytes()

    def is_mid_finger_up(self) -> bool:
        with self.lock:
            success, frame = self.cap.read()
            if not success:
                return False
            
            frame = detector.findHands(frame, draw=False)
            lmBothList, bb = detector.findBothHandLocations(frame)
            if lmBothList and len(lmBothList) > 0:
                firstDetected, secondDetected = detector.getBothFingersUp(lmBothList)
                if len(firstDetected) > 4 and len(secondDetected) > 4:
                    if firstDetected[2] == 1 or secondDetected[2] == 1:
                        print('yes')
                        return True
            
            return False

    def get_lmlists(self):
        with self.lock:
            success, frame = self.cap.read()
            if not success:
                return []
            
            frame = detector.findHands(frame, draw=False)
            lmBothList, bb = detector.findBothHandLocations(frame)

            return lmBothList
        
    def get_detected_lists(self) -> tuple[list[int], list[int]]:
        with self.lock:
            success, frame = self.cap.read()
            if not success:
                return tuple()
            
            frame = detector.findHands(frame, draw=False)
            lmBothList, bb = detector.findBothHandLocations(frame)

            firstDetected = [-1] * 5
            secondDetected = [-1] * 5
            if lmBothList and len(lmBothList) > 0:
                firstDetected, secondDetected = detector.getBothFingersUp(lmBothList)
            
            return (firstDetected, secondDetected)
    
    '''
    REQUIRES some_lmlist to not be None or empty
    '''
    def get_gap(self, some_lmlist, node1, node2) -> tuple[float, float, float]:
        with self.lock:
            success, frame = self.cap.read()
            if not success:
                return tuple()

            frame = detector.findHands(frame, draw=False)
            gapLength, center_x, center_y = detector.findDistance(frame, some_lmlist, node1, node2, True, draw=False)
            return gapLength, center_x, center_y
            


    def release(self) -> None:
        """
        Release the camera resource.
        """
        with self.lock:
            if self.cap.isOpened():
                self.cap.release()

'''
define a generate fingers function that keeps returning 2 binary int lists
with 1 denoting finger up 0 denoting finger down

define a get /fingers that returns a streaming response
'''

@app.get("/lmlists")
async def read_lmlists() :
    lmBothList = camera.get_lmlists()
    if not lmBothList:
        return [[-1], [-1]]
    elif len(lmBothList) == 1:
        return [lmBothList[0], []]
    else:
        return lmBothList

@app.get("/detectedlists")
async def read_detected_lists() -> Tuple[List[int], List[int]]:
    first, second = camera.get_detected_lists()
    return first, second

@app.get("/gap")
async def read_finger_gap() -> float:
    lmBothList = camera.get_lmlists()
    gap = 100.0
    for lmList in lmBothList:
        if lmList and detector.isLeft(lmList):
            gap, center_x, center_y = camera.get_gap(lmList, 4, 8)

    return gap

# ---------------------------------------------------------------------------------- #

async def gen_frames() -> AsyncGenerator[bytes, None]:
    """
    An asynchronous generator function that yields camera frames.

    :yield: JPEG encoded image bytes.
    """
    try:
        while True:
            frame = camera.get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                break
            await asyncio.sleep(0)
    except (asyncio.CancelledError, GeneratorExit):
        print("Frame generation cancelled.")
    finally:
        print("Frame generator exited.")


@app.get("/")
async def video_feed() -> StreamingResponse:
    """
    Video streaming route.

    :return: StreamingResponse with multipart JPEG frames.
    """
    return StreamingResponse(
        gen_frames(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )


@app.get("/snapshot")
async def snapshot() -> Response:
    """
    Snapshot route to get a single frame.

    :return: Response with JPEG image.
    """
    frame = camera.get_frame()
    if frame:
        return Response(content=frame, media_type="image/jpeg")
    else:
        return Response(status_code=404, content="Camera frame not available.")


async def main():
    """
    Main entry point to run the Uvicorn server.
    """
    config = uvicorn.Config(app, host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)

    # Run the server
    await server.serve()

if __name__ == '__main__':
    camera = Camera(0)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped by user.")
