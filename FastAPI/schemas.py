from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Data Validation using Pydantic
# User Schema -------------------------

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

# Allows model to be initialized using objects
    class Config:
        from_attributes = True

# Token schema ----------------------

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Event schema ----------------------
class EventBase(BaseModel):
    title: str
    desc: str

class EventCreate(EventBase):
    event_date = datetime

class Event(EventBase):
    id = int
    created_at = datetime
    owner_id = int

    class Config:
        from_attributes = True

# Task Schema ---------------------
class TaskBase(BaseModel):
    title: str
    desc: str
    complete: Optional[bool] = False
    priority: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

# Note Schema ----------------------
class NoteBase(BaseModel):
    title: str
    body: str

class NoteCreate(NoteBase):
    pass

class Note(NoteBase):
    id: int
    owner_id = int

    class Config:
        from_attributes = True

# Search Schema ------------------
class SearchBase(BaseModel):
    prompt: str
    response: str

class SearchCreate(SearchBase):
    pass

class Search(SearchBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True



