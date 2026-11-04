<template>
  <div
    ref="frame"
    class="cropper"
    :class="{ dragging: pointers.size > 0 }"
    tabindex="0"
    role="application"
    aria-label="Photo framing. Drag or use arrow keys to move, plus and minus to zoom."
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="onPointerUp"
    @pointercancel="onPointerUp"
    @wheel.prevent="onWheel"
    @keydown="onKey"
  >
    <img
      ref="img"
      :src="src"
      alt=""
      draggable="false"
      :style="imageStyle"
      @load="onLoad"
    />
    <div v-if="showHint" class="hint">
      <Icon name="move" /> Drag to frame
    </div>
    <div class="tools" @pointerdown.stop>
      <button type="button" class="tool" aria-label="Zoom out" :disabled="zoom <= 1" @click="setZoom(zoom - 0.2)">
        <Icon name="zoomOut" />
      </button>
      <button type="button" class="tool" aria-label="Zoom in" :disabled="zoom >= MAX_ZOOM" @click="setZoom(zoom + 0.2)">
        <Icon name="zoomIn" />
      </button>
      <button type="button" class="tool" aria-label="Reset framing" @click="reset">
        <Icon name="reset" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import Icon from './Icon.vue'

const props = defineProps({
  src: { type: String, required: true },
  aspect: { type: Number, default: 3 / 2 },
  rotation: { type: Number, default: 0 },
  fileName: { type: String, default: 'sparklet.jpg' }
})

const MAX_ZOOM = 4
const OUTPUT_WIDTH = 1200

const frame = ref(null)
const img = ref(null)
const natural = reactive({ w: 0, h: 0 })
const zoom = ref(1)
// Centre of the visible window, as a fraction of the image's width/height.
const center = reactive({ u: 0.5, v: 0.5 })
const pointers = reactive(new Map())
const showHint = ref(true)
let pinchStart = null

// Rendered image size relative to the frame (1 = exactly fills that axis).
const coverW = computed(() => (natural.w ? Math.max(1, natural.w / natural.h / props.aspect) : 1))
const coverH = computed(() => (natural.w ? Math.max(1, props.aspect / (natural.w / natural.h)) : 1))
const relW = computed(() => coverW.value * zoom.value)
const relH = computed(() => coverH.value * zoom.value)

const clampCenter = () => {
  const halfU = 0.5 / relW.value
  const halfV = 0.5 / relH.value
  center.u = Math.min(1 - halfU, Math.max(halfU, center.u))
  center.v = Math.min(1 - halfV, Math.max(halfV, center.v))
}

const imageStyle = computed(() => ({
  width: `${relW.value * 100}%`,
  height: `${relH.value * 100}%`,
  left: `${(0.5 - center.u * relW.value) * 100}%`,
  top: `${(0.5 - center.v * relH.value) * 100}%`
}))

const onLoad = () => {
  natural.w = img.value.naturalWidth
  natural.h = img.value.naturalHeight
  reset()
}

const reset = () => {
  zoom.value = 1
  center.u = 0.5
  center.v = 0.5
}

const setZoom = (value) => {
  zoom.value = Math.min(MAX_ZOOM, Math.max(1, value))
  clampCenter()
}

watch(() => props.src, () => {
  showHint.value = true
})

// Pointer deltas are in screen space; undo the card tilt so drags feel natural.
const panBy = (dx, dy) => {
  const rect = frame.value.getBoundingClientRect()
  const width = frame.value.offsetWidth || rect.width
  const height = frame.value.offsetHeight || rect.height
  const angle = (-props.rotation * Math.PI) / 180
  const lx = dx * Math.cos(angle) - dy * Math.sin(angle)
  const ly = dx * Math.sin(angle) + dy * Math.cos(angle)
  center.u -= lx / (width * relW.value)
  center.v -= ly / (height * relH.value)
  clampCenter()
}

const distance = () => {
  const [a, b] = [...pointers.values()]
  return Math.hypot(a.x - b.x, a.y - b.y)
}

const onPointerDown = (e) => {
  if (e.button !== undefined && e.button !== 0) return
  frame.value.setPointerCapture?.(e.pointerId)
  pointers.set(e.pointerId, { x: e.clientX, y: e.clientY })
  showHint.value = false
  if (pointers.size === 2) pinchStart = { dist: distance(), zoom: zoom.value }
}

