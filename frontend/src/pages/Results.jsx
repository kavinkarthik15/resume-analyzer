import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { AlertCircle, AlertTriangle, ArrowRight, BarChart3, CheckCircle2, Sparkles } from 'lucide-react'
import { useAnalysis } from '../context/AnalysisContext'
import ProgressBar from '../components/ProgressBar'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

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

function getProbabilityColor(label) {
  if (label === 'High') return '#16a34a'
  if (label === 'Medium') return '#ea580c'
  return '#dc2626'
}

function getConfidence(analysis) {
  const match = analysis?.match_score || 0
  const interview = typeof analysis?.interview_probability === 'object'
    ? analysis.interview_probability.score
    : analysis?.interview_probability || 0

  if (match >= 80 && interview >= 70) return 'High'
  if (match >= 60) return 'Medium'
  return 'Low'
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
  const { analysisResult: contextAnalysisResult, clearAnalysis } = useAnalysis()
  const [activeTab, setActiveTab] = React.useState('overview')
  const reportRef = React.useRef(null)

  const cachedResult = localStorage.getItem('analysis') || localStorage.getItem('analysisResult')
  let analysisResult = contextAnalysisResult

  if (!analysisResult && cachedResult) {
    try {
      analysisResult = JSON.parse(cachedResult)
    } catch (error) {
      console.error('Failed to parse analysis result:', error)
    }
  }

  if (!analysisResult) {
    analysisResult = location.state?.analysisResult || null
  }

  const analysis = analysisResult

  console.log('FULL ANALYSIS:', analysis)

  const matchScore = analysis?.match_score ?? analysis?.score ?? analysis?.ats_analysis?.score ?? 0
  const confidence = getConfidence(analysis)
  const verdict = analysis?.verdict || 'Low Match'
  const jobDescriptionProvided = analysis?.job_description_provided ?? false
  const roleData = analysis?.role_context || analysis?.role_data || {}
  const experienceLevel = roleData?.experience_level || analysis?.experience_level || null
  const matchedSkills = analysis?.matched_skills || []
  const missingSkills = analysis?.missing_skills || analysis?.ats_analysis?.missing_skills || []
  const warnings = Array.isArray(analysis?.warnings) ? analysis.warnings : []
  const rawSuggestions = analysis?.suggestions || analysis?.ats_analysis?.improvement_tips || []
  const normalizedSuggestions = rawSuggestions.map((item) =>
    typeof item === 'string'
      ? { type: 'general', message: item, example: '' }
      : {
          type: item?.type || 'general',
          message: item?.message || 'Suggestion',
          example: item?.example || '',
        }
  )
  const scoreBreakdown = analysis?.breakdown || null
  const rawInterview = analysis?.interview_probability

  let interviewScore = 0
  let interviewLabel = 'Low'

  if (typeof rawInterview === 'number') {
    interviewScore = rawInterview
    interviewLabel = rawInterview > 75 ? 'High' : rawInterview > 40 ? 'Medium' : 'Low'
  } else if (typeof rawInterview === 'object' && rawInterview !== null) {
    interviewScore = rawInterview.score || 0
    interviewLabel = rawInterview.label || 'Low'
  }

  if (interviewScore === 0 && analysis?.match_score) {
    interviewScore = Math.round(Number(analysis.match_score) * 0.8)
    interviewLabel = interviewScore > 75 ? 'High' : interviewScore > 40 ? 'Medium' : 'Low'
  }

  const interviewProbability = {
    score: interviewScore,
    label: interviewLabel,
  }

  const probabilityLabel = interviewProbability.label
  const probabilityScore = interviewProbability.score
  const probabilityColor = getProbabilityColor(probabilityLabel)
  const aiReview = analysis?.ai_review || roleData?.professional_review || 'No AI review generated yet.'
  const scoreColor = getScoreColor(matchScore)
  const scoreBarColor = getScoreBarColor(matchScore)

  const breakdownItems = scoreBreakdown
    ? [
        { key: 'skills', label: 'Skills Match', value: scoreBreakdown.skills ?? 0 },
        { key: 'keywords', label: 'Keyword Density', value: scoreBreakdown.keywords ?? 0 },
        { key: 'experience', label: 'Experience Signals', value: scoreBreakdown.experience ?? 0 },
        { key: 'quality', label: 'Resume Quality', value: scoreBreakdown.quality ?? 0 },
        { key: 'format', label: 'Format & Sections', value: scoreBreakdown.format ?? 0 },
      ]
    : []

  async function handleDownloadPDF() {
    const element = reportRef.current
    if (!element) return

    const canvas = await html2canvas(element, {
      scale: 2,
      backgroundColor: '#ffffff',
      useCORS: true,
      logging: false,
    })

    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')

    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    const imgWidth = pageWidth
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    let heightLeft = imgHeight
    let position = 0

    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight

    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
    }

    pdf.save('resume-analysis.pdf')
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#f7f7f4] via-[#f4f6f8] to-[#eef2f7] text-slate-900 pt-24 px-6 pb-10">
      <div className="max-w-[900px] mx-auto">
        <div className="mb-8 text-left" style={{ marginBottom: '24px' }}>
          <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight">
            Job Match Analysis
          </h1>
          <p className="mt-3 text-slate-600">
            Review how closely your resume aligns with the job description and where to improve next.
          </p>
          {analysisResult && (
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                type="button"
                onClick={clearAnalysis}
                className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-100 transition"
              >
                Clear Analysis
              </button>
              <button
                type="button"
                onClick={handleDownloadPDF}
                className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-700 hover:bg-slate-100 transition"
              >
                Download Report
              </button>
            </div>
          )}
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

              <div className="mt-5 rounded-xl border-2 bg-white p-4" style={{ borderColor: probabilityColor }}>
                <h2 className="text-lg font-semibold" style={{ color: probabilityColor }}>
                  Interview Probability: {probabilityLabel}
                </h2>
                <p className="text-sm text-slate-600 mt-1">
                  Score: <span className="font-semibold text-slate-900">{probabilityScore}%</span>
                </p>
              </div>
            </SectionCard>

            {(roleData.role || roleData.experience || roleData.workType || roleData.location || (roleData.skills && roleData.skills.length)) && (
              <SectionCard title="Role Context" tone="accent">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-700">
                  {roleData.role && (
                    <div>
                      <p className="text-slate-500 uppercase tracking-wide text-xs mb-1">Role</p>
                      <p className="font-medium text-slate-900">{roleData.role}</p>
                    </div>
                  )}
                  {roleData.role_type && (
                    <div>
                      <p className="text-slate-500 uppercase tracking-wide text-xs mb-1">Detected Role Type</p>
                      <p className="font-medium text-slate-900 capitalize">{roleData.role_type}</p>
                    </div>
                  )}
                  {roleData.experience && (
                    <div>
                      <p className="text-slate-500 uppercase tracking-wide text-xs mb-1">Experience</p>
                      <p className="font-medium text-slate-900">{roleData.experience}</p>
                    </div>
                  )}
                  {roleData.workType && (
                    <div>
                      <p className="text-slate-500 uppercase tracking-wide text-xs mb-1">Work Type</p>
                      <p className="font-medium text-slate-900">{roleData.workType}</p>
                    </div>
                  )}
                  {roleData.location && (
                    <div>
                      <p className="text-slate-500 uppercase tracking-wide text-xs mb-1">Location</p>
                      <p className="font-medium text-slate-900">{roleData.location}</p>
                    </div>
                  )}
                  {roleData.skills && (
                    <div className="md:col-span-2">
                      <p className="text-slate-500 uppercase tracking-wide text-xs mb-1">Key Skills</p>
                      <p className="font-medium text-slate-900">{Array.isArray(roleData.skills) ? roleData.skills.join(', ') : roleData.skills}</p>
                    </div>
                  )}
                  {(roleData.required_level || experienceLevel) && (
                    <div>
                      <p className="text-slate-500 uppercase tracking-wide text-xs mb-1">Experience Level</p>
                      <p className="font-medium text-slate-900 capitalize">{roleData.required_level || experienceLevel}</p>
                    </div>
                  )}
                  {roleData.professional_review && (
                    <div className="md:col-span-2 rounded-xl border border-slate-200 bg-white p-4">
                      <p className="text-slate-500 uppercase tracking-wide text-xs mb-2">Professional Review</p>
                      <p className="text-slate-700 leading-6">{roleData.professional_review}</p>
                    </div>
                  )}
                </div>
              </SectionCard>
            )}

            {!jobDescriptionProvided && (
              <SectionCard title="Job Description Needed" tone="accent">
                <div className="flex items-center gap-2 text-slate-700">
                  <AlertCircle size={16} strokeWidth={1.5} className="opacity-80" />
                  <p>Upload a job description to get a personalized match analysis.</p>
                </div>
              </SectionCard>
            )}

            <div
              className="tabs-container"
              style={{
                display: 'flex',
                gap: '8px',
                overflowX: 'auto',
                whiteSpace: 'nowrap',
                borderBottom: '1px solid #eee',
                marginBottom: '16px',
                position: 'sticky',
                top: 0,
                background: '#fff',
                zIndex: 10,
                padding: '8px 12px',
              }}
            >
              {[
                { id: 'overview', label: 'Overview', icon: BarChart3 },
                { id: 'warnings', label: 'Warnings', icon: AlertTriangle },
                { id: 'ai', label: 'AI Review', icon: Sparkles },
              ].map((tab) => {
                const isActive = activeTab === tab.id
                const Icon = tab.icon

                return (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => setActiveTab(tab.id)}
                    style={{
                      flex: '0 0 auto',
                      padding: '8px 14px',
                      border: 'none',
                      borderBottom: isActive ? '3px solid #4f46e5' : '3px solid transparent',
                      background: 'transparent',
                      color: isActive ? '#4f46e5' : '#555',
                      borderRadius: '8px 8px 0 0',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontWeight: isActive ? 600 : 400,
                    }}
                  >
                    <Icon size={16} />
                    {tab.label}
                  </button>
                )
              })}
              <div
                style={{
                  position: 'sticky',
                  right: 0,
                  top: 0,
                  bottom: 0,
                  width: '20px',
                  minWidth: '20px',
                  pointerEvents: 'none',
                  background: 'linear-gradient(to left, white, transparent)',
                  marginLeft: '-20px',
                }}
              />
            </div>

            <div style={{ minHeight: '250px' }}>
              <div className={`tab-panel ${activeTab === 'overview' ? 'active' : ''}`}>
                {activeTab === 'overview' && (
                  <div className="space-y-6">
                    {breakdownItems.length > 0 && (
                      <SectionCard title="Score Breakdown" tone="accent">
                        <div style={{ marginBottom: '24px' }}>
                          {breakdownItems.map((item) => (
                            <ProgressBar
                              key={item.key}
                              label={item.label}
                              value={item.value}
                            />
                          ))}
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

                      <SectionCard title="Suggestions">
                        {normalizedSuggestions.length > 0 ? (
                          <div>
                            {normalizedSuggestions.map((suggestion, index) => (
                              <div
                                key={index}
                                style={{
                                  borderLeft: '4px solid #4f46e5',
                                  padding: '10px',
                                  marginBottom: '10px',
                                  background: '#f8fafc',
                                  borderRadius: '8px',
                                }}
                              >
                                <div className="flex items-start gap-3 text-slate-700">
                                  <ArrowRight size={16} strokeWidth={1.5} className="opacity-80 mt-0.5" />
                                  <div>
                                    <p className="font-medium">{suggestion.message}</p>
                                    {suggestion.example && <small className="text-slate-500">{suggestion.example}</small>}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-slate-600">Upload a resume and job description to see improvement suggestions.</p>
                        )}
                      </SectionCard>
                    </div>
                  </div>
                )}
              </div>

              <div className={`tab-panel ${activeTab === 'warnings' ? 'active' : ''}`}>
                {activeTab === 'warnings' && (
                  <SectionCard title="Key Issues" tone="danger">
                    {warnings.length === 0 && missingSkills.length === 0 ? (
                      <p className="text-slate-600">No major issues.</p>
                    ) : warnings.length > 0 ? (
                      <div>
                        {warnings.map((warning, index) => (
                          <div
                            key={`${warning?.id || warning?.message || 'warning'}-${index}`}
                            style={{
                              borderLeft: '4px solid #dc2626',
                              padding: '10px',
                              marginBottom: '10px',
                              background: '#fff5f5',
                              borderRadius: '8px',
                            }}
                          >
                            <p className="text-sm text-red-900 font-medium">{warning?.message || 'Issue detected'}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div>
                        {missingSkills.map((skill, index) => (
                          <div
                            key={`${skill}-${index}`}
                            style={{
                              borderLeft: '4px solid #dc2626',
                              padding: '10px',
                              marginBottom: '10px',
                              background: '#fff5f5',
                              borderRadius: '8px',
                            }}
                          >
                            <p className="text-sm text-red-900 font-medium">Missing key skill: {skill}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </SectionCard>
                )}
              </div>

              <div className={`tab-panel ${activeTab === 'ai' ? 'active' : ''}`}>
                {activeTab === 'ai' && (
                  <SectionCard title="AI Review" tone="accent">
                    <pre
                      style={{
                        whiteSpace: 'pre-wrap',
                        background: '#f9f9f9',
                        padding: '12px',
                        borderRadius: '8px',
                        fontFamily: 'inherit',
                      }}
                    >
                      {aiReview}
                    </pre>
                  </SectionCard>
                )}
              </div>
            </div>

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

      <div
        ref={reportRef}
        style={{
          position: 'fixed',
          left: '-10000px',
          top: 0,
          width: '900px',
          background: '#ffffff',
          color: '#111827',
          padding: '24px',
          zIndex: -1,
        }}
      >
        <h1 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '8px' }}>Resume Analysis Report</h1>
        <p style={{ color: '#475569', marginBottom: '20px' }}>Generated by Resume Analyzer</p>

        <div style={{ border: '1px solid #e2e8f0', borderRadius: '12px', padding: '16px', marginBottom: '16px' }}>
          <h2 style={{ fontSize: '24px', fontWeight: 700, color: scoreColor, marginBottom: '8px' }}>{matchScore}% Match</h2>
          <p style={{ fontSize: '18px', fontWeight: 600, marginBottom: '4px' }}>{verdict}</p>
          <p style={{ color: '#475569' }}>Confidence: {confidence}</p>
        </div>

        <div style={{ border: `2px solid ${probabilityColor}`, borderRadius: '10px', padding: '14px', marginBottom: '16px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: 700, color: probabilityColor, marginBottom: '4px' }}>
            Interview Probability: {probabilityLabel}
          </h2>
          <p style={{ color: '#334155' }}>Score: {probabilityScore}%</p>
        </div>

        {breakdownItems.length > 0 && (
          <div style={{ marginBottom: '20px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '12px' }}>Score Breakdown</h2>
            {breakdownItems.map((item) => (
              <ProgressBar key={`pdf-${item.key}`} label={item.label} value={item.value} />
            ))}
          </div>
        )}

        <div style={{ marginBottom: '20px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '12px' }}>Key Issues</h2>
          {warnings.length > 0 ? (
            warnings.map((warning, index) => (
              <div
                key={`pdf-warning-${index}`}
                style={{
                  borderLeft: '4px solid #dc2626',
                  padding: '10px',
                  marginBottom: '10px',
                  background: '#fff5f5',
                  borderRadius: '8px',
                }}
              >
                {warning?.message || 'Issue detected'}
              </div>
            ))
          ) : (
            <p style={{ color: '#475569' }}>No major issues.</p>
          )}
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '12px' }}>Suggestions</h2>
          {normalizedSuggestions.length > 0 ? (
            normalizedSuggestions.map((suggestion, index) => (
              <div
                key={`pdf-suggestion-${index}`}
                style={{
                  borderLeft: '4px solid #4f46e5',
                  padding: '10px',
                  marginBottom: '10px',
                  background: '#f8fafc',
                  borderRadius: '8px',
                }}
              >
                <p style={{ marginBottom: '4px', fontWeight: 600 }}>{suggestion.message}</p>
                {suggestion.example && <small style={{ color: '#64748b' }}>{suggestion.example}</small>}
              </div>
            ))
          ) : (
            <p style={{ color: '#475569' }}>No suggestions available.</p>
          )}
        </div>

        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '12px' }}>AI Review</h2>
          <pre
            style={{
              whiteSpace: 'pre-wrap',
              background: '#f9f9f9',
              padding: '12px',
              borderRadius: '8px',
              fontFamily: 'inherit',
            }}
          >
            {aiReview}
          </pre>
        </div>
      </div>
    </main>
  )
}
