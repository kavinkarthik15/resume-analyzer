import React, { useEffect, useState } from 'react'
import QualityBar from './QualityBar'

export default function RewriteCard({ title, data, onAccept, onRevert, onToggleLock, onSaveEdit }) {
  const [showWhy, setShowWhy] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editedText, setEditedText] = useState(data?.original || '')
  const explanation = data?.explanation || {}
  const isLocked = Boolean(data?.locked)

  useEffect(() => {
    if (!isEditing) {
      setEditedText(data?.original || '')
    }
  }, [data?.original, isEditing])

  const handleSave = () => {
    if (!onSaveEdit) return
    onSaveEdit(editedText)
    setIsEditing(false)
  }

  return (
    <div
      style={{
        border: isEditing ? '2px solid #4f46e5' : isLocked ? '2px solid #f59e0b' : '1px solid #e2e8f0',
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '20px',
        background: '#ffffff',
        opacity: isLocked ? 0.75 : 1,
        transition: 'all 0.2s ease',
      }}
      title={isLocked ? 'Locked section will not be modified' : undefined}
    >
      <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '12px', color: '#0f172a' }}>
        {title} {isLocked ? '🔒' : ''}
      </h3>
      {isEditing && (
        <p style={{ fontSize: '13px', color: '#4338ca', fontWeight: 600, marginBottom: '10px' }}>
          Editing...
        </p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <p style={{ fontWeight: 600, marginBottom: '6px', color: '#334155' }}>Original</p>
          {isEditing ? (
            <textarea
              value={editedText}
              onChange={(event) => setEditedText(event.target.value)}
              style={{
                width: '100%',
                minHeight: '120px',
                padding: '10px',
                borderRadius: '8px',
                border: '1px solid #cbd5e1',
                resize: 'vertical',
                color: '#1f2937',
                background: '#ffffff',
              }}
            />
          ) : (
            <div
              style={{
                background: '#f8fafc',
                padding: '10px',
                borderRadius: '8px',
                minHeight: '100px',
                whiteSpace: 'pre-wrap',
                color: '#1f2937',
              }}
            >
              {data?.original || 'No content found for this section.'}
            </div>
          )}
        </div>

        <div>
          <p style={{ fontWeight: 600, marginBottom: '6px', color: '#166534' }}>AI Rewrite</p>
          <div
            style={{
              background: '#f0fdf4',
              padding: '10px',
              borderRadius: '8px',
              minHeight: '100px',
              whiteSpace: 'pre-wrap',
              color: '#14532d',
            }}
          >
            {data?.rewritten || data?.original || 'No rewrite available for this section.'}
          </div>
        </div>
      </div>

      <div style={{ marginTop: '12px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <button
          type="button"
          onClick={() => setIsEditing(true)}
          disabled={isLocked || isEditing}
          style={{
            border: '1px solid #4f46e5',
            color: '#4338ca',
            background: '#eef2ff',
            borderRadius: '8px',
            padding: '8px 12px',
            cursor: isLocked || isEditing ? 'not-allowed' : 'pointer',
            fontWeight: 600,
            opacity: isLocked || isEditing ? 0.5 : 1,
          }}
        >
          Edit
        </button>
        <button
          type="button"
          onClick={onAccept}
          disabled={isLocked || isEditing}
          style={{
            border: '1px solid #16a34a',
            color: '#166534',
            background: '#f0fdf4',
            borderRadius: '8px',
            padding: '8px 12px',
            cursor: isLocked || isEditing ? 'not-allowed' : 'pointer',
            fontWeight: 600,
            opacity: isLocked || isEditing ? 0.5 : 1,
          }}
        >
          Accept
        </button>
        <button
          type="button"
          onClick={onRevert}
          disabled={isLocked || isEditing}
          style={{
            border: '1px solid #94a3b8',
            color: '#334155',
            background: '#f8fafc',
            borderRadius: '8px',
            padding: '8px 12px',
            cursor: isLocked || isEditing ? 'not-allowed' : 'pointer',
            fontWeight: 600,
            opacity: isLocked || isEditing ? 0.5 : 1,
          }}
        >
          Revert
        </button>
        <button
          type="button"
          onClick={onToggleLock}
          title="Locked section will not be modified"
          disabled={isEditing}
          style={{
            border: isLocked ? '1px solid #f59e0b' : '1px solid #94a3b8',
            color: isLocked ? '#92400e' : '#334155',
            background: isLocked ? '#fffbeb' : '#ffffff',
            borderRadius: '8px',
            padding: '8px 12px',
            cursor: isEditing ? 'not-allowed' : 'pointer',
            fontWeight: 600,
            opacity: isEditing ? 0.5 : 1,
          }}
        >
          {isLocked ? '🔒 Locked' : '🔓 Editable'}
        </button>
        <button
          type="button"
          onClick={() => setShowWhy((value) => !value)}
          disabled={isEditing}
          style={{
            border: '1px solid #0f172a',
            color: '#0f172a',
            background: '#ffffff',
            borderRadius: '8px',
            padding: '8px 12px',
            cursor: isEditing ? 'not-allowed' : 'pointer',
            fontWeight: 600,
            opacity: isEditing ? 0.5 : 1,
          }}
        >
          {showWhy ? 'Hide Details' : 'Explain Why'}
        </button>
      </div>

      {isEditing && (
        <div style={{ marginTop: '10px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button
            type="button"
            onClick={handleSave}
            style={{
              border: '1px solid #16a34a',
              color: '#166534',
              background: '#f0fdf4',
              borderRadius: '8px',
              padding: '8px 12px',
              cursor: 'pointer',
              fontWeight: 600,
            }}
          >
            Save
          </button>
          <button
            type="button"
            onClick={() => {
              setIsEditing(false)
              setEditedText(data?.original || '')
            }}
            style={{
              border: '1px solid #94a3b8',
              color: '#334155',
              background: '#f8fafc',
              borderRadius: '8px',
              padding: '8px 12px',
              cursor: 'pointer',
              fontWeight: 600,
            }}
          >
            Cancel
          </button>
        </div>
      )}

      {data?.quality && (
        <div
          style={{
            marginTop: '12px',
            padding: '12px',
            background: '#f9fafb',
            borderRadius: '10px',
            border: '1px solid #e2e8f0',
          }}
        >
          <h4 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '10px', color: '#0f172a' }}>
            Quality Improvement
          </h4>
          <QualityBar
            label="Clarity"
            before={data.quality.before.clarity}
            after={data.quality.after.clarity}
          />
          <QualityBar
            label="ATS Alignment"
            before={data.quality.before.ats}
            after={data.quality.after.ats}
          />
          <QualityBar
            label="Keyword Coverage"
            before={data.quality.before.keywords}
            after={data.quality.after.keywords}
          />
          <QualityBar
            label="Action Strength"
            before={data.quality.before.action}
            after={data.quality.after.action}
          />
        </div>
      )}

      {showWhy && (
        <div
          className="explain-panel"
          style={{
            marginTop: '12px',
            padding: '12px',
            background: '#f8fafc',
            borderRadius: '10px',
            border: '1px solid #e2e8f0',
          }}
        >
          <div style={{ marginBottom: '12px' }}>
            <h4 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '6px', color: '#0f172a' }}>
              What Changed
            </h4>
            {explanation?.changes?.length > 0 ? (
              <ul style={{ paddingLeft: '18px', color: '#334155' }}>
                {explanation.changes.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            ) : (
              <p style={{ color: '#64748b' }}>No structural changes were detected for this section.</p>
            )}
          </div>

          <div style={{ marginBottom: '12px' }}>
            <h4 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '6px', color: '#0f172a' }}>
              Why It Helps
            </h4>
            {explanation?.why?.length > 0 ? (
              <ul style={{ paddingLeft: '18px', color: '#334155' }}>
                {explanation.why.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            ) : (
              <p style={{ color: '#64748b' }}>This rewrite improves readability and keyword clarity.</p>
            )}
          </div>

          <div>
            <h4 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '6px', color: '#0f172a' }}>
              Keywords Added
            </h4>
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
              {explanation?.keywords_added?.length > 0 ? (
                explanation.keywords_added.map((keyword, index) => (
                  <span
                    key={index}
                    style={{
                      background: '#e0f2fe',
                      color: '#075985',
                      padding: '4px 8px',
                      borderRadius: '6px',
                      fontSize: '12px',
                    }}
                  >
                    {keyword}
                  </span>
                ))
              ) : (
                <span style={{ color: '#64748b', fontSize: '13px' }}>No new keywords were added.</span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
