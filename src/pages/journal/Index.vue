<template>
  <div class="journal-page">

    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">My Journal</h1>
        <span class="badge badge-lavender">{{ journalStore.entries.length }} entries</span>
      </div>
      <router-link to="/journal/new" class="btn btn-primary">
        <span>＋</span> New Entry
      </router-link>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="search-wrap">
        <Search :size="14" class="search-icon" />
        <input
          v-model="search"
          class="input search-input"
          placeholder="Search entries..."
        />
      </div>
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab"
          class="tab-btn"
          :class="{ active: activeTab === tab }"
          @click="activeTab = tab"
        >{{ tab }}</button>
      </div>
      <select v-model="sortOrder" class="input sort-select">
        <option value="newest">Newest First</option>
        <option value="oldest">Oldest First</option>
        <option value="most_biases">Most Biases</option>
      </select>
    </div>

    <!-- Skeleton loading state -->
    <div v-if="journalStore.loading" class="entry-list">
      <div v-for="n in 3" :key="n" class="entry-card card skeleton-entry">
        <div class="skeleton sk-meta"></div>
        <div class="skeleton sk-title"></div>
        <div class="skeleton sk-excerpt"></div>
        <div class="skeleton sk-tags"></div>
      </div>
    </div>

    <!-- Entry List -->
    <div v-else class="entry-list">
      <div
        v-for="entry in displayEntries"
        :key="entry.id"
        class="entry-card card"
      >
        <div class="entry-top">
          <div class="entry-meta">
            <span class="entry-date">{{ entry.date }}</span>
            <span class="entry-dot">·</span>
            <span class="entry-time">{{ entry.time }}</span>
          </div>
          <div class="entry-mood">{{ entry.mood }}</div>
        </div>

        <div class="entry-body">
          <h3 class="entry-title">{{ entry.title }}</h3>
          <p class="entry-excerpt">{{ entry.content.slice(0, 100) }}{{ entry.content.length > 100 ? '…' : '' }}</p>
        </div>

        <div class="entry-footer">
          <div class="bias-tags">
            <span
              v-for="(bias, i) in entry.biases.slice(0, 3)"
              :key="bias"
              class="badge badge-lavender"
            >{{ bias }}</span>
            <span v-if="entry.biases.length > 3" class="badge badge-lavender">+{{ entry.biases.length - 3 }} more</span>
          </div>
          <div class="entry-actions">
            <router-link :to="`/journal/${entry.id}`" class="btn btn-ghost btn-sm">
              Read <ArrowRight :size="13" />
            </router-link>
            <button class="btn btn-icon" title="More options"><MoreHorizontal :size="16" /></button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!journalStore.loading && displayEntries.length === 0" class="empty-state">
      <div class="empty-icon"><BookOpen :size="40" /></div>
      <p class="empty-text">
        {{ journalStore.entries.length === 0 ? 'No journal entries yet. Start writing!' : 'No entries match your filters.' }}
      </p>
      <router-link v-if="journalStore.entries.length === 0" to="/journal/new" class="btn btn-primary" style="margin-top: 12px;">Write First Entry</router-link>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useJournalStore } from '@/stores/journal.js'
import { Search, ArrowRight, MoreHorizontal, BookOpen } from 'lucide-vue-next'

const journalStore = useJournalStore()

const activeTab = ref('All')
const search = ref('')
const sortOrder = ref('newest')
const tabs = ['All', 'This Week', 'This Month']

onMounted(() => {
  journalStore.fetchEntries({ limit: 50 })
})

const BIAS_NAMES = {
  confirmation_bias: 'Confirmation Bias',
  anchoring_bias: 'Anchoring',
  availability_heuristic: 'Availability',
  sunk_cost_fallacy: 'Sunk Cost',
  overconfidence: 'Overconfidence',
  dunning_kruger: 'Dunning-Kruger',
  halo_effect: 'Halo Effect',
  attribution_error: 'Attribution Error',
  status_quo_bias: 'Status Quo',
  ostrich_effect: 'Ostrich Effect',
  bandwagon_effect: 'Bandwagon Effect',
  framing_effect: 'Framing Effect',
  hindsight_bias: 'Hindsight Bias',
  planning_fallacy: 'Planning Fallacy',
  self_serving_bias: 'Self-Serving Bias',
}

function moodFromSentiment(score) {
  if (score == null) return '📝'
  if (score >= 0.6) return '😊'
  if (score >= 0.3) return '😐'
  if (score >= 0.0) return '😔'
  return '😤'
}

function normalizeEntry(e) {
  const dt = e.created_at ? new Date(e.created_at) : null
  const date = dt ? dt.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : ''
  const time = dt ? dt.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }) : ''
  const biases = (e.detected_biases || []).map(b => {
    const id = b.bias_id || b.bias || ''
    return BIAS_NAMES[id] || id.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
  }).filter(Boolean)
  return {
    id: e.id,
    date,
    time,
    mood: moodFromSentiment(e.sentiment_score),
    title: e.prompt_used || e.content?.slice(0, 60) || 'Untitled entry',
    content: e.content || '',
    biases,
    _raw: e,
  }
}

const normalizedEntries = computed(() =>
  journalStore.entries.map(normalizeEntry)
)

