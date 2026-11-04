<template>
  <div class="share">
    <div class="qr-tile" :style="{ background: tileBackground }">
      <img v-if="qrDataUrl" :src="qrDataUrl" :alt="`QR code shaped like a ${currentShape.name.toLowerCase()}, opens ${url}`" />
      <div v-else class="qr-skeleton" aria-hidden="true"></div>
    </div>

    <fieldset class="shapes">
      <legend class="field-label">
        QR shape
        <span class="field-hint">{{ currentShape.name }}</span>
      </legend>
      <div class="shape-grid" role="radiogroup" aria-label="QR code shape">
        <button
          v-for="s in qrShapes"
          :key="s.id"
          type="button"
          role="radio"
          class="shape"
          :class="{ active: s.id === shapeId }"
          :aria-checked="s.id === shapeId"
          :aria-label="s.name"
          :title="s.name"
          @click="shapeId = s.id"
        >
          <svg v-if="s.parts.length" viewBox="0 0 200 200" aria-hidden="true">
            <path
              v-for="(p, i) in s.parts"
              :key="i"
              :d="p.d"
              :fill-rule="p.rule || 'nonzero'"
              :stroke="p.stroke ? 'currentColor' : undefined"
              :stroke-width="p.stroke"
              stroke-linejoin="round"
            />
          </svg>
          <Icon v-else name="qr" class="plain-icon" />
        </button>
      </div>

      <div class="qr-options">
        <label class="toggle">
          <input v-model="matchColors" type="checkbox" />
          <span class="toggle-ui" aria-hidden="true"></span>
          <span class="toggle-text">
            <strong>Match colors</strong>
            <span>Code in the shape color on the background color</span>
          </span>
        </label>
        <label class="toggle">
          <input v-model="diamond" type="checkbox" />
          <span class="toggle-ui" aria-hidden="true"></span>
          <span class="toggle-text">
            <strong>Diamond</strong>
            <span>Turn the code 45°</span>
          </span>
        </label>
      </div>
      <p v-if="matchColors && palette.swapped" class="qr-note">
        On dark backgrounds the code is drawn dark-on-light so every phone can scan it.
      </p>
    </fieldset>

    <div class="link-row">
      <label class="visually-hidden" :for="linkId">Sparklet link</label>
      <input :id="linkId" class="input link" :value="url" readonly @focus="$event.target.select()" />
      <button type="button" class="btn btn-primary" @click="copyText(url)">
        <Icon name="link" /> Copy
      </button>
    </div>

    <div class="actions">
      <button type="button" class="btn btn-ghost" :disabled="!qrDataUrl" @click="downloadImage">
        <Icon name="download" /> Save QR image
      </button>
      <button type="button" class="btn btn-ghost" :disabled="!qrDataUrl" @click="downloadTag">
        <Icon name="download" /> Save QR card
      </button>
      <button v-if="canShare" type="button" class="btn btn-ghost" @click="nativeShare">
        <Icon name="share" /> Share…
      </button>
      <a :href="url" target="_blank" rel="noopener" class="btn btn-ghost">
        <Icon name="eye" /> Open
      </a>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import Icon from './Icon.vue'
import { copyText, toast } from '../lib/toast'
import { qrShapes, renderShapedQr } from '../lib/qrShapes'
import { contrastInk, matchedQrColors, tonesOf } from '../lib/themes'

const props = defineProps({
  url: { type: String, required: true },
  toName: { type: String, default: '' },
  fromName: { type: String, default: '' },
  id: { type: [String, Number], default: '' },
  // the sparklet's background color; the shape is a tone of it
  backgroundColor: { type: String, default: '' }
})

const linkId = `link-${Math.random().toString(36).slice(2, 8)}`
const qrDataUrl = ref('')
const shapeId = ref('heart')
const matchColors = ref(false)
const diamond = ref(false)
const canShare = typeof navigator !== 'undefined' && !!navigator.share

const currentShape = computed(() => qrShapes.find((s) => s.id === shapeId.value) || qrShapes[0])

const cssVar = (name, fallback) =>
  getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback

// Shape color: a rich tone of the sparklet background (deeper on light backgrounds).
const shapeColor = computed(() => {
  if (!props.backgroundColor) return cssVar('--spark', '#ff3d6e')
  const [light, deep] = tonesOf(props.backgroundColor)
  return contrastInk(props.backgroundColor) === 'light' ? deep : light
})

const tileBackground = computed(() => props.backgroundColor || 'var(--surface-2)')

// Shape, code and plate colors for the current options.
const palette = computed(() => {
  if (matchColors.value && props.backgroundColor) return matchedQrColors(props.backgroundColor)
  if (matchColors.value) return { shape: shapeColor.value, ink: shapeColor.value, paper: '#ffffff', swapped: false }
  return { shape: shapeColor.value, ink: '#1d1a2b', paper: '#ffffff', swapped: false }
})

const shapedCanvas = (size) =>
  renderShapedQr(props.url, {
    shapeId: shapeId.value,
    color: palette.value.shape,
    ink: palette.value.ink,
    paper: palette.value.paper,
    diamond: diamond.value,
    size
  })

const render = () => {
  try {
    qrDataUrl.value = shapedCanvas(720).toDataURL('image/png')
  } catch (err) {
    console.error(err)
    qrDataUrl.value = ''
  }
}

onMounted(render)
watch(() => [props.url, shapeId.value, palette.value, diamond.value], render)

const save = (canvas, name) => {
  const link = document.createElement('a')
  link.download = name
  link.href = canvas.toDataURL('image/png')
  link.click()
}

const fileBase = () =>
  `sparklet-${String(props.id || 'qr').slice(0, 8)}-${shapeId.value}${diamond.value ? '-diamond' : ''}${matchColors.value ? '-matched' : ''}`

