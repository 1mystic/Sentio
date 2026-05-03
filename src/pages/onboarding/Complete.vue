<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { CheckCircle, PartyPopper, ArrowRight } from 'lucide-vue-next'
import { usersApi } from '@/api/users.js'

const router = useRouter()

const interestMap = {
  decision: '🧠 Decision Making',
  communication: '💬 Communication',
  career: '💼 Work & Career',
  relationships: '❤️ Relationships',
  finance: '💰 Money & Finance',
  learning: '🎓 Learning',
  health: '🏋️ Health',
  social: '🌍 Social Justice',
  science: '🔬 Science',
  politics: '🗳️ Politics',
  creativity: '🎨 Creativity',
  leadership: '📈 Leadership'
}

const selectedInterests = ref([])
const saving = ref(false)

onMounted(() => {
  try {
    const raw = sessionStorage.getItem('sentio_interests')
    if (raw) {
      const ids = JSON.parse(raw)
      selectedInterests.value = ids.map(id => interestMap[id]).filter(Boolean)
    }
  } catch (e) { /* ignore */ }
})

async function enterSentio() {
  saving.value = true
  try {
    const interestIds = JSON.parse(sessionStorage.getItem('sentio_interests') || '[]')
    const baselineRaw = sessionStorage.getItem('sentio_baseline')
    const baselineAnswers = baselineRaw ? JSON.parse(baselineRaw) : []

    await usersApi.updateMe({
      onboarding_completed: true,
      cognitive_style: { baseline_answers: baselineAnswers },
      preferences: {
        interests: interestIds,
        notifications: { daily: true, weekly: true, assessments: false },
      },
    })
  } catch (e) {
    console.warn('Onboarding save failed (non-blocking):', e.message)
  } finally {
    sessionStorage.removeItem('sentio_interests')
    sessionStorage.removeItem('sentio_baseline')
    router.push('/dashboard')
  }
}
</script>

<template>
  <div class="complete-wrap fade-up">
    <!-- Confetti decoration -->
    <div class="confetti-container" aria-hidden="true">
      <span v-for="i in 16" :key="i" class="confetti-dot" :class="`dot-${i}`" />
    </div>

    <!-- Checkmark -->
    <div class="check-circle">
      <CheckCircle :size="40" class="check-icon" />
    </div>

    <!-- Text -->
    <div class="text-center">
      <h1 class="title">You're all set! <PartyPopper :size="28" class="title-icon" /></h1>
      <p class="subtitle">
        Your Sentio profile is ready. We've identified a personalized starting path
        for you based on your responses.
      </p>
    </div>

    <!-- Summary card -->
    <div class="summary-card card card-lavender">
      <div class="summary-row">
        <span class="summary-label">Your starting bias to explore</span>
        <span class="badge badge-lavender summary-val">Confirmation Bias</span>
      </div>
      <div class="divider-rule" />
      <div class="summary-row">
        <span class="summary-label">Recommended first assessment</span>
        <span class="summary-val-text">Cognitive Patterns Quiz</span>
      </div>
      <div v-if="selectedInterests.length" class="divider-rule" />
      <div v-if="selectedInterests.length" class="summary-row interests-row">
        <span class="summary-label">Your interest focus</span>
        <div class="interest-tags">
          <span
            v-for="interest in selectedInterests"
            :key="interest"
            class="interest-tag"
          >{{ interest }}</span>
        </div>
      </div>
    </div>

    <!-- CTA -->
    <button class="btn btn-primary btn-xl enter-btn" :disabled="saving" @click="enterSentio">
      <span v-if="saving" class="btn-spinner" />
      <template v-else>Enter Sentio <ArrowRight :size="18" /></template>
    </button>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

.complete-wrap {
  font-family: 'Urbanist', sans-serif;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 28px;
  text-align: center;
  padding: 16px 0 40px;
  position: relative;
}

/* Confetti */
.confetti-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200px;
  pointer-events: none;
  overflow: hidden;
}
.confetti-dot {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  opacity: 0;
  animation: confettiFly 3s ease-out forwards;
}

