<template>
  <div class="dashboard">

    <!-- Loading overlay while insights load -->
    <div v-if="insightsStore.loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Loading your insights...</p>
    </div>

    <!-- Section 1: Stat Cards -->
    <section class="stats-grid">
      <div
        v-for="stat in stats"
        :key="stat.label"
        class="stat-card"
        :class="stat.variant"
      >
        <div class="stat-label">{{ stat.label }}</div>
        <div class="stat-value">{{ stat.value }}</div>
        <div
          v-if="stat.dir === 'up'"
          class="stat-change up"
        >
          <component :is="stat.changeIcon" v-if="stat.changeIcon" :size="11" />
          {{ stat.changeText }}
        </div>
        <div
          v-else
          class="stat-change"
          style="background: rgba(251,191,36,0.15); color: #92400e;"
        >
          <component :is="stat.changeIcon" v-if="stat.changeIcon" :size="11" />
          {{ stat.changeText }}
        </div>
      </div>
    </section>

    <!-- Section 2: Bias Fingerprint + Archetype -->
    <section class="two-col">

      <!-- Bias Fingerprint (60%) -->
      <div class="card fingerprint-card">
        <div class="section-header">
          <span class="section-title">Bias Fingerprint</span>
          <span class="section-tag">RADAR</span>
        </div>
        <div class="radar-wrap">
          <svg :viewBox="`0 0 ${svgSize} ${svgSize}`" :width="svgSize" :height="svgSize" class="radar-svg">
            <!-- Background grid rings -->
            <polygon
              v-for="ring in rings"
              :key="ring"
              :points="hexPoints(ring)"
              fill="none"
              stroke="#dad8f9"
              stroke-width="1"
            />
            <!-- Axis lines -->
            <line
              v-for="(pt, i) in outerPoints"
              :key="'axis-' + i"
              :x1="cx"
              :y1="cy"
              :x2="pt.x"
              :y2="pt.y"
              stroke="#dad8f9"
              stroke-width="1"
            />
            <!-- Data polygon -->
            <polygon
              :points="dataPolygonPoints"
              fill="rgba(155,148,232,0.18)"
              stroke="#9b94e8"
              stroke-width="2"
              stroke-linejoin="round"
            />
            <!-- Data dots -->
            <circle
              v-for="(pt, i) in dataPoints"
              :key="'dot-' + i"
              :cx="pt.x"
              :cy="pt.y"
              r="5"
              fill="#9b94e8"
              stroke="white"
              stroke-width="2"
            />
            <!-- Axis labels -->
            <text
              v-for="(label, i) in axisLabels"
              :key="'label-' + i"
              :x="labelPoints[i].x"
              :y="labelPoints[i].y"
              :text-anchor="labelAnchors[i]"
              dominant-baseline="middle"
              font-family="'Urbanist', sans-serif"
              font-size="11"
              font-weight="600"
              fill="#7e808c"
            >{{ label }}</text>
          </svg>
        </div>

        <!-- Legend -->
        <div class="radar-legend">
          <div v-for="(label, i) in axisLabels" :key="label" class="legend-item">
            <span class="legend-dot" :style="{ background: legendColors[i] }"></span>
            <span class="legend-text">{{ label }}</span>
          </div>
        </div>

        <div class="card-footer">
          <button class="btn btn-ghost btn-sm" @click="router.push('/explore')">
            View Full Analysis
          </button>
        </div>
      </div>

      <!-- Archetype (40%) -->
      <div class="card archetype-card">
        <div class="archetype-emoji-wrap">
          <span class="archetype-emoji">{{ archetype ? '🧠' : '✨' }}</span>
        </div>
        <div class="archetype-title">{{ archetype || 'Your Archetype' }}</div>
        <span class="badge badge-lavender" style="margin-bottom: 14px; display: inline-block;">
          {{ archetype ? 'Cognitive Style' : 'Pending' }}
        </span>
        <p class="archetype-desc">
          {{ archetype
            ? 'Your cognitive archetype is based on your assessment results and journaling patterns.'
            : 'Complete assessments and journal entries to unlock your personalised cognitive archetype.' }}
        </p>
        <div class="trait-list">
          <span class="badge badge-lavender" v-for="trait in traits" :key="trait">{{ trait }}</span>
        </div>
        <div class="card-footer" style="margin-top: 24px;">
          <button class="btn btn-primary btn-sm" @click="router.push('/assessments')">
            {{ archetype ? 'Explore Archetype' : 'Take Assessment' }}
          </button>
        </div>
      </div>

    </section>

    <!-- Section 3: Recent Insights -->
    <section>
      <div class="section-header">
        <span class="section-title">Recent Insights</span>
        <span class="section-tag">AI-POWERED</span>
      </div>

      <div class="ai-container" style="margin-bottom: 24px;">
        <div class="ai-label"><Sparkles :size="12" /> Sentio AI</div>
        <div class="ai-prompt">Based on your recent journal entries…</div>
        <div class="ai-response">
          <template v-if="insightsStore.weeklyInsights.length">
            <span v-for="(ins, i) in insightsStore.weeklyInsights.slice(0,2)" :key="i">{{ ins.text }} </span>
          </template>
          <template v-else>
            Write journal entries to unlock AI-powered insights about your cognitive patterns.
          </template>
        </div>
      </div>

      <div class="insights-grid">
        <div v-for="insight in insights" :key="insight.title" class="insight-card">
          <div class="insight-top">
            <span class="badge" :class="`badge-${insight.badgeColor}`">{{ insight.badgeLabel }}</span>
          </div>
          <div class="insight-title">{{ insight.title }}</div>
          <div class="insight-desc">{{ insight.desc }}</div>
          <div class="card-footer" style="margin-top: 14px;">
            <button class="btn btn-ghost btn-sm" @click="router.push(insight.link || '/journal')">
              Explore <ArrowRight :size="13" />
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 4: Quick Actions + Recommendations -->
    <section class="two-col-balanced">

      <!-- Quick Actions -->
      <div class="card">
        <div class="section-header">
          <span class="section-title">Quick Actions</span>
        </div>
        <div class="quick-actions-list">
          <div
            v-for="action in quickActions"
            :key="action.label"
            class="quick-action-row"
            @click="router.push(action.path)"
          >
            <component :is="action.icon" :size="18" class="quick-action-icon" />
            <span class="quick-action-label">{{ action.label }}</span>
            <ArrowRight :size="14" class="quick-action-arrow" />
          </div>
        </div>
      </div>

      <!-- Recommended For You -->
      <div class="card">
        <div class="section-header">
          <span class="section-title">Recommended for You</span>
        </div>
        <div class="recommendations-list">
          <div v-for="rec in recommendations" :key="rec.name" class="rec-card">
            <div class="rec-top">
              <div class="rec-icon-wrap">
                <component :is="rec.icon" :size="22" class="rec-icon" />
              </div>
              <div class="rec-info">
                <div class="rec-name">{{ rec.name }}</div>
                <span class="badge" :class="`badge-${rec.badgeColor}`" style="font-size: 10px;">{{ rec.category }}</span>
              </div>
            </div>
            <button class="btn btn-secondary btn-sm" style="margin-top: 10px; width: 100%;" @click="router.push(rec.path || '/explore')">
              Start Learning <ArrowRight :size="13" />
            </button>
          </div>
        </div>
      </div>

    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'
