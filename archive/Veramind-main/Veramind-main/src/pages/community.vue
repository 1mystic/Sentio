<template>
  <ProtectedRoute>
    <DashboardLayout>
      <section class="community-page">
        <header class="page-header">
          <div>
            <p class="eyebrow">Community</p>
            <h1>Peer support circles</h1>
            <p class="subtitle">Join moderated spaces with bias checks, safety prompts, and resources.</p>
          </div>
          <MindTabs v-model="activeTab" :tabs="tabs" />
        </header>

        <div v-if="activeTab === 'discussions'" class="discussion-list">
          <MindCard
            v-for="thread in discussions"
            :key="thread.id"
            :title="thread.title"
            :description="thread.summary"
          >
            <div class="thread-meta">
              <span>{{ thread.replies }} replies</span>
              <span>{{ thread.sentiment }}</span>
              <span>Last active {{ thread.updated }}</span>
            </div>
            <template #footer>
              <button class="btn btn-outline btn-sm" type="button">Open thread</button>
              <button class="btn btn-primary btn-sm" type="button">Reply</button>
            </template>
          </MindCard>
        </div>

        <div v-else class="group-grid">
          <MindCard
            v-for="group in supportGroups"
            :key="group.id"
            :title="group.title"
            :description="group.description"
          >
            <ul class="group-info">
              <li>Focus: {{ group.focus }}</li>
              <li>Meeting cadence: {{ group.cadence }}</li>
              <li>Members: {{ group.members }}</li>
            </ul>
            <template #footer>
              <button class="btn btn-primary btn-sm" type="button">
                {{ group.joined ? 'Enter group space' : 'Join group' }}
              </button>
            </template>
          </MindCard>
        </div>
      </section>
    </DashboardLayout>
  </ProtectedRoute>
</template>

<script setup>
import { ref } from 'vue'
import DashboardLayout from '../components/DashboardLayout.vue'
import ProtectedRoute from '../components/ProtectedRoute.vue'
import MindCard from '../components/ui/MindCard.vue'
import MindTabs from '../components/ui/MindTabs.vue'

const tabs = [
  { label: 'Discussions', value: 'discussions' },
  { label: 'Support groups', value: 'groups' }
]

const activeTab = ref('discussions')

const discussions = [
  {
    id: 'breathwork',
    title: 'Favorite breathwork cues when panic rises',
    summary: 'Sharing somatic anchors that feel accessible in public spaces.',
    replies: 18,
    sentiment: 'Supportive tone',
    updated: '2h ago'
  },
  {
    id: 'value-check',
    title: 'How do you remember your values during conflict?',
    summary: 'Quick prompts or sticky notes that bring you back to what matters.',
    replies: 9,
    sentiment: 'Curious tone',
    updated: '6h ago'
  }
]

const supportGroups = [
  {
    id: 'creative-neurodivergent',
    title: 'Creative, neurodivergent professionals',
    description: 'Body doubling, sprint sessions, and processing bias checks.',
    focus: 'ADHD + anxiety',
    cadence: 'Weekly · Thursdays',
    members: 142,
    joined: true
  },
  {
    id: 'new-diagnosis',
    title: 'Living with a new diagnosis',
    description: 'Grief, celebration, and building your care team.',
    focus: 'Chronic conditions',
    cadence: 'Bi-weekly · Sundays',
    members: 87,
    joined: false
  }
]
</script>

<style scoped>
.community-page {
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

.discussion-list,
.group-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--spacing-5);
}

.thread-meta {
  display: flex;
  gap: var(--spacing-3);
  flex-wrap: wrap;
  color: var(--mind-gray);
}

.group-info {
  list-style: none;
  padding: 0;
  margin: 0 0 var(--spacing-4);
  color: var(--mind-gray);
}
</style>
