<template>
  <div class="thread-page">

    <div v-if="loading" class="state-center">Loading…</div>
    <div v-else-if="error" class="state-center error">{{ error }}</div>

    <template v-else>
      <!-- Back navigation -->
      <router-link :to="`/community/${topicSlug}`" class="back-link">
        <ArrowLeft :size="16" /> Back to topic
      </router-link>

      <!-- Original post -->
      <div class="card post-card">
        <div class="post-header">
          <div class="author-avatar">{{ initials(thread.profiles) }}</div>
          <div class="author-info">
            <div class="author-name">{{ authorName(thread.profiles) }}</div>
            <div class="post-time">{{ timeAgo(thread.created_at) }}</div>
          </div>
          <div class="post-actions" v-if="isOwnPost(thread.author_id)">
            <button class="btn-icon-sm danger" @click="deleteThread" title="Delete thread">
              <Trash2 :size="14" />
            </button>
          </div>
        </div>
        <h1 class="post-title">{{ thread.title }}</h1>
        <p class="post-body">{{ thread.body }}</p>
        <div class="post-footer">
          <button class="upvote-btn" :class="{ active: hasUpvotedThread }" @click="toggleThreadUpvote">
            <ThumbsUp :size="14" /> {{ thread.upvotes || 0 }}
          </button>
          <span class="reply-count">{{ replies.length }} {{ replies.length === 1 ? 'reply' : 'replies' }}</span>
        </div>
      </div>

      <!-- Replies -->
      <div class="replies-section">
        <div class="replies-label">Replies</div>

        <div v-if="!replies.length" class="no-replies">No replies yet. Be the first!</div>

        <div
          v-for="reply in topLevelReplies"
          :key="reply.id"
          class="reply-thread"
        >
          <div class="card reply-card">
            <div class="post-header">
              <div class="author-avatar sm">{{ initials(reply.profiles) }}</div>
              <div class="author-info">
                <div class="author-name">{{ authorName(reply.profiles) }}</div>
                <div class="post-time">{{ timeAgo(reply.created_at) }}</div>
              </div>
              <div class="post-actions">
                <button class="btn-icon-sm" title="Reply" @click="startReply(reply.id)">
                  <CornerDownRight :size="13" />
                </button>
                <button v-if="isOwnPost(reply.author_id)" class="btn-icon-sm danger" @click="deleteReply(reply.id)" title="Delete">
                  <Trash2 :size="13" />
                </button>
              </div>
            </div>
            <p class="reply-body">{{ reply.body }}</p>
            <div class="post-footer">
              <button class="upvote-btn sm" :class="{ active: upvotedReplies.has(reply.id) }" @click="toggleReplyUpvote(reply)">
                <ThumbsUp :size="12" /> {{ reply.upvotes || 0 }}
              </button>
            </div>
          </div>

          <!-- Nested replies (1 level) -->
          <div
            v-for="child in nestedReplies(reply.id)"
            :key="child.id"
            class="card reply-card nested"
          >
            <div class="post-header">
              <div class="author-avatar sm">{{ initials(child.profiles) }}</div>
              <div class="author-info">
                <div class="author-name">{{ authorName(child.profiles) }}</div>
                <div class="post-time">{{ timeAgo(child.created_at) }}</div>
              </div>
              <div class="post-actions" v-if="isOwnPost(child.author_id)">
                <button class="btn-icon-sm danger" @click="deleteReply(child.id)"><Trash2 :size="13" /></button>
              </div>
            </div>
            <p class="reply-body">{{ child.body }}</p>
          </div>

          <!-- Inline reply form for this parent -->
          <div v-if="replyingTo === reply.id" class="inline-reply-form">
            <textarea v-model="replyBody" class="input" placeholder="Write a reply…" rows="3" />
            <div v-if="replyError" class="form-error">{{ replyError }}</div>
            <div class="form-actions">
              <button class="btn btn-primary btn-sm" @click="submitReply(reply.id)" :disabled="submitting">
                {{ submitting ? 'Posting…' : 'Reply' }}
              </button>
              <button class="btn btn-ghost btn-sm" @click="replyingTo = null">Cancel</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Top-level reply form (if thread not locked) -->
      <div v-if="!thread.is_locked" class="card new-reply-form">
        <div class="form-title">Add a reply</div>
        <textarea v-model="newReplyBody" class="input" placeholder="Share your perspective…" rows="4" />
        <div v-if="newReplyError" class="form-error">{{ newReplyError }}</div>
        <button class="btn btn-primary btn-sm" @click="submitTopReply" :disabled="submitting">
          {{ submitting ? 'Posting…' : 'Post Reply' }}
        </button>
      </div>
      <div v-else class="locked-notice">🔒 This thread is locked.</div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, ThumbsUp, Trash2, CornerDownRight } from 'lucide-vue-next'
