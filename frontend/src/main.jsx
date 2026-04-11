import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { AuthProvider } from './context/AuthContext'
import { AnalysisProvider } from './context/AnalysisContext'
import './index.css'
import './styles/global.css'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <AnalysisProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </AnalysisProvider>
    </AuthProvider>
  </React.StrictMode>
)
