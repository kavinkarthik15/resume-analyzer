import React from 'react'
import { useNavigate } from 'react-router-dom'
import illustration from '../assets/ai-illustration.svg'
import { resumeAPI } from '../services/api'

export default function Landing(){
  const fileInput = React.useRef(null)
  const [isAnalyzing, setIsAnalyzing] = React.useState(false)
  const [errorMessage, setErrorMessage] = React.useState('')
  const navigate = useNavigate()

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
    fileInput.current?.click()
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

      setIsAnalyzing(true)
      setErrorMessage('')

      try {
        const response = await resumeAPI.uploadAndAnalyze(f)
        
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
    <main className="w-full min-h-screen bg-gradient-to-br from-[#07102a] via-[#0f2b4f] to-[#0b0620] text-white overflow-hidden pt-20">
      <div className="w-full px-6 h-full">
        <section className="flex flex-col-reverse lg:flex-row items-center gap-12 px-6 py-16 animate-fade-in">
          <div className="flex-1 animate-slide-left">
            <h1 className="text-4xl sm:text-5xl font-bold leading-tight bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">Improve Your Resume with AI</h1>
            <p className="mt-4 text-lg text-slate-300">Get ATS Score, Skill Analysis, and Smart Suggestions in Seconds.</p>
            <div className="mt-8 flex gap-4">
              <button onClick={handleUpload} disabled={isAnalyzing} className="px-6 py-3 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 shadow-lg hover:scale-110 transform transition btn-glow font-semibold disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100">{isAnalyzing ? 'Analyzing...' : 'Upload Resume'}</button>
              <button onClick={handleDemo} className="px-6 py-3 rounded-full bg-transparent border border-slate-400 hover:bg-white/10 transition font-semibold">Try Demo</button>
              <input type="file" accept=".pdf,.doc,.docx" ref={fileInput} onChange={handleFileChange} className="hidden" />
            </div>
            {errorMessage && <p className="mt-4 text-sm text-red-300">{errorMessage}</p>}
          </div>

          <div className="flex-1 flex items-center justify-center animate-slide-right animate-float">
            <div className="w-full max-w-sm bg-white/5 backdrop-blur-xl rounded-2xl p-6 shadow-2xl border border-white/10">
              <div className="h-56 bg-gradient-to-br from-indigo-600 via-purple-500 to-pink-400 rounded-lg flex items-center justify-center">
                <img src={illustration} alt="AI graphic" className="h-full w-full object-contain" />
              </div>
            </div>
          </div>
        </section>

        <section className="mt-20 px-6 py-12 bg-gradient-to-r from-blue-900/20 to-purple-900/20 animate-fade-in">
          <h2 className="text-3xl font-bold mb-12 text-center">Key Features</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 rounded-2xl bg-white/5 backdrop-blur hover:bg-white/10 transform transition hover:scale-105 shadow-lg feature-card border border-white/10">
              <div className="text-3xl mb-3">📊</div>
              <h3 className="font-bold text-lg">ATS Score Analysis</h3>
              <p className="mt-2 text-sm text-slate-300">Optimize your resume for applicant tracking systems.</p>
            </div>
            <div className="p-6 rounded-2xl bg-white/5 backdrop-blur hover:bg-white/10 transform transition hover:scale-105 shadow-lg feature-card border border-white/10">
              <div className="text-3xl mb-3">⚡</div>
              <h3 className="font-bold text-lg">Skill Gap Detection</h3>
              <p className="mt-2 text-sm text-slate-300">Identify missing skills for target roles.</p>
            </div>
            <div className="p-6 rounded-2xl bg-white/5 backdrop-blur hover:bg-white/10 transform transition hover:scale-105 shadow-lg feature-card border border-white/10">
              <div className="text-3xl mb-3">✨</div>
              <h3 className="font-bold text-lg">Resume Suggestions</h3>
              <p className="mt-2 text-sm text-slate-300">Improve phrasing and structure with AI.</p>
            </div>
            <div className="p-6 rounded-2xl bg-white/5 backdrop-blur hover:bg-white/10 transform transition hover:scale-105 shadow-lg feature-card border border-white/10">
              <div className="text-3xl mb-3">🎯</div>
              <h3 className="font-bold text-lg">Job Description Matching</h3>
              <p className="mt-2 text-sm text-slate-300">Match your resume to job descriptions.</p>
            </div>
          </div>
        </section>

        <section className="mt-12 px-6 py-16 text-center">
          <h2 className="text-3xl font-bold mb-8">Ready to Improve Your Resume?</h2>
          <button onClick={handleUpload} className="px-8 py-4 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-600 shadow-2xl hover:scale-110 transform transition btn-glow font-bold text-lg">Start Analyzing Now</button>
        </section>

        <footer className="mt-20 px-6 py-12 bg-black/30 border-t border-white/10 text-center text-slate-400">
          <p>© 2026 AI Resume Analyzer. All rights reserved.</p>
          <div className="mt-4 flex justify-center gap-6">
            <a href="#" className="hover:text-white transition">Privacy</a>
            <a href="#" className="hover:text-white transition">Terms</a>
            <a href="#" className="hover:text-white transition">Contact</a>
          </div>
        </footer>
      </div>
    </main>
  )
}
