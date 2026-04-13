import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, CheckCircle2, Upload as UploadIcon } from 'lucide-react';
import { jdAPI, resumeAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useAnalysis } from '../context/AnalysisContext';
import { saveResumeAnalysis } from '../services/firestoreService';

export default function Upload() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [roleData, setRoleData] = useState({
    role: '',
    experience: '',
    workType: '',
    location: '',
    skills: '',
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [loadingJD, setLoadingJD] = useState(false);
  const [error, setError] = useState('');
  const { user } = useAuth();
  const { setAnalysisResult, addToHistory } = useAnalysis();
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

  async function handleGenerateJD() {
    if (!roleData.role.trim() || !roleData.experience.trim()) {
      alert('Fill role and experience first');
      return;
    }

    setLoadingJD(true);

    try {
      const response = await jdAPI.generate(roleData);
      setJobDescription(response.data.job_description || '');
      setError('');
    } catch (err) {
      alert('Failed to generate JD');
    } finally {
      setLoadingJD(false);
    }
  }

  async function handleAnalyze(e) {
    e.preventDefault();
    
    // Validation: File required
    if (!file) {
      setError('Please select a resume file to upload.');
      return;
    }

    if (!roleData.role.trim() || !roleData.experience.trim()) {
      setError('Please fill role and experience.');
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
      const response = await resumeAPI.uploadAndAnalyze(file, {
        job_description: jobDescription.trim() || null,
        role_data: roleData,
      });
      const result = response.data;
      const trimmedJobDescription = jobDescription.trim();

      setAnalysisResult(result);
      addToHistory(result, file.name, trimmedJobDescription);

      if (user) {
        try {
          await saveResumeAnalysis(user.uid, {
            ...result,
            fileName: file.name,
          });
        } catch (saveError) {
          console.error('Failed to persist resume analysis:', saveError);
        }
      }

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

        <div className="mb-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500 mb-3">Role details</h3>
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
            className="mb-2 w-full resize-y rounded-lg border border-slate-300 !bg-white px-3 py-3 !text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-300"
          />
          <button
            type="button"
            onClick={handleGenerateJD}
            disabled={loadingJD}
            className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 hover:bg-slate-100 transition disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loadingJD ? 'Generating...' : '✨ Generate Job Description'}
          </button>
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
