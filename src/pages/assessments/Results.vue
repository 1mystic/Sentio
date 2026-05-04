<template>
  <div class="results-page">

    <!-- Celebration Header -->
    <div class="celebration-header">
      <Trophy :size="40" class="celebration-trophy" />
      <h1 class="celebration-title">Assessment Complete!</h1>
      <p class="celebration-sub">Here's what we discovered about your thinking patterns</p>
    </div>

    <!-- Score Card -->
    <div class="score-card card">
      <div class="score-inner">
        <div class="score-ring-wrap">
          <svg width="140" height="140" viewBox="0 0 140 140" class="score-svg">
            <circle cx="70" cy="70" r="58" fill="none" stroke="#eceaf9" stroke-width="12"/>
            <circle
              cx="70" cy="70" r="58"
              fill="none"
              stroke="url(#ringGradient)"
              stroke-width="12"
              stroke-linecap="round"
              :stroke-dasharray="circumference"
              :stroke-dashoffset="dashOffset"
              transform="rotate(-90 70 70)"
            />
            <defs>
              <linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#9b94e8"/>
                <stop offset="100%" stop-color="#b8b4f0"/>
              </linearGradient>
            </defs>
          </svg>
          <div class="score-number">{{ overallScore }}</div>
        </div>
        <div class="score-info">
          <div class="score-label">Your Bias Susceptibility Score</div>
          <div class="score-interpretation">{{ interpretation }}</div>
          <p class="score-desc">Your assessment reveals patterns across {{ categories.length }} dimension{{ categories.length !== 1 ? 's' : '' }}. Review your highest-scoring areas below and explore targeted resources to build self-awareness.</p>
          <div class="score-badges">
            <span class="badge badge-lavender">{{ overallScore }}th percentile</span>
            <span class="badge badge-green">{{ interpretation }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 4-Column Breakdown -->
    <div class="breakdown-grid">
      <div v-for="cat in categories" :key="cat.label" class="breakdown-card card">
        <div class="breakdown-icon" :style="{ color: cat.color }"><component :is="cat.icon" :size="26" /></div>
        <div class="breakdown-label">{{ cat.label }}</div>
        <div class="breakdown-score" :style="{ color: cat.color }">{{ cat.score }}</div>
        <div class="breakdown-bar-track">
          <div class="breakdown-bar-fill" :style="{ width: cat.score + '%', background: cat.color }"></div>
        </div>
      </div>
    </div>

    <!-- Bias Bars -->
    <div class="card bars-card">
      <div class="section-header">
        <span class="section-title">Bias by Category</span>
      </div>
      <div class="bars-list">
        <div v-for="bar in biasBars" :key="bar.name" class="result-bar">
          <div class="result-bar-label">{{ bar.name }}</div>
          <div class="result-bar-track">
            <div class="result-bar-fill" :style="{ width: bar.score + '%' }"></div>
          </div>
          <span class="result-bar-value">{{ bar.score }}</span>
        </div>
      </div>
    </div>

    <!-- Top Bias Highlight -->
    <div class="card top-bias-card">
      <div class="top-bias-header">
        <span class="badge badge-plum">Top Pattern Detected</span>
        <h3 class="top-bias-name">{{ topCategoryName }}</h3>
      </div>
      <p class="top-bias-text">This is your highest-scoring dimension from this assessment. Focused practice in this area will have the most impact on your cognitive self-awareness.</p>
      <div class="top-bias-indicators">
        <div v-for="(indicator, i) in topBiasIndicators" :key="i" class="indicator">
          <span class="indicator-dot"></span>
          <span>{{ indicator }}</span>
        </div>
      </div>
    </div>

    <!-- Recommendations -->
    <div class="recommendations">
      <div class="section-header">
        <span class="section-title">Recommended Next Steps</span>
      </div>
      <div class="rec-grid">
        <div v-for="rec in recommendations" :key="rec.title" class="rec-card card">
          <div class="rec-icon"><component :is="rec.icon" :size="28" /></div>
          <div class="rec-content">
            <h4 class="rec-title">{{ rec.title }}</h4>
            <p class="rec-desc">{{ rec.desc }}</p>
          </div>
          <router-link :to="rec.link" class="btn btn-secondary btn-sm">Start Learning</router-link>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="actions-bar">
      <router-link :to="`/assessments/${route.params.id}`" class="btn btn-ghost"><RotateCcw :size="14" /> Retake</router-link>
      <router-link to="/progress" class="btn btn-secondary"><TrendingUp :size="14" /> View in Progress</router-link>
      <router-link to="/explore" class="btn btn-primary">Explore Biases <ArrowRight :size="14" /></router-link>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Trophy, TrendingUp, RotateCcw, ArrowRight, Brain, BookMarked, Zap, Users, Scan, MessageSquare, Shield, Eye, Anchor, Activity } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

