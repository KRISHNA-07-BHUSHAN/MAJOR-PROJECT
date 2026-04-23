// src/App.jsx
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css'; // Your main CSS file with theme variables

// Layout Components
import SideBar from './components/Sidebar/Sidebar.jsx';
import TopBar from './components/TopBar/TopBar.jsx';
import Footer from './components/Footer/Footer.jsx';
import StartupAnimation from "./components/StartupAnimation.jsx";


// Page Components
import Home from './pages/Home.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Security from './pages/Security.jsx';
import Explainability from './pages/Explainability.jsx';
import AttackLibrary from './pages/AttackLibrary.jsx';
import Team from './pages/Team.jsx';
import Settings from './pages/Settings.jsx';

export default function App() {
  const [showStartup, setShowStartup] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true); // Control open/closed state
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'dark' ? 'light' : 'dark'));
  };

  // This function toggles the state
  const toggleSidebar = () => {
    setIsSidebarOpen(prevState => !prevState);
  };

  return (
  <>
    {showStartup ? (
      <StartupAnimation onFinish={() => setShowStartup(false)} />
    ) : (
    <Router>
      <div className="app-container">
        {/* Pass the state AND the toggle function */}
        <SideBar
          isOpen={isSidebarOpen}
          theme={theme}
          toggleTheme={toggleTheme}
          toggleSidebar={toggleSidebar} // Pass the handler
        />

        <div className={`main-section ${isSidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
          <TopBar />
          <main className="main-content-area">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/security" element={<Security />} />
              <Route path="/explainability" element={<Explainability />} />
              <Route path="/attack-library" element={<AttackLibrary />} />
              <Route path="/team" element={<Team />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<Navigate replace to="/" />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </div>
      </Router>
    )}
  </>
);
}
