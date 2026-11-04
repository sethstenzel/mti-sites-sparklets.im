<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="overlay" @mousedown.self="close">
        <div
          ref="dialog"
          class="dialog"
          :class="size"
          role="dialog"
          aria-modal="true"
          :aria-label="title"
          tabindex="-1"
          @keydown.esc="close"
        >
          <header class="head">
            <h2>{{ title }}</h2>
            <button type="button" class="btn btn-icon btn-ghost" aria-label="Close" @click="close">
              <Icon name="close" />
            </button>
          </header>
          <div class="body">
            <slot />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import Icon from './Icon.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
  size: { type: String, default: 'md' }
})
const emit = defineEmits(['close'])

const dialog = ref(null)
let lastFocus = null

const close = () => emit('close')

watch(
  () => props.open,
  async (open) => {
    if (open) {
      lastFocus = document.activeElement
      document.body.style.overflow = 'hidden'
      await nextTick()
      dialog.value?.focus()
    } else {
      document.body.style.overflow = ''
      lastFocus?.focus?.()
    }
  }
)

onBeforeUnmount(() => {
  document.body.style.overflow = ''
})
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: grid;
  place-items: center;
  padding: 1rem;
  overflow-y: auto;
  background: rgba(15, 12, 28, 0.5);
  backdrop-filter: blur(6px);
}

.dialog {
  width: 100%;
  max-width: 440px;
  max-height: calc(100dvh - 2rem);
  overflow-y: auto;
  background: var(--surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}

.dialog.lg {
  max-width: 880px;
}

.dialog:focus {
  outline: none;
}

.head {
  position: sticky;
  top: 0;
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 0.75rem 0.75rem 1.4rem;
  background: var(--surface);
  border-bottom: 1px solid var(--line);
}

.head h2 {
  font-size: 1.1rem;
  font-weight: 750;
  letter-spacing: -0.01em;
}

.body {
  padding: 1.4rem;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s;
}

.modal-enter-active .dialog,
.modal-leave-active .dialog {
  transition: transform 0.25s cubic-bezier(0.2, 1, 0.3, 1);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .dialog,
.modal-leave-to .dialog {
  transform: translateY(16px) scale(0.98);
}

@media (max-width: 560px) {
  .overlay {
    place-items: end center;
    padding: 0;
  }

  .dialog {
    max-height: 92dvh;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  }

  .modal-enter-from .dialog,
  .modal-leave-to .dialog {
    transform: translateY(100%);
  }
}
</style>
