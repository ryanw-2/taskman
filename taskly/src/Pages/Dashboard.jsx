import React, { useState, useEffect, useRef } from "react";
import "./Dashboard.css";

const Dashboard = () => {
  const [gesture, setGesture] = useState("none");
  const [buttonIndex, setButtonIndex] = useState(0);

  let currentTime = new Date();
  let hours = currentTime.getHours() % 12;
  let minutes = String(currentTime.getMinutes()).padStart(2, '0')
  let period = "AM";

  const monthList = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  let month = monthList[currentTime.getMonth()];
  let day = currentTime.getDate();
  let year = currentTime.getFullYear();

  if (hours >= 12) {
    period = "PM";
  }

  const buttonRefList = useRef([]);
  buttonRefList.current = [useRef(null), useRef(null)];

  useEffect(() => {
    // Key component used by front end to connect
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => {
      console.log("WebSocket connection established");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setGesture((prevGesture) => {
        if (data.gesture === "none") {
          return "none";
        }
        return data.gesture;
      });
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed");
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    return () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    if (gesture === "none") {
      return;
    }

    if (gesture === "click") {
      const currentButtonRef = buttonRefList.current[buttonIndex];
      if (currentButtonRef && currentButtonRef.current) {
        currentButtonRef.current.click();
      }
    } else if (gesture === "rightswipe") {
      setButtonIndex((prevIndex) =>
        prevIndex < buttonRefList.current.length - 1 ? prevIndex + 1 : prevIndex
      );
    } else if (gesture === "leftswipe") {
      setButtonIndex((prevIndex) =>
        prevIndex > 0 ? prevIndex - 1 : prevIndex
      );
    }
  }, [gesture]);

  const handleButtonClick = () => {
    alert(`Button ${index + 1} was clicked!`, "");
  };

  return (
    //Creates full screen container
    <div className="dashboard-container">
      <div className="grid-container">
        {/* Top Name/Greeting */}
        <div className="grid-item name-greeting">
          <h3>Welcome, Ryan</h3>
        </div>

        {/* Top Stat 1 */}
        <div className="grid-item stat-1">
          <h3>
            <span>
              {hours}:{minutes} {period}
            </span>
          </h3>
        </div>

        {/* Top Stat 2 */}
        <div className="grid-item stat-2"></div>

        {/* Calendar */}
        <div className="grid-item calendar">
          <h3>
            <span>{month} {day}, {year}</span>
          </h3>
        </div>

        {/* Smart Search */}
        <div className="grid-item smart-search">
          <h3>Taskly Ask</h3>
        </div>

        {/* Check List */}
        <div className="grid-item checklist">
          <h3>Checklist</h3>
        </div>

        {/* Secondary Widgets */}
        <div className="grid-item secondary-widgets"></div>

        {/* Bottom Information */}
        <div className="grid-item bottom-info">
          <p>
            Current Gesture: <span className="font-bold">{gesture}</span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
