import React, { useState, useEffect, useRef, act } from "react";
import "./Dashboard.css";
import ExpandedItemView from "./ExpandedItemView";
import { motion, AnimatePresence } from 'framer-motion';
import ItemContent from "./ItemContent";

const MONTH_LIST = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

const Dashboard = () => {
  const [gesture, setGesture] = useState("none");
  const [activeIndex, setActiveIndex] = useState(0);
  const [expandedIndex, setExpandedIndex] = useState(null);

  const itemRefList = useRef([]);
  itemRefList.current = Array(5).fill().map((_, i) => itemRefList.current[i] || React.createRef());

  // --- Time and Date Logic (can be simplified) ---
  const currentTime = new Date();
  const hours = currentTime.getHours();
  const period = hours >= 12 ? "PM" : "AM";
  const displayHours = hours % 12 || 12; // Handle midnight (0) as 12
  const minutes = String(currentTime.getMinutes()).padStart(2, "0");
  const month = MONTH_LIST[currentTime.getMonth()];
  const day = currentTime.getDate();
  const year = currentTime.getFullYear();

  useEffect(() => {
    // Key component used by front end to connect
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => {
      console.log("WebSocket connection established");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setGesture(data.gesture);
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
      const currentItemRef = itemRefList.current[activeIndex];
      if (currentItemRef && currentItemRef.current) {
        currentItemRef.current.click();
      }
    } else if (gesture === "rightswipe") {
      setActiveIndex((prevIndex) =>
        prevIndex < itemRefList.current.length - 1 ? prevIndex + 1 : 0
      );
    } else if (gesture === "leftswipe") {
      setActiveIndex((prevIndex) =>
        prevIndex > 0 ? prevIndex - 1 : itemRefList.current.length - 1
      );
    }
    
    setGesture("none");
  }, [gesture, activeIndex]);

  const handleItemClick = (index) => {
    alert(`Button ${index} was clicked!`, "");
    setActiveIndex(index)
    setExpandedIndex(index)
  };

  const handleCloseExpanded = () => {
    setExpandedIndex(null);
  };

  const gridItems = [
    { id: "Calendar", title: `${month} ${day}, ${year}`, className: "calendar" },
    { id: "Smart Search", title: "Taskly Ask", className: "smart-search" },
    { id: "Checklist", title: "Checklist", className: "checklist" },
    { id: "Timer", content: null, className: "secondary-widget1" },
    { id: "Notepad", content: null, className: "secondary-widget2" },
  ];
  
  return (
    //Creates full screen container
    <div className="dashboard-container">

      <div className="grid-container">
        {/* Static Items ---------------------------------------- */}
        {/* Top Name/Greeting */}
        <div className="grid-item name-greeting">
          <h3>Welcome, Ryan</h3>
        </div>

        {/* Top Stat 1 */}
        <div className="grid-item stat-1">
          <h3>
            <span>
              {displayHours}:{minutes} {period}
            </span>
          </h3>
        </div>

        {/* Top Stat 2 */}
        <div className="grid-item stat-2"></div>

        {/* Dynamic Items ---------------------------------------- */}

        {gridItems.map((item, index) => (
            <motion.div
              key={item.id}
              id={item.id}
              ref={itemRefList.current[index]}
              onClick={ () => handleItemClick(index)}
              className={`grid-dyn-item ${item.className} ${activeIndex === index ? 'active' : ''}`}
              style={{ visibility: expandedIndex === index ? 'hidden' : 'visible' }}
            >
              <ItemContent item={item} layoutId={`shared-content-${item.id}`}/>
            </motion.div>
          ))
        } 
      </div>
      
      <AnimatePresence>
        {expandedIndex !== null && (
          // We pass the unique layoutId to our component as a prop
          <ExpandedItemView
            layoutId={`shared-content-${gridItems[expandedIndex].id}`}
            item={gridItems[expandedIndex]}
            onClose={handleCloseExpanded}
          />
        )}
      </AnimatePresence>

      {/* Bottom Information -------------------------------------*/}
      <div className="bottom-info">
        <p>
        Active Module: <span className="font-bold">{gridItems[activeIndex].id}</span>
        </p>
      </div>
      <div className="next-actions">
        {activeIndex > 0 ? <p className="next-actions">Swipe Left: {gridItems[activeIndex - 1].id}</p> : <p className="next-actions">Swipe Left: {gridItems[gridItems.length - 1].id}</p>}
        {activeIndex < 4 ? <p className="next-actions">Swipe Right: {gridItems[activeIndex + 1].id}</p> : <p className="next-actions">Swipe Left: {gridItems[0].id}</p>}
      </div>
    </div>
    
  );
};

export default Dashboard;
