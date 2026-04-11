import { createContext, useContext, useMemo, useState } from 'react'

const AnalysisContext = createContext(null)

function readStoredAnalysis() {
  try {
    const raw = localStorage.getItem('analysisResult')
    return raw ? JSON.parse(raw) : null
  } catch (error) {
    console.error('Failed to read stored analysis result:', error)
    return null
  }
}

export function AnalysisProvider({ children }) {
  const [analysisResult, setAnalysisResultState] = useState(() => readStoredAnalysis())

  const setAnalysisResult = (nextResult) => {
    setAnalysisResultState(nextResult)

    try {
      if (nextResult) {
        localStorage.setItem('analysisResult', JSON.stringify(nextResult))
      } else {
        localStorage.removeItem('analysisResult')
      }
    } catch (error) {
      console.error('Failed to persist analysis result:', error)
    }
  }

  const value = useMemo(
    () => ({ analysisResult, setAnalysisResult }),
    [analysisResult]
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