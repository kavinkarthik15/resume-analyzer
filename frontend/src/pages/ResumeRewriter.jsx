import React from 'react';

export default function ResumeRewriter() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 pt-32 pb-12 px-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">AI Resume Rewriter</h1>
          <p className="text-slate-400">Advanced resume optimization coming soon</p>
        </div>

        {/* Coming Soon Card */}
        <div className="dashboard-card mb-6 text-center py-16">
          <div className="mb-6">
            <div className="text-6xl mb-4">🚀</div>
            <h2 className="text-3xl font-bold mb-3">Coming Soon</h2>
            <p className="text-slate-400 max-w-2xl mx-auto text-lg">
              We're working on an exciting new resume rewriter feature that will help you optimize your bullet points for maximum ATS compatibility and impact.
            </p>
          </div>
          <div className="mt-8 p-6 bg-white/5 rounded-xl border border-white/10">
            <p className="text-sm text-slate-300">
              In the meantime, you can:
            </p>
            <ul className="mt-4 text-sm text-slate-300 space-y-2">
              <li>✓ Upload and analyze your resume</li>
              <li>✓ Compare with job descriptions</li>
              <li>✓ Get AI-powered improvement suggestions</li>
              <li>✓ View your ATS compatibility score</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

