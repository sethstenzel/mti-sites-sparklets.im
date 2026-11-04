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

    <div class="send">
      <span class="field-label">Send it</span>
      <div class="send-row">
        <button type="button" class="send-btn facebook" @click="shareFacebook">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 8.5V6.8c0-.8.5-1 .9-1h2.4V2.1L14 2c-3.7 0-4.5 2.7-4.5 4.5v2H7v3.8h2.5V22H14v-9.7h3l.4-3.8H14z" /></svg>
          Facebook
        </button>
        <button type="button" class="send-btn messenger" @click="shareMessenger">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2C6.4 2 2 6.1 2 11.6c0 2.9 1.2 5.4 3.1 7.1V22l2.9-1.6c1.2.3 2.6.5 4 .5 5.6 0 10-4.1 10-9.6S17.6 2 12 2zm1 12.9-2.6-2.7-5 2.7 5.5-5.8 2.6 2.7 4.9-2.7-5.4 5.8z" /></svg>
          Messenger
        </button>
        <button type="button" class="send-btn x" @click="shareX">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.8 3h3.1l-6.8 7.7L22 21h-6.2l-4.9-6.4L5.3 21H2.2l7.3-8.3L2 3h6.4l4.4 5.8L17.8 3zm-1.1 16.2h1.7L7.4 4.7H5.6l11.1 14.5z" /></svg>
          X
        </button>
        <button type="button" class="send-btn email" @click="shareEmail">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm9 7.2L4.3 7H4v.6l8 5.4 8-5.4V7h-.3L12 12.2z" /></svg>
          Email
        </button>
      </div>
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

// ---------- sharing ----------
// Copy is deliberately generic, like the link preview: it never repeats the message.
const SHARE_TITLE = 'You’ve got a sparklet ✨'
const shareText = computed(() =>
  props.toName ? `${props.toName}, a special message is waiting for you ✨` : 'A special message is waiting for you ✨'
)

const openPopup = (href) => {
  const w = 600
  const h = 640
  const left = Math.max(0, (window.screen.width - w) / 2)
  const top = Math.max(0, (window.screen.height - h) / 2)
  const win = window.open(href, 'sparklets-share', `width=${w},height=${h},left=${left},top=${top}`)
  if (win) win.opener = null
  else window.open(href, '_blank', 'noopener')
}

const enc = encodeURIComponent
const isMobile = () => /Android|iPhone|iPad|iPod/i.test(navigator.userAgent)

const shareFacebook = () => openPopup(`https://www.facebook.com/sharer/sharer.php?u=${enc(props.url)}`)

const shareX = () => openPopup(`https://twitter.com/intent/tweet?text=${enc(shareText.value)}&url=${enc(props.url)}`)

// Messenger:
//  - phones: the system share sheet (Messenger is listed there); Meta retired the old
//    fb-messenger:// share link, which now just opens the app
//  - desktop: Facebook's "Send" dialog, which needs a Facebook App ID (VITE_FB_APP_ID at
//    build time). Without one there is no desktop share, so we copy the link instead.
const FB_APP_ID = import.meta.env.VITE_FB_APP_ID || ''
const shareMessenger = async () => {
  if (isMobile() && navigator.share) {
    try {
      await navigator.share({ title: SHARE_TITLE, text: shareText.value, url: props.url })
    } catch {
      /* dismissed */
    }
    return
  }
  if (FB_APP_ID) {
    openPopup(
      `https://www.facebook.com/dialog/send?app_id=${enc(FB_APP_ID)}&link=${enc(props.url)}&redirect_uri=${enc(props.url)}`
    )
    return
  }
  await copyText(props.url, 'Link copied. Open a Messenger chat and paste it')
  window.open('https://www.messenger.com/', '_blank', 'noopener')
}

// Email: a mailto: link can only carry plain text, so we copy a designed email (preview
// image + button + link) as rich HTML and open a new compose window to paste it into.
const PREVIEW_IMAGE = typeof __SPARKLET_PREVIEW_URL__ !== 'undefined' ? __SPARKLET_PREVIEW_URL__ : ''
const escapeHtml = (v) => String(v).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c])

