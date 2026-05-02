<template>
  <div class="not-found">
    <h1>Page not found</h1>
    <p>The page you were looking for has moved or no longer exists.</p>
    <div class="actions">
      <RouterLink to="/" class="btn btn-primary">Back to home</RouterLink>
      <RouterLink to="/dashboard" class="btn btn-outline">Open dashboard</RouterLink>
    </div>
  </div>
</template>

<script setup>
// Nuxt automatically maps this page to /not-found for manual navigation.
</script>

<style scoped>
.not-found {
  min-height: 80vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  gap: var(--spacing-4);
}

.actions {
  display: flex;
  gap: var(--spacing-3);
}
</style>
