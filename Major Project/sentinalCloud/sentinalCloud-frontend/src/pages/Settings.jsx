import React from "react";
import "./PageStyles.css"; // keep your shared styling

export default function Settings() {
  return (
    <div className="page-container">
      <header className="page-header">
        <h1>Settings</h1>
        <p>This will be updated in the upcoming versions.</p>
      </header>

      <div
        style={{
          background: "rgba(30, 40, 55, 0.6)",
          padding: "30px",
          borderRadius: "12px",
          border: "1px solid rgba(255,255,255,0.1)",
          textAlign: "center",
          marginTop: "20px",
          fontSize: "18px",
          color: "#c9d2e0",
        }}
      >
        🔧 <b>Settings Module Coming Soon</b>  
        <p style={{ marginTop: "10px" }}>
          We are actively working on improving this section.
        </p>
      </div>
    </div>
  );
}
