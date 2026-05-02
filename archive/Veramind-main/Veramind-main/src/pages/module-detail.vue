<template>
  <ProtectedRoute>
    <DashboardLayout>
      <section class="module-detail">
        <RouterLink to="/modules" class="back-link">← Back to modules</RouterLink>
        <header class="module-hero">
          <div>
            <p class="eyebrow">Module</p>
            <h1>{{ module.title }}</h1>
            <p class="subtitle">{{ module.description }}</p>
          </div>
          <div class="hero-actions">
            <button class="btn btn-outline" type="button">Download outline</button>
            <button class="btn btn-primary" type="button">Continue lesson</button>
          </div>
        </header>

        <MindCard title="Lesson map" description="Sequential unlocking">
          <ol class="lesson-list">
            <li v-for="lesson in module.lessons" :key="lesson.id" :class="lesson.status">
              <div class="lesson-header">
                <div>
                  <p class="lesson-title">{{ lesson.title }}</p>
                  <p class="lesson-meta">{{ lesson.duration }} · {{ lesson.type }}</p>
                </div>
                <span class="lesson-status">{{ lesson.status }}</span>
              </div>
              <p class="lesson-summary">{{ lesson.summary }}</p>
            </li>
          </ol>
        </MindCard>

        <MindCard title="Reflection prompts" description="Integrate what you learn">
          <ul class="insight-points">
            <li v-for="prompt in module.prompts" :key="prompt">{{ prompt }}</li>
          </ul>
        </MindCard>
      </section>
    </DashboardLayout>
  </ProtectedRoute>
</template>

<script setup>
import DashboardLayout from '../components/DashboardLayout.vue'
import ProtectedRoute from '../components/ProtectedRoute.vue'
import MindCard from '../components/ui/MindCard.vue'

const module = {
  title: 'Foundations of calm awareness',
  description: 'Learn nervous system basics, pacing, and daily grounding rituals.',
  lessons: [
    {
      id: 1,
      title: 'Lesson 1 · Naming body cues',
      duration: '8 min',
      type: 'Video + worksheet',
      status: 'completed',
      summary: 'Map physical sensations to emotional vocabulary.'
    },
    {
      id: 2,
      title: 'Lesson 2 · Breath pacing lab',
      duration: '12 min',
      type: 'Interactive',
      status: 'completed',
      summary: 'Practice cadence breathing with audiovisual cues.'
    },
    {
      id: 3,
      title: 'Lesson 3 · Interrupting spirals',
      duration: '10 min',
      type: 'Video + journaling',
      status: 'in-progress',
      summary: 'Stack grounding, cognitive reframing, and micro movements.'
    },
    {
      id: 4,
      title: 'Lesson 4 · Designing rituals',
      duration: '15 min',
      type: 'Workshop',
      status: 'locked',
      summary: 'Create crisis, calm, and maintenance rituals.'
    }
  ],
  prompts: [
    'Where does anxiety show up first in your body?',
    'Which rituals feel restorative vs. performative?',
    'What support do you need before lesson 4 unlocks?'
  ]
}
</script>

<style scoped>
.module-detail {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
}

.back-link {
  font-size: var(--text-sm);
  color: var(--mind-gray);
}

.module-hero {
  display: flex;
  justify-content: space-between;
  gap: var(--spacing-6);
  flex-wrap: wrap;
}

.hero-actions {
  display: inline-flex;
  gap: var(--spacing-3);
  align-items: center;
}

.lesson-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.lesson-list li {
  border-bottom: 1px solid var(--mind-gray-border);
  padding-bottom: var(--spacing-3);
}

.lesson-list li:last-child {
  border-bottom: none;
}

.lesson-header {
  display: flex;
  justify-content: space-between;
  gap: var(--spacing-4);
}

.lesson-title {
  font-weight: var(--font-semibold);
  margin: 0;
}

.lesson-meta {
  margin: var(--spacing-1) 0 0;
  color: var(--mind-gray);
}

.lesson-status {
  text-transform: capitalize;
  font-size: var(--text-sm);
  color: var(--mind-gray);
}

.lesson-summary {
  margin-top: var(--spacing-2);
  color: var(--mind-gray-dark);
}

.lesson-list li.completed .lesson-status {
  color: var(--success);
}

.lesson-list li.in-progress .lesson-status {
  color: var(--mind-blue);
}

.lesson-list li.locked .lesson-status {
  color: var(--mind-gray);
}

.insight-points {
  list-style: disc;
  padding-left: var(--spacing-6);
}
</style>
