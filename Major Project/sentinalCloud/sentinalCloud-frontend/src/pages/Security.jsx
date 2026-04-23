import React, { useState } from 'react';
import * as XLSX from 'xlsx'; // --- NEW: Import the Excel library ---

import EventQueue from '../components/EventQueue/EventQueue.jsx';
import AlertsPanel from '../components/AlertsPanel/AlertsPanel.jsx';
import Radar from '../components/Radar/Radar.jsx';
import DeepDiveCard from '../components/DeepDiveCard/DeepDiveCard.jsx';
import AttackSummary from '../components/AttackSummary/AttackSummary.jsx';
import TrafficStats from '../components/TrafficStats/TrafficStats.jsx';

import './PageStyles.css';
import './Security.css';

export default function Security() {
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [sessionEvents, setSessionEvents] = useState([]);
  const [isSimulationActive, setIsSimulationActive] = useState(false);
  
  // --- NEW: State for the Export Button ---
  const [isExportDisabled, setIsExportDisabled] = useState(true);
  const [exportPeriod, setExportPeriod] = useState(1);
  // --- END NEW ---

  const [summaryStats, setSummaryStats] = useState({
    total: 0,
    attacks: 0,
    normals: 0,
    avgConfidence: 0.0,
  });

  const [recentAlerts, setRecentAlerts] = useState([]);

  const handleAttackDetected = (eventData) => {
    console.log("New Event DETECTED:", eventData);
    if (eventData && eventData.event_id) {
      setSessionEvents(prevEvents => [eventData, ...prevEvents].slice(0, 500));
      setSelectedEvent(eventData);

      setSummaryStats(prevStats => {
        const newTotal = prevStats.total + 1;
        const newAttacks = eventData.type === 'attack' ? prevStats.attacks + 1 : prevStats.attacks;
        const newNormals = eventData.type !== 'attack' ? prevStats.normals + 1 : prevStats.normals;
        const currentConfidence = parseFloat(eventData.confidence) || 0;
        const newTotalConfidence = (prevStats.avgConfidence * prevStats.total) + currentConfidence;
        const newAvgConfidence = newTotalConfidence / newTotal;

        return {
          total: newTotal,
          attacks: newAttacks,
          normals: newNormals,
          avgConfidence: newAvgConfidence
        };
      });

      if (eventData.type === 'attack') {
        setRecentAlerts(prevAlerts => [eventData, ...prevAlerts].slice(0, 50));
      }
    } else {
      console.warn("handleAttackDetected called with invalid data:", eventData);
    }
  };

  const handleEventSelected = (eventData) => {
    console.log("Event SELECTED:", eventData);
    if (eventData && eventData.event_id) {
      setSelectedEvent(eventData);
    } else {
      console.warn("handleEventSelected called with invalid data:", eventData);
      setSelectedEvent(null);
    }
  };

  // --- NEW: Function to handle the Excel export ---
// --- NEW: Function to handle the Excel export (FIXED WIDE FORMAT) ---
// --- NEW: Function to handle the Excel export (FINAL WIDE FORMAT + TYPE) ---
  const handleExport = () => {
    // 1. Process Event Data (NEW 'WIDE' FORMAT)
    const eventData = sessionEvents.map(event => {
      // Start with the base row of info
      const row = {
        'Event ID': event.event_id,
        'Timestamp': event.time,
        'Prediction': event.label,
        'Type': event.specific_label, // <-- THIS IS THE NEW COLUMN YOU WANTED
        'Model Used': event.model_used,
        'Confidence (%)': event.confidence
      };

      // Pre-populate feature columns as 'N/A'
      for (let i = 1; i <= 7; i++) {
        row[`Feature ${i}`] = 'N/A';
      }

      // If the event has SHAP data, overwrite the 'N/A' values
      if (event.shap_explanation && event.shap_explanation.features) {
        event.shap_explanation.features.forEach((feature, index) => {
          const colName = `Feature ${index + 1}`; // e.g., "Feature 1"
          
          // Format the cell value: "feature_name = value (Impact: impact_value)"
          const cellValue = `${feature.name} = ${feature.value} (Impact: ${feature.impact.toFixed(3)})`;
          
          row[colName] = cellValue;
        });
      }
      
      return row;

    }).reverse(); // Reverse for chronological order (oldest first)

    // 2. Process Summary Data (This part is perfect and unchanged)
    const summaryData = [
      { Statistic: 'Total Events', Value: summaryStats.total },
      { Statistic: 'Attacks Detected', Value: summaryStats.attacks },
      { Statistic: 'Normal Events', Value: summaryStats.normals },
      { Statistic: 'Average Confidence', Value: `${summaryStats.avgConfidence.toFixed(2)}%` }
    ];

    // 3. Create Excel Workbook and Sheets
    const wb = XLSX.utils.book_new();
    const wsEvents = XLSX.utils.json_to_sheet(eventData);
    const wsSummary = XLSX.utils.json_to_sheet(summaryData);

    // 4. Add Sheets to Workbook
    XLSX.utils.book_append_sheet(wb, wsEvents, 'Event Details');
    XLSX.utils.book_append_sheet(wb, wsSummary, 'Simulation Summary');

    // 5. Generate Filename and Download
    const filename = `IDS_Events_Period_${exportPeriod}.xlsx`;
    XLSX.writeFile(wb, filename);

    // 6. Update state for next export
    setExportPeriod(prevPeriod => prevPeriod + 1);
    setIsExportDisabled(true); // Disable button again after export
  };
  // --- END OF UPDATED FUNCTION ---

  return (
    <div className="page-container security-dashboard-layout">
        <header className="page-header">
            <h1>Security Dashboard</h1>
        </header>

      <div className="security-dashboard-grid">
      
        {/* --- Left Column --- */}
        <div className="security-column left-column">
          <EventQueue
            events={sessionEvents}
            onSelect={handleEventSelected} 
            selectedEventId={selectedEvent ? selectedEvent.event_id : null}
            isSimulationStopped={!isSimulationActive && sessionEvents.length > 0}
          />
          <AlertsPanel alerts={recentAlerts} />
        </div>

        {/* --- Center Column --- */}
        <div className="security-column center-column">
          <Radar 
            onAttackDetected={handleAttackDetected} 
            onSimulationStart={() => {
              setIsSimulationActive(true);
              setSessionEvents([]);
              setSelectedEvent(null);
              setSummaryStats({ total: 0, attacks: 0, normals: 0, avgConfidence: 0.0 });
              setRecentAlerts([]);
              setIsExportDisabled(true); // --- NEW: Disable button on start
            }}
            onSimulationStop={() => {
              setIsSimulationActive(false);
              setIsExportDisabled(false); // --- NEW: Enable button on stop
            }}
          />
          <AttackSummary stats={summaryStats} />
          
          {/* --- NEW: Export Button --- */}
          <button 
            onClick={handleExport} 
            disabled={isExportDisabled}
            className="export-button" // (Add styling for this class in your CSS)
          >
            Export Results
          </button>
          {/* --- END NEW BUTTON --- */}

        </div>

        {/* --- Right Column --- */}
        <div className="security-column right-column">
          <DeepDiveCard selectedEvent={selectedEvent} />
          {/* We are leaving TrafficStats commented out as requested */}
          {/* <TrafficStats /> */}
        </div>
      </div>
    </div>
  );
}