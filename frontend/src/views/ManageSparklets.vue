<template>
  <div class="manage-container">
    <h1>Manage Sparklets</h1>

    <div v-if="loading" class="loading">Loading sparklets...</div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else-if="sparklets.length === 0" class="empty">
      <p>No sparklets found.</p>
    </div>

    <div v-else class="sparklets-grid">
      <div
        v-for="sparklet in sparklets"
        :key="sparklet.id"
        class="sparklet-item"
      >
        <div class="sparklet-preview" :style="{ backgroundColor: sparklet.background_color }">
          <div class="sparklet-card" :style="{ backgroundColor: sparklet.card_color }">
            <div class="image-section">
              <img :src="getImageUrl(sparklet.image_filename)" :alt="`Sparklet ${sparklet.id}`" />
            </div>
            <div class="message-section" :style="{ color: sparklet.text_color }">
              <p class="message">{{ sparklet.message }}</p>
              <div class="metadata">
                <p class="from">From: {{ sparklet.from_name }}</p>
                <p class="to">To: {{ sparklet.to_name }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="sparklet-info">
          <p><strong>ID:</strong> {{ sparklet.id }}</p>
          <p><strong>Created:</strong> {{ formatDate(sparklet.date_created) }}</p>
          <div class="actions">
            <router-link :to="`/sparklet/${sparklet.id}`" class="btn-view">View</router-link>
            <button @click="openEditModal(sparklet)" class="btn-edit">Edit</button>
            <button @click="confirmDelete(sparklet)" class="btn-delete">Delete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="cancelEdit">
      <div class="modal edit-modal" @click.stop>
        <h2>Edit Sparklet</h2>
        <form @submit.prevent="updateSparklet" class="edit-form">
          <div class="form-group">
            <label for="edit_to_name">To:</label>
            <input
              id="edit_to_name"
              v-model="editData.to_name"
              type="text"
              maxlength="100"
              required
            />
          </div>

          <div class="form-group">
            <label for="edit_from_name">From:</label>
            <input
              id="edit_from_name"
              v-model="editData.from_name"
              type="text"
              maxlength="100"
              required
            />
          </div>

          <div class="form-group">
            <label for="edit_message">Message (140 chars):</label>
            <textarea
              id="edit_message"
              v-model="editData.message"
              maxlength="140"
              rows="3"
              required
            ></textarea>
            <span class="char-count">{{ editData.message.length }}/140</span>
          </div>

          <div class="form-group">
            <label for="edit_image">Image (leave empty to keep current):</label>
            <input
              id="edit_image"
              type="file"
              accept="image/*"
              @change="handleEditImageChange"
            />
          </div>

          <div class="color-row">
            <div class="form-group">
              <label for="edit_background_color">Background:</label>
              <input
                id="edit_background_color"
                v-model="editData.background_color"
                type="color"
              />
            </div>

            <div class="form-group">
              <label for="edit_card_color">Card:</label>
              <input
                id="edit_card_color"
                v-model="editData.card_color"
                type="color"
              />
            </div>

            <div class="form-group">
              <label for="edit_text_color">Text:</label>
              <input
                id="edit_text_color"
                v-model="editData.text_color"
                type="color"
              />
            </div>
          </div>

          <div v-if="editError" class="edit-error">{{ editError }}</div>

          <div class="modal-actions">
            <button type="button" @click="cancelEdit" class="btn-cancel">Cancel</button>
            <button type="submit" :disabled="updating" class="btn-save">
              {{ updating ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="cancelDelete">
      <div class="modal" @click.stop>
        <h2>Confirm Delete</h2>
        <p>Are you sure you want to delete this sparklet?</p>
        <div v-if="sparkletToDelete" class="delete-info">
          <p><strong>ID:</strong> {{ sparkletToDelete.id }}</p>
          <p><strong>From:</strong> {{ sparkletToDelete.from_name }}</p>
          <p><strong>To:</strong> {{ sparkletToDelete.to_name }}</p>
        </div>
        <div class="modal-actions">
          <button @click="cancelDelete" class="btn-cancel">Cancel</button>
          <button @click="deleteSparklet" class="btn-confirm-delete">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// In production, use relative URL; in dev, use localhost
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const sparklets = ref([])
const loading = ref(true)
const error = ref(null)
const showDeleteModal = ref(false)
const sparkletToDelete = ref(null)
const showEditModal = ref(false)
const sparkletToEdit = ref(null)
const editData = ref({
  to_name: '',
  from_name: '',
  message: '',
  background_color: '#FFF8DC',
  card_color: '#FFFFFF',
  text_color: '#333333'
})
const editImageFile = ref(null)
const updating = ref(false)
const editError = ref(null)

const loadSparklets = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await axios.get(`${API_BASE_URL}/sparklets`)
    sparklets.value = response.data
  } catch (err) {
    console.error('Failed to load sparklets:', err)
    error.value = 'Failed to load sparklets. Please try again.'
  } finally {
    loading.value = false
  }
}

const getImageUrl = (filename) => {
  return `${API_BASE_URL}/contents/imgs/${filename}`
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}

const openEditModal = (sparklet) => {
  sparkletToEdit.value = sparklet
  editData.value = {
    to_name: sparklet.to_name,
    from_name: sparklet.from_name,
    message: sparklet.message,
    background_color: sparklet.background_color,
    card_color: sparklet.card_color,
    text_color: sparklet.text_color
  }
  editImageFile.value = null
  editError.value = null
  showEditModal.value = true
}

const cancelEdit = () => {
  sparkletToEdit.value = null
  editImageFile.value = null
  editError.value = null
  showEditModal.value = false
}

const handleEditImageChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    editImageFile.value = file
  }
}

