import './index.css'
import React, {useState, useEffect} from 'react'
import api from './API'
import Dashboard from './Pages/Dashboard'


const App = () => { 
  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}

export default App;
