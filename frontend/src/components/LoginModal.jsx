import React, { useState } from 'react'
import { connectGarmin } from '../api/client'

export default function LoginModal({ onClose, stravaStatus, garminStatus }) {
  const [garminEmail, setGarminEmail] = useState('')
  const [garminPassword, setGarminPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const API_URL = import.meta.env.VITE_API_URL || '/api'

  async function handleGarminConnect() {
    setLoading(true)
    setError('')
    setSuccess('')
    try {
      await connectGarmin(garminEmail, garminPassword)
      setSuccess('Garmin Connect connecté avec succès !')
      setTimeout(onClose, 1500)
    } catch (e) {
      setError(e.response?.data?.detail || 'Erreur de connexion Garmin. Vérifiez vos identifiants.')
    } finally {
      setLoading(false)
    }
  }

  const inputStyle = {
    background: '#1e293b', border: '1px solid #334155', color: '#f1f5f9',
    borderRadius: 6, padding: '8px 12px', fontSize: 14, width: '100%',
    boxSizing: 'border-box', outline: 'none',
  }

  return (
    <div
      onClick={(e) => { if (e.target === e.currentTarget) onClose() }}
      style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
      }}
    >
      <div style={{
        background: '#1e293b', border: '1px solid #334155', borderRadius: 12,
        padding: 28, width: 380, maxWidth: '90vw',
        boxShadow: '0 20px 60px rgba(0,0,0,0.6)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <h2 style={{ margin: 0, fontSize: 18, color: '#f1f5f9' }}>⛰️ Connexion</h2>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: 22, cursor: 'pointer', lineHeight: 1 }}
          >×</button>
        </div>

        {/* Strava Section */}
        <div style={{ marginBottom: 16, padding: 16, background: '#0f172a', borderRadius: 8 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <span style={{ fontWeight: 600, color: '#f1f5f9' }}>🟠 Strava</span>
            {stravaStatus.connected && <span style={{ fontSize: 12, color: '#22c55e', fontWeight: 600 }}>✓ Connecté</span>}
          </div>
          <a
            href={`${API_URL}/auth/strava/login`}
            style={{
              display: 'block', textAlign: 'center',
              background: '#fc4c02', color: 'white',
              padding: '9px 0', borderRadius: 6, textDecoration: 'none',
              fontWeight: 700, fontSize: 14,
            }}
          >
            {stravaStatus.connected ? '🔄 Reconnecter Strava' : 'Se connecter avec Strava'}
          </a>
          <div style={{ fontSize: 11, color: '#475569', marginTop: 8 }}>
            Redirige vers Strava pour autoriser l'accès à vos activités.
          </div>
        </div>

        {/* Garmin Section */}
        <div style={{ padding: 16, background: '#0f172a', borderRadius: 8 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <span style={{ fontWeight: 600, color: '#f1f5f9' }}>🔵 Garmin Connect</span>
            {garminStatus.connected && <span style={{ fontSize: 12, color: '#22c55e', fontWeight: 600 }}>✓ Connecté</span>}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <input
              type="email" placeholder="Email Garmin Connect"
              style={inputStyle} value={garminEmail}
              onChange={e => setGarminEmail(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleGarminConnect()}
            />
            <input
              type="password" placeholder="Mot de passe"
              style={inputStyle} value={garminPassword}
              onChange={e => setGarminPassword(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleGarminConnect()}
            />
            {error && (
              <div style={{ fontSize: 12, color: '#ef4444', padding: '6px 10px', background: '#450a0a', borderRadius: 4 }}>
                {error}
              </div>
            )}
            {success && (
              <div style={{ fontSize: 12, color: '#22c55e', padding: '6px 10px', background: '#052e16', borderRadius: 4 }}>
                {success}
              </div>
            )}
            <button
              onClick={handleGarminConnect}
              disabled={loading || !garminEmail || !garminPassword}
              style={{
                background: loading || !garminEmail || !garminPassword ? '#1e3a5f' : '#1d4ed8',
                color: 'white', border: 'none', borderRadius: 6,
                padding: '9px 0', cursor: loading || !garminEmail || !garminPassword ? 'not-allowed' : 'pointer',
                fontWeight: 700, fontSize: 14, transition: 'background 0.15s'
              }}
            >
              {loading ? 'Connexion en cours...' : 'Se connecter'}
            </button>
            <div style={{ fontSize: 11, color: '#475569', lineHeight: 1.5 }}>
              Vos identifiants sont transmis uniquement à votre serveur et stockés de façon chiffrée. Ils ne quittent jamais votre infrastructure.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
