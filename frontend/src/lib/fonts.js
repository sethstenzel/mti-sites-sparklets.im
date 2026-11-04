// Message fonts for a sparklet. `scale` evens out how big each face looks at the same
// font-size so a full 140-character note fits on the card in every font.
// Keep ids in sync with FONTS in backend/main.py.
export const fonts = [
  { id: 'kalam', name: 'Handwritten', family: "'Kalam', cursive", scale: 1 },
  { id: 'caveat', name: 'Script', family: "'Caveat', cursive", scale: 1.22 },
  { id: 'pacifico', name: 'Retro', family: "'Pacifico', cursive", scale: 0.86 },
  { id: 'fredoka', name: 'Rounded', family: "'Fredoka', sans-serif", scale: 0.95 },
  { id: 'playfair', name: 'Elegant', family: "'Playfair Display', serif", scale: 0.98, italic: true },
  { id: 'typewriter', name: 'Typewriter', family: "'Special Elite', monospace", scale: 0.88 }
]

export const defaultFont = 'kalam'

export const fontById = (id) => fonts.find((f) => f.id === id) || fonts[0]
