<template>
  <div ref="root" class="picker">
    <button
      type="button"
      class="trigger"
      :aria-expanded="open"
      aria-haspopup="true"
      :aria-label="`Site theme: ${current.name}. Change theme`"
      @click="open = !open"
    >
      <span class="dot" :style="dotStyle(current)" aria-hidden="true"></span>
      <span class="trigger-name">{{ current.name }}</span>
      <svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6" /></svg>
    </button>

    <Transition name="pop">
      <div v-if="open" class="menu" role="radiogroup" aria-label="Site theme" @keydown.esc="close(true)">
        <button
          v-for="t in siteThemes"
          :key="t.id"
          type="button"
          role="radio"
          class="option"
          :class="{ active: t.id === siteTheme }"
          :aria-checked="t.id === siteTheme"
          @click="choose(t.id)"
        >
          <span class="preview" :style="{ background: t.colors[0] }" aria-hidden="true">
            <span :style="{ background: t.colors[1] }"></span>
            <span :style="{ background: t.colors[2] }"></span>
          </span>
          <span class="text">
            <span class="name">{{ t.name }}</span>
            <span class="hint">{{ t.hint }}</span>
          </span>
          <svg v-if="t.id === siteTheme" class="check" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7" /></svg>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { setSiteTheme, siteTheme, siteThemes } from '../lib/siteTheme'

const root = ref(null)
const open = ref(false)

const current = computed(() => siteThemes.find((t) => t.id === siteTheme.value))

const dotStyle = (t) => ({
  background: `linear-gradient(135deg, ${t.colors[1]}, ${t.colors[2]})`,
  boxShadow: `inset 0 0 0 2px ${t.colors[0]}`
})

const close = (refocus = false) => {
  open.value = false
  if (refocus) root.value?.querySelector('.trigger')?.focus()
}

const choose = (id) => {
  setSiteTheme(id)
  close(true)
}

const onDocPointer = (e) => {
  if (open.value && root.value && !root.value.contains(e.target)) close()
}

onMounted(() => document.addEventListener('pointerdown', onDocPointer))
onBeforeUnmount(() => document.removeEventListener('pointerdown', onDocPointer))
</script>

<style scoped>
.picker {
  position: relative;
}

.trigger {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  min-height: 36px;
  padding: 0 0.6rem 0 0.4rem;
  border: 1.5px solid var(--line);
  border-radius: 999px;
  background: var(--surface);
  color: var(--ink);
  font-size: 0.875rem;
  font-weight: 650;
  cursor: pointer;
  transition: border-color 0.15s;
}

.trigger:hover {
  border-color: var(--ink-3);
}

.dot {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 1px solid var(--line);
}

.chev,
.check {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2.2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.chev {
  color: var(--ink-3);
}

.menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  z-index: 80;
  display: grid;
  gap: 2px;
  width: 260px;
  padding: 6px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--surface);
  box-shadow: var(--shadow-lg);
}

.option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.55rem;
  border: 0;
  border-radius: 12px;
  background: transparent;
  color: var(--ink);
  text-align: left;
  cursor: pointer;
}

.option:hover {
  background: var(--surface-2);
}

.option.active {
  background: var(--spark-soft);
}

.preview {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  width: 44px;
  height: 34px;
  flex: none;
  padding: 5px;
  border-radius: 9px;
  box-shadow: inset 0 0 0 1px rgba(127, 127, 127, 0.3);
}

.preview span {
  flex: 1;
  border-radius: 4px;
}

.preview span:first-child {
  height: 55%;
}

.preview span:last-child {
  height: 100%;
}

.text {
  display: grid;
  flex: 1;
  min-width: 0;
  line-height: 1.25;
}

.name {
  font-weight: 700;
  font-size: 0.925rem;
}

.hint {
  font-size: 0.8rem;
  color: var(--ink-2);
}

.check {
  color: var(--spark);
}

.pop-enter-active,
.pop-leave-active {
  transition: opacity 0.15s, transform 0.18s cubic-bezier(0.2, 1, 0.3, 1);
}

.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.98);
}

@media (max-width: 720px) {
  .trigger-name {
    display: none;
  }

  .trigger {
    padding: 0 0.45rem 0 0.35rem;
  }
}
</style>
