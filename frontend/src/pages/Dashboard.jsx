import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  createWorkspaceId,
  deleteWorkspace,
  listWorkspaces,
} from '../utils/workspaceStorage'

export default function Dashboard() {
  const navigate = useNavigate()
  const [workspaces, setWorkspaces] = useState([])

  useEffect(() => {
    setWorkspaces(listWorkspaces())
  }, [])

  const openWorkspace = (id) => {
    navigate(`/resume-rewriter?id=${id}`)
  }

  const createNewWorkspace = () => {
    const id = createWorkspaceId()
    navigate(`/resume-rewriter?id=${id}`)
  }

  const removeWorkspace = (id) => {
    const next = deleteWorkspace(id)
    setWorkspaces(next)
  }

  const features = [
    {
      icon: '📝',
      title: 'Resume Analysis',
      description: 'Get instant ATS scoring and detailed improvement suggestions',
      path: '/resume-analysis',
      color: 'from-blue-500/20 to-cyan-500/20',
      border: 'border-blue-500/30',
    },
    {
      icon: '🎯',
      title: 'JD Matching',
      description: 'Compare your resume against job descriptions for better matches',
      path: '/jd-comparison',
      color: 'from-purple-500/20 to-pink-500/20',
      border: 'border-purple-500/30',
    },
    {
      icon: '⚠️',
      title: 'Format Warnings',
      description: 'Identify ATS compatibility issues and formatting problems',
      path: '/resume-warnings',
      color: 'from-red-500/20 to-orange-500/20',
      border: 'border-red-500/30',
    },
    {
      icon: '🚀',
      title: 'Role Readiness',
      description: 'See how well your resume matches specific job roles',
      path: '/role-selection',
      color: 'from-green-500/20 to-emerald-500/20',
      border: 'border-green-500/30',
    },
    {
      icon: '✨',
      title: 'Resume Rewriter',
      description: 'Improve your bullet points with AI-powered suggestions',
      path: '/resume-rewriter',
      color: 'from-yellow-500/20 to-orange-500/20',
      border: 'border-yellow-500/30',
    },
    {
      icon: '💬',
      title: 'AI Assistant',
      description: 'Get instant answers and personalized resume guidance',
      path: '/chat-assistant',
      color: 'from-indigo-500/20 to-purple-500/20',
      border: 'border-indigo-500/30',
    },
  ]

  const stats = [
    { label: 'Resumes Analyzed', value: '10K+' },
    { label: 'Jobs Matched', value: '50K+' },
    { label: 'Success Rate', value: '94%' },
    { label: 'Users Hired', value: '2.3K' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 pt-32 pb-12 px-6">
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
            AI-Powered Resume Optimization
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            Our intelligent platform analyzes your resume against job descriptions, identifies ATS issues, and provides personalized improvement suggestions to help you land your dream job.
          </p>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-16">
          {stats.map((stat) => (
            <div key={stat.label} className="dashboard-card text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                {stat.value}
              </div>
              <p className="text-slate-400 text-sm mt-2">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Features Grid */}
        <div className="dashboard-card mb-10 bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 border border-emerald-500/30">
          <div className="flex items-center justify-between gap-4 flex-wrap mb-5">
            <div>
              <h2 className="text-2xl font-bold text-white">Saved Resume Sessions</h2>
              <p className="text-sm text-slate-400 mt-1">Reopen your latest workspace and continue from where you left off.</p>
            </div>
            <button
              type="button"
              onClick={createNewWorkspace}
              className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white font-semibold transition"
            >
              New Resume Session
            </button>
          </div>

          {workspaces.length === 0 ? (
            <div className="rounded-xl border border-white/10 bg-white/5 p-5 text-slate-300">
              No saved resumes yet. Create your first resume session to start persistent editing.
            </div>
          ) : (
            <div className="space-y-3">
              {workspaces.map((workspace) => (
                <div
                  key={workspace.id}
                  className="rounded-xl border border-white/10 bg-white/5 p-4 flex items-center justify-between gap-4 flex-wrap"
                >
                  <div>
                    <h3 className="text-white font-semibold">{workspace.title || 'Resume'}</h3>
                    <p className="text-xs text-slate-400 mt-1">
                      Last updated: {workspace.updatedAt ? new Date(workspace.updatedAt).toLocaleString() : 'N/A'}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      Versions: {Array.isArray(workspace.versions) ? workspace.versions.length : 0}
                    </p>
                  </div>

                  <div className="flex items-center gap-2 flex-wrap">
                    <button
                      type="button"
                      onClick={() => openWorkspace(workspace.id)}
                      className="px-3 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-600 text-white text-sm font-semibold transition"
                    >
                      Open
                    </button>
                    <button
                      type="button"
                      onClick={() => removeWorkspace(workspace.id)}
                      className="px-3 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-slate-200 text-sm font-semibold transition"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div id="features" className="mb-16 scroll-mt-32">
          <h2 className="text-3xl font-bold mb-8">Powerful Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => (
              <Link
                key={feature.path}
                to={feature.path}
                className={`dashboard-card group ${feature.color} border ${feature.border} hover:shadow-2xl hover:scale-105 transition-all duration-300`}
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-cyan-300 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-slate-400 text-sm mb-4">{feature.description}</p>
                <div className="text-cyan-400 text-sm font-semibold flex items-center gap-2 group-hover:gap-3 transition-all">
                  Get Started <span>→</span>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* How It Works */}
        <div className="dashboard-card mb-16">
          <h2 className="text-3xl font-bold mb-8">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 flex items-center justify-center text-white font-bold text-lg mx-auto mb-4">
                1
              </div>
              <h3 className="font-semibold text-white mb-2">Upload Resume</h3>
              <p className="text-sm text-slate-400">Simply upload your resume in PDF or DOCX format</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold text-lg mx-auto mb-4">
                2
              </div>
              <h3 className="font-semibold text-white mb-2">AI Analysis</h3>
              <p className="text-sm text-slate-400">Our AI analyzes your resume for ATS compatibility</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-lg mx-auto mb-4">
                3
              </div>
              <h3 className="font-semibold text-white mb-2">Get Insights</h3>
              <p className="text-sm text-slate-400">Receive detailed scores and improvement suggestions</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-pink-500 to-red-500 flex items-center justify-center text-white font-bold text-lg mx-auto mb-4">
                4
              </div>
              <h3 className="font-semibold text-white mb-2">Optimize & Succeed</h3>
              <p className="text-sm text-slate-400">Improve your resume and land interviews faster</p>
            </div>
          </div>
        </div>

        {/* About Section */}
        <div id="about" className="mb-16 scroll-mt-32">
          <h2 className="text-3xl font-bold mb-8">About Us</h2>
          <div className="dashboard-card bg-gradient-to-r from-blue-500/5 to-purple-500/5 border border-blue-500/20">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              <div>
                <h3 className="text-2xl font-semibold text-white mb-4">AI-Driven Resume Excellence</h3>
                <p className="text-slate-400 leading-relaxed mb-4">
                  AI Resume Analyzer is built to bridge the gap between job seekers and their dream roles. Our platform leverages cutting-edge AI and machine learning to provide actionable insights that transform ordinary resumes into interview-winning documents.
                </p>
                <p className="text-slate-400 leading-relaxed">
                  Whether you're a fresh graduate or a seasoned professional, our tools help you understand ATS requirements, optimize keyword usage, and present your experience in the most compelling way possible.
                </p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="dashboard-card text-center">
                  <div className="text-3xl mb-2">🤖</div>
                  <h4 className="font-semibold text-white text-sm">AI-Powered</h4>
                  <p className="text-xs text-slate-400 mt-1">Advanced NLP analysis</p>
                </div>
                <div className="dashboard-card text-center">
                  <div className="text-3xl mb-2">⚡</div>
                  <h4 className="font-semibold text-white text-sm">Instant Results</h4>
                  <p className="text-xs text-slate-400 mt-1">Analysis in seconds</p>
                </div>
                <div className="dashboard-card text-center">
                  <div className="text-3xl mb-2">🔒</div>
                  <h4 className="font-semibold text-white text-sm">Privacy First</h4>
                  <p className="text-xs text-slate-400 mt-1">Your data stays yours</p>
                </div>
                <div className="dashboard-card text-center">
                  <div className="text-3xl mb-2">🎯</div>
                  <h4 className="font-semibold text-white text-sm">Accurate</h4>
                  <p className="text-xs text-slate-400 mt-1">94% success rate</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="dashboard-card text-center bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-cyan-500/30 mb-16">
          <h2 className="text-3xl font-bold mb-4">Ready to Optimize Your Resume?</h2>
          <p className="text-slate-400 mb-8 max-w-2xl mx-auto">
            Start with a free analysis and see how your resume performs against thousands of job descriptions.
          </p>
          <Link to="/resume-analysis" className="btn-primary inline-block">
            Start Your Free Analysis Today
          </Link>
        </div>

        {/* Contact Section */}
        <div id="contact" className="mb-16 scroll-mt-32">
          <h2 className="text-3xl font-bold mb-8">Contact Us</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="dashboard-card bg-gradient-to-r from-indigo-500/5 to-cyan-500/5 border border-indigo-500/20">
              <h3 className="text-xl font-semibold text-white mb-6">Get In Touch</h3>
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center text-xl">📧</div>
                  <div>
                    <p className="text-sm text-slate-400">Email</p>
                    <p className="text-white font-medium">support@airesumeanalyzer.com</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center text-xl">💬</div>
                  <div>
                    <p className="text-sm text-slate-400">Live Chat</p>
                    <p className="text-white font-medium">Available 24/7 via AI Assistant</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center text-xl">🌐</div>
                  <div>
                    <p className="text-sm text-slate-400">Social</p>
                    <div className="flex gap-3 mt-1">
                      <a href="#" className="text-slate-400 hover:text-white transition">Twitter</a>
                      <a href="#" className="text-slate-400 hover:text-white transition">LinkedIn</a>
                      <a href="#" className="text-slate-400 hover:text-white transition">GitHub</a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="dashboard-card bg-gradient-to-r from-purple-500/5 to-pink-500/5 border border-purple-500/20">
              <h3 className="text-xl font-semibold text-white mb-6">Send a Message</h3>
              <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
                <div>
                  <label className="block text-sm text-slate-400 mb-1">Name</label>
                  <input type="text" placeholder="Your name" className="w-full px-4 py-2.5 rounded-lg bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 transition" />
                </div>
                <div>
                  <label className="block text-sm text-slate-400 mb-1">Email</label>
                  <input type="email" placeholder="your@email.com" className="w-full px-4 py-2.5 rounded-lg bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 transition" />
                </div>
                <div>
                  <label className="block text-sm text-slate-400 mb-1">Message</label>
                  <textarea rows="3" placeholder="How can we help?" className="w-full px-4 py-2.5 rounded-lg bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 transition resize-none"></textarea>
                </div>
                <button type="submit" className="w-full py-2.5 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold transition shadow-lg">Send Message</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
