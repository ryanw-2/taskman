from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

items = []


class TodoItem(BaseModel):
    id: int
    task: str
    complete: bool

class CreateTodoItem(BaseModel):
    task: str
    complete: bool

class UpdateTodoItem(BaseModel):
    task: Optional[str] = None
    complete: Optional[bool] = None


todo_db = [
    TodoItem(id=1, task="T1", complete=True),
    TodoItem(id=2, task="T2", complete=False),
]

def get_next_id():
    return max([todo.id for todo in todo_db]) + 1

@app.get("/todos", response_model=List[TodoItem])
def get_all_todos():
    return todo_db


@app.get("/todos/{todo_id}", response_model=TodoItem)
def get_todo_by_id(todo_id: int):
    for todo in todo_db:
        if todo.id == todo_id:
            return todo
    raise HTTPException(
        status_code=404, detail=f"Todo item with id {todo_id} not found"
    )

@app.post("/todos", response_model=TodoItem, status_code=201)
def new_todo(new_todo_item: CreateTodoItem):
    todo = TodoItem(
        id = get_next_id(),
        task= new_todo_item.task,
        complete = new_todo_item.complete
    )

    todo_db.append(todo)
    return todo

@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, update_info: UpdateTodoItem):
    for todo in todo_db:
        if todo.id == todo_id:
            update_todo = todo
            if update_info.task is not None:
                update_todo.task = update_info.task
            if update_info.complete is not None:
                update_todo.complete = update_info.complete
            return update_todo
    raise HTTPException(
        status_code=404, detail=f"Todo item with id {todo_id} not found"
    )

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    for todo in todo_db:
        if todo_id == todo.id:
            todo_db.remove(todo)
            return
    raise HTTPException(
        status_code=404, detail=f"Todo item with id {todo_id} not found"
    )