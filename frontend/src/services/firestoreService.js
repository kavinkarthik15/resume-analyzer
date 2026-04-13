import { db } from '../firebase'
import { doc, setDoc, serverTimestamp } from 'firebase/firestore'

export const saveResumeAnalysis = async (userId, analysis) => {
  try {
    const resumeId = Date.now().toString()

    await setDoc(doc(db, 'users', userId, 'resumes', resumeId), {
      title: analysis.fileName || 'Untitled Resume',
      currentVersionId: 'v1',
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp(),
    })

    await setDoc(doc(db, 'users', userId, 'resumes', resumeId, 'versions', 'v1'), {
      content: analysis,
      score: analysis.score || analysis.ats_score || analysis.match_score || 0,
      atsScore: analysis.match_score || analysis.ats_score || 0,
      createdAt: serverTimestamp(),
    })

    console.log('✅ Resume saved to Firestore')
    return resumeId
  } catch (error) {
    console.error('❌ Error saving resume:', error)
    throw error
  }
}
