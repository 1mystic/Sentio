<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-card">
        <h1>Sign In</h1>
        <p class="auth-subtitle">Welcome back to VeraMind</p>

        <form @submit.prevent="handleLogin" class="auth-form">
          <div class="form-group">
            <label class="form-label">Email</label>
            <input
              v-model="email"
              type="email"
              class="form-input"
              :class="{ error: errors.email }"
              placeholder="your@email.com"
              required
            />
            <span v-if="errors.email" class="form-error">{{ errors.email }}</span>
          </div>

          <div class="form-group">
            <label class="form-label">Password</label>
            <input
              v-model="password"
              type="password"
              class="form-input"
              :class="{ error: errors.password }"
              placeholder="••••••••"
              required
            />
            <span v-if="errors.password" class="form-error">{{ errors.password }}</span>
          </div>

          <div class="form-group">
            <label class="form-checkbox">
              <input type="checkbox" v-model="rememberMe" />
              <span>Remember me</span>
            </label>
          </div>

          <button 
            type="submit" 
            class="btn btn-primary btn-lg"
            :disabled="loading"
          >
            <span v-if="loading" class="loading"></span>
            <span v-else>Sign In</span>
          </button>
        </form>

        <div class="auth-links">
          <RouterLink to="/reset-password">Forgot password?</RouterLink>
          <p>Don't have an account? <RouterLink to="/signup">Sign up</RouterLink></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useToast } from '../composables/useToast'
import { useRouter } from 'vue-router'

const { signIn } = useAuth()
const { success, error: showError } = useToast()
const router = useRouter()

const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const loading = ref(false)
const errors = ref({})

const handleLogin = async () => {
  errors.value = {}
  loading.value = true

  try {
    const { data, error } = await signIn(email.value, password.value)

    if (error) {
      errors.value.general = error.message
      showError(error.message)
      return
    }

    success('Welcome back!')
    await router.push('/dashboard')
  } catch (err) {
    showError('An unexpected error occurred')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--mind-purple-light) 0%, var(--mind-blue-light) 100%);
  padding: var(--spacing-6);
}

.auth-container {
  width: 100%;
  max-width: 400px;
}

.auth-card {
  background-color: white;
  padding: var(--spacing-8);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
}

.auth-card h1 {
  text-align: center;
  margin-bottom: var(--spacing-2);
}

.auth-subtitle {
  text-align: center;
  color: var(--mind-gray);
  margin-bottom: var(--spacing-8);
}

.auth-form {
  margin-bottom: var(--spacing-6);
}

.form-checkbox {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  cursor: pointer;
}

.form-checkbox input[type="checkbox"] {
  width: auto;
  cursor: pointer;
}

.auth-links {
  text-align: center;
  font-size: var(--text-sm);
}

.auth-links a {
  color: var(--mind-purple);
}

.auth-links p {
  margin-top: var(--spacing-4);
  color: var(--mind-gray);
}
</style>

