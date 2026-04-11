import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { AlertCircle, ArrowRight, CheckCircle2 } from 'lucide-react'

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
      ? 'border-emerald-200 bg-emerald-50/70'
      : tone === 'danger'
      ? 'border-red-200 bg-red-50/70'
      : tone === 'accent'
      ? 'border-slate-200 bg-slate-50'
      : 'border-slate-200 bg-white'

  return (
    <div className={`rounded-2xl border p-6 shadow-sm ${toneClasses}`}>
      <h3 className="text-lg font-medium mb-4 text-slate-900">{title}</h3>
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
    <main className="min-h-screen bg-gradient-to-br from-[#f7f7f4] via-[#f4f6f8] to-[#eef2f7] text-slate-900 pt-24 px-6 pb-10">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8 max-w-xl text-left">
          <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight">
            Job Match Analysis
          </h1>
          <p className="mt-3 text-slate-600">
            Review how closely your resume aligns with the job description and where to improve next.
          </p>
        </div>

        {!analysisResult ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm text-left max-w-xl">
            <p className="text-slate-900 text-lg font-medium mb-2">No resume uploaded yet</p>
            <p className="text-slate-600 mb-6">Upload your resume and paste a job description to get a match analysis.</p>
            <Link to="/resume-analysis" className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-black text-white hover:bg-slate-800 transition">
              <ArrowRight size={16} strokeWidth={1.5} className="opacity-80" />
              Upload your resume
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            <SectionCard title="Match Overview" tone="accent">
              <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
                <div>
                  <h2 className="text-4xl sm:text-5xl font-extrabold" style={{ color: scoreColor }}>
                    {matchScore}%
                  </h2>
                  <h3 className="mt-2 text-2xl font-semibold text-slate-900">{verdict}</h3>
                  <p className="mt-2 text-slate-600">
                    Confidence: <span className="font-semibold text-slate-900">{confidence}</span>
                  </p>
                </div>
                <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
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
                <div className="flex items-center gap-2 text-slate-700">
                  <AlertCircle size={16} strokeWidth={1.5} className="opacity-80" />
                  <p>Upload a job description to get a personalized match analysis.</p>
                </div>
              </SectionCard>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SectionCard title="Matched Skills" tone="success">
                {matchedSkills.length > 0 ? (
                  <ul className="space-y-3">
                    {matchedSkills.map((skill, index) => (
                      <li key={index} className="flex items-center gap-3 text-emerald-800">
                        <CheckCircle2 size={16} strokeWidth={1.5} className="opacity-80" />
                        <span>{skill}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-slate-600">No matched skills detected yet.</p>
                )}
              </SectionCard>

              <SectionCard title="Missing Skills" tone="danger">
                {missingSkills.length > 0 ? (
                  <ul className="space-y-3">
                    {missingSkills.map((skill, index) => (
                      <li key={index} className="flex items-center gap-3 text-red-800">
                        <AlertCircle size={16} strokeWidth={1.5} className="opacity-80" />
                        <span>{skill}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-slate-600">No missing skills detected. Great match.</p>
                )}
              </SectionCard>
            </div>

            <SectionCard title="Suggestions">
              {suggestions.length > 0 ? (
                <ul className="space-y-3">
                  {suggestions.map((suggestion, index) => (
                    <li key={index} className="flex items-start gap-3 text-slate-700">
                      <ArrowRight size={16} strokeWidth={1.5} className="opacity-80 mt-0.5" />
                      <span>{suggestion}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-slate-600">Upload a resume and job description to see improvement suggestions.</p>
              )}
            </SectionCard>

            <SectionCard title="Tips to Improve" tone="accent">
              <ul className="space-y-3 text-slate-700">
                <li className="flex items-start gap-3">
                  <ArrowRight size={16} strokeWidth={1.5} className="opacity-80 mt-0.5" />
                  <span>Use exact skill keywords from the job description.</span>
                </li>
                <li className="flex items-start gap-3">
                  <ArrowRight size={16} strokeWidth={1.5} className="opacity-80 mt-0.5" />
                  <span>Add measurable achievements to show impact.</span>
                </li>
                <li className="flex items-start gap-3">
                  <ArrowRight size={16} strokeWidth={1.5} className="opacity-80 mt-0.5" />
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
