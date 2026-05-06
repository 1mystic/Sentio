<template>
  <div class="community-page">
    <div class="page-header">
      <h1 class="page-title">Community</h1>
      <p class="page-sub">A space to share patterns, ask questions, and support each other.</p>
    </div>

    <div v-if="loading" class="state-center">Loading topics…</div>
    <div v-else-if="error" class="state-center error">{{ error }}</div>

    <div v-else class="topics-grid">
      <router-link
        v-for="topic in topics"
        :key="topic.id"
        :to="`/community/${topic.slug}`"
        class="topic-card"
        :style="{ '--accent': topic.color || '#9b94e8' }"
      >
        <div class="topic-icon-wrap">
          <component :is="iconMap[topic.icon] || MessageCircle" :size="22" />
        </div>
        <div class="topic-body">
          <div class="topic-title">{{ topic.title }}</div>
          <div class="topic-desc">{{ topic.description }}</div>
        </div>
        <div class="topic-meta">
          <span class="thread-count">{{ topic.thread_count || 0 }} threads</span>
          <ChevronRight :size="16" class="chevron" />
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Eye, Scale, BookOpen, Zap, HelpCircle, MessageCircle, ChevronRight } from 'lucide-vue-next'
import apiClient from '@/api/client.js'

const iconMap = { Eye, Scale, BookOpen, Zap, HelpCircle, MessageCircle }

const topics = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const res = await apiClient.get('/community/topics')
    topics.value = res.data || []
  } catch (e) {
    error.value = e.message || 'Failed to load topics.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,400;0,500;0,600;0,700;0,800&display=swap');
* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.community-page { display: flex; flex-direction: column; gap: 28px; }
.page-header {}
.page-title { font-size: 28px; font-weight: 800; color: var(--plum); margin: 0 0 6px; }
.page-sub { font-size: 15px; color: var(--slate); margin: 0; }

.state-center { text-align: center; padding: 60px; color: var(--slate); font-size: 15px; }
.error { color: #dc2626; }

.topics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.topic-card {
  display: flex; gap: 16px; align-items: flex-start;
  background: white; border-radius: 16px;
  box-shadow: 0 4px 24px rgba(53,43,56,0.07);
  padding: 20px; text-decoration: none; color: inherit;
  border-left: 4px solid var(--accent, #9b94e8);
  transition: transform 0.15s, box-shadow 0.15s;
}
.topic-card:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(53,43,56,0.12); }

.topic-icon-wrap {
  width: 44px; height: 44px; flex-shrink: 0; border-radius: 12px;
  background: color-mix(in srgb, var(--accent, #9b94e8) 18%, white);
  color: var(--accent, #9b94e8);
  display: flex; align-items: center; justify-content: center;
}

.topic-body { flex: 1; min-width: 0; }
.topic-title { font-size: 16px; font-weight: 700; color: var(--plum); margin-bottom: 4px; }
.topic-desc { font-size: 13px; color: var(--slate); line-height: 1.5; }

.topic-meta { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; flex-shrink: 0; }
.thread-count { font-size: 11px; font-weight: 700; color: var(--slate); text-transform: uppercase; letter-spacing: 0.04em; }
.chevron { color: var(--slate); }
</style>
