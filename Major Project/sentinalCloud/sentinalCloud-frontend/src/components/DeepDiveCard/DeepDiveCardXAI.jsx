import React from "react";
import PropTypes from "prop-types";
import "./DeepDiveCard.css"; // reuse same CSS styles
import FeatureMini from "./FeatureMini.jsx";

const DeepDiveCardXAI = ({ selectedEvent }) => {

  if (!selectedEvent) {
    return (
      <div className="deep-dive-card deep-dive-empty">
        <p>Select an event from the list to see details.</p>
      </div>
    );
  }

  const { shap_explanation } = selectedEvent;
  const hasValidExplanation =
    shap_explanation &&
    !shap_explanation.error &&
    shap_explanation.features;

  if (!hasValidExplanation) {
    return (
      <div className="deep-dive-card deep-dive-empty">
        <h3 className="deep-dive-header">Details: {selectedEvent.event_id}</h3>
        <p className="deep-dive-meta">
          Type: {selectedEvent.specific_label || selectedEvent.label} |
          Time: {selectedEvent.time}
        </p>
        <p>No explanation data available for this event.</p>
      </div>
    );
  }

  // Meaning + Prevention
  const meaning = shap_explanation.meaning || "No description available.";
  const prevention = shap_explanation.prevention || ["No prevention steps available."];

  return (
    <div className="deep-dive-card">

      <h3 className="deep-dive-header">Deep Dive: {selectedEvent.event_id}</h3>
      <p className="deep-dive-meta">
        Type: {selectedEvent.specific_label || selectedEvent.label} |
        Time: {selectedEvent.time}
      </p>

      {/* --- Attack Summary Box --- */}
      <div className="attack-summary-box">
        <h4>Attack Summary</h4>
        <p className="attack-meaning">{meaning}</p>

        <h4 style={{ marginTop: "10px" }}>Prevention</h4>
        <ul className="prevention-list">
          {prevention.map((step, idx) => (
            <li key={idx}>{step}</li>
          ))}
        </ul>
      </div>

      {/* --- SHAP Feature List --- */}
      <div className="features-list">
        <h4 className="features-header">Key Contributing Features:</h4>
        {shap_explanation.features.map((f) => (
          <FeatureMini key={f.name} feature={f} />
        ))}
      </div>

    </div>
  );
};

DeepDiveCardXAI.propTypes = {
  selectedEvent: PropTypes.object,
};

export default DeepDiveCardXAI;
