<template>
  <div class="dashboard">

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
        >{{ stat.change }}</div>
        <div
          v-else
          class="stat-change"
          style="background: rgba(251,191,36,0.15); color: #92400e;"
        >{{ stat.change }}</div>
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
          <span class="archetype-emoji">🦅</span>
        </div>
        <div class="archetype-title">The Critical Thinker</div>
        <span class="badge badge-lavender" style="margin-bottom: 14px; display: inline-block;">Your Archetype</span>
        <p class="archetype-desc">
          You tend to analyze situations deeply but may miss emotional cues. Your strength lies in logical reasoning.
        </p>
        <div class="trait-list">
          <span class="badge badge-lavender" v-for="trait in traits" :key="trait">{{ trait }}</span>
        </div>
        <div class="card-footer" style="margin-top: 24px;">
          <button class="btn btn-primary btn-sm">Explore Archetype</button>
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
        <div class="ai-label">✨ Sentio AI</div>
        <div class="ai-prompt">Based on your recent journal entries...</div>
        <div class="ai-response">
          You've shown strong confirmation bias patterns — particularly around work decisions. Your journal entries from Tuesday and Thursday both reveal a tendency to seek information that confirms your existing project timeline estimates...
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
            <button class="btn btn-ghost btn-sm">Explore →</button>
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
            <span class="quick-action-icon">{{ action.icon }}</span>
            <span class="quick-action-label">{{ action.label }}</span>
            <span class="quick-action-arrow">→</span>
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
              <span class="rec-emoji">{{ rec.emoji }}</span>
              <div class="rec-info">
                <div class="rec-name">{{ rec.name }}</div>
                <span class="badge" :class="`badge-${rec.badgeColor}`" style="font-size: 10px;">{{ rec.category }}</span>
              </div>
            </div>
            <button class="btn btn-secondary btn-sm" style="margin-top: 10px; width: 100%;">
              Start Learning →
            </button>
          </div>
        </div>
      </div>

    </section>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const stats = ref([
  { label: 'BIASES IDENTIFIED', value: '7', change: '↑ 2 this week', dir: 'up', variant: 'blue' },
  { label: 'JOURNAL ENTRIES', value: '12', change: '↑ 3 this week', dir: 'up', variant: 'lavender' },
  { label: 'CURRENT STREAK', value: '5', change: '🔥 days', dir: 'neutral', variant: 'pink' },
  { label: 'INSIGHTS UNLOCKED', value: '23', change: '↑ 4 this month', dir: 'up', variant: 'green' },
])

const traits = ref(['Analytical', 'Detail-oriented', 'Logic-driven', 'Skeptical'])

const insights = ref([
  {
    badgeLabel: 'COGNITIVE',
    badgeColor: 'yellow',
    title: 'Confirmation Bias Spike',
    desc: 'Your reading and information-seeking showed strong confirmation patterns this week.',
  },
  {
    badgeLabel: 'BEHAVIORAL',
    badgeColor: 'blue',
    title: 'Anchoring on First Offer',
    desc: 'In 3 recent decisions, initial numbers had outsized influence on final choices.',
  },
  {
    badgeLabel: 'PATTERN',
    badgeColor: 'lavender',
    title: 'Weekly Reflection Loop',
    desc: 'Strong metacognitive pattern emerging — keep up the daily journaling.',
  },
])

const quickActions = ref([
  { icon: '📝', label: 'Write a journal entry', path: '/journal/new' },
  { icon: '🧩', label: 'Take an assessment', path: '/assessments' },
  { icon: '🔍', label: 'Explore a bias', path: '/explore' },
  { icon: '💬', label: 'Chat with AI Guide', path: '/ai-guide' },
])

const recommendations = ref([
  { name: 'Availability Heuristic', emoji: '🧠', category: 'Memory', badgeColor: 'blue' },
  { name: 'Dunning-Kruger Effect', emoji: '📊', category: 'Self', badgeColor: 'yellow' },
  { name: 'Halo Effect', emoji: '✨', category: 'Social', badgeColor: 'pink' },
])

// --- Radar chart ---
const svgSize = 240
const cx = svgSize / 2
const cy = svgSize / 2
const maxR = 88
const rings = [0.25, 0.5, 0.75, 1.0]
const numAxes = 6

const axisLabels = ['Confirmation', 'Availability', 'Anchoring', 'Dunning-Kruger', 'Sunk Cost', 'Attribution']
const scores = [0.7, 0.4, 0.6, 0.5, 0.3, 0.8]

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
  scores.map((score, i) => polarPoint(i, maxR * score))
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
.fingerprint-card {}

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
.quick-action-icon { font-size: 18px; width: 24px; text-align: center; }
.quick-action-label { flex: 1; font-size: 14px; font-weight: 600; color: var(--plum); }
.quick-action-arrow { font-size: 14px; color: var(--slate); }

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
.rec-emoji {
  font-size: 22px; width: 42px; height: 42px;
  background: white; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(53,43,56,0.06);
}
.rec-info { display: flex; flex-direction: column; gap: 4px; }
.rec-name { font-size: 14px; font-weight: 700; color: var(--plum); }

/* ── Card footer ── */
.card-footer { display: flex; }

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
</style>
