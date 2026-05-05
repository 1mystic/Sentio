<template>
  <div class="bias-detail">

    <!-- Loading state -->
    <div v-if="loading" class="loading-wrap">
      <div class="sk-line sk-w60"></div>
      <div class="sk-block"></div>
    </div>

    <!-- Not found -->
    <div v-else-if="!bias" class="not-found">
      <p>Bias not found. <button class="btn btn-ghost btn-sm" @click="router.push('/explore')">Back to Explorer</button></p>
    </div>

    <template v-else>

    <!-- Breadcrumb -->
    <div class="breadcrumb">
      <span class="breadcrumb-link" @click="router.push('/explore')">Bias Explorer</span>
      <span class="breadcrumb-sep">›</span>
      <span class="breadcrumb-current">{{ bias.name }}</span>
    </div>

    <!-- Hero Section -->
    <div class="hero-card">
      <div class="hero-left">
        <div class="hero-icon-circle">
          <component :is="getBiasIcon(bias.slug || bias.id)" :size="38" />
        </div>
        <div class="hero-text">
          <div class="hero-meta">
            <span class="badge badge-lavender">{{ bias.category }}</span>
          </div>
          <h1 class="hero-title">{{ bias.name }}</h1>
          <p class="hero-tagline">"{{ bias.tagline }}"</p>
        </div>
      </div>
      <div class="hero-stats">
        <div class="hero-stat-mini">
          <div class="hsm-label">Prevalence</div>
          <div class="hsm-value">{{ bias.prevalence }}%</div>
        </div>
        <div class="hero-stat-divider"></div>
        <div class="hero-stat-mini">
          <div class="hsm-label">Your Score</div>
          <div class="hsm-value">
            <template v-if="bias.userScore != null">{{ bias.userScore }}<span class="hsm-unit">/10</span></template>
            <template v-else><span class="hsm-unit">—</span></template>
          </div>
        </div>
        <div class="hero-stat-divider"></div>
        <div class="hero-stat-mini">
          <div class="hsm-label">This week</div>
          <div class="hsm-value">
            <template v-if="bias.weeklyEncounters != null">{{ bias.weeklyEncounters }}<span class="hsm-unit"> times</span></template>
            <template v-else><span class="hsm-unit">—</span></template>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs-bar">
      <button
        v-for="tab in tabs"
        :key="tab"
        class="tab-btn"
        :class="{ active: activeTab === tab.toLowerCase().replace(/ /g, '-') }"
        @click="activeTab = tab.toLowerCase().replace(/ /g, '-')"
      >{{ tab }}</button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">

      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" class="tab-pane">
        <div class="card">
          <div class="section-header">
            <span class="section-title">What is it?</span>
          </div>
          <p class="body-text">{{ bias.definition }}</p>
        </div>

        <div class="why-card">
          <div class="why-header">
            <Lightbulb :size="20" class="why-icon" />
            <span class="why-title">Why it happens</span>
          </div>
          <p class="body-text">{{ bias.whyItHappens }}</p>
        </div>

        <div class="card">
          <div class="section-header">
            <span class="section-title">Related Biases</span>
          </div>
          <div class="related-grid">
            <div
              v-for="rel in relatedBiases"
              :key="rel.id"
              class="related-card"
              @click="router.push('/explore/' + (rel.slug || rel.id))"
            >
              <component :is="getBiasIcon(rel.slug || rel.id)" :size="18" class="related-icon" />
              <span class="related-name">{{ rel.name }}</span>
              <ArrowRight :size="12" class="related-arrow" />
            </div>
          </div>
        </div>
      </div>

      <!-- Examples Tab -->
      <div v-if="activeTab === 'examples'" class="tab-pane">
        <div
          v-for="(ex, idx) in bias.examples"
          :key="idx"
          class="card example-card"
        >
          <div class="example-number">{{ idx + 1 }}</div>
          <div class="example-body">
            <div class="example-title">{{ ex.title }}</div>
            <p class="body-text">{{ ex.description }}</p>
            <div class="example-insight">
              <span class="insight-label">The bias in action:</span>
              <span class="insight-text">{{ ex.insight }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- In Your Life Tab -->
      <div v-if="activeTab === 'in-your-life'" class="tab-pane">
        <div class="ai-container" style="margin-bottom: 24px;">
          <div class="ai-label"><Sparkles :size="11" /> Personalized Analysis</div>
          <div class="ai-prompt">How {{ bias.name }} shows up in your life</div>
          <div class="ai-response">
            <template v-if="bias.userScore != null">
              You scored <strong>{{ bias.userScore }}/10</strong> on this bias in your last assessment.
              Keep journaling to build a clearer picture of how it shows up in your daily thinking.
            </template>
            <template v-else>
              You haven't taken an assessment covering this bias yet.
              Start journaling or take an assessment to see personalized insights here.
            </template>
          </div>
        </div>

        <div class="card">
          <div class="section-header">
            <span class="section-title">How to Track It</span>
            <span class="section-tag">TIPS</span>
          </div>
          <div class="timeline">
            <div class="timeline-item">
              <div class="timeline-dot"></div>
              <div class="timeline-body">
                <div class="timeline-date">Journal</div>
                <div class="timeline-title">Write about it</div>
                <div class="timeline-desc">Use the journal to capture moments when you notice this bias affecting your thinking. The AI will detect it automatically.</div>
              </div>
            </div>
            <div class="timeline-item">
              <div class="timeline-dot"></div>
              <div class="timeline-body">
                <div class="timeline-date">Assess</div>
                <div class="timeline-title">Take an assessment</div>
                <div class="timeline-desc">Structured assessments give you a quantified score for this bias and track changes over time on your Progress page.</div>
              </div>
            </div>
            <div class="timeline-item">
              <div class="timeline-dot"></div>
              <div class="timeline-body">
                <div class="timeline-date">Reflect</div>
                <div class="timeline-title">Ask the AI Guide</div>
                <div class="timeline-desc">Chat with Sentio AI and ask specifically about {{ bias.name }} — it will draw on your journal history to give you personalised insights.</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- How to Counter Tab -->
      <div v-if="activeTab === 'how-to-counter'" class="tab-pane">
        <div class="strategies-grid">
          <div
            v-for="(strategy, idx) in bias.strategies"
            :key="idx"
            class="strategy-card card"
          >
            <div class="strategy-top">
              <div class="strategy-number">{{ idx + 1 }}</div>
              <div class="strategy-name">{{ strategy.name }}</div>
            </div>
            <p class="body-text" style="margin: 0 0 16px;">{{ strategy.desc }}</p>
            <button class="btn btn-secondary btn-sm">Practice it</button>
          </div>
        </div>
      </div>

    </div>

    <!-- CTA Section -->
    <div class="cta-section">
      <div class="cta-content">
        <ClipboardList :size="36" class="cta-icon" />
        <div class="cta-text">
          <div class="cta-title">Ready to test yourself?</div>
          <div class="cta-desc">Take a short assessment to see how strongly this bias affects your thinking</div>
        </div>
      </div>
      <div class="cta-actions">
        <button class="btn btn-primary" @click="router.push('/assessments')">Take the Assessment</button>
        <button class="btn btn-ghost" @click="router.push('/journal/new')">Journal about it</button>
      </div>
    </div>

    </template><!-- end v-else -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBiasStore } from '@/stores/bias.js'
