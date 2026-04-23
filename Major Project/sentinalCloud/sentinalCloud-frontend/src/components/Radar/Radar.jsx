import React, { useState, useRef } from "react";
import PropTypes from 'prop-types';
import "./Radar.css";

// --- WIP Modal Component ---
const WipModal = ({ show, onClose }) => {
  if (!show) return null;
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h2>Feature Under Development</h2>
        <p>The Realtime Attack Simulation (Dynamic) feature is currently being built.</p>
        <p>Please check back later. Stay Tuned!</p>
        <button onClick={onClose} className="modal-close-button">Close</button>
      </div>
    </div>
  );
};
// --- End WIP Modal ---

// --- Constants ---
const RADAR_DIAMETER = 300;
const BLIP_TTL = 5000;
const API_BASE_URL = "http://localhost:8000/api";
const SIMULATION_INTERVAL_MS = 3000;

const Radar = ({ onAttackDetected, onSimulationStart, onSimulationStop }) => {
  const [blips, setBlips] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showWipModal, setShowWipModal] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const simulationTimeoutRef = useRef(null);
  const [consecutiveNormals, setConsecutiveNormals] = useState(0);

  // --- FIX: Use a REF for simulationMode ---
  // A 'ref' updates instantly and avoids state-timing bugs.
  const simulationModeRef = useRef('static'); 
  // We keep the 'useState' version *only* to update the button text
  const [simulationMode, setSimulationMode] = useState('static');

  // --- THIS FUNCTION IS NOW FIXED ---
  // (It reads from 'simulationModeRef' which is instant)
  const runSimulationCycle = async () => {
    if (isLoading) return;
    setIsLoading(true);
    setError(null);
    let eventData = null;

    try {
      let simResponse;
      
      // --- FIX: Read from simulationModeRef.current ---
      if (simulationModeRef.current === 'dynamic') {
        // 1. Call your new DYNAMIC generator API
        console.log("[Dynamic Mode] Requesting synthetic event...");
        simResponse = await fetch(`${API_BASE_URL}/simulation/dynamic`, {
          method: "POST", 
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({}) 
        });
      } else {
        // 2. Call your original STATIC API
        let desired_type = null;
        if (consecutiveNormals >= 2) { desired_type = "attack"; console.log("[Bias Logic] Requesting ATTACK.");}
        const requestPayload = desired_type ? { desired_type: desired_type } : {};

        simResponse = await fetch(`${API_BASE_URL}/simulation/static`, {
          method: "POST",
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestPayload)
        });
      }

      if (!simResponse.ok) {
        let detail = `Sim Error: ${simResponse.statusText}`;
        try { const errBody = await simResponse.json(); detail = errBody.detail || detail; } catch (_) {}
        throw new Error(`Static Sim Error: ${detail}`);
      }

      const simResult = await simResponse.json();
      const sampledData = simResult.data;
      const sourceFile = simResult.source;
      const modelKey = simResult.model_key;
      const trueLabel = simResult.label;

      if (!sampledData || typeof sampledData !== 'object' || Object.keys(sampledData).length === 0) { throw new Error("Invalid feature data from simulation."); }
      if (!modelKey) { throw new Error("Model key missing from simulation response."); }

      // 3. Send the generated event to /api/detect
      const detectPayload = { features: sampledData, model_key: modelKey };
      const detectResponse = await fetch(`${API_BASE_URL}/detect`, {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(detectPayload),
      });

      if (!detectResponse.ok) {
        let detail = `Detect Error: ${detectResponse.statusText}`;
        try { const errBody = await detectResponse.json(); detail = errBody.detail || detail; } catch (_) {}
        let errorMsg = `Detection Error: ${detail}`;
        if (detail.includes("incompatible")) { errorMsg += " ---> Check backend logic."; }
        throw new Error(errorMsg);
      }

      const detectionResult = await detectResponse.json();
      const event_id_from_backend = detectionResult.event_id;
      if (!event_id_from_backend) { throw new Error("Backend did not return an event_id."); }

      const shap_explanation = detectionResult.shap_explanation; 
      const predictedType = detectionResult.prediction?.toLowerCase() || 'unknown';
      const displayLabel = predictedType === 'attack' ? 'Attack' : 'Normal';

      // ⭐ Unified Dynamic Label Fix (FINAL)
      let specificLabel;

      // static mode → use original dataset label
      if (simulationModeRef.current === 'static') {
        specificLabel = trueLabel || displayLabel;
      }

      // dynamic mode → use backend class mapping
      else {
        specificLabel = detectionResult.specific_label;

        // fallback if backend classification not available
        if (!specificLabel || ["Unknown", "Attack", "Normal"].includes(specificLabel)) {
          specificLabel = displayLabel;
        }
      }

      
      eventData = {
        event_id: event_id_from_backend,
        id: event_id_from_backend,
        label: displayLabel,
        specific_label: specificLabel,
        time: new Date().toLocaleTimeString(),
        type: predictedType,
        confidence: ((detectionResult.confidence ?? 0) * 100).toFixed(1),
        features: sampledData,
        model_used: detectionResult.model_used || modelKey,
        sourceFile: sourceFile || 'N/A',
        shap_explanation: shap_explanation,
      };

      const isAttackBlip = eventData.type === 'attack';
      const newBlip = { id: eventData.id, x: Math.random()*(RADAR_DIAMETER-40)-(RADAR_DIAMETER/2-20), y: Math.random()*(RADAR_DIAMETER-40)-(RADAR_DIAMETER/2-20), color: isAttackBlip ? "var(--error-color)" : "var(--success-color)", label: eventData.specific_label };
      setBlips((prev) => [...prev, newBlip].slice(-20));

      if (onAttackDetected) { onAttackDetected(eventData); }
      setTimeout(() => { setBlips((prev) => prev.filter((b) => b.id !== newBlip.id)); }, BLIP_TTL);

    } catch (err) {
      console.error(`!!! Simulation Cycle Error Caught:`, err);
      setError(err.message || "An unknown error occurred.");
    } finally {
      setIsLoading(false);
      if (eventData) {
        if (eventData.type === 'normal') { setConsecutiveNormals(prev => prev + 1); }
        else { setConsecutiveNormals(0); }
      } else { setConsecutiveNormals(0); }
    }
  };

  // --- THIS FUNCTION IS NOW FIXED ---
  // (Uses your original, correct ref-based logic)
  const handleStopSimulation = () => {
    console.log("--- Continuous Simulation STOP ---");
    setIsSimulating(false);
    if (simulationTimeoutRef.current) { 
      clearTimeout(simulationTimeoutRef.current); 
      simulationTimeoutRef.current = null; // This is the key line
    }
    if (onSimulationStop) { onSimulationStop(); }
    setConsecutiveNormals(0);
  };
  // --- End Stop Handler ---

  // --- THIS FUNCTION IS NOW FIXED ---
  // (Uses your original, correct ref-based logic)
  const simulationLoop = async () => {
    await runSimulationCycle(); 
    
    // Check the ref. If it's not null, schedule the next loop
    if (simulationTimeoutRef.current) { 
      simulationTimeoutRef.current = setTimeout(simulationLoop, SIMULATION_INTERVAL_MS);
    }
  };
  // --- End New Loop ---

  // --- THIS FUNCTION IS NOW FIXED ---
  const handleSimulateClick = async (simulationType) => {
    if (isSimulating) return; 

    // --- FIX: Update both the ref (instantly) and state (for UI) ---
    simulationModeRef.current = simulationType; 
    setSimulationMode(simulationType);
    
    console.log(`--- Continuous ${simulationType} Simulation START ---`);
    setIsSimulating(true); 
    setError(null); 
    setConsecutiveNormals(0);
    if (onSimulationStart) { onSimulationStart(); }
    simulationTimeoutRef.current = true; // Set ref to allow loop to start
    simulationLoop(); // Start the loop
  };
  // --- End UPDATED Click Handler ---

  // --- Return JSX (Updated labels) ---
  return (
     <div className="radar-container">
      {error && <div className="radar-error">Error: {error}</div>}
      <div className="radar-circle">
         <div className="radar-grid"> <div className="circle-grid circle1"></div> <div className="circle-grid circle2"></div> <div className="circle-grid circle3"></div> <div className="circle-grid circle4"></div> <div className="radar-cross-lines"></div> </div>
         <div className="radar-sweep"></div>
         {blips.map((blip) => <div key={blip.id} className="radar-blip" style={{left:`${blip.x+RADAR_DIAMETER/2}px`, top:`${blip.y+RADAR_DIAMETER/2}px`, backgroundColor: blip.color}} title={`${blip.label} (${blip.id})`}></div>)}
      </div>
      <div className="radar-controls">
        <button onClick={() => handleSimulateClick('static')} disabled={isSimulating} >
          {isSimulating && simulationMode === 'static' ? "Simulating..." : "Simulate Static"}
        </button>
        {isSimulating && ( <button onClick={handleStopSimulation} className="button-stop" > Stop Simulation </button> )}
        <button onClick={() => handleSimulateClick('dynamic')} disabled={isSimulating} > 
          {isSimulating && simulationMode === 'dynamic' ? "Simulating..." : "Simulate Dynamic"}
        </button>
      </div>
      <WipModal show={showWipModal} onClose={() => setShowWipModal(false)} />
    </div>
  );
}; // End Component

// --- PropTypes and DefaultProps (No Changes) ---
Radar.propTypes = {
  onAttackDetected: PropTypes.func.isRequired,
  onSimulationStart: PropTypes.func,
  onSimulationStop: PropTypes.func,
};
Radar.defaultProps = {
  onSimulationStart: () => {},
  onSimulationStop: () => {},
};

export default Radar;