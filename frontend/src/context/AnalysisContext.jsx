import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const AnalysisContext = createContext(null)

const ANALYSIS_KEY = 'analysis'
const LEGACY_ANALYSIS_KEY = 'analysisResult'
const ANALYSIS_HISTORY_KEY = 'analysis_history'
const MAX_HISTORY_ITEMS = 10

function parseStoredAnalysis(raw) {
  if (!raw) return null

  try {
    return JSON.parse(raw)
  } catch (error) {
    console.error('Failed to parse saved analysis result:', error)
    return null
  }
}

export function AnalysisProvider({ children }) {
  const [analysisResult, setAnalysisResultState] = useState(null)
  const [history, setHistory] = useState([])

  // Load persisted analysis once on app startup.
  useEffect(() => {
    const saved = localStorage.getItem(ANALYSIS_KEY)
    const legacySaved = localStorage.getItem(LEGACY_ANALYSIS_KEY)
    const parsed = parseStoredAnalysis(saved) || parseStoredAnalysis(legacySaved)

    if (parsed) {
      setAnalysisResultState(parsed)
      if (!saved) {
        localStorage.setItem(ANALYSIS_KEY, JSON.stringify(parsed))
      }
    } else if (saved || legacySaved) {
      localStorage.removeItem(ANALYSIS_KEY)
      localStorage.removeItem(LEGACY_ANALYSIS_KEY)
    }
  }, [])

  // Load persisted analysis history once on app startup.
  useEffect(() => {
    const savedHistory = localStorage.getItem(ANALYSIS_HISTORY_KEY)
    const parsedHistory = parseStoredAnalysis(savedHistory)

    if (Array.isArray(parsedHistory)) {
      setHistory(parsedHistory)
      return
    }

    if (savedHistory) {
      localStorage.removeItem(ANALYSIS_HISTORY_KEY)
    }
  }, [])

  // Persist analysis changes for refresh resilience.
  useEffect(() => {
    try {
      if (analysisResult) {
        localStorage.setItem(ANALYSIS_KEY, JSON.stringify(analysisResult))
        localStorage.setItem(LEGACY_ANALYSIS_KEY, JSON.stringify(analysisResult))
      } else {
        localStorage.removeItem(ANALYSIS_KEY)
        localStorage.removeItem(LEGACY_ANALYSIS_KEY)
      }
    } catch (error) {
      console.error('Failed to persist analysis result:', error)
    }
  }, [analysisResult])

  // Persist history updates.
  useEffect(() => {
    try {
      localStorage.setItem(ANALYSIS_HISTORY_KEY, JSON.stringify(history))
    } catch (error) {
      console.error('Failed to persist analysis history:', error)
    }
  }, [history])

  const setAnalysisResult = (nextResult) => {
    setAnalysisResultState(nextResult)
  }

  const clearAnalysis = () => {
    setAnalysisResultState(null)
    try {
      localStorage.removeItem(ANALYSIS_KEY)
      localStorage.removeItem(LEGACY_ANALYSIS_KEY)
    } catch (error) {
      console.error('Failed to clear analysis result:', error)
    }
  }

  const addToHistory = (analysis, fileName = 'Resume', jobDescription = '') => {
    if (!analysis) return

    const newEntry = {
      id: `${Date.now()}-${Math.floor(Math.random() * 10000)}`,
      date: new Date().toISOString(),
      fileName,
      jobDescription,
      result: analysis,
    }

    setHistory((prev) => [newEntry, ...prev].slice(0, MAX_HISTORY_ITEMS))
  }

  const clearHistory = () => {
    setHistory([])
    try {
      localStorage.removeItem(ANALYSIS_HISTORY_KEY)
    } catch (error) {
      console.error('Failed to clear analysis history:', error)
    }
  }

  const value = useMemo(
    () => ({
      analysisResult,
      setAnalysisResult,
      clearAnalysis,
      history,
      addToHistory,
      clearHistory,
    }),
    [analysisResult, history]
  )

  return (
    <AnalysisContext.Provider value={value}>
      {children}
    </AnalysisContext.Provider>
  )
}

export function useAnalysis() {
  const context = useContext(AnalysisContext)

  if (!context) {
    throw new Error('useAnalysis must be used within AnalysisProvider')
  }

  return context
}