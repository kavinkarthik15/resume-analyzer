import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { resumeAPI } from '../services/api';

export default function Upload() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

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
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setIsAnalyzing(true);
    setError('');

    try {
      const response = await resumeAPI.uploadAndAnalyze(file);
      const result = response.data;

      // Store result in localStorage for the results page
      localStorage.setItem('analysisResult', JSON.stringify(result));

      // Navigate to results page
      navigate('/results');
    } catch (err) {
      console.error('Analysis failed:', err);
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <div className="page page-upload">
      <div className="upload-panel glass-card">
        <h2>📄 Upload Your Resume</h2>
        <p>Upload your resume (PDF or DOCX) and get AI-powered analysis</p>

        {error && (
          <div className="error-message" style={{
            color: '#ef4444',
            background: '#fef2f2',
            padding: '12px',
            borderRadius: '8px',
            marginBottom: '16px',
            border: '1px solid #fecaca'
          }}>
            ⚠️ {error}
          </div>
        )}

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
              className="file-input-label"
              style={{
                display: 'inline-block',
                padding: '12px 24px',
                background: '#f3f4f6',
                border: '2px dashed #d1d5db',
                borderRadius: '8px',
                cursor: 'pointer',
                marginBottom: '16px',
                transition: 'all 0.2s'
              }}
            >
              📎 Choose File
            </label>
          </div>

          {fileName && (
            <div className="file-name" style={{
              padding: '8px 12px',
              background: '#ecfdf5',
              border: '1px solid #d1fae5',
              borderRadius: '6px',
              marginBottom: '16px',
              color: '#065f46'
            }}>
              ✅ {fileName}
            </div>
          )}

          <button
            className="btn primary"
            type="submit"
            disabled={isAnalyzing || !file}
            style={{
              opacity: (isAnalyzing || !file) ? 0.6 : 1,
              cursor: (isAnalyzing || !file) ? 'not-allowed' : 'pointer'
            }}
          >
            {isAnalyzing ? '🔄 Analyzing...' : '🚀 Analyze Resume'}
          </button>
        </form>

        <div className="upload-info" style={{ marginTop: '24px', fontSize: '14px', color: '#6b7280' }}>
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
