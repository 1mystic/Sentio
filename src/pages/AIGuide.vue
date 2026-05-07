<template>
  <div class="chat-layout">

    <!-- Chat Header -->
    <div class="chat-header">
      <div class="ai-avatar"><Sparkles :size="18" /></div>
      <div class="chat-header-info">
        <div class="chat-title">Sentio AI Guide</div>
        <div class="chat-subtitle">Powered by Claude · Educational use only</div>
      </div>
      <div class="header-actions">
        <button class="hdr-btn" title="New chat" @click="newChat">
          <SquarePen :size="16" />
        </button>
        <button class="hdr-btn" :class="{ active: showHistory }" title="Chat history" @click="toggleHistory">
          <History :size="16" />
        </button>
      </div>
      <span class="status-dot"></span>
    </div>

    <!-- Body: messages + history panel side-by-side -->
    <div class="chat-body">

      <!-- Messages Area -->
      <div class="chat-messages" ref="messagesEl">

        <!-- Starter suggestions (empty state) -->
        <div v-if="messages.length === 1" class="suggestions-bar">
          <button
            v-for="s in suggestions"
            :key="s"
            class="suggestion-chip"
            @click="useSuggestion(s)"
          >{{ s }}</button>
        </div>

        <!-- Message bubbles -->
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="message-wrap"
          :class="msg.role"
        >
          <div v-if="msg.role === 'assistant'" class="msg-avatar">
            <Sparkles :size="14" />
          </div>
          <div class="bubble" :class="msg.role">
            <div class="bubble-text">{{ msg.content }}<span v-if="msg.streaming && !msg.content" class="typing-dots"><span></span><span></span><span></span></span><span v-else-if="msg.streaming" class="typing-cursor">▌</span></div>
            <div class="bubble-ts">{{ msg.ts }}</div>
          </div>
        </div>

      </div>

      <!-- History Panel -->
      <transition name="history-slide">
        <div v-if="showHistory" class="history-panel">
          <div class="history-header">
            <span class="history-title">Past conversations</span>
            <button class="hdr-btn" @click="showHistory = false"><X :size="15" /></button>
          </div>

          <div v-if="historyLoading" class="history-empty">
            <Loader :size="18" class="spin" /> Loading…
          </div>
          <div v-else-if="!history.length" class="history-empty">
            No previous conversations yet.
          </div>
          <div v-else class="history-list">
            <button
              v-for="conv in history"
              :key="conv.id"
              class="history-item"
              :class="{ active: activeConvId === conv.id }"
              @click="loadConversation(conv)"
            >
              <div class="history-item-preview">{{ convPreview(conv) }}</div>
              <div class="history-item-meta">{{ convDate(conv.created_at) }} · {{ conv.messages.length / 2 | 0 }} exchanges</div>
            </button>
          </div>
        </div>
      </transition>

    </div>

    <!-- Input Area -->
    <div class="chat-input-area">
      <div class="input-wrap" :class="{ focused: inputFocused }">
        <textarea
          v-model="input"
          class="chat-input"
          placeholder="Ask about cognitive biases, thinking patterns, or reflect on a decision…"
          rows="1"
          @keydown.enter.exact.prevent="sendMessage"
          @input="autoResize"
          @focus="inputFocused = true"
          @blur="inputFocused = false"
          ref="inputEl"
        ></textarea>
        <button
          class="send-btn"
          :disabled="!input.trim() || streaming"
          @click="sendMessage"
          :title="streaming ? 'Waiting for response…' : 'Send'"
        >
          <Send :size="16" color="white" />
        </button>
      </div>
      <div class="safety-notice">
        Not a replacement for professional mental health support.
        <router-link to="/therapists" class="safety-link">Find a therapist →</router-link>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { Sparkles, Send, History, SquarePen, X, Loader } from 'lucide-vue-next'

