<template>
  <figure
    class="sparklet"
    :style="{
      '--card': cardColor,
      '--note-ink': textColor,
      '--tilt': `${rotation}deg`,
      '--note-font': fontDef.family,
      '--note-scale': fontDef.scale,
      '--note-style': fontDef.italic ? 'italic' : 'normal'
    }"
  >
    <div class="photo">
      <slot name="photo">
        <img v-if="image" :src="image" :alt="alt" loading="lazy" decoding="async" />
        <div v-else class="photo-empty" aria-hidden="true">
          <Icon name="image" />
        </div>
      </slot>
    </div>
    <figcaption class="note">
      <p class="message" :class="sizeClass">{{ message || messagePlaceholder }}</p>
      <p class="signature">
        <span>To {{ toName || toPlaceholder }}</span>
        <span>From {{ fromName || fromPlaceholder }}</span>
      </p>
    </figcaption>
  </figure>
</template>

<script setup>
import { computed } from 'vue'
import Icon from './Icon.vue'
import { fontById } from '../lib/fonts'

const props = defineProps({
  message: { type: String, default: '' },
  toName: { type: String, default: '' },
  fromName: { type: String, default: '' },
  cardColor: { type: String, default: '#ffffff' },
  textColor: { type: String, default: '#333333' },
  rotation: { type: Number, default: 0 },
  image: { type: String, default: '' },
  font: { type: String, default: 'kalam' },
  messagePlaceholder: { type: String, default: '' },
  toPlaceholder: { type: String, default: '…' },
  fromPlaceholder: { type: String, default: '…' }
})

const fontDef = computed(() => fontById(props.font))

const alt = computed(() => (props.fromName ? `Photo from ${props.fromName}` : 'Sparklet photo'))

const sizeClass = computed(() => {
  const text = props.message || props.messagePlaceholder
  const lines = text.split('\n').length
  if (text.length > 100 || lines > 3) return 'is-xlong'
  if (text.length > 70 || lines > 2) return 'is-long'
  if (text.length > 36) return 'is-medium'
  return 'is-short'
})
</script>

<style scoped>
/* Everything inside is sized in cqw so the card looks identical at any width. */
.sparklet {
  container-type: inline-size;
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  padding: 4.5cqw 4.5cqw 3.5cqw;
  background:
    linear-gradient(160deg, rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0) 40%),
    var(--card);
  border-radius: 1.6cqw;
  transform: rotate(var(--tilt));
  box-shadow:
    0 0.4cqw 0.8cqw rgba(20, 16, 40, 0.1),
    0 5cqw 9cqw -3cqw rgba(20, 16, 40, 0.35);
  color: var(--note-ink);
}

.photo {
  position: relative;
  width: 100%;
  aspect-ratio: 3 / 2;
  flex: none;
  overflow: hidden;
  border-radius: 0.8cqw;
  background: rgba(0, 0, 0, 0.06);
}

.photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-empty {
  display: grid;
  place-items: center;
  width: 100%;
  height: 100%;
  color: color-mix(in srgb, var(--note-ink) 35%, transparent);
}

.photo-empty svg {
  width: 14cqw;
  height: 14cqw;
}

.note {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-top: 2.6cqw;
  font-family: var(--note-font, var(--hand));
  font-style: var(--note-style, normal);
  text-align: center;
}

.message {
  flex: 1;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  white-space: pre-line;
  overflow-wrap: anywhere;
  line-height: 1.18;
}

.message.is-short {
  font-size: calc(6.4cqw * var(--note-scale, 1));
}

.message.is-medium {
  font-size: calc(5.2cqw * var(--note-scale, 1));
}

.message.is-long {
  font-size: calc(4.3cqw * var(--note-scale, 1));
}

.message.is-xlong {
  font-size: calc(3.8cqw * var(--note-scale, 1));
  line-height: 1.14;
}

.signature {
  display: flex;
  justify-content: space-between;
  gap: 5cqw;
  padding-top: 1.2cqw;
  font-size: calc(3.4cqw * var(--note-scale, 1));
  font-weight: 700;
  line-height: 1.2;
  opacity: 0.82;
}

.signature span {
  flex: 0 1 auto;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
