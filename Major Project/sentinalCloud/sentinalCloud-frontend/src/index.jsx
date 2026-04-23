import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

// Note: We moved <BrowserRouter> into App.jsx in the last step.
// Wrapping it here is also fine, but for consistency with the
// previous answer, we will rely on it being inside App.jsx.
// The code will be simpler here.

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);