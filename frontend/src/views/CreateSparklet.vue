<template>
  <div class="create-container">
    <div class="content-wrapper">
      <div class="form-wrapper">
        <h1>Create a Sparklet</h1>
        <p class="subtitle">Send a special message to someone you care about</p>

        <form @submit.prevent="handleSubmit" class="sparklet-form">
        <div class="form-group">
          <label for="to_name">To:</label>
          <input
            id="to_name"
            v-model="formData.to_name"
            type="text"
            maxlength="100"
            required
            placeholder="Recipient name"
          />
        </div>

        <div class="form-group">
          <label for="from_name">From:</label>
          <input
            id="from_name"
            v-model="formData.from_name"
            type="text"
            maxlength="100"
            required
            placeholder="Your name"
          />
        </div>

        <div class="form-group">
          <label for="message">Message ({{ formData.message.length }}/140):</label>
          <textarea
            id="message"
            v-model="formData.message"
            maxlength="140"
            required
            rows="4"
            placeholder="Write your message here..."
          ></textarea>
        </div>

        <div class="form-group">
          <label for="image">Image:</label>
          <input
            id="image"
            type="file"
            accept="image/*"
            required
            @change="handleImageChange"
          />
        </div>

        <div class="color-row">
          <div class="form-group">
            <label for="background_color">Background:</label>
            <input
              id="background_color"
              v-model="formData.background_color"
              type="color"
            />
          </div>

          <div class="form-group">
            <label for="card_color">Card:</label>
            <input
              id="card_color"
              v-model="formData.card_color"
              type="color"
            />
          </div>

          <div class="form-group">
            <label for="text_color">Text:</label>
            <input
              id="text_color"
              v-model="formData.text_color"
              type="color"
            />
          </div>
        </div>

        <button type="submit" :disabled="submitting" class="submit-btn">
          {{ submitting ? 'Creating...' : 'Create Sparklet' }}
        </button>

        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-section">
          <div class="success-message">
            Sparklet created successfully!
          </div>

          <div class="share-actions">
            <h3>Share Your Sparklet</h3>

            <div class="share-link-section">
              <label>Share Link:</label>
              <div class="link-container">
                <input
                  type="text"
                  :value="shareUrl"
                  readonly
                  @click="copyToClipboard(shareUrl)"
                  class="share-link-input"
                />
                <button @click="copyToClipboard(shareUrl)" class="copy-btn">Copy</button>
              </div>
            </div>

            <div class="action-buttons">
              <button @click="downloadSparkletImage" class="action-btn download-btn">
                📥 Download Sparklet
              </button>
              <button @click="downloadShareQR" class="action-btn qr-btn">
                📱 Download Share QR Code
              </button>
              <router-link :to="`/sparklet/${createdId}`" class="action-btn view-btn">
                👁️ View Sparklet
              </router-link>
            </div>

            <div v-if="qrCodeUrl" class="qr-preview">
              <h4>Share QR Code</h4>
              <img :src="qrCodeUrl" alt="QR Code" class="qr-image" />
              <p class="qr-hint">Scan to view the sparklet</p>
            </div>
          </div>
        </div>
      </form>
    </div>

    <div class="preview-wrapper">
      <h2>Preview</h2>
      <div class="preview-container" :style="{ backgroundColor: formData.background_color }">
        <div class="sparklet-preview" :style="{ backgroundColor: formData.card_color }">
          <div class="preview-image-section">
            <img v-if="imagePreview" :src="imagePreview" alt="Preview" />
            <div v-else class="placeholder-image">
              <span>📸</span>
              <p>Upload an image</p>
            </div>
          </div>
          <div class="preview-message-section" :style="{ color: formData.text_color }">
            <p class="preview-message">{{ formData.message || 'Your message will appear here...' }}</p>
            <div class="preview-metadata">
              <p class="preview-from">From: {{ formData.from_name || 'Your name' }}</p>
              <p class="preview-to">To: {{ formData.to_name || 'Recipient name' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import html2canvas from 'html2canvas'
import QRCode from 'qrcode'

const router = useRouter()

const formData = ref({
  to_name: '',
  from_name: '',
  message: '',
  background_color: '#FFF8DC',
  card_color: '#FFFACD',
  text_color: '#2F4F4F'
})

const imageFile = ref(null)
const imagePreview = ref(null)
const submitting = ref(false)
const error = ref(null)
const success = ref(false)
const createdId = ref(null)
const qrCodeUrl = ref(null)

const shareUrl = computed(() => {
  if (!createdId.value) return ''
  return `${window.location.origin}/sparklet/${createdId.value}`
})

const handleImageChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    imageFile.value = file

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const handleSubmit = async () => {
  if (!imageFile.value) {
    error.value = 'Please select an image'
    return
  }

  submitting.value = true
  error.value = null
  success.value = false

  try {
    const formDataToSend = new FormData()
    formDataToSend.append('to_name', formData.value.to_name)
    formDataToSend.append('from_name', formData.value.from_name)
    formDataToSend.append('message', formData.value.message)
    formDataToSend.append('background_color', formData.value.background_color)
    formDataToSend.append('card_color', formData.value.card_color)
    formDataToSend.append('text_color', formData.value.text_color)
    formDataToSend.append('image', imageFile.value)

    const response = await axios.post('/api/sparklets', formDataToSend, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    createdId.value = response.data.id
    success.value = true

    // Generate QR code
    await generateQRCode()

    // Scroll to show share section
    setTimeout(() => {
      const shareSection = document.querySelector('.success-section')
      if (shareSection) {
        shareSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
      }
    }, 100)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create sparklet'
  } finally {
    submitting.value = false
  }
}

const generateQRCode = async () => {
  try {
    const url = shareUrl.value
    const qrDataUrl = await QRCode.toDataURL(url, {
      width: 300,
      margin: 2,
      color: {
        dark: '#5568d3',
        light: '#ffffff'
      }
    })
    qrCodeUrl.value = qrDataUrl
  } catch (err) {
    console.error('Failed to generate QR code:', err)
  }
}

const downloadSparkletImage = async () => {
  try {
    const previewCard = document.querySelector('.sparklet-preview')
    if (!previewCard) return

    const canvas = await html2canvas(previewCard, {
      backgroundColor: null,
      scale: 2,
      logging: false
    })

    const link = document.createElement('a')
    link.download = `sparklet-${createdId.value}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  } catch (err) {
    console.error('Failed to download sparklet:', err)
    error.value = 'Failed to download sparklet image'
  }
}

const downloadShareQR = () => {
  if (!qrCodeUrl.value) return

  const link = document.createElement('a')
  link.download = `sparklet-${createdId.value}-qr.png`
  link.href = qrCodeUrl.value
  link.click()
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    // You could add a toast notification here
    alert('Link copied to clipboard!')
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}
</script>

<style scoped>
.create-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 1rem;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  align-items: start;
}

.form-wrapper {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  width: 100%;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.preview-wrapper {
  position: sticky;
  top: 2rem;
}

.preview-wrapper h2 {
  color: white;
  margin: 0 0 1rem 0;
  text-align: center;
  font-size: 1.5rem;
}

.preview-container {
  min-height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  border-radius: 12px;
  transition: background-color 0.3s ease;
}

.sparklet-preview {
  width: 90%;
  max-width: 350px;
  aspect-ratio: 1;
  border-radius: 8px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  transform: rotate(10deg);
  transition: all 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sparklet-preview:hover {
  transform: rotate(10deg) translateY(-8px);
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.3);
}

.preview-image-section {
  flex: 2;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
}

.preview-image-section img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder-image {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  text-align: center;
}

.placeholder-image span {
  font-size: 4rem;
  margin-bottom: 0.5rem;
}

.placeholder-image p {
  margin: 0;
  font-size: 0.9rem;
}

.preview-message-section {
  flex: 1;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.preview-message {
  font-size: 0.9rem;
  line-height: 1.4;
  margin: 0 0 0.5rem 0;
  overflow-wrap: break-word;
  font-style: italic;
}

.preview-metadata {
  font-size: 0.75rem;
  opacity: 0.8;
}

.preview-metadata p {
  margin: 0.25rem 0;
}

.preview-from {
  font-weight: 600;
}

.preview-to {
  font-style: italic;
}

h1 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 2rem;
}

.subtitle {
  color: #666;
  margin: 0 0 2rem 0;
}

.sparklet-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-size: 0.95rem;
}

.form-group input[type="text"],
.form-group textarea {
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
  border-color: #667eea;
}

.form-group input[type="file"] {
  padding: 0.5rem;
  border: 2px dashed #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
}

.color-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.form-group input[type="color"] {
  width: 100%;
  height: 50px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem;
  border: none;
  border-radius: 6px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  padding: 1rem;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 6px;
  text-align: center;
  margin-bottom: 1rem;
}

.success-section {
  margin-top: 1.5rem;
}

.success-message {
  padding: 1rem;
  background-color: #e8f5e9;
  color: #2e7d32;
  border-radius: 6px;
  text-align: center;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.share-actions {
  background: #f9f9f9;
  padding: 1.5rem;
  border-radius: 8px;
  border: 2px solid #e0e0e0;
}

.share-actions h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.share-link-section {
  margin-bottom: 1.5rem;
}

.share-link-section label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-size: 0.9rem;
}

.link-container {
  display: flex;
  gap: 0.5rem;
}

.share-link-input {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 0.9rem;
  background: white;
  cursor: pointer;
}

.share-link-input:focus {
  outline: none;
  border-color: #5568d3;
}

.copy-btn {
  padding: 0.75rem 1.5rem;
  background: #5568d3;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.copy-btn:hover {
  background: #4456b8;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.action-btn {
  padding: 1rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.download-btn {
  background: #4caf50;
  color: white;
}

.download-btn:hover {
  background: #45a049;
  transform: translateY(-2px);
}

.qr-btn {
  background: #2196f3;
  color: white;
}

.qr-btn:hover {
  background: #1976d2;
  transform: translateY(-2px);
}

.view-btn {
  background: #ff9800;
  color: white;
}

.view-btn:hover {
  background: #f57c00;
  transform: translateY(-2px);
}

.qr-preview {
  text-align: center;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  border: 2px solid #e0e0e0;
}

.qr-preview h4 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1rem;
}

.qr-image {
  max-width: 250px;
  width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.qr-hint {
  margin: 1rem 0 0 0;
  color: #666;
  font-size: 0.9rem;
  font-style: italic;
}

@media (max-width: 1024px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }

  .preview-wrapper {
    position: static;
    order: -1;
  }

  .preview-container {
    min-height: 400px;
  }

  .sparklet-preview {
    max-width: 300px;
  }
}

@media (max-width: 640px) {
  .form-wrapper {
    padding: 1.5rem;
  }

  h1 {
    font-size: 1.5rem;
  }

  .color-row {
    grid-template-columns: 1fr;
  }

  .preview-container {
    min-height: 350px;
    padding: 1rem;
  }

  .sparklet-preview {
    max-width: 250px;
  }

  .preview-wrapper h2 {
    font-size: 1.2rem;
  }

  .action-buttons {
    grid-template-columns: 1fr;
  }

  .link-container {
    flex-direction: column;
  }

  .share-link-input {
    font-size: 0.85rem;
  }

  .share-actions {
    padding: 1rem;
  }
}
</style>
