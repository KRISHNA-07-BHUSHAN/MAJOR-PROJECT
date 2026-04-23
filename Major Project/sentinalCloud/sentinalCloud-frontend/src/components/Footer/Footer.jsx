import React from 'react';
import './Footer.css'; // Ensure this CSS file exists

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <p>&copy; {currentYear} SentinelCloud. All rights reserved.</p>
    </footer>
  );
};

export default Footer;