const updateSparklet = async () => {
  if (!sparkletToEdit.value) return

  try {
    updating.value = true
    editError.value = null

    const formData = new FormData()
    formData.append('to_name', editData.value.to_name)
    formData.append('from_name', editData.value.from_name)
    formData.append('message', editData.value.message)
    formData.append('background_color', editData.value.background_color)
    formData.append('card_color', editData.value.card_color)
    formData.append('text_color', editData.value.text_color)

    if (editImageFile.value) {
      formData.append('image', editImageFile.value)
    }

    await axios.put(`${API_BASE_URL}/sparklets/${sparkletToEdit.value.id}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    // Reload sparklets to get updated data
    await loadSparklets()

    // Close modal
    cancelEdit()
  } catch (err) {
    console.error('Failed to update sparklet:', err)
    editError.value = err.response?.data?.detail || 'Failed to update sparklet. Please try again.'
  } finally {
    updating.value = false
  }
}

const confirmDelete = (sparklet) => {
  sparkletToDelete.value = sparklet
  showDeleteModal.value = true
}

const cancelDelete = () => {
  sparkletToDelete.value = null
  showDeleteModal.value = false
}

const deleteSparklet = async () => {
  if (!sparkletToDelete.value) return

  try {
    await axios.delete(`${API_BASE_URL}/sparklets/${sparkletToDelete.value.id}`)

    // Remove from local array
    sparklets.value = sparklets.value.filter(s => s.id !== sparkletToDelete.value.id)

    // Close modal
    cancelDelete()
  } catch (err) {
    console.error('Failed to delete sparklet:', err)
    error.value = 'Failed to delete sparklet. Please try again.'
    cancelDelete()
  }
}

onMounted(() => {
  loadSparklets()
})
</script>

<style scoped>
.manage-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 2rem;
  color: #333;
  text-align: center;
}

.loading,
.error,
.empty {
  text-align: center;
  padding: 3rem;
  font-size: 1.2rem;
}

.error {
  color: #e74c3c;
}

.empty {
  color: #666;
}

.sparklets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.sparklet-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.sparklet-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.sparklet-preview {
  padding: 1rem;
  min-height: 250px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sparklet-card {
  width: 200px;
  height: 200px;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transform: rotate(5deg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.image-section {
  flex: 2;
  overflow: hidden;
}

.image-section img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-section {
  flex: 1;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 0.7rem;
}

.message {
  margin: 0;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.metadata {
  margin-top: 0.25rem;
}

.metadata p {
  margin: 0;
  font-size: 0.65rem;
}

.sparklet-info {
  padding: 1rem;
  background: #f9f9f9;
}

.sparklet-info p {
  margin: 0.5rem 0;
  font-size: 0.9rem;
  color: #666;
}

.actions {
  margin-top: 1rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.btn-view,
.btn-edit,
.btn-delete {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
  text-decoration: none;
  text-align: center;
}

.btn-view {
  background: #5568d3;
  color: white;
  display: block;
  grid-column: span 2;
}

.btn-view:hover {
  background: #4456b8;
}

.btn-edit {
  background: #ff9800;
  color: white;
}

.btn-edit:hover {
  background: #f57c00;
}

.btn-delete {
  background: #e74c3c;
  color: white;
}

.btn-delete:hover {
  background: #c0392b;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  overflow-y: auto;
  padding: 2rem 1rem;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  margin: auto;
}

.edit-modal {
  max-width: 600px;
}

.modal h2 {
  margin: 0 0 1rem 0;
  color: #333;
}

.modal p {
  margin: 0.5rem 0;
  color: #666;
}

.delete-info {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 4px;
  margin: 1rem 0;
}

.delete-info p {
  margin: 0.25rem 0;
  font-size: 0.9rem;
}

/* Edit Form Styles */
.edit-form {
  margin-top: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-size: 0.9rem;
}

.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.3s;
}

.form-group input[type="text"]:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #5568d3;
}

.form-group textarea {
  resize: vertical;
}

.char-count {
  display: block;
  text-align: right;
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.25rem;
}

.form-group input[type="file"] {
  padding: 0.5rem;
  border: 2px dashed #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  width: 100%;
}

.color-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group input[type="color"] {
  width: 100%;
  height: 50px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  padding: 0.25rem;
}

.edit-error {
  padding: 1rem;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 6px;
  text-align: center;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.modal-actions {
  margin-top: 1.5rem;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-cancel,
.btn-confirm-delete,
.btn-save {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
  font-weight: 600;
}

.btn-cancel {
  background: #95a5a6;
  color: white;
}

.btn-cancel:hover {
  background: #7f8c8d;
}

.btn-confirm-delete {
  background: #e74c3c;
  color: white;
}

.btn-confirm-delete:hover {
  background: #c0392b;
}

.btn-save {
  background: #4caf50;
  color: white;
}

.btn-save:hover {
  background: #45a049;
}

.btn-save:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .manage-container {
    padding: 1rem;
  }

  h1 {
    font-size: 2rem;
  }

  .sparklets-grid {
    grid-template-columns: 1fr;
  }

  .modal {
    padding: 1.5rem;
  }

  .color-row {
    grid-template-columns: 1fr;
  }
}
</style>
