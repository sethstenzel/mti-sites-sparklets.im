<template>
  <div class="fields">
    <div class="row-2">
      <label class="field">
        <span class="field-label">To</span>
        <input
          v-model="model.to_name"
          class="input"
          type="text"
          :maxlength="MAX_NAME_LENGTH"
          required
          autocomplete="off"
          placeholder="Who’s it for?"
          @keydown.enter.prevent
        />
      </label>
      <label class="field">
        <span class="field-label">From</span>
        <input
          v-model="model.from_name"
          class="input"
          type="text"
          :maxlength="MAX_NAME_LENGTH"
          required
          autocomplete="nickname"
          placeholder="Your name"
          @keydown.enter.prevent
        />
      </label>
    </div>

    <label class="field">
      <span class="field-label">
        Message
        <span class="field-hint" :class="{ warn: remaining <= 10 }">{{ remaining }} left</span>
      </span>
      <textarea
        v-model="model.message"
        class="input"
        :maxlength="MAX_MESSAGE_LENGTH"
        rows="3"
        required
        placeholder="Say something that’ll make their day"
      ></textarea>
    </label>

    <fieldset class="field">
      <legend class="field-label">Colors</legend>
      <div class="swatches" role="radiogroup" aria-label="Color theme">
        <button
          v-for="theme in themes"
          :key="theme.name"
          type="button"
          class="swatch"
          role="radio"
          :aria-checked="matchesTheme(model, theme)"
          :class="{ active: matchesTheme(model, theme) }"
          :title="theme.name"
          @click="applyTheme(theme)"
        >
          <span class="swatch-chip" :style="{ background: theme.background_color }">
            <span class="swatch-card" :style="{ background: theme.card_color, color: theme.text_color }">Aa</span>
          </span>
          <span class="swatch-name">{{ theme.name }}</span>
        </button>
      </div>
      <details class="custom" :open="isCustom">
        <summary>Custom colors</summary>
        <div class="color-row">
          <label class="color">
            <input v-model="model.background_color" type="color" />
            <span>Background</span>
          </label>
          <label class="color">
            <input v-model="model.card_color" type="color" />
            <span>Card</span>
          </label>
          <label class="color">
            <input v-model="model.text_color" type="color" />
            <span>Text</span>
          </label>
        </div>
      </details>
    </fieldset>

    <label class="field">
      <span class="field-label">
        Tilt
        <span class="field-hint">{{ model.card_rotation > 0 ? '+' : '' }}{{ model.card_rotation }}°</span>
      </span>
      <input
        v-model.number="model.card_rotation"
        class="range"
        type="range"
        min="-10"
        max="10"
        step="1"
        :style="{ '--pct': `${((model.card_rotation + 10) / 20) * 100}%` }"
      />
    </label>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { themes, matchesTheme } from '../lib/themes'
import { MAX_MESSAGE_LENGTH, MAX_NAME_LENGTH } from '../lib/limits'

const model = defineModel({ type: Object, required: true })

const remaining = computed(() => MAX_MESSAGE_LENGTH - (model.value.message?.length || 0))
const isCustom = computed(() => !themes.some((t) => matchesTheme(model.value, t)))

const applyTheme = (theme) => {
  model.value.background_color = theme.background_color
  model.value.card_color = theme.card_color
  model.value.text_color = theme.text_color
}
</script>

<style scoped>
.fields {
  display: grid;
  gap: 1.25rem;
}

.row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

fieldset {
  border: 0;
  min-width: 0;
}

legend {
  margin-bottom: 0.4rem;
}

.field-hint.warn {
  color: var(--spark);
}

.swatches {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 0.5rem;
}

.swatch {
  display: grid;
  gap: 0.3rem;
  justify-items: center;
  padding: 0;
  border: 0;
  background: none;
  cursor: pointer;
}

.swatch-chip {
  display: grid;
  place-items: center;
  width: 100%;
  aspect-ratio: 1;
  border-radius: 14px;
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.15s, transform 0.15s;
}

.swatch-card {
  display: grid;
  place-items: center;
  width: 58%;
  aspect-ratio: 1;
  border-radius: 5px;
  font-family: var(--hand);
  font-weight: 700;
  font-size: 0.85rem;
  transform: rotate(-6deg);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
}

.swatch:hover .swatch-chip {
  transform: translateY(-2px);
}

.swatch.active .swatch-chip {
  box-shadow: 0 0 0 2px var(--surface), 0 0 0 4px var(--spark);
}

.swatch-name {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--ink-2);
}

.swatch.active .swatch-name {
  color: var(--ink);
}

.custom {
  margin-top: 0.75rem;
}

.custom summary {
  width: fit-content;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink-2);
  cursor: pointer;
}

.custom summary:hover {
  color: var(--ink);
}

.color-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  margin-top: 0.6rem;
}

.color {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.6rem 0.4rem 0.4rem;
  border: 1.5px solid var(--line);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
}

.color input {
  width: 32px;
  height: 32px;
  flex: none;
  padding: 0;
  border: 0;
  border-radius: 8px;
  background: none;
  cursor: pointer;
}

.color input::-webkit-color-swatch-wrapper {
  padding: 0;
}

.color input::-webkit-color-swatch {
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 8px;
}

.color input::-moz-color-swatch {
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 8px;
}

.range {
  --pct: 50%;
  width: 100%;
  height: 28px;
  background: transparent;
  cursor: pointer;
  -webkit-appearance: none;
  appearance: none;
}

.range::-webkit-slider-runnable-track {
  height: 6px;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--spark) var(--pct), var(--surface-2) var(--pct));
}

.range::-moz-range-track {
  height: 6px;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--spark) var(--pct), var(--surface-2) var(--pct));
}

.range::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 22px;
  height: 22px;
  margin-top: -8px;
  border-radius: 50%;
  background: #fff;
  border: 0;
  box-shadow: 0 0 0 2px var(--spark), 0 2px 6px rgba(0, 0, 0, 0.2);
}

.range::-moz-range-thumb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #fff;
  border: 0;
  box-shadow: 0 0 0 2px var(--spark), 0 2px 6px rgba(0, 0, 0, 0.2);
}

@media (max-width: 420px) {
  .row-2 {
    grid-template-columns: 1fr;
  }

  .swatches {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .color-row {
    grid-template-columns: 1fr;
  }
}
</style>
