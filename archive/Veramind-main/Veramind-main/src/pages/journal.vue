<template>
  <ProtectedRoute>
    <DashboardLayout>
      <section class="journal-page">
        <header class="page-header">
          <div>
            <p class="eyebrow">Reflection studio</p>
            <h1>Journaling</h1>
            <p class="subtitle">Rotate prompts, analyze themes, and build a consistent practice.</p>
          </div>
          <MindTabs v-model="activeTab" :tabs="tabs" />
        </header>

        <div v-if="activeTab === 'write'" class="journal-write">
          <MindCard>
            <JournalEditor :entry="draftEntry" @save="handleSave" />
          </MindCard>
        </div>

        <div v-else-if="activeTab === 'past'">
          <JournalEntryList
            :entries="entries"
            :tags="availableTags"
            @edit="populateDraft"
          />
        </div>

        <div v-else-if="activeTab === 'calendar'">
          <JournalCalendar :entries="entries" />
        </div>

        <div v-else class="journal-analytics">
          <MindCard title="Sentiment overview" description="AI-powered tone analysis">
            <ul class="insight-points">
              <li>Optimistic tone increased 18% week-over-week.</li>
              <li>Recurring themes: resilience, clarity, rest.</li>
              <li>Consider adding evening wind-down log for sleep insights.</li>
            </ul>
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
import JournalEditor from '../components/journal/JournalEditor.vue'
import JournalEntryList from '../components/journal/JournalEntryList.vue'
import JournalCalendar from '../components/journal/JournalCalendar.vue'

const tabs = [
  { label: 'Write', value: 'write' },
  { label: 'Past entries', value: 'past' },
  { label: 'Calendar', value: 'calendar' },
  { label: 'Analytics', value: 'analytics' }
]

const activeTab = ref('write')

const entries = ref([
  {
    id: 1,
    date: '2025-11-15',
    title: 'Sunday reset wins',
    mood: 'Inspired',
    content: 'Outlined priorities and set gentle intentions for the week.',
    tags: ['gratitude', 'planning']
  },
  {
    id: 2,
    date: '2025-11-16',
    title: 'When anxiety whispered',
    mood: 'Anxious',
    content: 'Noticed tension before the presentation. Box breathing helped.',
    tags: ['anxiety', 'breathwork']
  }
])

const draftEntry = ref({
  date: new Date().toISOString().slice(0, 10),
  mood: 'neutral',
  content: '',
  tags: []
})

const availableTags = computed(() => Array.from(new Set(entries.value.flatMap((entry) => entry.tags))))

const handleSave = (entry) => {
  const existingIndex = entries.value.findIndex((item) => item.id === entry.id)
  if (existingIndex > -1) {
    entries.value[existingIndex] = entry
  } else {
    entries.value.unshift({ ...entry, id: Date.now() })
  }
  draftEntry.value = {
    date: new Date().toISOString().slice(0, 10),
    mood: 'neutral',
    content: '',
    tags: []
  }
  activeTab.value = 'past'
}

const populateDraft = (entry) => {
  draftEntry.value = { ...entry }
  activeTab.value = 'write'
}
</script>

<style scoped>
.journal-page {
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

.journal-write,
.journal-analytics {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
}

.subtitle {
  color: var(--mind-gray);
}

.insight-points {
  list-style: disc;
  padding-left: var(--spacing-6);
  color: var(--mind-gray-dark);
}
</style>
