<template>
  <div class="mind-metric-card">
    <div class="mind-metric-card__meta">
      <p class="mind-metric-card__label">{{ label }}</p>
      <span class="mind-metric-card__trend" :class="trendClass">
        {{ trend > 0 ? `+${trend}%` : `${trend}%` }}
      </span>
    </div>
    <h3 class="mind-metric-card__value">{{ value }}</h3>
    <p class="mind-metric-card__description">{{ description }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  description: { type: String, default: '' },
  trend: { type: Number, default: 0 }
})

const trendClass = computed(() => {
  if (props.trend > 0) return 'positive'
  if (props.trend < 0) return 'negative'
  return ''
})
</script>

<style scoped>
.mind-metric-card {
  border: 1px solid var(--mind-gray-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-5);
  background-color: white;
  box-shadow: var(--shadow-sm);
}

.mind-metric-card__meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-2);
}

.mind-metric-card__label {
  color: var(--mind-gray);
  margin: 0;
}

.mind-metric-card__trend {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
}

.mind-metric-card__trend.positive {
  color: var(--success);
}

.mind-metric-card__trend.negative {
  color: var(--error);
}

.mind-metric-card__value {
  font-size: var(--text-3xl);
  margin: 0 0 var(--spacing-2);
}

.mind-metric-card__description {
  margin: 0;
  color: var(--mind-gray);
}
</style>
