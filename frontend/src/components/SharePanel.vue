<template>
  <div class="share">
    <div class="qr-tile">
      <img v-if="qrDataUrl" :src="qrDataUrl" :alt="`QR code that opens ${url}`" />
      <div v-else class="qr-skeleton" aria-hidden="true"></div>
      <p>Scan to open</p>
    </div>

    <div class="link-row">
      <label class="visually-hidden" :for="linkId">Sparklet link</label>
      <input :id="linkId" class="input link" :value="url" readonly @focus="$event.target.select()" />
      <button type="button" class="btn btn-primary" @click="copyText(url)">
        <Icon name="link" /> Copy
      </button>
    </div>

    <div class="actions">
      <button v-if="canShare" type="button" class="btn btn-ghost" @click="nativeShare">
        <Icon name="share" /> Share…
      </button>
      <button type="button" class="btn btn-ghost" :disabled="!qrDataUrl" @click="downloadTag">
        <Icon name="download" /> Save QR card
      </button>
      <a :href="url" target="_blank" rel="noopener" class="btn btn-ghost">
        <Icon name="eye" /> Open
      </a>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import QRCode from 'qrcode'
import Icon from './Icon.vue'
import { copyText, toast } from '../lib/toast'

const props = defineProps({
  url: { type: String, required: true },
  toName: { type: String, default: '' },
  fromName: { type: String, default: '' },
  id: { type: [String, Number], default: '' }
})

const linkId = `link-${Math.random().toString(36).slice(2, 8)}`
const qrDataUrl = ref('')
const canShare = typeof navigator !== 'undefined' && !!navigator.share

const render = async () => {
  qrDataUrl.value = await QRCode.toDataURL(props.url, {
    width: 480,
    margin: 1,
    errorCorrectionLevel: 'M',
    color: { dark: '#1d1a2b', light: '#ffffff' }
  })
}

onMounted(render)
watch(() => props.url, render)

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

const loadImage = (src) =>
  new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = src
  })

const roundRect = (ctx, x, y, w, h, r) => {
  ctx.beginPath()
  ctx.moveTo(x + r, y)
  ctx.arcTo(x + w, y, x + w, y + h, r)
  ctx.arcTo(x + w, y + h, x, y + h, r)
  ctx.arcTo(x, y + h, x, y, r)
  ctx.arcTo(x, y, x + w, y, r)
  ctx.closePath()
}

/** A printable tag: QR code plus who it's for, ready to tuck into a gift. */
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

    const css = getComputedStyle(document.documentElement)
    const spark = css.getPropertyValue('--spark').trim() || '#ff3d6e'
    const accent = css.getPropertyValue('--accent-2').trim() || '#a66cff'
    const grad = ctx.createLinearGradient(0, 0, W, H)
    grad.addColorStop(0, accent)
    grad.addColorStop(1, spark)
    ctx.fillStyle = grad
    ctx.fillRect(0, 0, W, H)

    ctx.fillStyle = '#ffffff'
    roundRect(ctx, 40, 40, W - 80, H - 80, 36)
    ctx.fill()

    const qr = await loadImage(qrDataUrl.value)
    ctx.drawImage(qr, 120, 150, W - 240, W - 240)

    ctx.fillStyle = '#1d1a2b'
    ctx.textAlign = 'center'
    ctx.font = '700 44px Kalam, cursive'
    ctx.fillText(props.toName ? `For ${props.toName}` : 'A sparklet for you', W / 2, 118, W - 160)

    ctx.font = '600 26px "Bricolage Grotesque", sans-serif'
    ctx.fillStyle = '#5d5873'
    const caption = props.fromName ? `Scan me to open a note from ${props.fromName}` : 'Scan me to open your note'
    ctx.fillText(caption, W / 2, 150 + W - 240 + 64, W - 160)
    ctx.font = '700 24px "Bricolage Grotesque", sans-serif'
    ctx.fillStyle = spark
    ctx.fillText('sparklets.im', W / 2, H - 78)

    const link = document.createElement('a')
    link.download = `sparklet-${props.id || 'qr'}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
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
  justify-items: center;
  gap: 0.5rem;
  padding: 1.25rem;
  border-radius: var(--radius);
  background: var(--brand-grad);
}

.qr-tile img,
.qr-skeleton {
  width: min(220px, 60vw);
  aspect-ratio: 1;
  padding: 10px;
  border-radius: 14px;
  background: #fff;
}

.qr-tile p {
  color: #fff;
  font-weight: 700;
  font-size: 0.9rem;
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
</style>