const auth = useAuthStore()
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const WELCOME = {
  id: 1, role: 'assistant', streaming: false,
  content: "Hello! I'm Sentio AI — your cognitive bias guide. I'm here to help you explore patterns in your thinking, reflect on decisions, and understand psychological concepts.\n\nWhat's on your mind today?",
  ts: new Date().toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' }),
}

const messages = ref([{ ...WELCOME }])
const input = ref('')
const streaming = ref(false)
const inputFocused = ref(false)
const messagesEl = ref(null)
const inputEl = ref(null)

// ── History ──────────────────────────────────────────────
const showHistory = ref(false)
const history = ref([])
const historyLoading = ref(false)
const activeConvId = ref(null)

async function toggleHistory() {
  showHistory.value = !showHistory.value
  if (showHistory.value && !history.value.length) await fetchHistory()
}

async function fetchHistory() {
  historyLoading.value = true
  try {
    const token = auth.session?.access_token
    const res = await fetch(`${API_BASE}/ai/chat/history`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    if (res.ok) history.value = await res.json()
  } catch { /* silently ignore */ }
  finally { historyLoading.value = false }
}

function loadConversation(conv) {
  activeConvId.value = conv.id
  const date = new Date(conv.created_at)
  const dateStr = date.toLocaleDateString('en', { month: 'short', day: 'numeric' })
  messages.value = conv.messages.map((m, i) => ({
    id: i,
    role: m.role,
    streaming: false,
    content: m.content,
    ts: dateStr,
  }))
  showHistory.value = false
  scrollToBottom()
}

function newChat() {
  activeConvId.value = null
  messages.value = [{ ...WELCOME, ts: new Date().toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' }) }]
  showHistory.value = false
}

function convPreview(conv) {
  const first = conv.messages.find(m => m.role === 'user')
  const text = first?.content || 'Conversation'
  return text.length > 60 ? text.slice(0, 60) + '…' : text
}

function convDate(iso) {
  const d = new Date(iso)
  const now = new Date()
  const diff = now - d
  if (diff < 86400000) return d.toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' })
  if (diff < 604800000) return d.toLocaleDateString('en', { weekday: 'short' })
  return d.toLocaleDateString('en', { month: 'short', day: 'numeric' })
}

// ── Chat ─────────────────────────────────────────────────
const suggestions = [
  'What biases affect decisions most?',
  'Help me reflect on a recent conflict',
  'Explain confirmation bias with examples',
  'How can I think more objectively?',
]

function scrollToBottom() {
  nextTick(() => {
    if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  })
}

async function sendMessage() {
  const text = input.value.trim()
  if (!text || streaming.value) return

  activeConvId.value = null

  messages.value.push({
    id: Date.now(), role: 'user', streaming: false, content: text,
    ts: new Date().toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' }),
  })
  input.value = ''
  if (inputEl.value) inputEl.value.style.height = 'auto'
  scrollToBottom()

  const aiMsg = {
    id: Date.now() + 1, role: 'assistant', streaming: true, content: '',
    ts: new Date().toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' }),
  }
  messages.value.push(aiMsg)
  streaming.value = true
  scrollToBottom()

  try {
    const token = auth.session?.access_token
    const res = await fetch(`${API_BASE}/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ message: text }),
    })

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}))
      if (errBody.type === 'crisis') {
        aiMsg.content = errBody.response || 'Please reach out for support.'
        aiMsg.streaming = false
        return
      }
      throw new Error(`HTTP ${res.status}`)
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let lineBuffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      lineBuffer += decoder.decode(value, { stream: true })
      const parts = lineBuffer.split('\n')
      lineBuffer = parts.pop()

      for (const line of parts) {
        const trimmed = line.trim()
        if (!trimmed.startsWith('data:')) continue
        const raw = trimmed.slice(5).trim()
        if (raw === '[DONE]') { aiMsg.streaming = false; break }
        try {
          const parsed = JSON.parse(raw)
          if (parsed.chunk) { aiMsg.content += parsed.chunk; scrollToBottom() }
          if (parsed.error) { aiMsg.content = 'Sorry, I ran into an error. Please try again.'; aiMsg.streaming = false }
        } catch { /* partial chunk */ }
      }
      if (!aiMsg.streaming) break
    }
  } catch {
    aiMsg.content = "I'm having trouble connecting. Please check your connection and try again."
  } finally {
    aiMsg.streaming = false
    streaming.value = false
    scrollToBottom()
    // Refresh history list silently so new conversation appears next time
    history.value = []
  }
}

function useSuggestion(s) {
  input.value = s
  sendMessage()
}

function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800&display=swap');
* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.chat-layout {
  display: flex; flex-direction: column;
  height: calc(100vh - 64px);
  margin: -32px;
  overflow: hidden;
}

/* ── Header ──────────────────────────────────────────── */
.chat-header {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 28px;
  border-bottom: 1px solid var(--lavender-soft);
  background: var(--bg, #f4f3f8);
  flex-shrink: 0;
}
.ai-avatar {
  width: 38px; height: 38px; border-radius: 50%;
  background: linear-gradient(135deg, #352b38, #9b94e8);
  display: flex; align-items: center; justify-content: center;
  color: white; flex-shrink: 0;
}
.chat-header-info { flex: 1; min-width: 0; }
.chat-title { font-size: 15px; font-weight: 700; color: var(--plum); }
.chat-subtitle { font-size: 11px; color: var(--slate); }
.header-actions { display: flex; align-items: center; gap: 4px; }
.hdr-btn {
  width: 32px; height: 32px; border-radius: 8px;
  background: transparent; border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: var(--slate); transition: all 0.15s;
}
.hdr-btn:hover { background: var(--lavender); color: var(--plum); }
.hdr-btn.active { background: var(--lavender); color: var(--plum); }
.status-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #059669; flex-shrink: 0;
}

/* ── Body (messages + history panel) ─────────────────── */
.chat-body {
  flex: 1; display: flex; overflow: hidden; position: relative;
}

/* ── Messages ─────────────────────────────────────────── */
.chat-messages {
  flex: 1; overflow-y: auto;
  padding: 24px 28px;
  display: flex; flex-direction: column; gap: 14px;
  background: var(--lavender-soft, #f0eef9);
}

/* Starter chips */
.suggestions-bar { display: flex; gap: 8px; flex-wrap: wrap; padding-bottom: 8px; }
.suggestion-chip {
  font-family: 'Urbanist'; font-size: 13px; font-weight: 500;
  color: var(--plum); background: white;
  border: 1.5px solid var(--lavender); border-radius: 99px;
  padding: 8px 16px; cursor: pointer; transition: all 0.15s;
}
.suggestion-chip:hover { background: var(--lavender); }

/* Bubbles */
.message-wrap { display: flex; align-items: flex-end; gap: 8px; }
.message-wrap.user { flex-direction: row-reverse; }
.message-wrap.assistant { flex-direction: row; }

.msg-avatar {
  width: 30px; height: 30px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, #352b38, #9b94e8);
  display: flex; align-items: center; justify-content: center;
  color: white;
}

.bubble {
  max-width: 68%; padding: 12px 16px;
  display: flex; flex-direction: column; gap: 4px;
  word-break: break-word;
}
.bubble.assistant {
  background: white; color: var(--plum);
  border-radius: 4px 16px 16px 16px;
  border: 1px solid var(--lavender-soft);
  box-shadow: 0 2px 8px rgba(53,43,56,0.06);
}
.bubble.user {
  background: var(--plum); color: white;
  border-radius: 16px 4px 16px 16px;
}
.bubble-text { font-size: 14px; line-height: 1.65; white-space: pre-line; }
.bubble-ts { font-size: 10px; opacity: 0.45; align-self: flex-end; }

.typing-cursor { animation: blink 0.6s infinite; margin-left: 1px; }
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0; } }

.typing-dots { display: inline-flex; align-items: center; gap: 4px; margin-left: 2px; vertical-align: middle; }
.typing-dots span {
  display: inline-block; width: 6px; height: 6px;
  border-radius: 50%; background: var(--lavender-deep);
  animation: dot-bounce 1.2s infinite ease-in-out;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes dot-bounce { 0%,60%,100% { transform: translateY(0); opacity: 0.4; } 30% { transform: translateY(-5px); opacity: 1; } }

/* ── History Panel ────────────────────────────────────── */
.history-panel {
  width: 280px; flex-shrink: 0;
  background: white;
  border-left: 1px solid var(--lavender-soft);
  display: flex; flex-direction: column;
  overflow: hidden;
}

.history-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--lavender-soft);
  flex-shrink: 0;
}
.history-title { font-size: 13px; font-weight: 700; color: var(--plum); }

.history-empty {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px;
  font-size: 13px; color: var(--slate); padding: 32px 16px; text-align: center;
}

.history-list { flex: 1; overflow-y: auto; padding: 8px; }

.history-item {
  width: 100%; text-align: left;
  background: transparent; border: none; cursor: pointer;
  padding: 10px 12px; border-radius: 10px;
  transition: background 0.13s; margin-bottom: 2px;
}
.history-item:hover { background: var(--lavender-soft); }
.history-item.active { background: var(--lavender); }

.history-item-preview {
  font-size: 13px; font-weight: 500; color: var(--plum);
  line-height: 1.4; margin-bottom: 4px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
}
.history-item-meta { font-size: 11px; color: var(--slate); }

/* Slide transition */
.history-slide-enter-active,
.history-slide-leave-active { transition: width 0.22s ease, opacity 0.18s ease; overflow: hidden; }
.history-slide-enter-from,
.history-slide-leave-to { width: 0 !important; opacity: 0; }

.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Input ────────────────────────────────────────────── */
.chat-input-area {
  padding: 14px 28px 18px;
  border-top: 1px solid var(--lavender-soft);
  background: white; flex-shrink: 0;
  display: flex; flex-direction: column; gap: 8px;
}
.input-wrap {
  display: flex; align-items: flex-end; gap: 10px;
  background: var(--lavender-soft, #f0eef9);
  border: 1.5px solid var(--lavender);
  border-radius: 14px; padding: 10px 10px 10px 16px;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.input-wrap.focused {
  border-color: var(--lavender-deep);
  box-shadow: 0 0 0 3px rgba(155,148,232,0.12);
}
.chat-input {
  flex: 1; font-family: 'Urbanist'; font-size: 14px;
  color: var(--plum); background: transparent;
  border: none; outline: none; resize: none;
  line-height: 1.5; max-height: 120px; padding: 2px 0;
}
.chat-input::placeholder { color: var(--slate); opacity: 0.7; }

.send-btn {
  width: 38px; height: 38px; border-radius: 10px;
  background: var(--plum); border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: all 0.15s; color: white;
}
.send-btn:hover:not(:disabled) { background: #4a3550; transform: scale(1.04); }
.send-btn:disabled { opacity: 0.35; cursor: not-allowed; transform: none; }

.safety-notice { font-size: 11px; color: var(--slate); text-align: center; }
.safety-link { color: var(--lavender-deep); font-weight: 600; text-decoration: none; }
.safety-link:hover { text-decoration: underline; }

/* ── Responsive ──────────────────────────────────────── */
@media (max-width: 640px) {
  .chat-layout { height: calc(100vh - 56px); margin: -16px; }
  .chat-header { padding: 10px 14px; }
  .chat-subtitle { display: none; }
  .chat-messages { padding: 14px; gap: 10px; }
  .bubble { max-width: 85%; }
  .chat-input-area { padding: 10px 14px 14px; }
  .suggestions-bar { gap: 6px; }
  .suggestion-chip { font-size: 12px; padding: 6px 12px; }

  /* History panel becomes full-width overlay on mobile */
  .history-panel {
    position: absolute; top: 0; right: 0; bottom: 0;
    width: 100% !important; z-index: 10;
    border-left: none;
    box-shadow: -4px 0 20px rgba(53,43,56,0.12);
  }
}
</style>
