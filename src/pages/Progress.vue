<template>
  <div class="progress-page">

    <!-- Skeleton while loading -->
    <template v-if="journalStore.loading && !journalStore.entries.length">
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading your progress…</p>
      </div>
    </template>

    <template v-else>
    <!-- Page Header + Time Filter -->
    <div class="page-header">
      <h1 class="page-title">Your Progress</h1>
      <div class="time-tabs">
        <button
          v-for="t in timeTabs"
          :key="t"
          class="tab-btn"
          :class="{ active: activeTime === t }"
          @click="activeTime = t"
        >{{ t }}</button>
      </div>
    </div>

    <!-- Stat Cards Row -->
    <div class="stats-grid">
      <div v-for="stat in stats" :key="stat.label" class="stat-card card">
        <div class="stat-icon"><component :is="stat.icon" :size="22" /></div>
        <div class="stat-value">{{ stat.value }}</div>
        <div class="stat-label">{{ stat.label }}</div>
        <div class="stat-change" :class="stat.changeType">{{ stat.change }}</div>
      </div>
    </div>

    <!-- Activity Chart -->
    <div class="card chart-card">
      <div class="section-header">
        <span class="section-title">Activity Over Time</span>
        <span class="chart-label">Journal entries per day</span>
      </div>
      <div class="bar-chart">
        <div class="chart-bars">
          <div
            v-for="day in activityData"
            :key="day.label"
            class="bar-col"
          >
            <div class="bar-wrap" :title="`${day.count} entries`">
              <div
                class="bar"
                :style="{ height: (day.count / maxCount * 120) + 'px' }"
                :class="{ active: day.label === 'Thu' }"
              ></div>
            </div>
            <span class="bar-label">{{ day.label }}</span>
          </div>
        </div>
        <div class="chart-y-axis">
          <span v-for="y in yAxis" :key="y" class="y-label">{{ y }}</span>
        </div>
      </div>
    </div>

    <!-- Two-col charts -->
    <div class="two-col">

      <!-- Bias Frequency -->
      <div class="card bias-freq-card">
        <div class="section-header">
          <span class="section-title">Bias Frequency</span>
        </div>
        <div v-if="biasFrequency.length" class="freq-list">
          <div v-for="b in biasFrequency" :key="b.name" class="freq-row">
            <div class="freq-name">{{ b.name }}</div>
            <div class="freq-bar-track">
              <div class="freq-bar-fill" :style="{ width: (b.count / maxFreq * 100) + '%' }"></div>
            </div>
            <span class="freq-count">{{ b.count }}×</span>
          </div>
        </div>
        <div v-else class="empty-section">Write journal entries to see your bias patterns here.</div>
      </div>

      <!-- Learning Journey -->
      <div class="card journey-card">
        <div class="section-header">
          <span class="section-title">Learning Journey</span>
        </div>
        <div class="timeline">
          <div v-for="(m, i) in milestones" :key="m.title" class="timeline-item">
            <div class="timeline-left">
              <div class="timeline-dot" :class="{ complete: m.complete }"></div>
              <div v-if="i < milestones.length - 1" class="timeline-line"></div>
            </div>
            <div class="timeline-content">
              <div class="timeline-title"><component :is="m.icon" :size="14" class="timeline-icon" /> {{ m.title }}</div>
              <div class="timeline-time">{{ m.time }}</div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Themes Section -->
    <div id="themes" class="card" ref="themesSection">
      <div class="section-header">
        <span class="section-title">Explore Themes</span>
        <span class="chart-label">Topics you write about most</span>
      </div>
      <div v-if="topThemes.length" class="themes-wrap">
        <div v-for="t in topThemes" :key="t.theme" class="theme-row">
          <span class="theme-tag">{{ t.theme }}</span>
          <div class="freq-bar-track">
            <div class="freq-bar-fill theme-fill" :style="{ width: (t.count / topThemes[0].count * 100) + '%' }"></div>
          </div>
          <span class="freq-count">{{ t.count }}×</span>
        </div>
      </div>
      <div v-else class="empty-section">
        No themes detected yet — write journal entries and our AI will extract recurring topics automatically.
      </div>
    </div>

    <!-- Mood / Sentiment Section -->
    <div id="mood" class="card" ref="moodSection">
      <div class="section-header">
        <span class="section-title">Explore Mood</span>
        <span class="chart-label">Emotional tone of your recent entries</span>
      </div>
      <div v-if="moodData.length" class="mood-list">
        <div v-for="entry in moodData" :key="entry.id" class="mood-row">
          <span class="mood-emoji">{{ entry.emoji }}</span>
          <div class="mood-meta">
            <div class="mood-date">{{ entry.date }}</div>
            <div class="mood-excerpt">{{ entry.excerpt }}</div>
          </div>
          <div class="mood-bar-wrap">
            <div class="mood-bar" :style="{ width: entry.barWidth + '%', background: entry.color }"></div>
            <span class="mood-score">{{ entry.label }}</span>
          </div>
        </div>
      </div>
      <div v-else class="empty-section">
        No mood data yet — write journal entries to track your emotional patterns over time.
      </div>
    </div>

    <!-- Recommended Next Steps -->
    <div class="next-steps">
      <div class="section-header">
        <span class="section-title">Recommended Next Steps</span>
      </div>
      <div class="rec-grid">
        <div v-for="r in recommendations" :key="r.title" class="rec-card card">
          <div class="rec-icon"><component :is="r.icon" :size="28" /></div>
          <div class="rec-info">
            <div class="rec-title">{{ r.title }}</div>
            <div class="rec-desc">{{ r.desc }}</div>
          </div>
          <router-link :to="r.link" class="btn btn-secondary btn-sm">{{ r.cta }}</router-link>
        </div>
      </div>
    </div>

    </template><!-- end v-else -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useInsightsStore } from '@/stores/insights.js'
