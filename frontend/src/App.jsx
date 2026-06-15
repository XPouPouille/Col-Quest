import React, { useState, useEffect } from 'react'
import Map from './components/Map'
import ColList from './components/ColList'
import Filters from './components/Filters'
import LoginModal from './components/LoginModal'
import { getCols, getAllAscents, getStravaStatus, getGarminStatus, triggerSync } from './api/client'

export default function App() {
  const [cols, setCols] = useState([])
  const [ascents, setAscents] = useState([])
  const [selectedCol, setSelectedCol] = useState(null)
  const [selectedAscent, setSelectedAscent] = useState(null)
  const [filters, setFilters] = useState({ minAltitude: 0, maxAltitude: 3000, dateFrom: '', dateTo: '' })
  const [stravaStatus, setStravaStatus] = useState({ connected: false })
  const [garminStatus, setGarminStatus] = useState({ connected: false })
  const [showLogin, setShowLogin] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const [toast, setToast] = useState(null)

  useEffect(() => {
    loadStatuses()
    loadData()
    const params = new URLSearchParams(window.location.search)
    if (params.get('connected') === 'strava') {
      showToast('Strava connecté avec succès !', 'success')
      window.history.replaceState({}, '', '/')
    }
  }, [])

  useEffect(() => { loadData() }, [filters])

  async function loadStatuses() {
    try {
      const [s, g] = await Promise.all([getStravaStatus(), getGarminStatus()])
      setStravaStatus(s.data)
      setGarminStatus(g.data)
    } catch (e) {
      // Backend not reachable yet
    }
  }

  async function loadData() {
    try {
      const params = {
        min_altitude: filters.minAltitude,
        max_altitude: filters.maxAltitude,
        ...(filters.dateFrom && { date_from: filters.dateFrom }),
        ...(filters.dateTo && { date_to: filters.dateTo }),
      }
      const [colsRes, ascentsRes] = await Promise.all([
        getCols({ min_altitude: filters.minAltitude, max_altitude: filters.maxAltitude }),
        getAllAscents(params)
      ])
      setCols(colsRes.data)
      setAscents(ascentsRes.data)
    } catch (e) {
      // Backend not reachable yet
    }
  }

  async function handleSync() {
    setSyncing(true)
    try {
      await triggerSync()
      showToast('Synchronisation lancée en arrière-plan', 'info')
      setTimeout(() => { loadData(); loadStatuses() }, 5000)
    } catch (e) {
      showToast('Erreur de synchronisation', 'error')
    } finally {
      setSyncing(false)
    }
  }

  function showToast(message, type = 'info') {
    setToast({ message, type })
    setTimeout(() => setToast(null), 4000)
  }

  const climbed = cols.filter(c => c.ascent_count > 0)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#0f172a', color: '#f1f5f9' }}>
      {/* Header */}
      <header style={{ padding: '12px 20px', borderBottom: '1px solid #1e293b', display: 'flex', alignItems: 'center', gap: 16, flexShrink: 0, background: '#0b1120' }}>
        <span style={{ fontSize: 24 }}>⛰️</span>
        <h1 style={{ margin: 0, fontSize: 20, fontWeight: 700, color: '#60a5fa' }}>Col Quest</h1>
        <span style={{ color: '#94a3b8', fontSize: 14 }}>
          {climbed.length} col{climbed.length > 1 ? 's' : ''} gravé{climbed.length > 1 ? 's' : ''}
          {cols.length > 0 && <span style={{ color: '#475569' }}> / {cols.length} total</span>}
        </span>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 8, alignItems: 'center' }}>
          <StatusBadge label="Strava" connected={stravaStatus.connected} />
          <StatusBadge label="Garmin" connected={garminStatus.connected} />
          <button onClick={() => setShowLogin(true)} style={btnStyle('#1e293b')}>Connexion</button>
          <button onClick={handleSync} disabled={syncing} style={btnStyle('#3b82f6')}>
            {syncing ? '⏳ Sync...' : '🔄 Synchroniser'}
          </button>
        </div>
      </header>

      {/* Body */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Sidebar */}
        <div style={{ width: 320, borderRight: '1px solid #1e293b', display: 'flex', flexDirection: 'column', overflow: 'hidden', flexShrink: 0 }}>
          <Filters filters={filters} onChange={setFilters} />
          <ColList
            cols={cols}
            ascents={ascents}
            selected={selectedCol}
            onSelect={setSelectedCol}
            onSelectAscent={setSelectedAscent}
          />
        </div>
        {/* Map */}
        <div style={{ flex: 1, position: 'relative' }}>
          <Map
            cols={cols}
            ascents={ascents}
            selectedCol={selectedCol}
            selectedAscent={selectedAscent}
            onSelectCol={setSelectedCol}
          />
        </div>
      </div>

      {showLogin && (
        <LoginModal
          onClose={() => { setShowLogin(false); loadStatuses() }}
          stravaStatus={stravaStatus}
          garminStatus={garminStatus}
        />
      )}

      {toast && (
        <div style={{
          position: 'fixed', bottom: 24, right: 24,
          background: toast.type === 'success' ? '#16a34a' : toast.type === 'error' ? '#dc2626' : '#3b82f6',
          color: 'white', padding: '12px 20px', borderRadius: 8,
          boxShadow: '0 4px 20px rgba(0,0,0,0.4)', zIndex: 9999, fontWeight: 600,
          animation: 'fadeIn 0.2s ease'
        }}>
          {toast.message}
        </div>
      )}
    </div>
  )
}

function StatusBadge({ label, connected }) {
  return (
    <span style={{
      fontSize: 12, padding: '4px 10px', borderRadius: 20,
      background: connected ? '#14532d' : '#1e293b',
      color: connected ? '#22c55e' : '#64748b',
      border: `1px solid ${connected ? '#22c55e' : '#334155'}`
    }}>
      {connected ? '✓' : '○'} {label}
    </span>
  )
}

function btnStyle(bg) {
  return {
    background: bg, color: '#f1f5f9', border: '1px solid #334155',
    borderRadius: 6, padding: '6px 14px', cursor: 'pointer',
    fontSize: 13, fontWeight: 500, transition: 'opacity 0.15s'
  }
}
