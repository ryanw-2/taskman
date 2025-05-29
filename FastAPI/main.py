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

# class CreateTodoItem(BaseModel):
#     title: str
#     desc: Optional[str] = None
#     priority: Optional[str] = None
#     complete: Optional[bool] = None

# class UpdateTodoItem(BaseModel):
#     title: Optional[str] = None
#     desc: Optional[str] = None
#     priority: Optional[str] = None
#     complete: Optional[bool] = None


# todo_db = [
#     TodoItem(id=1, title="T1", desc="Walking the dog", priority="Medium", complete=False),
#     TodoItem(id=2, title="T2", desc="Mowing the lawn", priority="Low"),
#     TodoItem(id=3, title="T3"),
#     TodoItem(id=4, title="T4", complete=True),
# ]
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





# def get_next_id():
#     return max([todo.id for todo in todo_db]) + 1

# @app.get("/todos", response_model=List[TodoItem])
# def get_all_todos():
#     return todo_db


# @app.get("/todos/{todo_id}", response_model=TodoItem)
# def get_todo_by_id(todo_id: int):
#     for todo in todo_db:
#         if todo.id == todo_id:
#             return todo
#     raise HTTPException(
#         status_code=404, detail=f"Todo item with id {todo_id} not found"
#     )

# @app.post("/todos", response_model=TodoItem, status_code=201)
# def new_todo(new_todo_item: CreateTodoItem):
#     # Creates a new todo item
#     todo = TodoItem(
#         id = get_next_id(),
#         title= new_todo_item.title
#     )
#     if new_todo_item.desc is not None:
#         todo.desc = new_todo_item.desc
#     if new_todo_item.priority is not None:
#         todo.priority = new_todo_item.priority
#     if new_todo_item.complete is not None:
#         todo.complete = new_todo_item.complete

#     # Appends new todo item to database
#     todo_db.append(todo)
#     return todo

# @app.put("/todos/{todo_id}", response_model=TodoItem)
# def update_todo(todo_id: int, update_info: UpdateTodoItem):
#     for todo in todo_db:
#         if todo.id == todo_id:
#             update_todo = todo
#             if update_info.title is not None:
#                 update_todo.title = update_info.title
#             if update_info.desc is not None:
#                 update_todo.desc = update_info.desc
#             if update_info.priority is not None:
#                 update_todo.priority = update_info.priority
#             if update_info.complete is not None:
#                 update_todo.complete = update_info.complete
#             return update_todo
#     raise HTTPException(
#         status_code=404, detail=f"Todo item with id {todo_id} not found"
#     )

# @app.delete("/todos/{todo_id}", status_code=204)
# def delete_todo(todo_id: int):
#     for todo in todo_db:
#         if todo_id == todo.id:
#             todo_db.remove(todo)
#             return
#     raise HTTPException(
#         status_code=404, detail=f"Todo item with id {todo_id} not found"
#     )