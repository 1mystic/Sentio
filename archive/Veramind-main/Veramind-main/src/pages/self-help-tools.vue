<template>
  <ProtectedRoute>
    <DashboardLayout>
      <section class="tools-page">
        <header class="page-header">
          <div>
            <p class="eyebrow">Toolkit</p>
            <h1>Self-help tools</h1>
            <p class="subtitle">Interactive practices for grounding, reframing, and calming.</p>
          </div>
          <select class="form-select" v-model="selectedCategory">
            <option value="">All categories</option>
            <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
          </select>
        </header>

        <div class="tool-grid">
          <MindCard
            v-for="tool in filteredTools"
            :key="tool.id"
            :title="tool.title"
            :description="tool.summary"
          >
            <p class="tool-meta">{{ tool.category }} · {{ tool.time }}</p>
            <ul class="tool-steps">
              <li v-for="step in tool.steps" :key="step">{{ step }}</li>
            </ul>
            <template #footer>
              <button class="btn btn-primary btn-sm" type="button">Launch exercise</button>
            </template>
          </MindCard>
        </div>
      </section>
    </DashboardLayout>
  </ProtectedRoute>
</template>

<script setup>
import { computed, ref } from 'vue'
import DashboardLayout from '../components/DashboardLayout.vue'
import ProtectedRoute from '../components/ProtectedRoute.vue'
import MindCard from '../components/ui/MindCard.vue'

const selectedCategory = ref('')

const tools = [
  {
    id: 'box-breathing',
    title: 'Box breathing visualizer',
    summary: 'Animated guide with haptic cues to slow the nervous system.',
    category: 'Breathwork',
    time: '4 min',
    steps: ['Inhale 4', 'Hold 4', 'Exhale 4', 'Hold 4']
  },
  {
    id: 'thought-challenge',
    title: 'Thought challenging worksheet',
    summary: 'Reframe recurring cognitive distortions.',
    category: 'Cognitive',
    time: '7 min',
    steps: ['Trigger', 'Automatic thought', 'Evidence', 'Balanced response']
  },
  {
    id: 'body-scan',
    title: 'Sensory body scan',
    summary: 'Audio-led progressive relaxation script.',
    category: 'Somatic',
    time: '10 min',
    steps: ['Feet check-in', 'Torso sweep', 'Face softening']
  }
]

const categories = ['Breathwork', 'Cognitive', 'Somatic']

const filteredTools = computed(() =>
  tools.filter((tool) => (selectedCategory.value ? tool.category === selectedCategory.value : true))
)
</script>

<style scoped>
.tools-page {
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

.tool-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-5);
}

.tool-meta {
  color: var(--mind-gray);
  margin-bottom: var(--spacing-3);
}

.tool-steps {
  list-style: decimal;
  padding-left: var(--spacing-6);
  color: var(--mind-gray-dark);
}
</style>
