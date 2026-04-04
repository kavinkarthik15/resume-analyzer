import React, { useState, useEffect } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import ThemeProvider from './components/ThemeProvider'
import NavBar from './components/NavBar'
import Sidebar from './components/Sidebar'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import Results from './pages/Results'
import EditResume from './pages/EditResume'
import History from './pages/History'
import JDComparison from './pages/JDComparison'
import ResumeWarnings from './pages/ResumeWarnings'
import RoleSelection from './pages/RoleSelection'
import ResumeRewriter from './pages/ResumeRewriter'
import ChatAssistant from './pages/ChatAssistant'
import AuthModal from './components/AuthModal'

export default function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [authOpen, setAuthOpen] = useState(false)
  const [authMode, setAuthMode] = useState('login')
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userProfile, setUserProfile] = useState(null)
  const location = useLocation()

  // Auto-collapse sidebar when navigating to dashboard pages
  useEffect(() => {
    const dashboardRoutes = ['/', '/resume-analysis', '/jd-comparison', '/resume-warnings', '/role-selection', '/resume-rewriter', '/chat-assistant', '/results', '/edit-resume', '/history']
    const isDashboardRoute = dashboardRoutes.includes(location.pathname)
    setSidebarCollapsed(isDashboardRoute)
  }, [location.pathname])

  function openAuth(mode = 'login'){
    setAuthMode(mode)
    setAuthOpen(true)
  }
  function closeAuth(){ setAuthOpen(false) }
  function handleLogout(){ setIsLoggedIn(false); setUserProfile(null) }
  function handleLogin(name){
    setIsLoggedIn(true)
    setUserProfile({name: name || 'User'})
    setAuthOpen(false)
  }

  return (
    <ThemeProvider>
      <>
        <NavBar onLogin={()=>openAuth('login')} onRegister={()=>openAuth('register')} isLoggedIn={isLoggedIn} userProfile={userProfile} onLogout={handleLogout} />
        
        <div className="app-layout flex w-full" style={{height: 'calc(100vh - 64px)'}}>
          <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} />
          
          <div className={`flex-1 w-full h-screen overflow-auto transition-all duration-300 ease-in-out ${sidebarCollapsed ? 'ml-20' : 'ml-64'}`}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/resume-analysis" element={<Landing />} />
              <Route path="/results" element={<Results />} />
              <Route path="/edit-resume" element={<EditResume />} />
              <Route path="/history" element={<History />} />
              <Route path="/jd-comparison" element={<JDComparison />} />
              <Route path="/resume-warnings" element={<ResumeWarnings />} />
              <Route path="/role-selection" element={<RoleSelection />} />
              <Route path="/resume-rewriter" element={<ResumeRewriter />} />
              <Route path="/chat-assistant" element={<ChatAssistant />} />
            </Routes>

            <AuthModal open={authOpen} mode={authMode} onClose={closeAuth} onSwitch={setAuthMode} onLoginSuccess={handleLogin} />
          </div>
        </div>
      </>
    </ThemeProvider>
  )
}
