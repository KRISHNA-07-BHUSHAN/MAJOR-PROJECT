// src/components/AlertsPanel/AlertsPanel.jsx (Refined - Reads specific_label)
import React from 'react';
// import PropTypes from 'prop-types'; // Removing for now to fix blank page
import './AlertsPanel.css'; // Make sure this CSS file exists
// Uses styles from PageStyles.css for badges/lists

// --- Helper function to determine severity from confidence ---
const getSeverityFromConfidence = (confidenceStr) => {
  const confidence = parseFloat(confidenceStr);
  if (confidence >= 90) {
    return { label: 'High', className: 'severity-high' };
  }
  if (confidence >= 70) {
    return { label: 'Medium', className: 'severity-medium' };
  }
  return { label: 'Low', className: 'severity-low' };
};

// --- UPDATED: Component now receives 'alerts' prop ---
// --- We set a default value 'alerts = []' to prevent any crash ---
const AlertsPanel = ({ alerts = [] }) => {
  console.log("[AlertsPanel] Received alerts prop:", alerts); // <-- ADD THIS DEBUG LOG

  return (
    // Use card style from PageStyles.css or define locally
    <div className="alerts-panel-container card">
      <h2 className="card-title">Recent Alerts</h2>

      {/* --- UPDATED: Check for alerts && alerts.length --- */}
      <ul className="activity-list">
        {alerts && alerts.length > 0 ? (
          alerts.map(alert => {
            // --- ADD DEBUG LOG INSIDE MAP ---
            console.log("[AlertsPanel] Rendering alert:", alert);
            // --- END DEBUG LOG ---

            // Get severity object based on confidence
            const severity = getSeverityFromConfidence(alert.confidence);

            return (
              <li key={alert.event_id} className="activity-list-item">
                <div className="activity-item-main">

                  {/* It reads the specific label ("DDoS", "password", etc.) */}
                  <span className="activity-item-title">{alert.specific_label}</span>

                  {/* 2. Timestamp and Confidence */}
                  <span className="activity-item-time">
                    {alert.time}
                    {/* 3. Confidence % (as requested) */}
                    <span className="activity-item-confidence">{alert.confidence}%</span>
                  </span>

                </div>

                {/* 4. Severity Badge */}
                <span className={`severity-badge ${severity.className}`}>
                  {severity.label}
                </span>
              </li>
            );
          })
        ) : (
          // This message will now show when the simulation hasn't started
          <p className="no-alerts">No recent alerts.</p>
        )}
      </ul>
    </div>
  );
};

// --- Removed propTypes and defaultProps to ensure stability ---

export default AlertsPanel;