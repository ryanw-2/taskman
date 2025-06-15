from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text

# User - user, pass, email
# Calendar - record events
# Checklist - record tasks
# Notepad - record notes
# SmartSearch - record prompts/questions asked

# class User(Base):
#     __tablename__ = 'users'

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String(50), unique=True, index=True, nullable=False)
#     email = Column(String(255), unique=True, index=True, nullable=False)
#     hashed_pass = Column(String(255), nullable=False)
#     created_at = Column(DateTime, default=datetime.now(timezone.utc))

#     events = relationship("EventList", back_populates="owner")
#     tasks = relationship("TaskList", back_populates="owner")
#     notes = relationship("NoteList", back_populates="owner")
#     searches = relationship("SearchList", back_populates="owner")

# class EventList(Base):
#     __tablename__ = 'eventlist'

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String(100))
#     desc = Column(String(255))
#     event_date = Column(DateTime, default=datetime.now(timezone.utc))


#     owner_id = Column(Integer, ForeignKey("users.id"))
    

class TaskList(Base):
    __tablename__ = 'tasklist'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    desc = Column(String(255))
    priority = Column(String(50))
    complete = Column(Boolean)

    # owner_id = Column(Integer, ForeignKey("users.id"))

# class NoteList(Base):
#     __tablename__ = 'notelist'

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String(100))
#     body = Column(Text)

#     owner_id = Column(Integer, ForeignKey("users.id"))

# class SearchList(Base):
#     __tablename__ = 'searchlist'

#     id = Column(Integer, primary_key=True, index=True)
#     prompt = Column(String(255))
#     response = Column(Text)

#     owner_id = Column(Integer, ForeignKey("users.id"))