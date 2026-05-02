<template>
  <ProtectedRoute>
    <DashboardLayout>
      <section class="materials-page">
        <header class="page-header">
          <div>
            <p class="eyebrow">Library</p>
            <h1>Educational materials</h1>
            <p class="subtitle">Curated explainers and research snapshots with AI summaries.</p>
          </div>
          <div class="filters">
            <input class="form-input" type="search" v-model="query" placeholder="Search articles" />
            <select class="form-select" v-model="selectedTag">
              <option value="">All topics</option>
              <option v-for="tag in tags" :key="tag" :value="tag">{{ tag }}</option>
            </select>
          </div>
        </header>

        <div class="article-grid">
          <MindCard
            v-for="article in filteredArticles"
            :key="article.id"
            :title="article.title"
            :description="article.summary"
          >
            <div class="article-meta">
              <span>{{ article.length }}</span>
              <span>{{ article.tag }}</span>
            </div>
            <template #footer>
              <button class="btn btn-outline btn-sm" type="button">Read article</button>
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
const selectedTag = ref('')

const articles = [
  {
    id: 1,
    title: 'How to decode somatic cues',
    summary: 'Map tension, heat, and numbness signals to emotional needs.',
    length: '6 min read',
    tag: 'Somatics'
  },
  {
    id: 2,
    title: 'Cognitive distortions cheat sheet',
    summary: 'Identify personalization, catastrophizing, and mental filtering quickly.',
    length: '8 min read',
    tag: 'Cognition'
  },
  {
    id: 3,
    title: 'Understanding window of tolerance',
    summary: 'Nervous system basics with regulation strategies.',
    length: '10 min watch',
    tag: 'Nervous system'
  }
]

const tags = ['Somatics', 'Cognition', 'Nervous system']

const filteredArticles = computed(() =>
  articles.filter((article) => {
    const matchesQuery = article.title.toLowerCase().includes(query.value.toLowerCase())
    const matchesTag = selectedTag.value ? article.tag === selectedTag.value : true
    return matchesQuery && matchesTag
  })
)
</script>

<style scoped>
.materials-page {
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
  align-items: center;
}

.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-5);
}

.article-meta {
  display: flex;
  gap: var(--spacing-3);
  color: var(--mind-gray);
}
</style>
