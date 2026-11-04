<template>
  <fieldset class="field">
    <legend class="field-label">
      Entrance
      <span class="field-hint">{{ current?.hint }}</span>
    </legend>
    <div class="chips" role="radiogroup" aria-label="Entrance animation">
      <button
        v-for="a in animations"
        :key="a.id"
        type="button"
        role="radio"
        class="chip"
        :class="{ active: model === a.id }"
        :aria-checked="model === a.id"
        @click="select(a.id)"
      >
        <span class="chip-glyph" :class="`g-${a.id}`" aria-hidden="true"></span>
        {{ a.name }}
      </button>
    </div>
  </fieldset>
</template>

<script setup>
import { computed } from 'vue'
import { animations } from '../lib/animations'

const model = defineModel({ type: String, required: true })
const emit = defineEmits(['preview'])

const current = computed(() => animations.find((a) => a.id === model.value))

const select = (id) => {
  model.value = id
  emit('preview', id)
}
</script>

<style scoped>
fieldset {
  border: 0;
  min-width: 0;
}

legend {
  width: 100%;
  margin-bottom: 0.4rem;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  min-height: 38px;
  padding: 0 0.85rem 0 0.6rem;
  border: 1.5px solid var(--line);
  border-radius: 999px;
  background: var(--surface);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 0.15s, background-color 0.15s;
}

.chip:hover {
  border-color: color-mix(in srgb, var(--line) 50%, var(--ink-3));
}

.chip.active {
  border-color: var(--spark);
  background: var(--spark-soft);
  color: var(--ink);
}

.chip-glyph {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  background: var(--brand-grad);
}

/* tiny looping hint of each motion on hover / when selected */
.chip:hover .g-drop,
.chip.active .g-drop { animation: g-drop 1.4s ease-in-out infinite; }
.chip:hover .g-flip,
.chip.active .g-flip { animation: g-flip 1.6s ease-in-out infinite; }
.chip:hover .g-twirl,
.chip.active .g-twirl { animation: g-twirl 1.6s ease-in-out infinite; }
.chip:hover .g-rise,
.chip.active .g-rise { animation: g-rise 1.4s ease-in-out infinite; }
.chip:hover .g-pop,
.chip.active .g-pop { animation: g-pop 1.2s ease-in-out infinite; }
.g-none { background: var(--surface-2); box-shadow: inset 0 0 0 1.5px var(--ink-3); }

@keyframes g-drop { 0% { transform: translateY(-5px); opacity: 0.4; } 50%, 100% { transform: none; opacity: 1; } }
@keyframes g-flip { 0% { transform: rotateY(180deg); } 60%, 100% { transform: rotateY(0); } }
@keyframes g-twirl { 0% { transform: rotate(-360deg) scale(0.3); } 60%, 100% { transform: none; } }
@keyframes g-rise { 0% { transform: translateY(5px); opacity: 0.4; } 50%, 100% { transform: none; opacity: 1; } }
@keyframes g-pop { 0% { transform: scale(0.3); } 40% { transform: scale(1.2); } 60%, 100% { transform: none; } }
</style>
