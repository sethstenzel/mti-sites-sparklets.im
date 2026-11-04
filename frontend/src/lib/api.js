import axios from 'axios'

const TOKEN_KEY = 'sparklets.adminToken'

export const api = axios.create({ baseURL: '/' })

export const imageUrl = (filename) => (filename ? `/contents/imgs/${encodeURIComponent(filename)}` : '')

/** Sparklets are addressed only by their random public id. */
export const sparkletPath = (publicId) => `/s/${publicId}`

export const shareUrlFor = (publicId) => `${window.location.origin}${sparkletPath(publicId)}`

export const errorMessage = (err, fallback) => {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  if (err?.response?.status === 413) return 'That photo is too large. Try one under 10 MB.'
  if (!err?.response) return 'Can’t reach Sparklets right now. Check your connection and try again.'
  return fallback
}

export const getAdminToken = () => {
  try {
    return localStorage.getItem(TOKEN_KEY) || ''
  } catch {
    return ''
  }
}

export const setAdminToken = (token) => {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token)
    else localStorage.removeItem(TOKEN_KEY)
  } catch {
    /* storage unavailable: token lives only for this page view */
  }
}

export const adminHeaders = (token = getAdminToken()) => ({ 'X-Admin-Token': token })

export const buildSparkletForm = (data, imageFile) => {
  const form = new FormData()
  for (const key of ['to_name', 'from_name', 'message', 'background_color', 'card_color', 'text_color', 'entry_animation', 'font']) {
    form.append(key, data[key])
  }
  form.append('card_rotation', String(data.card_rotation))
  if (imageFile) form.append('image', imageFile)
  return form
}

/** Parse a server timestamp; legacy rows have no zone but are UTC. */
export const parseDate = (value) => {
  if (!value) return null
  const iso = /[zZ]|[+-]\d\d:?\d\d$/.test(value) ? value : `${value.replace(' ', 'T')}Z`
  const date = new Date(iso)
  return Number.isNaN(date.getTime()) ? null : date
}

const rtf = new Intl.RelativeTimeFormat(undefined, { numeric: 'auto' })

export const timeAgo = (value) => {
  const date = parseDate(value)
  if (!date) return ''
  const seconds = Math.round((date.getTime() - Date.now()) / 1000)
  const units = [
    ['year', 31536000],
    ['month', 2592000],
    ['week', 604800],
    ['day', 86400],
    ['hour', 3600],
    ['minute', 60]
  ]
  for (const [unit, size] of units) {
    if (Math.abs(seconds) >= size) return rtf.format(Math.round(seconds / size), unit)
  }
  return 'just now'
}