import {
  Search, Brain, Anchor, TrendingDown, Star, Calendar,
  Lock, Users, BookMarked, Scan, Megaphone, HandHelping, Sparkles,
  BarChart2, ArrowRight, Lightbulb, ClipboardList
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const biasStore = useBiasStore()

const activeTab = ref('overview')
const tabs = ['Overview', 'Examples', 'In Your Life', 'How to Counter']

const biasIconMap = {
  'confirmation-bias': Search,
  'availability-heuristic': Brain,
  'anchoring-bias': Anchor,
  'dunning-kruger': BarChart2,
  'sunk-cost': TrendingDown,
  'halo-effect': Sparkles,
  'fundamental-attribution': HandHelping,
  'bandwagon-effect': Megaphone,
  'optimism-bias': Star,
  'recency-bias': Calendar,
  'status-quo-bias': Lock,
  'in-group-bias': Users,
}

function getBiasIcon(id) { return biasIconMap[id] || Brain }

const bias = ref(null)
const loading = ref(true)

function mapBias(data) {
  // Map DB fields (description, example TEXT, detection_signals JSONB, prevalence_pct)
  // to the shape the template expects
  const examples = data.example
    ? [{ title: 'Real-world Example', description: data.example, insight: data.research_summary ? 'Research note: ' + data.research_summary.slice(0, 120) + '…' : '' }]
    : []

  const signals = Array.isArray(data.detection_signals) ? data.detection_signals : []
  const strategies = signals.length
    ? signals.map(s => ({ name: 'Watch for this pattern', desc: s }))
    : [
        { name: 'Notice it happening', desc: 'When you catch yourself very certain about something, pause and ask: what evidence would change my mind?' },
        { name: 'Seek the opposite', desc: 'Deliberately look for information that contradicts your current view before making a decision.' },
        { name: 'Name it out loud', desc: 'Simply labeling a bias when you notice it ("I might be doing X right now") reduces its influence on your judgment.' },
      ]

  return {
    id: data.slug || data.id,
    name: data.name,
    category: data.category,
    tagline: data.short_description || '',
    prevalence: data.prevalence_pct ?? 50,
    userScore: null,
    weeklyEncounters: null,
    definition: data.description,
    whyItHappens: data.research_summary || 'This bias emerges from cognitive shortcuts our brains use to process information quickly and efficiently.',
    examples,
    strategies,
    related_bias_slugs: data.related_bias_slugs || [],
  }
}

onMounted(async () => {
  const slug = route.params.slug || route.params.id
  if (!slug) { loading.value = false; return }
  const data = await biasStore.fetchBySlug(slug)
  bias.value = data ? mapBias(data) : null
  loading.value = false
})

const relatedBiases = computed(() => {
  const currentId = bias.value?.id
  if (biasStore.biases.length === 0) return [
    { id: 'availability-heuristic', name: 'Availability Heuristic' },
    { id: 'anchoring-bias', name: 'Anchoring Bias' },
  ]
  // Prefer explicitly related biases from the DB if stored
  const relatedSlugs = bias.value?.related_bias_slugs || []
  const fromSlugs = biasStore.biases
    .filter(b => relatedSlugs.includes(b.slug))
    .map(b => ({ id: b.slug || b.id, name: b.name }))
  if (fromSlugs.length >= 2) return fromSlugs.slice(0, 3)

  return biasStore.biases
    .filter(b => (b.slug || b.id) !== currentId)
    .slice(0, 3)
    .map(b => ({ id: b.slug || b.id, name: b.name }))
})

const timelineItems = [
  { date: 'This week', title: 'Detected in recent entries', desc: 'Review your journal entries to see specific instances.' },
]
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:wght@400;500;600;700;800;900&display=swap');

* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.bias-detail { display: flex; flex-direction: column; gap: 24px; }
.loading-wrap { display: flex; flex-direction: column; gap: 16px; padding: 24px 0; }
.sk-line { height: 20px; border-radius: 6px; background: var(--lavender-soft); animation: sk-pulse 1.4s ease-in-out infinite; }
.sk-w60 { width: 60%; }
.sk-block { height: 180px; border-radius: 16px; background: var(--lavender-soft); animation: sk-pulse 1.4s ease-in-out infinite; }
@keyframes sk-pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
.not-found { padding: 48px 0; text-align: center; color: var(--slate); }

/* ── Breadcrumb ── */
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 13px; }
.breadcrumb-link {
  color: var(--lavender-deep); font-weight: 600; cursor: pointer;
  transition: color 0.15s;
}
.breadcrumb-link:hover { color: var(--plum); text-decoration: underline; }
.breadcrumb-sep { color: var(--slate); }
.breadcrumb-current { color: var(--slate); font-weight: 500; }

