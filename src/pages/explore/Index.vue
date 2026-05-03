<template>
  <div class="explore-page">

    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">Bias Explorer</h1>
      <p class="page-desc">Discover and understand the cognitive biases shaping your world</p>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <!-- Search -->
      <div class="input-icon-wrap">
        <Search :size="14" class="input-icon" />
        <input
          v-model="search"
          type="text"
          class="search-input"
          placeholder="Search biases..."
        />
      </div>

      <!-- Category tabs -->
      <div class="category-tabs">
        <button
          v-for="cat in categories"
          :key="cat"
          class="cat-tab"
          :class="{ active: selectedCategory === cat }"
          @click="selectedCategory = cat"
        >{{ cat }}</button>
      </div>

      <!-- Sort -->
      <div class="sort-wrap">
        <select v-model="sortBy" class="sort-select">
          <option value="name">By Name</option>
          <option value="prevalence-desc">By Prevalence</option>
          <option value="relevance">By Relevance</option>
        </select>
      </div>
    </div>

    <!-- Results count -->
    <div class="results-meta">
      <span class="results-count">{{ displayBiases.length }} biases</span>
      <span v-if="search || selectedCategory !== 'All'" class="results-filter-label">
        — filtered by
        <strong v-if="selectedCategory !== 'All'">{{ selectedCategory }}</strong>
        <span v-if="search"> "{{ search }}"</span>
      </span>
    </div>

    <!-- Skeleton loading state -->
    <div v-if="biasStore.loading" class="bias-grid">
      <div v-for="n in 3" :key="n" class="bias-card skeleton-card">
        <div class="skeleton skeleton-top"></div>
        <div class="skeleton skeleton-title"></div>
        <div class="skeleton skeleton-desc"></div>
        <div class="skeleton skeleton-bar"></div>
      </div>
    </div>

    <!-- Bias Grid -->
    <div v-else-if="displayBiases.length" class="bias-grid">
      <div
        v-for="bias in displayBiases"
        :key="bias.id"
        class="bias-card"
        @click="router.push('/explore/' + bias.id)"
      >
        <div class="bias-card-top">
          <div class="bias-icon-circle">
            <component :is="getBiasIcon(bias.id)" :size="16" />
          </div>
          <span class="badge" :class="badgeClass(bias.categoryColor)">{{ bias.category }}</span>
          <ArrowRight :size="16" class="bias-card-arrow" />
        </div>

        <div class="bias-name">{{ bias.name }}</div>
        <div class="bias-desc">{{ bias.description }}</div>

        <div class="bias-stat">Affects ~{{ bias.prevalence }}% of decisions</div>

        <div class="progress-bar" style="margin-top: 10px;">
          <div
            class="progress-fill"
            :style="{ width: bias.prevalence + '%' }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="!biasStore.loading" class="empty-state">
      <div class="empty-icon"><Search :size="48" /></div>
      <div class="empty-title">No biases found</div>
      <div class="empty-desc">Try adjusting your search or filter</div>
      <button class="btn btn-secondary btn-sm" style="margin-top: 12px;" @click="search = ''; selectedCategory = 'All'">
        Clear filters
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBiasStore } from '@/stores/bias.js'
import {
  Search, ArrowRight, Brain, Anchor, TrendingDown, Star, Calendar,
  Lock, Users, BookMarked, Scan, Megaphone, HandHelping, Sparkles,
  BarChart2, Zap
} from 'lucide-vue-next'

const router = useRouter()
const biasStore = useBiasStore()

const categories = ['All', 'Memory', 'Social', 'Decision', 'Belief', 'Money', 'Self']
const selectedCategory = ref('All')
const search = ref('')
const sortBy = ref('name')

onMounted(() => {
  // Try to load from API; fall back to hardcoded biases if API isn't available
  biasStore.fetchAll().catch(() => {})
})

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

function getBiasIcon(id) {
  return biasIconMap[id] || Brain
}

