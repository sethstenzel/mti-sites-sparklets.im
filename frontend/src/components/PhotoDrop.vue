<template>
  <div
    class="drop"
    :class="{ over: isOver, compact: !!fileName }"
    @dragenter.prevent="isOver = true"
    @dragover.prevent="isOver = true"
    @dragleave.prevent="isOver = false"
    @drop.prevent="onDrop"
  >
    <input
      :id="inputId"
      ref="input"
      class="visually-hidden"
      type="file"
      accept="image/*"
      @change="onChange"
    />
    <template v-if="fileName">
      <span class="thumb"><Icon name="image" /></span>
      <span class="name">{{ fileName }}</span>
      <label :for="inputId" class="btn btn-sm btn-ghost">Replace</label>
    </template>
    <label v-else :for="inputId" class="empty">
      <span class="icon"><Icon name="image" /></span>
      <span class="title">{{ label }}</span>
      <span class="sub">Drop a photo here or tap to browse</span>
    </label>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Icon from './Icon.vue'

defineProps({
  fileName: { type: String, default: '' },
  label: { type: String, default: 'Add a photo' }
})
const emit = defineEmits(['select'])

const inputId = `photo-${Math.random().toString(36).slice(2, 8)}`
const input = ref(null)
const isOver = ref(false)

const pick = (file) => {
  if (file && file.type.startsWith('image/')) emit('select', file)
}

const onChange = (e) => {
  pick(e.target.files?.[0])
  e.target.value = ''
}

const onDrop = (e) => {
  isOver.value = false
  pick(e.dataTransfer?.files?.[0])
}
</script>

<style scoped>
.drop {
  border: 2px dashed var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  transition: border-color 0.15s, background-color 0.15s;
}

.drop.over {
  border-color: var(--spark);
  background: var(--spark-soft);
}

.drop:focus-within {
  border-color: var(--spark);
}

.empty {
  display: grid;
  justify-items: center;
  gap: 0.2rem;
  padding: 1.5rem 1rem;
  text-align: center;
  cursor: pointer;
}

.icon {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  margin-bottom: 0.4rem;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--sun), var(--spark));
  color: #fff;
}

.icon svg {
  width: 24px;
  height: 24px;
}

.title {
  font-weight: 700;
}

.sub {
  font-size: 0.875rem;
  color: var(--ink-3);
}

.compact {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.5rem 0.5rem 0.6rem;
  border-style: solid;
  border-width: 1.5px;
}

.thumb {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  flex: none;
  border-radius: 10px;
  background: var(--surface-2);
  color: var(--ink-2);
}

.thumb svg {
  width: 20px;
  height: 20px;
}

.name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.925rem;
  font-weight: 600;
}
</style>
