<template>
  <div class="journal-page" @click="closeMenu">

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
        <input v-model="search" class="input search-input" placeholder="Search entries..." />
      </div>
      <div class="tabs">
        <button v-for="tab in tabs" :key="tab" class="tab-btn" :class="{ active: activeTab === tab }" @click="activeTab = tab">{{ tab }}</button>
      </div>
      <select v-model="sortOrder" class="input sort-select">
        <option value="newest">Newest First</option>
        <option value="oldest">Oldest First</option>
        <option value="most_biases">Most Biases</option>
      </select>
    </div>

    <!-- Skeleton loading -->
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
      <div v-for="entry in displayEntries" :key="entry.id" class="entry-card card">
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
          <p class="entry-excerpt">{{ stripMd(entry.content, 110) }}</p>
        </div>

        <div class="entry-footer">
          <div class="bias-tags">
            <span v-for="bias in entry.biases.slice(0, 3)" :key="bias" class="badge badge-lavender">{{ bias }}</span>
            <span v-if="entry.biases.length > 3" class="badge badge-lavender">+{{ entry.biases.length - 3 }} more</span>
          </div>
          <div class="entry-actions">
            <router-link :to="`/journal/${entry.id}`" class="btn btn-ghost btn-sm">
              Read <ArrowRight :size="13" />
            </router-link>

            <!-- ⋯ menu -->
            <div class="menu-wrap" @click.stop>
              <button
                class="btn btn-icon"
                :class="{ active: openMenuId === entry.id }"
                title="More options"
                @click="toggleMenu(entry.id)"
              >
                <MoreHorizontal :size="16" />
              </button>
              <transition name="dropdown">
                <div v-if="openMenuId === entry.id" class="dropdown-menu">
                  <router-link :to="`/journal/${entry.id}`" class="dropdown-item">
                    <Eye :size="14" /> View
                  </router-link>
                  <router-link :to="`/journal/${entry.id}/edit`" class="dropdown-item">
                    <Pencil :size="14" /> Edit
                  </router-link>
                  <div class="dropdown-divider"></div>
                  <button class="dropdown-item danger" @click="confirmDelete(entry)">
                    <Trash2 :size="14" /> Delete
                  </button>
                </div>
              </transition>
            </div>
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

    <!-- Delete confirmation modal -->
    <transition name="fade">
      <div v-if="deleteTarget" class="modal-backdrop" @click="deleteTarget = null">
        <div class="modal-box" @click.stop>
          <div class="modal-icon"><Trash2 :size="24" /></div>
          <h3 class="modal-title">Delete this entry?</h3>
          <p class="modal-body">
            "{{ stripMd(deleteTarget.content, 60) }}"<br/>
            <span class="modal-warning">This action cannot be undone.</span>
          </p>
          <div class="modal-actions">
            <button class="btn btn-ghost" @click="deleteTarget = null">Cancel</button>
            <button class="btn btn-danger" :disabled="deleting" @click="doDelete">
              {{ deleting ? 'Deleting…' : 'Yes, delete' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useJournalStore } from '@/stores/journal.js'
import { Search, ArrowRight, MoreHorizontal, BookOpen, Pencil, Trash2, Eye } from 'lucide-vue-next'

const journalStore = useJournalStore()

const activeTab = ref('All')
const search = ref('')
const sortOrder = ref('newest')
const tabs = ['All', 'This Week', 'This Month']
const openMenuId = ref(null)
const deleteTarget = ref(null)
const deleting = ref(false)

onMounted(() => {
  journalStore.fetchEntries({ limit: 50 })
})

function toggleMenu(id) {
  openMenuId.value = openMenuId.value === id ? null : id
}
function closeMenu() {
  openMenuId.value = null
}
function confirmDelete(entry) {
  deleteTarget.value = entry._raw
  openMenuId.value = null
}
async function doDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  await journalStore.deleteEntry(deleteTarget.value.id)
  deleting.value = false
  deleteTarget.value = null
}

