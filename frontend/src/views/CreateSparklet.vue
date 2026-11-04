<template>
  <div class="create">
    <section class="composer panel">
      <template v-if="!createdId">
        <header class="composer-head">
          <h1>New sparklet</h1>
          <p>Everything you change shows up on the card as you go.</p>
        </header>

        <form class="form" novalidate @submit.prevent="handleSubmit">
          <div class="field">
            <span class="field-label">Photo</span>
            <PhotoDrop :file-name="imageFile?.name || ''" @select="handleImage" />
          </div>

          <SparkletFields v-model="form" />

          <AnimationPicker v-model="form.entry_animation" @preview="replay" />

          <div v-if="error" class="alert alert-error" role="alert">{{ error }}</div>

          <button type="submit" class="btn btn-primary btn-lg submit" :disabled="submitting">
            <Icon name="sparkle" />
            {{ submitting ? 'Creating…' : 'Create sparklet' }}
          </button>
        </form>
      </template>

      <template v-else>
        <header class="composer-head done">
          <span class="done-badge"><Icon name="check" /></span>
          <h1>Your sparklet is ready</h1>
          <p>Send {{ form.to_name }} the link, or save the QR card to print.</p>
        </header>
        <SharePanel :url="shareUrl" :to-name="form.to_name" :from-name="form.from_name" :id="createdId" />
        <div class="after">
          <button type="button" class="btn btn-ghost" @click="startOver">
            <Icon name="plus" /> Make another
          </button>
          <router-link :to="`/sparklet/${createdId}`" class="btn btn-ghost">
            <Icon name="eye" /> View it
          </router-link>
        </div>
      </template>
    </section>

    <aside class="preview" :style="{ background: form.background_color }" aria-label="Preview">
      <div class="preview-bar">
        <span class="preview-label" :class="contrastInk(form.background_color)">Preview</span>
        <button type="button" class="replay" @click="replay()">
          <Icon name="reset" /> Replay entrance
        </button>
      </div>
      <div class="preview-card">
        <SparkletStage :animation="form.entry_animation" :play-key="playKey" :burst-color="form.background_color">
          <SparkletCard
            :message="form.message"
            :to-name="form.to_name"
            :from-name="form.from_name"
            :card-color="form.card_color"
            :text-color="form.text_color"
            :rotation="form.card_rotation"
            message-placeholder="Your message shows up here"
            to-placeholder="them"
            from-placeholder="you"
          >
            <template #photo>
              <ImageCropper
                v-if="imagePreview && !createdId"
                ref="cropper"
                :src="imagePreview"
                :rotation="form.card_rotation"
                :matte="form.card_color"
                :file-name="imageFile?.name"
              />
              <img v-else-if="croppedPreview" :src="croppedPreview" alt="" class="cropped" />
              <button v-else type="button" class="photo-cta" @click="focusPhotoInput">
                <Icon name="image" />
                <span>Add a photo</span>
              </button>
            </template>
          </SparkletCard>
        </SparkletStage>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import Icon from '../components/Icon.vue'
import SparkletCard from '../components/SparkletCard.vue'
import SparkletStage from '../components/SparkletStage.vue'
import SparkletFields from '../components/SparkletFields.vue'
import AnimationPicker from '../components/AnimationPicker.vue'
import ImageCropper from '../components/ImageCropper.vue'
import PhotoDrop from '../components/PhotoDrop.vue'
import SharePanel from '../components/SharePanel.vue'
import { api, buildSparkletForm, errorMessage, shareUrlFor } from '../lib/api'
import { defaultTheme, contrastInk } from '../lib/themes'
import { defaultAnimation } from '../lib/animations'

const blankForm = () => ({
  to_name: '',
  from_name: '',
  message: '',
  background_color: defaultTheme.background_color,
  card_color: defaultTheme.card_color,
  text_color: defaultTheme.text_color,
  card_rotation: 5,
  entry_animation: defaultAnimation
})

const form = ref(blankForm())
const imageFile = ref(null)
const imagePreview = ref('')
const croppedPreview = ref('')
const cropper = ref(null)
const submitting = ref(false)
const error = ref('')
const createdId = ref(null)
const playKey = ref(0)

const shareUrl = computed(() => (createdId.value ? shareUrlFor(createdId.value) : ''))

const revoke = (url) => url && URL.revokeObjectURL(url)

const handleImage = (file) => {
  revoke(imagePreview.value)
  imageFile.value = file
  imagePreview.value = URL.createObjectURL(file)
  error.value = ''
}

