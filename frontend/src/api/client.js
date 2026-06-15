import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
})

export const getCols = (params) => api.get('/cols/', { params })
export const getAscents = (colId, params) => api.get(`/cols/${colId}/ascents`, { params })
export const getAllAscents = (params) => api.get('/cols/ascents/all', { params })
export const getStravaStatus = () => api.get('/auth/strava/status')
export const getGarminStatus = () => api.get('/auth/garmin/status')
export const connectGarmin = (email, password) => api.post('/auth/garmin/connect', null, { params: { email, password } })
export const triggerSync = () => api.post('/sync/trigger')

export default api
