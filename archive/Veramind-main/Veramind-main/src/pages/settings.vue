<template>
  <ProtectedRoute>
    <DashboardLayout>
      <section class="settings-page">
        <header class="page-header">
          <div>
            <p class="eyebrow">Settings</p>
            <h1>Account & preferences</h1>
            <p class="subtitle">Manage profile, privacy controls, notifications, and integrations.</p>
          </div>
        </header>

        <div class="settings-grid">
          <MindCard title="Account" description="Profile basics">
            <form class="settings-form" @submit.prevent>
              <label class="form-label" for="name">Full name</label>
              <input id="name" v-model="form.name" class="form-input" />

              <label class="form-label" for="email">Email</label>
              <input id="email" v-model="form.email" class="form-input" type="email" />

              <label class="form-label" for="timezone">Timezone</label>
              <select id="timezone" v-model="form.timezone" class="form-select">
                <option value="PST">Pacific</option>
                <option value="EST">Eastern</option>
                <option value="UTC">UTC</option>
              </select>
              <button class="btn btn-primary" type="submit">Save profile</button>
            </form>
          </MindCard>

          <MindCard title="Privacy" description="Data controls">
            <div class="form-group">
              <label class="form-label">Data exports</label>
              <button class="btn btn-outline" type="button">Download journal archive</button>
            </div>
            <div class="form-group">
              <label class="form-label">AI learning opt-in</label>
              <label class="form-checkbox">
                <input type="checkbox" v-model="form.aiOptIn" />
                <span>Share anonymized insights to improve VeraMind models</span>
              </label>
            </div>
          </MindCard>

          <MindCard title="Notifications" description="Stay in the loop">
            <label class="form-checkbox" v-for="option in notificationOptions" :key="option.id">
              <input type="checkbox" v-model="form.notifications" :value="option.id" />
              <span>{{ option.label }}</span>
            </label>
          </MindCard>

          <MindCard title="Connected services" description="Calendar & wearable sync">
            <div class="integration-card" v-for="integration in integrations" :key="integration.id">
              <div>
                <p class="integration-name">{{ integration.name }}</p>
                <p class="integration-status">Status: {{ integration.connected ? 'Connected' : 'Not connected' }}</p>
              </div>
              <button class="btn btn-outline btn-sm" type="button">
                {{ integration.connected ? 'Manage' : 'Connect' }}
              </button>
            </div>
          </MindCard>
        </div>
      </section>
    </DashboardLayout>
  </ProtectedRoute>
</template>

<script setup>
import { reactive } from 'vue'
import DashboardLayout from '../components/DashboardLayout.vue'
import ProtectedRoute from '../components/ProtectedRoute.vue'
import MindCard from '../components/ui/MindCard.vue'

const form = reactive({
  name: 'VeraMind Member',
  email: 'user@example.com',
  timezone: 'PST',
  aiOptIn: true,
  notifications: ['weekly-digest', 'journal-reminders']
})

const notificationOptions = [
  { id: 'weekly-digest', label: 'Weekly progress digest' },
  { id: 'journal-reminders', label: 'Gentle journal reminders' },
  { id: 'module-updates', label: 'Module unlock & quiz updates' }
]

const integrations = [
  { id: 'calendar', name: 'Google Calendar', connected: true },
  { id: 'wearable', name: 'Oura Ring', connected: false }
]
</script>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--spacing-5);
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.integration-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-4);
  border: 1px solid var(--mind-gray-border);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-3);
}

.integration-name {
  font-weight: var(--font-semibold);
  margin: 0;
}

.integration-status {
  margin: var(--spacing-1) 0 0;
  color: var(--mind-gray);
}
</style>