const displayEntries = computed(() => {
  const now = new Date()
  let list = normalizedEntries.value

  if (activeTab.value === 'This Week') {
    const weekAgo = new Date(now - 7 * 24 * 60 * 60 * 1000)
    list = list.filter(e => e._raw.created_at && new Date(e._raw.created_at) >= weekAgo)
  } else if (activeTab.value === 'This Month') {
    const monthAgo = new Date(now - 30 * 24 * 60 * 60 * 1000)
    list = list.filter(e => e._raw.created_at && new Date(e._raw.created_at) >= monthAgo)
  }

  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(e =>
      e.title.toLowerCase().includes(q) || e.content.toLowerCase().includes(q)
    )
  }

  if (sortOrder.value === 'oldest') list = [...list].reverse()
  else if (sortOrder.value === 'most_biases') list = [...list].sort((a, b) => b.biases.length - a.biases.length)

  return list
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

* { font-family: 'Urbanist', sans-serif; }

:root {
  --plum: #352b38;
  --slate: #7e808c;
  --lavender: #dad8f9;
  --ghost: #f4f3f8;
  --lavender-deep: #9b94e8;
  --lavender-mid: #b8b4f0;
  --lavender-soft: #eceaf9;
  --bg: #edeaf4;
  --white: #ffffff;
}

.journal-page { display: flex; flex-direction: column; gap: 28px; }

/* Header */
.page-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.header-left { display: flex; align-items: center; gap: 12px; }
.page-title { font-size: 28px; font-weight: 800; color: var(--plum); margin: 0; }

/* Buttons */
.btn { display: inline-flex; align-items: center; gap: 6px; font-family: 'Urbanist'; font-weight: 600; border: none; cursor: pointer; transition: all 0.18s; outline: none; text-decoration: none; }
.btn-primary { background: var(--plum); color: white; padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-primary:hover { background: #4a3550; transform: translateY(-1px); }
.btn-ghost { background: transparent; color: var(--plum); border: 1.5px solid var(--lavender); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-ghost:hover { background: var(--lavender-soft); }
.btn-sm { padding: 6px 14px !important; font-size: 13px !important; border-radius: 8px !important; }
.btn-icon { background: transparent; border: none; color: var(--slate); padding: 4px 8px; border-radius: 6px; cursor: pointer; }
.btn-icon:hover { background: var(--lavender-soft); color: var(--plum); }

/* Badges */
.badge { font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 99px; display: inline-flex; align-items: center; }
.badge-lavender { background: var(--lavender); color: var(--plum); }

/* Filter Bar */
.filter-bar { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.search-wrap { position: relative; flex: 1; min-width: 200px; max-width: 320px; display: flex; align-items: center; background: white; border: 1.5px solid var(--lavender); border-radius: 10px; padding: 0 14px; gap: 8px; }
.search-icon { color: var(--slate); flex-shrink: 0; }
.search-input { padding-left: 0 !important; border: none !important; box-shadow: none !important; }
.input { font-family: 'Urbanist'; font-size: 14px; color: var(--plum); background: white; border: 1.5px solid var(--lavender); border-radius: 10px; padding: 10px 14px; outline: none; transition: all 0.15s; width: 100%; box-sizing: border-box; }
.input:focus { border-color: var(--lavender-deep); box-shadow: 0 0 0 3px rgba(155,148,232,0.15); }
.sort-select { width: auto; flex-shrink: 0; cursor: pointer; }
.tabs { display: flex; gap: 4px; background: white; border: 1.5px solid var(--lavender); border-radius: 10px; padding: 4px; }
.tab-btn { font-family: 'Urbanist'; font-size: 13px; font-weight: 600; padding: 6px 14px; border-radius: 7px; border: none; background: transparent; color: var(--slate); cursor: pointer; transition: all 0.15s; }
.tab-btn.active { background: var(--plum); color: white; }
.tab-btn:hover:not(.active) { background: var(--lavender-soft); color: var(--plum); }

/* Entry List */
.entry-list { display: flex; flex-direction: column; gap: 16px; }

/* Card */
.card { background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(53,43,56,0.07); padding: 20px; }
.entry-card { display: flex; flex-direction: column; gap: 12px; transition: box-shadow 0.18s, transform 0.18s; }
.entry-card:hover { box-shadow: 0 8px 32px rgba(53,43,56,0.10); transform: translateY(-1px); }

.entry-top { display: flex; align-items: center; justify-content: space-between; }
.entry-meta { display: flex; align-items: center; gap: 6px; }
.entry-date { font-size: 12px; font-weight: 600; color: var(--slate); }
.entry-dot { color: var(--slate); font-size: 12px; }
.entry-time { font-size: 12px; color: var(--slate); }
.entry-mood { font-size: 22px; }

.entry-body { display: flex; flex-direction: column; gap: 6px; }
.entry-title { font-size: 16px; font-weight: 700; color: var(--plum); margin: 0; }
.entry-excerpt { font-size: 13px; color: var(--slate); margin: 0; line-height: 1.5; }

.entry-footer { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; padding-top: 8px; border-top: 1px solid var(--lavender-soft); }
.bias-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.entry-actions { display: flex; gap: 8px; align-items: center; }

/* Empty */
.empty-state { text-align: center; padding: 60px 20px; }
.empty-icon { color: var(--slate); margin-bottom: 12px; display: flex; justify-content: center; }
.empty-text { font-size: 16px; color: var(--slate); }

/* Skeleton */
.skeleton-entry { pointer-events: none; gap: 12px; }
.skeleton {
  background: var(--lavender); border-radius: 8px;
  animation: sk-pulse 1.4s ease-in-out infinite;
}
.sk-meta  { height: 14px; width: 160px; }
.sk-title { height: 18px; width: 55%; }
.sk-excerpt { height: 32px; width: 100%; }
.sk-tags  { height: 22px; width: 220px; }
@keyframes sk-pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 0.3; } }

svg { display: block; }
</style>
