import React, { useState, useEffect, useRef } from "react";
import api from "../API";
import "./ExpandedItemView.css";
import { motion } from "framer-motion"; // 1. Import motion
import { toDate, format} from 'date-fns-tz';

// 2. Accept layoutId as a prop
const getTopPosition = (date, userTimezone) => {
  // We need to create a Date object first if it's a string
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const hours = parseInt(format(dateObj, 'H', { timeZone: userTimezone }));
  const minutes = parseInt(format(dateObj, 'm', { timeZone: userTimezone }));
  const totalMinutes = hours * 60 + minutes;
  return (totalMinutes / 1440) * 100;
};

const ExpandedItemView = ({
  item,
  onClose,
  tasklist,
  eventlist,
  onEventSubmit,
  selectedTaskIndex,
  onToggleComplete,
  onTaskSubmit,
  isRecording,
  isThinking,
  chatHistory,
  interimTranscript,
  onStartRecord,
  onStopRecord,
}) => {
  // State for the "add new task" form is still managed locally.
  const [taskData, setTaskData] = useState({
    title: "",
    desc: "",
    priority: "",
    complete: false,
  });

  const [eventData, setEventData] = useState({
    title: "",
    desc: "",
    link: "",
    date: "",
  });

  const chatEndRef = useRef(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const timelineRef = useRef(null);
  const timeIndicatorRef = useRef(null);
  // Auto-scroll the chat history to the bottom
  useEffect(() => {
    if (item.id === "Smart Search"){
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    } 
  }, [chatHistory, isThinking, interimTranscript]);

  const handleInputChange = (event) => {
    const { name, value, type, checked } = event.target;
    setTaskData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleTaskSubmit = (event) => {
    event.preventDefault();
    onTaskSubmit(taskData); // Call the function passed down from Dashboard
    setTaskData({ title: "", desc: "", priority: "", complete: false }); // Reset form
  };
  
  useEffect(() => {
    if (item.id === "Calendar") {
      const timerId = setInterval(() => setCurrentTime(new Date()), 60000);
      setTimeout(() => {
        if (timeIndicatorRef.current) {
          timeIndicatorRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 100);
      return () => clearInterval(timerId);
    }
  }, [item.id]);

  const handleEventInputChange = (event) => {
    const { name, value } = event.target;
    setEventData(prev => ({ ...prev, [name]: value }));
  };

  // --- REVISED EVENT SUBMISSION HANDLER ---
  const handleEventSubmit = (event) => {
    event.preventDefault();

    const userTimezone = "America/Los_Angeles";
    const dateInputString = eventData.date; // e.g., "2025-06-20-09-30"

    try {
      const parts = dateInputString.split('-').map(part => parseInt(part, 10));
      if (parts.length !== 5 || parts.some(isNaN)) {
        throw new Error("Invalid date components.");
      }
      
      const [year, month, day, hour, minute] = parts;
      // WORKING
      const utcDate = new Date(Date.UTC(year, month - 1, day, hour, minute));
      
      const submissionData = {
        title: eventData.title,
        desc: eventData.desc,
        link: eventData.link,
        date: utcDate.toISOString(),
      };

      onEventSubmit(submissionData);
      setEventData({ title: "", desc: "", link: "", date: "" });
      
    } catch (error) {
      console.error("Error processing date:", error);
      alert("Invalid date format. Please use YYYY-MM-DD-HH-MM.");
    }
  };


  // RENDER CONTENT
  let expContent;
  if (item.id === "Timer") {
    expContent = (
      <div>
        <h4>Timer</h4>
        <p>Set a focus timer</p>
      </div>
    );
  } else if (item.id === "Notepad") {
    expContent = (
      <div>
        <h4>Notepad</h4>
        <p>Click on the button to start recording</p>
      </div>
    );
  } else if (item.id === "Calendar") {
    const sortedEvents = [...eventlist].sort((a, b) => new Date(a.date) - new Date(b.date));
    const userTimezone = "America/Los_Angeles";
    const hours = Array.from({ length: 24 }, (_, i) => i);

    expContent = (
      <div className="calendar-view">
        <div className="calendar-timeline-container" ref={timelineRef}>
          <div className="time-scale">
            {hours.map(hour => (
              <div key={hour} className="hour-marker">
                <span>{hour === 0 ? '12 AM' : hour < 12 ? `${hour} AM` : hour === 12 ? '12 PM' : `${hour % 12} PM`}</span>
              </div>
            ))}
          </div>
          <div className="timeline">
            {sortedEvents.map(event => (
              <div key={event.id} className="event-card" style={{ top: `${getTopPosition(event.date, userTimezone)}%` }}>
                  <div className="event-time">{format(new Date(event.date), 'p', { timeZone: userTimezone })}</div>
                  <div className="event-title">{event.title}</div>
                  <p className="event-desc">{event.desc}</p>
              </div>
            ))}
            <div 
              ref={timeIndicatorRef}
              className="time-indicator" 
              style={{ top: `${getTopPosition(currentTime, userTimezone)}%` }}
            >
              <div className="time-indicator-dot"></div>
            </div>
          </div>
        </div>
        <form onSubmit={handleEventSubmit} className="add-event-form">
          <input name="title" value={eventData.title} onChange={handleEventInputChange} placeholder="Event Title" required />
          <input name="desc" value={eventData.desc} onChange={handleEventInputChange} placeholder="Description" />
          <input name="link" value={eventData.link} onChange={handleEventInputChange} placeholder="Link (e.g., zoom.us)" />
          <input name="date" value={eventData.date} onChange={handleEventInputChange} placeholder="Date (YYYY-MM-DD-HH-MM)" required />
          <button type="submit">Add Event</button>
        </form>
      </div>
    );
  } else if (item.id === "Smart Search") {
    expContent = (
      <div className="smart-search-view">
        <div className="chat-history">
          {chatHistory.map((msg, index) => (
            <div key={index} className={`chat-message ${msg.sender}`}>
              <p>{msg.text}</p>
            </div>
          ))}
          {/* Display the real-time transcript while recording */}
          {isRecording && interimTranscript && (
            <div className="chat-message user interim">
              <p>{interimTranscript}</p>
            </div>
          )}
          {isThinking && (
            <div className="chat-message ai">
              <div className="thinking-indicator"></div>
            </div>
          )}
          {/* Empty div to ensure auto-scroll works correctly */}
          <div ref={chatEndRef} />
        </div>
        <div className="search-controls">
          <button
            onClick={isRecording ? onStopRecord : onStartRecord}
            className={`record-button ${isRecording ? "recording" : ""}`}
          >
            {isRecording ? "Stop Recording" : "Start Recording"}
          </button>
        </div>
      </div>
    );
  } else if (item.id === "Checklist") {
    expContent = (
      <div className="checklist-wrapper">
        <div className="task-list-container">
          {tasklist.map((task, index) => (
            <div
              key={task.id}
              className={`task-card ${
                index === selectedTaskIndex ? "selected" : ""
              }`}
              onClick={() => onToggleComplete(task)} // Call parent's handler
            >
              <div className="task-card-title">
                <input
                  type="checkbox"
                  checked={task.complete}
                  readOnly
                  className="task-checkbox"
                />
                <h4 className={task.complete ? "completed" : ""}>
                  {task.title}
                </h4>
              </div>
              <div className="task-card-details">
                <p className="task-description">{task.desc}</p>
                <div className="task-meta">
                  <span
                    className={`priority-badge priority-${task.priority.toLowerCase()}`}
                  >
                    {task.priority}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
        <form className="add-task-form" onSubmit={handleTaskSubmit}>
          <input
            name="title"
            value={taskData.title}
            onChange={handleInputChange}
            placeholder="New Task Title"
            required
          />
          <input
            name="desc"
            value={taskData.desc}
            onChange={handleInputChange}
            placeholder="Description"
            required
          />
          <input
            name="priority"
            value={taskData.priority}
            onChange={handleInputChange}
            placeholder="Priority"
            required
          />
          <button type="submit">Add Task</button>
        </form>
      </div>
    );
  } else {
    expContent = <div></div>;
  }

  return (
    <motion.div
      className="expanded-view-overlay"
      onClick={onClose}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* 3. The element that matches the grid item gets the layoutId */}
      <motion.div
        className="expanded-view-content"
        onClick={(e) => e.stopPropagation()}
      >
        {/* You can add extra details that only appear when expanded */}
        <motion.div
          className="expanded-only-details"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1, transition: { delay: 0 } }}
          exit={{ opacity: 0 }}
        >
          {expContent}
        </motion.div>

        <motion.button className="close-button" onClick={onClose}>
          x
        </motion.button>
      </motion.div>
    </motion.div>
  );
};

export default ExpandedItemView;
