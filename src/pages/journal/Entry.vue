<template>
  <div class="entry-page">

    <!-- Loading -->
    <div v-if="loading" class="state-center">
      <Loader :size="28" class="spin-icon" />
      <p>Loading entry…</p>
    </div>

    <!-- Not found -->
    <div v-else-if="notFound" class="state-center">
      <p>Entry not found.</p>
      <router-link to="/journal" class="btn btn-ghost btn-sm">← Back to Journal</router-link>
    </div>

    <template v-else-if="entry">
      <!-- Breadcrumb + Back -->
      <div class="page-top">
        <div class="breadcrumb">
          <router-link to="/journal" class="bc-link">Journal</router-link>
          <span class="bc-sep">/</span>
          <span class="bc-current">{{ formattedDate }}</span>
        </div>
        <router-link to="/journal" class="btn btn-ghost btn-sm"><ArrowLeft :size="14" /> Back</router-link>
      </div>

      <div class="entry-layout">

        <!-- Main Column -->
        <div class="main-col">

          <!-- Entry Header Card -->
          <div class="card header-card">
            <div class="header-meta">
              <span class="entry-date-full">{{ formattedDate }}</span>
              <span class="entry-dot">·</span>
              <span class="entry-time">{{ formattedTime }}</span>
            </div>
            <h1 class="entry-title">{{ entry.prompt_used || 'Journal Entry' }}</h1>
            <div v-if="emotions.length" class="theme-tags">
              <span v-for="theme in emotions.slice(0, 4)" :key="theme" class="theme-tag">{{ theme }}</span>
            </div>
          </div>

          <!-- Entry Content Card -->
          <div class="card content-card">
            <div class="entry-content" v-html="formattedContent"></div>
          </div>

          <!-- Action Bar -->
          <div class="action-bar">
            <button class="btn btn-danger btn-sm" :disabled="deleting" @click="handleDelete">
              <Trash2 :size="14" /> {{ deleting ? 'Deleting…' : 'Delete' }}
            </button>
          </div>

        </div>

        <!-- Sidebar: AI Analysis -->
        <div class="sidebar">
          <div class="card ai-card">
            <div class="ai-header">
              <Sparkles :size="16" class="ai-sparkle" />
              <span class="ai-title">Sentio Analysis</span>
            </div>

            <!-- Biases detected -->
            <div v-if="analysisProcessing" class="no-analysis pending">
              <Loader :size="14" class="spin-icon-sm" />
              <p>Analysis is processing… check back shortly.</p>
            </div>
            <div v-else-if="detectedBiases.length" class="bias-list">
              <div v-for="bias in detectedBiases" :key="bias.id" class="bias-row">
                <div class="bias-row-top">
                  <span class="badge badge-lavender">{{ bias.name }}</span>
                  <span class="bias-score">{{ bias.score }}/10</span>
                </div>
                <p v-if="bias.note" class="bias-note">{{ bias.note }}</p>
                <router-link :to="`/explore/${bias.slug}`" class="btn btn-secondary btn-sm explore-btn">
                  Explore <ArrowRight :size="12" />
                </router-link>
              </div>
            </div>
            <div v-else class="no-analysis">
              <p>No strong bias patterns detected in this entry.</p>
            </div>

            <div class="divider"></div>

            <div class="insight-section">
              <div class="insight-label">
                <Lightbulb :size="14" style="display:inline-block;vertical-align:middle;margin-right:4px;" />
                Sentiment
              </div>
              <p class="insight-text">
                <template v-if="entry.sentiment_score != null">
                  <template v-if="entry.sentiment_score > 0.2">Positive tone</template>
                  <template v-else-if="entry.sentiment_score < -0.2">Challenging tone</template>
                  <template v-else>Neutral tone</template>
                  <span v-if="Math.abs(entry.sentiment_score) > 0.05" class="sentiment-val">
                    ({{ entry.sentiment_score > 0 ? '+' : '' }}{{ (entry.sentiment_score * 100).toFixed(0) }})
                  </span>
                </template>
                <template v-else>Sentiment analysis pending.</template>
              </p>
            </div>
          </div>
        </div>

      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useJournalStore } from '@/stores/journal.js'
