import React, { useState, useEffect } from "react";
import api from "../API";
import './ExpandedItemView.css';
import { motion } from 'framer-motion'; // 1. Import motion
import ItemContent from './ItemContent'; // Import the shared content

// 2. Accept layoutId as a prop

const ExpandedItemView = ({ item, onClose, tasklist, selectedTaskIndex, onToggleComplete, onTaskSubmit }) => {
  // State for the "add new task" form is still managed locally.
  const [taskData, setTaskData] = useState({
    title: "", desc: "", priority: "", complete: false,
  });

  const handleInputChange = (event) => {
    const { name, value, type, checked } = event.target;
    setTaskData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onTaskSubmit(taskData); // Call the function passed down from Dashboard
    setTaskData({ title: "", desc: "", priority: "", complete: false }); // Reset form
  };

  let expContent;
  if (item.id === "Timer"){
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
    )
  } else if (item.id === "Calendar") {
    expContent = (
      <div>
        <p>Your tasks for the day</p>
      </div>
    )
  } else if (item.id === "Smart Search") {
    expContent = (
      <div>
        <p>Ask me anything</p>
      </div>
    )
  } else if (item.id === "Checklist") {
    expContent = (
      <div className="checklist-wrapper">
        <div className="task-list-container interactive">
          {tasklist.map((task, index) => (
            <div
              key={task.id}
              className={`task-card ${index === selectedTaskIndex ? 'selected' : ''}`}
              onClick={() => onToggleComplete(task)} // Call parent's handler
            >
              <div className="task-card-title">
                <input type="checkbox" checked={task.complete} readOnly className="task-checkbox" />
                <h4 className={task.complete ? 'completed' : ''}>{task.title}</h4>
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
        <form className="add-task-form" onSubmit={handleSubmit}>
          <input name="title" value={taskData.title} onChange={handleInputChange} placeholder="New Task Title" required />
          <input name="desc" value={taskData.desc} onChange={handleInputChange} placeholder="Description" required />
          <input name="priority" value={taskData.priority} onChange={handleInputChange} placeholder="Priority" required />
          <button type='submit'>Add Task</button>
        </form>
      </div>
    );
  } else {
    expContent = (
      <div></div>
    )
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