import { useJournalStore } from '@/stores/journal.js'
import { useAssessmentStore } from '@/stores/assessment.js'
import { assessmentsApi } from '@/api/assessments.js'
import { journalsApi } from '@/api/journals.js'
import { BookOpen, Brain, Search, Lightbulb, PartyPopper, Flame, MessageSquare, TrendingUp } from 'lucide-vue-next'

const route = useRoute()
const insightsStore = useInsightsStore()
const journalStore  = useJournalStore()
const assessStore   = useAssessmentStore()

const activeTime = ref('Week')
const timeTabs = ['Week', 'Month', 'All Time']

const topThemes = ref([])
const userResultsMap = ref({})

const themesSection = ref(null)
const moodSection = ref(null)

onMounted(async () => {
  await Promise.all([
    journalStore.fetchEntries({ limit: 100 }),
    insightsStore.fetchAll(),
    assessStore.fetchList(),
  ])
  // Fetch themes from API
  try {
    const res = await journalsApi.themes()
    topThemes.value = res.data || []
  } catch {}
  // Fetch user assessment results for accurate completion count
  try {
    const res = await assessmentsApi.userResults()
    const map = {}
    for (const r of (res.data || [])) map[r.assessment_id] = r
    userResultsMap.value = map
  } catch {}

  // Scroll to section if tab query param is present
  await nextTick()
  if (route.query.tab === 'themes' && themesSection.value) {
    themesSection.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } else if (route.query.tab === 'mood' && moodSection.value) {
    moodSection.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
})

// --- Helpers ---
function entriesInWindow(entries, days) {
  const cutoff = Date.now() - days * 86400000
  return entries.filter(e => new Date(e.created_at).getTime() >= cutoff)
}

const windowDays = computed(() => activeTime.value === 'Week' ? 7 : activeTime.value === 'Month' ? 30 : 9999)
const windowEntries = computed(() => entriesInWindow(journalStore.entries, windowDays.value))

// --- Stats ---
const stats = computed(() => {
  const biasScores = insightsStore.biasFingerprint?.bias_scores || {}
  const biasCount  = Object.values(biasScores).filter(v => v > 0.2).length
  const entryCount = windowEntries.value.length
  const doneCount  = Object.keys(userResultsMap.value).length

  return [
    { icon: BookOpen,   value: entryCount || '0', label: 'Journal Entries',   change: activeTime.value, changeType: 'up' },
    { icon: Brain,      value: doneCount  || '0', label: 'Assessments Done',  change: 'completed',      changeType: 'up' },
    { icon: Search,     value: biasCount  || '0', label: 'Biases Identified', change: 'from journals',  changeType: 'up' },
    { icon: Lightbulb,  value: insightsStore.weeklyInsights.length || '0', label: 'Weekly Insights', change: 'this week', changeType: 'up' },
  ]
})

// --- Activity bar chart (by day of week for Week view, by week for Month) ---
const activityData = computed(() => {
  if (activeTime.value === 'Week') {
    const days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
    const counts = Object.fromEntries(days.map(d => [d, 0]))
    for (const e of windowEntries.value) {
      const day = days[new Date(e.created_at).getDay()]
      counts[day]++
    }
    return days.map(d => ({ label: d, count: counts[d] }))
  }
  // Month view: group by week number
  const weeks = ['Wk1','Wk2','Wk3','Wk4']
  const counts = { Wk1:0, Wk2:0, Wk3:0, Wk4:0 }
  for (const e of windowEntries.value) {
    const day = (Date.now() - new Date(e.created_at).getTime()) / 86400000
    const wk = Math.min(3, Math.floor(day / 7))
    counts[weeks[wk]]++
  }
  return weeks.map(w => ({ label: w, count: counts[w] }))
})

const maxCount = computed(() => Math.max(1, ...activityData.value.map(d => d.count)))
const yAxis = computed(() => {
  const m = maxCount.value
  return [m, Math.ceil(m*0.75), Math.ceil(m*0.5), Math.ceil(m*0.25), 1, 0]
})

// --- Bias frequency from bias_scores ---
const biasFrequency = computed(() => {
  const scores = insightsStore.biasFingerprint?.bias_scores || {}
  return Object.entries(scores)
    .map(([k, v]) => ({
      name: k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
      count: Math.round(v * 10),
    }))
    .filter(b => b.count > 0)
    .sort((a, b) => b.count - a.count)
    .slice(0, 6)
})

const maxFreq = computed(() => Math.max(1, ...biasFrequency.value.map(b => b.count)))

// --- Mood data from journal sentiment scores ---
const moodData = computed(() => {
  return journalStore.entries
    .filter(e => e.sentiment_score != null)
    .slice(0, 10)
    .map(e => {
      const score = e.sentiment_score
      const date = new Date(e.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })
      const excerpt = (e.content || '').slice(0, 60)
      let emoji, label, color, barWidth
      if (score >= 0.5)       { emoji = '😊'; label = 'Positive';  color = '#88c9a0'; barWidth = 50 + score * 50 }
      else if (score >= 0.1)  { emoji = '🙂'; label = 'Upbeat';    color = '#a8d8b0'; barWidth = 40 + score * 60 }
      else if (score >= -0.1) { emoji = '😐'; label = 'Neutral';   color = '#b8b4f0'; barWidth = 50 }
      else if (score >= -0.4) { emoji = '😔'; label = 'Low';       color = '#e8c56a'; barWidth = 50 + score * 40 }
      else                    { emoji = '😤'; label = 'Difficult';  color = '#e88fa0'; barWidth = 20 }
      return { id: e.id, date, excerpt, emoji, label, color, barWidth: Math.max(8, Math.round(barWidth)) }
    })
})

