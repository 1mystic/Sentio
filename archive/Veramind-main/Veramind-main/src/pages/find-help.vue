<template>
  <ProtectedRoute>
    <DashboardLayout>
      <section class="find-help-page">
        <header class="page-header">
          <div>
            <p class="eyebrow">Care network</p>
            <h1>Find help</h1>
            <p class="subtitle">Browse vetted professionals, helplines, and organizations.</p>
          </div>
          <div class="filters">
            <input class="form-input" type="search" v-model="query" placeholder="Search providers or organizations" />
            <select class="form-select" v-model="selectedType">
              <option value="">All types</option>
              <option value="therapist">Therapist</option>
              <option value="coach">Coach</option>
              <option value="organization">Organization</option>
            </select>
          </div>
        </header>

        <section class="crisis-banner">
          <h2>Need immediate support?</h2>
          <p>Call or text 988 (US) · 24/7 crisis line · Confidential</p>
          <div class="banner-actions">
            <a class="btn btn-destructive" href="tel:988">Call 988</a>
            <a class="btn btn-outline" href="https://988lifeline.org" target="_blank" rel="noreferrer">Visit 988 Lifeline</a>
          </div>
        </section>

        <div class="provider-grid">
          <MindCard
            v-for="entry in filteredEntries"
            :key="entry.id"
            :title="entry.name"
            :description="entry.specialty"
          >
            <p class="provider-meta">{{ entry.location }} · {{ entry.typeLabel }}</p>
            <ul class="provider-tags">
              <li v-for="tag in entry.focus" :key="tag">{{ tag }}</li>
            </ul>
            <template #footer>
              <button class="btn btn-primary btn-sm" type="button">View profile</button>
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

const query = ref('')
const selectedType = ref('')

const entries = [
  {
    id: 1,
    name: 'Aria Flores, LMFT',
    type: 'therapist',
    typeLabel: 'Therapist · Telehealth + Oakland',
    specialty: 'Anxiety, culturally responsive care, creatives',
    location: 'Hybrid care',
    focus: ['Anxiety', 'BIPOC', 'Creative professionals']
  },
  {
    id: 2,
    name: 'North Star Peer Group',
    type: 'organization',
    typeLabel: 'Peer-led organization',
    specialty: 'Grief circles, body doubling, accountability pods',
    location: 'Virtual',
    focus: ['Peer support', 'Grief']
  },
  {
    id: 3,
    name: 'Somatic Skills Coach · MJ',
    type: 'coach',
    typeLabel: 'Somatic coach',
    specialty: 'Breathwork, nervous system mapping, ADHD tools',
    location: 'Remote',
    focus: ['Somatics', 'ADHD']
  }
]

const filteredEntries = computed(() =>
  entries.filter((entry) => {
    const matchesQuery = query.value
      ? entry.name.toLowerCase().includes(query.value.toLowerCase()) ||
        entry.specialty.toLowerCase().includes(query.value.toLowerCase())
      : true
    const matchesType = selectedType.value ? entry.type === selectedType.value : true
    return matchesQuery && matchesType
  })
)
</script>

<style scoped>
.find-help-page {
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
  display: flex;
  gap: var(--spacing-3);
  flex-wrap: wrap;
}

.crisis-banner {
  border-radius: var(--radius-xl);
  padding: var(--spacing-6);
  background: linear-gradient(135deg, var(--error) 0%, #f97316 100%);
  color: white;
}

.banner-actions {
  display: flex;
  gap: var(--spacing-3);
  margin-top: var(--spacing-4);
}

.provider-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-5);
}

.provider-meta {
  margin-bottom: var(--spacing-2);
  color: var(--mind-gray);
}

.provider-tags {
  list-style: none;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
}

.provider-tags li {
  background-color: var(--mind-gray-light);
  border-radius: var(--radius-full);
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--text-xs);
}
</style>
