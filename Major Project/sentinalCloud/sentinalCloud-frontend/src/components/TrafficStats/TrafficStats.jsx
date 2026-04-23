// src/components/TrafficStats/TrafficStats.jsx (Refined - Fetches Own Data)
import React, { useState, useEffect, useRef } from 'react';
//import Chart from 'chart.js/auto'; // Ensure chart.js is installed
import PropTypes from 'prop-types'; // Keep PropTypes import if used
import './TrafficStats.css'; // Make sure this CSS file exists

const API_BASE_URL = "http://localhost:8000/api";

const TrafficStats = () => {
  const chartRef = useRef(null);
  const canvasRef = useRef(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    let chartInstance = null; // Store instance locally in effect scope

    const fetchTrafficData = async () => {
      if (!isMounted || !canvasRef.current) return;
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`${API_BASE_URL}/stats/traffic-over-time`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        if (!isMounted || !canvasRef.current) return; // Check again before rendering

        // Destroy previous chart instance *before* creating new one
        if (chartRef.current) {
          chartRef.current.destroy();
          chartRef.current = null;
        }


        const ctx = canvasRef.current.getContext('2d');
        // Get theme colors for chart (requires access to theme state or CSS variables)
        // Example using CSS variables (simpler):
        const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim() || '#a0a6b1';
        const gridColor = getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim() || '#2a2e36';


        chartInstance = new Chart(ctx, { // Assign to local variable
          type: 'line',
          data: {
            labels: data.labels || [],
            datasets: [
              {
                label: 'Benign Traffic',
                data: data.datasets?.find(d => d.label === 'Benign Traffic')?.data || [],
                borderColor: 'rgba(75, 192, 192, 1)', // Example color
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                fill: true,
                tension: 0.3,
              },
              {
                label: 'Malicious Traffic',
                data: data.datasets?.find(d => d.label === 'Malicious Traffic')?.data || [],
                borderColor: 'rgba(255, 99, 132, 1)', // Example color
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                fill: true,
                tension: 0.3,
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: { 
                beginAtZero: true,
                ticks: { color: textColor }, // Use theme color
                grid: { color: gridColor }    // Use theme color
              },
              x: { 
                ticks: { color: textColor }, // Use theme color
                grid: { color: gridColor }    // Use theme color
              }
            },
            plugins: {
              legend: {
                 position: 'top',
                 labels: { color: textColor } // Use theme color
              }
            }
          }
        });
        chartRef.current = chartInstance; // Assign to ref *after* creation
      } catch (err) {
        console.error("Failed to fetch traffic stats:", err);
         if (isMounted) setError(err.message);
      } finally {
         if (isMounted) setIsLoading(false);
      }
    };

    fetchTrafficData();

    // Cleanup function
    return () => {
      isMounted = false;
      // Use the local variable `chartInstance` or the ref for cleanup
      const instanceToDestroy = chartRef.current || chartInstance;
      if (instanceToDestroy) {
        instanceToDestroy.destroy();
        chartRef.current = null; // Clear ref on unmount
      }
    };
  }, []); // Run once on mount

  return (
    // Use card style from PageStyles.css or define locally
    <div className="traffic-stats-container card"> 
      <h2 className="card-title">Traffic Over Time</h2>
      {/* Ensure wrapper has height */}
      <div className="chart-wrapper"> 
        {isLoading && <p>Loading chart...</p>}
        {error && <p className="error-message">Error: {error}</p>}
        {/* Render canvas when not loading/error */}
        {!isLoading && !error && <canvas ref={canvasRef}></canvas>}
      </div>
    </div>
  );
};

// Update PropTypes: Remove 'attackEvents' requirement
TrafficStats.propTypes = {}; 

export default TrafficStats;