import React from "react";
import PropTypes from 'prop-types';
import "./AttackSummary.css";

const AttackSummary = ({ stats }) => {
  return (
    <div className="attack-summary">
      <h3 className="attack-summary-header">Attack Summary</h3>
      
      <div className="summary-item">
        <span className="summary-label">Total Packets:</span>
        <span className="summary-value">{stats.total}</span>
      </div>
      
      <div className="summary-item">
        <span className="summary-label">Attacks Detected:</span>
        <span className="summary-value attack">{stats.attacks}</span>
      </div>
      
      <div className="summary-item">
        <span className="summary-label">Normal Packets:</span>
        <span className="summary-value normal">{stats.normals}</span>
      </div>
      
      <div className="summary-item">
        <span className="summary-label">Avg Confidence:</span>
        <span className="summary-value">{stats.avgConfidence.toFixed(2)}%</span>
      </div>
    </div>
  );
};

// Define prop types for validation and documentation
AttackSummary.propTypes = {
  stats: PropTypes.shape({
    total: PropTypes.number,
    attacks: PropTypes.number,
    normals: PropTypes.number,
    avgConfidence: PropTypes.number,
  }).isRequired,
};

// Provide default props to prevent errors if stats are undefined
AttackSummary.defaultProps = {
  stats: {
    total: 0,
    attacks: 0,
    normals: 0,
    avgConfidence: 0.0,
  }
};

export default AttackSummary;