import React from 'react'

function clampToPercent(value) {
  const num = Number(value)
  if (Number.isNaN(num)) return 0
  return Math.max(0, Math.min(100, Math.round(num)))
}

export default function ProgressBar({ label, value, color = '#4f46e5' }) {
  const safeValue = clampToPercent(value)

  return (
    <div style={{ marginBottom: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
        <span className="text-sm text-slate-700 font-medium">{label}</span>
        <span className="text-sm text-slate-900 font-semibold">{safeValue}%</span>
      </div>

      <div
        style={{
          height: '8px',
          background: '#e5e7eb',
          borderRadius: '999px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: `${safeValue}%`,
            height: '100%',
            background: color,
            transition: 'width 400ms ease',
          }}
        />
      </div>
    </div>
  )
}