import { Sparkles, ArrowLeft, ArrowRight, Trash2, Lightbulb, Loader } from 'lucide-vue-next'
import { marked } from 'marked'

marked.setOptions({ breaks: true, gfm: true })

const route = useRoute()
const router = useRouter()
const journalStore = useJournalStore()

const loading = ref(true)
const deleting = ref(false)
const notFound = ref(false)

onMounted(async () => {
  const data = await journalStore.fetchEntry(route.params.id)
  if (!data) notFound.value = true
  loading.value = false
})

const entry = computed(() => journalStore.currentEntry)

const formattedDate = computed(() => {
  if (!entry.value?.created_at) return ''
  return new Date(entry.value.created_at).toLocaleDateString('en-US', {
    month: 'long', day: 'numeric', year: 'numeric'
  })
})

const formattedTime = computed(() => {
  if (!entry.value?.created_at) return ''
  return new Date(entry.value.created_at).toLocaleTimeString('en-US', {
    hour: 'numeric', minute: '2-digit'
  })
})

// null → background task hasn't completed; [] → completed, no biases found
const analysisProcessing = computed(() => entry.value?.detected_biases == null)

// Normalise detected_biases array from the API
const detectedBiases = computed(() => {
  const raw = entry.value?.detected_biases || []
  return raw.map(b => ({
    id: b.bias_id || b.bias || '',
    name: (b.bias_id || b.bias || '')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase()),
    score: Math.round((b.confidence ?? 0.5) * 10 * 10) / 10,
    note: b.explanation || b.note || '',
    slug: (b.bias_id || b.bias || '').replace(/_/g, '-'),
  }))
})

const emotions = computed(() => entry.value?.themes || [])

const formattedContent = computed(() => {
  if (!entry.value?.content) return ''
  return marked.parse(entry.value.content)
})

