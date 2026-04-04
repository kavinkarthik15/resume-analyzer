import React, { useState, useEffect } from 'react'
import { API_BASE_URL } from '../services/api'

/* ── Match Gauge ────────────────────────────────────────────────────────────── */
function MatchGauge({ score, size = 170, strokeWidth = 13 }) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference

  let color, label
  if (score >= 75) { color = '#22c55e'; label = 'Excellent Match' }
  else if (score >= 55) { color = '#3b82f6'; label = 'Good Match' }
  else if (score >= 35) { color = '#eab308'; label = 'Partial Match' }
  else { color = '#ef4444'; label = 'Low Match' }

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={strokeWidth} />
          <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke={color} strokeWidth={strokeWidth}
            strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 1.2s ease-in-out', filter: `drop-shadow(0 0 8px ${color}55)` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-extrabold" style={{ color }}>{Math.round(score)}</span>
          <span className="text-xs text-slate-400">%</span>
        </div>
      </div>
      <p className="text-base font-bold text-white">JD Match Score</p>
      <span className="px-3 py-1 rounded-full text-xs font-semibold"
        style={{ backgroundColor: `${color}22`, color, border: `1px solid ${color}44` }}>
        {label}
      </span>
    </div>
  )
}

/* ── Skill Gap Bar ──────────────────────────────────────────────────────────── */
function SkillGapBar({ matched, total }) {
  const pct = total > 0 ? Math.round((matched / total) * 100) : 0
  let barColor
  if (pct >= 70) barColor = 'from-green-400 to-emerald-500'
  else if (pct >= 40) barColor = 'from-yellow-400 to-orange-500'
  else barColor = 'from-red-400 to-pink-500'

  return (
    <div>
      <div className="flex justify-between text-sm mb-1.5">
        <span className="text-slate-300">Skill Coverage</span>
        <span className="text-slate-400 font-mono">{matched}/{total} skills ({pct}%)</span>
      </div>
      <div className="h-3 rounded-full bg-white/10 overflow-hidden">
        <div className={`h-full rounded-full bg-gradient-to-r ${barColor}`}
          style={{ width: `${pct}%`, transition: 'width 1s ease-in-out' }} />
      </div>
    </div>
  )
}

