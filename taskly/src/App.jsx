import './index.css'
import Home from './Pages/Home'
import Calendar from './Pages/Calendar'
import SmartSearch from './Pages/SmartSearch'
import Checklist from './Pages/Checklist'
import {HashRouter as Router, Routes, Route} from 'react-router-dom'


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home/>}/>
        <Route path="/calendar" element={<Calendar/>}/>
        <Route path="/smartsearch" element={<SmartSearch/>}/>
        <Route path="/checklist" element={<Checklist/>}/>
      </Routes>
    </Router>
  )
}

export default App
