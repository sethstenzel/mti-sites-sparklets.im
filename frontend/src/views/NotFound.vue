<template>
  <div class="nf">
    <h1>There’s nothing at this address.</h1>
    <p>If someone sent you a sparklet, check that the whole link came through.</p>
    <div class="actions">
      <router-link to="/" class="btn btn-ghost">Go home</router-link>
      <router-link to="/create" class="btn btn-primary">Create a sparklet</router-link>
    </div>
  </div>
</template>

<style scoped>
.nf {
  display: grid;
  justify-items: center;
  align-content: center;
  gap: 1rem;
  min-height: 60dvh;
  padding: 2rem 1.25rem;
  text-align: center;
}

h1 {
  max-width: 16em;
  font-size: clamp(1.8rem, 4vw, 2.6rem);
  font-weight: 800;
  letter-spacing: -0.035em;
  line-height: 1.08;
}

p {
  max-width: 32em;
  color: var(--ink-2);
}

.actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
</style>
