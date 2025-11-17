/**
 * OSE Platform - Portal Principal
 * Main entry point
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'

// Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css'
// Bootstrap Icons
import 'bootstrap-icons/font/bootstrap-icons.css'

// Global styles
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
