import React, { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

/* ── Circular Gauge Component ───────────────────────────────────────────────── */
function CircularGauge({ score, size = 180, strokeWidth = 14 }) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference

  // Color based on score
  let color, glowColor, label
  if (score >= 75) {
    color = '#22c55e'; glowColor = 'rgba(34,197,94,0.35)'; label = 'Excellent'
  } else if (score >= 50) {
    color = '#eab308'; glowColor = 'rgba(234,179,8,0.35)'; label = 'Good'
  } else if (score >= 30) {
    color = '#f97316'; glowColor = 'rgba(249,115,22,0.35)'; label = 'Needs Work'
  } else {
    color = '#ef4444'; glowColor = 'rgba(239,68,68,0.35)'; label = 'Poor'
  }

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background circle */}
          <circle
            cx={size / 2} cy={size / 2} r={radius}
            fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={strokeWidth}
          />
          {/* Score arc */}
          <circle
            cx={size / 2} cy={size / 2} r={radius}
            fill="none" stroke={color} strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{
              transition: 'stroke-dashoffset 1.2s ease-in-out',
              filter: `drop-shadow(0 0 8px ${glowColor})`,
            }}
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-extrabold" style={{ color }}>{score}</span>
          <span className="text-xs text-slate-400 mt-0.5">/ 100</span>
        </div>
      </div>
      <div className="text-center">
        <p className="text-lg font-bold text-white">Resume Strength</p>
        <span
          className="inline-block mt-1 px-3 py-1 rounded-full text-xs font-semibold"
          style={{ backgroundColor: `${color}22`, color, border: `1px solid ${color}44` }}
        >
          {label}
        </span>
      </div>
    </div>
  )
}

/* ── Skill Card Component ───────────────────────────────────────────────────── */
function SkillCard({ skill, frequency }) {
  return (
    <div className="group relative px-3 py-2 rounded-lg bg-gradient-to-br from-blue-500/15 to-purple-500/15 border border-blue-400/20 hover:border-blue-400/50 hover:from-blue-500/25 hover:to-purple-500/25 transition-all duration-300 cursor-default">
      <div className="flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-blue-400 flex-shrink-0" />
        <span className="text-sm font-medium text-white">{skill}</span>
        {frequency > 1 && (
          <span className="ml-auto text-[10px] px-1.5 py-0.5 rounded-full bg-blue-500/30 text-blue-300 font-mono">
            ×{frequency}
          </span>
        )}
      </div>
    </div>
  )
}

/* ── Missing Skill Chip ─────────────────────────────────────────────────────── */
function MissingSkillChip({ skill }) {
  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-400/20 text-red-300 text-sm">
      <span className="w-1.5 h-1.5 rounded-full bg-red-400 flex-shrink-0" />
      {skill}
    </span>
  )
}

