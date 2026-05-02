<template>
  <div class="chat-layout">

    <!-- Chat Header -->
    <div class="chat-header">
      <div class="ai-avatar">✨</div>
      <div class="chat-header-info">
        <div class="chat-title">Sentio AI Guide</div>
        <div class="chat-subtitle">Powered by Claude</div>
      </div>
      <div class="status-dot"></div>
      <span class="status-label">Online</span>
    </div>

    <!-- Messages Area -->
    <div class="chat-messages" ref="messagesEl">

      <!-- Suggestions (show when only welcome message) -->
      <div v-if="messages.length === 1" class="suggestions-bar">
        <button
          v-for="s in suggestions"
          :key="s"
          class="suggestion-chip"
          @click="useSuggestion(s)"
        >{{ s }}</button>
      </div>

      <!-- Messages -->
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="message-wrap"
        :class="msg.role"
      >
        <div v-if="msg.role === 'assistant'" class="msg-avatar">✨</div>
        <div class="bubble" :class="msg.role">
          <div class="bubble-text">{{ msg.content }}</div>
          <div class="bubble-ts">{{ msg.ts }}</div>
        </div>
      </div>

      <!-- Typing indicator -->
      <div v-if="loading" class="message-wrap assistant">
        <div class="msg-avatar">✨</div>
        <div class="bubble assistant typing-bubble">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>

    </div>

    <!-- Input Area -->
    <div class="chat-input-area">
      <div class="input-wrap">
        <textarea
          v-model="input"
          class="chat-input"
          placeholder="Ask me anything about cognitive biases, your thinking patterns..."
          rows="1"
          @keydown.enter.exact.prevent="sendMessage"
          @keydown.shift.enter="null"
          @input="autoResize"
          ref="inputEl"
        ></textarea>
        <button class="send-btn btn btn-primary" :disabled="!input.trim() || loading" @click="sendMessage">
          <span class="send-icon">↑</span>
        </button>
      </div>
      <div class="safety-notice">Not a replacement for professional mental health support. <router-link to="/therapists" class="safety-link">Find a therapist →</router-link></div>
    </div>

  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const messages = ref([
  { id: 1, role: 'assistant', content: 'Hello! I\'m Sentio AI — your cognitive bias guide. I\'m here to help you explore patterns in your thinking, reflect on decisions, and understand psychological concepts in a practical way.\n\nWhat\'s on your mind today?', ts: '9:41 AM' }
])
const input = ref('')
const loading = ref(false)
const messagesEl = ref(null)
const inputEl = ref(null)
const suggestions = ['What biases affect my decisions most?', 'Help me reflect on a recent conflict', 'Explain confirmation bias with examples', 'How can I think more objectively?']

const simulatedReplies = [
  'That\'s a great reflection. Based on what you\'ve shared, this sounds like it could involve confirmation bias — the tendency to favor information that confirms what we already believe. Would you like to explore this further with a specific example from your experience?',
  'This is a really insightful question. The availability heuristic plays a big role here — our brains judge the likelihood of events based on how easily examples come to mind. Recent or vivid events feel more probable, even when statistics say otherwise.',
  'What you\'re describing sounds like the sunk cost fallacy. We tend to continue investing in something because of what we\'ve already put in — time, money, emotion — rather than evaluating what\'s the best path forward from now. Does that resonate?',
  'Recognizing this pattern is already a huge step. The Dunning-Kruger effect suggests that people with limited knowledge in a domain tend to overestimate their competence. The good news? As expertise grows, so does appropriate humility.',
]
let replyIndex = 0