const biases = ref([
  { id: 'confirmation-bias', name: 'Confirmation Bias', category: 'Belief', categoryColor: 'lavender', description: 'The tendency to search for and favor information that confirms existing beliefs.', prevalence: 85 },
  { id: 'availability-heuristic', name: 'Availability Heuristic', category: 'Memory', categoryColor: 'blue', description: 'Judging probability based on how easily examples come to mind.', prevalence: 72 },
  { id: 'anchoring-bias', name: 'Anchoring Bias', category: 'Decision', categoryColor: 'pink', description: 'Over-relying on the first piece of information encountered.', prevalence: 78 },
  { id: 'dunning-kruger', name: 'Dunning-Kruger Effect', category: 'Self', categoryColor: 'yellow', description: 'Overestimating ability when knowledge is limited; underestimating when expertise grows.', prevalence: 90 },
  { id: 'sunk-cost', name: 'Sunk Cost Fallacy', category: 'Money', categoryColor: 'green', description: 'Continuing a behavior due to past investments rather than future value.', prevalence: 68 },
  { id: 'halo-effect', name: 'Halo Effect', category: 'Social', categoryColor: 'pink', description: 'Letting one positive trait influence overall judgment of a person or thing.', prevalence: 75 },
  { id: 'fundamental-attribution', name: 'Fundamental Attribution Error', category: 'Social', categoryColor: 'blue', description: 'Blaming others for their situation while attributing your own to circumstances.', prevalence: 82 },
  { id: 'bandwagon-effect', name: 'Bandwagon Effect', category: 'Social', categoryColor: 'lavender', description: 'Adopting beliefs or behaviors because many others do.', prevalence: 70 },
  { id: 'optimism-bias', name: 'Optimism Bias', category: 'Self', categoryColor: 'yellow', description: 'Overestimating likelihood of positive outcomes in our own future.', prevalence: 65 },
  { id: 'recency-bias', name: 'Recency Bias', category: 'Memory', categoryColor: 'blue', description: 'Giving more weight to recent events than older ones when making decisions.', prevalence: 73 },
  { id: 'status-quo-bias', name: 'Status Quo Bias', category: 'Decision', categoryColor: 'pink', description: 'Preferring the current state of affairs over change, even when change is beneficial.', prevalence: 71 },
  { id: 'in-group-bias', name: 'In-Group Bias', category: 'Social', categoryColor: 'lavender', description: 'Favoring members of your own group over those in other groups.', prevalence: 80 },
])

const filteredBiases = computed(() => {
  let result = biases.value.filter(b =>
    (selectedCategory.value === 'All' || b.category === selectedCategory.value) &&
    b.name.toLowerCase().includes(search.value.toLowerCase())
  )
  if (sortBy.value === 'prevalence-desc') {
    result = [...result].sort((a, b) => b.prevalence - a.prevalence)
  } else if (sortBy.value === 'name') {
    result = [...result].sort((a, b) => a.name.localeCompare(b.name))
  }
  return result
})

// When store loads biases, use them; otherwise keep hardcoded ones
const displayBiases = computed(() => {
  const source = biasStore.biases.length > 0 ? biasStore.biases : biases.value
  let result = source.filter(b =>
    (selectedCategory.value === 'All' || b.category === selectedCategory.value) &&
    b.name.toLowerCase().includes(search.value.toLowerCase())
  )
  if (sortBy.value === 'prevalence-desc') {
    result = [...result].sort((a, b) => b.prevalence - a.prevalence)
  } else if (sortBy.value === 'name') {
    result = [...result].sort((a, b) => a.name.localeCompare(b.name))
  }
  return result
})

const badgeClass = (color) => `badge-${color}`
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:wght@400;500;600;700;800;900&display=swap');

* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.explore-page { display: flex; flex-direction: column; gap: 28px; }

/* ── Page Header ── */
.page-header { }
.page-title { font-size: 28px; font-weight: 800; color: var(--plum); margin: 0 0 6px; }
.page-desc { font-size: 15px; color: var(--slate); margin: 0; }

/* ── Filter Bar ── */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  background: white;
  padding: 16px 20px;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.input-icon-wrap {
  display: flex; align-items: center; gap: 8px;
  background: var(--ghost); border: 1.5px solid var(--lavender);
  border-radius: 10px; padding: 8px 14px;
  min-width: 220px;
}
.input-icon { color: var(--slate); flex-shrink: 0; }
.search-input {
  border: none; outline: none;
  font-family: 'Urbanist', sans-serif; font-size: 14px;
  color: var(--plum); background: transparent; width: 100%;
}
.search-input::placeholder { color: var(--slate); }