/* ── Category Progress Bar ──────────────────────────────────────────────────── */
function CategoryProgress({ category, percentage }) {
  let barColor
  if (percentage >= 60) barColor = 'from-green-400 to-emerald-500'
  else if (percentage >= 30) barColor = 'from-yellow-400 to-orange-500'
  else barColor = 'from-red-400 to-pink-500'

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-slate-300">{category}</span>
        <span className="text-slate-400 font-mono">{percentage}%</span>
      </div>
      <div className="h-2 rounded-full bg-white/10 overflow-hidden">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${barColor}`}
          style={{ width: `${percentage}%`, transition: 'width 1s ease-in-out' }}
        />
      </div>
    </div>
  )
}

/* ── Main Results Page ──────────────────────────────────────────────────────── */
export default function Results() {
  const location = useLocation()
  const navigate = useNavigate()
  const [shareMessage, setShareMessage] = useState('')

  // Get analysis result from localStorage (set by Upload page)
  const cachedResult = localStorage.getItem('analysisResult')
  let analysisResult = null

  if (cachedResult) {
    try {
      analysisResult = JSON.parse(cachedResult)
    } catch (e) {
      console.error('Failed to parse analysis result:', e)
    }
  }

  // Fallback to location state
  if (!analysisResult) {
    analysisResult = location.state?.analysisResult || null
  }

  const atsScore = analysisResult?.ats_analysis?.score || analysisResult?.ats_analysis?.breakdown?.total || 0
  const mlPrediction = analysisResult?.ml_prediction || null
  const parsing = analysisResult?.parsing || {}
  const skills = parsing.skills || []
  const skillCategories = parsing.skill_categories || {}
  const intelligentSummary = analysisResult?.intelligent_summary || {
    summary: '',
    priority_actions: analysisResult?.ats_analysis?.improvement_tips || []
  }

  function reportText() {
    if (!analysisResult) return 'No analysis found.'

    const lines = [
      `ATS SCORE: ${atsScore}/100`,
      '',
      'Skills Found:',
      skills.length ? skills.join(', ') : 'No skills found',
      '',
      'ML Prediction:',
      mlPrediction ? `Probability: ${Math.round(mlPrediction.probability * 100)}%` : 'Not available',
      mlPrediction ? `Decision: ${mlPrediction.decision}` : '',
      '',
      'Summary:',
      intelligentSummary.summary || 'Analysis completed',
      '',
      'Priority Actions:',
      ...(intelligentSummary.priority_actions || []).map(action => `- ${action}`)
    ]

    return lines.join('\n')
  }

  async function handleShareReport() {
    try {
      await navigator.clipboard.writeText(reportText())
      setShareMessage('Report copied to clipboard.')
    } catch {
      setShareMessage('Clipboard access failed. Please copy manually.')
    }

    setTimeout(() => setShareMessage(''), 2500)
  }

  function handlePrintPdf() {
    window.print()
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#07102a] via-[#0f2b4f] to-[#0b0620] text-white pt-20 px-6 pb-10">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">
            Resume Analysis Results
          </h1>
        </div>

        {!analysisResult ? (
          <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6">
            <p className="text-slate-200">No analysis data found. Please upload a resume from the home page.</p>
            <Link to="/resume-analysis" className="btn primary mt-4">Upload Resume</Link>
          </div>
        ) : (
          <div className="results-content">
            {/* ═══ INTELLIGENT SUMMARY ═══ */}
            {(intelligentSummary.summary || (intelligentSummary.priority_actions && intelligentSummary.priority_actions.length > 0)) && (
              <div className="rounded-2xl bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-cyan-500/10 border border-emerald-400/30 backdrop-blur-xl p-6">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-r from-emerald-500 to-teal-500 flex items-center justify-center">
                      <span className="text-white text-xl">🧠</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold mb-3 text-emerald-400">AI Summary & Insights</h3>
                    {intelligentSummary.summary && (
                      <p className="text-slate-200 mb-4 leading-relaxed">{intelligentSummary.summary}</p>
                    )}

                    {intelligentSummary.priority_actions && intelligentSummary.priority_actions.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-emerald-300 mb-3">🎯 Priority Actions</h4>
                        <ul className="space-y-2">
                          {intelligentSummary.priority_actions.map((action, index) => (
                            <li key={index} className="flex items-start gap-3 text-sm">
                              <span className="flex-shrink-0 w-5 h-5 rounded-full bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center text-xs text-emerald-300 font-bold">
                                {index + 1}
                              </span>
                              <span className="text-slate-300">{action}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {intelligentSummary.confidence_level && (
                      <div className="mt-4 pt-4 border-t border-emerald-400/20">
                        <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-semibold ${
                          intelligentSummary.confidence_level === 'High'
                            ? 'bg-green-500/20 text-green-400 border border-green-500/40'
                            : intelligentSummary.confidence_level === 'Medium'
                            ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/40'
                            : 'bg-red-500/20 text-red-400 border border-red-500/40'
                        }`}>
                          <span>Confidence:</span>
                          <span>{intelligentSummary.confidence_level}</span>
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* ═══ ATS SCORE GAUGE ═══ */}
            <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6">
              <div className="flex flex-col lg:flex-row items-center gap-8">
                <CircularGauge score={atsScore} />
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-4">📊 ATS Compatibility Score</h3>
                  <p className="text-slate-300 mb-4">
                    Your resume's compatibility with Applicant Tracking Systems.
                    Higher scores indicate better chances of passing automated screening.
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <CategoryProgress category="Skills & Keywords" percentage={75} />
                    <CategoryProgress category="Format & Structure" percentage={80} />
                    <CategoryProgress category="Content Quality" percentage={70} />
                    <CategoryProgress category="Length & Readability" percentage={65} />
                  </div>
                </div>
              </div>
            </div>

            {/* ═══ ML SHORTLIST PREDICTION ═══ */}
            {mlPrediction && (
              <div className="rounded-2xl bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10 border border-purple-400/30 backdrop-blur-xl p-6">
                <div className="flex flex-col sm:flex-row items-center gap-6">
                  {/* Probability Circle */}
                  <div className="relative w-28 h-28 flex-shrink-0">
                    <svg width="112" height="112" className="transform -rotate-90">
                      <circle cx="56" cy="56" r="48" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="10" />
                      <circle
                        cx="56" cy="56" r="48" fill="none"
                        stroke={mlPrediction.decision === 'Shortlisted' ? '#22c55e' : '#ef4444'}
                        strokeWidth="10" strokeLinecap="round"
                        strokeDasharray={2 * Math.PI * 48}
                        strokeDashoffset={2 * Math.PI * 48 * (1 - mlPrediction.probability)}
                        style={{ transition: 'stroke-dashoffset 1.2s ease-in-out', filter: `drop-shadow(0 0 8px ${mlPrediction.decision === 'Shortlisted' ? 'rgba(34,197,94,0.4)' : 'rgba(239,68,68,0.4)'})` }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-2xl font-extrabold text-white">{Math.round(mlPrediction.probability * 100)}%</span>
                    </div>
                  </div>

                  {/* Info */}
                  <div className="flex-1 text-center sm:text-left">
                    <h3 className="text-lg font-semibold flex items-center gap-2 justify-center sm:justify-start">
                      🤖 ML Shortlist Prediction
                    </h3>
                    <p className="text-slate-400 text-sm mt-1">AI model prediction of your shortlisting chances</p>
                    <div className="mt-3 flex items-center gap-3 justify-center sm:justify-start">
                      <span className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-bold ${
                        mlPrediction.decision === 'Shortlisted'
                          ? 'bg-green-500/20 text-green-400 border border-green-500/40'
                          : 'bg-red-500/20 text-red-400 border border-red-500/40'
                      }`}>
                        {mlPrediction.decision === 'Shortlisted' ? '✅' : '❌'}
                        {mlPrediction.decision}
                      </span>
                      <span className="text-xs text-slate-500">
                        Confidence: {mlPrediction.confidence || 'Medium'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ═══ SKILLS ANALYSIS ═══ */}
            <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6">
              <h3 className="text-xl font-bold mb-4">🛠️ Skills Analysis</h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-3 text-green-400">✅ Skills Found ({skills.length})</h4>
                  <div className="flex flex-wrap gap-2">
                    {skills.slice(0, 10).map((skill, index) => (
                      <SkillCard key={index} skill={skill} frequency={1} />
                    ))}
                    {skills.length > 10 && (
                      <span className="text-xs text-slate-500">+{skills.length - 10} more</span>
                    )}
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold mb-3 text-red-400">❌ Missing Critical Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    <MissingSkillChip skill="SQL" />
                    <MissingSkillChip skill="Docker" />
                    <MissingSkillChip skill="AWS" />
                    <MissingSkillChip skill="React" />
                  </div>
                </div>
              </div>
            </div>

            {/* ═══ IMPROVEMENT SUGGESTIONS ═══ */}
            <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6">
              <h3 className="text-xl font-bold mb-4">💡 Improvement Suggestions</h3>
              <div className="space-y-3">
                <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-400/20">
                  <h4 className="font-semibold text-blue-400 mb-2">🔑 Add Missing Skills</h4>
                  <p className="text-sm text-slate-300">Include SQL, Docker, and cloud technologies that are commonly required</p>
                </div>
                <div className="p-4 rounded-lg bg-green-500/10 border border-green-400/20">
                  <h4 className="font-semibold text-green-400 mb-2">📊 Quantify Achievements</h4>
                  <p className="text-sm text-slate-300">Add specific metrics and numbers to demonstrate impact</p>
                </div>
                <div className="p-4 rounded-lg bg-purple-500/10 border border-purple-400/20">
                  <h4 className="font-semibold text-purple-400 mb-2">🎯 Tailor Keywords</h4>
                  <p className="text-sm text-slate-300">Use industry-specific keywords that match job descriptions</p>
                </div>
              </div>
            </div>

            {/* ═══ ACTION BUTTONS ═══ */}
            <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6">
              <h3 className="text-xl font-bold mb-4">🚀 Next Steps</h3>
              <div className="flex flex-wrap gap-3">
                <Link to="/chat-assistant" className="btn primary">
                  💬 Chat with AI Assistant
                </Link>
                <Link to="/resume-rewriter" className="btn secondary">
                  ✏️ Rewrite Bullet Points
                </Link>
                <Link to="/jd-comparison" className="btn secondary">
                  🎯 Compare with Job Description
                </Link>
                <button onClick={handleShareReport} className="btn outline">
                  📤 Share Report
                </button>
              </div>
              {shareMessage && (
                <p className="text-green-400 text-sm mt-3">{shareMessage}</p>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
