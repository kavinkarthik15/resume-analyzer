import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { GoogleAuthProvider, signInWithEmailAndPassword, signInWithPopup } from 'firebase/auth'
import { auth } from '../firebase'

export default function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')

    try {
      await signInWithEmailAndPassword(auth, email, password)
      navigate('/upload')
    } catch (err) {
      console.error(err)
      setError('Login failed. Try again.')
    }
  }

  const handleGoogleLogin = async () => {
    const provider = new GoogleAuthProvider()
    setError('')
    setLoading(true)
    try {
      await signInWithPopup(auth, provider)
      navigate('/upload')
    } catch (err) {
      console.error(err)
      setError('Login failed. Try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page page-login">
      <div className="login-hero">
        <h1 className="title">Welcome to AI Resume Analyzer</h1>
        <p className="subtitle">Improve your resume with AI-powered analysis</p>
      </div>

      <form className="glass-card login-card" onSubmit={handleLogin}>
        <h2>Login</h2>
        <label>
          Email
          <input
            name="email"
            type="email"
            required
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>
        <label>
          Password
          <input
            name="password"
            type="password"
            required
            placeholder="********"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        <button className="btn primary" type="submit">Sign In</button>
        <button className="btn" type="button" onClick={handleGoogleLogin} disabled={loading}>
          {loading ? 'Signing in...' : 'Continue with Google'}
        </button>
        {error && (
          <p style={{ color: 'red', marginTop: '10px' }}>
            {error}
          </p>
        )}
      </form>
    </div>
  )
}
