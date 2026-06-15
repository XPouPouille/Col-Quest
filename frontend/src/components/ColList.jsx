import React, { useState } from 'react'
import { getAscents } from '../api/client'

function formatDuration(seconds) {
  if (!seconds) return ''
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  return h > 0 ? `${h}h${String(m).padStart(2, '0')}` : `${m}min`
}

export default function ColList({ cols, ascents, selected, onSelect, onSelectAscent }) {
  const [expandedCol, setExpandedCol] = useState(null)
  const [colAscents, setColAscents] = useState({})

  const climbed = cols.filter(c => c.ascent_count > 0).sort((a, b) => b.altitude - a.altitude)
  const unclimbed = cols.filter(c => c.ascent_count === 0).sort((a, b) => b.altitude - a.altitude)

  async function handleExpand(col) {
    if (expandedCol === col.id) {
      setExpandedCol(null)
      return
    }
    setExpandedCol(col.id)
    onSelect(col)
    if (!colAscents[col.id]) {
      try {
        const res = await getAscents(col.id)
        setColAscents(prev => ({ ...prev, [col.id]: res.data }))
      } catch (e) {
        setColAscents(prev => ({ ...prev, [col.id]: [] }))
      }
    }
  }

  const sectionHeader = (label) => (
    <div style={{
      padding: '8px 14px', fontSize: 11, fontWeight: 700, color: '#64748b',
      textTransform: 'uppercase', letterSpacing: 1,
      borderBottom: '1px solid #1e293b', background: '#0b1120',
      position: 'sticky', top: 0, zIndex: 1
    }}>
      {label}
    </div>
  )

  return (
    <div style={{ flex: 1, overflowY: 'auto' }}>
      {climbed.length > 0 && (
        <>
          {sectionHeader(`Cols gravis (${climbed.length})`)}
          {climbed.map(col => (
            <div key={col.id}>
              <div
                onClick={() => handleExpand(col)}
                style={{
                  padding: '10px 14px', cursor: 'pointer', borderBottom: '1px solid #1e293b',
                  background: selected?.id === col.id ? '#1e3a5f' : 'transparent',
                  transition: 'background 0.15s',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, fontSize: 14 }}>{col.name}</span>
                  <span style={{ fontSize: 12, color: '#22c55e', fontWeight: 700 }}>{col.altitude}m</span>
                </div>
                <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
                  {col.country} &nbsp;•&nbsp; {col.ascent_count} ascension{col.ascent_count > 1 ? 's' : ''}
                  {col.last_ascent && ` • ${new Date(col.last_ascent).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })}`}
                </div>
              </div>

              {expandedCol === col.id && (
                <div style={{ background: '#080d18', borderBottom: '1px solid #1e293b' }}>
                  {!colAscents[col.id] && (
                    <div style={{ padding: '10px 20px', color: '#64748b', fontSize: 12 }}>Chargement...</div>
                  )}
                  {colAscents[col.id]?.length === 0 && (
                    <div style={{ padding: '10px 20px', color: '#64748b', fontSize: 12 }}>Aucune ascension enregistrée.</div>
                  )}
                  {colAscents[col.id]?.map(a => (
                    <div
                      key={a.id}
                      onClick={() => onSelectAscent(a)}
                      style={{
                        padding: '9px 20px', cursor: 'pointer',
                        borderBottom: '1px solid #0f172a',
                        borderLeft: '3px solid #3b82f6',
                      }}
                    >
                      <div style={{ fontSize: 12, fontWeight: 600, color: '#93c5fd' }}>
                        {new Date(a.date).toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })}
                        <span style={{ marginLeft: 8, fontSize: 10, color: '#475569', fontWeight: 400 }}>
                          via {a.source}
                        </span>
                      </div>
                      <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 3, display: 'flex', flexWrap: 'wrap', gap: '4px 12px' }}>
                        {a.distance_km > 0 && <span>📏 {a.distance_km} km</span>}
                        {a.duration_seconds > 0 && <span>⏱ {formatDuration(a.duration_seconds)}</span>}
                        {a.avg_speed_kmh > 0 && <span>⚡ {a.avg_speed_kmh} km/h</span>}
                        {a.avg_gradient_pct > 0 && <span>📐 {a.avg_gradient_pct}%</span>}
                        {a.elevation_gain_m > 0 && <span>↑ {a.elevation_gain_m}m</span>}
                      </div>
                      {a.activity_name && (
                        <div style={{ fontSize: 11, color: '#64748b', marginTop: 2, fontStyle: 'italic' }}>
                          {a.activity_name}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </>
      )}

      {unclimbed.length > 0 && (
        <>
          {sectionHeader(`À gravir (${unclimbed.length})`)}
          {unclimbed.map(col => (
            <div
              key={col.id}
              onClick={() => { onSelect(col) }}
              style={{
                padding: '9px 14px', cursor: 'pointer', borderBottom: '1px solid #1e293b',
                background: selected?.id === col.id ? '#1e293b' : 'transparent',
                transition: 'background 0.15s',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: 13, color: '#94a3b8' }}>{col.name}</span>
                <span style={{ fontSize: 12, color: '#475569' }}>{col.altitude}m</span>
              </div>
              <div style={{ fontSize: 11, color: '#334155' }}>{col.country}</div>
            </div>
          ))}
        </>
      )}

      {cols.length === 0 && (
        <div style={{ padding: 24, color: '#475569', textAlign: 'center', fontSize: 13 }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>⛰️</div>
          <div>Connexion au backend...</div>
          <div style={{ marginTop: 8, fontSize: 11 }}>Assurez-vous que le backend est démarré.</div>
        </div>
      )}
    </div>
  )
}
