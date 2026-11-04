<template>
  <div class="home">
    <section class="hero">
      <div class="hero-copy">
        <h1>Little photo notes that open with a&nbsp;scan.</h1>
        <p class="lede">
          Pick a photo, write up to 138 characters, and send it as a link or a printable QR code.
          No accounts, no app to install.
        </p>
        <div class="cta">
          <router-link to="/create" class="btn btn-primary btn-lg"><Icon name="plus" /> Create a sparklet</router-link>
          <router-link to="/sparklet/1" class="btn btn-ghost btn-lg">See an example</router-link>
        </div>
      </div>

      <div class="hero-stack" aria-hidden="true">
        <div v-for="(s, i) in samples" :key="s.to" class="stack-item" :class="`pos-${i}`">
          <SparkletStage :animation="s.animation">
            <SparkletCard
              :message="s.message"
              :to-name="s.to"
              :from-name="s.from"
              :card-color="s.theme.card_color"
              :text-color="s.theme.text_color"
              :rotation="s.rotation"
            >
              <template #photo><div class="scene" :class="s.scene"></div></template>
            </SparkletCard>
          </SparkletStage>
        </div>
      </div>
    </section>

    <section class="steps" aria-labelledby="how">
      <h2 id="how">How it works</h2>
      <ol>
        <li>
          <span class="step-n">1</span>
          <h3>Pick a photo</h3>
          <p>Drop it into the frame, then drag and zoom until it looks right.</p>
        </li>
        <li>
          <span class="step-n">2</span>
          <h3>Write the note</h3>
          <p>Up to 138 characters. Choose the colors, a tilt, and how the card makes its entrance.</p>
        </li>
        <li>
          <span class="step-n">3</span>
          <h3>Send it</h3>
          <p>Share the link, or save the QR card and tuck it into a lunchbox, a gift, or a birthday card.</p>
        </li>
      </ol>
    </section>

    <section class="playground" aria-labelledby="entrances">
      <div class="play-copy">
        <h2 id="entrances">Every card makes an entrance.</h2>
        <p>When someone opens your sparklet, it arrives with the motion you picked, then hovers on their screen.</p>
        <div class="play-chips" role="radiogroup" aria-label="Preview an entrance">
          <button
            v-for="a in animations"
            :key="a.id"
            type="button"
            role="radio"
            class="chip"
            :class="{ active: demoAnimation === a.id }"
            :aria-checked="demoAnimation === a.id"
            @click="play(a.id)"
          >
            {{ a.name }}
          </button>
        </div>
      </div>
      <div class="play-stage" :style="{ background: demoTheme.background_color }">
        <div class="play-card">
          <SparkletStage :animation="demoAnimation" :play-key="playKey">
            <SparkletCard
              message="You’re my favorite person to get lost with."
              to-name="Robin"
              from-name="Kai"
              :card-color="demoTheme.card_color"
              :text-color="demoTheme.text_color"
              :rotation="-4"
            >
              <template #photo><div class="scene scene-night"></div></template>
            </SparkletCard>
          </SparkletStage>
        </div>
      </div>
    </section>

    <section class="closer">
      <h2>Someone’s day could use a spark.</h2>
      <router-link to="/create" class="btn btn-primary btn-lg"><Icon name="plus" /> Create a sparklet</router-link>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Icon from '../components/Icon.vue'
import SparkletCard from '../components/SparkletCard.vue'
import SparkletStage from '../components/SparkletStage.vue'
import { themes } from '../lib/themes'
import { animations } from '../lib/animations'

const byName = (name) => themes.find((t) => t.name === name)

const samples = [
  {
    to: 'Grandpa',
    from: 'Leo',
    message: 'I scored my first goal today!!',
    theme: byName('Sky'),
    rotation: -7,
    scene: 'scene-field',
    animation: 'rise'
  },
  {
    to: 'Mom',
    from: 'Jess',
    message: 'Thanks for every lunchbox note. Here’s one back ♥',
    theme: byName('Bubblegum'),
    rotation: 5,
    scene: 'scene-sunset',
    animation: 'drop'
  },
  {
    to: 'Sam',
    from: 'Priya',
    message: 'Happy 30th! Dinner’s on me.',
    theme: byName('Classic'),
    rotation: -2,
    scene: 'scene-beach',
    animation: 'pop'
  }
]

const demoAnimation = ref('flip')
const playKey = ref(0)
const demoTheme = byName('Midnight')

const play = (id) => {
  demoAnimation.value = id
  playKey.value++
}
</script>

<style scoped>
.home {
  overflow-x: clip;
}

section {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 1.25rem;
}

h1,
h2 {
  font-weight: 800;
  letter-spacing: -0.035em;
  line-height: 1.02;
  font-variation-settings: 'opsz' 96;
  text-wrap: balance;
}

/* ---------- hero ---------- */

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr);
  align-items: center;
  gap: 3rem;
  min-height: min(760px, calc(100dvh - var(--topbar-h)));
  padding-top: 3rem;
  padding-bottom: 4rem;
}

h1 {
  font-size: clamp(2.6rem, 6.2vw, 5rem);
}

.lede {
  max-width: 34em;
  margin-top: 1.25rem;
  font-size: clamp(1.05rem, 1.6vw, 1.2rem);
  color: var(--ink-2);
}

.cta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 2rem;
}

.hero-stack {
  position: relative;
  aspect-ratio: 1 / 1.02;
  width: 100%;
  max-width: 540px;
  justify-self: center;
}