const downloadImage = () => {
  try {
    save(shapedCanvas(1200), `${fileBase()}.png`)
    toast('QR image saved', { tone: 'ok' })
  } catch (err) {
    console.error(err)
    toast('Couldn’t create the QR image.', { tone: 'error' })
  }
}

const nativeShare = async () => {
  try {
    await navigator.share({
      title: 'A sparklet for you',
      text: props.toName ? `${props.toName}, someone sent you a sparklet` : 'Someone sent you a sparklet',
      url: props.url
    })
  } catch {
    /* user dismissed the share sheet */
  }
}

/** A printable tag: the shaped QR plus who it's for, ready to tuck into a gift. */
const downloadTag = async () => {
  try {
    await Promise.all([
      document.fonts?.load('700 40px "Kalam"'),
      document.fonts?.load('700 26px "Bricolage Grotesque"')
    ])
    const W = 720
    const H = 920
    const canvas = document.createElement('canvas')
    canvas.width = W
    canvas.height = H
    const ctx = canvas.getContext('2d')

    const spark = cssVar('--spark', '#ff3d6e')
    const accent = cssVar('--accent-2', '#a66cff')
    const grad = ctx.createLinearGradient(0, 0, W, H)
    grad.addColorStop(0, accent)
    grad.addColorStop(1, spark)
    ctx.fillStyle = grad
    ctx.fillRect(0, 0, W, H)

    ctx.fillStyle = '#ffffff'
    ctx.beginPath()
    ctx.roundRect(40, 40, W - 80, H - 80, 36)
    ctx.fill()

    ctx.drawImage(shapedCanvas(1200), 110, 140, W - 220, W - 220)

    ctx.fillStyle = '#1d1a2b'
    ctx.textAlign = 'center'
    ctx.font = '700 44px Kalam, cursive'
    ctx.fillText(props.toName ? `For ${props.toName}` : 'A sparklet for you', W / 2, 112, W - 160)

    ctx.font = '600 26px "Bricolage Grotesque", sans-serif'
    ctx.fillStyle = '#5d5873'
    const caption = props.fromName ? `Scan me to open a note from ${props.fromName}` : 'Scan me to open your note'
    ctx.fillText(caption, W / 2, 140 + W - 220 + 50, W - 160)
    ctx.font = '700 24px "Bricolage Grotesque", sans-serif'
    ctx.fillStyle = spark
    ctx.fillText('sparklets.im', W / 2, H - 74)

    save(canvas, `${fileBase()}-card.png`)
    toast('QR card saved', { tone: 'ok' })
  } catch (err) {
    console.error(err)
    toast('Couldn’t create the QR card image.', { tone: 'error' })
  }
}
</script>

<style scoped>
.share {
  display: grid;
  gap: 1rem;
}

.qr-tile {
  display: grid;
  place-items: center;
  padding: 1rem;
  border-radius: var(--radius);
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.06);
  transition: background-color 0.2s;
}

.qr-tile img,
.qr-skeleton {
  width: min(250px, 64vw);
  aspect-ratio: 1;
}

fieldset {
  border: 0;
  min-width: 0;
}

legend {
  width: 100%;
  margin-bottom: 0.4rem;
}

.shape-grid {
  display: grid;
  grid-template-columns: repeat(8, minmax(0, 1fr));
  gap: 0.35rem;
}

.shape {
  display: grid;
  place-items: center;
  aspect-ratio: 1;
  padding: 18%;
  border: 1.5px solid var(--line);
  border-radius: 12px;
  background: var(--surface);
  color: var(--ink-2);
  cursor: pointer;
  transition: border-color 0.15s, background-color 0.15s, color 0.15s;
}

.shape:hover {
  border-color: var(--ink-3);
  color: var(--ink);
}

.shape.active {
  border-color: var(--spark);
  background: var(--spark-soft);
  color: var(--spark);
}

.shape svg {
  width: 100%;
  height: 100%;
  fill: currentColor;
}

.shape .plain-icon {
  fill: none;
}

.qr-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.toggle {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.6rem 0.7rem;
  border: 1.5px solid var(--line);
  border-radius: var(--radius-sm);
  background: var(--surface);
  cursor: pointer;
  transition: border-color 0.15s, background-color 0.15s;
}

.toggle:hover {
  border-color: var(--ink-3);
}

.toggle:has(input:checked) {
  border-color: var(--spark);
  background: var(--spark-soft);
}

.toggle input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.toggle-ui {
  position: relative;
  width: 34px;
  height: 20px;
  flex: none;
  border-radius: 999px;
  background: var(--line);
  transition: background-color 0.15s;
}

.toggle-ui::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
  transition: transform 0.15s;
}

.toggle input:checked + .toggle-ui {
  background: var(--spark);
}

.toggle input:checked + .toggle-ui::after {
  transform: translateX(14px);
}

.toggle input:focus-visible + .toggle-ui {
  outline: 3px solid color-mix(in srgb, var(--spark) 60%, transparent);
  outline-offset: 2px;
}

.toggle-text {
  display: grid;
  min-width: 0;
  line-height: 1.2;
}

.toggle-text strong {
  font-size: 0.875rem;
  font-weight: 700;
}

.toggle-text span {
  font-size: 0.75rem;
  color: var(--ink-2);
}

.qr-note {
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: var(--ink-2);
}

.link-row {
  display: flex;
  gap: 0.5rem;
}

.link {
  min-width: 0;
  font-size: 0.925rem;
  color: var(--ink-2);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.actions .btn {
  flex: 1 1 auto;
}

@media (max-width: 400px) {
  .qr-options {
    grid-template-columns: 1fr;
  }

  .shape-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
</style>
