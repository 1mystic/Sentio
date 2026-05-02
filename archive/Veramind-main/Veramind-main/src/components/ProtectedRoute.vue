<template>
  <div v-if="loading" class="loading-container">
    <div class="loading"></div>
  </div>
  <div v-else-if="!isAuthenticated">
    <div class="auth-redirect">
      <p>Please sign in to access this page.</p>
      <RouterLink to="/login" class="btn btn-primary">Sign In</RouterLink>
    </div>
  </div>
  <slot v-else />
</template>

<script setup>
import { useAuth } from '../composables/useAuth'
import { useRouter } from 'vue-router'
import { watch } from 'vue'

const { user, loading, isAuthenticated } = useAuth()
const router = useRouter()

watch([isAuthenticated, loading], ([authenticated, isLoading]) => {
  if (!isLoading && !authenticated) {
    router.push('/login')
  }
}, { immediate: true })
</script>

<style scoped>
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}

.auth-redirect {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  gap: var(--spacing-4);
  text-align: center;
  padding: var(--spacing-6);
}
</style>

