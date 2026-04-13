import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAnalysis } from '../context/AnalysisContext'

export default function History() {
  const navigate = useNavigate()
  const { history, setAnalysisResult, clearHistory } = useAnalysis()

  function handleView(item) {
    setAnalysisResult(item.result)
    navigate('/results')
  }

  const items = history

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#07102a] via-[#0f2b4f] to-[#0b0620] text-white pt-24 px-6 pb-10">
      <div className="max-w-5xl mx-auto">
        <div className="mb-6 flex items-center justify-between gap-4">
          <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">Analysis History</h1>
          <button onClick={clearHistory} className="px-4 py-2 rounded-full border border-slate-300 hover:bg-white/10 transition">Clear History</button>
        </div>

        {items.length === 0 ? (
          <div className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-6">
            <p className="text-slate-200">No previous analysis found.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {items.map((item) => (
              <div key={item.id} className="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl p-5">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                  <div>
                    <p className="text-lg font-semibold">{item.fileName || 'Resume'}</p>
                    <p className="text-sm text-slate-300">{new Date(item.date).toLocaleString()}</p>
                    <p className="text-sm text-slate-200 mt-1">
                      Score: {item.result?.match_score ?? item.result?.score ?? item.result?.ats_analysis?.score ?? 0}%
                    </p>
                    {item.jobDescription && (
                      <p className="text-xs text-slate-400 mt-1">
                        JD: {item.jobDescription.slice(0, 120)}{item.jobDescription.length > 120 ? '...' : ''}
                      </p>
                    )}
                  </div>
                  <button onClick={() => handleView(item)} className="px-4 py-2 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:scale-105 transform transition font-semibold">
                    View Result
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}
