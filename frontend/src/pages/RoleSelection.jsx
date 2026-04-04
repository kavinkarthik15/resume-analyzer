import React, { useState, useEffect } from 'react'
import { API_BASE_URL } from '../services/api'

const API = API_BASE_URL

/* ─── Circular Readiness Gauge ─── */
function ReadinessGauge({ score }) {
  const r = 45, c = 2 * Math.PI * r
  const color = score >= 80 ? '#22c55e' : score >= 60 ? '#eab308' : score >= 40 ? '#f97316' : '#ef4444'
  return (
    <div className="relative w-48 h-48 flex items-center justify-center mx-auto">
      <svg className="absolute w-full h-full" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="8" />
        <circle cx="50" cy="50" r={r} fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={`${(score / 100) * c} ${c}`} strokeLinecap="round"
          transform="rotate(-90 50 50)" style={{ transition: 'stroke-dasharray 0.8s ease-out' }} />
      </svg>
      <div className="text-center">
        <div className="text-5xl font-bold" style={{ color }}>{score}%</div>
        <p className="text-slate-400 text-xs mt-1">Readiness</p>
      </div>
    </div>
  )
}

/* ─── Skill Bar ─── */
function SkillBar({ label, matchPct }) {
  const color = matchPct >= 70 ? 'bg-green-500' : matchPct >= 40 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-slate-300">{label}</span>
        <span className="text-slate-400">{matchPct}%</span>
      </div>
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${matchPct}%`, transition: 'width 0.6s ease-out' }} />
      </div>
    </div>
  )
}

/* ─── Role Emoji Map ─── */
const ROLE_EMOJI = {
  'Data Scientist': '📊', 'Web Developer': '🌐', 'AI Engineer': '🤖',
  'Backend Developer': '⚙️', 'Frontend Developer': '🎨', 'Full Stack Developer': '🚀',
  'DevOps Engineer': '🔧', 'Mobile Developer': '📱', 'Cloud Architect': '☁️',
  'Machine Learning Engineer': '🧠', 'QA Engineer': '🧪', 'Product Manager': '📋',
}

export default function RoleSelection() {
  const [roles, setRoles] = useState([])
  const [selectedRole, setSelectedRole] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [rolesLoading, setRolesLoading] = useState(true)
  const [error, setError] = useState('')

  // Load available roles on mount
  useEffect(() => {
    fetch(`${API}/available-roles`)
      .then(r => r.json())
      .then(data => {
        if (data.success && data.roles) {
          setRoles(data.roles)
          setSelectedRole(data.roles[0] || '')
        }
      })
      .catch(() => setError('Failed to load roles'))
      .finally(() => setRolesLoading(false))
  }, [])

  // Get user skills from sessionStorage (set during analysis)
  const getUserSkills = () => {
    try {
      const stored = sessionStorage.getItem('resumeAnalysis')
      if (stored) {
        const parsed = JSON.parse(stored)
        return parsed.skills_found || parsed.data?.skills_found || []
      }
    } catch { }
    return []
  }

  const handleAnalyze = async () => {
    if (!selectedRole) return
    const skills = getUserSkills()
    if (skills.length === 0) {
      setError('No resume skills found. Please analyze your resume first from the Home page.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${API}/role-recommendation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills, role: selectedRole }),
      })
      const data = await res.json()
      if (data.success) setResult(data.data)
      else setError(data.detail || 'Analysis failed')
    } catch {
      setError('Connection failed. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  const getStatusLabel = (score) => {
    if (score >= 80) return { text: 'Highly Qualified', cls: 'bg-green-500/20 text-green-400' }
    if (score >= 60) return { text: 'Good – Some Gaps', cls: 'bg-yellow-500/20 text-yellow-400' }
    if (score >= 40) return { text: 'Developing', cls: 'bg-orange-500/20 text-orange-400' }
    return { text: 'Needs Upskilling', cls: 'bg-red-500/20 text-red-400' }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 pt-32 pb-12 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold mb-2">Role Readiness Assessment</h1>
          <p className="text-slate-400">Select a target role to see how your skills match up</p>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-center">{error}</div>
        )}

        {/* Role Grid */}
        {rolesLoading ? (
          <div className="text-center py-12 text-slate-400">Loading roles…</div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 mb-8">
            {roles.map((role) => (
              <button key={role} onClick={() => { setSelectedRole(role); setResult(null); }}
                className={`dashboard-card p-3 text-center transition-all duration-200
                  ${selectedRole === role
                    ? 'ring-2 ring-cyan-400 bg-gradient-to-br from-cyan-500/20 to-blue-500/20'
                    : 'hover:bg-white/10'}`}>
                <div className="text-3xl mb-1">{ROLE_EMOJI[role] || '💼'}</div>
                <p className="text-xs font-semibold text-white leading-tight">{role}</p>
              </button>
            ))}
          </div>
        )}

        {/* Analyze Button */}
        <div className="flex justify-center mb-10">
          <button onClick={handleAnalyze} disabled={loading || !selectedRole}
            className="btn-primary px-10 py-3 text-lg disabled:opacity-50 disabled:cursor-not-allowed">
            {loading ? 'Analyzing…' : `Check Readiness for ${selectedRole || '…'}`}
          </button>
        </div>

        {/* ── Results ── */}
        {result && (
          <div className="space-y-8 animate-fade-in">
            {/* Top Row: Gauge + Summary */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Gauge */}
              <div className="dashboard-card flex flex-col items-center justify-center">
                <ReadinessGauge score={result.readiness_score} />
                <div className="mt-4 text-center">
                  {(() => { const s = getStatusLabel(result.readiness_score); return (
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${s.cls}`}>{s.text}</span>
                  ) })()}
                  <p className="text-slate-400 text-xs mt-2">{result.readiness_level}</p>
                </div>
              </div>

              {/* Required Skills */}
              <div className="dashboard-card">
                <h3 className="text-lg font-bold mb-1">Required Skills</h3>
                <SkillBar label="Coverage" matchPct={result.required_skills.match_percentage} />
                <p className="text-xs text-slate-500 mb-3">{result.required_skills.matched.length}/{result.required_skills.total} matched</p>
                <div className="flex flex-wrap gap-2 mb-4">
                  {result.required_skills.matched.map(s => (
                    <span key={s} className="px-2 py-1 text-xs rounded-full bg-green-500/20 text-green-400 border border-green-500/30">{s}</span>
                  ))}
                </div>
                {result.required_skills.missing.length > 0 && (
                  <>
                    <p className="text-xs text-slate-500 mb-2">Missing ({result.required_skills.missing.length})</p>
                    <div className="flex flex-wrap gap-2">
                      {result.required_skills.missing.map(s => (
                        <span key={s} className="px-2 py-1 text-xs rounded-full bg-red-500/20 text-red-400 border border-red-500/30">{s}</span>
                      ))}
                    </div>
                  </>
                )}
              </div>

              {/* Preferred Skills */}
              <div className="dashboard-card">
                <h3 className="text-lg font-bold mb-1">Preferred Skills</h3>
                <SkillBar label="Coverage" matchPct={result.preferred_skills.match_percentage} />
                <p className="text-xs text-slate-500 mb-3">{result.preferred_skills.matched.length}/{result.preferred_skills.total} matched</p>
                <div className="flex flex-wrap gap-2 mb-4">
                  {result.preferred_skills.matched.map(s => (
                    <span key={s} className="px-2 py-1 text-xs rounded-full bg-green-500/20 text-green-400 border border-green-500/30">{s}</span>
                  ))}
                </div>
                {result.preferred_skills.missing.length > 0 && (
                  <>
                    <p className="text-xs text-slate-500 mb-2">Nice to Have ({result.preferred_skills.missing.length})</p>
                    <div className="flex flex-wrap gap-2">
                      {result.preferred_skills.missing.map(s => (
                        <span key={s} className="px-2 py-1 text-xs rounded-full bg-orange-500/20 text-orange-400 border border-orange-500/30">{s}</span>
                      ))}
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Priority Skills */}
            {(result.top_priority_skills?.length > 0 || result.nice_to_have_skills?.length > 0) && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {result.top_priority_skills?.length > 0 && (
                  <div className="dashboard-card">
                    <h3 className="text-lg font-bold mb-4 text-red-400">🎯 Top Priority Skills</h3>
                    <div className="space-y-2">
                      {result.top_priority_skills.map((s, i) => (
                        <div key={s} className="flex items-center gap-3 p-2 rounded-lg bg-red-500/10 border border-red-500/20">
                          <span className="w-6 h-6 rounded-full bg-red-500/30 text-red-400 text-xs flex items-center justify-center font-bold">{i + 1}</span>
                          <span className="text-white text-sm">{s}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {result.nice_to_have_skills?.length > 0 && (
                  <div className="dashboard-card">
                    <h3 className="text-lg font-bold mb-4 text-cyan-400">💡 Nice to Have</h3>
                    <div className="space-y-2">
                      {result.nice_to_have_skills.map((s, i) => (
                        <div key={s} className="flex items-center gap-3 p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
                          <span className="w-6 h-6 rounded-full bg-cyan-500/30 text-cyan-400 text-xs flex items-center justify-center font-bold">{i + 1}</span>
                          <span className="text-white text-sm">{s}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Suggestions */}
            {result.suggestions?.length > 0 && (
              <div className="dashboard-card">
                <h3 className="text-lg font-bold mb-4">📝 Personalized Suggestions</h3>
                <div className="space-y-3">
                  {result.suggestions.map((s, i) => (
                    <div key={i} className="flex gap-3 p-3 rounded-lg bg-white/5 border border-white/10">
                      <span className="text-cyan-400 mt-0.5">→</span>
                      <p className="text-slate-300 text-sm">{s}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
