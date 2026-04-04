import React from 'react'
import { Link, useLocation } from 'react-router-dom'

export default function Sidebar({ collapsed, setCollapsed }) {
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  const menuItems = [
    { icon: '📊', label: 'Dashboard', path: '/' },
    { icon: '📝', label: 'Resume Analysis', path: '/resume-analysis' },
    { icon: '🎯', label: 'JD Matching', path: '/jd-comparison' },
    { icon: '⚠️', label: 'Format Warnings', path: '/resume-warnings' },
    { icon: '🚀', label: 'Role Readiness', path: '/role-selection' },
    { icon: '✨', label: 'Resume Rewriter', path: '/resume-rewriter' },
    { icon: '💬', label: 'AI Assistant', path: '/chat-assistant' },
    { icon: '📚', label: 'History', path: '/history' },
  ]

  return (
    <aside
      className={`fixed left-0 top-0 h-screen bg-white/5 border-r border-white/10 backdrop-blur-2xl transition-all duration-350 cubic-bezier(0.34, 1.56, 0.64, 1) z-30 pt-20 flex flex-col
        ${collapsed ? 'w-20' : 'w-64'}`}
      style={{
        boxShadow: 'inset -1px 0 0 rgba(0,0,0,0.1), 0 0 20px var(--accent-glow)',
      }}
    >
      {/* Toggle Button */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute top-24 -right-3 w-6 h-6 rounded-full btn-accent flex items-center justify-center text-white text-xs font-bold hover:scale-110 transition-transform z-40"
      >
        {collapsed ? '→' : '←'}
      </button>

      {/* Logo */}
      {!collapsed && (
        <div className="px-6 py-4 border-b border-white/10">
          <h2 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            AI Resume
          </h2>
          <p className="text-xs text-slate-400 mt-1">SaaS Dashboard</p>
        </div>
      )}

      {/* Menu Items - Scrollable */}
      <nav className="mt-6 px-3 flex flex-col gap-2 flex-1 overflow-y-auto pb-20">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center gap-4 px-4 py-3 rounded-lg transition-all duration-300 cubic-bezier(0.34, 1.56, 0.64, 1) group
              ${isActive(item.path)
                ? 'bg-accent-soft border border-accent text-white nav-item-active'
                : 'text-slate-300 hover:bg-white/5 border border-transparent hover:text-white'
              }`}
            title={collapsed ? item.label : ''}
          >
            <span className="text-xl flex-shrink-0 transition-transform group-hover:scale-110">{item.icon}</span>
            {!collapsed && (
              <>
                <span className="font-medium">{item.label}</span>
                {isActive(item.path) && (
                  <div className="ml-auto w-2 h-2 rounded-full bg-accent animate-pulse"></div>
                )}
              </>
            )}
          </Link>
        ))}
      </nav>

      {/* Footer - Sticky at bottom */}
      {!collapsed && (
        <div className="px-6 py-4 border-t border-white/10 mt-auto">
          <div className="glass p-4 rounded-lg text-center border border-purple-500/20">
            <p className="text-xs text-slate-400 mb-2">Need Help?</p>
            <a href="#contact" className="text-cyan-400 hover:text-cyan-300 text-sm font-semibold transition">
              Contact Support
            </a>
          </div>
        </div>
      )}
    </aside>
  )
}
