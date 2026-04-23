import React, { useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
//import Chart from 'chart.js/auto'; // <-- THIS LINE IS NOW UNCOMMENTED
import './SHAPWaterfall.css'; 

const SHAPWaterfall = ({ shapData }) => {
  const chartRef = useRef(null); // Ref to store the chart instance
  const canvasRef = useRef(null); // Ref for the canvas element

  useEffect(() => {
    if (!shapData || !shapData.features || shapData.features.length === 0 || !canvasRef.current) {
      // Clear previous chart if data is invalid or canvas isn't ready
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
      return;
    }

    const { base_value, features } = shapData;

    // --- Prepare data for Waterfall Chart ---
    const labels = ['Base Value', ...features.map(f => f.name), 'Final Prediction'];
    const dataPoints = [];
    let cumulativeValue = base_value;

    // 1. Base Value Bar
    dataPoints.push([0, base_value]); // Starts at 0, ends at base_value

    // 2. Feature Impact Bars (Floating)
    features.forEach(feature => {
      const startValue = cumulativeValue;
      const endValue = cumulativeValue + feature.impact;
      dataPoints.push([startValue, endValue]);
      cumulativeValue = endValue;
    });

    // 3. Final Prediction Bar
    dataPoints.push([0, cumulativeValue]); // Starts at 0, ends at the final value

    // Destroy previous chart instance if it exists
    if (chartRef.current) {
      chartRef.current.destroy();
    }

    // --- Create new Chart.js instance ---
    const ctx = canvasRef.current.getContext('2d');
    chartRef.current = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'SHAP Impact',
          data: dataPoints,
          backgroundColor: (context) => {
            const index = context.dataIndex;
            // First (Base) and Last (Final) bars are neutral
            if (index === 0 || index === labels.length - 1) {
              return 'rgba(100, 100, 100, 0.7)'; // Neutral color
            }
            // Feature bars: positive impact = green, negative = red
            const impact = features[index - 1].impact;
            return impact > 0 ? 'rgba(22, 163, 74, 0.7)' : 'rgba(220, 38, 38, 0.7)'; // Green/Red
          },
          borderColor: (context) => {
            const index = context.dataIndex;
            if (index === 0 || index === labels.length - 1) {
              return 'rgba(100, 100, 100, 1)';
            }
            const impact = features[index - 1].impact;
            return impact > 0 ? 'rgba(22, 163, 74, 1)' : 'rgba(220, 38, 38, 1)';
          },
          borderWidth: 1,
          barPercentage: 0.8, // Adjust bar thickness
        }]
      },
      options: {
        indexAxis: 'y', // Make it a horizontal waterfall
        responsive: true,
        maintainAspectRatio: false, // Important for fitting in container
        scales: {
          x: {
            stacked: false, // Waterfall bars are floating, not stacked
            title: {
              display: true,
              text: 'Model Output Value (Log Odds or Probability)'
            }
          },
          y: {
            stacked: false,
            beginAtZero: false, // Allow y-axis to adjust
          }
        },
        plugins: {
          legend: {
            display: false // Hide the dataset label legend
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const index = context.dataIndex;
                // This logic might be complex, check chart.js docs for floating bars
                // Simplified: show impact for features
                if (index > 0 && index < labels.length - 1) {
                   const impact = features[index - 1].impact;
                   return ` Impact: ${impact.toFixed(4)}`;
                }
                // Show absolute value for base/final
                return ` Value: ${context.parsed.x.toFixed(4)}`;
              }
            }
          }
        }
      }
    });

    // Cleanup function to destroy chart on component unmount
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };

  }, [shapData]); // Re-run effect when shapData changes

  // Render the canvas element
  return (
    <div className="shap-waterfall-container">
      <h4 className="shap-header">Feature Impact on Prediction</h4>
      {(!shapData || !shapData.features || shapData.features.length === 0) ? (
          <p className="shap-placeholder">SHAP values are not available.</p>
      ) : (
        <canvas ref={canvasRef}></canvas>
      )}
    </div>
  );
};

// Updated PropTypes to expect the full explanation object
SHAPWaterfall.propTypes = {
  shapData: PropTypes.shape({
    base_value: PropTypes.number,
    final_prediction: PropTypes.number,
    features: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string.isRequired,
      value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]), // Original feature value
      impact: PropTypes.number.isRequired, // SHAP value
    }))
  }),
};

SHAPWaterfall.defaultProps = {
  shapData: null,
};

export default SHAPWaterfall;