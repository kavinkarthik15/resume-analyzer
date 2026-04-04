import React from 'react'
import { Link } from 'react-router-dom'

export default function Home(){
  return (
    <div className="page page-home w-full">
      <header className="hero">
        <h1>Welcome to AI Resume Analyzer</h1>
        <p className="hero-subtitle">Improve your resume with AI-powered analysis and increase your chances of getting hired.</p>
        <div className="upload-card glass-card">
          <h2>Upload Your Resume</h2>
          <p>Upload in PDF or DOCX format for instant analysis.</p>
          <Link to="/resume-analysis" className="btn primary">Choose File</Link>
        </div>
      </header>

      <section className="features">
        <h3>Key Features</h3>
        <div className="feature-grid">
          <div className="feature glass-card">ATS Score Analysis</div>
          <div className="feature glass-card">Skill Analysis</div>
          <div className="feature glass-card">Job Description Matching</div>
          <div className="feature glass-card">Resume Suggestions</div>
        </div>
      </section>

      <section className="roles">
        <h3>Check Your Role Readiness</h3>
        <div className="role-buttons">
          <button className="btn secondary">Data Scientist</button>
          <button className="btn secondary">AI Engineer</button>
          <button className="btn secondary">Web Developer</button>
          <button className="btn secondary">Backend Developer</button>
        </div>
      </section>

      <section className="assistant">
        <h3>AI Resume Assistant</h3>
        <div className="assistant-content">
          <ul>
            <li>Why is my ATS score low?</li>
            <li>What skills should I add?</li>
            <li>Rewrite my project description.</li>
          </ul>
          <div className="assistant-image">
            {/* placeholder for image/illustration */}
          </div>
        </div>
      </section>

      <footer className="footer">
        <nav>
          <a href="#">Home</a>
          <a href="#">Features</a>
          <a href="#">Contact</a>
          <a href="#">About</a>
        </nav>
        <p>© 2026 AI Resume Analyzer. All Right Reserved.</p>
      </footer>
    </div>
  )
}
