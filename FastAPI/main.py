# --- Standard Library Imports ---
import asyncio
import json
import os
from datetime import datetime, time, timedelta
from typing import Annotated, AsyncGenerator, List, Optional, Tuple

# --- Third-Party Imports ---
import cv2 as cv
import numpy as np
import pytz
import uvicorn
from dotenv import load_dotenv
from fastapi import (Depends, FastAPI, HTTPException, Response, WebSocket,
                   WebSocketDisconnect)
from starlette.websockets import WebSocketState
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import Date, cast
from sqlalchemy.orm import Session
"""
GCP VERTEX
"""
from google.cloud import aiplatform
from google.cloud import aiplatform_v1
from vertexai.preview.generative_models import GenerativeModel
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.aiplatform_v1.services.prediction_service import client as prediction_service_client
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
import aiohttp

# --- Local Application Imports ---
import handTrackingModule as htm
import models
from database import SessionLocal, engine

# --- Load Environment Variables ---
# This should be called once, right after all imports.
load_dotenv()

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
"""
------------------------ SPEECH TO TEXT CONFIG -------------------------
"""
PROJECT_ID = "first-provider-463201-q5"
LOCATION = "us-central1"

speech_config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
    sample_rate_hertz=16000,
    language_code="en-US",
    enable_automatic_punctuation=True,
    model="telephony",
)

streaming_config = speech.StreamingRecognitionConfig(
    config=speech_config,
    interim_results=True,
)


"""
------------------------ GEMINI CONFIG -------------------------
"""
async def get_gemini_response(text_prompt: str, websocket: WebSocket):
    """
    Sends a prompt to the Gemini API using the high-level Vertex AI SDK
    and streams the response back through the provided WebSocket.
    """
    try:
        # Initialize the generative model with the desired model name
        model = GenerativeModel("gemini-2.5-flash")
        
        # Generate content with streaming enabled. This is the modern, correct method.
        responses = model.generate_content(text_prompt, stream=True)
        
        # Stream the response chunks back to the client as they arrive
        for response in responses:
            # The response object contains the text directly
            await websocket.send_text(response.text)

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        await websocket.send_text("Sorry, I couldn't get a response.")
"""
------------------------ DATABASE CONFIG -------------------------
"""

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Session is a type hint, Depends tells FastAPI to first call get_db
# The value of get_db is then injected as an argument into the endpoints
db_dependency = Annotated[Session, Depends(get_db)]
# creating our database
models.Base.metadata.create_all(bind=engine)

"""
------------------------ PYDANTIC MODELS -------------------------
"""
class TaskBase(BaseModel):
    title: str
    desc: str
    priority: str
    complete: bool

class CompleteTaskBase(BaseModel):
    complete: bool

    class Config:
        from_attributes = True

class TaskModel(TaskBase):
    id: int

    # Pydantic expects to read data from
    # a dictionary by default
    # However, SQL Alchemy uses Object Relational Mapper ORM
    # my_orm_object.title instead of my_dict['title']
    class Config:
        from_attributes = True

class EventBase(BaseModel):
    title: str
    desc: str
    link: str
    date: datetime

class EventModel(EventBase):
    id: int

    class Config:
        from_attributes = True

"""
------------------------ ENDPOINTS -------------------------
"""
@app.websocket("/ws/smart-search")
async def smart_search_websocket(websocket: WebSocket):
    await websocket.accept()
    
    audio_queue = asyncio.Queue()

    async def receive_audio():
        """Producer: Receives audio from the client and puts it into the queue."""
        try:
            while True:
                audio_chunk = await websocket.receive_bytes()
                await audio_queue.put(audio_chunk)
        except WebSocketDisconnect:
            print("Client disconnected.")
            await audio_queue.put(None)

    async def audio_stream_generator():
        """Generator that yields requests for the Speech-to-Text API."""
        yield speech.StreamingRecognizeRequest(streaming_config=streaming_config)
        while True:
            chunk = await audio_queue.get()
            if chunk is None:
                break
            yield speech.StreamingRecognizeRequest(audio_content=chunk)

    async def process_transcriptions():
        """Consumer: Processes transcription results and sends them to the client."""
        speech_client = speech.SpeechAsyncClient()
        responses_iterator = speech_client.streaming_recognize(requests=audio_stream_generator())
        async_iterable = await responses_iterator
        async for response in async_iterable:
            if not response.results or not response.results[0].alternatives:
                continue

            result = response.results[0]
            print(result)
            transcript = result.alternatives[0].transcript.strip()

            if not transcript:
                continue

            if result.is_final:
                print(f"Final Transcription: {transcript}")
                await websocket.send_text(f"[USER] {transcript}")
                await websocket.send_text("[THINKING]")
                await get_gemini_response(transcript, websocket)
                await websocket.send_text("[END_OF_RESPONSE]")
            else:
                await websocket.send_text(f"[INTERIM] {transcript}")

    receive_task = asyncio.create_task(receive_audio())
    process_task = asyncio.create_task(process_transcriptions())

    try:
        await asyncio.gather(receive_task, process_task)
    except Exception as e:
        print(f"An error occurred in the main WebSocket task: {e}")
    finally:
        receive_task.cancel() 
        process_task.cancel()
        print("WebSocket connection cleanup completed.")
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()

