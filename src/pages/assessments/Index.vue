<template>
  <div class="assessments-page">

    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Assessments</h1>
        <p class="page-desc">Discover and measure your cognitive bias patterns through evidence-based tests.</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs-bar">
      <button
        v-for="tab in tabs"
        :key="tab"
        class="tab-btn"
        :class="{ active: activeTab === tab }"
        @click="activeTab = tab"
      >
        {{ tab }}
        <span class="tab-count">{{ countByStatus(tab) }}</span>
      </button>
    </div>

    <!-- Skeleton loading state -->
    <div v-if="assessmentStore.loading" class="assessment-grid">
      <div v-for="n in 4" :key="n" class="assessment-card card skeleton-assessment">
        <div class="skeleton sk-emoji"></div>
        <div class="skeleton sk-atitle"></div>
        <div class="skeleton sk-adesc"></div>
        <div class="skeleton sk-stats"></div>
      </div>
    </div>

    <!-- Assessment Grid -->
    <div v-else class="assessment-grid">
      <div
        v-for="a in displayAssessments"
        :key="a.id"
        class="assessment-card card"
        :style="{ borderTop: `4px solid ${a.color}` }"
      >
        <div class="card-top">
          <span class="card-icon"><component :is="a.icon" :size="28" /></span>
          <span class="badge badge-lavender">{{ a.category }}</span>
        </div>
        <h3 class="card-title">{{ a.title }}</h3>
        <p class="card-desc">{{ a.description }}</p>
        <div class="card-stats">
          <span class="stat-item"><Clock :size="12" /> {{ a.time }} min</span>
          <span class="stat-item"><HelpCircle :size="12" /> {{ a.questions }} questions</span>
        </div>

        <!-- Progress bar for in-progress -->
        <div v-if="a.status === 'in-progress'" class="progress-wrap">
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: a.progress + '%' }"></div>
          </div>
          <span class="progress-label">{{ a.progress }}% complete</span>
        </div>

        <!-- Completed badge -->
        <div v-if="a.status === 'completed'" class="completed-row">
          <span class="badge badge-green"><CheckCircle :size="11" style="margin-right:3px;" /> Completed</span>
          <span class="score-label">Score: {{ a.score }}/100</span>
        </div>

        <div class="card-action">
          <router-link
            v-if="a.status === 'available'"
            :to="`/assessments/${a.id}`"
            class="btn btn-primary btn-sm"
          >Start</router-link>
          <router-link
            v-else-if="a.status === 'in-progress'"
            :to="`/assessments/${a.id}`"
            class="btn btn-secondary btn-sm"
          >Continue</router-link>
          <router-link
            v-else
            :to="`/assessments/${a.id}/results`"
            class="btn btn-ghost btn-sm"
          >Review</router-link>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAssessmentStore } from '@/stores/assessment.js'
import { Clock, HelpCircle, CheckCircle, Brain, Zap, Users, BookMarked, DollarSign, Scan, Heart, Microscope } from 'lucide-vue-next'

const router = useRouter()
const assessmentStore = useAssessmentStore()

const activeTab = ref('Available')
const tabs = ['Available', 'In Progress', 'Completed']

onMounted(() => {
  assessmentStore.fetchList()
})

// Display metadata keyed by slug (from seed_assessments.py)
const ASSESSMENT_META = {
  'cognitive-bias-inventory': { icon: Brain,      color: '#dad8f9', category: 'Core' },
  'need-for-cognition':       { icon: Microscope, color: '#d8edf9', category: 'Thinking' },
  'metacognitive-awareness':  { icon: Scan,       color: '#d8f9e8', category: 'Self' },
}

function enrichAssessment(a) {
  const meta = ASSESSMENT_META[a.slug] || { icon: Brain, color: '#dad8f9', category: 'General' }
  const qCount = Array.isArray(a.questions) ? a.questions.length : (a.question_count || '?')
  return {
    ...a,
    icon: meta.icon,
    color: meta.color,
    category: a.category || meta.category,
    time: a.estimated_minutes || 10,
    questions: qCount,
    status: a.completed ? 'completed' : 'available',
  }
}

const enrichedAssessments = computed(() =>
  assessmentStore.assessments.length > 0
    ? assessmentStore.assessments.map(enrichAssessment)
    : []
)

function countByStatus(tab) {
  const map = { 'Available': 'available', 'In Progress': 'in-progress', 'Completed': 'completed' }
  return enrichedAssessments.value.filter(a => a.status === map[tab]).length
}

