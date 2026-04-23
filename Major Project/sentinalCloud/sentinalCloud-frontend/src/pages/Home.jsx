import React from 'react';
import { Link } from 'react-router-dom'; // Import Link for navigation

// Data for feature highlight cards
const features = [
  {
    id: 1,
    title: 'Real-time Detection',
    description: 'Monitor network traffic and detect anomalies as they happen with our high-performance models.',
    link: '/security'
  },
  {
    id: 2,
    title: 'AI-Powered Explainability',
    description: 'Understand exactly why an alert was triggered with clear, AI-driven SHAP and counterfactual explanations.',
    link: '/explainability'
  },
  {
    id: 3,
    title: 'Attack Library',
    description: 'Browse a comprehensive catalog of known attack signatures and patterns used by our detection engine.',
    link: '/attack-library'
  }
];

export default function Home() {
  return (
    <div className="page-container home-page">
      <div className="hero-section">
        <h1 className="hero-title">Welcome to SentinelCloud</h1>
        <p className="hero-subtitle">
          Your intelligent partner in network security. Monitor, detect, and understand threats in real-time.
        </p>
        <Link to="/security" className="cta-button">
          Go to Security Dashboard
        </Link>
      </div>

      <div className="features-section">
        <h2 className="section-title">Key Features</h2>
        <div className="card-grid">
          {features.map(feature => (
            <div key={feature.id} className="card feature-card">
              <h3 className="card-title">{feature.title}</h3>
              <p className="card-description">{feature.description}</p>
              <Link to={feature.link} className="card-link">Learn More &rarr;</Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}