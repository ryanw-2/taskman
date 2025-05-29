from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Float

class TodoList(Base):
    __tablename__ = 'todolist'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    desc = Column(String)
    priority = Column(String)
    complete = Column(Boolean)