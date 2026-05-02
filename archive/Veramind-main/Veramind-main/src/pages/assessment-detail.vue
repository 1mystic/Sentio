<template>
  <ProtectedRoute>
    <DashboardLayout>
      <section class="assessment-detail">
        <RouterLink to="/assessments" class="back-link">← Back to assessments</RouterLink>

        <header class="assessment-detail__hero">
          <div>
            <p class="eyebrow">Assessment</p>
            <h1>{{ assessment.title }}</h1>
            <p class="subtitle">{{ assessment.description }}</p>
          </div>
          <div class="hero-meta">
            <div>
              <p class="label">Duration</p>
              <strong>{{ assessment.duration }}</strong>
            </div>
            <div>
              <p class="label">Questions</p>
              <strong>{{ assessment.questions.length }}</strong>
            </div>
            <div>
              <p class="label">Status</p>
              <span class="status">{{ assessment.status }}</span>
            </div>
          </div>
        </header>

        <div class="assessment-detail__grid">
          <MindCard title="Instructions" description="What to expect">
            <ol class="instruction-list">
              <li v-for="step in assessment.instructions" :key="step">{{ step }}</li>
            </ol>
          </MindCard>

          <MindCard title="Progress" description="Pause anytime">
            <div class="progress">
              <div class="progress-bar">
                <div class="progress-bar__fill" :style="{ width: `${progress}%` }" />
              </div>
              <p>{{ answered }} / {{ assessment.questions.length }} answered</p>
            </div>
            <button class="btn btn-primary btn-lg" type="button">Resume assessment</button>
          </MindCard>
        </div>

        <section class="question-preview">
          <h2>Question preview</h2>
          <article
            v-for="question in assessment.questions"
            :key="question.id"
            class="question-card"
          >
            <header>
              <span class="question-id">Q{{ question.id }}</span>
              <p class="question-category">{{ question.category }}</p>
            </header>
            <p class="question-text">{{ question.text }}</p>
            <ul class="question-scale">
              <li v-for="choice in question.scale" :key="choice">{{ choice }}</li>
            </ul>
          </article>
        </section>

        <section class="results" v-if="assessment.results">
          <h2>Recent results</h2>
          <div class="results-grid">
            <MindCard
              v-for="result in assessment.results"
              :key="result.id"
              :title="result.title"
              :description="result.summary"
            >
              <p class="result-score">Score: {{ result.score }}</p>
              <p class="result-recommendation">{{ result.recommendation }}</p>
            </MindCard>
          </div>
        </section>
      </section>
    </DashboardLayout>
  </ProtectedRoute>
</template>

<script setup>
import { computed } from 'vue'
import DashboardLayout from '../components/DashboardLayout.vue'
import ProtectedRoute from '../components/ProtectedRoute.vue'
import MindCard from '../components/ui/MindCard.vue'

const assessment = {
  title: 'GAD-7 Anxiety Screener',
  description: 'Understand the frequency of generalized anxiety indicators.',
  duration: '4 min',
  status: 'In progress',
  instructions: [
    'Find a calm moment to reflect on the past two weeks.',
    'Answer honestly—there are no right or wrong responses.',
    'Flag any question that feels unclear to revisit with a clinician.',
    'Review your personalized recommendations at the end.'
  ],
  questions: [
    {
      id: 1,
      text: 'Feeling nervous, anxious, or on edge.',
      category: 'Emotional',
      scale: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day']
    },
    {
      id: 2,
      text: 'Not being able to stop or control worrying.',
      category: 'Thought patterns',
      scale: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day']
    },
    {
      id: 3,
      text: 'Trouble relaxing or sitting still.',
      category: 'Physical',
      scale: ['Not at all', 'Several days', 'More than half the days', 'Nearly every day']
    }
  ],
  answers: {
    1: 'More than half the days',
    2: 'Several days'
  },
  results: [
    {
      id: 'score',
      title: 'Overall score',
      summary: 'Moderate anxiety presentation',
      score: 12,
      recommendation: 'Practice scheduled worry time and body-based grounding exercises.'
    },
    {
      id: 'pattern',
      title: 'Pattern insight',
      summary: 'Peak worry happens Sunday nights and weekday mornings.',
      score: 'High cognitive load windows',
      recommendation: 'Layer guided journaling prompts before these windows.'
    }
  ]
}

const answered = computed(() => Object.keys(assessment.answers).length)

const progress = computed(() => Math.round((answered.value / assessment.questions.length) * 100))
</script>

<style scoped>
.assessment-detail {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
}

.back-link {
  color: var(--mind-gray);
  font-size: var(--text-sm);
}

.assessment-detail__hero {
  display: flex;
  justify-content: space-between;
  gap: var(--spacing-6);
  flex-wrap: wrap;
  align-items: flex-start;
}

.subtitle {
  color: var(--mind-gray);
  max-width: 520px;
}

.hero-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: var(--spacing-4);
}

.label {
  text-transform: uppercase;
  font-size: var(--text-xs);
  letter-spacing: 0.08em;
  color: var(--mind-gray);
}

.status {
  background-color: var(--mind-blue-light);
  color: var(--mind-blue-dark);
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--radius-full);
}

.assessment-detail__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-5);
}

.instruction-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  padding-left: var(--spacing-4);
}

.progress {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.progress-bar {
  width: 100%;
  height: 8px;
  border-radius: var(--radius-full);
  background-color: var(--mind-gray-light);
}

.progress-bar__fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--mind-purple) 0%, var(--mind-blue) 100%);
}

.question-preview {
  background-color: white;
  border-radius: var(--radius-lg);
  border: 1px solid var(--mind-gray-border);
  padding: var(--spacing-6);
}

.question-card {
  border-bottom: 1px solid var(--mind-gray-border);
  padding: var(--spacing-4) 0;
}

.question-card:last-child {
  border-bottom: none;
}

.question-card header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--mind-gray);
}

.question-id {
  font-weight: var(--font-semibold);
}

.question-text {
  margin: var(--spacing-2) 0;
}

.question-scale {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
  list-style: none;
  padding: 0;
}

.question-scale li {
  padding: var(--spacing-2) var(--spacing-3);
  background-color: var(--mind-gray-light);
  border-radius: var(--radius-full);
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-4);
}

.result-score {
  font-size: var(--text-2xl);
  margin-bottom: var(--spacing-2);
}

.result-recommendation {
  color: var(--mind-gray);
}
</style>
