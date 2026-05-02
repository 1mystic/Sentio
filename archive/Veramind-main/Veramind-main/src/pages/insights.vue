<template>
  <ProtectedRoute>
    <DashboardLayout>
      <section class="insights-page">
        <header class="page-header">
          <div>
            <p class="eyebrow">Analytics</p>
            <h1>Personal insights hub</h1>
            <p class="subtitle">Track assessments, journaling cadence, and mood patterns over time.</p>
          </div>
          <div class="filters">
            <select class="form-select" v-model="selectedRange">
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
            </select>
          </div>
        </header>

        <div class="metrics-grid">
          <MindMetricCard
            v-for="metric in metrics"
            :key="metric.label"
            v-bind="metric"
          />
        </div>

        <MindCard title="Mood consistency" description="Daily check-ins">
          <div class="chart-placeholder">
            <p>Line chart placeholder showing sentiment trends.</p>
          </div>
        </MindCard>

        <div class="insight-grid">
          <MindCard
            v-for="insight in dynamicInsights"
            :key="insight.id"
            :title="insight.title"
            :description="insight.summary"
          >
            <ul class="insight-points">
              <li v-for="point in insight.points" :key="point">{{ point }}</li>
            </ul>
            <template #footer>
              <button class="btn btn-outline btn-sm" type="button">Apply Recommendation</button>
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
import MindMetricCard from '../components/ui/MindMetricCard.vue'

const selectedRange = ref('30')

const metrics = [
  { label: 'Check-ins completed', value: 9, description: 'Consistent weekly cadence', trend: 18 },
  { label: 'Assessments tracked', value: 4, description: '2 due for refresh', trend: -5 },
  { label: 'Journal entries', value: 14, description: '4 streak days in a row', trend: 12 }
]

const insightsMap = {
  7: [
    {
      id: 'micro-wins',
      title: 'Micro wins recognized',
      summary: 'Short gratitude logs improved mood stability.',
      points: ['+22% positive sentiment', 'Morning entries are most upbeat']
    }
  ],
  30: [
    {
      id: 'sunday-scan',
      title: 'Sunday anticipatory spike',
      summary: 'Anxiety rises before the workweek.',
      points: ['Average score +4 on Sundays', 'Pair Sunday planning with grounding audio']
    },
    {
      id: 'afternoon-slump',
      title: '2pm energy dip',
      summary: 'Journal tone dips between 1-3pm.',
      points: ['Add hydration reminder', 'Consider daylight walk blocks']
    }
  ],
  90: [
    {
      id: 'seasonal-shift',
      title: 'Seasonal affective pattern',
      summary: 'Lower sunlight correlates with decreased motivation.',
      points: ['Consider dawn-simulating alarm', 'Increase outdoor time by 10 min/day']
    }
  ]
}

const dynamicInsights = computed(() => insightsMap[selectedRange.value] ?? [])
</script>

<style scoped>
.insights-page {
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

.filters {
  min-width: 200px;
}

.eyebrow {
  text-transform: uppercase;
  font-size: var(--text-xs);
  color: var(--mind-gray);
  letter-spacing: 0.08em;
}

.subtitle {
  color: var(--mind-gray);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--spacing-4);
}

.chart-placeholder {
  height: 240px;
  border: 2px dashed var(--mind-gray-border);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--mind-gray);
}

.insight-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--spacing-5);
}

.insight-points {
  list-style: disc;
  padding-left: var(--spacing-6);
  color: var(--mind-gray-dark);
}
</style>
