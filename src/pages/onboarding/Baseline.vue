<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const questions = [
  {
    text: 'When I make a decision, I usually…',
    options: ['Trust my gut', 'Research extensively', 'Ask others', 'Mix of both']
  },
  {
    text: 'When someone disagrees with me, I…',
    options: ['Get defensive', 'Listen carefully', 'Consider their point', 'Depends on topic']
  },
  {
    text: 'I believe my memory is…',
    options: ['Very reliable', 'Sometimes faulty', 'Often unreliable', 'Not sure']
  },
  {
    text: 'When looking for information I…',
    options: ['Check multiple sources', 'Use the first result', 'Trust familiar sources', 'Verify with experts']
  },
  {
    text: 'In groups, my opinions are…',
    options: ['Easily influenced', 'Sometimes shifted', 'Rarely changed', 'Never changed']
  }
]

const currentQ = ref(0)
const answers = ref(Array(questions.length).fill(null))

const currentQuestion = computed(() => questions[currentQ.value])
const currentAnswer = computed(() => answers.value[currentQ.value])
const isLast = computed(() => currentQ.value === questions.length - 1)
const isFirst = computed(() => currentQ.value === 0)

function selectOption(idx) {
  answers.value[currentQ.value] = idx
}

function goNext() {
  if (currentAnswer.value === null) return
  if (isLast.value) {
    router.push('/onboarding/interests')
  } else {
    currentQ.value++
  }
}

function goBack() {
  if (!isFirst.value) currentQ.value--
  else router.push('/onboarding/welcome')
}
</script>

<template>
  <div class="baseline-wrap fade-up">
    <!-- Header -->
    <div class="step-header">
      <span class="badge badge-lavender">Step 2 of 4</span>
      <h2 class="title">Quick Baseline Assessment</h2>
      <p class="description">
        Answer these 5 scenarios honestly — there are no wrong answers.
      </p>
    </div>

    <!-- Question card -->
    <div class="question-card card">
      <div class="q-meta">
        <span class="q-num">Question {{ currentQ + 1 }} of {{ questions.length }}</span>
      </div>
      <h3 class="q-text">{{ currentQuestion.text }}</h3>
      <div class="options-list">
        <button
          v-for="(opt, i) in currentQuestion.options"
          :key="i"
          type="button"
          class="option-btn"
          :class="{ selected: currentAnswer === i }"
          @click="selectOption(i)"
        >
          <span class="opt-letter">{{ ['A', 'B', 'C', 'D'][i] }}</span>
          <span class="opt-text">{{ opt }}</span>
        </button>
      </div>
    </div>

    <!-- Progress dots -->
    <div class="progress-dots" role="tablist" aria-label="Question progress">
      <button
        v-for="(_, i) in questions"
        :key="i"
        type="button"
        class="dot"
        :class="{
          active: i === currentQ,
          answered: answers[i] !== null
        }"
        role="tab"
        :aria-selected="i === currentQ"
        :aria-label="`Question ${i + 1}`"
        @click="currentQ = i"
      />
    </div>

    <!-- Actions -->
    <div class="actions">
      <button type="button" class="btn btn-ghost" @click="goBack">
        ← Back
      </button>
      <button
        type="button"
        class="btn btn-primary btn-lg"
        :disabled="currentAnswer === null"
        @click="goNext"
      >
        {{ isLast ? 'Finish' : 'Next' }} →
      </button>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

.baseline-wrap {
  font-family: 'Urbanist', sans-serif;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.step-header { display: flex; flex-direction: column; gap: 8px; }
.title { font-size: 24px; font-weight: 700; color: var(--plum); line-height: 1.25; margin: 0; }
.description { font-size: 14px; color: var(--slate); line-height: 1.6; margin: 0; }

/* Question card */
.question-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(53,43,56,0.07);
  padding: 24px;
  border: 1px solid rgba(218,216,249,0.5);
}
.q-meta { margin-bottom: 8px; }
.q-num {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--lavender-deep);
  background: var(--lavender-soft);
  padding: 3px 10px;
  border-radius: 99px;
}
.q-text {
  font-size: 17px;
  font-weight: 600;
  color: var(--plum);
  margin: 14px 0 18px;
  line-height: 1.45;
}

/* Options */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.option-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1.5px solid var(--lavender);
  background: white;
  cursor: pointer;
  font-family: 'Urbanist', sans-serif;
  font-size: 14px;
  color: var(--plum);
  text-align: left;
  transition: all 0.15s;
}
.option-btn:hover {
  border-color: var(--lavender-deep);
  background: var(--lavender-soft);
}
.option-btn.selected {
  background: var(--lavender);
  border-color: var(--lavender-deep);
  font-weight: 600;
}
.opt-letter {
  width: 26px;
  height: 26px;
  border-radius: 7px;
  background: var(--lavender-soft);
  color: var(--lavender-deep);
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.15s;
}
.option-btn.selected .opt-letter {
  background: var(--lavender-deep);
  color: white;
}
.opt-text { flex: 1; }

/* Progress dots */
.progress-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--lavender-soft);
  border: 1.5px solid var(--lavender);
  cursor: pointer;
  transition: all 0.2s;
  padding: 0;
}
.dot.answered { background: var(--lavender-mid); border-color: var(--lavender-mid); }
.dot.active { background: var(--lavender-deep); border-color: var(--lavender-deep); transform: scale(1.25); }

/* Actions */
.actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; }
</style>
