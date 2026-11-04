import { ref } from 'vue'

export const STORAGE_KEY = 'sparklets.siteTheme'

export const siteThemes = [
  { id: 'neutral', name: 'Neutral', hint: 'Soft white, charcoal and rose', colors: ['#fbf9fa', '#c7a1b2', '#2b2329'], meta: '#fbf9fa' },
  { id: 'blush', name: 'Blush', hint: 'Soft pink and violet', colors: ['#fbf7fb', '#a66cff', '#ff3d6e'], meta: '#fbf7fb' },
  { id: 'slate', name: 'Slate', hint: 'Graphite, blue and cyan', colors: ['#0e1318', '#22d3ee', '#3b82f6'], meta: '#0e1318' }
]

const valid = (id) => siteThemes.some((t) => t.id === id)

// index.html applies the saved theme before the app loads; start from whatever it set.
const initial = document.documentElement.dataset.theme
export const siteTheme = ref(valid(initial) ? initial : 'neutral')

export const setSiteTheme = (id) => {
  if (!valid(id)) return
  siteTheme.value = id
  document.documentElement.dataset.theme = id
  const meta = document.querySelector('meta[name="theme-color"]')
  if (meta) meta.setAttribute('content', siteThemes.find((t) => t.id === id).meta)
  try {
    localStorage.setItem(STORAGE_KEY, id)
  } catch {
    /* storage blocked: the choice lasts for this visit only */
  }
}
