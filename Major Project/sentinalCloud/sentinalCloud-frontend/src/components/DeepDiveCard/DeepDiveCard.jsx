import React from "react";
import PropTypes from 'prop-types';
import "./DeepDiveCard.css";
// import SHAPWaterfall from "./SHAPWaterfall.jsx"; // <-- THIS LINE IS COMMENTED OUT
import FeatureMini from "./FeatureMini.jsx";

const DeepDiveCard = ({ selectedEvent }) => {

  // Case 1: No event selected
  if (!selectedEvent) {
    return (
      <div className="deep-dive-card deep-dive-empty">
        <p>Select an event from the list to see details.</p>
      </div>
    );
  }

  // Case 2: Event selected, check for explanation data
  const { shap_explanation } = selectedEvent; 

  // Check if explanation exists and is valid
  const hasValidExplanation = shap_explanation && !shap_explanation.error && shap_explanation.features;

  // Case 3: Explanation is missing or has an error
  if (!hasValidExplanation) {
    let message = "No explanation data available for this event.";
    if (selectedEvent.type === 'normal') {
      message = "Explanation is not generated for 'Normal' events.";
    } else if (shap_explanation && shap_explanation.error) {
      message = `Error generating explanation: ${shap_explanation.error}`;
      console.error("SHAP Explanation Error from Backend:", shap_explanation.error);
    }
    return (
        <div className="deep-dive-card deep-dive-empty">
          <h3 className="deep-dive-header">Details: {selectedEvent.event_id}</h3>
          <p className="deep-dive-meta">Type: {selectedEvent.specific_label || selectedEvent.label || 'N/A'} | Time: {selectedEvent.time || 'N/A'} | Prediction: {selectedEvent.label}</p>
          <p>{message}</p>
        </div>
    );
  }

  // Case 4: Explanation is valid, proceed to render
  const { features: shapFeatures } = shap_explanation;
  const confidencePercent = parseFloat(selectedEvent.confidence) || 0;

  return (
    <div className="deep-dive-card">
      <h3 className="deep-dive-header">Deep Dive: {selectedEvent.event_id}</h3>
      <p className="deep-dive-meta">Type: {selectedEvent.specific_label || selectedEvent.label || 'N/A'} | Time: {selectedEvent.time || 'N/A'} | Prediction: {selectedEvent.label}</p>

      {/* Confidence Gauge */}
      <div className="confidence-gauge">
        <div
          className="gauge-circle"
          style={{ '--confidence-percent': `${confidencePercent}%` }}
          title={`Model Confidence: ${confidencePercent.toFixed(1)}%`}
        >
          {confidencePercent.toFixed(0)}%
        </div>
        <span className="gauge-label">{selectedEvent.label} Confidence</span>
      </div>

      {/* SHAP Waterfall Component -- THIS IS COMMENTED OUT TO PREVENT CRASH */}
      {/* <SHAPWaterfall shapData={shap_explanation} /> */}

      {/* List of key features (THIS WILL STILL WORK) */}
      <div className="features-list">
        <h4 className="features-header">Key Contributing Features:</h4>
        {shapFeatures && shapFeatures.length > 0 ? (
          shapFeatures.map((feature) => (
            <FeatureMini key={feature.name} feature={feature} />
          ))
        ) : (
          <p>No specific feature data available in explanation.</p>
        )}
      </div>
    </div>
  );
};

// PropTypes (unchanged)
DeepDiveCard.propTypes = {
  selectedEvent: PropTypes.shape({
    event_id: PropTypes.string.isRequired,
    label: PropTypes.string,
    specific_label: PropTypes.string,
    time: PropTypes.string,
    confidence: PropTypes.string,
    type: PropTypes.string,
    shap_explanation: PropTypes.object,
  }),
};

DeepDiveCard.defaultProps = {
  selectedEvent: null,
};

export default DeepDiveCard;