async function handleDelete() {
  if (!confirm('Permanently delete this journal entry?')) return
  deleting.value = true
  const ok = await journalStore.deleteEntry(route.params.id)
  if (ok) router.push('/journal')
  else deleting.value = false
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.entry-page { display: flex; flex-direction: column; gap: 24px; }

/* Breadcrumb */
.page-top { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
.breadcrumb { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.bc-link { color: var(--lavender-deep); font-weight: 600; text-decoration: none; }
.bc-link:hover { text-decoration: underline; }
.bc-sep { color: var(--slate); }
.bc-current { color: var(--slate); }

/* Buttons */
.btn { display: inline-flex; align-items: center; gap: 6px; font-family: 'Urbanist'; font-weight: 600; border: none; cursor: pointer; transition: all 0.18s; outline: none; text-decoration: none; }
.btn-ghost { background: transparent; color: var(--plum); border: 1.5px solid var(--lavender); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-ghost:hover { background: var(--lavender-soft); }
.btn-secondary { background: var(--lavender); color: var(--plum); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-secondary:hover { background: var(--lavender-mid); }
.btn-sm { padding: 6px 14px !important; font-size: 13px !important; border-radius: 8px !important; }
.btn-danger { background: #fee2e2; color: #dc2626; border: none; padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-danger:hover { background: #fecaca; }

/* Cards */
.card { background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(53,43,56,0.07); padding: 28px; }
.badge { font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 99px; display: inline-flex; align-items: center; }
.badge-lavender { background: var(--lavender); color: var(--plum); }

/* Layout */
.entry-layout { display: grid; grid-template-columns: 1fr 300px; gap: 24px; align-items: start; }
@media (max-width: 900px) { .entry-layout { grid-template-columns: 1fr; } }

.main-col { display: flex; flex-direction: column; gap: 20px; }

/* Header Card */
.header-card { background: linear-gradient(135deg, var(--lavender-soft), white); }
.header-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.entry-date-full { font-size: 13px; font-weight: 600; color: var(--slate); }
.entry-dot { color: var(--slate); }
.entry-time { font-size: 13px; color: var(--slate); }
.entry-mood-large { font-size: 32px; margin-bottom: 8px; }
.entry-title { font-size: 24px; font-weight: 700; color: var(--plum); margin: 0; }

/* Content */
.content-card { padding: 32px; }
.entry-content { font-size: 15px; line-height: 1.8; color: var(--plum); }
.entry-content :deep(p) { margin: 0 0 14px; }
.entry-content :deep(p:last-child) { margin-bottom: 0; }
.entry-content :deep(h1) { font-size: 22px; font-weight: 800; margin: 0 0 14px; color: var(--plum); }
.entry-content :deep(h2) { font-size: 18px; font-weight: 700; margin: 24px 0 10px; color: var(--plum); border-bottom: 1px solid var(--lavender-soft); padding-bottom: 6px; }
.entry-content :deep(h3) { font-size: 15px; font-weight: 700; margin: 18px 0 8px; color: var(--plum); }
.entry-content :deep(strong) { font-weight: 700; }
.entry-content :deep(em) { font-style: italic; }
.entry-content :deep(ul), .entry-content :deep(ol) { padding-left: 22px; margin: 0 0 14px; }
.entry-content :deep(li) { margin-bottom: 4px; }
.entry-content :deep(blockquote) { border-left: 3px solid var(--lavender-deep); padding: 4px 16px; margin: 12px 0; color: var(--slate); font-style: italic; background: var(--lavender-soft); border-radius: 0 8px 8px 0; }
.entry-content :deep(code) { font-family: 'Courier New', monospace; font-size: 13px; background: var(--lavender-soft); color: var(--plum); padding: 2px 6px; border-radius: 4px; }
.entry-content :deep(pre) { background: #2d2b3a; border-radius: 10px; padding: 18px; overflow-x: auto; margin: 14px 0; }
.entry-content :deep(pre code) { background: none; color: #e2e0ff; padding: 0; font-size: 13px; line-height: 1.6; }
.entry-content :deep(hr) { border: none; border-top: 1px solid var(--lavender); margin: 24px 0; }
.entry-content :deep(a) { color: var(--lavender-deep); text-decoration: underline; }
.entry-content :deep(.bias-mark) { background: var(--lavender); color: var(--plum); padding: 2px 4px; border-radius: 4px; font-style: normal; cursor: help; border-bottom: 2px solid var(--lavender-deep); }

/* Action Bar */
.action-bar { display: flex; gap: 12px; align-items: center; }

/* Sidebar */
.sidebar {}
.ai-card { display: flex; flex-direction: column; gap: 20px; }
.ai-header { display: flex; align-items: center; gap: 8px; }
.ai-title { font-size: 15px; font-weight: 700; color: var(--plum); }

.bias-list { display: flex; flex-direction: column; gap: 16px; }
.bias-row { display: flex; flex-direction: column; gap: 6px; }
.bias-row-top { display: flex; align-items: center; justify-content: space-between; }
.bias-score { font-size: 12px; font-weight: 700; color: var(--lavender-deep); }
.bias-note { font-size: 12px; color: var(--slate); margin: 0; line-height: 1.4; }
.explore-btn { align-self: flex-start; }

.divider { height: 1px; background: var(--lavender-soft); }

.insight-section { display: flex; flex-direction: column; gap: 8px; }
.insight-label { font-size: 13px; font-weight: 700; color: var(--plum); display: flex; align-items: center; }
.ai-sparkle { color: var(--lavender-deep); }
.insight-text { font-size: 13px; color: var(--slate); line-height: 1.6; margin: 0; }

.state-center { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; padding: 80px 0; color: var(--slate); font-size: 15px; }
.spin-icon { animation: spin 1s linear infinite; color: var(--lavender-deep); }
@keyframes spin { to { transform: rotate(360deg); } }

.theme-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.theme-tag { font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 99px; background: var(--lavender-soft); color: var(--plum); }

.no-analysis { font-size: 13px; color: var(--slate); background: var(--lavender-soft); border-radius: 10px; padding: 14px; line-height: 1.5; }
.no-analysis p { margin: 0; }
.no-analysis.pending { display: flex; align-items: center; gap: 8px; }
.spin-icon-sm { animation: spin 1s linear infinite; color: var(--lavender-deep); flex-shrink: 0; }
.sentiment-val { opacity: 0.7; font-size: 11px; margin-left: 4px; }
</style>
