<template>
  <div class="topic-page">

    <div v-if="loading" class="state-center">Loading…</div>
    <div v-else-if="error" class="state-center error">{{ error }}</div>

    <template v-else>
      <!-- Header -->
      <div class="topic-header" :style="{ '--accent': topic.color || '#9b94e8' }">
        <router-link to="/community" class="back-link">
          <ArrowLeft :size="16" /> Community
        </router-link>
        <div class="topic-title-row">
          <div class="topic-icon-wrap">
            <component :is="iconMap[topic.icon] || MessageCircle" :size="22" />
          </div>
          <div>
            <h1 class="topic-title">{{ topic.title }}</h1>
            <p class="topic-desc">{{ topic.description }}</p>
          </div>
        </div>
      </div>

      <!-- New thread button + form -->
      <div class="thread-actions">
        <button class="btn btn-primary" @click="showForm = !showForm">
          <Plus :size="15" /> New Thread
        </button>
      </div>

      <div v-if="showForm" class="card new-thread-form">
        <div class="form-title">Start a new thread</div>
        <input v-model="newTitle" class="input" placeholder="Thread title…" maxlength="120" />
        <textarea v-model="newBody" class="input body-input" placeholder="Share your thoughts…" rows="4"></textarea>
        <div v-if="formError" class="form-error">{{ formError }}</div>
        <div class="form-actions">
          <button class="btn btn-primary btn-sm" @click="submitThread" :disabled="submitting">
            {{ submitting ? 'Posting…' : 'Post Thread' }}
          </button>
          <button class="btn btn-ghost btn-sm" @click="cancelForm">Cancel</button>
        </div>
      </div>

      <!-- Thread list -->
      <div v-if="!threads.length" class="state-center">No threads yet. Start the conversation!</div>

      <div class="threads-list">
        <router-link
          v-for="t in threads"
          :key="t.id"
          :to="`/community/${topicSlug}/${t.id}`"
          class="thread-row"
          :class="{ pinned: t.is_pinned }"
        >
          <div class="thread-main">
            <div class="thread-title-row">
              <span v-if="t.is_pinned" class="pin-badge">📌 Pinned</span>
              <span class="thread-title">{{ t.title }}</span>
            </div>
            <div class="thread-meta">
              by {{ authorName(t) }} · {{ timeAgo(t.created_at) }}
            </div>
          </div>
          <div class="thread-stats">
            <span class="stat"><MessageSquare :size="13" /> {{ t.reply_count || 0 }}</span>
            <span class="stat"><ThumbsUp :size="13" /> {{ t.upvotes || 0 }}</span>
          </div>
        </router-link>
      </div>

      <!-- Pagination -->
      <div v-if="threads.length === PAGE_SIZE || page > 1" class="pagination">
        <button class="btn btn-ghost btn-sm" :disabled="page <= 1" @click="changePage(page - 1)">← Prev</button>
        <span class="page-label">Page {{ page }}</span>
        <button class="btn btn-ghost btn-sm" :disabled="threads.length < PAGE_SIZE" @click="changePage(page + 1)">Next →</button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, Plus, MessageSquare, ThumbsUp, MessageCircle, Eye, Scale, BookOpen, Zap, HelpCircle } from 'lucide-vue-next'
import apiClient from '@/api/client.js'

const iconMap = { Eye, Scale, BookOpen, Zap, HelpCircle, MessageCircle }
const PAGE_SIZE = 20

const route = useRoute()
const topicSlug = ref(route.params.topicSlug)

const topic = ref({})
const threads = ref([])
const loading = ref(true)
const error = ref('')
const page = ref(1)

