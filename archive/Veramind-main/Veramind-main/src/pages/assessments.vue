<template>
  <ProtectedRoute>
    <DashboardLayout>
      <section class="assessments-page">
        <header class="page-header">
          <div>
            <p class="eyebrow">Discover</p>
            <h1>Mental health assessments</h1>
            <p class="subtitle">
              Evidence-backed screeners with gentle guidance at every step.
            </p>
          </div>
          <MindTabs v-model="activeTab" :tabs="tabs" />
        </header>

        <div class="assessment-grid">
          <MindCard
            v-for="assessment in filteredAssessments"
            :key="assessment.id"
            :title="assessment.title"
            :description="assessment.description"
          >
            <dl class="assessment-meta">
              <div>
                <dt>Estimated time</dt>
                <dd>{{ assessment.duration }}</dd>
              </div>
              <div>
                <dt>Focus</dt>
                <dd>{{ assessment.focus }}</dd>
              </div>
              <div>
                <dt>Clinical use</dt>
                <dd>{{ assessment.use }}</dd>
              </div>
            </dl>

            <template #footer>
              <div class="assessment-footer">
                <span class="status" :class="assessment.status">
                  {{ assessment.status === 'completed' ? 'Completed' : 'Ready' }}
                </span>
                <div class="footer-actions">
                          <RouterLink :to="`/assessment-detail?id=${assessment.id}`" class="btn btn-outline btn-sm">
                            View Details
                          </RouterLink>
                  <button class="btn btn-primary btn-sm" type="button">
                    {{ assessment.status === 'completed' ? 'Review Results' : 'Start Assessment' }}
                  </button>
                </div>
              </div>
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
import MindTabs from '../components/ui/MindTabs.vue'

const tabs = [
  { label: 'Available', value: 'available', badge: 4 },
  { label: 'Completed', value: 'completed', badge: 2 }
]

const activeTab = ref('available')

const assessments = [
  {
    id: 'gad7',
    title: 'GAD-7 Anxiety Screener',
    description: 'Track patterns of worry, restlessness, and somatic symptoms.',
    duration: '4 min',
    focus: 'Generalized anxiety',
    use: 'Monitoring severity',
    status: 'available'
  },
  {
    id: 'phq9',
    title: 'PHQ-9 Mood Check',
    description: 'Measure mood shifts, motivation, and energy levels.',
    duration: '5 min',
    focus: 'Depressive symptoms',
    use: 'Severity detection',
    status: 'available'
  },
  {
    id: 'cbi',
    title: 'Cognitive Bias Inventory',
    description: 'Surface automatic thoughts and distortion patterns.',
    duration: '7 min',
    focus: 'Thinking patterns',
    use: 'Insight building',
    status: 'completed'
  },
  {
    id: 'values',
    title: 'Core Values Assessment',
    description: 'Clarify what matters and align decisions around it.',
    duration: '6 min',
    focus: 'Values discovery',
    use: 'Motivation cues',
    status: 'completed'
  }
]

const filteredAssessments = computed(() =>
  assessments.filter((assessment) =>
    activeTab.value === 'available'
      ? assessment.status === 'available'
      : assessment.status === 'completed'
  )
)
</script>

<style scoped>
.assessments-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: var(--spacing-6);
  flex-wrap: wrap;
  align-items: center;
}

.eyebrow {
  text-transform: uppercase;
  font-size: var(--text-xs);
  letter-spacing: 0.08em;
  color: var(--mind-gray);
}

.subtitle {
  color: var(--mind-gray);
  max-width: 560px;
}

.assessment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--spacing-5);
}

.assessment-meta {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--spacing-4);
  margin: var(--spacing-4) 0;
}

.assessment-meta dt {
  font-size: var(--text-xs);
  text-transform: uppercase;
  color: var(--mind-gray);
}

.assessment-meta dd {
  margin: var(--spacing-1) 0 0;
  font-weight: var(--font-semibold);
}

.assessment-footer {
  display: flex;
  justify-content: space-between;
  gap: var(--spacing-4);
  flex-wrap: wrap;
  align-items: center;
}

.status {
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  background-color: var(--mind-gray-light);
}

.status.completed {
  background-color: var(--success);
  color: white;
}

.footer-actions {
  display: inline-flex;
  gap: var(--spacing-3);
}
</style>