/* ── Main Page ──────────────────────────────────────────────────────────────── */
export default function JDComparison() {
  const [jdText, setJdText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const apiBaseUrl = API_BASE_URL

  // Get resume data from session
  function getResumeData() {
    const cached = sessionStorage.getItem('resumeAnalysis')
    if (cached) {
      try { return JSON.parse(cached) } catch { return null }
    }
    return null
  }

  const resumeData = getResumeData()

  async function handleAnalyze() {
    if (!jdText.trim()) return

    // We need resume text. If we have the stored file, extract it; otherwise use skills from analysis.
    const storedFile = sessionStorage.getItem('resumeFile')
    const analysis = getResumeData()

    if (!analysis && !storedFile) {
      setError('No resume data found. Please upload a resume from the home page first.')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      // Build resume text from analysis data or use a reconstructed version
      let resumeText = ''
      if (storedFile) {
        // Extract text from file via a quick analyze call or use cached
        // For now, reconstruct from analysis data
        if (analysis) {
          const skills = analysis.skills_found || []
          const sections = Object.entries(analysis.sections || {})
            .filter(([, v]) => v === 'Found')
            .map(([k]) => k)
          resumeText = `Skills: ${skills.join(', ')}. Sections: ${sections.join(', ')}.`
          // Add any other text we can reconstruct
          if (analysis.suggestions) resumeText += ' ' + analysis.suggestions.join('. ')
        }
      }

      // If we still have no text, build from skills
      if (!resumeText && analysis) {
        resumeText = (analysis.skills_found || []).join(', ')
      }

      const skills = analysis?.skills_found || []

      const response = await fetch(`${apiBaseUrl}/compare-jd`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: resumeText,
          jd_text: jdText,
          skills: skills,
        }),
      })

      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload?.detail || 'JD comparison failed.')
      }

      setResult(payload.data)
    } catch (err) {
      setError(err.message || 'Failed to compare with job description.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#07102a] via-[#0f2b4f] to-[#0b0620] text-white pt-24 pb-12 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-cyan-300 to-blue-300 bg-clip-text text-transparent">
            Job Description Matching
          </h1>
          <p className="text-slate-400 mt-1">Paste a job description to see how well your resume aligns with the role</p>
        </div>

        {!resumeData && (
          <div className="rounded-2xl bg-yellow-500/10 border border-yellow-500/30 p-4 mb-6">
            <p className="text-yellow-300 text-sm">⚠️ No resume analysis found. Upload a resume from the home page first for best results.</p>
          </div>
        )}

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* ═══ LEFT: JD Input ═══ */}
          <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6">
            <label className="block text-lg font-semibold mb-3 text-white">📋 Paste Job Description</label>
            <textarea
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              placeholder="Paste the full job description here...&#10;&#10;We'll analyze your resume against this role's requirements, highlighting matched skills, missing keywords, and giving you a match score."
              className="w-full min-h-[340px] bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white text-sm placeholder-slate-500 focus:outline-none focus:bg-black/30 focus:border-blue-500/50 transition-all resize-y"
            />
            <div className="flex items-center justify-between mt-4">
              <span className="text-xs text-slate-500">
                {jdText.trim().split(/\s+/).filter(Boolean).length} words
              </span>
              <div className="flex gap-2">
                {jdText && (
                  <button onClick={() => { setJdText(''); setResult(null); setError('') }}
                    className="px-4 py-2 text-sm rounded-full border border-slate-600 hover:bg-white/10 transition">
                    Clear
                  </button>
                )}
                <button
                  onClick={handleAnalyze}
                  disabled={!jdText.trim() || loading}
                  className="px-6 py-2 text-sm font-semibold rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:scale-105 transition-transform disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                      Analyzing...
                    </span>
                  ) : '🎯 Compare Match'}
                </button>
              </div>
            </div>
            {error && <p className="mt-3 text-sm text-red-300">{error}</p>}
          </div>

          {/* ═══ RIGHT: Results ═══ */}
          <div className="space-y-6">
            {result ? (
              <>
                {/* Match Gauge + Skill Gap Bar */}
                <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6">
                  <div className="flex flex-col sm:flex-row items-center gap-6">
                    <MatchGauge score={result.jd_match_score} />
                    <div className="flex-1 w-full space-y-4">
                      <SkillGapBar matched={result.matched_count} total={result.total_jd_skills} />
                      <div className="grid grid-cols-2 gap-3">
                        <div className="rounded-lg bg-green-500/10 border border-green-500/20 p-3 text-center">
                          <div className="text-2xl font-bold text-green-400">{result.matched_count}</div>
                          <p className="text-xs text-slate-400 mt-0.5">Matched Skills</p>
                        </div>
                        <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3 text-center">
                          <div className="text-2xl font-bold text-red-400">{result.missing_skills?.length || 0}</div>
                          <p className="text-xs text-slate-400 mt-0.5">Missing Skills</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Matched Skills */}
                {result.matched_skills?.length > 0 && (
                  <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6">
                    <h3 className="text-base font-semibold mb-3 flex items-center gap-2">
                      ✅ Matched Skills
                      <span className="text-xs text-slate-400 font-normal">({result.matched_skills.length})</span>
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {result.matched_skills.map((skill) => (
                        <span key={skill} className="px-3 py-1.5 rounded-lg bg-green-500/15 border border-green-400/25 text-green-300 text-sm font-medium flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Missing Skills */}
                {result.missing_skills?.length > 0 && (
                  <div className="rounded-2xl bg-white/5 border border-red-500/20 backdrop-blur-xl p-6">
                    <h3 className="text-base font-semibold mb-3 flex items-center gap-2">
                      ❌ Missing Keywords
                      <span className="text-xs text-slate-400 font-normal">({result.missing_skills.length})</span>
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {result.missing_skills.map((skill) => (
                        <span key={skill} className="px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-400/20 text-red-300 text-sm font-medium flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Suggestions */}
                {result.suggestions?.length > 0 && (
                  <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6">
                    <h3 className="text-base font-semibold mb-3">💡 Suggestions</h3>
                    <div className="space-y-2">
                      {result.suggestions.map((s, i) => (
                        <div key={i} className="flex items-start gap-2 py-1">
                          <span className="text-blue-400 flex-shrink-0 mt-0.5">→</span>
                          <p className="text-sm text-slate-300">{s}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6 flex flex-col items-center justify-center min-h-[400px] text-center">
                <div className="text-5xl mb-4">🎯</div>
                <p className="text-slate-300 mb-2 font-medium">Paste a job description to get started</p>
                <p className="text-slate-500 text-sm max-w-xs">We'll compare your resume skills against the JD requirements and calculate a match score</p>
              </div>
            )}
          </div>
        </div>

        {/* ═══ Tips Section ═══ */}
        <div className="mt-8 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6">
          <h3 className="text-lg font-semibold mb-5">💡 Tips to Improve Your Match Score</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-cyan-500/5 border border-cyan-500/20">
              <p className="font-semibold text-cyan-400 mb-2">🔑 Add Missing Keywords</p>
              <p className="text-sm text-slate-400">Include technical skills and tools mentioned in the job description naturally in your resume.</p>
            </div>
            <div className="p-4 rounded-xl bg-purple-500/5 border border-purple-500/20">
              <p className="font-semibold text-purple-400 mb-2">✏️ Tailor Your Bullets</p>
              <p className="text-sm text-slate-400">Rewrite experience bullets to mirror the language and requirements from the JD.</p>
            </div>
            <div className="p-4 rounded-xl bg-blue-500/5 border border-blue-500/20">
              <p className="font-semibold text-blue-400 mb-2">📊 Quantify Results</p>
              <p className="text-sm text-slate-400">Add metrics and numbers that demonstrate impact relevant to the role requirements.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
