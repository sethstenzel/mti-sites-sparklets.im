<template>
  <div class="view" :class="tone" :style="{ background: sparklet?.background_color || 'var(--bg)' }">
    <div v-if="state === 'loading'" class="center">
      <div class="loader" aria-label="Loading sparklet"><Icon name="sparkle" /></div>
    </div>

    <div v-else-if="state === 'error'" class="center">
      <div class="missing panel">
        <div class="missing-art" aria-hidden="true">
          <SparkletCard message="?" card-color="#ffffff" text-color="#8f8aa5" :rotation="-6" />
        </div>
        <h1>{{ notFound ? 'This sparklet isn’t here' : 'Couldn’t load this sparklet' }}</h1>
        <p>{{ notFound ? 'It may have been removed, or the link is incomplete. Check the link and try again.' : errorText }}</p>
        <div class="missing-actions">
          <button v-if="!notFound" type="button" class="btn btn-ghost" @click="load">Try again</button>
          <router-link to="/create" class="btn btn-primary"><Icon name="plus" /> Make your own</router-link>
        </div>
      </div>
    </div>

    <article v-else class="post" :aria-label="`A sparklet from ${sparklet.from_name} to ${sparklet.to_name}`">
      <header class="post-head glass">
        <span class="avatar" aria-hidden="true"><span>{{ initial }}</span></span>
        <p class="byline">
          <strong>{{ sparklet.from_name }}</strong>
          <span>sent {{ sparklet.to_name }} a sparklet</span>
        </p>
        <span v-if="isExample" class="badge">Example</span>
        <time v-else :datetime="sparklet.created_at">{{ timeAgo(sparklet.created_at) }}</time>
      </header>

      <div class="card-slot">
        <SparkletStage :animation="sparklet.entry_animation" :play-key="playKey" :burst-color="sparklet.background_color">
          <SparkletCard
            :message="sparklet.message"
            :to-name="sparklet.to_name"
            :from-name="sparklet.from_name"
            :card-color="sparklet.card_color"
            :text-color="sparklet.text_color"
            :rotation="sparklet.card_rotation"
            :font="sparklet.font"
            :image="photo"
          />
        </SparkletStage>
      </div>

      <footer class="post-actions glass">
        <button type="button" class="act" aria-label="Replay entrance" title="Replay entrance" @click="playKey++">
          <Icon name="reset" />
        </button>
        <button type="button" class="act" aria-label="Copy link" title="Copy link" @click="copyText(url)">
          <Icon name="link" />
        </button>
        <button type="button" class="act" aria-label="Share or get QR code" title="Share" @click="shareOpen = true">
          <Icon name="share" />
        </button>
        <router-link to="/create" class="btn btn-primary btn-sm make">
          <Icon name="plus" /> Make your own
        </router-link>
      </footer>
    </article>

    <Modal :open="shareOpen" title="Share this sparklet" @close="shareOpen = false">
      <SharePanel
        v-if="sparklet"
        :url="url"
        :to-name="sparklet.to_name"
        :from-name="sparklet.from_name"
        :id="sparklet.public_id"
        :background-color="sparklet.background_color"
      />
    </Modal>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { EXAMPLE_SPARKLET } from '../lib/example'
import Icon from '../components/Icon.vue'
import Modal from '../components/Modal.vue'
import SharePanel from '../components/SharePanel.vue'
import SparkletCard from '../components/SparkletCard.vue'
import SparkletStage from '../components/SparkletStage.vue'
import { api, errorMessage, imageUrl, shareUrlFor, timeAgo } from '../lib/api'
import { copyText } from '../lib/toast'
import { contrastInk } from '../lib/themes'

const route = useRoute()
const sparklet = ref(null)
const state = ref('loading')
const notFound = ref(false)
const errorText = ref('')
const playKey = ref(0)
const shareOpen = ref(false)

const isExample = computed(() => !!route.meta.example)
const url = computed(() => {
  if (!sparklet.value) return ''
  return isExample.value ? `${window.location.origin}/example` : shareUrlFor(sparklet.value.public_id)
})
const photo = computed(() => sparklet.value?.image || imageUrl(sparklet.value?.image_filename))
const initial = computed(() => (sparklet.value?.from_name || '?').trim().charAt(0).toUpperCase())
const tone = computed(() => `on-${contrastInk(sparklet.value?.background_color)}`)

