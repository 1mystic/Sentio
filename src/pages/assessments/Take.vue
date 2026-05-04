<template>
  <div class="take-page">

    <!-- Top Bar: Progress + Exit -->
    <div class="top-bar">
      <div class="progress-section">
        <div class="progress-label-row">
          <span class="badge badge-lavender">Question {{ currentQ + 1 }} of {{ questions.length }}</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: ((currentQ + 1) / questions.length * 100) + '%' }"></div>
        </div>
      </div>
      <router-link to="/assessments" class="btn btn-ghost btn-sm exit-btn">× Exit</router-link>
    </div>

    <!-- Loading -->
    <div v-if="assessStore.loading" class="state-center">
      <div class="spinner"></div>
      <p>Loading assessment…</p>
    </div>

    <!-- Question Card -->
    <div v-else-if="currentQuestion" class="question-wrap">
      <div class="card question-card">

        <div class="q-number">Question {{ currentQ + 1 }}</div>
        <h2 class="q-text">{{ currentQuestion.text }}</h2>
        <p v-if="currentQuestion.context" class="q-context">{{ currentQuestion.context }}</p>

        <div class="options-list">
          <div
            v-for="(label, i) in currentQuestion.optionLabels"
            :key="i"
            class="option-card"
            :class="{ selected: answers[currentQ] === label }"
            @click="selectAnswer(label)"
          >
            <span class="option-letter">{{ String.fromCharCode(65 + i) }}</span>
            <span class="option-text">{{ label }}</span>
          </div>
        </div>

        <!-- Navigation -->
        <div class="nav-bar">
          <button
            class="btn btn-ghost"
            :disabled="currentQ === 0"
            @click="currentQ--"
          >← Previous</button>

          <div class="nav-right">
            <span class="nav-hint" v-if="!answers[currentQ]">Select an answer to continue</span>
            <button
              v-if="currentQ < questions.length - 1"
              class="btn btn-primary"
              :disabled="!answers[currentQ]"
              @click="currentQ++"
            >Next Question →</button>
            <button
              v-else
              class="btn btn-primary"
              :disabled="!answers[currentQ] || submitting"
              @click="finish"
            >{{ submitting ? 'Saving…' : 'Finish Assessment →' }}</button>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssessmentStore } from '@/stores/assessment.js'

const route = useRoute()
const router = useRouter()
const assessStore = useAssessmentStore()

const currentQ = ref(0)
const answers = ref({})
const submitting = ref(false)

onMounted(() => assessStore.fetchOne(route.params.id))

const assessment = computed(() => assessStore.currentAssessment)

// Normalise questions: support both {text, options:[string]} and {text, options:[{text,score,category}]}
const questions = computed(() => {
  const qs = assessment.value?.questions || []
  return qs.map(q => ({
    ...q,
    optionLabels: q.options.map(o => (typeof o === 'string' ? o : o.text)),
  }))
})

const currentQuestion = computed(() => questions.value[currentQ.value])

function selectAnswer(option) {
  answers.value[currentQ.value] = option
  if (currentQ.value < questions.value.length - 1) {
    setTimeout(() => currentQ.value++, 300)
  }
}

function computeScores() {
  const raw = {}
  const categoryTotals = {}
  const categoryCounts = {}

  questions.value.forEach((q, i) => {
    const selectedLabel = answers.value[i]
    const optObj = typeof q.options[0] === 'string'
      ? { score: q.options.indexOf(selectedLabel) + 1 }
      : q.options.find(o => o.text === selectedLabel) || { score: 1 }

    raw[q.id || `q${i}`] = optObj.score
    const cat = q.bias_signal || optObj.category || q.category || 'general'
    categoryTotals[cat] = (categoryTotals[cat] || 0) + optObj.score
    categoryCounts[cat] = (categoryCounts[cat] || 0) + 1
  })

  const computed_scores = {}
  for (const cat of Object.keys(categoryTotals)) {
    computed_scores[cat] = Math.round((categoryTotals[cat] / categoryCounts[cat]) * 10)
  }
  return { raw, computed_scores }
}

