import React from 'react'

export default function QualityBar({ label, before, after }) {
  const delta = after - before
  const isImprovement = after > before

  return (
    <div style={{ marginBottom: '10px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', marginBottom: '4px' }}>
        <span style={{ fontSize: '13px', fontWeight: 600, color: '#334155' }}>{label}</span>
        <span style={{ fontSize: '13px', color: '#475569' }}>
          {before}% → {after}%
          {isImprovement && <span style={{ color: '#16a34a', marginLeft: '6px' }}>+{delta}%</span>}
        </span>
      </div>

      <div
        style={{
          height: '6px',
          background: '#e5e7eb',
          borderRadius: '5px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: `${Math.max(0, Math.min(100, after))}%`,
            height: '100%',
            background: '#10b981',
          }}
        />
      </div>
    </div>
  )
}