<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { AlertTriangle, Mail, Lock, Eye, EyeOff } from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const showPass = ref(false)

async function handleLogin() {
  if (!email.value || !password.value) {
    error.value = 'Please enter your email and password.'
    return
  }
  loading.value = true
  error.value = ''
  const { error: err } = await auth.signIn(email.value, password.value)
  loading.value = false
  if (err) {
    error.value = err.message || 'Sign in failed. Check your credentials.'
  } else {
    router.push('/dashboard')
  }
}

async function handleGoogle() {
  // Google OAuth — requires client ID configured in Supabase dashboard
  // Will be enabled after Vercel deployment with OAuth callback URL
  error.value = 'Google sign-in will be available after deployment. Use email sign in for now.'
}
</script>

<template>
  <div class="login-wrap">
    <div class="page-head">
      <h1 class="title">Welcome back</h1>
      <p class="subtitle">Sign in to continue your journey</p>
    </div>

    <transition name="err-fade">
      <div v-if="error" class="error-box" role="alert">
        <AlertTriangle :size="15" class="err-icon" /> {{ error }}
      </div>
    </transition>

    <form class="form" @submit.prevent="handleLogin" novalidate>
      <div class="form-group">
        <label class="form-label" for="email">Email</label>
        <div class="input-wrap">
          <Mail :size="15" class="input-icon" />
          <input
            id="email"
            v-model="email"
            class="input padded-icon"
            type="email"
            placeholder="you@example.com"
            autocomplete="email"
            required
          />
        </div>
      </div>

      <div class="form-group">
        <div class="label-row">
          <label class="form-label" for="password">Password</label>
          <router-link to="/forgot-password" class="forgot-link">Forgot password?</router-link>
        </div>
        <div class="input-wrap">
          <Lock :size="15" class="input-icon" />
          <input
            id="password"
            v-model="password"
            class="input padded-icon padded-right"
            :type="showPass ? 'text' : 'password'"
            placeholder="••••••••"
            autocomplete="current-password"
            required
          />
          <button
            type="button"
            class="eye-btn"
            :title="showPass ? 'Hide password' : 'Show password'"
            @click="showPass = !showPass"
          >
            <EyeOff v-if="showPass" :size="15" />
            <Eye v-else :size="15" />
          </button>
        </div>
      </div>

      <button
        type="submit"
        class="btn btn-primary btn-lg submit-btn"
        :disabled="loading"
      >
        <span v-if="loading" class="spinner" aria-hidden="true" />
        {{ loading ? 'Signing in…' : 'Sign in' }}
      </button>
    </form>

    <div class="divider">
      <span class="divider-line" />
      <span class="divider-text">or continue with</span>
      <span class="divider-line" />
    </div>

    <button type="button" class="btn btn-ghost btn-lg google-btn" @click="handleGoogle">
      <svg width="18" height="18" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M47.532 24.552c0-1.636-.132-3.196-.388-4.692H24.48v9.076h13.012c-.572 2.988-2.244 5.524-4.764 7.216v5.968h7.7c4.508-4.148 7.104-10.26 7.104-17.568z" fill="#4285F4"/>
        <path d="M24.48 48c6.504 0 11.964-2.152 15.948-5.84l-7.7-5.968c-2.152 1.444-4.908 2.3-8.248 2.3-6.34 0-11.708-4.284-13.628-10.036H2.892v6.164C6.86 42.776 15.1 48 24.48 48z" fill="#34A853"/>
        <path d="M10.852 28.456A14.478 14.478 0 0 1 9.96 24c0-1.556.268-3.068.892-4.456v-6.164H2.892A23.97 23.97 0 0 0 .48 24c0 3.876.932 7.548 2.412 10.62l7.96-6.164z" fill="#FBBC05"/>
        <path d="M24.48 9.508c3.572 0 6.772 1.228 9.292 3.628l6.924-6.924C36.44 2.368 30.984 0 24.48 0 15.1 0 6.86 5.224 2.892 13.38l7.96 6.164c1.92-5.752 7.288-10.036 13.628-10.036z" fill="#EA4335"/>
      </svg>
      Continue with Google
    </button>

    <p class="footer-text">
      Don't have an account?
      <router-link to="/signup" class="footer-link">Sign up</router-link>
    </p>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

.login-wrap {
  font-family: 'Urbanist', sans-serif;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Header */
.page-head { text-align: center; }
.title { font-size: 28px; font-weight: 700; color: var(--plum); line-height: 1.2; margin-bottom: 6px; }
.subtitle { font-size: 14px; color: var(--slate); }

/* Error box */
.error-box {
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  padding: 10px 14px;
  color: #dc2626;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.err-icon { font-style: normal; font-size: 14px; }
.err-fade-enter-active, .err-fade-leave-active { transition: opacity 0.2s, transform 0.2s; }
.err-fade-enter-from, .err-fade-leave-to { opacity: 0; transform: translateY(-4px); }

/* Form */
.form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 13px; font-weight: 600; color: var(--plum); }
.label-row { display: flex; align-items: center; justify-content: space-between; }
.forgot-link {
  font-size: 12px;
  font-weight: 600;
  color: var(--lavender-deep);
  text-decoration: none;
  transition: color 0.15s;
}
.forgot-link:hover { color: var(--plum); }

/* Input wrapper */
.input-wrap { position: relative; display: flex; align-items: center; }
.input-icon {
  position: absolute;
  left: 12px;
  font-size: 15px;
  pointer-events: none;
  z-index: 1;
  line-height: 1;
  color: var(--slate);
}
.input {
  font-family: 'Urbanist', sans-serif;
  font-size: 14px;
  color: var(--plum);
  background: white;
  border: 1.5px solid var(--lavender);
  border-radius: 10px;
  padding: 10px 14px;
  outline: none;
  transition: all 0.15s;
  width: 100%;
}
.input.padded-icon { padding-left: 38px; }
.input.padded-right { padding-right: 42px; }
.input:focus { border-color: var(--lavender-deep); box-shadow: 0 0 0 3px rgba(155,148,232,0.15); }
.input::placeholder { color: var(--slate); opacity: 0.7; }
.input.error { border-color: #dc2626; }

.eye-btn {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  font-size: 16px;
  line-height: 1;
  color: var(--slate);
  display: flex;
  align-items: center;
  transition: color 0.15s;
}
.eye-btn:hover { color: var(--plum); }

/* Submit */
.submit-btn {
  width: 100%;
  justify-content: center;
  margin-top: 4px;
  position: relative;
}
.submit-btn:disabled { opacity: 0.7; cursor: not-allowed; transform: none !important; }

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Divider */
.divider {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}
.divider-line {
  flex: 1;
  height: 1px;
  background: var(--lavender);
}
.divider-text {
  font-size: 12px;
  color: var(--slate);
  font-weight: 500;
  white-space: nowrap;
}

/* Google button */
.google-btn {
  width: 100%;
  justify-content: center;
  gap: 10px;
}

/* Footer */
.footer-text {
  text-align: center;
  font-size: 13px;
  color: var(--slate);
  margin-top: 4px;
}
.footer-link {
  font-weight: 700;
  color: var(--lavender-deep);
  text-decoration: none;
  transition: color 0.15s;
}
.footer-link:hover { color: var(--plum); }
</style>
