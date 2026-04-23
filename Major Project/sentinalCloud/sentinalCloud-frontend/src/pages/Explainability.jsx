import React, { useState, useEffect } from 'react';
import DeepDiveCardXAI from '../components/DeepDiveCard/DeepDiveCardXAI.jsx';
import './PageStyles.css';

export default function Explainability() {

  const [eventList, setEventList] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const fetchEvents = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/detect/explain/events");
      const data = await response.json();
      setEventList(data.events || []);
    } catch (err) {
      console.error("Failed to load explainability events:", err);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleSelectEvent = async (evt) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/detect/explain/event?event_id=${evt.event_id}`
      );
      const data = await response.json();

      setSelectedEvent({
        event_id: evt.event_id,
        label: data.explanation.grouped_label,
        specific_label: data.explanation.raw_label,
        time: data.explanation.timestamp,
        shap_explanation: {
          features: data.explanation.features || [],
          shap_values: data.explanation.shap_values || {},
          shap_image: data.explanation.shap_image || null,
          meaning: data.explanation.meaning,
          prevention: data.explanation.prevention
        }
      });
    } catch (err) {
      console.error("Failed to load explanation:", err);
    }
  };

  // DELETE ALL handler
  const handleDeleteAll = async () => {
    try {
      await fetch("http://localhost:8000/api/detect/explain/clear", {
        method: "POST"
      });

      setShowDeleteConfirm(false);
      setSelectedEvent(null);
      fetchEvents();
    } catch (err) {
      console.error("Failed to clear XAI store:", err);
    }
  };

  return (
    <div className="page-container">
      <header className="page-header">
        <h1>Explainability (XAI)</h1>
        <p className="page-subtitle">
          Understand why SentinelCloud flagged an event.
        </p>
      </header>

      {/* DELETE BUTTON — Placed on top */}
      <div style={{ marginBottom: "15px" }}>
        <button
          className="danger-btn-xai"
          onClick={() => setShowDeleteConfirm(true)}
        >
          Delete All Events
        </button>
      </div>

      {/* Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="xai-modal-overlay">
          <div className="xai-modal">
            <h3>Delete All Explained Events?</h3>
            <p style={{ marginBottom: "20px", fontSize: "1rem" }}>
              Deleting these events will remove all stored XAI explanations.
              You will need to run the simulation again to generate new events.
            </p>

            <div className="modal-buttons">
              <button
                className="modal-btn-cancel"
                onClick={() => setShowDeleteConfirm(false)}
              >
                Cancel
              </button>

              <button
                className="modal-btn-confirm"
                onClick={handleDeleteAll}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="xai-layout">

        {/* LEFT PANEL */}
        <div className="xai-events-panel">
          <h3>Explained Events</h3>

          <button 
             className="primary-btn"
             onClick={fetchEvents}
             style={{ marginBottom: "12px" }}
          >
            Refresh
          </button>

          {eventList.length === 0 ? (
            <p style={{ color: "#888" }}>No explained events yet.</p>
          ) : (
            eventList.map(evt => (
              <div
                key={evt.event_id}
                className={`xai-event-item ${
                  selectedEvent?.event_id === evt.event_id ? "selected-xai-item" : ""
                }`}
                onClick={() => handleSelectEvent(evt)}
              >
                <span className="xai-event-label">{evt.grouped_label}</span>
                <span className="xai-event-time">{evt.timestamp}</span>
              </div>
            ))
          )}
        </div>

        {/* RIGHT PANEL */}
        <div style={{ flex: 1 }}>
          {selectedEvent ? (
            <DeepDiveCardXAI selectedEvent={selectedEvent} />
          ) : (
            <div className="card card-placeholder">
              <p>Select an event from the list to view details.</p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
