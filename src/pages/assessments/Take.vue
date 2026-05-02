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

    <!-- Question Card -->
    <div class="question-wrap">
      <div class="card question-card">

        <div class="q-number">Question {{ currentQ + 1 }}</div>
        <h2 class="q-text">{{ currentQuestion.text }}</h2>
        <p v-if="currentQuestion.context" class="q-context">{{ currentQuestion.context }}</p>

        <div class="options-list">
          <div
            v-for="(option, i) in currentQuestion.options"
            :key="i"
            class="option-card"
            :class="{ selected: answers[currentQ] === option }"
            @click="selectAnswer(option)"
          >
            <span class="option-letter">{{ String.fromCharCode(65 + i) }}</span>
            <span class="option-text">{{ option }}</span>
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
              :disabled="!answers[currentQ]"
              @click="finish"
            >Finish Assessment →</button>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const questions = ref([
  { id: 1, text: 'You\'ve been following a stock for months, convinced it will recover. It\'s down 40% from your purchase price. You...', options: ['Sell immediately to cut losses', 'Hold — I believe in my analysis', 'Buy more to average down', 'Seek opinions from others first', 'Check what the original reasons for buying were'] },
  { id: 2, text: 'You read a news article that contradicts your political views. Your first reaction is to...', options: ['Look for flaws in the article\'s methodology', 'Consider that it might have valid points', 'Share it to discuss with others', 'Close the tab and not engage', 'Look for a counter-article to balance it'] },
  { id: 3, text: 'Your first impression of a new colleague is very positive. When they make a mistake at work, you...', options: ['Assume it\'s out of character for them', 'Update your impression significantly', 'Investigate to understand what happened', 'Defend them to others', 'Give them benefit of the doubt temporarily'] },
  { id: 4, text: 'You\'re planning a 6-month project. Your gut says 6 months. Historical data says similar projects take 9 months. You estimate...', options: ['6 months — I know this project better', '9 months — trust the data', '7-8 months — compromise', '12 months — better to over-estimate', 'Ask the team for their estimates first'] },
  { id: 5, text: 'A plane crash is widely reported in the news this week. How does it affect your fear of flying?', options: ['Significantly increases it', 'Slightly increases it', 'No change — I know statistics', 'Actually makes me think more rationally', 'Depends on the cause of the crash'] },
  { id: 6, text: 'A friend is late for your coffee meeting (again). You immediately think...', options: ['They don\'t value my time', 'Something must have come up', 'I should text to check in', 'I\'m annoyed but won\'t say anything', 'This is a pattern I need to address'] },
  { id: 7, text: 'You\'re presented with a product described as "95% fat free" vs one labeled "5% fat". You...', options: ['Prefer the 95% fat free option', 'They\'re the same — no preference', 'Check the full nutrition label', 'Would need more context to decide', 'Trust neither framing'] },
  { id: 8, text: 'After making a difficult decision, new information suggests it was wrong. You...', options: ['Defend the original decision', 'Regret and ruminate', 'Accept it and adapt going forward', 'Look for reasons it could still work out', 'Analyze what went wrong to learn from it'] },
  { id: 9, text: 'Your team achieves a major success. You believe the main reason was...', options: ['My leadership and contributions', 'The team\'s collective effort', 'Good timing and circumstances', 'The process and systems we followed', 'A combination of all these factors'] },
  { id: 10, text: 'You\'re about to start a home renovation and get three quotes. You tend to...', options: ['Go with the first one you received', 'Choose the cheapest option', 'Anchor to the first quote when evaluating others', 'Research market rates before deciding', 'Choose based on gut feeling about the contractor'] },
])

const currentQ = ref(0)
const answers = ref({})

const currentQuestion = computed(() => questions.value[currentQ.value])

function selectAnswer(option) {
  answers.value[currentQ.value] = option
  if (currentQ.value < questions.value.length - 1) {
    setTimeout(() => currentQ.value++, 300)
  }
}

function finish() {
  router.push('/assessments/1/results')
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
</style>
