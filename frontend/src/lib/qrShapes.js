import QRCode from 'qrcode'

/*
 * QR codes framed inside a fun silhouette.
 *
 * Every shape is drawn in a 200×200 box as one or more "parts" (filled separately, so
 * overlapping parts simply union). The QR sits on a white plate placed in the largest
 * square that fits inside the silhouette, found from a raster mask, so any shape works
 * without hand-tuning and the code always has a clean quiet zone to scan.
 */

const circle = (cx, cy, r) => `M${cx - r} ${cy}a${r} ${r} 0 1 1 ${2 * r} 0a${r} ${r} 0 1 1 ${-2 * r} 0Z`
const ellipse = (cx, cy, rx, ry) => `M${cx - rx} ${cy}a${rx} ${ry} 0 1 1 ${2 * rx} 0a${rx} ${ry} 0 1 1 ${-2 * rx} 0Z`
const rrect = (x, y, w, h, r) =>
  `M${x + r} ${y}h${w - 2 * r}a${r} ${r} 0 0 1 ${r} ${r}v${h - 2 * r}a${r} ${r} 0 0 1 ${-r} ${r}` +
  `h${-(w - 2 * r)}a${r} ${r} 0 0 1 ${-r} ${-r}v${-(h - 2 * r)}a${r} ${r} 0 0 1 ${r} ${-r}Z`

const starPath = (cx, cy, R, r, points = 5) => {
  let d = ''
  for (let i = 0; i < points * 2; i++) {
    const rad = i % 2 === 0 ? R : r
    const a = (Math.PI / points) * i - Math.PI / 2
    d += `${i === 0 ? 'M' : 'L'}${(cx + rad * Math.cos(a)).toFixed(1)} ${(cy + rad * Math.sin(a)).toFixed(1)}`
  }
  return `${d}Z`
}

const petals = Array.from({ length: 6 }, (_, i) => {
  const a = (Math.PI / 3) * i - Math.PI / 2
  return { d: circle(+(100 + 56 * Math.cos(a)).toFixed(1), +(100 + 56 * Math.sin(a)).toFixed(1), 40) }
})

export const qrShapes = [
  { id: 'plain', name: 'Plain', parts: [] },
  {
    id: 'heart',
    name: 'Heart',
    parts: [{ d: 'M100 184C42 142 8 106 10 64C12 30 40 12 68 14C84 15 95 26 100 38C105 26 116 15 132 14C160 12 188 30 190 64C192 106 158 142 100 184Z' }]
  },
  { id: 'star', name: 'Star', parts: [{ d: starPath(100, 110, 98, 60), stroke: 14 }] },
  {
    id: 'egg',
    name: 'Easter egg',
    parts: [{ d: 'M100 6C152 6 184 92 184 130C184 172 148 196 100 196C52 196 16 172 16 130C16 92 48 6 100 6Z' }]
  },
  {
    id: 'tree',
    name: 'Christmas tree',
    parts: [{ d: 'M100 8L148 66H130L170 118H150L192 168H112V194H88V168H8L50 118H30L70 66H52Z', stroke: 10 }]
  },
  {
    id: 'present',
    name: 'Present',
    parts: [{ d: rrect(14, 60, 172, 34, 8) }, { d: rrect(24, 90, 152, 104, 8) }, { d: ellipse(70, 40, 30, 20) }, { d: ellipse(130, 40, 30, 20) }, { d: circle(100, 50, 14) }]
  },
  {
    id: 'ornament',
    name: 'Ornament',
    parts: [{ d: circle(100, 118, 78) }, { d: rrect(80, 26, 40, 22, 5) }, { d: circle(100, 16, 11) + circle(100, 16, 5), rule: 'evenodd' }]
  },
  {
    id: 'pumpkin',
    name: 'Pumpkin',
    parts: [{ d: ellipse(62, 120, 48, 70) }, { d: ellipse(138, 120, 48, 70) }, { d: ellipse(100, 118, 54, 76) }, { d: rrect(90, 18, 18, 34, 6) }]
  },
  {
    id: 'ghost',
    name: 'Ghost',
    parts: [{ d: 'M26 192V92C26 42 60 8 100 8C140 8 174 42 174 92V192L151 172L126 192L100 170L74 192L49 172Z' }]
  },
  {
    id: 'shamrock',
    name: 'Shamrock',
    parts: [
      { d: circle(100, 52, 44) },
      { d: circle(52, 110, 44) },
      { d: circle(148, 110, 44) },
      { d: circle(100, 98, 54) },
      { d: 'M94 128C98 156 92 178 74 194L86 199C106 180 112 156 108 128Z' }
    ]
  },
  {
    id: 'cake',
    name: 'Birthday cake',
    parts: [
      { d: rrect(16, 120, 168, 72, 12) },
      { d: rrect(38, 66, 124, 62, 12) },
      { d: rrect(93, 32, 14, 40, 4) },
      { d: 'M100 4C112 16 113 25 100 31C87 25 88 16 100 4Z' }
    ]
  },
  {
    id: 'balloon',
    name: 'Balloon',
    parts: [
      { d: ellipse(100, 82, 74, 80) },
      { d: 'M90 158H110L104 170H96Z' },
      { d: 'M98 168C90 178 108 186 98 198L102 199C113 186 95 178 103 168Z' }
    ]
  },
  { id: 'flower', name: 'Flower', parts: [...petals, { d: circle(100, 100, 58) }] },
  {
    id: 'bunny',
    name: 'Bunny',
    parts: [{ d: circle(100, 124, 74) }, { d: ellipse(70, 46, 18, 44) }, { d: ellipse(130, 46, 18, 44) }]
  },
  {
    id: 'cloud',
    name: 'Cloud',
    parts: [{ d: circle(58, 116, 42) }, { d: circle(98, 86, 54) }, { d: circle(146, 108, 44) }, { d: rrect(18, 108, 164, 68, 32) }]
  },
  { id: 'bubble', name: 'Speech bubble', parts: [{ d: rrect(8, 16, 184, 140, 32) }, { d: 'M42 148L32 192L90 148Z' }] }
]

