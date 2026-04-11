import React, { useState, useEffect } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import ThemeProvider from './components/ThemeProvider'
import NavBar from './components/NavBar'
import Sidebar from './components/Sidebar'
import ProtectedRoute from './components/ProtectedRoute'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import Results from './pages/Results'
import EditResume from './pages/EditResume'
import History from './pages/History'
import Login from './pages/Login'
import Upload from './pages/Upload'
import JDComparison from './pages/JDComparison'
import ResumeWarnings from './pages/ResumeWarnings'
import RoleSelection from './pages/RoleSelection'
import ResumeRewriter from './pages/ResumeRewriter'
import ChatAssistant from './pages/ChatAssistant'

export default function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const location = useLocation()

  // Auto-collapse sidebar when navigating to dashboard pages
  useEffect(() => {
    const dashboardRoutes = ['/', '/resume-analysis', '/jd-comparison', '/resume-warnings', '/role-selection', '/resume-rewriter', '/chat-assistant', '/results', '/edit-resume', '/history']
    const isDashboardRoute = dashboardRoutes.includes(location.pathname)
    setSidebarCollapsed(isDashboardRoute)
  }, [location.pathname])

  return (
    <ThemeProvider>
      <>
        <NavBar />
        
        <div className="app-layout flex w-full" style={{height: 'calc(100vh - 64px)'}}>
          <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} />
          
          <div className={`flex-1 w-full h-screen overflow-auto transition-all duration-300 ease-in-out ${sidebarCollapsed ? 'ml-20' : 'ml-64'}`}>
            <Routes>
              <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/login" element={<Login />} />
              <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
              <Route path="/resume-analysis" element={<ProtectedRoute><Landing /></ProtectedRoute>} />
              <Route path="/results" element={<ProtectedRoute><Results /></ProtectedRoute>} />
              <Route path="/edit-resume" element={<ProtectedRoute><EditResume /></ProtectedRoute>} />
              <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
              <Route path="/jd-comparison" element={<ProtectedRoute><JDComparison /></ProtectedRoute>} />
              <Route path="/resume-warnings" element={<ProtectedRoute><ResumeWarnings /></ProtectedRoute>} />
              <Route path="/role-selection" element={<ProtectedRoute><RoleSelection /></ProtectedRoute>} />
              <Route path="/resume-rewriter" element={<ProtectedRoute><ResumeRewriter /></ProtectedRoute>} />
              <Route path="/chat-assistant" element={<ProtectedRoute><ChatAssistant /></ProtectedRoute>} />
            </Routes>
          </div>
        </div>
      </>
    </ThemeProvider>
  )
}
