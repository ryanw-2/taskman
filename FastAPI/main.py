import asyncio
import numpy as np
import cv2 as cv
import uvicorn
import threading
import json
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

'''
Create database tables and initialize app
'''
# db_dependency = Annotated[Session, Depends(get_db)]
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

'''
Allows React website, which is hosted to localhost3000
to call FastAPI backend. Origins may include more urls.
'''
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Patiently waits for the front-end connection. Once 
    the front-end connects, a persistent, two-way connection
    is established between FastAPI backend and React front-end.
    """
    await websocket.accept()

    # start video processing
    cap = cv.VideoCapture(0)
    detector = htm.handDetector(minDetectionConf=0.55)

    try:
        while True:
            
            success, frame = cap.read()
            if not success:
                break

            frame = cv.flip(frame, 1)
            frame = cv.addWeighted(frame, 1.2, np.zeros(frame.shape, frame.dtype), 0, 0)
            lmBothList, bb = detector.find2Hands(frame)

            gap_length = 50
            if lmBothList and len(lmBothList) > 0:
                for lmList in lmBothList:
                    if lmList and detector.isLeft(lmList):
                        gap_length, center_x, center_y = detector.findDistance(frame, lmList, 1, 3, False)
                        if center_y < 160:
                            detector.setCursorState(gap_length, center_x, center_y)
                            break
            
            
            gesture = detector.getCursorGesture()
            # Key component to send data over to the front-end
            await websocket.send_text(json.dumps({'gesture': gesture}))

            # Small delay to prevent overwhelming the client
            await asyncio.sleep(0.02)

    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        cap.release()
        print("Camera released")



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