// --- Milestones ---
const milestones = computed(() => {
  const entries    = journalStore.entries
  const biasN      = Object.values(insightsStore.biasFingerprint?.bias_scores || {}).filter(v => v > 0.2).length
  const doneCount  = Object.keys(userResultsMap.value).length
  return [
    { icon: BookOpen,   title: 'First journal entry',     time: entries.length >= 1  ? 'Completed' : 'Pending', complete: entries.length >= 1 },
    { icon: Brain,      title: 'First assessment done',   time: doneCount >= 1 ? 'Completed' : 'Pending',        complete: doneCount >= 1 },
    { icon: Search,     title: '5 biases identified',     time: biasN >= 5  ? 'Completed' : `${biasN}/5`,        complete: biasN >= 5 },
    { icon: BookOpen,   title: '10 journal entries',      time: entries.length >= 10 ? 'Completed' : `${entries.length}/10`, complete: entries.length >= 10 },
    { icon: Brain,      title: '3 assessments done',      time: doneCount >= 3 ? 'Completed' : `${doneCount}/3`, complete: doneCount >= 3 },
  ]
})

const recommendations = ref([
  { icon: BookOpen,     title: "Write Today's Entry",      desc: 'Keep your streak going — reflect on something that happened today.', link: '/journal/new', cta: 'Write Now' },
  { icon: Brain,        title: 'Take an Assessment',       desc: 'Discover your cognitive patterns with a validated assessment.',        link: '/assessments', cta: 'Start' },
  { icon: MessageSquare,title: 'Explore with AI Guide',    desc: 'Discuss your top bias pattern with Sentio AI.',                       link: '/ai-guide',    cta: 'Open Chat' },
])
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.progress-page { display: flex; flex-direction: column; gap: 28px; }