/* Place dots at varied x positions */
.dot-1  { left: 5%;  background: var(--lavender-deep); animation-delay: 0.1s; width: 6px; height: 6px; }
.dot-2  { left: 12%; background: #f9c4e1; animation-delay: 0.25s; border-radius: 2px; }
.dot-3  { left: 20%; background: var(--lavender-mid); animation-delay: 0.05s; width: 10px; height: 10px; }
.dot-4  { left: 28%; background: #fcd38a; animation-delay: 0.4s; border-radius: 3px; }
.dot-5  { left: 35%; background: var(--lavender-deep); animation-delay: 0.2s; }
.dot-6  { left: 42%; background: #c4e4f9; animation-delay: 0.35s; width: 7px; height: 7px; }
.dot-7  { left: 50%; background: #f9c4c4; animation-delay: 0.15s; border-radius: 2px; }
.dot-8  { left: 58%; background: var(--lavender); animation-delay: 0.5s; width: 9px; height: 9px; }
.dot-9  { left: 65%; background: #fcd38a; animation-delay: 0.08s; }
.dot-10 { left: 72%; background: var(--lavender-deep); animation-delay: 0.3s; width: 6px; height: 6px; border-radius: 2px; }
.dot-11 { left: 78%; background: #c4f9da; animation-delay: 0.45s; }
.dot-12 { left: 84%; background: var(--lavender-mid); animation-delay: 0.18s; width: 10px; height: 10px; }
.dot-13 { left: 90%; background: #f9c4e1; animation-delay: 0.6s; border-radius: 3px; }
.dot-14 { left: 96%; background: var(--lavender-deep); animation-delay: 0.28s; }
.dot-15 { left: 46%; background: #fcd38a; animation-delay: 0.55s; width: 7px; height: 7px; border-radius: 2px; }
.dot-16 { left: 22%; background: var(--lavender); animation-delay: 0.38s; width: 9px; height: 9px; }

@keyframes confettiFly {
  0%   { opacity: 0; transform: translateY(0) rotate(0deg); }
  15%  { opacity: 1; }
  100% { opacity: 0; transform: translateY(-160px) rotate(540deg); }
}

/* Checkmark */
.check-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #34d399, #059669);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 28px rgba(5,150,105,0.28);
  animation: checkPop 0.55s cubic-bezier(0.34, 1.56, 0.64, 1) both;
  margin-top: 40px;
}
.check-icon {
  color: white;
}
@keyframes checkPop {
  0%   { opacity: 0; transform: scale(0); }
  100% { opacity: 1; transform: scale(1); }
}

/* Text */
.text-center { max-width: 480px; }
.title { font-size: 32px; font-weight: 800; color: var(--plum); margin-bottom: 10px; line-height: 1.2; display: flex; align-items: center; justify-content: center; gap: 8px; }
.title-icon { color: var(--lavender-deep); flex-shrink: 0; }
.subtitle { font-size: 16px; color: var(--slate); line-height: 1.65; }

/* Summary card */
.summary-card {
  width: 100%;
  max-width: 480px;
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 20px 22px;
  text-align: left;
  border: 1px solid rgba(218,216,249,0.6);
}
.summary-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  flex-wrap: wrap;
}
.interests-row { flex-direction: column; gap: 8px; }
.summary-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--slate);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}
.summary-val { font-size: 12px; }
.summary-val-text {
  font-size: 13px;
  font-weight: 700;
  color: var(--plum);
}
.divider-rule {
  height: 1px;
  background: rgba(218,216,249,0.6);
  margin: 0 -2px;
}

/* Interest tags */
.interest-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.interest-tag {
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 99px;
  background: white;
  color: var(--plum);
  border: 1.5px solid var(--lavender);
}

/* CTA */
.enter-btn {
  padding: 16px 44px;
  font-size: 18px;
  border-radius: 14px;
  font-weight: 700;
  letter-spacing: -0.2px;
  margin-top: 4px;
}
.enter-btn:disabled { opacity: 0.7; cursor: not-allowed; transform: none !important; }
.btn-spinner {
  display: inline-block; width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.4); border-top-color: white;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
