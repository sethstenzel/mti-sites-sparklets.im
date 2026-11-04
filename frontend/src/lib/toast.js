import { reactive } from 'vue'

export const toasts = reactive([])
let nextId = 1

export const toast = (text, { tone = 'default', duration = 2600 } = {}) => {
  const id = nextId++
  toasts.push({ id, text, tone })
  setTimeout(() => {
    const index = toasts.findIndex((t) => t.id === id)
    if (index !== -1) toasts.splice(index, 1)
  }, duration)
}

export const copyText = async (text, label = 'Link copied') => {
  try {
    await navigator.clipboard.writeText(text)
    toast(label, { tone: 'ok' })
    return true
  } catch {
    toast('Couldn’t copy automatically. Select the link and copy it.', { tone: 'error' })
    return false
  }
}
