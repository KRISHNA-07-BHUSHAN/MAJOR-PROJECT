// src/components/SideBar/SideBar.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { NavLink } from 'react-router-dom';
import './Sidebar.css'; // Ensure this CSS exists and matches Gemini style
import {
  ShieldCheck, LayoutDashboard, Sparkles, Library, Users, Settings, Menu, Moon, Sun
} from 'lucide-react'; // Make sure lucide-react is installed

const navItems = [
  { name: "Dashboard", path: "/", icon: LayoutDashboard },
  { name: "Security", path: "/security", icon: ShieldCheck },
  { name: "Explainability", path: "/explainability", icon: Sparkles },
  { name: "Attack Library", path: "/attack-library", icon: Library },
  { name: "Team", path: "/team", icon: Users },
];

const SideBar = ({ isOpen, theme, toggleTheme, toggleSidebar }) => { // Receive toggleSidebar prop
  return (
    <aside className="sidebar" data-is-open={isOpen}>
      <div className="sidebar-top">
        <div className="sidebar-header">
          <span className="sidebar-logo-text" data-is-open={isOpen}>
            SentinelCloud
          </span>
          {/* Ensure this button calls the toggleSidebar function passed from App.jsx */}
          <button className="sidebar-toggle-btn" onClick={toggleSidebar}>
            <Menu size={24} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink key={item.name} to={item.path} className="nav-link" end={item.path === '/'}>
              <item.icon size={20} />
              <span className="nav-link-text" data-is-open={isOpen}>
                {item.name}
              </span>
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="sidebar-bottom">
        <NavLink to="/settings" className="nav-link">
          <Settings size={20} />
          <span className="nav-link-text" data-is-open={isOpen}>
            Settings
          </span>
        </NavLink>
        <button className="nav-link theme-toggle" onClick={toggleTheme}>
          {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
          <span className="nav-link-text" data-is-open={isOpen}>
            {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
          </span>
        </button>
      </div>
    </aside>
  );
};

SideBar.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  theme: PropTypes.string.isRequired,
  toggleTheme: PropTypes.func.isRequired,
  toggleSidebar: PropTypes.func.isRequired, // Ensure prop type is defined
};

export default SideBar;