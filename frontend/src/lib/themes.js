export const themes = [
  // everyday
  { name: 'Classic', background_color: '#fff8dc', card_color: '#fffacd', text_color: '#2f4f4f' },
  { name: 'Bubblegum', background_color: '#ffd9e6', card_color: '#ffffff', text_color: '#7a1e48' },
  { name: 'Mint', background_color: '#d6f2e4', card_color: '#fbfffd', text_color: '#1f4d3a' },
  { name: 'Sky', background_color: '#dbe9ff', card_color: '#ffffff', text_color: '#1d3a6b' },
  { name: 'Sunset', background_color: '#ffd8b8', card_color: '#fff6ec', text_color: '#7a2e12' },
  { name: 'Midnight', background_color: '#1d1b3a', card_color: '#2b2858', text_color: '#f5e9c8' },
  // holidays and seasons, roughly in calendar order
  { name: 'Valentine’s', background_color: '#e8456b', card_color: '#fff0f3', text_color: '#a3153b' },
  { name: 'Chinese New Year', background_color: '#c3161c', card_color: '#ffe7a3', text_color: '#9e1515' },
  { name: 'St. Patrick’s', background_color: '#2f9e5a', card_color: '#f2fff5', text_color: '#165c33' },
  { name: 'Easter', background_color: '#e5dcff', card_color: '#fffbe3', text_color: '#5a4a9c' },
  { name: 'Cherry Blossom', background_color: '#fbd3e0', card_color: '#fff8fa', text_color: '#9c2f5a' },
  { name: 'Seaside', background_color: '#a8e1ef', card_color: '#fffbf0', text_color: '#0f5a74' },
  { name: 'Birthday', background_color: '#ffe066', card_color: '#ffffff', text_color: '#b8124e' },
  { name: 'Halloween', background_color: '#221a2b', card_color: '#ff8a2a', text_color: '#221a2b' },
  { name: 'Thanks­giving', background_color: '#d9803f', card_color: '#fff4e3', text_color: '#6b3410' },
  { name: 'Diwali', background_color: '#5b1a7a', card_color: '#ffd76a', text_color: '#5b1a7a' },
  { name: 'Hanukkah', background_color: '#24489e', card_color: '#f3f7ff', text_color: '#1f3d88' },
  { name: 'Christmas', background_color: '#b3202a', card_color: '#fdf8ee', text_color: '#1f5132' }
]

export const defaultTheme = themes[0]

export const matchesTheme = (data, theme) =>
  ['background_color', 'card_color', 'text_color'].every(
    (key) => (data[key] || '').toLowerCase() === theme[key]
  )

/** Pick black or white for legible text over an arbitrary hex background. */
export const contrastInk = (hex) => {
  const value = (hex || '#ffffff').replace('#', '')
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(value.slice(i, i + 2), 16) / 255)
  const lum = [r, g, b].map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4))
  const L = 0.2126 * lum[0] + 0.7152 * lum[1] + 0.0722 * lum[2]
  return L > 0.4 ? 'light' : 'dark'
}

/** Blend a hex color toward black (amount > 0) or white (amount < 0). */
export const shade = (hex, amount) => {
  const value = (hex || '#ffffff').replace('#', '')
  const target = amount > 0 ? 0 : 255
  const t = Math.abs(amount)
  return (
    '#' +
    [0, 2, 4]
      .map((i) => {
        const c = parseInt(value.slice(i, i + 2), 16)
        return Math.round(c + (target - c) * t).toString(16).padStart(2, '0')
      })
      .join('')
  )
}

const toHsl = (hex) => {
  const value = (hex || '#ffffff').replace('#', '')
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(value.slice(i, i + 2), 16) / 255)
  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  const l = (max + min) / 2
  if (max === min) return [0, 0, l * 100]
  const d = max - min
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min)
  const h = max === r ? (g - b) / d + (g < b ? 6 : 0) : max === g ? (b - r) / d + 2 : (r - g) / d + 4
  return [h * 60, s * 100, l * 100]
}

/**
 * Two visible tones of a background color (same hue, richer saturation) for decorations
 * drawn on top of it: deeper tones on light backgrounds, brighter tones on dark ones.
 */
export const tonesOf = (hex) => {
  const [h, s] = toHsl(hex)
  const sat = s < 8 ? s : Math.max(s, 65)
  const [l1, l2] = contrastInk(hex) === 'light' ? [58, 44] : [72, 84]
  return [`hsl(${h.toFixed(0)} ${sat.toFixed(0)}% ${l1}%)`, `hsl(${h.toFixed(0)} ${sat.toFixed(0)}% ${l2}%)`]
}
