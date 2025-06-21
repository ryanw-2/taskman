import React, { useState, useEffect, useRef, act } from "react";
import "./Dashboard.css";
import api from "../API";
import ExpandedItemView from "./ExpandedItemView";
import { motion, AnimatePresence } from "framer-motion";
import ItemContent from "./ItemContent";

const MONTH_LIST = [
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

const Dashboard = () => {
  // GESTURE CONTROL STATE
  const [gesture, setGesture] = useState("none");
  const [activeIndex, setActiveIndex] = useState(0);
  const [expandedIndex, setExpandedIndex] = useState(null);

  // --- CHECKLIST-SPECIFIC STATE IS NOW IN THE DASHBOARD ---
  const [taskList, setTasklist] = useState([]);
  const [selectedTaskIndex, setSelectedTaskIndex] = useState(0);
  
  // --- CALENDAR STATE
  const [eventList, setEventList] = useState([]);

  // --- GRID ITEM LIST
  const itemRefList = useRef([]);
  itemRefList.current = Array(5)
    .fill()
    .map((_, i) => itemRefList.current[i] || React.createRef());

  // --- SMART SEARCH STATE ---
  const [isRecording, setIsRecording] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [interimTranscript, setInterimTranscript] = useState("");

  const smartSearchSocket = useRef(null);
  const mediaRecorder = useRef(null);
  const audioStream = useRef(null);

  // --- Time and Date Logic (can be simplified) ---
  const currentTime = new Date();
  const hours = currentTime.getHours();
  const period = hours >= 12 ? "PM" : "AM";
  const displayHours = hours % 12 || 12; // Handle midnight (0) as 12
  const minutes = String(currentTime.getMinutes()).padStart(2, "0");
  const month = MONTH_LIST[currentTime.getMonth()];
  const day = currentTime.getDate();
  const year = currentTime.getFullYear();

  // --- API & DATA HANDLING LIVES IN THE PARENT ---
  // CHECKLIST -------------------------------------
  const fetchTasklist = async () => {
    try {
      const response = await api.get("/checklist/");
      setTasklist(response.data);
    } catch (error) {
      console.error("Failed to fetch tasklist:", error);
    }
  };

  const handleToggleComplete = async (taskToUpdate) => {
    const newStatus = !taskToUpdate.complete;
    try {
      setTasklist((prev) =>
        prev.map((t) =>
          t.id === taskToUpdate.id ? { ...t, complete: newStatus } : t
        )
      );
      await api.patch(`/checklist/${taskToUpdate.id}`, { complete: newStatus });
    } catch (error) {
      console.error("Failed to update task:", error);
      setTasklist((prev) =>
        prev.map((t) =>
          t.id === taskToUpdate.id ? { ...t, complete: !newStatus } : t
        )
      );
    }
  };

  const handleTaskSubmit = async (newTaskData) => {
    await api.post("/checklist/", newTaskData);
    fetchTasklist(); // Re-fetch to get the new list with the new ID
  };

  // CALENDAR -------------------------------------
  const fetchEventList = async () => {
    try {
      const response = await api.get("/calendar/today/");
      setEventList(response.data);
    } catch (error) {
      console.error("Fail to fetch EventList: ", error);
    }
  }

  const handleEventSubmit = async (newEventData) => {
    await api.post("/calendar/", newEventData);
    fetchEventList();
  }

  // SMART SEARCH ---------------------------------
  const startRecording = async () => {
    if (isRecording) return;
    setInterimTranscript("");
    setIsThinking(false);

    try {
      audioStream.current = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });
      smartSearchSocket.current = new WebSocket("ws://localhost:8000/ws/smart-search");

      smartSearchSocket.current.onopen = () => {
        console.log("Smart Search WebSocket established.");
        setIsRecording(true);
        mediaRecorder.current = new MediaRecorder(audioStream.current, {
          mimeType: "audio/webm;codecs=opus",
        });

        mediaRecorder.current.ondataavailable = (event) => {
          if (
            event.data.size > 0 &&
            smartSearchSocket.current.readyState === WebSocket.OPEN
          ) {
            smartSearchSocket.current.send(event.data);
          }
        };

        mediaRecorder.current.onstop = () => {
          if (smartSearchSocket.current.readyState === WebSocket.OPEN) {
            smartSearchSocket.current.close();
          }
        };

        mediaRecorder.current.start(250);
      };

      smartSearchSocket.current.onmessage = (event) => {
        const message = event.data;
        // --- REAL-TIME TRANSCRIPT HANDLING ---

        if (message.startsWith("[INTERIM]")) {
            setInterimTranscript(message.replace("[INTERIM]", "").trim());
        } else if (message.startsWith("[USER]")) {
          const userText = message.replace("[USER]", "").trim();
          setInterimTranscript(""); // Clear interim text
          setChatHistory(prev => [...prev, { sender: 'user', text: userText }]);
        } else if (message === "[THINKING]") {
          setIsThinking(true);
          setChatHistory(prev => [...prev, { sender: 'ai', text: '' }]);
        } else if (message === "[END_OF_RESPONSE]") {
          setIsThinking(false);
        } else {
          setIsThinking(false); // Stop thinking once first text chunk arrives
          setChatHistory(prev => {
            const newHistory = [...prev];
            if (newHistory.length > 0 && newHistory[newHistory.length - 1].sender === 'ai') {
              newHistory[newHistory.length - 1].text += message;
            }
            return newHistory;
          });
        }
      };

      smartSearchSocket.current.onclose = () => {
        console.log("Smart Search Websocket closed.");
        stopRecordingCleanup();
      };
    } catch (err) {
      console.error("Error starting recording:", err);
      stopRecordingCleanup();
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state === "recording") {
      mediaRecorder.current.stop();
    }
  };

  const stopRecordingCleanup = () => {
    if (audioStream.current) {
      audioStream.current.getTracks().forEach((track) => track.stop());
    }
    setIsRecording(false);
    setIsThinking(false);
  };

  // Fetch Data Lists
  useEffect(() => {
    fetchTasklist();
    fetchEventList();
  }, []);

  // Establish Hand Gesture Detector WS
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

  // Work Gesture Control
  useEffect(() => {
    if (gesture === "none") {
      return;
    }
    // We are in Dashboard View
    if (expandedIndex == null) {
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
    }
    // We are in Expanded View
    else {
      // --- Gestures for CHECKLIST Expanded View ---
      if (gridItems[expandedIndex].id === "Checklist") {
        if (gesture === "downswipe") {
          setSelectedTaskIndex((prev) =>
            prev < taskList.length - 1 ? prev + 1 : 0
          );
        } else if (gesture === "upswipe") {
          setSelectedTaskIndex((prev) =>
            prev > 0 ? prev - 1 : taskList.length - 1
          );
        } else if (gesture === "click") {
          if (taskList[selectedTaskIndex]) {
            handleToggleComplete(taskList[selectedTaskIndex]);
          }
        }
      // --- Gestures for SMART SEARCH Expanded View ---
      } else if (gridItems[expandedIndex].id === "Smart Search") {
        if (gesture === "click") {
          isRecording ? stopRecording() : startRecording();
        }
      // --- Gestures for CALENDAR Expanded View
      } else if (gridItems[expandedIndex].id === "Calendar") {
        if (gesture === "downswipe") {
          setSelectedTaskIndex((prev) =>
            prev < eventList.length - 1 ? prev + 1 : 0
          );
        } else if (gesture === "upswipe") {
          setSelectedTaskIndex((prev) =>
            prev > 0 ? prev - 1 : eventList.length - 1
          );
        } else if (gesture === "click") {
          if (eventList[selectedTaskIndex]) {
            handleToggleComplete(eventList[selectedTaskIndex]);
          }
        }        
      }

      if (gesture === "fist") handleCloseExpanded();
    }

    setGesture("none");
  }, [gesture, isRecording]);

  const handleItemClick = (index) => {
    alert(`Button ${index} was clicked!`, "");
    setActiveIndex(index);
    setExpandedIndex(index);
  };

  const handleCloseExpanded = () => {
    setExpandedIndex(null);
  };

  // DATA
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
            onClick={() => handleItemClick(index)}
            className={`grid-dyn-item ${item.className} ${
              activeIndex === index && expandedIndex === null ? "active" : ""
            }`}
            style={{
              visibility: expandedIndex === index ? "visible" : "visible",
            }}
          >
            <ItemContent
              item={item}
              tasklist={taskList}
              eventlist={eventList}
              selectedTaskIndex={selectedTaskIndex}
              chatHistory={chatHistory}
            />
          </motion.div>
        ))}
      </div>

      <AnimatePresence>
        {expandedIndex !== null && (
          <ExpandedItemView
            item={gridItems[expandedIndex]}
            onClose={handleCloseExpanded}
            tasklist={taskList}
            eventlist={eventList}
            onEventSubmit={handleEventSubmit}
            selectedTaskIndex={selectedTaskIndex}
            onToggleComplete={handleToggleComplete}
            onTaskSubmit={handleTaskSubmit}
            // Smart Search Props
            isRecording={isRecording}
            isThinking={isThinking}
            chatHistory={chatHistory}
            interimTranscript={interimTranscript}
            onStartRecord={startRecording}
            onStopRecord={stopRecording}
          />
        )}
      </AnimatePresence>

      {/* Bottom Information -------------------------------------*/}
      <div className="bottom-info">
        <p>
          Active Module:{" "}
          <span className="font-bold">{gridItems[activeIndex].id}</span>
        </p>
      </div>
      <div className="next-actions">
        {activeIndex > 0 ? (
          <p className="next-actions">
            Swipe Left: {gridItems[activeIndex - 1].id}
          </p>
        ) : (
          <p className="next-actions">
            Swipe Left: {gridItems[gridItems.length - 1].id}
          </p>
        )}
        {activeIndex < 4 ? (
          <p className="next-actions">
            Swipe Right: {gridItems[activeIndex + 1].id}
          </p>
        ) : (
          <p className="next-actions">Swipe Left: {gridItems[0].id}</p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
