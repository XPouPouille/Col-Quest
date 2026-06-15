import React from 'react'

export default function Filters({ filters, onChange }) {
  const update = (key, val) => onChange(prev => ({ ...prev, [key]: val }))

  const inputStyle = {
    background: '#1e293b', border: '1px solid #334155', color: '#f1f5f9',
    borderRadius: 4, padding: '5px 8px', fontSize: 12, width: '100%',
    outline: 'none',
  }
  const labelStyle = { fontSize: 11, color: '#94a3b8', marginBottom: 3, display: 'block' }

  return (
    <div style={{ padding: 12, borderBottom: '1px solid #1e293b', flexShrink: 0 }}>
      <div style={{ fontSize: 11, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 10 }}>
        Filtres
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
        <div>
          <label style={labelStyle}>Altitude min (m)</label>
          <input
            type="number" style={inputStyle}
            value={filters.minAltitude}
            onChange={e => update('minAltitude', Number(e.target.value))}
            min={0} max={3000} step={100}
          />
        </div>
        <div>
          <label style={labelStyle}>Altitude max (m)</label>
          <input
            type="number" style={inputStyle}
            value={filters.maxAltitude}
            onChange={e => update('maxAltitude', Number(e.target.value))}
            min={0} max={3000} step={100}
          />
        </div>
        <div>
          <label style={labelStyle}>Date début</label>
          <input
            type="date" style={inputStyle}
            value={filters.dateFrom}
            onChange={e => update('dateFrom', e.target.value)}
          />
        </div>
        <div>
          <label style={labelStyle}>Date fin</label>
          <input
            type="date" style={inputStyle}
            value={filters.dateTo}
            onChange={e => update('dateTo', e.target.value)}
          />
        </div>
      </div>
      <button
        onClick={() => onChange({ minAltitude: 0, maxAltitude: 3000, dateFrom: '', dateTo: '' })}
        style={{
          marginTop: 8, fontSize: 11, color: '#64748b', background: 'none',
          border: '1px solid #334155', borderRadius: 4, padding: '4px 10px',
          cursor: 'pointer', width: '100%'
        }}
      >
        Réinitialiser les filtres
      </button>
    </div>
  )
}
