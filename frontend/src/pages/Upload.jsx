import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, CheckCircle2, Upload as UploadIcon } from 'lucide-react';
import { resumeAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useAnalysis } from '../context/AnalysisContext';

export default function Upload() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const { user } = useAuth();
  const { setAnalysisResult } = useAnalysis();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/login');
    }
  }, [user, navigate]);

  if (!user) {
    return null;
  }

  function handleFile(e) {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileName(selectedFile.name);
      setError('');
    }
  }

  async function handleAnalyze(e) {
    e.preventDefault();
    
    // Validation: File required
    if (!file) {
      setError('Please select a resume file to upload.');
      return;
    }
    
    // Validation: File size (2MB limit)
    const maxSize = 2 * 1024 * 1024; // 2MB
    if (file.size > maxSize) {
      setError(`File size must be under 2MB. Your file is ${(file.size / 1024 / 1024).toFixed(1)}MB.`);
      return;
    }
    
    // Validation: File type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const extension = file.name.split('.').pop().toLowerCase();
    if (!allowedTypes.includes(file.type) && !['pdf', 'doc', 'docx'].includes(extension)) {
      setError('Please upload a PDF or Word document (.pdf, .doc, .docx)');
      return;
    }

    setIsAnalyzing(true);
    setError('');

    try {
      const response = await resumeAPI.uploadAndAnalyze(file, jobDescription.trim() || null);
      const result = response.data;

      // Store result in localStorage for the results page
      localStorage.setItem('analysisResult', JSON.stringify(result));
      setAnalysisResult(result);

      // Navigate to results page
      navigate('/results');
    } catch (err) {
      console.error('Analysis failed:', err);
      
      let errorMsg = 'Analysis failed. Please try again.';
      if (err.message === 'Network Error' || err.code === 'ECONNABORTED') {
        errorMsg = 'Server is waking up, please wait a few seconds and try again.';
      } else if (err.response?.status === 404) {
        errorMsg = 'Backend service is initializing. Please wait a moment and try again.';
      } else if (err.response?.data?.detail) {
        errorMsg = err.response.data.detail;
      }
      
      setError(errorMsg);
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <div className="w-full min-h-screen bg-gradient-to-br from-[#f7f7f4] via-[#f4f6f8] to-[#eef2f7] px-6 pt-24 pb-12">
      <div className="max-w-3xl mx-auto rounded-3xl border border-slate-200 bg-white shadow-sm p-8">
        <div className="max-w-xl text-left">
          <h2 className="text-2xl font-semibold mb-2 text-slate-900">Upload your resume</h2>
          <p className="text-slate-500 mb-6">Upload your resume to get instant job-match and ATS insights.</p>
        </div>

        {error && (
          <div className="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-red-700 mb-4">
            <AlertCircle size={16} strokeWidth={1.5} className="opacity-80 mt-0.5" />
            <p>{error}</p>
          </div>
        )}

        <div style={{ marginBottom: '16px' }}>
          <label htmlFor="job-description" style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>
            Job Description
          </label>
          <textarea
            id="job-description"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste Job Description here..."
            rows={6}
            style={{
              width: '100%',
              padding: '12px',
              borderRadius: '8px',
              border: '1px solid #d1d5db',
              background: '#fff',
              color: '#111827',
              resize: 'vertical',
              marginBottom: '8px'
            }}
          />
          <p style={{ fontSize: '13px', color: '#6b7280', margin: 0 }}>
            Paste a job description to compare it against your resume.
          </p>
        </div>

        <form onSubmit={handleAnalyze}>
          <div className="file-input-container">
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={handleFile}
              id="resume-file"
              style={{ display: 'none' }}
            />
            <label
              htmlFor="resume-file"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-300 bg-white hover:bg-slate-100 transition cursor-pointer mb-4"
            >
              <UploadIcon size={16} strokeWidth={1.5} className="opacity-80" />
              Choose file
            </label>
          </div>

          {fileName && (
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg border border-emerald-200 bg-emerald-50 text-emerald-800 mb-4">
              <CheckCircle2 size={16} strokeWidth={1.5} className="opacity-80" />
              {fileName}
            </div>
          )}

          <button
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-black text-white hover:bg-slate-800 transition"
            type="submit"
            disabled={isAnalyzing || !file}
            style={{
              opacity: (isAnalyzing || !file) ? 0.6 : 1,
              cursor: (isAnalyzing || !file) ? 'not-allowed' : 'pointer'
            }}
          >
            <UploadIcon size={16} strokeWidth={1.5} className="opacity-80" />
            {isAnalyzing ? 'Analyzing...' : 'Analyze Resume'}
          </button>
        </form>

        <div className="upload-info" style={{ marginTop: '24px', fontSize: '14px', color: '#6b7280' }}>
          <p style={{ marginBottom: '12px', fontSize: '12px', color: '#9ca3af', fontStyle: 'italic' }}>
            <strong>Tip:</strong> Upload a real resume with skills, projects, and experience for best results. File size must be under 2MB.
          </p>
          <p><strong>What happens next?</strong></p>
          <ul style={{ paddingLeft: '20px', lineHeight: '1.6' }}>
            <li>AI analyzes your resume content and structure</li>
            <li>Calculates ATS compatibility score</li>
            <li>Identifies skill gaps and improvement suggestions</li>
            <li>Provides ML-powered shortlist probability</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
