import React from 'react';
import './PageStyles.css'; // Import shared page styles

// Mock data for the team. In a real application, this might come from a CMS or API.
const teamMembers = [
  {
    id: 1,
    name: 'Manoj',
    role: 'Role Here...', // Example Role
    bio: 'About Here...', // Example Bio
    avatarUrl: 'https://avatar.iran.liara.run/public/8' // Example Placeholder
  },
  {
    id: 2,
    name: 'Thrisha',
    role: 'Role Here...', // Example Role
    bio: 'About Here...', // Example Bio
    avatarUrl: 'https://avatar.iran.liara.run/public/92' // Example Placeholder
  },
  {
    id: 3,
    name: 'Bhuvan',
    role: 'Role Here...', // Example Role
    bio: 'About Here...', // Example Bio
    avatarUrl: 'https://avatar.iran.liara.run/public/21' // Example Placeholder
  },
  {
    id: 4,
    name: 'Krishnakant',
    role: 'Role Here...', // Example Role
    bio: 'About Here...', // Example Bio
    avatarUrl: 'https://avatar.iran.liara.run/public/13' // Example Placeholder
  },
];

export default function Team() {
  return (
    <div className="page-container">
      <header className="page-header">
        <h1>Our Team</h1>
        <p>Meet the dedicated project team behind SentinelCloud's success.</p>
      </header>

      {/* Assuming PageStyles.css or a Team.css provides styles for .team-grid, .team-card etc. */}
      <div className="card-grid team-grid">
        {teamMembers.map((member) => (
          <div key={member.id} className="card team-card">
            <img src={member.avatarUrl} alt={member.name} className="team-avatar" />
            <h2 className="card-title team-name">{member.name}</h2>
            <p className="team-role">{member.role}</p>
            <p className="card-description">{member.bio}</p>
          </div>
        ))}
      </div>
    </div>
  );
}