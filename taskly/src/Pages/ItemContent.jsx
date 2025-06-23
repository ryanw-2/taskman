// src/ItemContent.jsx
import React, { useState, useEffect, useRef } from "react";
import api from "../API";
import "./ItemContent.css";
import timer from "../assets/stopwatch_icon.png";
import note from "../assets/notepad_icon.png";
import { motion } from "framer-motion";
import { toDate, format} from 'date-fns-tz';

const getTopPosition = (date, userTimezone) => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  if (isNaN(dateObj.getTime())) return 0; // Guard against invalid dates

  const hours = parseInt(format(dateObj, 'H', { timeZone: userTimezone }));
  const minutes = parseInt(format(dateObj, 'm', { timeZone: userTimezone }));
  const totalMinutes = hours * 60 + minutes;
  return (totalMinutes / 1440) * 100;
};


// This component just renders the 'insides' of a grid item
const ItemContent = ({ item, tasklist, eventlist, chatHistory }) => {
  const timeIndicatorRef = useRef(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  
  // Use a motion.h3 for the title to allow for smoother text animation
  const title = item.title ? (
    <motion.h3 layout="position">
      <h4>{item.title}</h4>
    </motion.h3>
  ) : null;

  let content;
  if (item.id === "Timer") {
    content = (
      <div className="icon">
        <img src={timer} alt="timer icon" />
      </div>
    );
  } else if (item.id === "Notepad") {
    content = (
      <div className="icon">
        <img src={note} alt="notepad icon" />
      </div>
    );
  } else if (item.id === "Calendar") {
    const sortedEvents = [...(eventlist || [])].sort((a, b) => new Date(a.date) - new Date(b.date));
    const userTimezone = "America/Los_Angeles";
    const hours = Array.from({ length: 24 }, (_, i) => i);

    content = (
      // FIX: New wrapper to hold both title and timeline
      <div className="calendar-grid-view">
        <div className="time-scale-grid">
          {hours.map(hour => (
            <div key={hour} className="hour-marker-grid">
              <span>{hour === 12 ? '12P' : hour > 12 ? `${hour % 12}P` : hour === 0 ? '12A' : `${hour}A`}</span>
            </div>
          ))}
        </div>
        <div className="timeline-grid">
          {sortedEvents.map(event => (
            <div key={event.id} className="event-card-grid" style={{ top: `${getTopPosition(event.date, userTimezone)}%` }}>
              <div className="event-title-grid">{event.title}</div>
            </div>
          ))}
          <div 
            ref={timeIndicatorRef}
            className="time-indicator-grid" 
            style={{ top: `${getTopPosition(currentTime, userTimezone)}%` }}
          ></div>
        </div>
      </div>
    );
  } else if (item.id === "Smart Search") {
    content = (
      <div className="smart-search-view" readOnly>
        <div className="chat-history">
          {chatHistory.map((msg, index) => (
            <div key={index} className={`chat-message ${msg.sender}`}>
              <p>{msg.text}</p>
            </div>
          ))}
        </div>
      </div>
    );
  } else if (item.id === "Checklist") {
    content = (
      <div className="task-list-container">
        {tasklist.map((task, index) => (
          <div key={task.id}
               className={`task-card`}
          >
            <div className="task-card-title">
              <input
                type="checkbox"
                checked={task.complete}
                readOnly
                className="task-checkbox"
              />
              <h4 className={task.complete ? 'completed' : ''}>
                {task.title}
              </h4>
            </div>

            <div className="task-card-details">
              <p className="task-description">{task.desc}</p>
              <div className="task-meta">
                <span className={`priority-badge priority-${task.priority.toLowerCase()}`}>
                  {task.priority}
                </span>
              </div>
            </div>

          </div>
        ))}
      </div>
    );
  } else {
    content = <div className="placeholder-content"></div>;
  }

  return (
    <>
      {title}
      {content}
    </>
  );
};

export default ItemContent;
