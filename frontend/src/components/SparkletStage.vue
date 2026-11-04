<template>
  <div ref="stage" class="stage" :class="[`enter-${safeAnimation}`, { floating: float }]">
    <div class="float">
      <slot />
    </div>
    <div v-if="safeAnimation === 'pop'" class="burst" :style="burstStyle" aria-hidden="true">
      <span v-for="n in 12" :key="n" :style="{ '--i': n }"></span>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { isAnimation } from '../lib/animations'
import { tonesOf } from '../lib/themes'

const props = defineProps({
  animation: { type: String, default: 'drop' },
  float: { type: Boolean, default: true },
  // change this value to replay the entrance
  playKey: { type: [String, Number], default: 0 },
  // the sparklet's background color; the pop sparkles use tones of it
  burstColor: { type: String, default: '' }
})

const burstStyle = computed(() => {
  if (!props.burstColor) return {}
  const [a, b] = tonesOf(props.burstColor)
  return { '--burst-a': a, '--burst-b': b }
})

const safeAnimation = computed(() => (isAnimation(props.animation) ? props.animation : 'drop'))

const stage = ref(null)

// Restart the CSS animations in place (no remount, so slot state such as photo framing survives).
watch(
  () => props.playKey,
  async () => {
    await nextTick()
    const root = stage.value
    if (!root) return
    const els = [root, ...root.querySelectorAll('.float, .burst span')]
    els.forEach((el) => (el.style.animation = 'none'))
    void root.offsetWidth
    els.forEach((el) => (el.style.animation = ''))
  }
)
</script>

<style scoped>
.stage {
  --enter-duration: 1s;
  container-type: inline-size;
  position: relative;
  width: 100%;
  perspective: 1400px;
}

/* ---------- entrances ---------- */

.enter-drop {
  animation: drop var(--enter-duration) cubic-bezier(0.22, 1.2, 0.36, 1) both;
}

@keyframes drop {
  0% { opacity: 0; transform: translateY(-70vh) rotate(-14deg); }
  55% { opacity: 1; }
  70% { transform: translateY(14px) rotate(2deg); }
  85% { transform: translateY(-6px) rotate(-1deg); }
  100% { transform: none; }
}

.enter-flip {
  --enter-duration: 1.1s;
  animation: flip var(--enter-duration) cubic-bezier(0.3, 1.25, 0.4, 1) both;
}

@keyframes flip {
  0% { opacity: 0; transform: perspective(1400px) rotateY(-180deg) scale(0.6); }
  30% { opacity: 1; }
  100% { transform: perspective(1400px) rotateY(0deg) scale(1); }
}

.enter-flip {
  backface-visibility: hidden;
}

.enter-twirl {
  --enter-duration: 1.05s;
  animation: twirl var(--enter-duration) cubic-bezier(0.25, 1.3, 0.4, 1) both;
}

@keyframes twirl {
  0% { opacity: 0; transform: rotate(-540deg) scale(0.1); }
  40% { opacity: 1; }
  100% { transform: none; }
}

.enter-rise {
  --enter-duration: 1.15s;
  animation: rise var(--enter-duration) cubic-bezier(0.2, 0.9, 0.3, 1.15) both;
}

@keyframes rise {
  0% { opacity: 0; transform: translateY(60vh) scale(0.85) rotate(6deg); }
  40% { opacity: 1; }
  100% { transform: none; }
}

.enter-pop {
  --enter-duration: 0.75s;
  animation: pop var(--enter-duration) cubic-bezier(0.3, 1.6, 0.5, 1) both;
}

@keyframes pop {
  0% { opacity: 0; transform: scale(0.2); }
  60% { opacity: 1; transform: scale(1.08); }
  100% { transform: none; }
}

.enter-none {
  --enter-duration: 0s;
}

/* ---------- sparkle burst for "pop" ---------- */

.float {
  position: relative;
  z-index: 1;
}

/* sparkles start behind the card and fly out past its edges */
.burst {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.burst span {
  --angle: calc(var(--i) * 30deg + 8deg);
  --dist: 78cqw;
  position: absolute;
  left: 50%;
  top: 50%;
  width: 7cqw;
  height: 7cqw;
  margin: -3.5cqw;
  background: var(--burst-a, var(--accent-2));
  clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
  opacity: 0;
  animation: burst 1.1s 0.12s cubic-bezier(0.15, 0.7, 0.3, 1) both;
}

.burst span:nth-child(even) {
  --dist: 92cqw;
  background: var(--burst-b, var(--spark));
  width: 4.5cqw;
  height: 4.5cqw;
  margin: -2.25cqw;
}

@keyframes burst {
  0% { opacity: 0; transform: rotate(var(--angle)) translateY(-20cqw) scale(0.3); }
  15% { opacity: 1; }
  70% { opacity: 1; }
  100% { opacity: 0; transform: rotate(var(--angle)) translateY(calc(var(--dist) * -1)) scale(1) rotate(90deg); }
}

/* ---------- idle hover ---------- */

.floating .float {
  animation: hover 6s ease-in-out infinite;
  animation-delay: var(--enter-duration);
  will-change: transform;
}

@keyframes hover {
  0%, 100% { transform: translate3d(0, 0, 0) rotate(0deg); }
  25% { transform: translate3d(2px, -9px, 0) rotate(0.6deg); }
  50% { transform: translate3d(0, -14px, 0) rotate(0deg); }
  75% { transform: translate3d(-2px, -7px, 0) rotate(-0.6deg); }
}

@media (prefers-reduced-motion: reduce) {
  .stage,
  .floating .float,
  .burst span {
    animation: none !important;
  }
}
</style>
