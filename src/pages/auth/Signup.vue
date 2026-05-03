<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { User, Mail, Lock, Eye, EyeOff } from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPw = ref('')
const agreed = ref(false)
const error = ref('')
const loading = ref(false)
const showPass = ref(false)
const showConfirm = ref(false)
const emailSent = ref(false)

const passwordStrength = computed(() => {
  const pw = password.value
  if (!pw) return 0
  let score = 0
  if (pw.length >= 8) score++
  if (pw.length >= 12) score++
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++
  if (/[0-9]/.test(pw)) score++
  if (/[^A-Za-z0-9]/.test(pw)) score++
  return Math.min(4, score)
})

const strengthLabel = computed(() => {
  const labels = ['', 'Weak', 'Fair', 'Good', 'Strong']
  return labels[passwordStrength.value]
})

const strengthColor = computed(() => {
  const colors = ['', '#ef4444', '#f59e0b', '#10b981', '#059669']
  return colors[passwordStrength.value]
})

async function handleSignup() {
  error.value = ''
  if (!name.value.trim()) { error.value = 'Please enter your full name'; return }
  if (password.value !== confirmPw.value) { error.value = 'Passwords do not match'; return }
  if (!agreed.value) { error.value = 'Please agree to the Terms of Service'; return }
  loading.value = true
  const { data, error: err } = await auth.signUp(email.value, password.value, {
    full_name: name.value,
    display_name: name.value
  })
  loading.value = false
  if (err) {
    error.value = err.message || 'Sign up failed'
  } else if (data?.session) {
    // Email confirmation disabled — user is immediately signed in
    router.push('/onboarding')
  } else {
    // Email confirmation required — session is null until they click the link
    emailSent.value = true
  }
}

async function handleGoogle() {
  error.value = 'Google sign-in coming soon.'
}
</script>

<template>
  <div class="signup-wrap">
    <!-- Email confirmation sent state -->
    <template v-if="emailSent">
      <div class="page-head">
        <div class="confirm-icon">✉️</div>
        <h1 class="title">Check your email</h1>
        <p class="subtitle">We sent a confirmation link to <strong>{{ email }}</strong>. Click it to activate your account, then sign in.</p>
      </div>
      <router-link to="/login" class="btn btn-primary btn-lg" style="justify-content:center;text-align:center;display:flex">
        Go to sign in
      </router-link>
      <p class="footer-text">Didn't receive it? Check your spam folder or <button class="resend-btn" @click="emailSent = false">try again</button>.</p>
    </template>

    <template v-else>
    <div class="page-head">
      <h1 class="title">Create your account</h1>
      <p class="subtitle">Start understanding your mind today</p>
    </div>

    <transition name="err-fade">
      <div v-if="error" class="error-box" role="alert">
        <span class="err-icon">⚠</span> {{ error }}
      </div>
    </transition>

    <form class="form" @submit.prevent="handleSignup" novalidate>
      <!-- Full Name -->
      <div class="form-group">
        <label class="form-label" for="name">Full Name</label>
        <div class="input-wrap">
          <span class="input-icon"><User :size="15" /></span>
          <input
            id="name"
            v-model="name"
            class="input padded-icon"
            type="text"
            placeholder="Jane Smith"
            autocomplete="name"
            required
          />
        </div>
      </div>

      <!-- Email -->
      <div class="form-group">
        <label class="form-label" for="email">Email</label>
        <div class="input-wrap">
          <span class="input-icon"><Mail :size="15" /></span>
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

      <!-- Password + strength -->
      <div class="form-group">
        <label class="form-label" for="password">Password</label>
        <div class="input-wrap">
          <span class="input-icon"><Lock :size="15" /></span>
          <input
            id="password"
            v-model="password"
            class="input padded-icon padded-right"
            :type="showPass ? 'text' : 'password'"
            placeholder="Min. 8 characters"
            autocomplete="new-password"
            required
          />
          <button type="button" class="eye-btn" @click="showPass = !showPass">
            <EyeOff v-if="showPass" :size="16" /><Eye v-else :size="16" />
          </button>
        </div>
        <!-- Strength indicator -->
        <div v-if="password" class="strength-wrap">
          <div class="strength-bar">
            <div
              v-for="i in 4"
              :key="i"
              class="strength-seg"
              :class="{ filled: i <= passwordStrength }"
              :style="i <= passwordStrength ? { background: strengthColor } : {}"
            />
          </div>
          <span class="strength-label" :style="{ color: strengthColor }">{{ strengthLabel }}</span>
        </div>
        <p class="form-hint">Use 8+ characters with uppercase, numbers, and symbols.</p>
      </div>

      <!-- Confirm Password -->
      <div class="form-group">
        <label class="form-label" for="confirm">Confirm Password</label>
        <div class="input-wrap">
          <span class="input-icon"><Lock :size="15" /></span>
          <input
            id="confirm"
            v-model="confirmPw"
            class="input padded-icon padded-right"
            :class="{ error: confirmPw && confirmPw !== password }"
            :type="showConfirm ? 'text' : 'password'"
            placeholder="Re-enter your password"
            autocomplete="new-password"
            required
          />
          <button type="button" class="eye-btn" @click="showConfirm = !showConfirm">
            <EyeOff v-if="showConfirm" :size="16" /><Eye v-else :size="16" />
          </button>
        </div>
        <p v-if="confirmPw && confirmPw !== password" class="form-error">Passwords do not match</p>
      </div>

      <!-- Terms checkbox -->
      <label class="terms-row">
        <span class="custom-checkbox" :class="{ checked: agreed }" @click="agreed = !agreed" tabindex="0" role="checkbox" :aria-checked="agreed" @keydown.space.prevent="agreed = !agreed">
          <span v-if="agreed" class="check-mark">✓</span>
        </span>
        <span class="terms-text">
          I agree to the
          <a href="#" class="terms-link">Terms of Service</a>
          and
          <a href="#" class="terms-link">Privacy Policy</a>
        </span>
      </label>

      <button
        type="submit"
        class="btn btn-primary btn-lg submit-btn"
        :disabled="loading"
      >
        <span v-if="loading" class="spinner" aria-hidden="true" />
        {{ loading ? 'Creating account…' : 'Create account' }}
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
      Already have an account?
      <router-link to="/login" class="footer-link">Sign in</router-link>
    </p>
    </template><!-- end v-else -->
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

