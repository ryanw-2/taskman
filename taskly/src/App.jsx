import './index.css'
import React from 'react'
import Home from './Pages/Home'
import Calendar from './Pages/Calendar'
import SmartSearch from './Pages/SmartSearch'
import Checklist from './Pages/Checklist'
import {HashRouter as Router, Routes, Route} from 'react-router-dom'
import Dashboard from './Pages/Dashboard'


function App() {
  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}

export default App;
