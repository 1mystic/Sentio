<template>
              <RouterLink :to="`/module-detail?id=${module.id}`" class="btn btn-outline btn-sm">
                View module
              </RouterLink>
        <header class="page-header">
          <div>
            <p class="eyebrow">Learning path</p>
            <h1>Guided modules</h1>
            <p class="subtitle">Structured micro-lessons that unlock as you progress.</p>
          </div>
          <button class="btn btn-primary" type="button">Browse library</button>
        </header>

        <div class="module-grid">
          <MindCard
            v-for="module in modules"
            :key="module.id"
            :title="module.title"
            :description="module.description"
          >
            <div class="module-meta">
              <div>
                <p class="label">Progress</p>
                <div class="progress">
                  <div class="progress__fill" :style="{ width: `${module.progress}%` }" />
                </div>
                <span>{{ module.progress }}% complete</span>
              </div>
              <div>
                <p class="label">Next lesson</p>
                <strong>{{ module.nextLesson }}</strong>
              </div>
            </div>
            <template #footer>
              <NuxtLink :to="`/module-detail?id=${module.id}`" class="btn btn-outline btn-sm">
                View module
              </NuxtLink>
              <button class="btn btn-primary btn-sm" type="button">Continue</button>
            </template>
          </MindCard>
        </div>
      </section>
    </DashboardLayout>
  </ProtectedRoute>
</template>

<script setup>
import DashboardLayout from '../components/DashboardLayout.vue'
import ProtectedRoute from '../components/ProtectedRoute.vue'
import MindCard from '../components/ui/MindCard.vue'

const modules = [
  {
    id: 'foundations',
    title: 'Foundations of calm awareness',
    description: 'Strengthen interoception, breathing cadence, and gentler self-talk.',
    progress: 65,
    nextLesson: 'Lesson 5 · Interrupting spirals'
  },
  {
    id: 'bias',
    title: 'Cognitive bias lab',
    description: 'Spot personalization, catastrophizing, and black-or-white patterns.',
    progress: 30,
    nextLesson: 'Lesson 3 · Mapping distortions'
  },
  {
    id: 'values',
    title: 'Values-aligned planning',
    description: 'Translate core values into weekly rituals and checkpoints.',
    progress: 10,
    nextLesson: 'Lesson 2 · Micro commitments'
  }
]
</script>

<style scoped>
.modules-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: var(--spacing-6);
  flex-wrap: wrap;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--spacing-5);
}

.module-meta {
  display: flex;
  justify-content: space-between;
  gap: var(--spacing-4);
  flex-wrap: wrap;
}

.label {
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--mind-gray);
}

.progress {
  width: 160px;
  height: 8px;
  background-color: var(--mind-gray-light);
  border-radius: var(--radius-full);
  margin: var(--spacing-2) 0;
}

.progress__fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--mind-blue) 0%, var(--mind-purple) 100%);
}
</style>