// Results passed via router.push state from Take.vue
const routeState = history.state || {}
const scores = routeState.scores || {}  // { category: score }

const CATEGORY_META = {
  // Assessment categories
  decision:           { label: 'Decision',          icon: Zap,        color: '#9b94e8' },
  social:             { label: 'Social',             icon: Users,      color: '#e88fa0' },
  memory:             { label: 'Memory',             icon: BookMarked, color: '#88c9a0' },
  self_perception:    { label: 'Self-Perception',    icon: Scan,       color: '#e8c56a' },
  general:            { label: 'General',            icon: Brain,      color: '#9b94e8' },
  // Bias signal keys from CBI/NCS/MAI questions
  confirmation_bias:  { label: 'Confirmation Bias',  icon: Shield,     color: '#9b94e8' },
  anchoring_bias:     { label: 'Anchoring Bias',     icon: Anchor,     color: '#e88fa0' },
  availability_bias:  { label: 'Availability Bias',  icon: Eye,        color: '#88c9a0' },
  overconfidence:     { label: 'Overconfidence',     icon: TrendingUp, color: '#e8c56a' },
  social_conformity:  { label: 'Social Conformity',  icon: Users,      color: '#94c9e8' },
  attribution_error:  { label: 'Attribution Error',  icon: Brain,      color: '#e8b994' },
  sunk_cost_fallacy:  { label: 'Sunk Cost',          icon: Activity,   color: '#c9e894' },
  dunning_kruger:     { label: 'Dunning-Kruger',     icon: TrendingUp, color: '#e8d494' },
}

const categories = computed(() => {
  const cats = Object.entries(scores)
  if (!cats.length) return [
    { label: 'Decision', icon: Zap, score: 72, color: '#9b94e8' },
    { label: 'Social', icon: Users, score: 65, color: '#e88fa0' },
  ]
  return cats.map(([k, v]) => {
    const meta = CATEGORY_META[k] || { label: k, icon: Brain, color: '#9b94e8' }
    return { label: meta.label, icon: meta.icon, score: v, color: meta.color }
  })
})

const overallScore = computed(() => {
  const vals = Object.values(scores)
  if (!vals.length) return 72
  return Math.round(vals.reduce((a, b) => a + b, 0) / vals.length)
})

const topCategory = computed(() => {
  const cats = Object.entries(scores)
  if (!cats.length) return null
  return cats.sort((a, b) => b[1] - a[1])[0]
})

const topCategoryName = computed(() =>
  topCategory.value ? (CATEGORY_META[topCategory.value[0]]?.label || topCategory.value[0]) : 'General Bias Patterns'
)

const interpretation = computed(() => {
  const s = overallScore.value
  if (s >= 80) return 'High Bias Awareness'
  if (s >= 60) return 'Moderate Bias Awareness'
  if (s >= 40) return 'Developing Awareness'
  return 'Early Stage Awareness'
})

const biasBars = computed(() => {
  const cats = Object.entries(scores)
  if (!cats.length) return [
    { name: 'Confirmation Bias', score: 72 },
    { name: 'Anchoring', score: 65 },
  ]
  return cats
    .sort((a, b) => b[1] - a[1])
    .map(([k, v]) => ({
      name: CATEGORY_META[k]?.label || k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
      score: v,
    }))
})

