<template>
  <div id="app">
    <header>
      <h1>Sparklets.IM</h1>
      <nav>
        <router-link to="/">Home</router-link>
        <router-link to="/create">Create</router-link>
        <router-link to="/sparklet/1">Demo</router-link>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style scoped>
header {
  background: linear-gradient(135deg, #5568d3 0%, #633a8a 100%);
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

h1 {
  margin: 0;
  font-size: 2rem;
}

nav {
  margin-top: 1rem;
}

nav a {
  color: white;
  text-decoration: none;
  margin-right: 1rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}

nav a:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

nav a.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
}

main {
  padding: 0;
}
</style>
