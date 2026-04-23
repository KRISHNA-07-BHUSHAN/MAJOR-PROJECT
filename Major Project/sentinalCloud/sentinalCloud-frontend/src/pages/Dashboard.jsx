import React, { useState, useEffect } from 'react';

// Import the components that will make up the dashboard
// Make sure the paths are correct relative to Dashboard.jsx
import TrafficStats from '../components/TrafficStats/TrafficStats.jsx';
import AlertsPanel from '../components/AlertsPanel/AlertsPanel.jsx';
// Import a shared CSS file for page styles
import './PageStyles.css'; // Make sure this CSS file exists

const API_BASE_URL = "http://localhost:8000/api"; // Your backend URL

export default function Dashboard() {
  // Initialize KPI state with loading indicators
  const [kpiData, setKpiData] = useState([
    { id: 1, title: 'Total Events Analyzed', value: '...' },
    { id: 2, title: 'High-Severity Alerts', value: '...' },
    { id: 3, title: 'Models Active', value: '...' },
    { id: 4, title: 'System Uptime (h)', value: '...' },
  ]);
  const [error, setError] = useState(null);

  // Fetch KPI data from the backend on component mount
  useEffect(() => {
    const fetchSummaryStats = async () => {
      setError(null); // Clear previous errors
      try {
        const response = await fetch(`${API_BASE_URL}/stats/summary`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        // Map the API data to the state structure, formatting numbers
        const formattedKpiData = [
          { id: 1, title: 'Total Events Analyzed', value: data.total_packets_analyzed?.toLocaleString() ?? 'N/A' },
          { id: 2, title: 'High-Severity Alerts', value: data.attacks_detected?.toLocaleString() ?? 'N/A', status: 'danger' },
          { id: 3, title: 'Models Active', value: '3' }, // Assuming 3 models based on backend logs
          { id: 4, title: 'System Uptime (h)', value: data.system_uptime_hours ?? 'N/A', status: 'success' },
        ];

        setKpiData(formattedKpiData);
      } catch (err) {
        console.error("Failed to fetch summary stats:", err);
        setError(err.message);
        // Set error state for KPIs
        setKpiData(prevKpi => prevKpi.map(kpi => ({ ...kpi, value: 'Error' })));
      }
    };

    fetchSummaryStats();
    // Run only once on component mount
  }, []);

  return (
    <div className="page-container">
      <header className="page-header">
        <h1>Dashboard</h1>
        <p>High-level overview of network security events and metrics.</p>
      </header>

      {/* KPI Stats Grid */}
      {error && <p className="error-message">Could not load KPI data: {error}</p>}
      <div className="stats-grid">
        {kpiData.map(kpi => (
          <div key={kpi.id} className="stat-card">
            <h3 className="stat-card-title">{kpi.title}</h3>
            <p className={`stat-card-value ${kpi.status || ''}`}>{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Main Dashboard Grid for Charts and Lists */}
      <div className="main-grid two-columns">

        {/* Card 1: Renders the TrafficStats component */}
        {/* This component fetches and displays the traffic line chart */}
        <div className="card">
          <TrafficStats />
        </div>

        {/* Card 2: Renders the AlertsPanel component */}
        {/* This component fetches and displays recent alerts */}
        <div className="card">
          <AlertsPanel />
        </div>
      </div>
    </div>
  );
}