import { useInsightsStore } from '@/stores/insights.js'
import { useJournalStore } from '@/stores/journal.js'
import {
  Sparkles, ArrowRight, TrendingUp, Flame,
  BookOpen, ClipboardList, Search, MessageSquare, Brain, BarChart2, Lightbulb
} from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()
const insightsStore = useInsightsStore()
const journalStore = useJournalStore()

onMounted(async () => {
  await Promise.all([
    insightsStore.fetchAll(),
    journalStore.fetchEntries({ limit: 30 }),
  ])
})

// --- Stats (computed from real data) ---
function computeStreak(entries) {
  if (!entries.length) return 0
  const sorted = [...entries].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  let streak = 0
  let cursor = new Date(); cursor.setHours(0, 0, 0, 0)
  const seen = new Set()
  for (const e of sorted) {
    const d = new Date(e.created_at); d.setHours(0, 0, 0, 0)
    const key = d.toDateString()
    if (seen.has(key)) continue
    const diff = Math.round((cursor - d) / 86400000)
    if (diff <= 1) { streak++; seen.add(key); cursor = d }
    else break
  }
  return streak
}

const stats = computed(() => {
  const biasScores = insightsStore.biasFingerprint?.bias_scores || {}
  const biasCount = Object.keys(biasScores).filter(k => biasScores[k] > 0).length
  const entryCount = journalStore.entries.length
  const streak = computeStreak(journalStore.entries)
  const insightCount = insightsStore.weeklyInsights.length

  return [
    { label: 'BIASES IDENTIFIED', value: biasCount.toString(), changeText: 'from your journals', changeIcon: TrendingUp, dir: 'up', variant: 'blue' },
    { label: 'JOURNAL ENTRIES', value: entryCount || '—', changeText: 'total entries', changeIcon: TrendingUp, dir: 'up', variant: 'lavender' },
    { label: 'CURRENT STREAK', value: streak || '—', changeText: 'days in a row', changeIcon: Flame, dir: 'up', variant: 'pink' },
    { label: 'WEEKLY INSIGHTS', value: insightCount || '—', changeText: 'this week', changeIcon: TrendingUp, dir: 'up', variant: 'green' },
  ]
})

