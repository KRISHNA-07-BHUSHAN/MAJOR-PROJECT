import React, { useState, useEffect } from "react";
import "./StartupAnimation.css";

export default function StartupAnimation({ onFinish }) {
  const fullText =
    "Initializing secure environment... Loading deep-learning modules... Activating XAI-based intrusion detection...";

  const [typedText, setTypedText] = useState("");
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    let index = 0;

    const interval = setInterval(() => {
      if (index < fullText.length) {
        setTypedText((prev) => prev + fullText.charAt(index));
        index++;
      } else {
        clearInterval(interval);

        // Start fade-out animation before exiting
        setTimeout(() => {
          setFadeOut(true);
          setTimeout(() => onFinish && onFinish(), 700);
        }, 800);
      }
    }, 30);

    return () => clearInterval(interval);
  }, [fullText, onFinish]);

  return (
    <div className={`startup-container ${fadeOut ? "fade-out" : ""}`}>
      <div className="glow-behind"></div>

      <h1 className="startup-title">Welcome Security Analyst</h1>

      <p className="startup-typed">
        {typedText}
        <span className="cursor"></span>
      </p>
    </div>
  );
}