/* ── Hero Card ── */
.hero-card {
  background: linear-gradient(135deg, #f0effe 0%, #e8eafd 60%, #f5d8f9 100%);
  border: 1px solid var(--lavender);
  border-radius: var(--radius-lg);
  padding: 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
}
.hero-left { display: flex; align-items: center; gap: 20px; }
.hero-icon-circle {
  width: 80px; height: 80px; border-radius: 99px;
  background: white;
  display: flex; align-items: center; justify-content: center;
  color: var(--lavender-deep); flex-shrink: 0;
  box-shadow: 0 4px 20px rgba(53,43,56,0.1);
}
.hero-meta { margin-bottom: 8px; }
.hero-title { font-size: 36px; font-weight: 800; color: var(--plum); margin: 0 0 6px; line-height: 1.1; }
.hero-tagline { font-size: 16px; color: var(--slate); font-style: italic; margin: 0; }

.hero-stats {
  display: flex; align-items: center; gap: 0;
  background: white; border-radius: 16px;
  padding: 20px 24px;
  box-shadow: var(--shadow);
  flex-shrink: 0;
}
.hero-stat-mini { text-align: center; padding: 0 20px; }
.hero-stat-mini:first-child { padding-left: 0; }
.hero-stat-mini:last-child { padding-right: 0; }
.hsm-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--slate); margin-bottom: 4px; }
.hsm-value { font-size: 26px; font-weight: 800; color: var(--plum); line-height: 1; }
.hsm-unit { font-size: 14px; font-weight: 600; color: var(--slate); }
.hero-stat-divider { width: 1px; height: 40px; background: var(--lavender-soft); }

