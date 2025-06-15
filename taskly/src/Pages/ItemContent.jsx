// src/ItemContent.jsx
import React, { useState, useEffect } from "react";
import api from "../API";
import "./ItemContent.css";
import timer from "../assets/stopwatch_icon.png";
import note from "../assets/notepad_icon.png";
import { motion } from "framer-motion";

// This component just renders the 'insides' of a grid item
const ItemContent = ({ item }) => {
  const [tasklist, setTasklist] = useState([]);
  const [taskData, setTaskData] = useState({
    title: "",
    desc: "",
    priority: "",
    complete: false,
  });

  const fetchTasklist = async () => {
    const response = await api.get("/checklist/");
    setTasklist(response.data);
  };

  useEffect(() => {
    fetchTasklist();
  }, []);

  const handleInputChange = (event) => {
    const val =
      event.target.type === "checkbox"
        ? event.target.checked
        : event.target.value;
    setTaskData({
      ...taskData,
      [event.target.name]: val,
    });
  };

  const handleTaskSubmit = async (event) => {
    event.preventDefault();
    await api.post("/checklist/", taskData);
    fetchTasklist();
    setTaskData({
      title: "",
      desc: "",
      priority: "",
      complete: false,
    });
  };

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
      <div>
        <form onSubmit={handleTaskSubmit}>
          <div>
            <label htmlFor="title" className="form-label">
              Title
            </label>
            <input
              type="text"
              className="form-control"
              id="title"
              name="title"
              onChange={handleInputChange}
              value={taskData.title}
            />
          </div>
          
          <div>
            <label htmlFor="desc" className="form-label">
              Description
            </label>
            <input
              type="text"
              className="form-control"
              id="desc"
              name="desc"
              onChange={handleInputChange}
              value={taskData.desc}
            />
          </div>

          <div>
            <label htmlFor="priority" className="form-label">
              Priority
            </label>
            <input
              type="text"
              className="form-control"
              id="priority"
              name="priority"
              onChange={handleInputChange}
              value={taskData.priority}
            />
          </div>

          <div>
            <label htmlFor="complete" className="form-label">
              Complete?
            </label>
            <input
              type="checkbox"
              id="complete"
              name="complete"
              onChange={handleInputChange}
              value={taskData.complete}
            />
          </div>
          
          <button type='submit'>
            Submit
          </button>
          
        </form>

        <table className="table-auto">
        <thead>
            <tr>Title</tr>
            <tr>Description</tr>
            <tr>Priority</tr>
            <tr>Complete</tr>
        </thead>
        <tbody>
            {tasklist.map((task) => (
                <tr key={task.id}>
                    <td>{task.title}</td>
                    <td>{task.desc}</td>
                    <td>{task.priority}</td>
                    <td>{task.complete ? 'Yes' : 'No'}</td>
                </tr>
            ))}
        </tbody>
        </table>
      </div>
    );
  } else {
    // You can add more complex content for other items here
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
