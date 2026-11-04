<template>
  <div ref="stage" class="stage" :class="[`enter-${safeAnimation}`, { floating: float }]">
    <div class="float">
      <slot />
    </div>
    <div v-if="safeAnimation === 'pop'" class="burst" aria-hidden="true">
      <span v-for="n in 10" :key="n" :style="{ '--i': n }"></span>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { isAnimation } from '../lib/animations'

const props = defineProps({
  animation: { type: String, default: 'drop' },
  float: { type: Boolean, default: true },
  // change this value to replay the entrance
  playKey: { type: [String, Number], default: 0 }
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

.burst {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.burst span {
  --angle: calc(var(--i) * 36deg);
  position: absolute;
  left: 50%;
  top: 50%;
  width: 14px;
  height: 14px;
  margin: -7px;
  background: var(--sun);
  clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
  opacity: 0;
  animation: burst 0.9s 0.15s ease-out both;
}

.burst span:nth-child(even) {
  background: var(--spark);
  width: 10px;
  height: 10px;
  margin: -5px;
}

@keyframes burst {
  0% { opacity: 1; transform: rotate(var(--angle)) translateY(0) scale(0.4); }
  100% { opacity: 0; transform: rotate(var(--angle)) translateY(-62cqw) scale(1.2); }
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