/* ── Tabs Bar ── */
.tabs-bar {
  display: flex; gap: 4px;
  background: white; padding: 6px;
  border-radius: 14px;
  box-shadow: var(--shadow);
  width: fit-content;
}
.tab-btn {
  font-family: 'Urbanist', sans-serif; font-size: 14px; font-weight: 600;
  padding: 8px 20px; border-radius: 10px;
  border: none; background: transparent; color: var(--slate);
  cursor: pointer; transition: all 0.17s;
}
.tab-btn:hover { background: var(--lavender-soft); color: var(--plum); }
.tab-btn.active { background: var(--plum); color: white; }

/* ── Tab Content ── */
.tab-content { }
.tab-pane { display: flex; flex-direction: column; gap: 20px; }

/* ── Generic Card ── */
.card {
  background: white; border-radius: var(--radius);
  padding: 24px; box-shadow: var(--shadow);
}

/* ── Section Header ── */
.section-header {
  display: flex; align-items: baseline; gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1.5px solid var(--lavender-soft);
  margin-bottom: 20px;
}
.section-title { font-size: 18px; font-weight: 700; color: var(--plum); }
.section-tag {
  font-size: 11px; font-weight: 600; letter-spacing: 0.5px;
  color: var(--lavender-deep); background: var(--lavender-soft);
  padding: 2px 10px; border-radius: 99px;
}

/* ── Body text ── */
.body-text { font-size: 15px; color: var(--slate); line-height: 1.75; margin: 0 0 16px; }

