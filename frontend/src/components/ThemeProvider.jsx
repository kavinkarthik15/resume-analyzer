import React from 'react'
import { useLocation } from 'react-router-dom'

export default function ThemeProvider({ children }) {
  const location = useLocation()

  // Map routes to theme classes
  const getThemeClass = (pathname) => {
    switch (pathname) {
      case '/':
        return 'route-resume'
      case '/dashboard':
        return 'route-dashboard'
      case '/jd-comparison':
        return 'route-jd-comparison'
      case '/resume-warnings':
        return 'route-resume-warnings'
      case '/role-selection':
        return 'route-role-selection'
      case '/resume-rewriter':
        return 'route-resume-rewriter'
      case '/chat-assistant':
        return 'route-chat-assistant'
      case '/results':
        return 'route-resume'
      case '/edit-resume':
        return 'route-resume'
      case '/history':
        return 'route-resume'
      default:
        return 'route-resume'
    }
  }

  const themeClass = getThemeClass(location.pathname)

  return (
    <div className={themeClass}>
      {children}
    </div>
  )
}
