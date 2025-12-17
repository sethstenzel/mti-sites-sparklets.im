<template>
  <div class="view-container" :style="{ backgroundColor: sparklet?.background_color || '#f0f0f0' }">
    <div v-if="loading" class="loading">Loading sparklet...</div>
    <div v-else-if="error" class="error-message">
      <div class="error-emoji">😅</div>
      <h2>Oops! Not Found</h2>
      <p>{{ error }}</p>
      <router-link to="/create" class="create-link">Create Your Own Sparklet</router-link>
    </div>
    <div v-else-if="sparklet" class="sparklet-card" :style="{
      backgroundColor: sparklet.card_color,
      transform: `rotate(${sparklet.card_rotation || 5}deg)`
    }">
      <div class="image-section">
        <img
          :src="imageUrl"
          :alt="`Sparklet from ${sparklet.from_name}`"
          :style="{
            transform: `translate(${sparklet.image_offset_x || 0}px, ${sparklet.image_offset_y || 0}px) scale(${sparklet.image_scale || 1})`
          }"
        />
      </div>
      <div class="message-section" :style="{ color: sparklet.text_color }">
        <p class="message">{{ sparklet.message }}</p>
        <div class="metadata">
          <span class="to">To: {{ sparklet.to_name }}</span>
          <span class="from">From: {{ sparklet.from_name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const sparklet = ref(null)
const loading = ref(true)
const error = ref(null)

const imageUrl = computed(() => {
  if (!sparklet.value) return ''
  // In production, use relative URL; in dev, use localhost
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
  return `${API_BASE_URL}/contents/imgs/${sparklet.value.image_filename}`
})

onMounted(async () => {
  const sparkletId = route.params.id
  try {
    const response = await axios.get(`/api/sparklets/${sparkletId}`)
    sparklet.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load sparklet'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.view-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  transition: background-color 0.3s ease;
}

.loading {
  text-align: center;
  font-size: 1.2rem;
  color: #333;
}

.error-message {
  text-align: center;
  background: white;
  padding: 3rem 2rem;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  margin: 2rem;
}

.error-emoji {
  font-size: 5rem;
  margin-bottom: 1rem;
  animation: bounce 1s ease-in-out;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.error-message h2 {
  color: #333;
  font-size: 2rem;
  margin: 0 0 1rem 0;
}

.error-message p {
  color: #666;
  font-size: 1.1rem;
  margin: 0 0 2rem 0;
}

.create-link {
  display: inline-block;
  background: linear-gradient(135deg, #5568d3 0%, #633a8a 100%);
  color: white;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(85, 104, 211, 0.3);
}

.create-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(85, 104, 211, 0.4);
}

.sparklet-card {
  width: 90vw;
  max-width: 400px;
  aspect-ratio: 1;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transform: rotate(10deg);
  transition: all 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sparklet-card:hover {
  transform: rotate(10deg) translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
}

.image-section {
  flex: 2;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
}

.image-section img {
  width: 100%;
  object-fit: cover;
  transform-origin: center center;
}

.message-section {
  flex: 1;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-family: 'Kalam', cursive;
}

.message {
  font-size: 0.9rem;
  line-height: 1.4;
  margin: 0 0 0.5rem 0;
  overflow-wrap: break-word;
  text-align: center;
}

.metadata {
  font-size: 0.75rem;
  opacity: 0.8;
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.from {
  font-weight: 600;
}

.to {
  font-weight: 600;
}

@media (min-width: 768px) {
  .sparklet-card {
    max-width: 450px;
  }

  .message {
    font-size: 1rem;
  }

  .metadata {
    font-size: 0.85rem;
  }
}

@media (min-width: 1024px) {
  .sparklet-card {
    max-width: 500px;
  }
}
</style>