async function finish() {
  submitting.value = true
  const { raw, computed_scores } = computeScores()
  const { data, error } = await assessStore.submit(route.params.id, {
    raw_scores: raw,
    computed_scores,
  })
  submitting.value = false

  if (data) {
    router.push({
      path: `/assessments/${route.params.id}/results`,
      state: { result: data, scores: computed_scores },
    })
  } else {
    // Even if submit fails (e.g. no auth), go to results with local scores
    router.push({
      path: `/assessments/${route.params.id}/results`,
      state: { scores: computed_scores },
    })
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.take-page { display: flex; flex-direction: column; gap: 32px; min-height: calc(100vh - 120px); }

/* Buttons */
.btn { display: inline-flex; align-items: center; gap: 6px; font-family: 'Urbanist'; font-weight: 600; border: none; cursor: pointer; transition: all 0.18s; outline: none; text-decoration: none; }
.btn-primary { background: var(--plum); color: white; padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-primary:hover:not(:disabled) { background: #4a3550; transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
.btn-ghost { background: transparent; color: var(--plum); border: 1.5px solid var(--lavender); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-ghost:hover:not(:disabled) { background: var(--lavender-soft); }
.btn-ghost:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-sm { padding: 6px 14px !important; font-size: 13px !important; border-radius: 8px !important; }

/* Badge */
.badge { font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 99px; display: inline-flex; align-items: center; }
.badge-lavender { background: var(--lavender); color: var(--plum); }

/* Card */
.card { background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(53,43,56,0.07); padding: 20px; }

/* Top Bar */
.top-bar { display: flex; align-items: center; gap: 20px; }
.progress-section { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.progress-label-row { display: flex; align-items: center; gap: 10px; }
.progress-track { height: 8px; background: var(--lavender-soft); border-radius: 99px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, var(--lavender-deep), var(--lavender-mid)); border-radius: 99px; transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
.exit-btn { flex-shrink: 0; }

/* Question Wrap */
.question-wrap { display: flex; justify-content: center; }
.question-card { max-width: 640px; width: 100%; padding: 40px; display: flex; flex-direction: column; gap: 24px; }

.q-number { font-size: 12px; font-weight: 700; color: var(--lavender-deep); text-transform: uppercase; letter-spacing: 0.08em; }
.q-text { font-size: 20px; font-weight: 700; color: var(--plum); margin: 0; line-height: 1.4; }
.q-context { font-size: 14px; color: var(--slate); font-style: italic; margin: 0; }

/* Options */
.options-list { display: flex; flex-direction: column; gap: 10px; }
.option-card { padding: 16px 20px; border: 2px solid var(--lavender); border-radius: 12px; cursor: pointer; transition: all 0.15s; font-weight: 500; font-size: 14px; color: var(--plum); display: flex; align-items: center; gap: 14px; }
.option-card:hover { border-color: var(--lavender-deep); background: var(--lavender-soft); }
.option-card.selected { border-color: var(--lavender-deep); background: var(--lavender); font-weight: 600; }
.option-letter { width: 26px; height: 26px; border-radius: 50%; background: var(--lavender-soft); border: 1.5px solid var(--lavender); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0; transition: all 0.15s; }
.option-card.selected .option-letter { background: var(--lavender-deep); color: white; border-color: var(--lavender-deep); }
.option-text { flex: 1; }

/* Nav */
.nav-bar { display: flex; align-items: center; justify-content: space-between; padding-top: 8px; border-top: 1.5px solid var(--lavender-soft); }
.nav-right { display: flex; align-items: center; gap: 12px; }
.nav-hint { font-size: 12px; color: var(--slate); font-style: italic; }
.state-center { display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 80px 0; color: var(--slate); }
.spinner { width: 28px; height: 28px; border-radius: 50%; border: 3px solid var(--lavender); border-top-color: var(--lavender-deep); animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