const onPointerMove = (e) => {
  const prev = pointers.get(e.pointerId)
  if (!prev) return
  e.preventDefault()
  const next = { x: e.clientX, y: e.clientY }
  if (pointers.size === 1) {
    panBy(next.x - prev.x, next.y - prev.y)
    pointers.set(e.pointerId, next)
  } else {
    pointers.set(e.pointerId, next)
    if (pinchStart) setZoom((pinchStart.zoom * distance()) / pinchStart.dist)
  }
}

const onPointerUp = (e) => {
  pointers.delete(e.pointerId)
  if (pointers.size < 2) pinchStart = null
}

const onWheel = (e) => {
  showHint.value = false
  setZoom(zoom.value * Math.exp(-e.deltaY * 0.0015))
}

const onKey = (e) => {
  const step = e.shiftKey ? 40 : 10
  const actions = {
    ArrowLeft: () => panBy(step, 0),
    ArrowRight: () => panBy(-step, 0),
    ArrowUp: () => panBy(0, step),
    ArrowDown: () => panBy(0, -step),
    '+': () => setZoom(zoom.value + 0.2),
    '=': () => setZoom(zoom.value + 0.2),
    '-': () => setZoom(zoom.value - 0.2),
    '0': reset
  }
  const action = actions[e.key]
  if (action) {
    e.preventDefault()
    showHint.value = false
    action()
  }
}

/** Render exactly what the frame shows into a JPEG file. */
const getCroppedFile = () =>
  new Promise((resolve, reject) => {
    if (!natural.w) {
      reject(new Error('Image not loaded yet'))
      return
    }
    const sw = natural.w / relW.value
    const sh = natural.h / relH.value
    const sx = center.u * natural.w - sw / 2
    const sy = center.v * natural.h - sh / 2
    const outW = Math.round(Math.min(OUTPUT_WIDTH, sw))
    const outH = Math.round(outW / props.aspect)

    const canvas = document.createElement('canvas')
    canvas.width = outW
    canvas.height = outH
    const ctx = canvas.getContext('2d')
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, outW, outH)
    ctx.imageSmoothingQuality = 'high'
    ctx.drawImage(img.value, sx, sy, sw, sh, 0, 0, outW, outH)

    canvas.toBlob(
      (blob) => {
        if (!blob) return reject(new Error('Could not process the photo'))
        const base = props.fileName.replace(/\.[^.]+$/, '') || 'sparklet'
        resolve(new File([blob], `${base}.jpg`, { type: 'image/jpeg', lastModified: Date.now() }))
      },
      'image/jpeg',
      0.9
    )
  })

defineExpose({ getCroppedFile, reset })
</script>

<style scoped>
.cropper {
  position: absolute;
  inset: 0;
  overflow: hidden;
  cursor: grab;
  touch-action: none;
  user-select: none;
  -webkit-user-select: none;
}

.cropper.dragging {
  cursor: grabbing;
}

.cropper:focus-visible {
  outline: 3px solid var(--spark);
  outline-offset: -3px;
}

.cropper img {
  position: absolute;
  max-width: none;
  pointer-events: none;
}

.hint {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  display: inline-flex;
  align-items: center;
  gap: 0.4em;
  padding: 0.4em 0.8em;
  border-radius: 999px;
  background: rgba(20, 16, 40, 0.62);
  color: #fff;
  font-family: var(--font);
  font-size: max(11px, 3.4cqw);
  font-weight: 600;
  pointer-events: none;
  backdrop-filter: blur(6px);
}

.hint svg {
  width: 1.1em;
  height: 1.1em;
}

.tools {
  position: absolute;
  right: 2cqw;
  bottom: 2cqw;
  display: flex;
  gap: 2px;
  padding: 3px;
  border-radius: 999px;
  background: rgba(20, 16, 40, 0.55);
  backdrop-filter: blur(8px);
}

.tool {
  display: grid;
  place-items: center;
  width: max(30px, 8cqw);
  height: max(30px, 8cqw);
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: #fff;
  cursor: pointer;
}

.tool:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.18);
}

.tool:disabled {
  opacity: 0.4;
  cursor: default;
}

.tool svg {
  width: 55%;
  height: 55%;
}
</style>
