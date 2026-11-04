<template>
  <a class="skip" href="#main">Skip to content</a>
  <header class="topbar" :class="{ scrolled }">
    <div class="topbar-inner">
      <router-link to="/" class="brand" aria-label="Sparklets home">
        <span class="brand-mark"><Icon name="sparkle" /></span>
        <span class="brand-word">sparklets</span>
      </router-link>
      <nav class="topnav" aria-label="Main">
        <router-link to="/" class="navlink" exact-active-class="active">Home</router-link>
        <router-link to="/sparklet/1" class="navlink" active-class="active">Example</router-link>
      </nav>
      <router-link to="/create" class="btn btn-primary btn-sm create-btn">
        <Icon name="plus" /> Create
      </router-link>
    </div>
  </header>

  <main id="main">
    <router-view />
  </main>

  <nav class="tabbar" aria-label="Main">
    <router-link to="/" class="tab" exact-active-class="active">
      <Icon name="home" /><span>Home</span>
    </router-link>
    <router-link to="/create" class="tab tab-create" active-class="active" aria-label="Create">
      <span class="tab-plus"><Icon name="plus" /></span>
    </router-link>
    <router-link to="/sparklet/1" class="tab" active-class="active">
      <Icon name="eye" /><span>Example</span>
    </router-link>
  </nav>

  <div class="toasts" role="status" aria-live="polite">
    <TransitionGroup name="toast">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="t.tone">
        <Icon v-if="t.tone === 'ok'" name="check" />
        {{ t.text }}
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import Icon from './components/Icon.vue'
import { toasts } from './lib/toast'

const scrolled = ref(false)
const onScroll = () => {
  scrolled.value = window.scrollY > 4
}
onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onBeforeUnmount(() => window.removeEventListener('scroll', onScroll))
</script>

<style scoped>
.skip {
  position: absolute;
  left: 1rem;
  top: -100px;
  z-index: 200;
  padding: 0.5rem 1rem;
  border-radius: 999px;
  background: var(--ink);
  color: var(--bg);
  font-weight: 700;
}

.skip:focus {
  top: 0.75rem;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  height: var(--topbar-h);
  background: var(--glass);
  backdrop-filter: saturate(1.6) blur(16px);
  -webkit-backdrop-filter: saturate(1.6) blur(16px);
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s;
}

.topbar.scrolled {
  border-bottom-color: var(--line);
}

.topbar-inner {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  height: 100%;
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 1.25rem;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  text-decoration: none;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 11px;
  background: linear-gradient(135deg, var(--sun), var(--spark));
  color: #fff;
  transform: rotate(-6deg);
}

.brand-mark svg {
  width: 20px;
  height: 20px;
  fill: #fff;
  stroke: none;
}

.brand-word {
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  font-variation-settings: 'opsz' 96;
}

.topnav {
  display: flex;
  gap: 0.25rem;
  margin-right: auto;
}

.navlink {
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--ink-2);
  text-decoration: none;
  transition: color 0.15s, background-color 0.15s;
}

.navlink:hover {
  color: var(--ink);
  background: var(--surface-2);
}

.navlink.active {
  color: var(--ink);
  background: var(--surface-2);
}

main {
  min-height: calc(100dvh - var(--topbar-h));
  padding-bottom: var(--tabbar-h);
}

/* ---------- mobile tab bar ---------- */

.tabbar {
  display: none;
}

@media (max-width: 720px) {
  .topnav,
  .create-btn {
    display: none;
  }

  .topbar-inner {
    justify-content: center;
  }

  .tabbar {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 50;
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    height: calc(var(--tabbar-h) + env(safe-area-inset-bottom));
    padding: 0 1.5rem env(safe-area-inset-bottom);
    background: var(--glass);
    backdrop-filter: saturate(1.6) blur(16px);
    -webkit-backdrop-filter: saturate(1.6) blur(16px);
    border-top: 1px solid var(--line);
  }

  .tab {
    display: grid;
    justify-items: center;
    gap: 2px;
    color: var(--ink-3);
    font-size: 0.7rem;
    font-weight: 600;
    text-decoration: none;
  }

  .tab svg {
    width: 24px;
    height: 24px;
  }

  .tab.active {
    color: var(--ink);
  }

  .tab-plus {
    display: grid;
    place-items: center;
    width: 56px;
    height: 40px;
    border-radius: 14px;
    background: linear-gradient(135deg, var(--sun), var(--spark));
    color: #fff;
    box-shadow: 0 6px 16px -6px var(--spark);
  }

  .tab-plus svg {
    stroke-width: 2.6;
  }
}

/* ---------- toasts ---------- */

.toasts {
  position: fixed;
  left: 50%;
  bottom: calc(1.25rem + var(--tabbar-h) + env(safe-area-inset-bottom));
  z-index: 300;
  display: grid;
  gap: 0.5rem;
  justify-items: center;
  transform: translateX(-50%);
  pointer-events: none;
  width: max-content;
  max-width: calc(100vw - 2rem);
}

.toast {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 1.1rem;
  border-radius: 999px;
  background: var(--ink);
  color: var(--bg);
  font-weight: 600;
  font-size: 0.925rem;
  box-shadow: var(--shadow-lg);
}

.toast svg {
  width: 18px;
  height: 18px;
  color: var(--ok);
}

.toast.error {
  background: var(--danger);
  color: #fff;
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.2s, transform 0.25s cubic-bezier(0.2, 1, 0.3, 1);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.96);
}
</style>