function stripMd(text, maxLen = 110) {
  const plain = text
    .replace(/#{1,6}\s*/g, '')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/_(.+?)_/g, '$1')
    .replace(/`{1,3}[^`]*`{1,3}/g, '')
    .replace(/^\s*[-*>]\s*/gm, '')
    .replace(/\n+/g, ' ')
    .trim()
  return plain.length > maxLen ? plain.slice(0, maxLen) + '…' : plain
}

const BIAS_NAMES = {
  confirmation_bias: 'Confirmation Bias',
  anchoring_bias: 'Anchoring',
  availability_bias: 'Availability',
  sunk_cost_fallacy: 'Sunk Cost',
  overconfidence: 'Overconfidence',
  dunning_kruger: 'Dunning-Kruger',
  halo_effect: 'Halo Effect',
  attribution_error: 'Attribution Error',
  status_quo_bias: 'Status Quo',
  bandwagon_effect: 'Bandwagon',
  all_or_nothing: 'All-or-Nothing',
  catastrophizing: 'Catastrophizing',
  mind_reading: 'Mind Reading',
  overgeneralization: 'Overgeneralization',
  fundamental_attribution: 'Attribution Error',
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
  return { id: e.id, date, time, mood: moodFromSentiment(e.sentiment_score), title: e.prompt_used || e.content?.slice(0, 60) || 'Untitled entry', content: e.content || '', biases, _raw: e }
}

const normalizedEntries = computed(() => journalStore.entries.map(normalizeEntry))

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
    list = list.filter(e => e.title.toLowerCase().includes(q) || e.content.toLowerCase().includes(q))
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
  --plum: #352b38; --slate: #7e808c; --lavender: #dad8f9;
  --ghost: #f4f3f8; --lavender-deep: #9b94e8; --lavender-mid: #b8b4f0;
  --lavender-soft: #eceaf9; --bg: #edeaf4; --white: #ffffff;
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
.btn-icon:hover, .btn-icon.active { background: var(--lavender-soft); color: var(--plum); }
.btn-danger { background: #e53e3e; color: white; padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-danger:hover:not(:disabled) { background: #c53030; }
.btn-danger:disabled { opacity: 0.6; cursor: not-allowed; }

/* Badges */
.badge { font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 99px; display: inline-flex; align-items: center; }
.badge-lavender { background: var(--lavender); color: var(--plum); }

/* Filter */
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

/* Cards */
.entry-list { display: flex; flex-direction: column; gap: 16px; }
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

/* Dropdown */
.menu-wrap { position: relative; }
.dropdown-menu {
  position: absolute; right: 0; top: calc(100% + 6px); z-index: 100;
  background: white; border: 1.5px solid var(--lavender); border-radius: 12px;
  box-shadow: 0 8px 32px rgba(53,43,56,0.14); min-width: 148px; overflow: hidden;
}
.dropdown-item {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 16px; font-size: 13px; font-weight: 600; color: var(--plum);
  cursor: pointer; background: none; border: none; width: 100%;
  text-decoration: none; transition: background 0.13s;
  font-family: 'Urbanist';
}
.dropdown-item:hover { background: var(--lavender-soft); }
.dropdown-item.danger { color: #e53e3e; }
.dropdown-item.danger:hover { background: #fff5f5; }
.dropdown-divider { height: 1px; background: var(--lavender-soft); margin: 4px 0; }

/* Dropdown animation */
.dropdown-enter-active, .dropdown-leave-active { transition: opacity 0.15s, transform 0.15s; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-6px); }

/* Delete modal */
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(53,43,56,0.45); backdrop-filter: blur(3px);
  display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px;
}
.modal-box {
  background: white; border-radius: 20px; padding: 32px; max-width: 420px; width: 100%;
  box-shadow: 0 24px 64px rgba(53,43,56,0.18); text-align: center;
}
.modal-icon { color: #e53e3e; margin-bottom: 12px; display: flex; justify-content: center; }
.modal-title { font-size: 20px; font-weight: 800; color: var(--plum); margin: 0 0 10px; }
.modal-body { font-size: 14px; color: var(--slate); line-height: 1.6; margin: 0 0 24px; }
.modal-warning { font-size: 12px; color: #e53e3e; font-weight: 600; }
.modal-actions { display: flex; gap: 10px; justify-content: center; }

/* Fade */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* Empty */
.empty-state { text-align: center; padding: 60px 20px; }
.empty-icon { color: var(--slate); margin-bottom: 12px; display: flex; justify-content: center; }
.empty-text { font-size: 16px; color: var(--slate); }

/* Skeleton */
.skeleton-entry { pointer-events: none; gap: 12px; }
.skeleton { background: var(--lavender); border-radius: 8px; animation: sk-pulse 1.4s ease-in-out infinite; }
.sk-meta  { height: 14px; width: 160px; }
.sk-title { height: 18px; width: 55%; }
.sk-excerpt { height: 32px; width: 100%; }
.sk-tags  { height: 22px; width: 220px; }
@keyframes sk-pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 0.3; } }

svg { display: block; }

@media (max-width: 640px) {
  .journal-page { gap: 16px; }
  .page-title { font-size: 22px; }
  .filter-bar { flex-direction: column; align-items: stretch; gap: 8px; }
  .search-wrap { min-width: 0; max-width: 100%; }
  .tabs { justify-content: center; }
  .sort-select { width: 100%; }
  .card { padding: 14px; }
}
</style>
