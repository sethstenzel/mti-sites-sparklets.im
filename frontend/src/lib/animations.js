export const animations = [
  { id: 'drop', name: 'Drop', hint: 'Falls in and settles' },
  { id: 'flip', name: 'Flip', hint: 'Turns over to reveal' },
  { id: 'twirl', name: 'Twirl', hint: 'Spins into place' },
  { id: 'rise', name: 'Rise', hint: 'Slides up like it’s leaving an envelope' },
  { id: 'pop', name: 'Pop', hint: 'Bursts in with sparkles' },
  { id: 'none', name: 'None', hint: 'Just appears' }
]

export const defaultAnimation = 'drop'

export const isAnimation = (id) => animations.some((a) => a.id === id)