const circumference = 364.4
const dashOffset = computed(() => circumference - (circumference * overallScore.value / 100))

const BIAS_INDICATORS = {
  confirmation_bias:  ['Dismissing contradictory data in discussions', 'Seeking validation rather than critique', 'Filtering news and information selectively'],
  anchoring_bias:     ['Over-relying on the first number heard in negotiations', 'Initial estimates dominating final decisions', 'Struggling to adjust away from early reference points'],
  availability_bias:  ['Overweighting recent events when assessing risk', 'Judging frequency by how easily examples come to mind', 'Vivid stories influencing decisions more than statistics'],
  overconfidence:     ['Underestimating time needed for projects', 'Overestimating accuracy of own predictions', 'Taking on tasks beyond current skill level without noticing'],
  social_conformity:  ['Changing opinions when outnumbered in a group', 'Avoiding dissent to maintain social harmony', 'Going along with crowd decisions without critical evaluation'],
  attribution_error:  ['Blaming personality when others make mistakes', 'Crediting circumstances when you make the same mistake', 'Judging people harshly without considering their context'],
  sunk_cost_fallacy:  ['Continuing projects only because of past investment', 'Finishing books/films you dislike to not "waste" them', 'Holding losing positions longer than rational analysis warrants'],
  dunning_kruger:     ['Overestimating competence in unfamiliar domains', 'Undervaluing expert advice in areas you recently learned', 'Feeling less confident after gaining deeper expertise'],
  decision:           ['Rushing important choices to reduce discomfort', 'Preferring familiar options even when alternatives are better', 'Over-analysing low-stakes decisions while under-analysing high-stakes ones'],
  social:             ['Adjusting your views to match perceived group consensus', 'Feeling pressure to agree in group settings', 'Attributing others\' behaviour to personality rather than situation'],
  memory:             ['Recalling vivid recent events as more common than they are', 'Trusting first impressions more than updated information', 'Forgetting disconfirming evidence more easily than confirming evidence'],
  self_perception:    ['Overestimating skill in areas where knowledge is limited', 'Underestimating your own performance after gaining expertise', 'Setting expectations based on initial, not updated, self-image'],
  general:            ['Noticing patterns that confirm existing beliefs', 'Discounting evidence that challenges current assumptions', 'Making decisions based on feelings rather than data'],
}

const topBiasIndicators = computed(() => {
  if (!topCategory.value) return BIAS_INDICATORS.general
  return BIAS_INDICATORS[topCategory.value[0]] || BIAS_INDICATORS.general
})

const recommendations = ref([
  { icon: Brain, title: 'Explore Your Top Pattern', desc: 'Learn the science and practical strategies for your highest-scoring bias.', link: '/explore' },
  { icon: BookMarked, title: 'Start a Reflection Journal', desc: 'Daily journaling is proven to surface hidden biases.', link: '/journal/new' },
  { icon: MessageSquare, title: 'Talk with Sentio AI', desc: 'Explore your specific patterns in a conversation with our AI guide.', link: '/ai-guide' },
])
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.results-page { display: flex; flex-direction: column; gap: 28px; }