const showForm = ref(false)
const newTitle = ref('')
const newBody = ref('')
const submitting = ref(false)
const formError = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await apiClient.get(`/community/topics/${topicSlug.value}?page=${page.value}`)
    topic.value = res.data.topic
    threads.value = res.data.threads || []
  } catch (e) {
    error.value = e.message || 'Failed to load topic.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => route.params.topicSlug, (slug) => { topicSlug.value = slug; load() })

function changePage(p) {
  page.value = p
  load()
  window.scrollTo({ top: 0 })
}

function authorName(t) {
  return t.profiles?.display_name || t.profiles?.full_name || 'Anonymous'
}

function timeAgo(iso) {
  if (!iso) return ''
  const diff = Date.now() - new Date(iso).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 60) return `${m || 1}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

async function submitThread() {
  formError.value = ''
  if (!newTitle.value.trim()) { formError.value = 'Title is required.'; return }
  if (!newBody.value.trim()) { formError.value = 'Body is required.'; return }
  submitting.value = true
  try {
    await apiClient.post(`/community/topics/${topicSlug.value}/threads`, {
      title: newTitle.value.trim(),
      body: newBody.value.trim(),
    })
    cancelForm()
    load()
  } catch (e) {
    formError.value = e.message || 'Failed to post thread.'
  } finally {
    submitting.value = false
  }
}

function cancelForm() {
  showForm.value = false
  newTitle.value = ''
  newBody.value = ''
  formError.value = ''
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,400;0,500;0,600;0,700;0,800&display=swap');
* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.topic-page { display: flex; flex-direction: column; gap: 20px; }
.state-center { text-align: center; padding: 60px; color: var(--slate); font-size: 15px; }
.error { color: #dc2626; }

.back-link { display: inline-flex; align-items: center; gap: 6px; color: var(--slate); text-decoration: none; font-size: 13px; font-weight: 600; margin-bottom: 16px; }
.back-link:hover { color: var(--plum); }

.topic-header {}
.topic-title-row { display: flex; align-items: center; gap: 16px; }
.topic-icon-wrap {
  width: 48px; height: 48px; flex-shrink: 0; border-radius: 14px;
  background: color-mix(in srgb, var(--accent, #9b94e8) 18%, white);
  color: var(--accent, #9b94e8);
  display: flex; align-items: center; justify-content: center;
}
.topic-title { font-size: 24px; font-weight: 800; color: var(--plum); margin: 0 0 4px; }
.topic-desc { font-size: 14px; color: var(--slate); margin: 0; }

.thread-actions { display: flex; justify-content: flex-end; }

.card { background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(53,43,56,0.07); padding: 24px; }
.new-thread-form { display: flex; flex-direction: column; gap: 12px; }
.form-title { font-size: 16px; font-weight: 700; color: var(--plum); }
.input { font-family: 'Urbanist'; font-size: 14px; color: var(--plum); border: 1.5px solid var(--lavender); border-radius: 10px; padding: 10px 14px; outline: none; width: 100%; }
.input:focus { border-color: var(--lavender-deep); box-shadow: 0 0 0 3px rgba(155,148,232,0.15); }
.body-input { resize: vertical; min-height: 80px; }
.form-error { font-size: 12px; color: #dc2626; }
.form-actions { display: flex; gap: 10px; }

.btn { display: inline-flex; align-items: center; gap: 6px; font-family: 'Urbanist'; font-weight: 600; border: none; cursor: pointer; transition: all 0.15s; }
.btn-primary { background: var(--plum); color: white; padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-primary:hover:not(:disabled) { background: #4a3550; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-ghost { background: transparent; color: var(--plum); border: 1.5px solid var(--lavender); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-ghost:hover:not(:disabled) { background: var(--lavender-soft); }
.btn-ghost:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-sm { padding: 6px 14px !important; font-size: 13px !important; border-radius: 8px !important; }

.threads-list { display: flex; flex-direction: column; gap: 8px; }
.thread-row {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  background: white; border-radius: 12px;
  box-shadow: 0 2px 12px rgba(53,43,56,0.06);
  padding: 16px 20px; text-decoration: none; color: inherit;
  transition: transform 0.12s, box-shadow 0.12s;
}
.thread-row:hover { transform: translateY(-1px); box-shadow: 0 6px 24px rgba(53,43,56,0.10); }
.thread-row.pinned { border-left: 3px solid #f59e0b; }

.thread-main { flex: 1; min-width: 0; }
.thread-title-row { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.pin-badge { font-size: 11px; font-weight: 700; }
.thread-title { font-size: 15px; font-weight: 600; color: var(--plum); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.thread-meta { font-size: 12px; color: var(--slate); }

.thread-stats { display: flex; gap: 14px; flex-shrink: 0; }
.stat { display: flex; align-items: center; gap: 4px; font-size: 12px; font-weight: 600; color: var(--slate); }

.pagination { display: flex; align-items: center; justify-content: center; gap: 16px; padding: 8px 0; }
.page-label { font-size: 13px; color: var(--slate); font-weight: 600; }
</style>