/* Buttons */
.btn { display: inline-flex; align-items: center; gap: 6px; font-family: 'Urbanist'; font-weight: 600; border: none; cursor: pointer; transition: all 0.18s; outline: none; text-decoration: none; }
.btn-secondary { background: var(--lavender); color: var(--plum); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-secondary:hover { background: var(--lavender-mid); }
.btn-sm { padding: 6px 14px !important; font-size: 13px !important; border-radius: 8px !important; }

.card { background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(53,43,56,0.07); padding: 24px; }

/* Header */
.page-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.page-title { font-size: 28px; font-weight: 800; color: var(--plum); margin: 0; }
.time-tabs { display: flex; gap: 4px; background: white; border: 1.5px solid var(--lavender); border-radius: 10px; padding: 4px; }
.tab-btn { font-family: 'Urbanist'; font-size: 13px; font-weight: 600; padding: 6px 14px; border-radius: 7px; border: none; background: transparent; color: var(--slate); cursor: pointer; transition: all 0.15s; }
.tab-btn.active { background: var(--plum); color: white; }
.tab-btn:hover:not(.active) { background: var(--lavender-soft); color: var(--plum); }

/* Stats */
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
@media (max-width: 800px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
.stat-card { display: flex; flex-direction: column; gap: 6px; padding: 20px; }
.stat-icon { color: var(--lavender-deep); display: flex; align-items: center; }
.stat-value { font-size: 24px; font-weight: 800; color: var(--plum); }
.stat-label { font-size: 12px; color: var(--slate); font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.stat-change { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 99px; display: inline-flex; width: fit-content; }
.stat-change.up { background: #d1fae5; color: #059669; }

/* Section Header */
.section-header { display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; border-bottom: 1.5px solid var(--lavender-soft); margin-bottom: 20px; }
.section-title { font-size: 16px; font-weight: 700; color: var(--plum); }
.chart-label { font-size: 12px; color: var(--slate); }

/* Bar Chart */
.bar-chart { display: flex; gap: 16px; align-items: flex-end; }
.chart-bars { flex: 1; display: flex; align-items: flex-end; gap: 12px; height: 140px; justify-content: space-around; }
.bar-col { display: flex; flex-direction: column; align-items: center; gap: 6px; flex: 1; }
.bar-wrap { flex: 1; display: flex; align-items: flex-end; width: 100%; justify-content: center; height: 120px; }
.bar { width: 32px; background: var(--lavender); border-radius: 6px 6px 0 0; transition: all 0.3s; min-height: 4px; }
.bar:hover { background: var(--lavender-deep); opacity: 0.9; }
.bar.active { background: var(--lavender-deep); }
.bar-label { font-size: 12px; color: var(--slate); font-weight: 600; }
.chart-y-axis { display: flex; flex-direction: column; justify-content: space-between; height: 140px; align-items: flex-end; padding-right: 4px; }
.y-label { font-size: 11px; color: var(--slate); }

/* Two Col */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 700px) { .two-col { grid-template-columns: 1fr; } }

/* Bias Freq */
.freq-list { display: flex; flex-direction: column; gap: 12px; }
.freq-row { display: flex; align-items: center; gap: 12px; }
.freq-name { width: 140px; font-size: 13px; font-weight: 600; color: var(--plum); flex-shrink: 0; }
.freq-bar-track { flex: 1; height: 8px; background: var(--lavender-soft); border-radius: 99px; overflow: hidden; }
.freq-bar-fill { height: 100%; border-radius: 99px; background: linear-gradient(90deg, var(--lavender-deep), var(--lavender-mid)); transition: width 0.6s; }
.freq-count { font-size: 12px; font-weight: 700; color: var(--slate); width: 24px; text-align: right; }

/* Timeline */
.timeline { display: flex; flex-direction: column; gap: 0; }
.timeline-item { display: flex; gap: 16px; }
.timeline-left { display: flex; flex-direction: column; align-items: center; }
.timeline-dot { width: 12px; height: 12px; border-radius: 50%; background: var(--lavender); border: 2px solid var(--lavender-mid); flex-shrink: 0; margin-top: 4px; transition: all 0.2s; }
.timeline-dot.complete { background: var(--lavender-deep); border-color: var(--lavender-deep); }
.timeline-line { width: 2px; flex: 1; background: var(--lavender-soft); min-height: 24px; margin: 4px 0; }
.timeline-content { flex: 1; padding-bottom: 20px; }
.timeline-title { font-size: 14px; font-weight: 600; color: var(--plum); display: flex; align-items: center; gap: 6px; }
.timeline-icon { flex-shrink: 0; color: var(--lavender-deep); }
.timeline-time { font-size: 12px; color: var(--slate); margin-top: 2px; }

/* Rec Grid */
.next-steps {}
.rec-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }
.rec-card { display: flex; flex-direction: column; gap: 12px; }
.rec-icon { color: var(--lavender-deep); display: flex; align-items: center; }
.rec-info { flex: 1; }
.rec-title { font-size: 15px; font-weight: 700; color: var(--plum); margin-bottom: 4px; }
.rec-desc { font-size: 13px; color: var(--slate); line-height: 1.5; }

/* Themes section */
.themes-wrap { display: flex; flex-direction: column; gap: 12px; }
.theme-row { display: flex; align-items: center; gap: 12px; }
.theme-tag { font-size: 13px; font-weight: 700; color: var(--plum); width: 140px; flex-shrink: 0; text-transform: capitalize; }
.theme-fill { background: linear-gradient(90deg, #9b94e8, #b8b4f0); }

/* Mood section */
.mood-list { display: flex; flex-direction: column; gap: 14px; }
.mood-row { display: flex; align-items: center; gap: 14px; padding: 10px 0; border-bottom: 1px solid var(--lavender-soft); }
.mood-row:last-child { border-bottom: none; }
.mood-emoji { font-size: 22px; flex-shrink: 0; width: 28px; text-align: center; }
.mood-meta { flex: 1; min-width: 0; }
.mood-date { font-size: 12px; font-weight: 700; color: var(--plum); }
.mood-excerpt { font-size: 12px; color: var(--slate); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mood-bar-wrap { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.mood-bar { height: 8px; border-radius: 99px; transition: width 0.5s; }
.mood-score { font-size: 11px; font-weight: 700; color: var(--slate); width: 52px; }

/* Empty state for sections */
.empty-section { font-size: 14px; color: var(--slate); padding: 20px 0; text-align: center; font-style: italic; line-height: 1.6; }

/* Loading */
.loading-state { display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 80px 0; color: var(--slate); }
.spinner { width: 28px; height: 28px; border-radius: 50%; border: 3px solid var(--lavender); border-top-color: var(--lavender-deep); animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
