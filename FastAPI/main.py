from typing import List, Optional, Annotated
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import models

'''
Allows FastAPI to call the React website
'''
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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

items = []



class TodoItemBase(BaseModel):
    # ***ID provided by database
    # id: int

    # ***Title of task
    title: str

    # Description or notes of task
    desc: str

    # Priority of task: High, Medium, Low, None
    priority: str

    # ***Status of task
    complete: bool

class TodoItemModel(TodoItemBase):
    id: int

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

'''
Creating table
'''
models.Base.metadata.create_all(bind=engine)

'''
Endpoint Definitions
'''
# Creating a new todo item and adding it to database
@app.post("/todos/", response_model=TodoItemModel)
async def new_todo_item(item: TodoItemBase, db: db_dependency):
    db_todo = models.TodoList(**item.model_dump()) ###
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Retrieving items in the database
@app.get("/todos/", response_model=List[TodoItemModel])
async def read_items(db: db_dependency, skip: int = 0, limit: int= 100):
    todo_items = db.query(models.TodoList).offset(skip).limit(limit).all()
    return todo_items