.category-tabs { display: flex; gap: 4px; flex-wrap: wrap; }
.cat-tab {
  font-family: 'Urbanist', sans-serif; font-size: 13px; font-weight: 600;
  padding: 6px 14px; border-radius: 99px;
  border: 1.5px solid transparent;
  background: var(--ghost); color: var(--slate);
  cursor: pointer; transition: all 0.15s;
}
.cat-tab:hover { background: var(--lavender-soft); color: var(--plum); }
.cat-tab.active {
  background: var(--lavender); color: var(--plum);
  border-color: var(--lavender-mid);
}

.sort-wrap { margin-left: auto; }
.sort-select {
  font-family: 'Urbanist', sans-serif; font-size: 13px; font-weight: 600;
  padding: 7px 12px; border-radius: 10px;
  border: 1.5px solid var(--lavender); color: var(--plum);
  background: white; outline: none; cursor: pointer;
}

/* ── Results meta ── */
.results-meta { font-size: 13px; color: var(--slate); }
.results-count { font-weight: 700; color: var(--plum); }
.results-filter-label { font-weight: 500; }

/* ── Bias Grid ── */
.bias-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.bias-card {
  background: white; border-radius: 16px; padding: 20px;
  cursor: pointer; transition: all 0.2s;
  border: 1.5px solid transparent;
  box-shadow: var(--shadow);
}
.bias-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(53,43,56,0.12);
  border-color: var(--lavender);
}

.bias-card-top {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 12px;
}
.bias-icon-circle {
  width: 34px; height: 34px; border-radius: 99px;
  background: var(--lavender-soft);
  display: flex; align-items: center; justify-content: center;
  color: var(--lavender-deep); flex-shrink: 0;
}
.bias-card-arrow {
  margin-left: auto; color: var(--slate);
  transition: transform 0.15s;
}
.bias-card:hover .bias-card-arrow { transform: translateX(3px); color: var(--lavender-deep); }

.bias-name { font-size: 16px; font-weight: 700; color: var(--plum); margin-bottom: 6px; }
.bias-desc {
  font-size: 13px; color: var(--slate); line-height: 1.55;
  display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden;
  margin-bottom: 10px;
}
.bias-stat { font-size: 12px; font-style: italic; color: var(--slate); }

/* ── Progress Bar ── */
.progress-bar {
  height: 4px; background: var(--lavender-soft);
  border-radius: 99px; overflow: hidden;
}
.progress-fill {
  height: 100%; border-radius: 99px;
  background: linear-gradient(90deg, var(--lavender-deep), var(--lavender-mid));
  transition: width 0.6s ease;
}

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

/* ── Empty State ── */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 64px 32px;
  background: white; border-radius: var(--radius);
  box-shadow: var(--shadow);
}
.empty-icon { color: var(--slate); margin-bottom: 12px; }
.empty-title { font-size: 18px; font-weight: 700; color: var(--plum); margin-bottom: 6px; }
.empty-desc { font-size: 14px; color: var(--slate); }

/* ── Skeleton loading ── */
.skeleton-card { pointer-events: none; }
.skeleton {
  background: var(--lavender);
  border-radius: 8px;
  opacity: 0.6;
  animation: pulse 1.4s ease-in-out infinite;
}
.skeleton-top { height: 34px; width: 80px; margin-bottom: 12px; }
.skeleton-title { height: 18px; width: 70%; margin-bottom: 10px; }
.skeleton-desc { height: 32px; width: 100%; margin-bottom: 10px; }
.skeleton-bar { height: 4px; width: 100%; border-radius: 99px; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 0.3; } }

/* ── Buttons ── */
.btn {
  display: inline-flex; align-items: center; gap: 6px;
  font-family: 'Urbanist', sans-serif; font-weight: 600;
  border: none; cursor: pointer; transition: all 0.18s;
}
.btn-secondary {
  background: var(--lavender); color: var(--plum);
  padding: 10px 20px; border-radius: 10px; font-size: 14px;
}
.btn-secondary:hover { background: var(--lavender-mid); }
.btn-sm {
  padding: 6px 14px !important;
  font-size: 13px !important;
  border-radius: 8px !important;
}

svg { display: block; }
</style>