async function sendMessage() {
  if (!input.value.trim() || loading.value) return
  const userMsg = {
    id: Date.now(),
    role: 'user',
    content: input.value,
    ts: new Date().toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' })
  }
  messages.value.push(userMsg)
  input.value = ''
  loading.value = true
  if (inputEl.value) { inputEl.value.style.height = 'auto' }
  await nextTick()
  messagesEl.value?.scrollTo({ top: messagesEl.value.scrollHeight, behavior: 'smooth' })

  await new Promise(r => setTimeout(r, 1500))
  messages.value.push({
    id: Date.now() + 1,
    role: 'assistant',
    content: simulatedReplies[replyIndex % simulatedReplies.length],
    ts: new Date().toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' })
  })
  replyIndex++
  loading.value = false
  await nextTick()
  messagesEl.value?.scrollTo({ top: messagesEl.value.scrollHeight, behavior: 'smooth' })
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
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

/* Full height chat */
.chat-layout { display: flex; flex-direction: column; height: calc(100vh - 60px); margin: -32px; }

/* Header */
.chat-header { padding: 16px 32px; border-bottom: 1px solid var(--lavender-soft); display: flex; align-items: center; gap: 12px; flex-shrink: 0; background: white; }
.ai-avatar { width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, #352b38, #9b94e8); display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.chat-header-info { flex: 1; }
.chat-title { font-size: 16px; font-weight: 700; color: var(--plum); }
.chat-subtitle { font-size: 12px; color: var(--slate); }
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: #059669; }
.status-label { font-size: 12px; color: #059669; font-weight: 600; }

/* Messages */
.chat-messages { flex: 1; overflow-y: auto; padding: 24px 32px; display: flex; flex-direction: column; gap: 16px; background: var(--bg); }

/* Suggestions */
.suggestions-bar { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }
.suggestion-chip { font-family: 'Urbanist'; font-size: 13px; font-weight: 500; color: var(--plum); background: white; border: 1.5px solid var(--lavender); border-radius: 99px; padding: 8px 16px; cursor: pointer; transition: all 0.15s; }
.suggestion-chip:hover { background: var(--lavender-soft); border-color: var(--lavender-deep); }

/* Messages */
.message-wrap { display: flex; align-items: flex-end; gap: 10px; }
.message-wrap.user { flex-direction: row-reverse; }
.message-wrap.assistant { flex-direction: row; }

.msg-avatar { width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #352b38, #9b94e8); display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; }

.bubble { max-width: 65%; padding: 12px 16px; display: flex; flex-direction: column; gap: 4px; }
.bubble.assistant { background: white; color: var(--plum); border-radius: 4px 16px 16px 16px; border: 1.5px solid var(--lavender-soft); box-shadow: 0 2px 8px rgba(53,43,56,0.06); }
.bubble.user { background: var(--plum); color: white; border-radius: 16px 4px 16px 16px; }
.bubble-text { font-size: 14px; line-height: 1.6; white-space: pre-line; }
.bubble-ts { font-size: 10px; opacity: 0.5; text-align: right; }

/* Typing */
.typing-bubble { padding: 14px 20px; flex-direction: row; gap: 5px; align-items: center; }
.dot { width: 7px; height: 7px; border-radius: 50%; background: var(--lavender-deep); animation: bounce 1.2s infinite; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 60%, 100% { transform: translateY(0); opacity: 0.5; } 30% { transform: translateY(-6px); opacity: 1; } }

/* Input Area */
.chat-input-area { padding: 16px 32px; border-top: 1px solid var(--lavender-soft); background: white; flex-shrink: 0; display: flex; flex-direction: column; gap: 8px; }
.input-wrap { display: flex; align-items: flex-end; gap: 10px; background: var(--ghost); border: 1.5px solid var(--lavender); border-radius: 14px; padding: 8px 8px 8px 16px; transition: border-color 0.15s; }
.input-wrap:focus-within { border-color: var(--lavender-deep); box-shadow: 0 0 0 3px rgba(155,148,232,0.12); }
.chat-input { flex: 1; font-family: 'Urbanist'; font-size: 14px; color: var(--plum); background: transparent; border: none; outline: none; resize: none; line-height: 1.5; max-height: 120px; padding: 4px 0; }
.chat-input::placeholder { color: var(--lavender-mid); }

.btn { display: inline-flex; align-items: center; justify-content: center; font-family: 'Urbanist'; font-weight: 600; border: none; cursor: pointer; transition: all 0.18s; outline: none; }
.btn-primary { background: var(--plum); color: white; border-radius: 10px; }
.btn-primary:hover:not(:disabled) { background: #4a3550; }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
.send-btn { width: 40px; height: 40px; border-radius: 10px; font-size: 18px; flex-shrink: 0; }
.send-icon { font-size: 16px; font-weight: 800; }

.safety-notice { font-size: 11px; color: var(--slate); font-style: italic; text-align: center; }
.safety-link { color: var(--lavender-deep); text-decoration: none; font-weight: 600; }
.safety-link:hover { text-decoration: underline; }
</style>
