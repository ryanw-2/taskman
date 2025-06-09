import React, { useState, useEffect, useRef } from 'react';

const Dashboard = () => {
  const [gesture, setGesture] = useState('none');
  const buttonRef = useRef(null);

  useEffect(() => {
    // Key component used by front end to connect
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onopen = () => {
      console.log('WebSocket connection established');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setGesture(data.gesture);
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
    if (gesture == 'click') {
      if (buttonRef.current) {
        buttonRef.current.click();
      }
    }
  }, [gesture]);

  const handleButtonClick = () => {
    
  };

  return (
    <div className='flex flex-col items-center justify-center h-screen bg-gray-900 text-white'>
      <h1 className='text-4xl mb-8'>Gesture Controlled Dashboard</h1>
      <p className='text-xl mb-4'>
        Current Gesture:{' '}
        <span className='font-bold text-yellow-400'>{gesture}</span>
      </p>
      <button
        ref={buttonRef}
        onClick={handleButtonClick}
        className='px-8 py-4 bg-blue-600 text-white font-bold rounded-lg shadow-lg hover:bg-blue-700 transition-colors'
      >
        Click Me with a Pinch!
      </button>
    </div>
  );
};

export default Dashboard;