@app.post("/calendar/")
async def create_eventlist(eventlist: EventBase, db: db_dependency):
    """
    Obtains the database from database, updates it, and refreshes it
    """
    # model dump converts library into dictionary
    # ** is python's unpacking operator
    db_eventlist = models.EventList(**eventlist.model_dump())
    db.add(db_eventlist)
    db.commit()
    db.refresh(db_eventlist)
    return db_eventlist

@app.get("/calendar/today/", response_model=List[EventModel])
async def read_today_eventlist(db: db_dependency, skip: int = 0, limit: int = 20):
    """
    Reads Today's items from the database, based on the current date
    in the Pacific Timezone, compatible with SQLite.
    """
    pacific_tz = pytz.timezone("America/Los_Angeles")

    start_of_today_pacific = datetime.now(pacific_tz).replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_tomorrow_pacific = start_of_today_pacific + timedelta(days=1)

    start_of_today_utc = start_of_today_pacific.astimezone(pytz.utc)
    start_of_tomorrow_utc = start_of_tomorrow_pacific.astimezone(pytz.utc)

    eventlist = db.query(models.EventList).filter(
        models.EventList.date >= start_of_today_utc,
        models.EventList.date < start_of_tomorrow_utc
    ).offset(skip).limit(limit).all()

    return eventlist

@app.get("/calendar/month/", response_model=List[EventModel])
async def read_month_eventlist(db: db_dependency, skip: int = 0, limit: int = 1000):
    """
    Reads this Month's items from the database, based on the current date
    in the Pacific Timezone, compatible with SQLite.
    """
    pacific_tz = pytz.timezone("America/Los_Angeles")

    this_month = datetime.now(pacific_tz).month
    next_month = this_month + 1 if this_month < 13 else 1
    start_of_month_pacific = datetime.now(pacific_tz).replace(month=this_month, minute=0, second=0, microsecond=0)
    start_of_next_month_pacific = datetime.now(pacific_tz).replace(month=next_month, minute=0, second=0, microsecond=0)

    start_of_month_utc = start_of_month_pacific.astimezone(pytz.utc)
    start_of_next_month_utc = start_of_next_month_pacific.astimezone(pytz.utc)

    eventlist = db.query(models.EventList).filter(
        models.EventList.date >= start_of_month_utc,
        models.EventList.date < start_of_next_month_utc
    ).offset(skip).limit(limit).all()

    return eventlist

@app.get("/calendar/", response_model=List[EventModel])
async def read_eventlist(db: db_dependency, skip: int = 0, limit: int = 100):
    """
    Reads all items up to limit (100) items from the database
    """
    eventlist = db.query(models.EventList).offset(skip).limit(limit).all()
    return eventlist

@app.delete("/calendar/clear-all")
async def clear_all_events(db: db_dependency):
    """
    Deletes all events from the eventlist table.
    USE WITH CAUTION: This action is irreversible.
    """
    try:
        # Perform a bulk delete on the EventList table
        num_rows_deleted = db.query(models.EventList).delete(synchronize_session=False)
        
        # Commit the transaction to make the changes permanent
        db.commit()
        
        # Return a success message
        return {"message": f"Successfully deleted {num_rows_deleted} events."}
    except Exception as e:
        # If anything goes wrong, roll back the transaction
        db.rollback()
        # And raise an HTTP exception
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.post("/checklist/")
async def create_task(tasklist: TaskBase, db: db_dependency):
    """
    Obtains the database from database, updates it, and refreshes it
    """
    # model dump converts library into dictionary
    # ** is python's unpacking operator
    db_tasklist = models.TaskList(**tasklist.model_dump())
    db.add(db_tasklist)
    db.commit()
    db.refresh(db_tasklist)
    return db_tasklist

@app.patch("/checklist/{task_id}", response_model=TaskModel)
async def complete_task(task_id: int, taskUpdate: CompleteTaskBase, db: db_dependency):
    """
    Updates the completeness of a task
    """
    # model dump converts library into dictionary
    # ** is python's unpacking operator
    db_task = db.query(models.TaskList).filter(models.TaskList.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    setattr(db_task, 'complete', taskUpdate.complete)

    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/checklist/", response_model=List[TaskModel])
async def read_tasklist(db: db_dependency, skip: int = 0, limit: int = 10):
    """
    Reads up to limit (10) items from the database
    """
    tasklist = db.query(models.TaskList).offset(skip).limit(limit).all()
    return tasklist

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
