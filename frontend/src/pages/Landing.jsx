import React from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertCircle, ArrowRight, Upload } from 'lucide-react'
import illustration from '../assets/ai-illustration.svg'
import { jdAPI, resumeAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { saveResumeAnalysis } from '../services/firestoreService'

export default function Landing(){
  const fileInput = React.useRef(null)
  const [isAnalyzing, setIsAnalyzing] = React.useState(false)
  const [loadingJD, setLoadingJD] = React.useState(false)
  const [errorMessage, setErrorMessage] = React.useState('')
  const [jobDescription, setJobDescription] = React.useState('')
  const [roleData, setRoleData] = React.useState({
    role: '',
    experience: '',
    workType: '',
    location: '',
    skills: '',
  })
  const navigate = useNavigate()
  const { user } = useAuth()

  function saveAnalysisToHistory(analysisResult, fileName = 'Demo Resume'){
    const stored = localStorage.getItem('analysisHistory')
    let list = []

    if(stored){
      try {
        list = JSON.parse(stored)
      } catch {
        list = []
      }
    }

    const nextItem = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      timestamp: new Date().toLocaleString(),
      fileName,
      analysisResult,
    }

    const updated = [nextItem, ...list].slice(0, 20)
    localStorage.setItem('analysisHistory', JSON.stringify(updated))
  }

  function handleUpload(){
    if (!user) {
      alert('Please login to upload your resume')
      navigate('/login')
      return
    }

    fileInput.current?.click()
  }

  async function handleGenerateJD() {
    if (!roleData.role.trim() || !roleData.experience.trim()) {
      alert('Fill role and experience first')
      return
    }

    setLoadingJD(true)

    try {
      const response = await jdAPI.generate(roleData)
      setJobDescription(response.data.job_description || '')
    } catch (error) {
      alert('Failed to generate JD')
    } finally {
      setLoadingJD(false)
    }
  }

  function handleDemo(){
    setErrorMessage('')
    const demoResult = {
      ats_score: 78,
      skills_found: ['Python', 'SQL', 'React'],
      score_breakdown: {
        skill_score: { score: 20, max: 30 },
        section_score: { score: 20, max: 25 },
        keyword_score: { score: 15, max: 20 },
        format_score: { score: 13, max: 15 },
        length_score: { score: 10, max: 10 },
        total: 78,
      },
      skill_categories: {
        Programming: ['Python'],
        Web: ['React'],
      },
      sections: {
        Education: 'Found',
        Experience: 'Found',
        Projects: 'Missing',
        Skills: 'Found',
        Certifications: 'Missing',
      },
      suggestions: ['Add projects section', 'Add more relevant skills', 'Increase resume length'],
      ml_prediction: {
        shortlist_probability: 0.72,
        decision: 'Shortlisted',
      },
      ml_features: {
        skill_count: 3,
        matched_role_skills: 3,
        ats_score: 78,
        jd_similarity: 0.0,
        experience_years: 2.0,
        action_verbs: 5,
        achievements: 2,
        pages: 1,
        section_score: 0.5,
      },
    }

    saveAnalysisToHistory(demoResult, 'Demo Resume')
    sessionStorage.setItem('resumeAnalysis', JSON.stringify(demoResult))
    navigate('/results', { state: { analysisResult: demoResult } })
  }

  async function handleFileChange(e){
    const f = e.target.files[0]
    if(f){
      if(!f.size){
        setErrorMessage('Selected file is empty. Please upload a valid resume file.')
        e.target.value = ''
        return
      }

      const allowed = ['application/pdf','application/msword','application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      const extension = (f.name?.split('.').pop() || '').toLowerCase()
      const extensionAllowed = ['pdf', 'doc', 'docx'].includes(extension)
      const mimeAllowed = allowed.includes(f.type)

      if(!mimeAllowed && !extensionAllowed){
        setErrorMessage('Please select a PDF or DOC/DOCX file.')
        e.target.value = '';
        return;
      }

      if (!roleData.role.trim() || !roleData.experience.trim()) {
        setErrorMessage('Please fill role and experience.')
        e.target.value = ''
        return
      }

      setIsAnalyzing(true)
      setErrorMessage('')

      try {
        const jd = jobDescription.trim()
        if (!jd) {
          setErrorMessage('Job Description Needed. Please paste a JD before analyzing.')
          setIsAnalyzing(false)
          e.target.value = ''
          return
        }

        const response = await resumeAPI.uploadAndAnalyze(f, {
          job_description: jd,
          role_data: roleData,
        })
        
        // Store the file for format checking on the warnings page
        const reader = new FileReader()
        reader.onload = () => {
          sessionStorage.setItem('resumeFile', reader.result)
          sessionStorage.setItem('resumeFileName', f.name)
        }
        reader.readAsDataURL(f)

        // API response structure: { status, parsing, ats_analysis, ml_prediction, ml_features, ... }
        const analysisData = response.data

        saveAnalysisToHistory(analysisData, f.name)
        localStorage.setItem('analysisResult', JSON.stringify(analysisData))
        sessionStorage.setItem('resumeAnalysis', JSON.stringify(analysisData))

        if (user) {
          try {
            await saveResumeAnalysis(user.uid, {
              ...analysisData,
              fileName: f.name,
            })
          } catch (saveError) {
            console.error('Failed to persist resume analysis:', saveError)
          }
        }

        navigate('/results', { state: { analysisResult: analysisData } })
      } catch (error) {
        let message = 'Something went wrong. Please try again.';
        
        if (error.message === 'Network Error' || error.code === 'ECONNABORTED') {
          message = 'Server is waking up, please wait a few seconds and try again.';
        } else if (error.response?.status === 404) {
          message = 'Backend service is initializing. Please wait a moment and try again.';
        } else if (error.response?.data?.detail) {
          message = error.response.data.detail;
        }
        
        setErrorMessage(message)
      } finally {
        setIsAnalyzing(false)
      }

      e.target.value = ''
    }
  }

  return (
    <main className="w-full min-h-screen bg-gradient-to-br from-[#f7f7f4] via-[#f4f6f8] to-[#eef2f7] text-slate-900 pt-24 px-6 pb-16">
      <div className="max-w-6xl mx-auto">
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
          <div className="max-w-xl text-left">
            <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight mb-3">
              Upload your resume
            </h1>
            <p className="text-slate-600 mb-7">
              Get instant job match insights based on your resume and optional job description.
            </p>

            <div className="mb-5 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500 mb-3">Role details</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <input
                  placeholder="Role (e.g. Frontend Developer)"
                  value={roleData.role}
                  onChange={(e) => setRoleData((prev) => ({ ...prev, role: e.target.value }))}
                  className="w-full rounded-xl border border-slate-300 !bg-white px-3 py-2 !text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-300"
                />
                <input
                  placeholder="Experience (e.g. 2+ years)"
                  value={roleData.experience}
                  onChange={(e) => setRoleData((prev) => ({ ...prev, experience: e.target.value }))}
                  className="w-full rounded-xl border border-slate-300 !bg-white px-3 py-2 !text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-300"
                />
                <select
                  value={roleData.workType}
                  onChange={(e) => setRoleData((prev) => ({ ...prev, workType: e.target.value }))}
                  className="w-full rounded-xl border border-slate-300 !bg-white px-3 py-2 !text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-300"
                >
                  <option value="">Work Type</option>
                  <option value="remote">Remote</option>
                  <option value="onsite">On-site</option>
                  <option value="hybrid">Hybrid</option>
                </select>
                <input
                  placeholder="Location (optional)"
                  value={roleData.location}
                  onChange={(e) => setRoleData((prev) => ({ ...prev, location: e.target.value }))}
                  className="w-full rounded-xl border border-slate-300 !bg-white px-3 py-2 !text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-300"
                />
                <input
                  placeholder="Key Skills (comma separated)"
                  value={roleData.skills}
                  onChange={(e) => setRoleData((prev) => ({ ...prev, skills: e.target.value }))}
                  className="w-full sm:col-span-2 rounded-xl border border-slate-300 !bg-white px-3 py-2 !text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-300"
                />
              </div>
            </div>

            <div className="mb-5">
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Job Description
              </label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the job description here..."
                rows={6}
                className="w-full rounded-xl border border-slate-300 !bg-white px-3 py-2 !text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-300"
              />
            </div>

            <div className="flex flex-wrap gap-3 mb-5">
              <button
                onClick={handleUpload}
                disabled={isAnalyzing}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-black text-white hover:bg-slate-800 transition disabled:opacity-60 disabled:cursor-not-allowed"
              >
                <Upload size={16} strokeWidth={1.5} className="opacity-80" />
                {isAnalyzing ? 'Analyzing...' : user ? 'Upload Resume' : 'Login to Upload'}
              </button>
              <button
                onClick={handleDemo}
                className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-300 bg-white text-slate-900 hover:bg-slate-100 transition"
              >
                <ArrowRight size={16} strokeWidth={1.5} className="opacity-80" />
                Try Demo
              </button>
              <input type="file" accept=".pdf,.doc,.docx" ref={fileInput} onChange={handleFileChange} className="hidden" />
            </div>

            {errorMessage && (
              <div className="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-red-700 mb-6">
                <AlertCircle size={16} strokeWidth={1.5} className="opacity-80 mt-0.5" />
                <p className="text-sm leading-6">{errorMessage}</p>
              </div>
            )}

              <button
                type="button"
                onClick={handleGenerateJD}
                disabled={loadingJD}
                className="mt-3 inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 hover:bg-slate-100 transition disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loadingJD ? 'Generating...' : '✨ Generate Job Description'}
              </button>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="p-5 rounded-2xl border border-slate-200 bg-white shadow-sm">
                <h3 className="font-medium mb-2">ATS match score</h3>
                <p className="text-sm text-slate-600">Understand how your resume performs in applicant tracking systems.</p>
              </div>
              <div className="p-5 rounded-2xl border border-slate-200 bg-white shadow-sm">
                <h3 className="font-medium mb-2">Skill gaps</h3>
                <p className="text-sm text-slate-600">See which missing skills matter most for your target role.</p>
              </div>
              <div className="p-5 rounded-2xl border border-slate-200 bg-white shadow-sm">
                <h3 className="font-medium mb-2">Actionable rewrite tips</h3>
                <p className="text-sm text-slate-600">Get practical suggestions to improve impact and clarity.</p>
              </div>
              <div className="p-5 rounded-2xl border border-slate-200 bg-white shadow-sm">
                <h3 className="font-medium mb-2">JD alignment insights</h3>
                <p className="text-sm text-slate-600">Compare your resume against a job description when provided.</p>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="h-72 rounded-2xl bg-gradient-to-br from-slate-100 via-blue-50 to-emerald-50 flex items-center justify-center overflow-hidden">
              <img src={illustration} alt="Resume analysis illustration" className="h-full w-full object-contain" />
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}
