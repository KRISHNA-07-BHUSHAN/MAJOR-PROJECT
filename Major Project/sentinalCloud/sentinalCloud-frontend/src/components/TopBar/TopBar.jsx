import React, { useState } from 'react';
import './TopBar.css';
import { Search, Bell, UserCircle } from 'lucide-react';

const TopBar = () => {
  const [message, setMessage] = useState("");

  const showMessage = () => {
    setMessage("This feature will be updated soon.");
    setTimeout(() => setMessage(""), 2000); // auto hide after 2s
  };

  return (
    <header className="top-bar">
      {/* Left side of TopBar - Search Input */}
      <div className="top-bar-search">
        <Search size={20} className="search-icon" />
        <input type="text" placeholder="Search attacks, IPs, or events..." />
      </div>

      {/* Right side of TopBar */}
      <div className="top-bar-actions">
        <button
          className="top-bar-icon-btn"
          aria-label="Notifications"
          onClick={showMessage}
        >
          <Bell size={22} />
        </button>

        <button
          className="top-bar-icon-btn"
          aria-label="User profile"
          onClick={showMessage}
        >
          <UserCircle size={24} />
        </button>

        {/* Inline In-App Message */}
        {message && <div className="top-bar-message">{message}</div>}
      </div>
    </header>
  );
};

export default TopBar;
