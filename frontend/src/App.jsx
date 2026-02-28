import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Scenarios from './pages/Scenarios'
import Chat from './pages/Chat'
import Summary from './pages/Summary'
import Stats from './pages/Stats'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<Scenarios />} />
          <Route path="/chat/:sessionId" element={<Chat />} />
          <Route path="/summary/:sessionId" element={<Summary />} />
          <Route path="/stats" element={<Stats />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