.signup-wrap {
  font-family: 'Urbanist', sans-serif;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.page-head { text-align: center; }
.title { font-size: 28px; font-weight: 700; color: var(--plum); line-height: 1.2; margin-bottom: 6px; }
.subtitle { font-size: 14px; color: var(--slate); }

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
.err-icon { font-style: normal; }
.err-fade-enter-active, .err-fade-leave-active { transition: opacity 0.2s, transform 0.2s; }
.err-fade-enter-from, .err-fade-leave-to { opacity: 0; transform: translateY(-4px); }

.form { display: flex; flex-direction: column; gap: 14px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 13px; font-weight: 600; color: var(--plum); }
.form-hint { font-size: 12px; color: var(--slate); }
.form-error { font-size: 12px; color: #dc2626; }

.input-wrap { position: relative; display: flex; align-items: center; }
.input-icon {
  position: absolute;
  left: 12px;
  pointer-events: none;
  z-index: 1;
  color: var(--slate);
  display: flex;
  align-items: center;
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
  color: var(--slate);
  display: flex;
  align-items: center;
  transition: color 0.15s;
}
.eye-btn:hover { color: var(--plum); }

/* Password strength */
.strength-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
}
.strength-bar {
  display: flex;
  gap: 4px;
  flex: 1;
}
.strength-seg {
  flex: 1;
  height: 4px;
  border-radius: 99px;
  background: var(--lavender-soft);
  transition: background 0.25s;
}
.strength-label {
  font-size: 11px;
  font-weight: 700;
  min-width: 40px;
  text-align: right;
  transition: color 0.25s;
}

/* Terms */
.terms-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
}
.custom-checkbox {
  width: 18px;
  height: 18px;
  border: 2px solid var(--lavender-mid);
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.15s;
  background: white;
  margin-top: 1px;
  cursor: pointer;
}
.custom-checkbox.checked {
  background: var(--lavender-deep);
  border-color: var(--lavender-deep);
}
.check-mark {
  color: white;
  font-size: 11px;
  font-weight: 700;
  line-height: 1;
}
.terms-text {
  font-size: 13px;
  color: var(--slate);
  line-height: 1.5;
  user-select: none;
}
.terms-link {
  color: var(--lavender-deep);
  font-weight: 600;
  text-decoration: none;
}
.terms-link:hover { text-decoration: underline; }

.submit-btn {
  width: 100%;
  justify-content: center;
  margin-top: 4px;
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

.divider {
  display: flex;
  align-items: center;
  gap: 10px;
}
.divider-line { flex: 1; height: 1px; background: var(--lavender); }
.divider-text { font-size: 12px; color: var(--slate); font-weight: 500; white-space: nowrap; }

.google-btn { width: 100%; justify-content: center; gap: 10px; }

.footer-text { text-align: center; font-size: 13px; color: var(--slate); }
.footer-link { font-weight: 700; color: var(--lavender-deep); text-decoration: none; }
.footer-link:hover { color: var(--plum); }

.confirm-icon { font-size: 40px; text-align: center; margin-bottom: 8px; }
.resend-btn {
  background: none; border: none; cursor: pointer;
  color: var(--lavender-deep); font-weight: 600; font-size: 13px;
  font-family: 'Urbanist', sans-serif; padding: 0;
}
.resend-btn:hover { color: var(--plum); text-decoration: underline; }
</style>