// --- Archetype ---
const archetype = computed(() => insightsStore.biasFingerprint?.archetype || null)

const ARCHETYPE_TRAITS = {
  'The Conviction Keeper': ['Tenacious', 'Pattern-seeking', 'Committed', 'Selective listener'],
  'The Anchor':            ['Methodical', 'Reference-reliant', 'Structured', 'Slow to revise'],
  'The Storyteller':       ['Vivid thinker', 'Experience-driven', 'Memorable', 'Availability-led'],
  'The Visionary':         ['Confident', 'Bold', 'Ambitious', 'Occasionally overestimates'],
  'The Harmonizer':        ['Empathetic', 'Group-minded', 'Agreeable', 'Consensus-seeking'],
  'The Judge':             ['Decisive', 'Person-focused', 'Direct', 'Attribution-prone'],
  'The Investor':          ['Persistent', 'Committed', 'Long-term focused', 'Loss-averse'],
  'The Explorer':          ['Curious', 'Confident learner', 'Self-assessing', 'Growth-oriented'],
  'The Traditionalist':    ['Stable', 'Risk-averse', 'Reliable', 'Change-resistant'],
  'The Idealist':          ['Optimistic', 'First-impression driven', 'Enthusiastic', 'Halo-prone'],
  'The Thinker':           ['Analytical', 'Detail-oriented', 'Logic-driven', 'Reflective'],
}

const traits = computed(() => {
  if (!archetype.value) return []
  return ARCHETYPE_TRAITS[archetype.value] || ARCHETYPE_TRAITS['The Thinker']
})

// --- Weekly insights ---
const INSIGHT_TYPE_META = {
  journal:   { label: 'ACTIVITY', color: 'lavender', link: '/journal' },
  themes:    { label: 'THEMES',   color: 'blue',     link: '/progress?tab=themes' },
  sentiment: { label: 'MOOD',     color: 'yellow',   link: '/progress?tab=mood' },
  empty:     { label: 'TIP',      color: 'green',    link: '/journal/new' },
}
const insights = computed(() => {
  if (!insightsStore.weeklyInsights.length) return [
    { badgeLabel: 'TIP', badgeColor: 'green', title: 'Start Journaling', desc: 'Write your first journal entry to unlock personalised weekly insights.', link: '/journal/new' },
  ]
  return insightsStore.weeklyInsights.slice(0, 3).map(i => {
    const meta = INSIGHT_TYPE_META[i.type] || { label: 'INSIGHT', color: 'lavender', link: '/journal' }
    return { badgeLabel: meta.label, badgeColor: meta.color, title: i.text.slice(0, 60), desc: i.text, link: meta.link }
  })
})

// --- Recommendations ---
const quickActions = ref([
  { icon: BookOpen, label: 'Write a journal entry', path: '/journal/new' },
  { icon: ClipboardList, label: 'Take an assessment', path: '/assessments' },
  { icon: Search, label: 'Explore a bias', path: '/explore' },
  { icon: MessageSquare, label: 'Chat with AI Guide', path: '/ai-guide' },
])

