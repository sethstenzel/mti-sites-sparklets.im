<template>
  <div class="about">
    <h2>About Sparklets.IM</h2>
    <p>
      This is a full-stack application built with Vue 3 and FastAPI.
    </p>
    <ul>
      <li>Frontend: Vue 3 with Vite</li>
      <li>Backend: FastAPI with Python</li>
      <li>State Management: Pinia</li>
      <li>Routing: Vue Router</li>
    </ul>
  </div>
</template>

<script setup>
</script>

<style scoped>
.about {
  max-width: 800px;
  margin: 0 auto;
}

h2 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

p {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #555;
  margin-bottom: 1rem;
}

ul {
  list-style-position: inside;
  font-size: 1.1rem;
  color: #555;
}

li {
  margin-bottom: 0.5rem;
}
</style>
