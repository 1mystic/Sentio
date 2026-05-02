<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-card">
        <h1>Create Account</h1>
        <p class="auth-subtitle">Start your mental wellness journey</p>

        <form @submit.prevent="handleSignup" class="auth-form">
          <div class="form-group">
            <label class="form-label">Full Name</label>
            <input
              v-model="fullName"
              type="text"
              class="form-input"
              :class="{ error: errors.fullName }"
              placeholder="John Doe"
              required
            />
            <span v-if="errors.fullName" class="form-error">{{ errors.fullName }}</span>
          </div>

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
              minlength="8"
            />
            <span v-if="errors.password" class="form-error">{{ errors.password }}</span>
            <small class="form-hint">At least 8 characters</small>
          </div>

          <div class="form-group">
            <label class="form-label">Confirm Password</label>
            <input
              v-model="confirmPassword"
              type="password"
              class="form-input"
              :class="{ error: errors.confirmPassword }"
              placeholder="••••••••"
              required
            />
            <span v-if="errors.confirmPassword" class="form-error">{{ errors.confirmPassword }}</span>
          </div>

          <div class="form-group">
            <label class="form-checkbox">
              <input type="checkbox" v-model="acceptTerms" required />
              <span>I agree to the <RouterLink to="/terms" target="_blank">Terms of Service</RouterLink> and <RouterLink to="/privacy" target="_blank">Privacy Policy</RouterLink></span>
            </label>
          </div>

          <button 
            type="submit" 
            class="btn btn-primary btn-lg"
            :disabled="loading || !acceptTerms"
          >
            <span v-if="loading" class="loading"></span>
            <span v-else>Create Account</span>
          </button>
        </form>

        <div class="auth-links">
          <p>Already have an account? <RouterLink to="/login">Sign in</RouterLink></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useToast } from '../composables/useToast'
import { useRouter } from 'vue-router'
import { isValidEmail } from '../utils/utils'

const { signUp } = useAuth()
const { success, error: showError } = useToast()
const router = useRouter()

const fullName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const acceptTerms = ref(false)
const loading = ref(false)
const errors = ref({})

const handleSignup = async () => {
  errors.value = {}

  // Validation
  if (!fullName.value.trim()) {
    errors.value.fullName = 'Full name is required'
  }

  if (!isValidEmail(email.value)) {
    errors.value.email = 'Please enter a valid email'
  }

  if (password.value.length < 8) {
    errors.value.password = 'Password must be at least 8 characters'
  }

  if (password.value !== confirmPassword.value) {
    errors.value.confirmPassword = 'Passwords do not match'
  }

  if (Object.keys(errors.value).length > 0) {
    return
  }

  loading.value = true

  try {
    const { data, error } = await signUp(email.value, password.value, fullName.value)

    if (error) {
      errors.value.general = error.message
      showError(error.message)
      return
    }

    success('Account created successfully!')
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

.form-hint {
  display: block;
  font-size: var(--text-xs);
  color: var(--mind-gray);
  margin-top: var(--spacing-1);
}

.form-checkbox {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-2);
  cursor: pointer;
  font-size: var(--text-sm);
}

.form-checkbox input[type="checkbox"] {
  width: auto;
  margin-top: 2px;
  cursor: pointer;
}

.form-checkbox a {
  color: var(--mind-purple);
  text-decoration: underline;
}

.auth-links {
  text-align: center;
  font-size: var(--text-sm);
}

.auth-links a {
  color: var(--mind-purple);
}

.auth-links p {
  color: var(--mind-gray);
}
</style>