/* ── Why card ── */
.why-card {
  background: linear-gradient(135deg, #f0eafe, #ebe8fd);
  border-radius: var(--radius); padding: 24px;
  border: 1px solid var(--lavender);
}
.why-header { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
.why-icon { color: var(--lavender-deep); }
.why-title { font-size: 16px; font-weight: 700; color: var(--plum); }

/* ── Related Biases ── */
.related-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.related-card {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 14px; border-radius: 12px;
  background: var(--ghost); border: 1.5px solid transparent;
  cursor: pointer; transition: all 0.17s;
}
.related-card:hover { background: var(--lavender-soft); border-color: var(--lavender); transform: translateY(-2px); }
.related-icon { color: var(--lavender-deep); flex-shrink: 0; }
.related-name { flex: 1; font-size: 13px; font-weight: 600; color: var(--plum); }
.related-arrow { color: var(--slate); }

/* ── Example cards ── */
.example-card { display: flex; gap: 16px; }
.example-number {
  width: 36px; height: 36px; border-radius: 99px;
  background: var(--plum); color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 800; flex-shrink: 0;
}
.example-body { flex: 1; }
.example-title { font-size: 16px; font-weight: 700; color: var(--plum); margin-bottom: 8px; }
.example-insight {
  background: var(--lavender-soft); border-radius: 10px;
  padding: 12px 14px; margin-top: 12px;
  font-size: 13px; line-height: 1.6; color: var(--slate);
}
.insight-label { font-weight: 700; color: var(--lavender-deep); }
.insight-text { color: var(--slate); }

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

/* ── Timeline ── */
.timeline { display: flex; flex-direction: column; gap: 0; }
.timeline-item {
  display: flex; gap: 16px;
  padding: 0 0 20px;
  position: relative;
}
.timeline-item::before {
  content: '';
  position: absolute; left: 7px; top: 16px;
  width: 2px; height: calc(100% - 8px);
  background: var(--lavender-soft);
}
.timeline-item:last-child::before { display: none; }
.timeline-dot {
  width: 16px; height: 16px; border-radius: 99px;
  background: var(--lavender-deep); border: 3px solid white;
  outline: 2px solid var(--lavender);
  flex-shrink: 0; margin-top: 2px;
  z-index: 1;
}
.timeline-body { flex: 1; }
.timeline-date { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--lavender-deep); margin-bottom: 3px; }
.timeline-title { font-size: 14px; font-weight: 700; color: var(--plum); margin-bottom: 4px; }
.timeline-desc { font-size: 13px; color: var(--slate); line-height: 1.55; }

/* ── Strategies ── */
.strategies-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}
.strategy-card {
  display: flex; flex-direction: column;
  transition: all 0.2s;
}
.strategy-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }
.strategy-top { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.strategy-number {
  width: 36px; height: 36px; border-radius: 99px;
  background: var(--plum); color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 800; flex-shrink: 0;
}
.strategy-name { font-size: 16px; font-weight: 700; color: var(--plum); }

/* ── CTA Section ── */
.cta-section {
  background: linear-gradient(135deg, var(--plum) 0%, #4a3550 100%);
  border-radius: var(--radius-lg); padding: 32px;
  display: flex; align-items: center; justify-content: space-between; gap: 24px;
  flex-wrap: wrap;
}
.cta-content { display: flex; align-items: center; gap: 16px; }
.cta-icon { color: rgba(255,255,255,0.85); }
.cta-title { font-size: 20px; font-weight: 700; color: white; margin-bottom: 4px; }
.cta-desc { font-size: 14px; color: rgba(255,255,255,0.7); }
.cta-actions { display: flex; gap: 12px; align-items: center; }

/* ── Badges ── */
.badge {
  font-size: 11px; font-weight: 700; padding: 3px 10px;
  border-radius: 99px; display: inline-flex; align-items: center;
}
.badge-lavender { background: var(--lavender); color: var(--plum); }
.badge-plum     { background: var(--plum); color: white; }
.badge-green    { background: #d1fae5; color: #059669; }
.badge-yellow   { background: #fef9c3; color: #92400e; }
.badge-blue     { background: #dbeafe; color: #1d4ed8; }
.badge-pink     { background: #f9d8f0; color: #9d174d; }

/* ── Buttons ── */
.btn {
  display: inline-flex; align-items: center; gap: 6px;
  font-family: 'Urbanist', sans-serif; font-weight: 600;
  border: none; cursor: pointer; transition: all 0.18s;
}
.btn-primary { background: white; color: var(--plum); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-primary:hover { background: var(--ghost); transform: translateY(-1px); }
.btn-secondary { background: var(--lavender); color: var(--plum); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-secondary:hover { background: var(--lavender-mid); }
.btn-ghost {
  background: transparent; color: white;
  border: 1.5px solid rgba(255,255,255,0.4);
  padding: 10px 20px; border-radius: 10px; font-size: 14px;
}
.btn-ghost:hover { background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.7); }
.btn-sm {
  padding: 6px 14px !important;
  font-size: 13px !important;
  border-radius: 8px !important;
}

svg { display: block; }
</style>
