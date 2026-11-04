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

/** Largest axis-aligned square inside the silhouette, in 200-unit coordinates (cached). */
const plateCache = {}
const findPlate = (shape) => {
  if (plateCache[shape.id]) return plateCache[shape.id]
  const N = 400
  const k = N / 200
  const canvas = document.createElement('canvas')
  canvas.width = canvas.height = N
  const ctx = canvas.getContext('2d')
  ctx.scale(k, k)
  paintShape(ctx, shape, '#000')
  const alpha = ctx.getImageData(0, 0, N, N).data
  // classic "maximal square" dynamic programme over the mask
  const dp = new Uint16Array(N * N)
  let best = 0
  for (let y = 0; y < N; y++) {
    for (let x = 0; x < N; x++) {
      if (alpha[(y * N + x) * 4 + 3] < 250) continue
      const i = y * N + x
      dp[i] = x && y ? Math.min(dp[i - 1], dp[i - N], dp[i - N - 1]) + 1 : 1
      if (dp[i] > best) best = dp[i]
    }
  }
  // among near-largest squares, prefer the one nearest the horizontal centre
  let pick = null
  for (let y = 0; y < N; y++) {
    for (let x = 0; x < N; x++) {
      const s = dp[y * N + x]
      if (s < best - 2) continue
      const cx = x - s / 2
      const score = Math.abs(cx - N / 2) - s * 4
      if (!pick || score < pick.score) pick = { score, x: x - s + 1, y: y - s + 1, s }
    }
  }
  const plate = { x: pick.x / k, y: pick.y / k, size: pick.s / k }
  plateCache[shape.id] = plate
  return plate
}

/**
 * Render a QR code for `text` inside `shapeId`, filled with `color`.
 * Returns a square canvas (transparent around the silhouette).
 */
export const renderShapedQr = (text, { shapeId = 'plain', color = '#1d1a2b', size = 1200, ink = '#1d1a2b' } = {}) => {
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
    plate = { x: 4, y: 4, size: 192 }
  } else {
    ctx.save()
    ctx.scale(k, k)
    paintShape(ctx, shape, color)
    ctx.restore()
    const fit = findPlate(shape)
    const inset = fit.size * 0.06
    plate = { x: fit.x + inset, y: fit.y + inset, size: fit.size - inset * 2 }
  }

  // white plate with a quiet zone of 2 modules (3 for the plain code)
  const quiet = shape.parts.length ? 2 : 3
  const px = plate.x * k
  const py = plate.y * k
  const ps = plate.size * k
  const radius = ps * 0.07
  ctx.fillStyle = '#ffffff'
  ctx.beginPath()
  ctx.roundRect(px, py, ps, ps, radius)
  ctx.fill()

  const cell = ps / (n + quiet * 2)
  const ox = px + quiet * cell
  const oy = py + quiet * cell
  ctx.fillStyle = ink
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      if (!cells[r * n + c]) continue
      // snap to whole pixels and overlap slightly so modules never show hairline seams
      const x0 = Math.floor(ox + c * cell)
      const y0 = Math.floor(oy + r * cell)
      const x1 = Math.ceil(ox + (c + 1) * cell)
      const y1 = Math.ceil(oy + (r + 1) * cell)
      ctx.fillRect(x0, y0, x1 - x0, y1 - y0)
    }
  }
  return canvas
}
