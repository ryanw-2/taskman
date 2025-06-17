// src/ItemContent.jsx
import React, { useState, useEffect, useRef } from "react";
import api from "../API";
import "./ItemContent.css";
import timer from "../assets/stopwatch_icon.png";
import note from "../assets/notepad_icon.png";
import { motion } from "framer-motion";

// This component just renders the 'insides' of a grid item
const ItemContent = ({ item, tasklist, selectedTaskIndex }) => {
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
    content = (
      <div>
        <p>Hello Calendar</p>
      </div>
    );
  } else if (item.id === "Smart Search") {
    content = (
      <div>
        <p>Hello Smart Search</p>
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