const byId = Object.fromEntries(qrShapes.map((s) => [s.id, s]))

const paintShape = (ctx, shape, color) => {
  ctx.fillStyle = color
  ctx.strokeStyle = color
  ctx.lineJoin = 'round'
  for (const part of shape.parts) {
    const p = new Path2D(part.d)
    ctx.fill(p, part.rule || 'nonzero')
    if (part.stroke) {
      ctx.lineWidth = part.stroke
      ctx.stroke(p)
    }
  }
}

/**
 * Largest square that fits inside the silhouette, optionally turned 45° (a diamond).
 * Returns { cx, cy, size } in 200-unit shape coordinates (cached per shape + angle).
 *
 * The shape is rasterised in the plate's own frame (rotated by -angle), so the plate is
 * an axis-aligned square there and a classic "maximal square" DP finds it exactly.
 */
const plateCache = {}
const findPlate = (shape, diamond) => {
  const key = `${shape.id}:${diamond ? 45 : 0}`
  if (plateCache[key]) return plateCache[key]
  const k = 2 // raster pixels per shape unit
  const M = Math.ceil(200 * k * Math.SQRT2) // big enough for the rotated shape
  const angle = diamond ? -Math.PI / 4 : 0
  const canvas = document.createElement('canvas')
  canvas.width = canvas.height = M
  const ctx = canvas.getContext('2d', { willReadFrequently: true })
  ctx.translate(M / 2, M / 2)
  ctx.rotate(angle)
  ctx.scale(k, k)
  ctx.translate(-100, -100)
  paintShape(ctx, shape, '#000')
  const alpha = ctx.getImageData(0, 0, M, M).data

  const dp = new Uint16Array(M * M)
  let best = 0
  for (let y = 0; y < M; y++) {
    for (let x = 0; x < M; x++) {
      if (alpha[(y * M + x) * 4 + 3] < 250) continue
      const i = y * M + x
      dp[i] = x && y ? Math.min(dp[i - 1], dp[i - M], dp[i - M - 1]) + 1 : 1
      if (dp[i] > best) best = dp[i]
    }
  }
  // among near-largest squares, prefer the one nearest the shape's vertical axis
  let pick = null
  for (let y = 0; y < M; y++) {
    for (let x = 0; x < M; x++) {
      const s = dp[y * M + x]
      if (s < best - 2) continue
      // centre back in shape units (undo the rotation)
      const mx = (x - s / 2 + 0.5 - M / 2) / k
      const my = (y - s / 2 + 0.5 - M / 2) / k
      const sx = mx * Math.cos(-angle) - my * Math.sin(-angle) + 100
      const sy = mx * Math.sin(-angle) + my * Math.cos(-angle) + 100
      const score = Math.abs(sx - 100) - s * 4
      if (!pick || score < pick.score) pick = { score, cx: sx, cy: sy, size: s / k }
    }
  }
  const plate = { cx: pick.cx, cy: pick.cy, size: pick.size }
  plateCache[key] = plate
  return plate
}

/**
 * Render a QR code for `text` inside `shapeId`.
 *  - color:   fill of the silhouette
 *  - ink:     QR modules (normally near-black)
 *  - paper:   the plate behind the code (normally white)
 *  - diamond: turn the code 45°
 * Returns a square canvas, transparent around the silhouette.
 */
export const renderShapedQr = (
  text,
  { shapeId = 'plain', color = '#1d1a2b', size = 1200, ink = '#1d1a2b', paper = '#ffffff', diamond = false } = {}
) => {
  const shape = byId[shapeId] || byId.plain
  const qr = QRCode.create(text, { errorCorrectionLevel: 'M' })
  const n = qr.modules.size
  const cells = qr.modules.data

  const canvas = document.createElement('canvas')
  canvas.width = canvas.height = size
  const ctx = canvas.getContext('2d')
  const k = size / 200

  let plate
  if (!shape.parts.length) {
    plate = { cx: 100, cy: 100, size: diamond ? 192 / Math.SQRT2 : 192 }
  } else {
    ctx.save()
    ctx.scale(k, k)
    paintShape(ctx, shape, color)
    ctx.restore()
    const fit = findPlate(shape, diamond)
    plate = { cx: fit.cx, cy: fit.cy, size: fit.size * 0.88 }
  }

  // draw the plate and modules in the plate's own (possibly rotated) frame
  const ps = plate.size * k
  ctx.save()
  ctx.translate(plate.cx * k, plate.cy * k)
  if (diamond) ctx.rotate(Math.PI / 4)
  ctx.fillStyle = paper
  ctx.beginPath()
  ctx.roundRect(-ps / 2, -ps / 2, ps, ps, ps * 0.07)
  ctx.fill()

  // quiet zone of 2 modules (3 for the plain code); all modules filled as one path so
  // neighbouring squares never show anti-aliased seams, even when rotated
  const quiet = shape.parts.length ? 2 : 3
  const cell = ps / (n + quiet * 2)
  const o = -ps / 2 + quiet * cell
  const modules = new Path2D()
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      if (cells[r * n + c]) modules.rect(o + c * cell, o + r * cell, cell, cell)
    }
  }
  ctx.fillStyle = ink
  ctx.fill(modules)
  ctx.restore()
  return canvas
}
