<template>
  <div class="manage">
    <!-- token gate -->
    <div v-if="!authed" class="gate-wrap">
      <form class="gate panel" @submit.prevent="signIn">
        <span class="gate-icon"><Icon name="lock" /></span>
        <h1>Manage sparklets</h1>
        <p>Enter the admin token from the server’s <code>backend/.env</code> file.</p>
        <label class="field">
          <span class="visually-hidden">Admin token</span>
          <input v-model="tokenInput" class="input" type="password" autocomplete="current-password" placeholder="Admin token" required />
        </label>
        <div v-if="gateError" class="alert alert-error" role="alert">{{ gateError }}</div>
        <button type="submit" class="btn btn-primary" :disabled="checking || !tokenInput">
          {{ checking ? 'Checking…' : 'Unlock' }}
        </button>
      </form>
    </div>

    <template v-else>
      <header class="head">
        <div>
          <h1>Manage sparklets</h1>
          <p>{{ sparklets.length }} {{ sparklets.length === 1 ? 'sparklet' : 'sparklets' }}</p>
        </div>
        <div class="head-tools">
          <input v-model="query" class="input search" type="search" placeholder="Search names or messages" aria-label="Search sparklets" />
          <button type="button" class="btn btn-ghost" @click="signOut"><Icon name="logout" /> Lock</button>
        </div>
      </header>

      <div v-if="loading" class="grid">
        <div v-for="n in 6" :key="n" class="tile skeleton"></div>
      </div>

      <div v-else-if="loadError" class="empty">
        <p>{{ loadError }}</p>
        <button type="button" class="btn btn-ghost" @click="loadSparklets">Try again</button>
      </div>

      <div v-else-if="filtered.length === 0" class="empty">
        <p>{{ query ? 'No sparklets match that search.' : 'No sparklets yet.' }}</p>
        <router-link v-if="!query" to="/create" class="btn btn-primary"><Icon name="plus" /> Create one</router-link>
      </div>

      <div v-else class="grid">
        <article v-for="s in filtered" :key="s.id" class="tile">
          <router-link :to="`/sparklet/${s.id}`" class="thumb" :style="{ background: s.background_color }" :aria-label="`Open sparklet ${s.id}`">
            <div class="thumb-card">
              <SparkletCard
                :message="s.message"
                :to-name="s.to_name"
                :from-name="s.from_name"
                :card-color="s.card_color"
                :text-color="s.text_color"
                :rotation="s.card_rotation"
                :image="imageUrl(s.image_filename)"
               
              />
            </div>
          </router-link>
          <div class="meta">
            <div class="who">
              <strong>{{ s.from_name }}</strong>
              <Icon name="arrowRight" />
              <strong>{{ s.to_name }}</strong>
            </div>
            <p class="sub">
              <span>#{{ s.id }}</span>
              <time :datetime="s.date_created" :title="fullDate(s.date_created)">{{ timeAgo(s.date_created) }}</time>
              <span class="anim">{{ animationName(s.entry_animation) }}</span>
            </p>
            <div class="tile-actions">
              <button type="button" class="btn btn-sm btn-ghost" @click="openEdit(s)"><Icon name="edit" /> Edit</button>
              <button type="button" class="btn btn-sm btn-ghost danger" @click="toDelete = s"><Icon name="trash" /> Delete</button>
            </div>
          </div>
        </article>
      </div>
    </template>

    <!-- edit -->
    <Modal :open="!!editing" :title="editing ? `Edit sparklet #${editing.id}` : ''" size="lg" @close="closeEdit">
      <form v-if="editing" class="edit" @submit.prevent="saveEdit">
        <div class="edit-preview" :style="{ background: editData.background_color }">
          <div class="edit-card">
            <SparkletStage :animation="editData.entry_animation" :play-key="editPlayKey" :float="false" :burst-color="editData.background_color">
              <SparkletCard
                :message="editData.message"
                :to-name="editData.to_name"
                :from-name="editData.from_name"
                :card-color="editData.card_color"
                :text-color="editData.text_color"
                :rotation="editData.card_rotation"
              >
                <template #photo>
                  <ImageCropper
                    v-if="editImagePreview"
                    ref="editCropper"
                    :src="editImagePreview"
                    :rotation="editData.card_rotation"
                    :matte="editData.card_color"
                    :file-name="editImageFile?.name"
                  />
                  <img v-else :src="imageUrl(editing.image_filename)" alt="" class="current-photo" />
                </template>
              </SparkletCard>
            </SparkletStage>
          </div>
        </div>
        <div class="edit-fields">
          <div class="field">
            <span class="field-label">Photo</span>
            <PhotoDrop :file-name="editImageFile?.name || ''" label="Replace the photo" @select="pickEditImage" />
          </div>
          <SparkletFields v-model="editData" />
          <AnimationPicker v-model="editData.entry_animation" @preview="editPlayKey++" />
          <div v-if="editError" class="alert alert-error" role="alert">{{ editError }}</div>
          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="closeEdit">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">{{ saving ? 'Saving…' : 'Save changes' }}</button>
          </div>
        </div>
      </form>
    </Modal>

    <!-- delete -->
    <Modal :open="!!toDelete" title="Delete this sparklet?" @close="toDelete = null">
      <template v-if="toDelete">
        <p class="confirm-text">
          The card from <strong>{{ toDelete.from_name }}</strong> to <strong>{{ toDelete.to_name }}</strong> and its photo
          will be removed. Anyone with the link or QR code will see a “not found” page. This can’t be undone.
        </p>
        <div class="modal-actions">
          <button type="button" class="btn btn-ghost" @click="toDelete = null">Cancel</button>
          <button type="button" class="btn btn-danger" :disabled="deleting" @click="deleteSparklet">
            {{ deleting ? 'Deleting…' : 'Delete sparklet' }}
          </button>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import Icon from '../components/Icon.vue'
