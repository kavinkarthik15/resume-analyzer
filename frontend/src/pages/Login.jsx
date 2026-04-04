import React from 'react'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const nav = useNavigate()
  function handleSubmit(e) {
    e.preventDefault()
    nav('/')
  }

  return (
    <div className="page page-login">
      <div className="login-hero">
        <h1 className="title">Welcome to AI Resume Analyzer</h1>
        <p className="subtitle">Improve your resume with AI-powered analysis</p>
      </div>

      <form className="glass-card login-card" onSubmit={handleSubmit}>
        <h2>Login</h2>
        <label>
          Email
          <input type="email" required placeholder="you@example.com" />
        </label>
        <label>
          Password
          <input type="password" required placeholder="••••••••" />
        </label>
        <button className="btn primary" type="submit">Sign In</button>
      </form>
    </div>
  )
}
