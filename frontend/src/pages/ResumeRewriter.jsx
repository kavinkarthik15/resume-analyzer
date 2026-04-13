import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import RewriteCard from '../components/RewriteCard'
import { rewriteAPI } from '../services/api'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import { exportToDocx } from '../utils/exportDocx'
import {
  createWorkspaceId,
  loadWorkspace,
  saveWorkspace,
} from '../utils/workspaceStorage'

const SECTION_LABELS = {
  summary: 'Summary',
  experience: 'Experience',
  projects: 'Projects',
  skills: 'Skills',
}

const MAX_VERSIONS = 5

function buildVersionLabel(index) {
  if (index === 0) return 'Original'
  if (index === 1) return 'AI Rewrite'
  if (index === 2) return 'After Edits'
  return `Version ${index + 1}`
}

function withLockFlags(sectionMap) {
  const source = sectionMap || {}
  const output = {}

  Object.keys(source).forEach((key) => {
    output[key] = {
      ...source[key],
      locked: Boolean(source[key]?.locked),
    }
  })

  return output
}

export default function ResumeRewriter() {
  const [searchParams, setSearchParams] = useSearchParams()
  const queryWorkspaceId = searchParams.get('id')

  const [currentResumeId, setCurrentResumeId] = useState(null)
  const [workspaceTitle, setWorkspaceTitle] = useState('Resume')
  const [createdAt, setCreatedAt] = useState(Date.now())
  const [isWorkspaceReady, setIsWorkspaceReady] = useState(false)

  const [resumeText, setResumeText] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [tone, setTone] = useState('professional')
  const [level, setLevel] = useState('mid')
  const [industry, setIndustry] = useState('frontend')
  const [versions, setVersions] = useState([])
  const [currentVersionId, setCurrentVersionId] = useState(null)
  const [originalSections, setOriginalSections] = useState({})
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const exportRef = useRef(null)

  const currentVersion = useMemo(
    () => versions.find((version) => version.id === currentVersionId) || versions[versions.length - 1] || null,
    [versions, currentVersionId]
  )

  const sections = currentVersion?.sections || {}
  const hasSections = useMemo(() => Object.keys(sections || {}).length > 0, [sections])
  const unlockedCount = useMemo(
    () => Object.values(sections).filter((section) => !section?.locked).length,
    [sections]
  )

  const generateMarkdown = (sectionData) => {
    const safe = sectionData || {}
    return `# Resume

## Summary
${safe.summary?.original || ''}

## Experience
${safe.experience?.original || ''}

## Projects
${safe.projects?.original || ''}

## Skills
${safe.skills?.original || ''}
`
  }

  const buildExportFileBase = () => {
    const date = new Date().toISOString().slice(0, 10)
    const label = (currentVersion?.label || 'version')
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^a-z0-9-]/g, '')

    return `resume-${label}-${date}`
  }

  const handleDownloadMD = () => {
    if (!currentVersion) return

    const markdown = generateMarkdown(currentVersion.sections)
    const blob = new Blob([markdown], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')

    link.href = url
    link.download = `${buildExportFileBase()}.md`
    document.body.appendChild(link)
    link.click()
    link.remove()

    URL.revokeObjectURL(url)
  }

  const handleDownloadPDF = async () => {
    if (!currentVersion || !exportRef.current) return

    const canvas = await html2canvas(exportRef.current, {
      scale: 2,
      backgroundColor: '#ffffff',
      useCORS: true,
      logging: false,
    })

    const image = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    const imageWidth = pageWidth
    const imageHeight = (canvas.height * imageWidth) / canvas.width

    let remainingHeight = imageHeight
    let position = 0

    pdf.addImage(image, 'PNG', 0, position, imageWidth, imageHeight)
    remainingHeight -= pageHeight

    while (remainingHeight > 0) {
      position = remainingHeight - imageHeight
      pdf.addPage()
      pdf.addImage(image, 'PNG', 0, position, imageWidth, imageHeight)
      remainingHeight -= pageHeight
    }

    pdf.save(`${buildExportFileBase()}.pdf`)
  }

  const handleExportDOCX = async () => {
    if (!currentVersion) return
    await exportToDocx(currentVersion.sections, `${buildExportFileBase()}.docx`)
  }

  useEffect(() => {
    if (!queryWorkspaceId) {
      const newWorkspaceId = createWorkspaceId()
      setCurrentResumeId(newWorkspaceId)
      setSearchParams({ id: newWorkspaceId }, { replace: true })
      setIsWorkspaceReady(true)
      return
    }

    setCurrentResumeId(queryWorkspaceId)
    const existingWorkspace = loadWorkspace(queryWorkspaceId)

    if (existingWorkspace) {
      setWorkspaceTitle(existingWorkspace.title || 'Resume')
      setCreatedAt(existingWorkspace.createdAt || Date.now())
      setVersions(Array.isArray(existingWorkspace.versions) ? existingWorkspace.versions : [])
      setCurrentVersionId(
        existingWorkspace.currentVersionId ||
          existingWorkspace.versions?.[existingWorkspace.versions.length - 1]?.id ||
          null
      )
      setResumeText(existingWorkspace.resumeText || '')
      setJobDescription(existingWorkspace.jobDescription || '')
      setTone(existingWorkspace.tone || 'professional')
      setLevel(existingWorkspace.level || 'mid')
      setIndustry(existingWorkspace.industry || 'frontend')
      setOriginalSections(existingWorkspace.originalSections || {})
    } else {
      setWorkspaceTitle('Resume')
      setCreatedAt(Date.now())
      setVersions([])
      setCurrentVersionId(null)
      setOriginalSections({})
    }

    setIsWorkspaceReady(true)
  }, [queryWorkspaceId, setSearchParams])

  useEffect(() => {
    if (!isWorkspaceReady || !currentResumeId) return

    const workspace = {
      id: currentResumeId,
      title: workspaceTitle || 'Resume',
      createdAt,
      updatedAt: Date.now(),
      versions,
      currentVersionId,
      resumeText,
      jobDescription,
      tone,
      level,
      industry,
      originalSections,
    }

    saveWorkspace(workspace)
  }, [
    isWorkspaceReady,
    currentResumeId,
    workspaceTitle,
    createdAt,
    versions,
    currentVersionId,
    resumeText,
    jobDescription,
    tone,
    level,
    industry,
    originalSections,
  ])

  const saveNewVersion = (updatedSections, labelOverride) => {
    const newVersion = {
      id: Date.now(),
      label: labelOverride || buildVersionLabel(versions.length),
      sections: withLockFlags(updatedSections),
      timestamp: Date.now(),
    }

    setVersions((prev) => {
      const trimmed = prev.length >= MAX_VERSIONS ? prev.slice(prev.length - (MAX_VERSIONS - 1)) : prev
      return [...trimmed, newVersion]
    })
    setCurrentVersionId(newVersion.id)
  }

  const handleGenerate = async () => {
    if (!resumeText.trim()) {
      setErrorMessage('Paste your resume text to generate section rewrites.')
      return
    }

    setIsLoading(true)
    setErrorMessage('')

    try {
      const response = await rewriteAPI.rewriteResume({
        text: resumeText,
        job_description: jobDescription.trim() || undefined,
        tone,
        level,
        industry,
      })
      const nextSections = withLockFlags(response?.data?.rewrites || {})
      setOriginalSections(nextSections)
      const initialVersion = {
        id: Date.now(),
        label: 'Original',
        sections: nextSections,
        timestamp: Date.now(),
      }
      setVersions([initialVersion])
      setCurrentVersionId(initialVersion.id)
    } catch (error) {
      const apiMessage = error?.response?.data?.error
      setErrorMessage(apiMessage || 'Rewrite failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAccept = (sectionKey) => {
    if (!currentVersion) return
    if (currentVersion.sections[sectionKey]?.locked) return

    const updatedSections = {
      ...currentVersion.sections,
      [sectionKey]: {
        ...currentVersion.sections[sectionKey],
        original: currentVersion.sections[sectionKey]?.rewritten || currentVersion.sections[sectionKey]?.original || '',
      },
    }

    saveNewVersion(updatedSections)
  }

  const handleRevert = (sectionKey) => {
    if (!currentVersion) return
    if (currentVersion.sections[sectionKey]?.locked) return

    const updatedSections = {
      ...currentVersion.sections,
      [sectionKey]: {
        ...currentVersion.sections[sectionKey],
        original: originalSections?.[sectionKey]?.original || currentVersion.sections[sectionKey]?.original || '',
      },
    }

    saveNewVersion(updatedSections)
  }

  const toggleLock = (sectionKey) => {
    if (!currentVersion) return

    const updatedSections = {
      ...currentVersion.sections,
      [sectionKey]: {
        ...currentVersion.sections[sectionKey],
        locked: !currentVersion.sections[sectionKey]?.locked,
      },
    }

    saveNewVersion(updatedSections, 'After Edits')
  }

  const handleAcceptAll = () => {
    if (!currentVersion) return

    const updatedSections = {}

    Object.keys(currentVersion.sections).forEach((key) => {
      const section = currentVersion.sections[key]
      if (section?.locked) {
        updatedSections[key] = section
      } else {
        updatedSections[key] = {
          ...section,
          original: section?.rewritten || section?.original || '',
        }
      }
    })

    saveNewVersion(updatedSections)
  }

  const handleSaveEdit = (sectionKey, newText) => {
    if (!currentVersion) return
    if (currentVersion.sections[sectionKey]?.locked) return

    const updatedSections = {
      ...currentVersion.sections,
      [sectionKey]: {
        ...currentVersion.sections[sectionKey],
        original: newText,
      },
    }

    saveNewVersion(updatedSections, 'After Edits')
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#f7f7f4] via-[#f4f6f8] to-[#eef2f7] text-slate-900 pt-24 px-6 pb-12">
      <div className="max-w-5xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight mb-2">AI Resume Rewriter</h1>
          <p className="text-slate-600">
            Compare each section before applying any rewrite. Nothing is auto-overwritten.
          </p>
          <div className="mt-4 flex items-center gap-3 flex-wrap">
            <label htmlFor="workspaceTitle" className="text-sm font-medium text-slate-700">
              Resume Title
            </label>
            <input
              id="workspaceTitle"
              value={workspaceTitle}
              onChange={(event) => setWorkspaceTitle(event.target.value)}
              placeholder="Frontend Developer Resume"
              className="px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
            />
            <span className="text-xs text-slate-500">
              Workspace ID: {currentResumeId || 'loading'}
            </span>
          </div>
        </div>

        <section className="rounded-2xl border border-slate-200 bg-white shadow-sm p-5 mb-6">
          <div
            style={{
              display: 'flex',
              gap: '14px',
              marginBottom: '16px',
              flexWrap: 'wrap',
            }}
          >
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">Tone</p>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {['professional', 'direct', 'confident'].map((option) => {
                  const selected = tone === option
                  return (
                    <button
                      key={option}
                      type="button"
                      onClick={() => setTone(option)}
                      style={{
                        border: selected ? '2px solid #4f46e5' : '1px solid #cbd5e1',
                        background: selected ? '#eef2ff' : '#fff',
                        color: selected ? '#4338ca' : '#334155',
                        borderRadius: '999px',
                        padding: '6px 12px',
                        fontWeight: 600,
                        fontSize: '13px',
                        cursor: 'pointer',
                      }}
                    >
                      {option.charAt(0).toUpperCase() + option.slice(1)}
                    </button>
                  )
                })}
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">Level</p>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {['junior', 'mid', 'senior'].map((option) => {
                  const selected = level === option
                  return (
                    <button
                      key={option}
                      type="button"
                      onClick={() => setLevel(option)}
                      style={{
                        border: selected ? '2px solid #4f46e5' : '1px solid #cbd5e1',
                        background: selected ? '#eef2ff' : '#fff',
                        color: selected ? '#4338ca' : '#334155',
                        borderRadius: '999px',
                        padding: '6px 12px',
                        fontWeight: 600,
                        fontSize: '13px',
                        cursor: 'pointer',
                      }}
                    >
                      {option.charAt(0).toUpperCase() + option.slice(1)}
                    </button>
                  )
                })}
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">Industry</p>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {['frontend', 'backend', 'data', 'design'].map((option) => {
                  const selected = industry === option
                  return (
                    <button
                      key={option}
                      type="button"
                      onClick={() => setIndustry(option)}
                      style={{
                        border: selected ? '2px solid #4f46e5' : '1px solid #cbd5e1',
                        background: selected ? '#eef2ff' : '#fff',
                        color: selected ? '#4338ca' : '#334155',
                        borderRadius: '999px',
                        padding: '6px 12px',
                        fontWeight: 600,
                        fontSize: '13px',
                        cursor: 'pointer',
                      }}
                    >
                      {option.charAt(0).toUpperCase() + option.slice(1)}
                    </button>
                  )
                })}
              </div>
            </div>
          </div>

          <p className="text-sm text-slate-600 mb-3">
            Tone: <span className="font-semibold capitalize">{tone}</span>
            {' | '}Level: <span className="font-semibold capitalize">{level}</span>
            {' | '}Industry: <span className="font-semibold capitalize">{industry}</span>
          </p>

          <label htmlFor="resumeText" className="block text-sm font-medium text-slate-700 mb-2">
            Paste Resume Text
          </label>
          <textarea
            id="resumeText"
            value={resumeText}
            onChange={(event) => setResumeText(event.target.value)}
            placeholder="Paste your full resume text with headings like Summary, Experience, Projects, Skills"
            className="w-full rounded-xl border border-slate-300 bg-white p-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-400"
            rows={12}
          />

          <label htmlFor="jobDescription" className="block text-sm font-medium text-slate-700 mt-4 mb-2">
            Optional Job Description
          </label>
          <textarea
            id="jobDescription"
            value={jobDescription}
            onChange={(event) => setJobDescription(event.target.value)}
            placeholder="Paste the target job description to improve keyword coverage scoring"
            className="w-full rounded-xl border border-slate-300 bg-white p-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-400"
            rows={8}
          />

          <div className="mt-4 flex items-center gap-3 flex-wrap">
            <button
              type="button"
              onClick={handleGenerate}
              disabled={isLoading}
              className="px-4 py-2 rounded-lg bg-slate-900 text-white font-medium hover:bg-slate-800 transition disabled:opacity-60"
            >
              {isLoading ? 'Generating...' : 'Generate Section Rewrites'}
            </button>
            <span className="text-sm text-slate-500">You can accept or revert each section individually.</span>
          </div>

          {errorMessage && (
            <p className="mt-3 text-sm text-red-600">{errorMessage}</p>
          )}
        </section>

        {hasSections && (
          <section className="rounded-2xl border border-slate-200 bg-slate-50/50 p-5">
            <div className="mb-4">
              <h2 className="text-xl font-semibold text-slate-900">Original vs AI Rewrite</h2>
              <p className="text-sm text-slate-600">Accept updates section by section to stay in control.</p>
              <p className="text-sm text-slate-600 mt-1">
                Exporting: <span className="font-semibold text-slate-900">{currentVersion?.label || 'No version selected'}</span>
              </p>
            </div>

            <div
              style={{
                display: 'flex',
                gap: '10px',
                overflowX: 'auto',
                marginBottom: '20px',
                paddingBottom: '4px',
              }}
            >
              {versions.map((version, index) => {
                const isActive = currentVersionId === version.id
                const timeLabel = new Date(version.timestamp).toLocaleTimeString([], {
                  hour: 'numeric',
                  minute: '2-digit',
                })

                return (
                  <div
                    key={version.id}
                    style={{
                      minWidth: '180px',
                      borderRadius: '12px',
                      border: isActive ? '2px solid #4f46e5' : '1px solid #d1d5db',
                      background: isActive ? '#eef2ff' : '#ffffff',
                      padding: '10px 12px',
                      boxShadow: isActive ? '0 8px 20px rgba(79, 70, 229, 0.12)' : 'none',
                      cursor: 'pointer',
                      flex: '0 0 auto',
                    }}
                    role="button"
                    tabIndex={0}
                    onClick={() => setCurrentVersionId(version.id)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        setCurrentVersionId(version.id)
                      }
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', alignItems: 'flex-start' }}>
                      <div>
                        <p style={{ fontSize: '14px', fontWeight: 700, color: '#0f172a' }}>{version.label || buildVersionLabel(index)}</p>
                        <small style={{ color: '#64748b' }}>{timeLabel}</small>
                      </div>
                      {isActive ? (
                        <span style={{ fontSize: '11px', fontWeight: 700, color: '#4338ca' }}>Current</span>
                      ) : (
                        <button
                          type="button"
                          onClick={(event) => {
                            event.stopPropagation()
                            setCurrentVersionId(version.id)
                          }}
                          style={{
                            border: '1px solid #c7d2fe',
                            background: '#ffffff',
                            color: '#4338ca',
                            borderRadius: '999px',
                            padding: '4px 10px',
                            fontSize: '12px',
                            fontWeight: 600,
                            cursor: 'pointer',
                          }}
                        >
                          Restore
                        </button>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>

            {Object.entries(sections).map(([key, value]) => (
              <RewriteCard
                key={key}
                title={SECTION_LABELS[key] || key.toUpperCase()}
                data={value}
                onAccept={() => handleAccept(key)}
                onRevert={() => handleRevert(key)}
                onToggleLock={() => toggleLock(key)}
                onSaveEdit={(newText) => handleSaveEdit(key, newText)}
              />
            ))}

            <div style={{ display: 'flex', gap: '10px', marginTop: '20px', flexWrap: 'wrap' }}>
              <button
                type="button"
                onClick={handleAcceptAll}
                disabled={!currentVersion || unlockedCount === 0}
                title="Locked sections will not be modified"
                className="px-4 py-2 rounded-lg bg-amber-500 text-white font-medium hover:bg-amber-600 transition disabled:opacity-50"
              >
                Accept All Unlocked
              </button>
              <button
                type="button"
                onClick={handleDownloadMD}
                disabled={!currentVersion}
                className="px-4 py-2 rounded-lg bg-white border border-slate-300 text-slate-700 font-medium hover:bg-slate-100 transition disabled:opacity-50"
              >
                Export Markdown
              </button>
              <button
                type="button"
                onClick={handleExportDOCX}
                disabled={!currentVersion}
                className="px-4 py-2 rounded-lg bg-white border border-slate-300 text-slate-700 font-medium hover:bg-slate-100 transition disabled:opacity-50"
              >
                Export DOCX
              </button>
              <button
                type="button"
                onClick={handleDownloadPDF}
                disabled={!currentVersion}
                className="px-4 py-2 rounded-lg bg-slate-900 text-white font-medium hover:bg-slate-800 transition disabled:opacity-50"
              >
                Export PDF
              </button>
            </div>

            <div
              ref={exportRef}
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
              <h1 style={{ fontSize: '30px', fontWeight: 700, marginBottom: '8px' }}>Resume</h1>
              <p style={{ color: '#475569', marginBottom: '16px' }}>Version: {currentVersion?.label || 'N/A'}</p>

              <h2 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '8px' }}>Summary</h2>
              <p style={{ whiteSpace: 'pre-wrap', marginBottom: '16px' }}>{currentVersion?.sections?.summary?.original || ''}</p>

              <h2 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '8px' }}>Experience</h2>
              <p style={{ whiteSpace: 'pre-wrap', marginBottom: '16px' }}>{currentVersion?.sections?.experience?.original || ''}</p>

              <h2 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '8px' }}>Projects</h2>
              <p style={{ whiteSpace: 'pre-wrap', marginBottom: '16px' }}>{currentVersion?.sections?.projects?.original || ''}</p>

              <h2 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '8px' }}>Skills</h2>
              <p style={{ whiteSpace: 'pre-wrap', marginBottom: '16px' }}>{currentVersion?.sections?.skills?.original || ''}</p>
            </div>
          </section>
        )}
      </div>
    </main>
  )
}