const recommendations = computed(() => {
  const recs = insightsStore.recommendations
  const list = []
  if (recs?.next_bias) {
    list.push({
      name: recs.next_bias.name || recs.next_bias,
      icon: Brain,
      category: recs.next_bias.category || 'Bias',
      badgeColor: 'blue',
      path: `/explore/${recs.next_bias.slug || recs.next_bias}`,
    })
  }
  if (recs?.next_assessment) {
    list.push({
      name: recs.next_assessment.title || recs.next_assessment,
      icon: BarChart2,
      category: 'Assessment',
      badgeColor: 'yellow',
      path: `/assessments/${recs.next_assessment.id || ''}`,
    })
  }
  // Pad with defaults if API returned nothing yet
  if (!list.length) {
    list.push(
      { name: 'Availability Heuristic', icon: Brain, category: 'Memory', badgeColor: 'blue', path: '/explore/availability-heuristic' },
      { name: 'Dunning-Kruger Effect', icon: BarChart2, category: 'Self', badgeColor: 'yellow', path: '/explore/dunning-kruger-effect' },
      { name: 'Halo Effect', icon: Sparkles, category: 'Social', badgeColor: 'lavender', path: '/explore/halo-effect' },
    )
  }
  return list
})

// --- Radar chart (live from bias fingerprint) ---
const svgSize = 240
const cx = svgSize / 2
const cy = svgSize / 2
const maxR = 88
const rings = [0.25, 0.5, 0.75, 1.0]
const numAxes = 6

const FALLBACK_RADAR = {
  labels: ['Confirmation', 'Availability', 'Anchoring', 'Dunning-Kruger', 'Sunk Cost', 'Attribution'],
  scores: [0.4, 0.3, 0.35, 0.3, 0.25, 0.35],
}

const radarData = computed(() => {
  const biasScores = insightsStore.biasFingerprint?.bias_scores || {}
  const entries = Object.entries(biasScores)
    .sort((a, b) => b[1] - a[1])
    .slice(0, numAxes)
  if (!entries.length) return FALLBACK_RADAR

  // Pad to exactly numAxes if needed
  while (entries.length < numAxes) entries.push([`bias_${entries.length}`, 0])

  // Scale the scores relative to the max score so the radar is always visible
  const maxScore = Math.max(...entries.map(e => e[1]), 0.15)

  return {
    labels: entries.map(([k]) =>
      k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()).replace(/ Bias$/, '').replace(/ Error$/, '').trim()
    ),
    scores: entries.map(([, v]) => Math.min(1.0, (v / maxScore) * 0.85)), // Cap at 85% of radar radius
  }
})

const axisLabels = computed(() => radarData.value.labels)
const scores = computed(() => radarData.value.scores)

const legendColors = ['#9b94e8', '#b8b4f0', '#7e93e8', '#e89b94', '#94e8b4', '#e8c894']

function polarPoint(angle, r) {
  // Start at top (−π/2), go clockwise
  const rad = (angle / numAxes) * 2 * Math.PI - Math.PI / 2
  return {
    x: cx + r * Math.cos(rad),
    y: cy + r * Math.sin(rad),
  }
}

const outerPoints = computed(() =>
  Array.from({ length: numAxes }, (_, i) => polarPoint(i, maxR))
)

function hexPoints(ringFraction) {
  const r = maxR * ringFraction
  return Array.from({ length: numAxes }, (_, i) => {
    const p = polarPoint(i, r)
    return `${p.x},${p.y}`
  }).join(' ')
}

const dataPoints = computed(() =>
  scores.value.map((score, i) => polarPoint(i, maxR * score))
)

const dataPolygonPoints = computed(() =>
  dataPoints.value.map(p => `${p.x},${p.y}`).join(' ')
)

const labelPoints = computed(() =>
  Array.from({ length: numAxes }, (_, i) => polarPoint(i, maxR + 20))
)

const labelAnchors = computed(() =>
  Array.from({ length: numAxes }, (_, i) => {
    const rad = (i / numAxes) * 2 * Math.PI - Math.PI / 2
    const cosVal = Math.cos(rad)
    if (cosVal > 0.3) return 'start'
    if (cosVal < -0.3) return 'end'
    return 'middle'
  })
)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:wght@400;500;600;700;800;900&display=swap');

* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.dashboard { display: flex; flex-direction: column; gap: 40px; }

/* ── Stat Cards ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card { border-radius: 16px; padding: 20px; }
.stat-card.blue     { background: linear-gradient(135deg, #d8edf9, #e8f4fd); }
.stat-card.lavender { background: linear-gradient(135deg, #dad8f9, #eceaf9); }
.stat-card.pink     { background: linear-gradient(135deg, #f9d8f0, #fde8f9); }
.stat-card.green    { background: linear-gradient(135deg, #d8f9e8, #e8fdf0); }

.stat-label {
  font-size: 12px; font-weight: 600; color: var(--slate);
  text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;
}
.stat-value { font-size: 36px; font-weight: 800; color: var(--plum); line-height: 1; }
.stat-change {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 12px; font-weight: 600; padding: 2px 8px;
  border-radius: 99px; margin-top: 6px;
}
.stat-change.up { background: rgba(34,197,94,0.12); color: #16a34a; }
.stat-change.down { background: rgba(239,68,68,0.12); color: #dc2626; }

/* ── Two-column layout ── */
.two-col {
  display: grid;
  grid-template-columns: 60% 40%;
  gap: 20px;
}

.two-col-balanced {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

/* ── Generic card ── */
.card {
  background: white;
  border-radius: var(--radius);
  padding: 24px;
  box-shadow: var(--shadow);
}

/* ── Section header ── */
.section-header {
  display: flex; align-items: baseline; gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1.5px solid var(--lavender-soft);
  margin-bottom: 24px;
}
.section-title { font-size: 20px; font-weight: 700; color: var(--plum); }
.section-tag {
  font-size: 11px; font-weight: 600; letter-spacing: 0.5px;
  color: var(--lavender-deep); background: var(--lavender-soft);
  padding: 2px 10px; border-radius: 99px;
}

/* ── Fingerprint card ── */
.fingerprint-card {
  
}

.radar-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 8px 0 20px;
}
.radar-svg { display: block; overflow: visible; }

.radar-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  justify-content: center;
  margin-bottom: 20px;
}
.legend-item { display: flex; align-items: center; gap: 6px; }
.legend-dot { width: 8px; height: 8px; border-radius: 99px; flex-shrink: 0; }
.legend-text { font-size: 11px; font-weight: 600; color: var(--slate); }