// Let the photo arrive before the card makes its entrance (but never wait long).
const preload = (src) =>
  new Promise((resolve) => {
    const img = new Image()
    const done = () => resolve()
    img.onload = done
    img.onerror = done
    setTimeout(done, 2500)
    img.src = src
  })

const load = async () => {
  state.value = 'loading'
  notFound.value = false
  try {
    const data = isExample.value
      ? EXAMPLE_SPARKLET
      : (await api.get(`/api/sparklets/${route.params.token}`)).data
    await preload(data.image || imageUrl(data.image_filename))
    sparklet.value = data
    document.title = `A sparklet for ${data.to_name} · Sparklets`
    state.value = 'ready'
  } catch (err) {
    sparklet.value = null
    notFound.value = err?.response?.status === 404
    errorText.value = errorMessage(err, 'Something went wrong loading this sparklet.')
    state.value = 'error'
  }
}

watch(() => [route.params.token, route.meta.example], () => (route.params.token || route.meta.example) && load(), { immediate: true })
</script>

<style scoped>
.view {
  min-height: calc(100dvh - var(--topbar-h) - var(--tabbar-h));
  display: grid;
  transition: background-color 0.4s;
  overflow: clip;
}

.center {
  display: grid;
  place-items: center;
  padding: 2rem 1rem;
}

.loader {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  border-radius: 18px;
  background: var(--brand-grad);
  color: #fff;
  animation: pulse 1.1s ease-in-out infinite;
}

.loader svg {
  width: 28px;
  height: 28px;
  fill: #fff;
  stroke: none;
}

@keyframes pulse {
  50% { transform: scale(0.86) rotate(12deg); }
}

/* ---------- not found ---------- */

.missing {
  max-width: 420px;
  padding: 2rem;
  text-align: center;
}

.missing-art {
  width: 120px;
  margin: 0 auto 1.5rem;
}

.missing-art :deep(.message) {
  font-size: 30cqw;
}

.missing h1 {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.025em;
  line-height: 1.15;
}

.missing p {
  margin-top: 0.5rem;
  color: var(--ink-2);
}

.missing-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

/* ---------- the post ---------- */

.post {
  display: grid;
  grid-template-rows: auto 1fr auto;
  justify-items: center;
  gap: 1rem;
  width: 100%;
  max-width: 620px;
  margin: 0 auto;
  padding: 1.25rem 1rem 1.5rem;
}

.glass {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: saturate(1.5) blur(14px);
  -webkit-backdrop-filter: saturate(1.5) blur(14px);
  color: #1d1a2b;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05), 0 8px 24px -10px rgba(0, 0, 0, 0.18);
}

.on-dark .glass {
  background: rgba(20, 18, 34, 0.55);
  color: #f3f1fa;
}

.post-head {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.55rem 1rem 0.55rem 0.55rem;
  border-radius: 999px;
}

.avatar {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  flex: none;
  padding: 2.5px;
  border-radius: 50%;
  background: var(--ring);
}

.avatar span {
  display: grid;
  place-items: center;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2.5px solid #fff;
  background: #1d1a2b;
  color: #fff;
  font-weight: 800;
  font-size: 1rem;
}

.byline {
  flex: 1;
  min-width: 0;
  line-height: 1.25;
  font-size: 0.95rem;
}

.byline strong {
  display: block;
  font-weight: 750;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.byline span {
  display: block;
  opacity: 0.75;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.badge {
  flex: none;
  padding: 0.15rem 0.6rem;
  border-radius: 999px;
  background: rgba(127, 127, 127, 0.18);
  font-size: 0.75rem;
  font-weight: 700;
}

time {
  flex: none;
  font-size: 0.8rem;
  font-weight: 600;
  opacity: 0.65;
}

.card-slot {
  align-self: center;
  width: min(500px, 86vw, calc((100dvh - var(--topbar-h) - var(--tabbar-h) - 220px)));
  min-width: 240px;
  padding: 2rem 0;
}

.post-actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.4rem;
  border-radius: 999px;
}

.act {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.act:hover {
  background: rgba(127, 127, 127, 0.16);
}

.act svg {
  width: 21px;
  height: 21px;
}

.make {
  margin-left: 0.35rem;
}
</style>
