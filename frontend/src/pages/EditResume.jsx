import React from 'react'
import { useNavigate } from 'react-router-dom'

export default function EditResume() {
  const navigate = useNavigate()
  const [resumeText, setResumeText] = React.useState('')
  const [isSaving, setIsSaving] = React.useState(false)

  React.useEffect(() => {
    const cached = sessionStorage.getItem('resumeAnalysis')
    if (cached) {
      try {
        const data = JSON.parse(cached)
        // Reconstruct resume text from analysis data
        const text = [
          data.skills_found?.join(', ') || '',
          Object.entries(data.skill_categories || {})
            .map(([cat, skills]) => `${cat}: ${skills.join(', ')}`)
            .join('\n') || '',
          Object.entries(data.sections || {})
            .map(([sec, status]) => `${sec}: ${status}`)
            .join('\n') || '',
          data.suggestions?.join('\n') || '',
        ]
          .filter(Boolean)
          .join('\n\n')
        setResumeText(text || 'Edit your resume here to improve your ATS score...')
      } catch {
        setResumeText('Edit your resume here to improve your ATS score...')
      }
    }
  }, [])

  function handleSaveAndRe_analyze() {
    setIsSaving(true)
    if (!resumeText.trim()) {
      alert('Please enter resume content.')
      setIsSaving(false)
      return
    }

    // For now, just save and navigate back to results
    // In a future phase, this could re-analyze the edited text
    sessionStorage.setItem('editedResumeText', resumeText)
    alert('Resume updated. You can now upload the edited version for re-analysis.')
    setIsSaving(false)
    navigate('/')
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#07102a] via-[#0f2b4f] to-[#0b0620] text-white pt-20 px-6 pb-10">
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">Edit Resume</h1>
          <p className="mt-2 text-slate-300">Edit your resume content below to enhance your ATS score and re-upload for analysis.</p>
        </div>

        <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6 animate-fade-in">
          <textarea
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            className="w-full h-96 bg-white/10 border border-slate-400 rounded-lg p-4 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 resize-none"
            placeholder="Edit your resume here..."
          />

          <div className="mt-6 flex gap-4">
            <button
              onClick={handleSaveAndRe_analyze}
              disabled={isSaving}
              className="px-8 py-3 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:scale-105 transform transition font-semibold disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              {isSaving ? 'Saving...' : 'Save & Re-analyze'}
            </button>
            <button
              onClick={() => navigate('/results')}
              className="px-8 py-3 rounded-full bg-transparent border border-slate-300 hover:bg-white/10 transition font-semibold"
            >
              Cancel
            </button>
          </div>

          <div className="mt-8 p-4 rounded-lg bg-blue-500/10 border border-blue-400/30">
            <h3 className="font-semibold text-blue-300 mb-2">Tips for Improving ATS Score:</h3>
            <ul className="space-y-1 text-sm text-slate-300">
              <li>✓ Use clear section headers (Education, Experience, Skills)</li>
              <li>✓ List relevant technical skills and tools</li>
              <li>✓ Keep formatting simple (avoid special characters)</li>
              <li>✓ Use industry keywords from job descriptions</li>
              <li>✓ Use standard fonts and clear spacing</li>
              <li>✓ Add quantifiable achievements (metrics, numbers)</li>
            </ul>
          </div>
        </div>
      </div>
    </main>
  )
}