/* ── Archetype card ── */
.archetype-card {
  background: linear-gradient(135deg, #dad8f9, #eceaf9) !important;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.archetype-emoji-wrap {
  width: 80px; height: 80px; border-radius: 99px;
  background: white;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 16px;
  box-shadow: var(--shadow);
}
.archetype-emoji { font-size: 38px; line-height: 1; }
.archetype-title { font-size: 20px; font-weight: 700; color: var(--plum); margin-bottom: 8px; }
.archetype-desc {
  font-size: 13px; color: var(--slate); line-height: 1.6;
  margin-bottom: 16px;
}
.trait-list { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; }

/* ── Badges ── */
.badge {
  font-size: 11px; font-weight: 700; padding: 3px 10px;
  border-radius: 99px; display: inline-flex; align-items: center;
}
.badge-lavender { background: var(--lavender); color: var(--plum); }
.badge-plum     { background: var(--plum); color: white; }
.badge-green    { background: #d1fae5; color: #059669; }
.badge-red      { background: #fee2e2; color: #dc2626; }
.badge-yellow   { background: #fef9c3; color: #92400e; }
.badge-blue     { background: #dbeafe; color: #1d4ed8; }
.badge-pink     { background: #f9d8f0; color: #9d174d; }

/* ── AI Container ── */
.ai-container {
  border-radius: 24px; padding: 24px;
  background: linear-gradient(135deg, #f0effe 0%, #e8eafd 50%, #f5d8f9 100%);
  border: 1px solid var(--lavender);
  position: relative; overflow: hidden;
}
.ai-label {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px;
  color: var(--lavender-deep); background: white;
  padding: 4px 10px; border-radius: 99px; margin-bottom: 12px;
}
.ai-prompt { font-size: 15px; font-weight: 600; color: var(--plum); margin-bottom: 12px; }
.ai-response { font-size: 14px; color: var(--slate); line-height: 1.7; }

/* ── Insight cards ── */
.insights-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.insight-card {
  background: white;
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
  border: 1.5px solid transparent;
  transition: all 0.2s;
}
.insight-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
  border-color: var(--lavender);
}
.insight-top { margin-bottom: 10px; }
.insight-title { font-size: 15px; font-weight: 700; color: var(--plum); margin-bottom: 8px; }
.insight-desc { font-size: 13px; color: var(--slate); line-height: 1.55; }

/* ── Quick Actions ── */
.quick-actions-list { display: flex; flex-direction: column; gap: 8px; }
.quick-action-row {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 14px; border-radius: 12px;
  background: var(--ghost);
  cursor: pointer;
  transition: all 0.17s;
  border: 1.5px solid transparent;
}
.quick-action-row:hover {
  background: var(--lavender-soft);
  border-color: var(--lavender);
  transform: translateX(4px);
}
.quick-action-icon { color: var(--lavender-deep); flex-shrink: 0; }
.quick-action-label { flex: 1; font-size: 14px; font-weight: 600; color: var(--plum); }
.quick-action-arrow { color: var(--slate); }

/* ── Recommendations ── */
.recommendations-list { display: flex; flex-direction: column; gap: 12px; }
.rec-card {
  padding: 14px 16px;
  border-radius: 12px;
  background: var(--ghost);
  border: 1.5px solid transparent;
  transition: all 0.17s;
}
.rec-card:hover {
  background: var(--lavender-soft);
  border-color: var(--lavender);
}
.rec-top { display: flex; align-items: center; gap: 12px; }
.rec-icon-wrap {
  width: 42px; height: 42px;
  background: white; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(53,43,56,0.06);
  color: var(--lavender-deep);
}
.rec-info { display: flex; flex-direction: column; gap: 4px; }
.rec-name { font-size: 14px; font-weight: 700; color: var(--plum); }

/* ── Card footer ── */
.card-footer { display: flex; }

/* ── Responsive ── */
@media (max-width: 640px) {
  .dashboard { gap: 20px; }
  .stats-grid { grid-template-columns: 1fr 1fr; gap: 10px; }
  .stat-value { font-size: 28px; }
  .two-col { grid-template-columns: 1fr; }
  .two-col-balanced { grid-template-columns: 1fr; }
  .insights-grid { grid-template-columns: 1fr; }
  .card { padding: 16px; }
  .section-title { font-size: 17px; }
  .radar-wrap svg { width: 200px; height: 200px; }
}

@media (min-width: 641px) and (max-width: 900px) {
  .stats-grid { grid-template-columns: 1fr 1fr; }
  .two-col { grid-template-columns: 1fr; }
  .insights-grid { grid-template-columns: 1fr 1fr; }
}

/* ── Buttons ── */
.btn {
  display: inline-flex; align-items: center; gap: 6px;
  font-family: 'Urbanist', sans-serif; font-weight: 600;
  border: none; cursor: pointer; transition: all 0.18s;
}
.btn-primary {
  background: var(--plum); color: white;
  padding: 10px 20px; border-radius: 10px; font-size: 14px;
}
.btn-primary:hover { background: #4a3550; transform: translateY(-1px); }
.btn-secondary {
  background: var(--lavender); color: var(--plum);
  padding: 10px 20px; border-radius: 10px; font-size: 14px;
}
.btn-secondary:hover { background: var(--lavender-mid); }
.btn-ghost {
  background: transparent; color: var(--plum);
  border: 1.5px solid var(--lavender);
  padding: 10px 20px; border-radius: 10px; font-size: 14px;
}
.btn-ghost:hover { background: var(--lavender-soft); }
.btn-sm {
  padding: 6px 14px !important;
  font-size: 13px !important;
  border-radius: 8px !important;
}

/* ── Loading Overlay ── */
.loading-overlay {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 60px; color: var(--slate); gap: 16px;
}
.spinner {
  width: 32px; height: 32px; border-radius: 50%;
  border: 3px solid var(--lavender); border-top-color: var(--lavender-deep);
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

svg { display: block; }
</style>
