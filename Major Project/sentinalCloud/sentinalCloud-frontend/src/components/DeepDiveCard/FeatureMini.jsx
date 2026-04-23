// src/components/DeepDiveCard/FeatureMini.jsx (Refined Version)
import React from 'react';
import PropTypes from 'prop-types';
import './FeatureMini.css'; // Use the refined CSS (without local variables)

// Helper to format numbers nicely
const formatValue = (value) => {
  if (typeof value === 'number') {
    // Format impact values precisely, others normally
    // Use Number.EPSILON to handle floating point comparisons safely
    if (Math.abs(value) < 1 && Math.abs(value) > Number.EPSILON) return value.toFixed(3);
    return value.toLocaleString();
  }
  // Handle potential null/undefined values gracefully
  return value ?? 'N/A';
};


// Helper to calculate bar style based on impact, using GLOBAL theme vars
const getImpactBarStyle = (impact) => {
  const numericImpact = impact ?? 0; // Handle null/undefined impact
  const absImpact = Math.abs(numericImpact);
  // Adjust scaling factor (e.g., 200 = impact of 0.5 fills 100%)
  const widthPercent = Math.min(absImpact * 200, 100);
  // Use GLOBAL CSS variables for colors (defined in App.css)
  const colorVar = numericImpact >= 0 ? 'var(--success-color)' : 'var(--error-color)';

  return {
    width: `${widthPercent}%`,
    backgroundColor: colorVar, // Set color directly using the global variable
  };
};

const FeatureMini = ({ feature }) => {
  // Ensure feature object exists and has impact property
  const impactValue = feature?.impact;
  const impactBarStyle = getImpactBarStyle(impactValue);

  return (
    <div
      className="feature-mini"
      title={`${feature?.name ?? 'Unknown Feature'}: ${formatValue(feature?.value)} (Impact: ${typeof impactValue === 'number' ? impactValue.toFixed(3) : 'N/A'})`}
    >
      <div className="feature-mini__info">
        <span className="feature-mini__name">{feature?.name ?? 'Unknown Feature'}</span>
        <span className="feature-mini__value">{formatValue(feature?.value)}</span>
      </div>
      <div className="feature-mini__impact-viz">
         {/* Container for the bar */}
        <div className="feature-mini__impact-bar-container">
            {/* The actual colored bar */}
            <div className="feature-mini__impact-bar" style={impactBarStyle}></div>
        </div>
        <span className="feature-mini__impact-value">
          {/* Format impact value, handle non-numeric cases */}
          {typeof impactValue === 'number' ? impactValue.toFixed(3) : 'N/A'}
        </span>
      </div>
    </div>
  );
};

// PropTypes remain the same
FeatureMini.propTypes = {
  feature: PropTypes.shape({
    name: PropTypes.string.isRequired,
    value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]), // Allow null/undefined value
    impact: PropTypes.number, // SHAP value (can be null/undefined)
  }).isRequired,
};

export default FeatureMini;