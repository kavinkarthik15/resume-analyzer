import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { resumeAPI } from '../services/api'

/* ── Health Score Gauge ─────────────────────────────────────────────────────── */
function HealthGauge({ score, size = 160, strokeWidth = 12 }) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference

  let color, label
  if (score >= 75) { color = '#22c55e'; label = 'Healthy' }
  else if (score >= 50) { color = '#eab308'; label = 'Needs Improvement' }
  else if (score >= 30) { color = '#f97316'; label = 'Weak' }
  else { color = '#ef4444'; label = 'Critical' }

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={strokeWidth} />
          <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke={color} strokeWidth={strokeWidth}
            strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 1.2s ease-in-out', filter: `drop-shadow(0 0 8px ${color}55)` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-extrabold" style={{ color }}>{score}</span>
          <span className="text-[10px] text-slate-400 mt-0.5">/ 100</span>
        </div>
      </div>
      <p className="text-base font-bold text-white">Resume Health</p>
      <span className="px-3 py-1 rounded-full text-xs font-semibold" style={{ backgroundColor: `${color}22`, color, border: `1px solid ${color}44` }}>
        {label}
      </span>
    </div>
  )
}

/* ── Status Badge ───────────────────────────────────────────────────────────── */
function StatusBadge({ status }) {
  const styles = {
    Good: 'bg-green-500/20 text-green-400 border-green-500/30',
    Fair: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    Warning: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    Poor: 'bg-red-500/20 text-red-400 border-red-500/30',
  }
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${styles[status] || styles.Fair}`}>
      {status}
    </span>
  )
}

/* ── Category Score Card ────────────────────────────────────────────────────── */
function CategoryCard({ icon, title, status, message, details }) {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className="rounded-xl bg-white/5 border border-white/10 p-4 hover:bg-white/[0.07] transition-all">
      <div className="flex items-start justify-between gap-3 cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-start gap-3">
          <span className="text-2xl mt-0.5">{icon}</span>
          <div>
            <h4 className="font-semibold text-white">{title}</h4>
            <p className="text-sm text-slate-400 mt-0.5">{message}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <StatusBadge status={status} />
          <span className="text-slate-500 text-xs">{expanded ? '▲' : '▼'}</span>
        </div>
      </div>
      {expanded && details && (
        <div className="mt-3 pl-10 text-sm text-slate-300 space-y-1 border-t border-white/5 pt-3">
          {details}
        </div>
      )}
    </div>
  )
}

/* ── Warning Card ───────────────────────────────────────────────────────────── */
function WarningCard({ warning }) {
  const priorityStyles = {
    high: { border: 'border-red-500/30', bg: 'bg-red-500/5', badge: 'bg-red-500/20 text-red-300', dot: 'bg-red-400' },
    medium: { border: 'border-yellow-500/30', bg: 'bg-yellow-500/5', badge: 'bg-yellow-500/20 text-yellow-300', dot: 'bg-yellow-400' },
    low: { border: 'border-blue-500/30', bg: 'bg-blue-500/5', badge: 'bg-blue-500/20 text-blue-300', dot: 'bg-blue-400' },
  }
  const s = priorityStyles[warning.priority] || priorityStyles.medium

  return (
    <div className={`rounded-xl ${s.bg} border ${s.border} p-4 transition-all hover:scale-[1.01]`}>
      <div className="flex items-start gap-3">
        <span className="text-xl mt-0.5 flex-shrink-0">{warning.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="font-semibold text-white text-sm">{warning.title}</h4>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${s.badge}`}>
              {warning.priority}
            </span>
            <span className="text-[10px] text-slate-500 px-2 py-0.5 rounded-full bg-white/5">
              {warning.category}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">{warning.message}</p>
          {warning.suggestion && (
            <div className="mt-2 flex items-start gap-1.5 text-xs">
              <span className="text-green-400 flex-shrink-0">💡</span>
              <span className="text-green-300/80">{warning.suggestion}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

/* ── Main Page ──────────────────────────────────────────────────────────────── */
export default function ResumeWarnings() {
  const [formatData, setFormatData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [hasFile, setHasFile] = useState(false)

  useEffect(() => {
    const storedAnalysis = sessionStorage.getItem('resumeAnalysis')
    if (storedAnalysis) {
      const analysis = JSON.parse(storedAnalysis)
      setHasFile(true)
      setFormatData(buildFormatData(analysis))
    }
  }, [])

  function buildFormatData(analysis) {
    const issues = analysis?.parsing?.validation?.issues || []
    const warnings = issues.map((issue) => ({
      title: issue,
      priority: 'high',
      category: 'Validation',
      icon: '⚠️',
    }))

    const improvementTips = analysis?.ats_analysis?.improvement_tips || []
    improvementTips.forEach((tip) => {
      warnings.push({
        title: tip,
        priority: 'medium',
        category: 'ATS',
        icon: '💡',
      })
    })

    return {
      warnings,
      format_score: analysis?.ats_analysis?.breakdown?.format ?? 0,
      summary: analysis?.parsing?.validation?.warnings || [],
    }
  }

  async function handleFileUpload(e) {
    const f = e.target.files[0]
    if (!f) return

    setLoading(true)
    setError('')

    try {
      const response = await resumeAPI.uploadAndAnalyze(f)
      const payload = response.data
      const analysis = payload.data?.analysis || payload.data

      const reader = new FileReader()
      reader.onload = () => {
        sessionStorage.setItem('resumeFile', reader.result)
        sessionStorage.setItem('resumeFileName', f.name)
      }
      reader.readAsDataURL(f)

      sessionStorage.setItem('resumeAnalysis', JSON.stringify(analysis))
      setHasFile(true)
      setFormatData(buildFormatData(analysis))
    } catch (err) {
      const message = err.response?.data?.detail || err.message || 'Failed to check resume format.'
      setError(message)
    } finally {
      setLoading(false)
    }

    e.target.value = ''
  }

  const warnings = formatData?.warnings || []
  const warningCounts = {
    high: warnings.filter((w) => w.priority === 'high').length,
    medium: warnings.filter((w) => w.priority === 'medium').length,
    low: warnings.filter((w) => w.priority === 'low').length,
  }
  const totalWarnings = warnings.length
  const healthScore = formatData?.format_score || 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#07102a] via-[#0f2b4f] to-[#0b0620] text-white pt-24 pb-12 px-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-orange-300 to-red-300 bg-clip-text text-transparent">
            Format & ATS Warnings
          </h1>
          <p className="text-slate-400 mt-1">Review and fix issues to improve your resume quality</p>
        </div>

        {/* Loading / Error / No File states */}
        {loading && (
          <div className="rounded-2xl bg-white/5 border border-white/10 p-12 text-center">
            <div className="inline-block w-10 h-10 border-4 border-blue-400 border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-slate-300">Analyzing resume format...</p>
          </div>
        )}

        {error && (
          <div className="rounded-2xl bg-red-500/10 border border-red-500/30 p-6 mb-6">
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {!loading && !formatData && (
          <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-8 text-center">
            <p className="text-slate-300 mb-4">
              {hasFile ? 'Unable to load format data.' : 'No resume uploaded yet. Upload a resume to see format warnings.'}
            </p>
            <label className="inline-block px-6 py-3 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 font-semibold cursor-pointer hover:scale-105 transition-transform">
              Upload Resume
              <input type="file" accept=".pdf,.docx" onChange={handleFileUpload} className="hidden" />
            </label>
          </div>
        )}

        {!loading && formatData && (
          <div className="space-y-6 animate-fade-in">

            {/* ═══ TOP ROW: Health Gauge + Summary ═══ */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Health Gauge */}
              <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6 flex flex-col items-center justify-center">
                <HealthGauge score={healthScore} />
              </div>

              {/* Summary Cards */}
              <div className="lg:col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="rounded-xl bg-white/5 border border-white/10 p-5 border-l-4 border-l-red-500">
                  <div className="text-red-400 text-3xl font-bold">{warningCounts.high}</div>
                  <p className="text-slate-400 text-sm mt-1">High Priority</p>
                  <p className="text-slate-500 text-xs mt-0.5">Fix these first</p>
                </div>
                <div className="rounded-xl bg-white/5 border border-white/10 p-5 border-l-4 border-l-yellow-500">
                  <div className="text-yellow-400 text-3xl font-bold">{warningCounts.medium}</div>
                  <p className="text-slate-400 text-sm mt-1">Medium Priority</p>
                  <p className="text-slate-500 text-xs mt-0.5">Improve for better score</p>
                </div>
                <div className="rounded-xl bg-white/5 border border-white/10 p-5 border-l-4 border-l-blue-500">
                  <div className="text-blue-400 text-3xl font-bold">{warningCounts.low}</div>
                  <p className="text-slate-400 text-sm mt-1">Low Priority</p>
                  <p className="text-slate-500 text-xs mt-0.5">Nice to have</p>
                </div>

                {/* Upload another */}
                <div className="sm:col-span-3 rounded-xl bg-white/5 border border-white/10 p-4 flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-300">
                      📁 Analyzing: <span className="font-semibold text-white">{sessionStorage.getItem('resumeFileName') || 'resume'}</span>
                    </p>
                    <p className="text-xs text-slate-500 mt-0.5">{formatData.page_count} page{formatData.page_count !== 1 ? 's' : ''} • {totalWarnings} warning{totalWarnings !== 1 ? 's' : ''} found</p>
                  </div>
                  <label className="px-4 py-2 text-sm rounded-full bg-white/10 hover:bg-white/20 cursor-pointer transition font-medium">
                    Re-upload
                    <input type="file" accept=".pdf,.docx" onChange={handleFileUpload} className="hidden" />
                  </label>
                </div>
              </div>
            </div>

            {/* ═══ CATEGORY BREAKDOWN ═══ */}
            <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6">
              <h3 className="text-lg font-semibold mb-4">📋 Format Analysis Breakdown</h3>
              <div className="space-y-3">
                <CategoryCard
                  icon="📄" title="Page Length" 
                  status={formatData.length_analysis?.status}
                  message={formatData.length_analysis?.message}
                  details={<p>{formatData.page_count} page{formatData.page_count !== 1 ? 's' : ''} detected. Ideal resume length is 1-2 pages.</p>}
                />
                <CategoryCard
                  icon="📝" title="Bullet Points"
                  status={formatData.bullet_point_analysis?.status}
                  message={formatData.bullet_point_analysis?.message}
                  details={
                    <div>
                      <p>Total bullets: {formatData.bullet_point_analysis?.total_bullets || 0}</p>
                      {formatData.bullet_point_analysis?.long_bullets > 0 && <p>⚠ {formatData.bullet_point_analysis.long_bullets} too long (&gt;25 words)</p>}
                      {formatData.bullet_point_analysis?.short_bullets > 0 && <p>⚠ {formatData.bullet_point_analysis.short_bullets} too short (&lt;5 words)</p>}
                    </div>
                  }
                />
                <CategoryCard
                  icon="💪" title="Action Verbs"
                  status={formatData.action_verb_analysis?.status}
                  message={formatData.action_verb_analysis?.message}
                  details={
                    <div>
                      <p>Strong verbs: {formatData.action_verb_analysis?.strong_verb_count || 0} | Weak verbs: {formatData.action_verb_analysis?.weak_verb_count || 0}</p>
                      <p>Strength ratio: {formatData.action_verb_analysis?.strong_ratio || 0}%</p>
                      {formatData.action_verb_analysis?.weak_verbs_found?.length > 0 && (
                        <p className="mt-1">Weak verbs: {formatData.action_verb_analysis.weak_verbs_found.join(', ')}</p>
                      )}
                    </div>
                  }
                />
                <CategoryCard
                  icon="📊" title="Quantified Results"
                  status={formatData.quantified_results_analysis?.status}
                  message={formatData.quantified_results_analysis?.message}
                  details={
                    <div>
                      <p>Metrics found: {formatData.quantified_results_analysis?.metric_count || 0}</p>
                      {formatData.quantified_results_analysis?.examples?.length > 0 && (
                        <p className="mt-1">Examples: {formatData.quantified_results_analysis.examples.join(', ')}</p>
                      )}
                    </div>
                  }
                />
                {formatData.weak_wording_analysis && (
                  <CategoryCard
                    icon="⚠️" title="Weak Wording"
                    status={formatData.weak_wording_analysis?.status}
                    message={formatData.weak_wording_analysis?.message}
                    details={
                      formatData.weak_wording_analysis?.weak_phrases_found?.length > 0 ? (
                        <div className="space-y-1">
                          {formatData.weak_wording_analysis.weak_phrases_found.map((item, i) => (
                            <p key={i}>
                              <span className="text-red-300">"{item.phrase}"</span> (×{item.count}) → 
                              <span className="text-green-300 ml-1">{item.replacement}</span>
                            </p>
                          ))}
                        </div>
                      ) : <p>No weak wording detected!</p>
                    }
                  />
                )}
              </div>
            </div>

            {/* ═══ WARNINGS LIST ═══ */}
            {warnings.length > 0 && (
              <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6">
                <h3 className="text-lg font-semibold mb-4">
                  🚨 All Warnings ({totalWarnings})
                </h3>
                <div className="space-y-3">
                  {warnings.map((warning) => (
                    <WarningCard key={warning.id} warning={warning} />
                  ))}
                </div>
              </div>
            )}

            {warnings.length === 0 && (
              <div className="rounded-2xl bg-green-500/10 border border-green-500/30 p-6 text-center">
                <span className="text-4xl">🎉</span>
                <h3 className="text-xl font-bold text-green-400 mt-2">No Warnings!</h3>
                <p className="text-slate-300 mt-1">Your resume formatting looks great.</p>
              </div>
            )}

            {/* ═══ IMPROVEMENT SUGGESTIONS ═══ */}
            {formatData.overall_suggestions?.length > 0 && (
              <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6">
                <h3 className="text-lg font-semibold mb-4">💡 Improvement Suggestions</h3>
                <div className="space-y-2">
                  {formatData.overall_suggestions.map((suggestion, index) => (
                    <div key={index} className="flex items-start gap-2 py-1.5">
                      <span className={`flex-shrink-0 mt-0.5 ${suggestion.startsWith('PRIORITY') ? 'text-red-400' : 'text-blue-400'}`}>
                        {suggestion.startsWith('PRIORITY') ? '🔴' : '→'}
                      </span>
                      <p className="text-sm text-slate-300">{suggestion}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ═══ CTA ═══ */}
            <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-8 text-center">
              <h3 className="text-2xl font-bold mb-3">Ready to Fix Your Resume?</h3>
              <p className="text-slate-400 mb-6">Use our AI Resume Rewriter to automatically improve formatting and content</p>
              <div className="flex gap-3 justify-center flex-wrap">
                <Link to="/resume-rewriter" className="px-6 py-3 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 font-semibold hover:scale-105 transition-transform">
                  Go to Resume Rewriter
                </Link>
                <Link to="/results" className="px-6 py-3 rounded-full border border-slate-500 hover:bg-white/10 font-semibold transition">
                  View Analysis Results
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
