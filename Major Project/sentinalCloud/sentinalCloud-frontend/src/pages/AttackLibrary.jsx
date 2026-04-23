import React from 'react';

// Mock data representing different types of attacks.
// In the future, this would be fetched from your backend API.
const attacks = [
  {
    id: 'ddos-01',
    name: 'DDoS (Distributed Denial-of-Service)',
    severity: 'High',
    description: 'An attempt to make an online service unavailable by overwhelming it with traffic from multiple sources.',
  },
  {
    id: 'phish-02',
    name: 'Phishing',
    severity: 'High',
    description: 'Fraudulent attempts, usually made through email, to steal sensitive data, such as login credentials and credit card numbers.',
  },
  {
    id: 'malw-03',
    name: 'Malware',
    severity: 'Medium',
    description: 'Software intentionally designed to cause damage to a computer, server, client, or computer network.',
  },
  {
    id: 'sqli-04',
    name: 'SQL Injection',
    severity: 'High',
    description: 'A code injection technique that might destroy your database. It involves inserting a malicious SQL query via input data.',
  },
  {
    id: 'xss-05',
    name: 'Cross-Site Scripting (XSS)',
    severity: 'Medium',
    description: 'A type of security vulnerability where attackers inject malicious scripts into content from otherwise trusted websites.',
  },
  {
    id: 'mitm-06',
    name: 'Man-in-the-Middle (MitM)',
    severity: 'High',
    description: 'An attack where the attacker secretly relays and possibly alters communications between two parties who believe they are directly communicating.',
  },
];

// A helper function to get a color class based on severity
const getSeverityClass = (severity) => {
  switch (severity.toLowerCase()) {
    case 'high':
      return 'severity-high';
    case 'medium':
      return 'severity-medium';
    case 'low':
      return 'severity-low';
    default:
      return '';
  }
};

export default function AttackLibrary() {
  return (
    <div className="page-container">
      <header className="page-header">
        <h1>Attack Library</h1>
        <p>A catalog of known attack types, their patterns, and severity.</p>
      </header>
      
      <div className="card-grid">
        {attacks.map((attack) => (
          <div key={attack.id} className="card">
            <div className="card-header">
              <h2 className="card-title">{attack.name}</h2>
              <span className={`severity-badge ${getSeverityClass(attack.severity)}`}>
                {attack.severity}
              </span>
            </div>
            <p className="card-description">{attack.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}