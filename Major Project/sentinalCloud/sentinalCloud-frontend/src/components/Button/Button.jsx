import React from 'react';
import PropTypes from 'prop-types';
import './Button.css';

const Button = ({ children, onClick, type = 'primary', disabled = false, ...rest }) => {
  return (
    <button
      className={`custom-btn ${type}`}
      onClick={onClick}
      disabled={disabled}
      {...rest} // Pass down any other props like 'type="submit"', 'aria-label', etc.
    >
      {children}
    </button>
  );
};

// Define prop types for the component
Button.propTypes = {
  children: PropTypes.node.isRequired,
  onClick: PropTypes.func,
  type: PropTypes.oneOf(['primary', 'secondary']),
  disabled: PropTypes.bool,
};

export default Button;