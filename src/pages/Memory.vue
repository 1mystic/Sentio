<template>
  <div class="memory-page">

    <div class="page-header">
      <h1 class="page-title">What Sentio Remembers</h1>
      <p class="page-sub">
        Sentio keeps two kinds of memory about you: recent session summaries (episodic) and
        long-term patterns it has learned (semantic). You can delete any item — or everything — at any time.
      </p>
    </div>

    <div v-if="loading" class="card empty-card">Loading your memory…</div>
    <div v-else-if="error" class="card empty-card error-text">{{ error }}</div>

    <template v-else>

      <!-- Semantic facts -->
      <div class="card mem-card">
        <div class="section-header">
          <span class="section-title">🧠 Long-term facts</span>
          <span class="mem-count">{{ facts.length }}</span>
        </div>
        <p class="mem-desc">Stable patterns consolidated nightly from your conversations. These persist for months and shape how the AI Guide responds to you.</p>
        <div v-if="!facts.length" class="empty-hint">Nothing here yet — facts appear after you've chatted across multiple sessions.</div>
        <div v-for="f in facts" :key="f.id" class="mem-item">
          <div class="mem-text">{{ f.fact }}</div>
          <div class="mem-meta">
            <span class="badge badge-lavender">used {{ f.access_count }}×</span>
            <button class="btn btn-ghost btn-sm del-btn" :disabled="deleting === f.id" @click="deleteItem(f.id, 'fact')">
              {{ deleting === f.id ? '…' : '🗑' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Episodic memories -->
      <div class="card mem-card">
        <div class="section-header">
          <span class="section-title">💬 Recent session memories</span>
          <span class="mem-count">{{ episodes.length }}</span>
        </div>
        <p class="mem-desc">One summary per chat session. These fade over ~2 weeks; important ones get promoted into long-term facts.</p>
        <div v-if="!episodes.length" class="empty-hint">No session memories yet — have a conversation with the AI Guide first.</div>
        <div v-for="e in episodes" :key="e.id" class="mem-item">
          <div class="mem-text">{{ e.summary }}</div>
          <div class="mem-meta">
            <span class="badge badge-lavender">{{ formatAge(e.age_days) }}</span>
            <button class="btn btn-ghost btn-sm del-btn" :disabled="deleting === e.id" @click="deleteItem(e.id, 'episode')">
              {{ deleting === e.id ? '…' : '🗑' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Wipe all -->
      <div class="card danger-card">
        <div class="danger-title">Forget everything</div>
        <p class="danger-desc">Permanently delete all episodic memories and long-term facts. The AI Guide will start fresh. This cannot be undone.</p>
        <button class="btn btn-danger btn-sm" :disabled="wiping || (!facts.length && !episodes.length)" @click="wipeAll">
          {{ wiping ? 'Deleting…' : '🗑 Delete All Memory' }}
        </button>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import client from '@/api/client.js'

const loading = ref(true)
const error = ref('')
const episodes = ref([])
const facts = ref([])
const deleting = ref(null)
const wiping = ref(false)

function formatAge(days) {
  if (days < 1) return 'today'
  if (days < 2) return 'yesterday'
  return `${Math.round(days)} days ago`
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get('/ai/memory')
    episodes.value = data.episodes || []
    facts.value = data.facts || []
  } catch (e) {
    error.value = e.message || 'Failed to load memory'
  } finally {
    loading.value = false
  }
}

async function deleteItem(id, source) {
  deleting.value = id
  try {
    await client.delete(`/ai/memory/${id}`, { params: { source } })
    if (source === 'fact') facts.value = facts.value.filter(f => f.id !== id)
    else episodes.value = episodes.value.filter(e => e.id !== id)
  } catch (e) {
    error.value = e.message
  } finally {
    deleting.value = null
  }
}

async function wipeAll() {
  if (!confirm('Delete ALL memories? Sentio will forget everything it has learned about you.')) return
  wiping.value = true
  try {
    await client.delete('/ai/memory')
    episodes.value = []
    facts.value = []
  } catch (e) {
    error.value = e.message
  } finally {
    wiping.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.memory-page { max-width: 760px; margin: 0 auto; }
.page-header { margin-bottom: 20px; }
.page-title { font-size: 24px; font-weight: 700; margin: 0 0 6px; }
.page-sub { font-size: 13.5px; color: var(--slate, #64748b); margin: 0; line-height: 1.5; }
.mem-card { margin-bottom: 16px; padding: 20px; }
.section-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.section-title { font-weight: 600; font-size: 15px; }
.mem-count { font-size: 12px; color: var(--slate, #64748b); background: var(--bg, #f4f2f7); border-radius: 10px; padding: 2px 8px; }
.mem-desc { font-size: 12.5px; color: var(--slate, #64748b); margin: 0 0 12px; line-height: 1.45; }
.empty-hint { font-size: 13px; color: var(--slate, #94a3b8); padding: 12px 0; font-style: italic; }
.mem-item { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; padding: 10px 0; border-top: 1px solid var(--bg, #eee); }
.mem-text { font-size: 13.5px; line-height: 1.5; flex: 1; }
.mem-meta { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
.del-btn { padding: 2px 8px; }
.empty-card { padding: 32px; text-align: center; color: var(--slate, #64748b); }
.error-text { color: #dc2626; }
.danger-card { padding: 20px; border: 1px solid #fecaca; }
.danger-title { font-weight: 600; font-size: 14px; color: #dc2626; margin-bottom: 4px; }
.danger-desc { font-size: 12.5px; color: var(--slate, #64748b); margin: 0 0 12px; line-height: 1.45; }
</style>
