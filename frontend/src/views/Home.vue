<template>
  <div class="home">
    <div class="hero">
      <h2>Send Sparks of Joy with Sparklets</h2>
      <p class="tagline">Create beautiful QR code / Weblink message cards for the people you care about!</p>

      <div class="cta-buttons">
        <router-link to="/create" class="btn btn-primary">Create a Sparklet</router-link>
        <router-link to="/sparklet/1" class="btn btn-secondary">View Demo</router-link>
      </div>
    </div>

    <div class="features">
      <div class="feature">
        <div class="feature-icon">🎨</div>
        <h3>Customize Colors</h3>
        <p>Choose your own background, card, and text colors</p>
      </div>
      <div class="feature">
        <div class="feature-icon">📸</div>
        <h3>Add Images</h3>
        <p>Upload a photo to make your Sparklet personal</p>
      </div>
      <div class="feature">
        <div class="feature-icon">💌</div>
        <h3>Share Messages</h3>
        <p>Write up to 100 characters of heartfelt text</p>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.hero {
  text-align: center;
  padding: 4rem 2rem;
  color: white;
}

h2 {
  font-size: 3rem;
  margin: 0 0 1rem 0;
  font-weight: 700;
}

.tagline {
  font-size: 1.3rem;
  margin: 0 0 2rem 0;
  opacity: 0.95;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 1rem 2rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  display: inline-block;
}

.btn-primary {
  background: white;
  color: #667eea;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  padding: 3rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.feature {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.feature:hover {
  transform: translateY(-8px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature h3 {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-size: 1.3rem;
}

.feature p {
  color: #666;
  margin: 0;
  line-height: 1.5;
}

@media (max-width: 640px) {
  h2 {
    font-size: 2rem;
  }

  .tagline {
    font-size: 1.1rem;
  }

  .hero {
    padding: 3rem 1rem;
  }

  .features {
    padding: 2rem 1rem;
  }
}
</style>
