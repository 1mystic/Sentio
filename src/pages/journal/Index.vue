<template>
  <div class="journal-page">

    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">My Journal</h1>
        <span class="badge badge-lavender">12 entries</span>
      </div>
      <router-link to="/journal/new" class="btn btn-primary">
        <span>＋</span> New Entry
      </router-link>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="search-wrap">
        <span class="search-icon">🔍</span>
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
      <select class="input sort-select">
        <option>Newest First</option>
        <option>Oldest First</option>
        <option>Most Biases</option>
      </select>
    </div>

    <!-- Entry List -->
    <div class="entry-list">
      <div
        v-for="entry in filteredEntries"
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
            <router-link :to="`/journal/${entry.id}`" class="btn btn-ghost btn-sm">Read →</router-link>
            <button class="btn btn-icon" title="More options">···</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="filteredEntries.length === 0" class="empty-state">
      <div class="empty-icon">📝</div>
      <p class="empty-text">No entries match your search.</p>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeTab = ref('All')
const search = ref('')
const tabs = ['All', 'This Week', 'This Month']

const entries = ref([
  { id: 1, date: '2026-04-30', time: '9:41 AM', mood: '😊', title: 'Productive morning session', content: 'Had a great planning session this morning. I noticed I kept dismissing Sarah\'s timeline concerns without really considering them.', biases: ['Confirmation Bias', 'Overconfidence'], color: 'green' },
  { id: 2, date: '2026-04-28', time: '11:22 PM', mood: '😐', title: 'That meeting went sideways', content: 'The project review meeting was tough. I found myself anchoring on the original budget estimate even when presented with new information.', biases: ['Anchoring Bias', 'Status Quo'], color: 'blue' },
  { id: 3, date: '2026-04-26', time: '8:15 PM', mood: '😔', title: 'Feeling stuck on the project', content: 'Still working on the same feature. Started wondering if I\'m falling for the sunk cost fallacy — we\'ve already spent 3 weeks on this approach.', biases: ['Sunk Cost Fallacy'], color: 'lavender' },
  { id: 4, date: '2026-04-24', time: '7:00 PM', mood: '😊', title: 'Great conversation with mentor', content: 'My mentor challenged me on my assumption about the user research. I had completely missed the contradictory data from the last usability test.', biases: ['Confirmation Bias', 'Availability Heuristic', 'Halo Effect'], color: 'pink' },
  { id: 5, date: '2026-04-22', time: '10:30 PM', mood: '😤', title: 'Frustrated with team dynamics', content: 'Today was frustrating. I kept attributing the delays to Raj\'s poor planning without considering the external dependencies he was dealing with.', biases: ['Attribution Error'], color: 'yellow' },
  { id: 6, date: '2026-04-20', time: '8:45 PM', mood: '😴', title: 'Low energy reflection', content: 'Not much to write about today. Did notice I was avoiding reading the competitor analysis report because I don\'t want it to challenge our current strategy.', biases: ['Confirmation Bias', 'Ostrich Effect'], color: 'blue' },
])

const filteredEntries = computed(() => {
  return entries.value.filter(e => e.title.toLowerCase().includes(search.value.toLowerCase()))
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
.btn-icon { background: transparent; border: none; color: var(--slate); font-size: 18px; padding: 4px 8px; border-radius: 6px; cursor: pointer; letter-spacing: 1px; }
.btn-icon:hover { background: var(--lavender-soft); }

/* Badges */
.badge { font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 99px; display: inline-flex; align-items: center; }
.badge-lavender { background: var(--lavender); color: var(--plum); }

/* Filter Bar */
.filter-bar { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.search-wrap { position: relative; flex: 1; min-width: 200px; max-width: 320px; }
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); font-size: 14px; pointer-events: none; }
.search-input { padding-left: 36px; }
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
.empty-icon { font-size: 40px; margin-bottom: 12px; }
.empty-text { font-size: 16px; color: var(--slate); }
</style>
