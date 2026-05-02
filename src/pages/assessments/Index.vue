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

    <!-- Assessment Grid -->
    <div class="assessment-grid">
      <div
        v-for="a in filteredAssessments"
        :key="a.id"
        class="assessment-card card"
        :style="{ borderTop: `4px solid ${a.color}` }"
      >
        <div class="card-top">
          <span class="card-emoji">{{ a.emoji }}</span>
          <span class="badge badge-lavender">{{ a.category }}</span>
        </div>
        <h3 class="card-title">{{ a.title }}</h3>
        <p class="card-desc">{{ a.description }}</p>
        <div class="card-stats">
          <span class="stat-item">⏱ {{ a.time }} min</span>
          <span class="stat-item">❓ {{ a.questions }} questions</span>
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
          <span class="badge badge-green">✓ Completed</span>
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeTab = ref('Available')
const tabs = ['Available', 'In Progress', 'Completed']

const assessments = ref([
  { id: 1, title: 'Cognitive Bias Inventory', emoji: '🧠', category: 'Core', status: 'available', time: 12, questions: 20, color: '#dad8f9', description: 'A comprehensive test covering 10 major cognitive biases. Establishes your baseline profile.' },
  { id: 2, title: 'Decision Making Patterns', emoji: '⚡', category: 'Decision', status: 'in-progress', time: 8, questions: 15, progress: 60, color: '#d8edf9', description: 'Explore how you make decisions under uncertainty and time pressure.' },
  { id: 3, title: 'Social Bias Audit', emoji: '👥', category: 'Social', status: 'completed', time: 10, questions: 18, score: 72, color: '#f9d8f0', description: 'How do your social biases affect relationships and group dynamics?' },
  { id: 4, title: 'Memory Reliability Test', emoji: '📚', category: 'Memory', status: 'available', time: 7, questions: 12, color: '#d8f9e8', description: 'Test how reliable your memory is and discover recency and availability biases.' },
  { id: 5, title: 'Financial Bias Scan', emoji: '💰', category: 'Money', status: 'available', time: 6, questions: 10, color: '#fef9c3', description: 'Uncover biases affecting your financial decisions and risk assessment.' },
  { id: 6, title: 'Self-Perception Audit', emoji: '🪞', category: 'Self', status: 'available', time: 9, questions: 14, color: '#dad8f9', description: 'How accurate is your self-image? Explore overconfidence and imposter syndrome patterns.' },
  { id: 7, title: 'Relationship Patterns', emoji: '❤️', category: 'Social', status: 'available', time: 11, questions: 16, color: '#f9d8f0', description: 'Discover how cognitive biases shape your romantic and platonic relationships.' },
  { id: 8, title: 'Critical Thinking Challenge', emoji: '🔬', category: 'Logic', status: 'available', time: 15, questions: 25, color: '#d8edf9', description: 'A challenging test of logical reasoning and susceptibility to common fallacies.' },
])

function countByStatus(tab) {
  const map = { 'Available': 'available', 'In Progress': 'in-progress', 'Completed': 'completed' }
  return assessments.value.filter(a => a.status === map[tab]).length
}

const filteredAssessments = computed(() => {
  const map = { 'Available': 'available', 'In Progress': 'in-progress', 'Completed': 'completed' }
  return assessments.value.filter(a => a.status === map[activeTab.value])
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
.card-emoji { font-size: 28px; }
.card-title { font-size: 16px; font-weight: 700; color: var(--plum); margin: 0; line-height: 1.3; }
.card-desc { font-size: 13px; color: var(--slate); margin: 0; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card-stats { display: flex; gap: 16px; }
.stat-item { font-size: 12px; color: var(--slate); font-weight: 500; }

/* Progress */
.progress-wrap { display: flex; flex-direction: column; gap: 6px; }
.progress-track { height: 6px; background: var(--lavender-soft); border-radius: 99px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, var(--lavender-deep), var(--lavender-mid)); border-radius: 99px; transition: width 0.3s; }
.progress-label { font-size: 11px; color: var(--slate); font-weight: 600; }

/* Completed */
.completed-row { display: flex; align-items: center; gap: 10px; }
.score-label { font-size: 12px; font-weight: 700; color: var(--plum); }

.card-action { margin-top: auto; }
</style>
