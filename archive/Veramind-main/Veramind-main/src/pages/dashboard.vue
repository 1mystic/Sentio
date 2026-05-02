<template>
  <ProtectedRoute>
    <DashboardLayout>
      <div class="dashboard-page">
        <h1>Welcome back, {{ userName }}!</h1>
        
        <div class="quick-actions">
          <h2>Quick Actions</h2>
          <div class="actions-grid">
            <RouterLink to="/assessments" class="action-card">
              <div class="action-icon">📝</div>
              <h3>Start Check-in</h3>
              <p>Take a mental health assessment</p>
            </RouterLink>
            <RouterLink to="/modules" class="action-card">
              <div class="action-icon">📚</div>
              <h3>Continue Module</h3>
              <p>Resume your learning</p>
            </RouterLink>
            <RouterLink to="/journal" class="action-card">
              <div class="action-icon">📔</div>
              <h3>Write in Journal</h3>
              <p>Reflect on your day</p>
            </RouterLink>
          </div>
        </div>

        <div class="dashboard-sections">
          <div class="dashboard-section">
            <h2>Recent Insights</h2>
            <div class="insights-placeholder">
              <p>Your insights will appear here</p>
            </div>
          </div>

          <div class="dashboard-section">
            <h2>Active Modules</h2>
            <div class="modules-placeholder">
              <p>Your active modules will appear here</p>
            </div>
          </div>
        </div>

        <div class="crisis-banner">
          <h3>🆘 Need Immediate Help?</h3>
          <p>If you're in crisis, please reach out:</p>
          <div class="crisis-links">
            <a href="tel:988" class="btn btn-destructive">Call 988</a>
            <RouterLink to="/crisis" class="btn btn-outline">Crisis Resources</RouterLink>
          </div>
        </div>
      </div>
    </DashboardLayout>
  </ProtectedRoute>
</template>

<script setup>
import { computed } from 'vue'
import { useAuth } from '../composables/useAuth'

const { user } = useAuth()

const userName = computed(() => {
  return user.value?.user_metadata?.full_name || 'User'
})
</script>

<style scoped>
.dashboard-page {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-page > h1 {
  margin-bottom: var(--spacing-8);
}

.quick-actions {
  margin-bottom: var(--spacing-8);
}

.quick-actions h2 {
  margin-bottom: var(--spacing-4);
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-6);
}

.action-card {
  background-color: white;
  padding: var(--spacing-6);
  border-radius: var(--radius-lg);
  border: 1px solid var(--mind-gray-border);
  text-decoration: none;
  color: inherit;
  transition: all var(--transition-base);
  text-align: center;
}

.action-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
  border-color: var(--mind-purple);
}

.action-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-4);
}

.action-card h3 {
  margin-bottom: var(--spacing-2);
  color: var(--mind-gray-dark);
}

.action-card p {
  color: var(--mind-gray);
  margin: 0;
}

.dashboard-sections {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--spacing-6);
  margin-bottom: var(--spacing-8);
}

.dashboard-section {
  background-color: white;
  padding: var(--spacing-6);
  border-radius: var(--radius-lg);
  border: 1px solid var(--mind-gray-border);
}

.dashboard-section h2 {
  margin-bottom: var(--spacing-4);
}

.insights-placeholder,
.modules-placeholder {
  padding: var(--spacing-8);
  text-align: center;
  color: var(--mind-gray);
  background-color: var(--mind-gray-light);
  border-radius: var(--radius-md);
}

.crisis-banner {
  background-color: var(--error);
  color: white;
  padding: var(--spacing-6);
  border-radius: var(--radius-lg);
  text-align: center;
}

.crisis-banner h3 {
  color: white;
  margin-bottom: var(--spacing-2);
}

.crisis-banner p {
  margin-bottom: var(--spacing-4);
}

.crisis-links {
  display: flex;
  gap: var(--spacing-4);
  justify-content: center;
}
</style>

