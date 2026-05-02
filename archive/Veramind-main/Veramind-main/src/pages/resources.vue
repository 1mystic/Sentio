<template>
  <ProtectedRoute>
    <DashboardLayout>
      <section class="resources-page">
        <header class="page-header">
          <div>
            <p class="eyebrow">Support hub</p>
            <h1>Resources</h1>
            <p class="subtitle">Central place for crisis care, educational deep dives, and practical tools.</p>
          </div>
          <RouterLink to="/find-help" class="btn btn-destructive">Crisis & Find help</RouterLink>
        </header>

        <div class="resource-grid">
          <MindCard title="Educational materials" description="Research-backed articles and explainers">
            <p>Explore explainers on cognitive distortions, nervous system 101, and AI-summarized research.</p>
            <template #footer>
              <RouterLink to="/educational-materials" class="btn btn-outline">Browse articles</RouterLink>
            </template>
          </MindCard>

          <MindCard title="Self-help tools" description="Interactive exercises">
            <p>Breath pacing, thought challenging, sensory grounding, and journaling templates.</p>
            <template #footer>
              <RouterLink to="/self-help-tools" class="btn btn-outline">Open toolkit</RouterLink>
            </template>
          </MindCard>

          <MindCard title="Find help" description="Human support">
            <p>Therapists, peer specialists, helplines, and culturally informed organizations.</p>
            <template #footer>
              <RouterLink to="/find-help" class="btn btn-outline">View directory</RouterLink>
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
</script>

<style scoped>
.resources-page {
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

.resource-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-5);
}
</style>