.stack-item {
  position: absolute;
  width: 58%;
}

.stack-item :deep(.stage) {
  animation-delay: var(--delay, 0s);
}

.pos-0 {
  left: 0;
  top: 6%;
  --delay: 0.35s;
}

.pos-1 {
  right: 0;
  top: 0;
  --delay: 0.15s;
}

.pos-2 {
  left: 22%;
  bottom: 0;
  --delay: 0.55s;
}

.pos-0 :deep(.float) {
  animation-duration: 7s;
}

.pos-2 :deep(.float) {
  animation-duration: 5.5s;
}

/* little CSS "photos" so the samples never depend on uploaded files */
.scene {
  width: 100%;
  height: 100%;
}

.scene-sunset {
  background:
    radial-gradient(circle at 62% 62%, #fff3b0 0 9%, #ffd36b 10% 13%, transparent 14%),
    radial-gradient(120% 60% at 20% 100%, #7b3d6b 0 45%, transparent 46%),
    radial-gradient(120% 55% at 90% 105%, #5a2a55 0 48%, transparent 49%),
    linear-gradient(180deg, #ff9a6b 0%, #ff6f91 55%, #c45ba0 100%);
}

.scene-field {
  background:
    radial-gradient(circle at 70% 58%, #ffffff 0 4.5%, #222 4.6% 5%, transparent 5.1%),
    radial-gradient(160% 70% at 50% 120%, #3fae5e 0 55%, transparent 56%),
    linear-gradient(180deg, #8fd0ff 0%, #c7ecff 70%, #3fae5e 70%);
}

.scene-beach {
  background:
    radial-gradient(circle at 24% 30%, #fff5c2 0 8%, transparent 9%),
    linear-gradient(180deg, #7fd3f0 0 55%, #2b9bc9 55% 72%, #f6dca6 72%);
}

.scene-night {
  background:
    radial-gradient(circle at 78% 26%, #fff8d6 0 7%, transparent 8%),
    radial-gradient(1.5px 1.5px at 20% 30%, #fff 50%, transparent 51%),
    radial-gradient(1.5px 1.5px at 40% 15%, #fff 50%, transparent 51%),
    radial-gradient(2px 2px at 58% 40%, #fff 50%, transparent 51%),
    radial-gradient(1.5px 1.5px at 12% 55%, #fff 50%, transparent 51%),
    radial-gradient(140% 60% at 30% 110%, #1b1840 0 50%, transparent 51%),
    linear-gradient(180deg, #2c2a6b 0%, #5b3f8f 100%);
}

/* ---------- steps ---------- */

.steps {
  padding-top: 4rem;
  padding-bottom: 5rem;
  border-top: 1px solid var(--line);
}

.steps h2,
.closer h2 {
  font-size: clamp(2rem, 4vw, 3rem);
}

.steps ol {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 2.5rem;
  margin-top: 2.5rem;
  list-style: none;
}

.step-n {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  margin-bottom: 1rem;
  border-radius: 14px;
  background: var(--ink);
  color: var(--bg);
  font-weight: 800;
  font-size: 1.15rem;
}

.steps li:nth-child(2) .step-n {
  background: var(--spark);
  color: #fff;
}

.steps li:nth-child(3) .step-n {
  background: var(--accent-2);
  color: var(--on-accent-2);
}

.steps h3 {
  font-size: 1.3rem;
  font-weight: 750;
  letter-spacing: -0.02em;
}

.steps p {
  max-width: 30em;
  margin-top: 0.4rem;
  color: var(--ink-2);
}

/* ---------- entrance playground ---------- */

.playground {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
  gap: 3rem;
  align-items: center;
  padding-bottom: 5rem;
}

.playground h2 {
  font-size: clamp(2rem, 4vw, 3rem);
}

.play-copy p {
  max-width: 30em;
  margin-top: 1rem;
  color: var(--ink-2);
  font-size: 1.1rem;
}

.play-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.chip {
  min-height: 40px;
  padding: 0 1rem;
  border: 1.5px solid var(--line);
  border-radius: 999px;
  background: var(--surface);
  font-weight: 650;
  cursor: pointer;
}

.chip:hover {
  border-color: var(--ink-3);
}

.chip.active {
  border-color: var(--ink);
  background: var(--ink);
  color: var(--bg);
}

.play-stage {
  display: grid;
  place-items: center;
  aspect-ratio: 5 / 4;
  overflow: hidden;
  border-radius: 32px;
}

.play-card {
  width: min(58%, 340px);
}

/* ---------- closer ---------- */

.closer {
  display: grid;
  justify-items: center;
  gap: 1.75rem;
  margin-bottom: 4rem;
  padding: 4.5rem 1.25rem;
  text-align: center;
  border-radius: 32px;
  background: var(--brand-grad);
  color: #fff;
  max-width: calc(1180px - 2.5rem);
}

.closer .btn-primary {
  --btn-bg: #fff;
  --btn-ink: #1d1a2b;
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.35);
}

.closer .btn-primary:hover {
  background: #fff6f8;
}

@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
    gap: 2.5rem;
    min-height: 0;
    padding-top: 2rem;
  }

  .hero-stack {
    max-width: 440px;
  }

  .steps ol {
    grid-template-columns: 1fr;
    gap: 1.75rem;
  }

  .playground {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
}

@media (max-width: 1220px) {
  .closer {
    margin-left: 1.25rem;
    margin-right: 1.25rem;
  }
}
</style>