const emailHtml = () => {
  const url = escapeHtml(props.url)
  const hi = props.toName ? `<p style="margin:0 0 16px;font-size:17px">Hi ${escapeHtml(props.toName)},</p>` : ''
  const sign = props.fromName ? `<p style="margin:20px 0 0;font-size:16px">${escapeHtml(props.fromName)}</p>` : ''
  return `<div style="max-width:520px;font-family:Arial,Helvetica,sans-serif;color:#1f1a1e;line-height:1.5">
${hi}<a href="${url}" style="text-decoration:none"><img src="${PREVIEW_IMAGE}" width="520" alt="You’ve got a sparklet. A special message is waiting for you." style="display:block;width:100%;max-width:520px;height:auto;border:0;border-radius:14px"></a>
<p style="margin:18px 0 14px;font-size:17px">A special message is waiting for you on Sparklets ✨</p>
<p style="margin:0 0 18px"><a href="${url}" style="display:inline-block;background:#2b2329;color:#ffffff;text-decoration:none;font-weight:bold;font-size:16px;padding:12px 24px;border-radius:999px">Open your sparklet</a></p>
<p style="margin:0;font-size:13px;color:#5b5258">Or open this link: <a href="${url}" style="color:#5b5258">${url}</a></p>${sign}
</div>`
}

const emailText = () => {
  const greeting = props.toName ? `Hi ${props.toName},\n\n` : ''
  const sign = props.fromName ? `\n\n${props.fromName}` : ''
  return `${greeting}A special message is waiting for you on Sparklets. Open it here:\n${props.url}${sign}`
}

const openInNewWindow = (href) => {
  const a = document.createElement('a')
  a.href = href
  a.target = '_blank'
  a.rel = 'noopener'
  document.body.appendChild(a)
  a.click()
  a.remove()
}

const shareEmail = async () => {
  let rich = false
  try {
    if (window.ClipboardItem && navigator.clipboard?.write) {
      await navigator.clipboard.write([
        new ClipboardItem({
          'text/html': new Blob([emailHtml()], { type: 'text/html' }),
          'text/plain': new Blob([emailText()], { type: 'text/plain' })
        })
      ])
      rich = true
    }
  } catch {
    rich = false
  }
  if (rich) {
    // subject only: the body comes from the pasted, designed email
    openInNewWindow(`mailto:?subject=${enc(SHARE_TITLE)}`)
    toast('Email copied. Paste it into the message (Ctrl+V / ⌘V)', { tone: 'ok', duration: 6000 })
  } else {
    openInNewWindow(`mailto:?subject=${enc(SHARE_TITLE)}&body=${enc(emailText())}`)
  }
}

const nativeShare = async () => {
  try {
    await navigator.share({
      title: SHARE_TITLE,
      text: shareText.value,
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

.send {
  display: grid;
  gap: 0.4rem;
}

.send-row {
  display: grid;
  /* sized to the labels: Messenger is longest, X shortest */
  grid-template-columns: 1.12fr 1.3fr 0.68fr 0.9fr;
  gap: 0.5rem;
}

.send-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  min-width: 0;
  min-height: 44px;
  padding: 0 0.5rem;
  border: 0;
  border-radius: 999px;
  color: #fff;
  font-weight: 650;
  font-size: 0.875rem;
  text-decoration: none;
  white-space: nowrap;
  cursor: pointer;
  transition: filter 0.15s, transform 0.1s;
}

.send-btn:hover {
  filter: brightness(1.08);
}

.send-btn:active {
  transform: scale(0.97);
}

.send-btn svg {
  width: 18px;
  height: 18px;
  flex: none;
  fill: currentColor;
}

.send-btn.facebook {
  background: #1877f2;
}

.send-btn.messenger {
  background: linear-gradient(135deg, #0a7cff, #a033ff 60%, #ff5c87);
}

.send-btn.x {
  background: #0f1419;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.12);
}

.send-btn.email {
  background: var(--spark);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.actions .btn {
  flex: 1 1 auto;
}

@media (max-width: 460px) {
  .send-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
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