/* Buttons */
.btn { display: inline-flex; align-items: center; gap: 6px; font-family: 'Urbanist'; font-weight: 600; border: none; cursor: pointer; transition: all 0.18s; outline: none; text-decoration: none; }
.btn-primary { background: var(--plum); color: white; padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-primary:hover { background: #4a3550; transform: translateY(-1px); }
.btn-secondary { background: var(--lavender); color: var(--plum); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-secondary:hover { background: var(--lavender-mid); }
.btn-ghost { background: transparent; color: var(--plum); border: 1.5px solid var(--lavender); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-ghost:hover { background: var(--lavender-soft); }
.btn-sm { padding: 6px 14px !important; font-size: 13px !important; border-radius: 8px !important; }

.card { background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(53,43,56,0.07); padding: 28px; }
.badge { font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 99px; display: inline-flex; align-items: center; }
.badge-lavender { background: var(--lavender); color: var(--plum); }
.badge-green { background: #d1fae5; color: #059669; }
.badge-plum { background: var(--plum); color: white; }

/* Header */
.celebration-header { text-align: center; padding: 20px 0; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.celebration-trophy { color: var(--lavender-deep); }
.celebration-title { font-size: 32px; font-weight: 800; color: var(--plum); margin: 0 0 8px; }
.celebration-sub { font-size: 16px; color: var(--slate); margin: 0; }

/* Score Card */
.score-card { background: linear-gradient(135deg, var(--lavender-soft) 0%, white 100%); }
.score-inner { display: flex; align-items: center; gap: 40px; flex-wrap: wrap; }
.score-ring-wrap { position: relative; width: 140px; height: 140px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.score-svg { position: absolute; top: 0; left: 0; }
.score-number { font-size: 36px; font-weight: 800; color: var(--plum); position: relative; z-index: 1; }
.score-info { flex: 1; display: flex; flex-direction: column; gap: 10px; }
.score-label { font-size: 12px; font-weight: 700; color: var(--slate); text-transform: uppercase; letter-spacing: 0.06em; }
.score-interpretation { font-size: 20px; font-weight: 600; color: var(--plum); }
.score-desc { font-size: 14px; color: var(--slate); line-height: 1.6; margin: 0; }
.score-badges { display: flex; gap: 8px; flex-wrap: wrap; }

/* Breakdown */
.breakdown-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
@media (max-width: 700px) { .breakdown-grid { grid-template-columns: repeat(2, 1fr); } }
.breakdown-card { text-align: center; padding: 20px 16px; display: flex; flex-direction: column; gap: 8px; align-items: center; }
.breakdown-icon { display: flex; align-items: center; justify-content: center; }
.breakdown-label { font-size: 13px; font-weight: 600; color: var(--slate); }
.breakdown-score { font-size: 24px; font-weight: 800; }
.breakdown-bar-track { width: 100%; height: 6px; background: var(--lavender-soft); border-radius: 99px; overflow: hidden; }
.breakdown-bar-fill { height: 100%; border-radius: 99px; transition: width 0.6s; }

/* Bars */
.bars-card { }
.section-header { display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; border-bottom: 1.5px solid var(--lavender-soft); margin-bottom: 20px; }
.section-title { font-size: 18px; font-weight: 700; color: var(--plum); }
.bars-list { display: flex; flex-direction: column; gap: 0; }
.result-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.result-bar-label { width: 160px; font-size: 13px; font-weight: 600; color: var(--plum); flex-shrink: 0; }
.result-bar-track { flex: 1; height: 8px; background: var(--lavender-soft); border-radius: 99px; overflow: hidden; }
.result-bar-fill { height: 100%; border-radius: 99px; background: linear-gradient(90deg, var(--lavender-deep), var(--lavender-mid)); transition: width 0.6s; }
.result-bar-value { font-size: 12px; font-weight: 700; color: var(--slate); width: 28px; text-align: right; }

/* Top Bias */
.top-bias-card { border: 2px solid var(--lavender); background: var(--lavender-soft); }
.top-bias-header { display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }
.top-bias-name { font-size: 22px; font-weight: 800; color: var(--plum); margin: 0; }
.top-bias-text { font-size: 14px; color: var(--slate); line-height: 1.6; margin: 0 0 16px; }
.top-bias-indicators { display: flex; flex-direction: column; gap: 8px; }
.indicator { display: flex; align-items: center; gap: 10px; font-size: 14px; color: var(--plum); }
.indicator-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--lavender-deep); flex-shrink: 0; }

/* Recommendations */
.recommendations { display: flex; flex-direction: column; gap: 16px; }
.rec-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }
.rec-card { display: flex; flex-direction: column; gap: 12px; }
.rec-icon { font-size: 28px; color: var(--lavender-deep); display: flex; align-items: center; }
.rec-content { flex: 1; }
.rec-title { font-size: 15px; font-weight: 700; color: var(--plum); margin: 0 0 6px; }
.rec-desc { font-size: 13px; color: var(--slate); line-height: 1.5; margin: 0; }

/* Actions */
.actions-bar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; justify-content: center; padding: 20px 0; }
</style>