import Modal from '../components/Modal.vue'
import SparkletCard from '../components/SparkletCard.vue'
import SparkletStage from '../components/SparkletStage.vue'
import SparkletFields from '../components/SparkletFields.vue'
import AnimationPicker from '../components/AnimationPicker.vue'
import ImageCropper from '../components/ImageCropper.vue'
import PhotoDrop from '../components/PhotoDrop.vue'
import {
  api,
  adminHeaders,
  buildSparkletForm,
  errorMessage,
  getAdminToken,
  imageUrl,
  parseDate,
  setAdminToken,
  timeAgo
} from '../lib/api'
import { animations } from '../lib/animations'
import { toast } from '../lib/toast'

const authed = ref(false)
const tokenInput = ref('')
const checking = ref(false)
const gateError = ref('')

const sparklets = ref([])
const loading = ref(false)
const loadError = ref('')
const query = ref('')

const editing = ref(null)
const editData = ref({})
const editImageFile = ref(null)
const editImagePreview = ref('')
const editCropper = ref(null)
const editPlayKey = ref(0)
const editError = ref('')
const saving = ref(false)

const toDelete = ref(null)
const deleting = ref(false)

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return sparklets.value
  return sparklets.value.filter((s) =>
    [s.to_name, s.from_name, s.message, String(s.id)].some((v) => v?.toLowerCase().includes(q))
  )
})

const animationName = (id) => animations.find((a) => a.id === id)?.name || 'Drop'
const fullDate = (value) => parseDate(value)?.toLocaleString() || ''

const handleAuthError = (err) => {
  if (err?.response?.status === 401) {
    setAdminToken('')
    authed.value = false
    gateError.value = 'Your admin token was rejected. Enter it again.'
    return true
  }
  return false
}

const signIn = async () => {
  checking.value = true
  gateError.value = ''
  try {
    await api.get('/api/admin/check', { headers: adminHeaders(tokenInput.value) })
    setAdminToken(tokenInput.value)
    authed.value = true
    tokenInput.value = ''
    loadSparklets()
  } catch (err) {
    gateError.value =
      err?.response?.status === 401 ? 'That token doesn’t match. Check it and try again.' : errorMessage(err, 'Couldn’t verify the token.')
  } finally {
    checking.value = false
  }
}

const signOut = () => {
  setAdminToken('')
  authed.value = false
  sparklets.value = []
}

const loadSparklets = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const { data } = await api.get('/api/sparklets', { headers: adminHeaders() })
    sparklets.value = data
  } catch (err) {
    if (!handleAuthError(err)) loadError.value = errorMessage(err, 'Couldn’t load sparklets.')
  } finally {
    loading.value = false
  }
}

const clearEditImage = () => {
  if (editImagePreview.value) URL.revokeObjectURL(editImagePreview.value)
  editImagePreview.value = ''
  editImageFile.value = null
}

const openEdit = (s) => {
  editing.value = s
  editData.value = {
    to_name: s.to_name,
    from_name: s.from_name,
    message: s.message,
    background_color: s.background_color,
    card_color: s.card_color,
    text_color: s.text_color,
    card_rotation: s.card_rotation ?? 5,
    entry_animation: s.entry_animation || 'drop'
  }
  clearEditImage()
  editError.value = ''
}

const closeEdit = () => {
  editing.value = null
  clearEditImage()
}

const pickEditImage = (file) => {
  clearEditImage()
  editImageFile.value = file
  editImagePreview.value = URL.createObjectURL(file)
}