import apiClient from '@/api/client.js'
import { useAuthStore } from '@/stores/auth.js'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const topicSlug = route.params.topicSlug
const threadId = route.params.threadId

const thread = ref({})
const replies = ref([])
const loading = ref(true)
const error = ref('')

const hasUpvotedThread = ref(false)
const upvotedReplies = ref(new Set())

const replyingTo = ref(null)
const replyBody = ref('')
const replyError = ref('')

const newReplyBody = ref('')
const newReplyError = ref('')
const submitting = ref(false)

const topLevelReplies = computed(() => replies.value.filter(r => !r.parent_reply_id))
function nestedReplies(parentId) {
  return replies.value.filter(r => r.parent_reply_id === parentId)
}

function initials(profiles) {
  const name = profiles?.display_name || profiles?.full_name || '?'
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}
function authorName(profiles) {
  return profiles?.display_name || profiles?.full_name || 'Anonymous'
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
function isOwnPost(authorId) {
  return auth.user?.id === authorId
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await apiClient.get(`/community/threads/${threadId}`)
    thread.value = res.data.thread
    replies.value = res.data.replies || []
  } catch (e) {
    error.value = e.message || 'Failed to load thread.'
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function toggleThreadUpvote() {
  try {
    const res = await apiClient.post(`/community/threads/${threadId}/upvote`)
    if (res.data.action === 'added') {
      hasUpvotedThread.value = true
      thread.value.upvotes = (thread.value.upvotes || 0) + 1
    } else {
      hasUpvotedThread.value = false
      thread.value.upvotes = Math.max(0, (thread.value.upvotes || 0) - 1)
    }
  } catch {}
}

async function toggleReplyUpvote(reply) {
  try {
    const res = await apiClient.post(`/community/replies/${reply.id}/upvote`)
    if (res.data.action === 'added') {
      upvotedReplies.value = new Set([...upvotedReplies.value, reply.id])
      reply.upvotes = (reply.upvotes || 0) + 1
    } else {
      const next = new Set(upvotedReplies.value)
      next.delete(reply.id)
      upvotedReplies.value = next
      reply.upvotes = Math.max(0, (reply.upvotes || 0) - 1)
    }
  } catch {}
}

function startReply(parentId) {
  replyingTo.value = replyingTo.value === parentId ? null : parentId
  replyBody.value = ''
  replyError.value = ''
}

async function submitReply(parentId) {
  replyError.value = ''
  if (!replyBody.value.trim()) { replyError.value = 'Reply cannot be empty.'; return }
  submitting.value = true
  try {
    await apiClient.post(`/community/threads/${threadId}/replies`, {
      body: replyBody.value.trim(),
      parent_reply_id: parentId,
    })
    replyingTo.value = null
    replyBody.value = ''
    load()
  } catch (e) {
    replyError.value = e.message || 'Failed to post reply.'
  } finally {
    submitting.value = false
  }
}

async function submitTopReply() {
  newReplyError.value = ''
  if (!newReplyBody.value.trim()) { newReplyError.value = 'Reply cannot be empty.'; return }
  submitting.value = true
  try {
    await apiClient.post(`/community/threads/${threadId}/replies`, {
      body: newReplyBody.value.trim(),
    })
    newReplyBody.value = ''
    load()
  } catch (e) {
    newReplyError.value = e.message || 'Failed to post reply.'
  } finally {
    submitting.value = false
  }
}

async function deleteThread() {
  if (!confirm('Delete this thread? This cannot be undone.')) return
  try {
    await apiClient.delete(`/community/threads/${threadId}`)
    router.push(`/community/${topicSlug}`)
  } catch (e) {
    alert(e.message || 'Failed to delete thread.')
  }
}

async function deleteReply(replyId) {
  if (!confirm('Delete this reply?')) return
  try {
    await apiClient.delete(`/community/replies/${replyId}`)
    load()
  } catch (e) {
    alert(e.message || 'Failed to delete reply.')
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,400;0,500;0,600;0,700;0,800&display=swap');
* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.thread-page { display: flex; flex-direction: column; gap: 16px; }
.state-center { text-align: center; padding: 60px; color: var(--slate); font-size: 15px; }
.error { color: #dc2626; }

.back-link { display: inline-flex; align-items: center; gap: 6px; color: var(--slate); text-decoration: none; font-size: 13px; font-weight: 600; }
.back-link:hover { color: var(--plum); }

.card { background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(53,43,56,0.07); padding: 24px; }

/* Post / Reply header */
.post-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.author-avatar {
  width: 38px; height: 38px; border-radius: 50%;
  background: linear-gradient(135deg, var(--lavender), var(--lavender-deep));
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; color: var(--plum); flex-shrink: 0;
}
.author-avatar.sm { width: 30px; height: 30px; font-size: 11px; }
.author-info { flex: 1; min-width: 0; }
.author-name { font-size: 14px; font-weight: 700; color: var(--plum); }
.post-time { font-size: 11px; color: var(--slate); }
.post-actions { display: flex; gap: 4px; margin-left: auto; }

.post-title { font-size: 22px; font-weight: 800; color: var(--plum); margin: 0 0 12px; }
.post-body { font-size: 15px; color: var(--slate); line-height: 1.7; margin: 0 0 16px; white-space: pre-wrap; }
.post-footer { display: flex; align-items: center; gap: 16px; }

.upvote-btn {
  display: inline-flex; align-items: center; gap: 5px;
  background: var(--lavender-soft); border: 1.5px solid var(--lavender);
  color: var(--slate); font-family: 'Urbanist'; font-size: 13px; font-weight: 600;
  padding: 5px 12px; border-radius: 99px; cursor: pointer; transition: all 0.15s;
}
.upvote-btn:hover, .upvote-btn.active { background: var(--lavender); color: var(--plum); border-color: var(--lavender-deep); }
.upvote-btn.sm { font-size: 12px; padding: 4px 10px; }

.reply-count { font-size: 12px; color: var(--slate); font-weight: 600; }

/* Replies */
.replies-section { display: flex; flex-direction: column; gap: 10px; }
.replies-label { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--slate); }
.no-replies { font-size: 14px; color: var(--slate); text-align: center; padding: 24px; }
.reply-thread { display: flex; flex-direction: column; gap: 6px; }
.reply-card { padding: 16px 20px; }
.reply-card.nested { margin-left: 32px; border-left: 3px solid var(--lavender); border-radius: 0 12px 12px 0; }
.reply-body { font-size: 14px; color: var(--slate); line-height: 1.65; margin: 0 0 12px; white-space: pre-wrap; }

/* Inline reply */
.inline-reply-form { margin-left: 32px; display: flex; flex-direction: column; gap: 10px; }
.new-reply-form { display: flex; flex-direction: column; gap: 12px; }
.form-title { font-size: 15px; font-weight: 700; color: var(--plum); }
.input { font-family: 'Urbanist'; font-size: 14px; color: var(--plum); border: 1.5px solid var(--lavender); border-radius: 10px; padding: 10px 14px; outline: none; width: 100%; resize: vertical; }
.input:focus { border-color: var(--lavender-deep); box-shadow: 0 0 0 3px rgba(155,148,232,0.15); }
.form-error { font-size: 12px; color: #dc2626; }
.form-actions { display: flex; gap: 10px; }

.btn { display: inline-flex; align-items: center; gap: 6px; font-family: 'Urbanist'; font-weight: 600; border: none; cursor: pointer; transition: all 0.15s; }
.btn-primary { background: var(--plum); color: white; padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-primary:hover:not(:disabled) { background: #4a3550; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-ghost { background: transparent; color: var(--plum); border: 1.5px solid var(--lavender); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-ghost:hover { background: var(--lavender-soft); }
.btn-sm { padding: 6px 14px !important; font-size: 13px !important; border-radius: 8px !important; }

.btn-icon-sm {
  background: none; border: none; cursor: pointer; padding: 5px;
  border-radius: 6px; color: var(--slate); display: flex; align-items: center;
  transition: all 0.12s;
}
.btn-icon-sm:hover { background: var(--lavender-soft); color: var(--plum); }
.btn-icon-sm.danger:hover { background: #fee2e2; color: #dc2626; }

.locked-notice { text-align: center; color: var(--slate); font-size: 14px; font-weight: 600; padding: 16px; background: var(--lavender-soft); border-radius: 12px; }
</style>
