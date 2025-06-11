import React, { useState, useEffect, useRef } from 'react';

const Dashboard = () => {
  const [gesture, setGesture] = useState('none');
  const [buttonIndex, setButtonIndex] = useState(0);

  const buttonRefList = useRef([]);
  buttonRefList.current = [useRef(null), useRef(null)];

  useEffect(() => {
    // Key component used by front end to connect
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onopen = () => {
      console.log('WebSocket connection established');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setGesture(prevGesture => {
        if (data.gesture === 'none') {
          return 'none';
        }
        return data.gesture;
      })
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    if (gesture === 'none') {
      return;
    }

    if (gesture === 'click') {
      const currentButtonRef = buttonRefList.current[buttonIndex];
      if (currentButtonRef && currentButtonRef.current) {
        currentButtonRef.current.click();
      }
    }
    else if (gesture === 'rightswipe') {
      setButtonIndex(prevIndex => (prevIndex < buttonRefList.current.length - 1 ? prevIndex + 1 : prevIndex));
    }
    else if (gesture === 'leftswipe') {
      setButtonIndex(prevIndex => (prevIndex > 0 ? prevIndex - 1 : prevIndex));
    }
  }, [gesture]);

  const handleButtonClick = () => {
    alert(`Button ${index + 1} was clicked!`);
  };

  return (
    <div className='flex flex-col items-center justify-center h-screen bg-gray-900 text-white'>
      <h1 className='text-4xl mb-8'>Gesture Controlled Dashboard</h1>
      <p className='text-xl mb-4'>
        Current Gesture:{' '}
        <span className='font-bold text-yellow-400'>{gesture}</span>
      </p>
      <p className='text-lg mb-4'>
        Selected Button: {buttonIndex + 1}
      </p>
      <div className='flex space-x-4'>
        <button
          ref={buttonRefList.current[0]}
          onClick={() => handleButtonClick(0)}
          className={`px-8 py-4 font-bold rounded-lg shadow-lg transition-all ${buttonIndex === 0 ? 'bg-blue-600 ring-4 ring-yellow-400' : 'bg-gray-700'}`}
        >
          Button 1
        </button>
        <button
          ref={buttonRefList.current[1]}
          onClick={() => handleButtonClick(1)}
          className={`px-8 py-4 font-bold rounded-lg shadow-lg transition-all ${buttonIndex === 1 ? 'bg-red-600 ring-4 ring-yellow-400' : 'bg-gray-700'}`}
        >
          Button 2
        </button>
      </div>
    </div>
  );
};

export default Dashboard;