const saveEdit = async () => {
  const d = editData.value
  if (!d.to_name.trim() || !d.from_name.trim() || !d.message.trim()) {
    editError.value = 'To, From and Message all need something in them.'
    return
  }
  saving.value = true
  editError.value = ''
  try {
    const file = editImagePreview.value ? await editCropper.value.getCroppedFile() : null
    await api.put(`/api/sparklets/${editing.value.id}`, buildSparkletForm(d, file), { headers: adminHeaders() })
    toast('Changes saved', { tone: 'ok' })
    closeEdit()
    await loadSparklets()
  } catch (err) {
    if (handleAuthError(err)) closeEdit()
    else editError.value = errorMessage(err, 'Couldn’t save changes.')
  } finally {
    saving.value = false
  }
}

const deleteSparklet = async () => {
  deleting.value = true
  const target = toDelete.value
  try {
    await api.delete(`/api/sparklets/${target.id}`, { headers: adminHeaders() })
    sparklets.value = sparklets.value.filter((s) => s.id !== target.id)
    toast('Sparklet deleted', { tone: 'ok' })
    toDelete.value = null
  } catch (err) {
    toDelete.value = null
    if (!handleAuthError(err)) toast(errorMessage(err, 'Couldn’t delete that sparklet.'), { tone: 'error' })
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  if (getAdminToken()) {
    authed.value = true
    loadSparklets()
  }
})

onBeforeUnmount(clearEditImage)
</script>

<style scoped>
.manage {
  max-width: 1180px;
  margin: 0 auto;
  padding: 1.5rem 1.25rem 3rem;
}

h1 {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.035em;
  line-height: 1.1;
}

/* ---------- gate ---------- */

.gate-wrap {
  display: grid;
  place-items: center;
  min-height: 60dvh;
}

.gate {
  display: grid;
  gap: 1rem;
  width: 100%;
  max-width: 380px;
  padding: 2rem;
  text-align: center;
}

.gate-icon {
  display: grid;
  place-items: center;
  width: 52px;
  height: 52px;
  margin: 0 auto;
  border-radius: 16px;
  background: var(--surface-2);
}

.gate-icon svg {
  width: 26px;
  height: 26px;
}

.gate h1 {
  font-size: 1.5rem;
}

.gate p {
  color: var(--ink-2);
  font-size: 0.95rem;
}

code {
  padding: 0.1em 0.35em;
  border-radius: 6px;
  background: var(--surface-2);
  font-size: 0.9em;
}

/* ---------- list ---------- */

.head {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.head p {
  color: var(--ink-2);
}

.head-tools {
  display: flex;
  gap: 0.5rem;
}

.search {
  width: min(320px, 60vw);
  border-radius: 999px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.25rem;
}

.tile {
  overflow: hidden;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
}

.tile.skeleton {
  aspect-ratio: 0.78;
  background: linear-gradient(100deg, var(--surface) 30%, var(--surface-2) 50%, var(--surface) 70%) 0 0 / 300% 100%;
  animation: shimmer 1.4s linear infinite;
}

@keyframes shimmer {
  to { background-position: -150% 0; }
}

.thumb {
  display: grid;
  place-items: center;
  aspect-ratio: 1.15;
}

.thumb-card {
  width: 62%;
  transition: transform 0.25s cubic-bezier(0.2, 1, 0.3, 1);
}

.thumb:hover .thumb-card {
  transform: translateY(-4px) scale(1.03);
}

.meta {
  padding: 0.9rem 1rem 1rem;
}

.who {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  min-width: 0;
}

.who strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 700;
}

.who svg {
  width: 16px;
  height: 16px;
  flex: none;
  color: var(--ink-3);
}

.sub {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-top: 0.15rem;
  font-size: 0.825rem;
  color: var(--ink-3);
}

.anim {
  padding: 0 0.5rem;
  border-radius: 999px;
  background: var(--surface-2);
  color: var(--ink-2);
  font-weight: 600;
}

.tile-actions {
  display: flex;
  gap: 0.4rem;
  margin-top: 0.8rem;
}

.tile-actions .btn {
  flex: 1;
}

.danger {
  color: var(--danger);
}

.empty {
  display: grid;
  justify-items: center;
  gap: 1rem;
  padding: 4rem 1rem;
  color: var(--ink-2);
}

/* ---------- modals ---------- */

.edit {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.1fr);
  gap: 1.5rem;
  align-items: start;
}

.edit-preview {
  position: sticky;
  top: 1rem;
  display: grid;
  place-items: center;
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: var(--radius-lg);
}

.edit-card {
  width: 72%;
}

.current-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.edit-fields {
  display: grid;
  gap: 1.25rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.confirm-text {
  color: var(--ink-2);
}

.confirm-text strong {
  color: var(--ink);
}

@media (max-width: 760px) {
  .edit {
    grid-template-columns: 1fr;
  }

  .edit-preview {
    position: static;
  }

  .head-tools {
    width: 100%;
  }

  .search {
    flex: 1;
    width: auto;
  }
}
</style>
