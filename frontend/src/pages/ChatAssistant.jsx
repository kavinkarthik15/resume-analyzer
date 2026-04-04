import React, { useState, useRef, useEffect } from 'react';
import { chatAPI } from '../services/api';

export default function ChatAssistant() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      text: "Hello! I'm your AI Resume Assistant. I can answer questions about your ATS score, skill gaps, formatting, job description matching, role readiness, and more. Upload & analyze your resume first, then ask me anything!",
      suggestions: [],
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  /* Get resume ID and analysis context */
  const getResumeData = () => {
    try {
      const analysis = localStorage.getItem('analysisResult');
      if (analysis) {
        const parsed = JSON.parse(analysis);
        return {
          resume_id: parsed.resume_id,
          analysis: parsed
        };
      }
    } catch (e) {
      console.error('Failed to get resume data:', e);
    }
    return { resume_id: null, analysis: null };
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || loading) return;

    const { resume_id, analysis } = getResumeData();
    if (!resume_id) {
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'bot',
        text: 'Please upload and analyze your resume first before chatting.',
        suggestions: ['Go to Resume Analysis', 'Analyze your resume']
      }]);
      return;
    }

    const userMsg = { id: Date.now(), type: 'user', text: inputValue };
    setMessages(prev => [...prev, userMsg]);

    const question = inputValue;
    setInputValue('');
    setLoading(true);

    try {
      const response = await chatAPI.chat({
        resume_id: resume_id,
        question: question,
        context: analysis || undefined
      });

      const botMsg = {
        id: Date.now() + 1,
        type: 'bot',
        text: response.data.answer,
        suggestions: response.data.suggestions || [],
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (error) {
      console.error('Chat failed:', error);
      const errorMsg = error.response?.data?.detail || 'Sorry, I couldn\'t process your question right now. Please try again.';
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'bot',
        text: errorMsg,
        suggestions: []
      }]);
    } finally {
      setLoading(false);
    }
  };

  const suggestedQuestions = [
    'Why is my ATS score low?',
    'What skills should I add?',
    'How can I improve my resume?',
    'Am I missing any sections?',
    'Am I ready for a Data Scientist role?',
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 pt-32 pb-12 px-6">
      <div className="max-w-3xl mx-auto h-[calc(100vh-120px)] flex flex-col">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
            <span>💬</span> AI Resume Assistant
          </h1>
          <p className="text-slate-400">Ask questions about your resume analysis</p>
        </div>

        {/* Chat Container */}
        <div className="dashboard-card flex-1 flex flex-col mb-6 overflow-hidden">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto pr-4 space-y-4 py-6">
            {messages.map((msg) => (
              <div key={msg.id} className={`animate-fade-in ${msg.type === 'user' ? 'flex justify-end' : 'flex justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.type === 'user'
                    ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-br-sm'
                    : 'bg-white/10 text-slate-200 rounded-bl-sm'
                }`}>
                  <p>{msg.text}</p>

                  {/* Suggestions */}
                  {msg.suggestions?.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-white/10">
                      <p className="text-xs font-semibold text-slate-400 mb-2">💡 Suggestions:</p>
                      <ul className="space-y-1">
                        {msg.suggestions.map((s, i) => (
                          <li key={i} className="text-xs text-cyan-300 flex items-start gap-1.5">
                            <span>→</span>
                            <span>{s}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-white/10 rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-2 text-slate-400">
                  <span className="animate-pulse">●</span>
                  <span className="animate-pulse" style={{ animationDelay: '0.2s' }}>●</span>
                  <span className="animate-pulse" style={{ animationDelay: '0.4s' }}>●</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-white/10 pt-4">
            {/* Suggested Questions */}
            <div className="mb-4">
              <p className="text-xs text-slate-500 mb-2">Try asking:</p>
              <div className="flex flex-wrap gap-2">
                {suggestedQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => setInputValue(q)}
                    className="text-xs bg-white/5 hover:bg-white/10 border border-white/10 rounded-full px-3 py-1 text-slate-300 hover:text-white transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>

            {/* Input Field */}
            <div className="flex gap-3">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask me anything about your resume..."
                className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400"
                disabled={loading}
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || loading}
                className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 disabled:from-slate-600 disabled:to-slate-700 text-white px-6 py-3 rounded-xl font-semibold transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? '...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
