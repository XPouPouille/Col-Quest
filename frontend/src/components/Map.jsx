import React, { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Inline polyline decoder (Google encoded polyline format)
function decodePolyline(str) {
  if (!str) return []
  let index = 0, lat = 0, lng = 0, coordinates = []
  while (index < str.length) {
    let b, shift = 0, result = 0
    do { b = str.charCodeAt(index++) - 63; result |= (b & 0x1f) << shift; shift += 5 } while (b >= 0x20)
    lat += (result & 1) ? ~(result >> 1) : (result >> 1)
    shift = 0; result = 0
    do { b = str.charCodeAt(index++) - 63; result |= (b & 0x1f) << shift; shift += 5 } while (b >= 0x20)
    lng += (result & 1) ? ~(result >> 1) : (result >> 1)
    coordinates.push([lat / 1e5, lng / 1e5])
  }
  return coordinates
}

export default function Map({ cols, ascents, selectedCol, selectedAscent, onSelectCol }) {
  const mapRef = useRef(null)
  const mapInstanceRef = useRef(null)
  const markersRef = useRef({})
  const polylineRef = useRef(null)

  // Init map once
  useEffect(() => {
    if (mapInstanceRef.current) return
    const map = L.map(mapRef.current, { center: [45.5, 7.0], zoom: 7, zoomControl: true })
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 19
    }).addTo(map)
    mapInstanceRef.current = map
    return () => {
      map.remove()
      mapInstanceRef.current = null
    }
  }, [])

  // Update markers when cols/ascents change
  useEffect(() => {
    const map = mapInstanceRef.current
    if (!map) return

    // Remove old markers
    Object.values(markersRef.current).forEach(m => m.remove())
    markersRef.current = {}

    cols.forEach(col => {
      const climbed = col.ascent_count > 0
      const size = climbed ? Math.max(10, Math.min(22, (col.altitude - 500) / 110)) : 7

      const icon = L.divIcon({
        className: '',
        html: `<div style="
          width:${size}px;height:${size}px;border-radius:50%;
          background:${climbed ? '#3b82f6' : '#475569'};
          border:2px solid ${climbed ? '#93c5fd' : '#64748b'};
          box-shadow:${climbed ? '0 0 8px rgba(59,130,246,0.6)' : 'none'};
          cursor:pointer;
        "></div>`,
        iconSize: [size, size],
        iconAnchor: [size / 2, size / 2],
      })

      const marker = L.marker([col.latitude, col.longitude], { icon })
      marker.on('click', () => onSelectCol(col))

      const lastAscent = ascents
        .filter(a => a.col_id === col.id)
        .sort((a, b) => new Date(b.date) - new Date(a.date))[0]

      marker.bindPopup(`
        <div style="min-width:190px;font-family:system-ui,sans-serif;color:#0f172a">
          <div style="font-weight:700;font-size:14px;margin-bottom:4px">${col.name}</div>
          <div style="color:#475569;font-size:12px;margin-bottom:6px">⛰️ ${col.altitude}m &nbsp;•&nbsp; ${col.country}</div>
          ${climbed
            ? `<div style="color:#16a34a;font-size:12px;font-weight:600">✓ ${col.ascent_count} ascension${col.ascent_count > 1 ? 's' : ''}</div>
               ${lastAscent ? `<div style="font-size:11px;color:#64748b;margin-top:2px">Dernière : ${new Date(lastAscent.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })}</div>` : ''}`
            : `<div style="color:#94a3b8;font-size:12px">Non gravé</div>`
          }
        </div>
      `)

      marker.addTo(map)
      markersRef.current[col.id] = marker
    })
  }, [cols, ascents])

  // Show polyline for selected ascent
  useEffect(() => {
    if (polylineRef.current) { polylineRef.current.remove(); polylineRef.current = null }
    if (!selectedAscent?.polyline || !mapInstanceRef.current) return
    const coords = decodePolyline(selectedAscent.polyline)
    if (coords.length === 0) return
    polylineRef.current = L.polyline(coords, { color: '#f59e0b', weight: 3, opacity: 0.9 })
      .addTo(mapInstanceRef.current)
    mapInstanceRef.current.fitBounds(polylineRef.current.getBounds(), { padding: [40, 40] })
  }, [selectedAscent])

  // Pan to selected col
  useEffect(() => {
    if (!selectedCol || !mapInstanceRef.current) return
    const marker = markersRef.current[selectedCol.id]
    if (marker) {
      mapInstanceRef.current.setView([selectedCol.latitude, selectedCol.longitude], 13, { animate: true })
      marker.openPopup()
    }
  }, [selectedCol])

  return <div ref={mapRef} style={{ width: '100%', height: '100%' }} />
}
