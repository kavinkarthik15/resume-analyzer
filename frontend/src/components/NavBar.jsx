import React, { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'

export default function NavBar({onLogin, onRegister, isLoggedIn, userProfile, onLogout}){
  const [profileOpen, setProfileOpen] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  function scrollToSection(id) {
    if (location.pathname !== '/') {
      navigate('/')
      setTimeout(() => {
        const el = document.getElementById(id)
        if (el) el.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    } else {
      const el = document.getElementById(id)
      if (el) el.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <header className="w-full bg-gradient-to-r from-[#0f1a35]/90 via-[#1a0f35]/90 to-[#0b0620]/90 backdrop-blur-md px-6 py-4 fixed top-0 z-40 border-b border-white/10">
      <div className="w-full flex items-center justify-between">
        {/* Logo Left - Home Link */}
        <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition">
          <div className="text-white font-bold text-xl bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">🚀 AI Resume Analyzer</div>
        </Link>

        {/* Nav Items + Auth Right */}
        <div className="flex items-center gap-8">
          <nav className="hidden md:flex items-center gap-8">
            <Link to="/" className="text-slate-300 hover:text-white transition font-medium">Dashboard</Link>
            <a href="/#features" onClick={(e) => { e.preventDefault(); scrollToSection('features'); }} className="text-slate-300 hover:text-white transition font-medium">Features</a>
            <a href="/#about" onClick={(e) => { e.preventDefault(); scrollToSection('about'); }} className="text-slate-300 hover:text-white transition font-medium">About</a>
            <a href="/#contact" onClick={(e) => { e.preventDefault(); scrollToSection('contact'); }} className="text-slate-300 hover:text-white transition font-medium">Contact</a>
          </nav>

          {!isLoggedIn ? (
            <div className="flex items-center gap-3">
              <button onClick={onLogin} className="px-6 py-2 rounded-full bg-white/10 hover:bg-white/20 text-white border border-white/30 font-semibold transition">Login</button>
              <button onClick={onRegister} className="px-6 py-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white shadow-lg btn-glow font-semibold transition">Register</button>
            </div>
          ) : (
            userProfile && (
              <div className="relative">
                <button 
                  onClick={() => setProfileOpen(!profileOpen)}
                  className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold hover:scale-110 transition shadow-lg"
                >
                  {userProfile.name.charAt(0).toUpperCase()}
                </button>
                
                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white/10 border border-white/20 backdrop-blur-xl rounded-lg shadow-lg p-4 animate-fade-in">
                    <div className="text-white font-semibold mb-3">{userProfile.name}</div>
                    <a href="#profile" className="block text-slate-300 hover:text-white mb-2 transition">My Profile</a>
                    <a href="#resumes" className="block text-slate-300 hover:text-white mb-2 transition">My Resumes</a>
                    <a href="#settings" className="block text-slate-300 hover:text-white mb-4 transition">Settings</a>
                    <button 
                      onClick={() => { onLogout(); setProfileOpen(false); }}
                      className="w-full px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white font-semibold transition"
                    >
                      Logout
                    </button>
                  </div>
                )}
              </div>
            )
          )}
        </div>
      </div>
    </header>
  )
}
