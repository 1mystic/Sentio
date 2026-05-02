<template>
  <div class="progress-page">

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
        <div class="stat-icon">{{ stat.icon }}</div>
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
        <div class="freq-list">
          <div v-for="b in biasFrequency" :key="b.name" class="freq-row">
            <div class="freq-name">{{ b.name }}</div>
            <div class="freq-bar-track">
              <div class="freq-bar-fill" :style="{ width: (b.count / maxFreq * 100) + '%' }"></div>
            </div>
            <span class="freq-count">{{ b.count }}×</span>
          </div>
        </div>
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
              <div class="timeline-title">{{ m.emoji }} {{ m.title }}</div>
              <div class="timeline-time">{{ m.time }}</div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Recommended Next Steps -->
    <div class="next-steps">
      <div class="section-header">
        <span class="section-title">Recommended Next Steps</span>
      </div>
      <div class="rec-grid">
        <div v-for="r in recommendations" :key="r.title" class="rec-card card">
          <div class="rec-emoji">{{ r.emoji }}</div>
          <div class="rec-info">
            <div class="rec-title">{{ r.title }}</div>
            <div class="rec-desc">{{ r.desc }}</div>
          </div>
          <router-link :to="r.link" class="btn btn-secondary btn-sm">{{ r.cta }}</router-link>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeTime = ref('Week')
const timeTabs = ['Week', 'Month', 'All Time']

const stats = ref([
  { icon: '📝', value: '12', label: 'Total Entries', change: '+3 this week', changeType: 'up' },
  { icon: '🧠', value: '3', label: 'Assessments Done', change: '+1 this month', changeType: 'up' },
  { icon: '🔍', value: '7', label: 'Biases Identified', change: '+2 this week', changeType: 'up' },
  { icon: '💡', value: '68/100', label: 'Insight Score', change: '+5 pts', changeType: 'up' },
])

const activityData = ref([
  { label: 'Mon', count: 1 },
  { label: 'Tue', count: 3 },
  { label: 'Wed', count: 2 },
  { label: 'Thu', count: 4 },
  { label: 'Fri', count: 2 },
  { label: 'Sat', count: 1 },
  { label: 'Sun', count: 3 },
])

const maxCount = computed(() => Math.max(...activityData.value.map(d => d.count)))
const yAxis = [5, 4, 3, 2, 1, 0]

const biasFrequency = ref([
  { name: 'Confirmation Bias', count: 8 },
  { name: 'Overconfidence', count: 5 },
  { name: 'Anchoring', count: 4 },
  { name: 'Sunk Cost Fallacy', count: 3 },
  { name: 'Attribution Error', count: 2 },
  { name: 'Halo Effect', count: 2 },
])

const maxFreq = computed(() => Math.max(...biasFrequency.value.map(b => b.count)))

const milestones = ref([
  { emoji: '🎉', title: 'Completed first assessment', time: 'Week 1', complete: true },
  { emoji: '📝', title: '10th journal entry', time: 'Week 2', complete: true },
  { emoji: '🧠', title: 'Identified 5 unique biases', time: 'Week 3', complete: true },
  { emoji: '🔥', title: '7-day streak achieved', time: 'Week 4', complete: false },
])

const recommendations = ref([
  { emoji: '📔', title: 'Write Today\'s Entry', desc: 'Keep your streak going — reflect on something that happened today.', link: '/journal/new', cta: 'Write Now' },
  { emoji: '🧠', title: 'Take an Assessment', desc: 'You have 5 assessments waiting. Start with Decision Making Patterns.', link: '/assessments', cta: 'Start' },
  { emoji: '💬', title: 'Explore with AI Guide', desc: 'Discuss your top bias pattern — Confirmation Bias — with Sentio AI.', link: '/ai-guide', cta: 'Open Chat' },
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
.stat-icon { font-size: 22px; }
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
.timeline-title { font-size: 14px; font-weight: 600; color: var(--plum); }
.timeline-time { font-size: 12px; color: var(--slate); margin-top: 2px; }

/* Rec Grid */
.next-steps {}
.rec-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }
.rec-card { display: flex; flex-direction: column; gap: 12px; }
.rec-emoji { font-size: 28px; }
.rec-info { flex: 1; }
.rec-title { font-size: 15px; font-weight: 700; color: var(--plum); margin-bottom: 4px; }
.rec-desc { font-size: 13px; color: var(--slate); line-height: 1.5; }
</style>
