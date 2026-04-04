import React, {useEffect, useState} from 'react'

export default function AuthModal({open, mode='login', onClose, onSwitch, onLoginSuccess}){
  const [name, setName] = useState('')

  useEffect(()=>{
    function onKey(e){ if(e.key === 'Escape') onClose() }
    if(open) window.addEventListener('keydown', onKey)
    return ()=> window.removeEventListener('keydown', onKey)
  },[open,onClose])

  const handleSubmit = (e) => {
    e.preventDefault()
    const nameValue = mode === 'register' ? name : 'User'
    onLoginSuccess(nameValue)
  }

  if(!open) return null

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center animate-fade-in">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-md" onClick={onClose}></div>

      <div className="relative z-50 w-full max-w-md mx-4 transform transition-all">
        <div className="bg-white/10 border border-white/30 backdrop-blur-2xl rounded-3xl p-8 shadow-2xl">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-3xl font-bold text-white">{mode === 'login' ? '👋 Welcome Back' : '✨ Create Account'}</h3>
            <button className="text-white/70 hover:text-white text-2xl transition" onClick={onClose}>✕</button>
          </div>

          {mode === 'login' ? (
            <form className="space-y-5" onSubmit={handleSubmit}>
              <div>
                <label className="block text-sm font-semibold text-white/90 mb-2">Email</label>
                <input className="w-full p-3 rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:border-blue-400 focus:bg-white/10 transition" type="email" placeholder="you@example.com" required />
              </div>
              <div>
                <label className="block text-sm font-semibold text-white/90 mb-2">Password</label>
                <input className="w-full p-3 rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:border-blue-400 focus:bg-white/10 transition" type="password" placeholder="••••••••" required />
              </div>
              <button className="w-full py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold btn-glow hover:scale-110 transition">Sign In</button>
              <p className="text-sm text-white/70 text-center">Don't have an account? <button type="button" className="text-blue-300 hover:text-blue-200 font-semibold underline transition" onClick={()=>onSwitch('register')}>Register</button></p>
            </form>
          ) : (
            <form className="space-y-5" onSubmit={handleSubmit}>
              <div>
                <label className="block text-sm font-semibold text-white/90 mb-2">Name</label>
                <input className="w-full p-3 rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:border-blue-400 focus:bg-white/10 transition" type="text" placeholder="John Doe" value={name} onChange={(e)=>setName(e.target.value)} required />
              </div>
              <div>
                <label className="block text-sm font-semibold text-white/90 mb-2">Email</label>
                <input className="w-full p-3 rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:border-blue-400 focus:bg-white/10 transition" type="email" placeholder="you@example.com" required />
              </div>
              <div>
                <label className="block text-sm font-semibold text-white/90 mb-2">Password</label>
                <input className="w-full p-3 rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:border-blue-400 focus:bg-white/10 transition" type="password" placeholder="••••••••" required />
              </div>
              <div>
                <label className="block text-sm font-semibold text-white/90 mb-2">Confirm Password</label>
                <input className="w-full p-3 rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:border-blue-400 focus:bg-white/10 transition" type="password" placeholder="••••••••" required />
              </div>
              <button className="w-full py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold btn-glow hover:scale-110 transition">Create Account</button>
              <p className="text-sm text-white/70 text-center">Already have an account? <button type="button" className="text-blue-300 hover:text-blue-200 font-semibold underline transition" onClick={()=>onSwitch('login')}>Login</button></p>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