const focusPhotoInput = () => {
  document.querySelector('.composer input[type="file"]')?.click()
}

const replay = () => {
  playKey.value++
}

const validate = () => {
  const f = form.value
  if (!imageFile.value) return 'Add a photo for the card.'
  if (!f.to_name.trim()) return 'Add who the sparklet is for.'
  if (!f.from_name.trim()) return 'Add your name so they know who it’s from.'
  if (!f.message.trim()) return 'Write a short message.'
  return ''
}

const handleSubmit = async () => {
  error.value = validate()
  if (error.value) return

  submitting.value = true
  try {
    const cropped = await cropper.value.getCroppedFile()
    const { data } = await api.post('/api/sparklets', buildSparkletForm(form.value, cropped))
    croppedPreview.value = URL.createObjectURL(cropped)
    createdId.value = data.id
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (err) {
    error.value = errorMessage(err, 'Couldn’t create the sparklet. Try again in a moment.')
  } finally {
    submitting.value = false
  }
}

const startOver = () => {
  revoke(imagePreview.value)
  revoke(croppedPreview.value)
  form.value = blankForm()
  imageFile.value = null
  imagePreview.value = ''
  croppedPreview.value = ''
  createdId.value = null
  error.value = ''
  replay()
}

onBeforeUnmount(() => {
  revoke(imagePreview.value)
  revoke(croppedPreview.value)
})
</script>

<style scoped>
.create {
  display: grid;
  grid-template-columns: minmax(0, 480px) minmax(0, 1fr);
  gap: 1.5rem;
  max-width: 1180px;
  margin: 0 auto;
  padding: 1.5rem 1.25rem 3rem;
  align-items: start;
}

.composer {
  padding: 1.75rem;
}

.composer-head h1 {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.035em;
  line-height: 1.1;
}

.composer-head p {
  margin-top: 0.35rem;
  color: var(--ink-2);
}

.composer-head {
  margin-bottom: 1.75rem;
}

.done-badge {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  margin-bottom: 1rem;
  border-radius: 50%;
  background: var(--ok-soft);
  color: var(--ok);
}

.done-badge svg {
  width: 26px;
  height: 26px;
  stroke-width: 2.6;
}

.form {
  display: grid;
  gap: 1.5rem;
}

.submit {
  width: 100%;
}

.after {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
}

.after .btn {
  flex: 1 1 auto;
}

/* ---------- preview ---------- */

.preview {
  position: sticky;
  top: calc(var(--topbar-h) + 1.5rem);
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: min(720px, calc(100dvh - var(--topbar-h) - 3rem));
  border-radius: 32px;
  overflow: hidden;
  transition: background-color 0.3s;
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.05);
}

.preview-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1rem 0 1.4rem;
}

.preview-label {
  font-weight: 700;
  font-size: 0.9rem;
}

.preview-label.light {
  color: rgba(29, 26, 43, 0.6);
}

.preview-label.dark {
  color: rgba(255, 255, 255, 0.7);
}

.replay {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  min-height: 36px;
  padding: 0 0.9rem;
  border: 0;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  color: #1d1a2b;
  font-weight: 650;
  font-size: 0.85rem;
  cursor: pointer;
  backdrop-filter: blur(8px);
}

.replay:hover {
  background: #fff;
}

.replay svg {
  width: 16px;
  height: 16px;
}

.preview-card {
  align-self: center;
  justify-self: center;
  width: min(440px, 82%);
  padding: 2.5rem 0 3.5rem;
}

/* hold still while someone is framing the photo */
.preview-card:hover :deep(.float),
.preview-card:focus-within :deep(.float) {
  animation-play-state: paused;
}

.cropped {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-cta {
  display: grid;
  place-content: center;
  justify-items: center;
  gap: 1.5cqw;
  width: 100%;
  height: 100%;
  border: 0;
  background: none;
  font-family: var(--font);
  font-size: max(12px, 3.6cqw);
  font-weight: 650;
  color: color-mix(in srgb, var(--note-ink) 60%, transparent);
  cursor: pointer;
}

.photo-cta svg {
  width: 12cqw;
  height: 12cqw;
}

@media (max-width: 900px) {
  .create {
    grid-template-columns: 1fr;
    padding: 1rem 1rem 2rem;
  }

  .preview {
    position: static;
    order: -1;
    min-height: 0;
    border-radius: 24px;
  }

  .preview-card {
    width: min(360px, 76%);
    padding: 2.5rem 0 2.75rem;
  }

  .composer {
    padding: 1.25rem;
  }
}
</style>
