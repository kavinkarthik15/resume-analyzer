import React from 'react'
import { Link, useLocation } from 'react-router-dom'

function getScoreColor(score) {
  if (score >= 75) return '#22c55e'
  if (score >= 50) return '#f59e0b'
  return '#ef4444'
}

function getScoreBarColor(score) {
  if (score >= 75) return 'linear-gradient(90deg, #22c55e, #16a34a)'
  if (score >= 50) return 'linear-gradient(90deg, #f59e0b, #ea580c)'
  return 'linear-gradient(90deg, #ef4444, #dc2626)'
}

function SectionCard({ title, children, tone = 'default' }) {
  const toneClasses =
    tone === 'success'
      ? 'border-emerald-400/20 bg-emerald-500/10'
      : tone === 'danger'
      ? 'border-red-400/20 bg-red-500/10'
      : tone === 'accent'
      ? 'border-cyan-400/20 bg-cyan-500/10'
      : 'border-white/10 bg-white/5'

  return (
    <div className={`rounded-2xl border backdrop-blur-xl p-6 ${toneClasses}`}>
      <h3 className="text-lg font-bold mb-4 text-white">{title}</h3>
      {children}
    </div>
  )
}

export default function Results() {
  const location = useLocation()

  const cachedResult = localStorage.getItem('analysisResult')
  let analysisResult = null

  if (cachedResult) {
    try {
      analysisResult = JSON.parse(cachedResult)
    } catch (error) {
      console.error('Failed to parse analysis result:', error)
    }
  }

  if (!analysisResult) {
    analysisResult = location.state?.analysisResult || null
  }

  const matchScore = analysisResult?.match_score ?? analysisResult?.ats_analysis?.score ?? 0
  const confidence = analysisResult?.confidence || 'Low'
  const verdict = analysisResult?.verdict || 'Low Match'
  const jobDescriptionProvided = analysisResult?.job_description_provided ?? false
  const matchedSkills = analysisResult?.matched_skills || []
  const missingSkills = analysisResult?.missing_skills || analysisResult?.ats_analysis?.missing_skills || []
  const suggestions = analysisResult?.suggestions || analysisResult?.ats_analysis?.improvement_tips || []
  const scoreColor = getScoreColor(matchScore)
  const scoreBarColor = getScoreBarColor(matchScore)

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#07102a] via-[#0f2b4f] to-[#0b0620] text-white pt-20 px-6 pb-10">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">
            Job Match Analysis
          </h1>
          <p className="mt-3 text-slate-400 max-w-2xl">
            Review how closely your resume aligns with the job description and where to improve next.
          </p>
        </div>

        {!analysisResult ? (
          <div className="rounded-2xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-400/30 backdrop-blur-xl p-8 text-center">
            <div className="text-5xl mb-4">📄</div>
            <p className="text-slate-300 text-lg mb-2">No resume uploaded yet</p>
            <p className="text-slate-400 mb-6">Upload your resume and paste a job description to get a match analysis.</p>
            <Link to="/resume-analysis" className="btn primary">Upload Your Resume</Link>
          </div>
        ) : (
          <div className="space-y-6">
            <SectionCard title="Match Overview" tone="accent">
              <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
                <div>
                  <h2 className="text-4xl sm:text-5xl font-extrabold" style={{ color: scoreColor }}>
                    Match Score: {matchScore}%
                  </h2>
                  <h3 className="mt-2 text-2xl font-bold text-white">{verdict}</h3>
                  <p className="mt-2 text-slate-300">
                    Confidence: <span className="font-semibold text-white">{confidence}</span>
                  </p>
                </div>
                <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
                  Higher scores mean stronger alignment between your resume and the job description.
                </div>
              </div>

              <div className="mt-6">
                <div className="h-3 w-full rounded-full bg-white/10 overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{ width: `${matchScore}%`, background: scoreBarColor }}
                  />
                </div>
              </div>
            </SectionCard>

            {!jobDescriptionProvided && (
              <SectionCard title="Job Description Needed" tone="accent">
                <p className="text-slate-200">
                  Upload a job description to get a personalized match analysis.
                </p>
              </SectionCard>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SectionCard title="Matched Skills" tone="success">
                {matchedSkills.length > 0 ? (
                  <ul className="space-y-3">
                    {matchedSkills.map((skill, index) => (
                      <li key={index} className="flex items-center gap-3 text-emerald-200">
                        <span className="text-emerald-400 font-bold">✔</span>
                        <span>{skill}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-slate-300">No matched skills detected yet.</p>
                )}
              </SectionCard>

              <SectionCard title="Missing Skills" tone="danger">
                {missingSkills.length > 0 ? (
                  <ul className="space-y-3">
                    {missingSkills.map((skill, index) => (
                      <li key={index} className="flex items-center gap-3 text-red-200">
                        <span className="text-red-400 font-bold">✘</span>
                        <span>{skill}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-slate-300">No missing skills detected. Great match.</p>
                )}
              </SectionCard>
            </div>

            <SectionCard title="Suggestions">
              {suggestions.length > 0 ? (
                <ul className="space-y-3">
                  {suggestions.map((suggestion, index) => (
                    <li key={index} className="flex items-start gap-3 text-slate-200">
                      <span className="text-cyan-300">→</span>
                      <span>{suggestion}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-slate-300">Upload a resume and job description to see improvement suggestions.</p>
              )}
            </SectionCard>

            <SectionCard title="Tips to Improve" tone="accent">
              <ul className="space-y-3 text-slate-200">
                <li className="flex items-start gap-3">
                  <span className="text-cyan-300">→</span>
                  <span>Use exact skill keywords from the job description.</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-cyan-300">→</span>
                  <span>Add measurable achievements to show impact.</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-cyan-300">→</span>
                  <span>Include relevant tools and technologies from your target role.</span>
                </li>
              </ul>
            </SectionCard>
          </div>
        )}
      </div>
    </main>
  )
}
