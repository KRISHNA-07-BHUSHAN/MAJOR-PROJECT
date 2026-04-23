// src/components/EventQueue/EventQueue.jsx (Receives events prop)
import React from 'react'; // Removed useState, useEffect
import PropTypes from 'prop-types';
import './EventQueue.css'; // Make sure CSS for scrolling is applied here

// --- UPDATED: Added 'isSimulationStopped' prop ---
const EventQueue = ({ events, onSelect, selectedEventId, isSimulationStopped }) => {

  const getEventTypeClass = (type) => (type === 'attack' ? 'event-attack' : 'event-normal');

  return (
    // Add card class for consistent styling
    <div className="event-queue card"> 
      <h3 className="card-title">Live Event Queue</h3>
      {/* List will scroll if CSS is applied correctly */}
      <ul className="event-list"> 
        {/* Directly use the events prop */}
        {events && events.length > 0 ? (
          events.map((event) => (
            <li
              key={event.event_id} 
              // --- UPDATED: Added 'stopped' class based on prop ---
              className={
                `event-item ${getEventTypeClass(event.type)} ` +
                `${selectedEventId === event.event_id ? 'selected' : ''} ` +
                `${isSimulationStopped ? 'stopped' : ''}`
              }
              onClick={() => onSelect(event)} // Clicking selects the event
            >
              <span className="event-label">{event.label}</span>
              <span className="event-time">{event.time}</span>
              <span className="event-confidence">{event.confidence}%</span>
            </li>
          ))
        ) : (
          // Message shown when sessionEvents is empty
          <p className="no-events">Simulate an attack to populate the queue.</p> 
        )}
      </ul>
    </div>
  );
};

// Update PropTypes: Add 'events' requirement
EventQueue.propTypes = {
  events: PropTypes.arrayOf(PropTypes.shape({
      event_id: PropTypes.string.isRequired,
      label: PropTypes.string,
      time: PropTypes.string,
      type: PropTypes.string,
      confidence: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  })).isRequired, 
  onSelect: PropTypes.func.isRequired,
  selectedEventId: PropTypes.string,
  isSimulationStopped: PropTypes.bool, // --- NEW PROP ---
};

// Add defaultProps for events
EventQueue.defaultProps = {
    events: [], // Default to empty array
    selectedEventId: null,
    isSimulationStopped: false, // --- NEW PROP DEFAULT ---
};


export default EventQueue;