const displayAssessments = computed(() => {
  const map = { 'Available': 'available', 'In Progress': 'in-progress', 'Completed': 'completed' }
  return enrichedAssessments.value.filter(a => a.status === map[activeTab.value])
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.assessments-page { display: flex; flex-direction: column; gap: 28px; }

.page-header { display: flex; align-items: flex-start; justify-content: space-between; }
.page-title { font-size: 28px; font-weight: 800; color: var(--plum); margin: 0 0 6px; }
.page-desc { font-size: 14px; color: var(--slate); margin: 0; }

/* Buttons */
.btn { display: inline-flex; align-items: center; gap: 6px; font-family: 'Urbanist'; font-weight: 600; border: none; cursor: pointer; transition: all 0.18s; outline: none; text-decoration: none; }
.btn-primary { background: var(--plum); color: white; padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-primary:hover { background: #4a3550; transform: translateY(-1px); }
.btn-secondary { background: var(--lavender); color: var(--plum); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-secondary:hover { background: var(--lavender-mid); }
.btn-ghost { background: transparent; color: var(--plum); border: 1.5px solid var(--lavender); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-ghost:hover { background: var(--lavender-soft); }
.btn-sm { padding: 6px 14px !important; font-size: 13px !important; border-radius: 8px !important; }

/* Cards */
.card { background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(53,43,56,0.07); padding: 20px; }
.badge { font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 99px; display: inline-flex; align-items: center; }
.badge-lavender { background: var(--lavender); color: var(--plum); }
.badge-green { background: #d1fae5; color: #059669; }

/* Tabs */
.tabs-bar { display: flex; gap: 4px; background: white; border: 1.5px solid var(--lavender); border-radius: 12px; padding: 5px; width: fit-content; }
.tab-btn { font-family: 'Urbanist'; font-size: 13px; font-weight: 600; padding: 7px 18px; border-radius: 8px; border: none; background: transparent; color: var(--slate); cursor: pointer; transition: all 0.15s; display: flex; align-items: center; gap: 6px; }
.tab-btn.active { background: var(--plum); color: white; }
.tab-btn:hover:not(.active) { background: var(--lavender-soft); color: var(--plum); }
.tab-count { font-size: 11px; font-weight: 700; background: rgba(255,255,255,0.3); padding: 1px 6px; border-radius: 99px; }
.tab-btn.active .tab-count { background: rgba(255,255,255,0.2); }
.tab-btn:not(.active) .tab-count { background: var(--lavender-soft); color: var(--slate); }

/* Grid */
.assessment-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }

.assessment-card { display: flex; flex-direction: column; gap: 12px; border-radius: 16px; transition: box-shadow 0.18s, transform 0.18s; overflow: hidden; }
.assessment-card:hover { box-shadow: 0 8px 32px rgba(53,43,56,0.10); transform: translateY(-2px); }

.card-top { display: flex; align-items: center; justify-content: space-between; }
.card-icon { color: var(--lavender-deep); display: flex; align-items: center; }
.stat-item { font-size: 12px; color: var(--slate); font-weight: 500; display: inline-flex; align-items: center; gap: 4px; }
.card-title { font-size: 16px; font-weight: 700; color: var(--plum); margin: 0; line-height: 1.3; }
.card-desc { font-size: 13px; color: var(--slate); margin: 0; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card-stats { display: flex; gap: 16px; }

/* Progress */
.progress-wrap { display: flex; flex-direction: column; gap: 6px; }
.progress-track { height: 6px; background: var(--lavender-soft); border-radius: 99px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, var(--lavender-deep), var(--lavender-mid)); border-radius: 99px; transition: width 0.3s; }
.progress-label { font-size: 11px; color: var(--slate); font-weight: 600; }

/* Completed */
.completed-row { display: flex; align-items: center; gap: 10px; }
.score-label { font-size: 12px; font-weight: 700; color: var(--plum); }

.card-action { margin-top: auto; }

/* Skeleton */
.skeleton-assessment { pointer-events: none; gap: 12px; }
.skeleton {
  background: var(--lavender); border-radius: 8px;
  animation: a-pulse 1.4s ease-in-out infinite;
}
.sk-emoji  { height: 36px; width: 36px; border-radius: 50%; }
.sk-atitle { height: 18px; width: 60%; }
.sk-adesc  { height: 32px; width: 100%; }
.sk-stats  { height: 14px; width: 50%; }
@keyframes a-pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 0.3; } }
</style>
