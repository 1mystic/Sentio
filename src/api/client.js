import axios from 'axios'
import { useAuthStore } from '@/stores/auth.js'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// Attach Supabase JWT as Bearer token
client.interceptors.request.use((config) => {
  try {
    const auth = useAuthStore()
    const token = auth.session?.access_token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  } catch {}
  return config
})

// Normalize errors
client.interceptors.response.use(
  (res) => res,
  (err) => {
    const message = err.response?.data?.detail || err.message || 'Request failed'
    return Promise.reject(new Error(message))
  }
)

export default client
