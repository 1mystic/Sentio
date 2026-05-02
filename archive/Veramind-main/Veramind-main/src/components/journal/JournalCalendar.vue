<template>
  <div class="journal-calendar">
    <header class="journal-calendar__header">
      <button class="btn btn-ghost btn-sm" type="button" @click="previousMonth">Prev</button>
      <div>
        <p class="journal-calendar__label">Consistency tracker</p>
        <h3>{{ formattedMonth }}</h3>
      </div>
      <button class="btn btn-ghost btn-sm" type="button" @click="nextMonth">Next</button>
    </header>

    <div class="journal-calendar__grid">
      <div v-for="dayLabel in dayLabels" :key="dayLabel" class="journal-calendar__day-label">
        {{ dayLabel }}
      </div>
      <div
        v-for="(day, index) in paddedDays"
        :key="`${currentMonthKey}-${index}`"
        class="journal-calendar__cell"
        :class="{ 'has-entry': day && hasEntry(day.date) }"
      >
        <span v-if="day" class="day-number">{{ day.day }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  entries: {
    type: Array,
    default: () => []
  }
})

const currentDate = ref(new Date())

const formattedMonth = computed(() =>
  currentDate.value.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
)

const currentMonthKey = computed(() => `${currentDate.value.getFullYear()}-${currentDate.value.getMonth()}`)

const dayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

const startOfMonth = () => new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), 1)
const endOfMonth = () => new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 0)

const paddedDays = computed(() => {
  const start = startOfMonth()
  const end = endOfMonth()
  const totalDays = end.getDate()
  const padding = start.getDay()
  const days = []

  for (let i = 0; i < padding; i += 1) {
    days.push(null)
  }

  for (let day = 1; day <= totalDays; day += 1) {
    days.push({
      day,
      date: new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), day)
    })
  }

  while (days.length % 7 !== 0) {
    days.push(null)
  }

  return days
})

const previousMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
}

const nextMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
}

const hasEntry = (date) => {
  if (!date) return false
  return props.entries.some((entry) => entry.date === date.toISOString().slice(0, 10))
}
</script>

<style scoped>
.journal-calendar {
  background-color: white;
  border: 1px solid var(--mind-gray-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-6);
}

.journal-calendar__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-4);
}

.journal-calendar__label {
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: var(--spacing-1);
  color: var(--mind-gray);
}

.journal-calendar__grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: var(--spacing-2);
}

.journal-calendar__day-label {
  text-align: center;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--mind-gray);
}

.journal-calendar__cell {
  min-height: 70px;
  border-radius: var(--radius-md);
  background-color: var(--mind-gray-light);
  padding: var(--spacing-2);
  text-align: right;
}

.journal-calendar__cell.has-entry {
  background-color: var(--mind-purple-light);
  border: 1px solid var(--mind-purple);
}

.day-number {
  font-weight: var(--font-semibold);
}
</style>
