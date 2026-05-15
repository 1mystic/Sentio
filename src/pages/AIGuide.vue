<template>
  <div class="guide-layout">

    <!-- ── Header ──────────────────────────────────────────────────────────── -->
    <div class="guide-header">
      <div class="ai-avatar"><Sparkles :size="18" /></div>
      <div class="header-info">
        <div class="header-title">Sentio AI Guide</div>
        <div class="header-sub">Powered by Claude · Educational use only</div>
      </div>

      <!-- Mode toggle pill -->
      <div class="mode-toggle">
        <button
          class="mode-btn"
          :class="{ active: mode === 'guide' }"
          @click="setMode('guide')"
        ><MessageSquare :size="13" />Ask anything</button>
        <button
          class="mode-btn"
          :class="{ active: mode === 'socratic' }"
          @click="setMode('socratic')"
        ><GraduationCap :size="13" />Socratic</button>
      </div>

      <div class="header-actions">
        <button class="hdr-btn" title="New chat" @click="newChat">
          <SquarePen :size="16" />
        </button>
        <button
          v-if="mode === 'guide'"
          class="hdr-btn"
          :class="{ active: showHistory }"
          title="Chat history"
          @click="toggleHistory"
        >
          <History :size="16" />
        </button>
        <button
          v-if="mode === 'socratic'"
          class="hdr-btn"
          :class="{ active: showSocraticHistory }"
          title="Past sessions"
          @click="toggleSocraticHistory"
        >
          <Clock :size="16" />
        </button>
      </div>
      <span class="status-dot"></span>
    </div>

    <!-- ── Guide mode body ─────────────────────────────────────────────────── -->
    <div v-if="mode === 'guide'" class="guide-body">

      <div class="chat-messages" ref="messagesEl">
        <!-- Starter suggestions -->
        <div v-if="guideMessages.length === 1" class="suggestions-bar">
          <button
            v-for="s in suggestions"
            :key="s"
            class="suggestion-chip"
            @click="useSuggestion(s)"
          >{{ s }}</button>
        </div>

        <!-- Message bubbles -->
        <div
          v-for="msg in guideMessages"
          :key="msg.id"
          class="message-wrap"
          :class="msg.role"
        >
          <div v-if="msg.role === 'assistant'" class="msg-avatar">
            <Sparkles :size="14" />
          </div>
          <div class="bubble" :class="msg.role">
            <div class="bubble-text">
              <span v-if="msg.role === 'assistant'" class="md-content" v-html="renderMarkdown(msg.content)"></span>
              <span v-else>{{ msg.content }}</span>
              <span v-if="msg.streaming && !msg.content" class="typing-dots"><span></span><span></span><span></span></span><span v-else-if="msg.streaming" class="typing-cursor">▌</span>
            </div>
            <div class="bubble-ts">{{ msg.ts }}</div>
          </div>
        </div>
      </div>

      <!-- History panel -->
      <transition name="history-slide">
        <div v-if="showHistory" class="history-panel">
          <div class="history-header">
            <span class="history-title">Past conversations</span>
            <button class="hdr-btn" @click="showHistory = false"><X :size="15" /></button>
          </div>
          <div v-if="historyLoading" class="history-empty">
            <Loader :size="18" class="spin" /> Loading…
          </div>
          <div v-else-if="!history.length" class="history-empty">No previous conversations yet.</div>
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

    <!-- ── Socratic mode body ──────────────────────────────────────────────── -->
    <div v-else class="socratic-body">

      <!-- Mobile top strip -->
      <div class="socratic-strip" v-if="episteme.sessionId.value">
        <div class="strip-clarity">
          <span class="strip-score">{{ episteme.clarityScore.value }}</span>
          <span class="strip-label">clarity</span>
        </div>
        <div class="strip-divider"></div>
        <div class="state-pill" :class="stateClass">{{ episteme.stateLabel.value }}</div>
        <div class="depth-pill">{{ episteme.depthLabel.value }}</div>
        <div class="strip-turns">Turn {{ episteme.turnNumber.value }}</div>
        <button
          v-if="episteme.canGenerateInsight.value && !episteme.insightCard.value"
          class="strip-insight-btn"
          :disabled="episteme.insightLoading.value"
          @click="episteme.generateInsight()"
        >
          <Sparkles :size="11" />
          {{ episteme.insightLoading.value ? 'Generating…' : 'Insight' }}
        </button>
      </div>

      <!-- Socratic session history panel -->
      <transition name="soc-history-slide">
        <div v-if="showSocraticHistory" class="soc-history-panel">
          <div class="history-header">
            <span class="history-title">Past sessions</span>
            <button class="hdr-btn" @click="showSocraticHistory = false"><X :size="15" /></button>
          </div>
          <div v-if="socraticHistoryLoading" class="history-empty">
            <Loader :size="18" class="spin" /> Loading…
          </div>
          <div v-else-if="!socraticHistory.length" class="history-empty">No past Socratic sessions yet.</div>
          <div v-else class="history-list">
            <button
              v-for="sess in socraticHistory"
              :key="sess.id"
              class="history-item"
              :class="{ active: episteme.sessionId.value === sess.id }"
              @click="loadSocraticSession(sess.id)"
            >
              <div class="soc-hist-domain">{{ domainLabel(sess.domain) }}</div>
              <div class="history-item-preview">{{ sess.preview || 'No messages yet' }}</div>
              <div class="history-item-meta">
                {{ convDate(sess.created_at) }} · {{ sess.turns_count }} turns
                <span v-if="sess.is_complete" class="hist-complete-pill">complete</span>
              </div>
            </button>
          </div>
        </div>
      </transition>

      <!-- Main: chat (left) + cognitive panel (right) -->
      <div class="socratic-main">

        <!-- Chat column -->
        <div class="socratic-chat">

          <!-- Domain selector (pre-session) -->
          <div v-if="!episteme.sessionId.value" class="domain-selector">
            <div class="domain-icon"><Brain :size="32" /></div>
            <h2 class="domain-heading">What are you exploring today?</h2>
            <p class="domain-sub">Choose a domain — Sentio will guide you through Socratic dialogue to build real understanding.</p>
            <div class="domain-grid">
              <button
                v-for="d in domains"
                :key="d.value"
                class="domain-card"
                :class="{ selected: selectedDomain === d.value }"
                @click="selectedDomain = d.value"
              >
                <component :is="d.icon" :size="22" class="domain-icon-svg" />
                <span class="domain-label">{{ d.label }}</span>
              </button>
            </div>
            <button class="start-btn" @click="startSocraticSession">
              Begin session <ArrowRight :size="16" />
            </button>
          </div>

          <!-- Messages -->
          <div v-else class="chat-messages" ref="socraticMessagesEl">

            <!-- First-turn prompt when session started but no messages yet -->
            <div v-if="episteme.messages.value.length === 0" class="session-prompt">
              <div class="session-prompt-icon"><BookOpen :size="20" /></div>
              <p class="session-prompt-text">Ask your first question and Sentio will guide you through it Socratically — building understanding through dialogue, not direct answers.</p>
            </div>

            <div
              v-for="msg in episteme.messages.value"
              :key="msg.id"
              class="message-wrap"
              :class="msg.role"
            >
              <div v-if="msg.role === 'assistant'" class="msg-avatar socratic-avatar">
                <BookOpen :size="14" />
              </div>
              <div class="bubble" :class="msg.role">
                <div v-if="msg.role === 'assistant' && msg.state" class="state-label-inline" :class="stateClassFor(msg.state)">
                  {{ stateLabelFor(msg.state) }}
                </div>
                <div class="bubble-text">
                  <span v-if="msg.role === 'assistant'" class="md-content" v-html="renderMarkdown(msg.content)"></span>
                  <span v-else>{{ msg.content }}</span>
                  <span v-if="msg.isStreaming && !msg.content" class="typing-dots"><span></span><span></span><span></span></span><span v-else-if="msg.isStreaming" class="typing-cursor">▌</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Cognitive panel (desktop) -->
        <div class="cognitive-panel" v-if="episteme.sessionId.value">

          <!-- Clarity meter -->
          <div class="panel-section">
            <div class="panel-label">Clarity</div>
            <div class="clarity-display">
              <span class="clarity-number">{{ episteme.clarityScore.value }}</span>
              <span class="clarity-max">/100</span>
            </div>
            <div class="clarity-track">
              <div
                class="clarity-fill"
                :style="{ width: episteme.clarityScore.value + '%' }"
              ></div>
            </div>
            <div class="clarity-hint">Bayesian mastery estimate</div>
          </div>

          <div class="panel-divider"></div>

          <!-- SDSM state -->
          <div class="panel-section">
            <div class="panel-label">Dialogue state</div>
            <div class="state-badge-lg" :class="stateClass">{{ episteme.stateLabel.value }}</div>
            <div class="state-desc">{{ episteme.stateDescription.value }}</div>
          </div>

          <div class="panel-divider"></div>

          <!-- Bloom depth -->
          <div class="panel-section">
            <div class="panel-label">Bloom depth</div>
            <div class="depth-badge-lg" :class="depthClass">{{ episteme.depthLabel.value }}</div>
          </div>

          <div class="panel-divider"></div>

          <!-- Turn count -->
          <div class="panel-section">
            <div class="panel-label">Session progress</div>
            <div class="turn-display">Turn {{ episteme.turnNumber.value }}</div>
            <div class="turn-track">
              <div class="turn-fill" :style="{ width: Math.min(episteme.turnNumber.value / 9 * 100, 100) + '%' }"></div>
            </div>
          </div>

          <!-- Insight button -->
          <template v-if="episteme.canGenerateInsight.value && !episteme.insightCard.value">
            <div class="panel-section">
              <button
                class="insight-btn"
                :disabled="episteme.insightLoading.value"
                @click="episteme.generateInsight()"
              >
                <Sparkles :size="14" />
                {{ episteme.insightLoading.value ? 'Generating…' : 'Generate insight card' }}
              </button>
              <div class="insight-hint">Summarises what you've genuinely worked out this session.</div>
            </div>
          </template>

          <!-- Insight card -->
          <template v-if="episteme.insightCard.value">
            <div class="insight-card">
              <div class="insight-card-header">
                <Sparkles :size="13" />
                <span>Insight card</span>
              </div>
              <div class="insight-concept">{{ episteme.insightCard.value.concept }}</div>
              <div class="insight-text">{{ episteme.insightCard.value.insight }}</div>
              <div v-if="episteme.insightCard.value.gaps?.length" class="insight-gaps">
                <div class="gaps-label">Explore next</div>
                <div class="gaps-pills">
                  <span v-for="gap in episteme.insightCard.value.gaps" :key="gap" class="gap-pill">{{ gap }}</span>
                </div>
              </div>
              <div v-if="episteme.insightCard.value.next_question" class="insight-next">
                <BookOpen :size="12" />
                <span>{{ episteme.insightCard.value.next_question }}</span>
              </div>
              <div class="insight-export-btns">
                <button class="export-btn" @click="copyInsight" :title="copiedInsight ? 'Copied!' : 'Copy to clipboard'">
                  <Copy :size="10" />
                  {{ copiedInsight ? 'Copied!' : 'Copy' }}
                </button>
                <button class="export-btn" @click="exportInsightMd" title="Download as Markdown">
                  <FileText :size="10" />
                  .md
                </button>
                <button class="export-btn" @click="exportInsightPdf" title="Export as PDF">
                  <Printer :size="10" />
                  PDF
                </button>
              </div>
            </div>
          </template>

        </div>
      </div>
    </div>

    <!-- ── Input area ──────────────────────────────────────────────────────── -->
    <div class="input-area">

      <!-- Live cognitive signals (socratic mode, while typing) -->
      <transition name="signals-fade">
        <div v-if="liveSignals" class="cognitive-signals">
          <div class="signals-header">
            <Activity :size="11" />
            <span>Cognitive signals</span>
          </div>
          <div class="signal-row">
            <span class="signal-name">Analysis</span>
            <div class="signal-track">
              <div class="signal-fill signal-analysis" :style="{ width: liveSignals.analysis + '%' }"></div>
            </div>
            <span class="signal-val">{{ liveSignals.analysis }}%</span>
          </div>
          <div class="signal-row">
            <span class="signal-name">Depth</span>
            <div class="signal-track">
              <div class="signal-fill signal-depth" :style="{ width: liveSignals.depthConfidence + '%' }"></div>
            </div>
            <span class="signal-val signal-depth-val">{{ liveSignals.depthLevel }}</span>
          </div>
          <div class="signal-row">
            <span class="signal-name">Clarity</span>
            <div class="signal-track">
              <div class="signal-fill signal-clarity" :style="{ width: liveSignals.clarity + '%' }"></div>
            </div>
            <span class="signal-val signal-clarity-val">{{ liveSignals.clarity }}%</span>
          </div>
        </div>
      </transition>

      <div class="input-wrap" :class="{ focused: inputFocused }">
        <textarea
          v-model="input"
          class="chat-input"
          :placeholder="inputPlaceholder"
          rows="1"
          @keydown.enter.exact.prevent="handleSend"
          @input="autoResize"
          @focus="inputFocused = true"
          @blur="inputFocused = false"
          ref="inputEl"
        ></textarea>
        <button
          class="send-btn"
          :disabled="!input.trim() || isBusy"
          @click="handleSend"
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
import { ref, computed, nextTick, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useEpistemeChat } from '@/composables/useEpistemeChat.ts'
import { extractDepthSignals, keywordClassify } from '@/lib/episteme/algorithms.ts'
import {
  Sparkles, Send, History, SquarePen, X, Loader, BookOpen,
  Brain, ArrowRight, Cpu, BarChart3, TrendingUp, Code2, Activity,
  MessageSquare, GraduationCap, Copy, FileText, Printer, Clock,
} from 'lucide-vue-next'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import markedKatex from 'marked-katex-extension'

marked.use(markedKatex({ throwOnError: false, displayMode: true }))

function renderMarkdown(text) {
  if (!text) return ''
  return DOMPurify.sanitize(marked.parse(text))
}

const auth = useAuthStore()
const route = useRoute()
const episteme = useEpistemeChat()
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// ── Mode ──────────────────────────────────────────────────────────────────────
const mode = ref('guide') // 'guide' | 'socratic'
const input = ref('')
const inputFocused = ref(false)
const inputEl = ref(null)
const messagesEl = ref(null)
const socraticMessagesEl = ref(null)

function setMode(m) {
  mode.value = m
  input.value = ''
  if (inputEl.value) inputEl.value.style.height = 'auto'
}

const isBusy = computed(() => mode.value === 'guide' ? guideStreaming.value : episteme.isStreaming.value)

const inputPlaceholder = computed(() => {
  if (mode.value === 'socratic') {
    if (!episteme.sessionId.value) return 'Choose a domain above to start…'
    return 'Share your thoughts…'
  }
  return 'Ask about cognitive biases, thinking patterns, or reflect on a decision…'
})

// ── Guide mode ────────────────────────────────────────────────────────────────
const WELCOME = {
  id: 1, role: 'assistant', streaming: false,
  content: "Hello! I'm Sentio AI — your cognitive bias guide. I'm here to help you explore patterns in your thinking, reflect on decisions, and understand psychological concepts.\n\nWhat's on your mind today?",
  ts: new Date().toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' }),
}

const guideMessages = ref([{ ...WELCOME }])
const guideStreaming = ref(false)
const showHistory = ref(false)
const history = ref([])
const historyLoading = ref(false)
const activeConvId = ref(null)

const suggestions = [
  'What biases affect decisions most?',
  'Help me reflect on a recent conflict',
  'Explain confirmation bias with examples',
  'How can I think more objectively?',
]

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
  } catch { /* ignore */ }
  finally { historyLoading.value = false }
}

function loadConversation(conv) {
  activeConvId.value = conv.id
  const dateStr = new Date(conv.created_at).toLocaleDateString('en', { month: 'short', day: 'numeric' })
  guideMessages.value = conv.messages.map((m, i) => ({
    id: i, role: m.role, streaming: false, content: m.content, ts: dateStr,
  }))
  showHistory.value = false
  scrollToBottom()
}

function newChat() {
  if (mode.value === 'guide') {
    activeConvId.value = null
    guideMessages.value = [{ ...WELCOME, ts: new Date().toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' }) }]
    showHistory.value = false
  } else {
    episteme.reset()
    selectedDomain.value = 'general'
  }
}

function convPreview(conv) {
  const first = conv.messages.find(m => m.role === 'user')
  const text = first?.content || 'Conversation'
  return text.length > 60 ? text.slice(0, 60) + '…' : text
}

function convDate(iso) {
  const d = new Date(iso), now = new Date(), diff = now - d
  if (diff < 86400000) return d.toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' })
  if (diff < 604800000) return d.toLocaleDateString('en', { weekday: 'short' })
  return d.toLocaleDateString('en', { month: 'short', day: 'numeric' })
}

function scrollToBottom() {
  nextTick(() => {
    const el = mode.value === 'guide' ? messagesEl.value : socraticMessagesEl.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

async function sendGuideMessage(text) {
  activeConvId.value = null
  guideMessages.value.push({
    id: Date.now(), role: 'user', streaming: false, content: text,
    ts: new Date().toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' }),
  })
  scrollToBottom()

  const aiMsg = {
    id: Date.now() + 1, role: 'assistant', streaming: true, content: '',
    ts: new Date().toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' }),
  }
  guideMessages.value.push(aiMsg)
  guideStreaming.value = true
  scrollToBottom()

  try {
    const token = auth.session?.access_token
    const res = await fetch(`${API_BASE}/ai/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: JSON.stringify({ message: text }),
    })

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}))
      if (errBody.type === 'crisis') { aiMsg.content = errBody.response || 'Please reach out for support.'; aiMsg.streaming = false; return }
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
        } catch { /* partial */ }
      }
      if (!aiMsg.streaming) break
    }
  } catch {
    aiMsg.content = "I'm having trouble connecting. Please check your connection and try again."
  } finally {
    aiMsg.streaming = false
    guideStreaming.value = false
    scrollToBottom()
    history.value = []
  }
}

function useSuggestion(s) { input.value = s; sendGuideMessage(s); input.value = '' }

// ── Socratic mode ─────────────────────────────────────────────────────────────
const domains = [
  { value: 'general',    label: 'General thinking',  icon: Brain },
  { value: 'ml',         label: 'ML concepts',       icon: Cpu },
  { value: 'statistics', label: 'Statistics',        icon: BarChart3 },
  { value: 'economics',  label: 'Economics',         icon: TrendingUp },
  { value: 'cs',         label: 'Computer Science',  icon: Code2 },
]

// Live cognitive signals — recomputed as user types in socratic mode
const liveSignals = computed(() => {
  if (mode.value !== 'socratic' || !input.value.trim()) return null
  const text = input.value
  const { qualityScore } = extractDepthSignals(text, episteme.domain.value, episteme.turnNumber.value)
  const { depth, confidence } = keywordClassify(text)
  return {
    analysis: Math.round(qualityScore * 100),
    depthConfidence: Math.round(confidence * 100),
    depthLevel: depth,
    clarity: episteme.clarityScore.value,
  }
})
const selectedDomain = ref('general')

async function startSocraticSession() {
  try {
    await episteme.startSession(selectedDomain.value)
  } catch (err) {
    console.error('Failed to start session:', err)
  }
}

// ── Shared send handler ───────────────────────────────────────────────────────
async function handleSend() {
  const text = input.value.trim()
  if (!text || isBusy.value) return
  if (mode.value === 'socratic' && !episteme.sessionId.value) return

  input.value = ''
  if (inputEl.value) inputEl.value.style.height = 'auto'

  if (mode.value === 'guide') {
    await sendGuideMessage(text)
  } else {
    await episteme.sendMessage(text)
    scrollToBottom()
  }
}

function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

// ── Socratic session history ──────────────────────────────────────────────────
const showSocraticHistory = ref(false)
const socraticHistory = ref([])
const socraticHistoryLoading = ref(false)

async function toggleSocraticHistory() {
  showSocraticHistory.value = !showSocraticHistory.value
  if (showSocraticHistory.value && !socraticHistory.value.length) {
    await fetchSocraticHistory()
  }
}

async function fetchSocraticHistory() {
  socraticHistoryLoading.value = true
  try {
    const token = auth.session?.access_token
    const res = await fetch(`${API_BASE}/socratic/sessions`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    if (res.ok) {
      const data = await res.json()
      socraticHistory.value = data.sessions || []
    }
  } catch { /* ignore */ }
  finally { socraticHistoryLoading.value = false }
}

async function loadSocraticSession(sessionId) {
  showSocraticHistory.value = false
  try {
    const token = auth.session?.access_token
    const res = await fetch(`${API_BASE}/socratic/sessions/${sessionId}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    if (res.ok) {
      const data = await res.json()
      episteme.loadSession(data)
      // Restore domain selector state
      selectedDomain.value = data.session.domain
      scrollToBottom()
    }
  } catch (err) {
    console.error('Failed to load socratic session:', err)
  }
}

function domainLabel(d) {
  return { general: 'General thinking', ml: 'ML concepts', statistics: 'Statistics', economics: 'Economics', cs: 'Computer Science' }[d] ?? d
}

// ── State styling helpers ─────────────────────────────────────────────────────
const stateClass = computed(() => ({
  PROBE: 'state-probe',
  DEEPEN: 'state-deepen',
  SCAFFOLD: 'state-scaffold',
  RECTIFY: 'state-rectify',
  REDIRECT: 'state-redirect',
  CONSOLIDATE: 'state-consolidate',
  COMPLETE: 'state-complete',
}[episteme.currentState.value] ?? 'state-probe'))

const depthClass = computed(() => ({
  SURFACE: 'depth-surface',
  CONCEPTUAL: 'depth-conceptual',
  ANALYTICAL: 'depth-analytical',
  SYNTHESIS: 'depth-synthesis',
}[episteme.depthLevel.value] ?? 'depth-surface'))

function stateClassFor(state) {
  return {
    PROBE: 'state-probe', DEEPEN: 'state-deepen', SCAFFOLD: 'state-scaffold',
    RECTIFY: 'state-rectify', REDIRECT: 'state-redirect',
    CONSOLIDATE: 'state-consolidate', COMPLETE: 'state-complete',
  }[state] ?? 'state-probe'
}

function stateLabelFor(state) {
  return { PROBE: 'Probing', DEEPEN: 'Deepening', SCAFFOLD: 'Scaffolding',
           RECTIFY: 'Correcting', REDIRECT: 'Redirecting',
           CONSOLIDATE: 'Consolidating', COMPLETE: 'Complete' }[state] ?? state
}

// Auto-scroll socratic messages when content streams in
watch(episteme.messages, () => {
  if (mode.value === 'socratic') scrollToBottom()
}, { deep: true })

// Auto-switch to socratic mode if navigated from Learn page banner
onMounted(() => {
  if (route.query.mode === 'socratic') mode.value = 'socratic'
})

// Refresh socratic history cache when a turn completes so the panel shows updated data
watch(episteme.turnNumber, () => {
  if (socraticHistory.value.length) socraticHistory.value = []
})

// ── Insight card export ───────────────────────────────────────────────────────
const copiedInsight = ref(false)

function buildInsightText(card, md = false) {
  const gaps = card.gaps?.length ? (md ? '## Explore next\n' : 'Explore next:\n') + card.gaps.map(g => `- ${g}`).join('\n') + '\n\n' : ''
  const next = card.next_question ? (md ? '## Next question\n> ' : 'Next question: ') + card.next_question : ''
  return `${md ? '# ' : ''}Insight: ${card.concept}\n\n${card.insight}\n\n${gaps}${next}${md ? '\n\n---\n*Generated by Sentio Socratic Engine*' : ''}`
}

function copyInsight() {
  const card = episteme.insightCard.value
  if (!card) return
  navigator.clipboard.writeText(buildInsightText(card))
  copiedInsight.value = true
  setTimeout(() => { copiedInsight.value = false }, 2000)
}

function exportInsightMd() {
  const card = episteme.insightCard.value
  if (!card) return
  const blob = new Blob([buildInsightText(card, true)], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `insight-${card.concept.slice(0, 30).replace(/\s+/g, '-').toLowerCase()}.md`
  a.click()
  URL.revokeObjectURL(url)
}

function exportInsightPdf() {
  const card = episteme.insightCard.value
  if (!card) return
  const gapsHtml = card.gaps?.length ? `<h2>Explore next</h2><ul>${card.gaps.map(g => `<li>${g}</li>`).join('')}</ul>` : ''
  const nextHtml = card.next_question ? `<blockquote>${card.next_question}</blockquote>` : ''
  const win = window.open('', '_blank')
  if (!win) return
  win.document.write(`<!DOCTYPE html><html><head><title>Insight: ${card.concept}</title><style>body{font-family:'Segoe UI',sans-serif;max-width:620px;margin:48px auto;color:#352b38;line-height:1.7;}h1{font-size:22px;margin-bottom:6px;color:#352b38;}h2{font-size:14px;font-weight:700;margin-top:24px;color:#6b6b8a;}p{font-size:15px;margin:12px 0;}ul{padding-left:20px;}li{font-size:13px;margin-bottom:4px;}blockquote{border-left:3px solid #9b94e8;padding:8px 14px;margin:16px 0;color:#555;font-style:italic;background:#f4f2ff;border-radius:4px;}footer{margin-top:48px;font-size:11px;color:#aaa;}</style></head><body><h1>${card.concept}</h1><p>${card.insight}</p>${gapsHtml}${nextHtml}<footer>Generated by Sentio Socratic Engine</footer></body></html>`)
  win.document.close()
  win.print()
}
</script>

<style>
@import 'katex/dist/katex.min.css';

.md-content p { margin: 0 0 0.5em 0; }
.md-content p:last-child { margin: 0; }
.md-content strong { font-weight: 700; color: inherit; }
.md-content code { background: rgba(0,0,0,0.06); padding: 2px 4px; border-radius: 4px; font-family: monospace; font-size: 0.9em; }
.md-content pre { background: rgba(0,0,0,0.06); padding: 8px; border-radius: 6px; overflow-x: auto; margin: 0.5em 0; }
.md-content pre code { background: none; padding: 0; }
.md-content ul, .md-content ol { margin: 0.5em 0; padding-left: 20px; }
.md-content li { margin-bottom: 0.25em; }
.md-content blockquote { border-left: 3px solid rgba(0,0,0,0.2); padding-left: 10px; margin: 0.5em 0; color: inherit; opacity: 0.9; }
</style>
<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800&display=swap');
* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

/* ═══════════════════════════════════════════════════════════
   LAYOUT SHELL
   ═══════════════════════════════════════════════════════════ */
.guide-layout {
  display: flex; flex-direction: column;
  height: calc(100vh - 64px);
  margin: -32px;
  overflow: hidden;
}

/* ═══════════════════════════════════════════════════════════
   HEADER
   ═══════════════════════════════════════════════════════════ */
.guide-header {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 24px;
  border-bottom: 1px solid var(--lavender-soft);
  background: var(--bg, #f4f3f8);
  flex-shrink: 0;
}
.ai-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: linear-gradient(135deg, #352b38, #9b94e8);
  display: flex; align-items: center; justify-content: center;
  color: white; flex-shrink: 0;
}
.header-info { min-width: 0; }
.header-title { font-size: 14px; font-weight: 700; color: var(--plum); line-height: 1.2; }
.header-sub { font-size: 11px; color: var(--slate); }
.header-actions { display: flex; align-items: center; gap: 4px; margin-left: auto; }
.hdr-btn {
  width: 30px; height: 30px; border-radius: 8px;
  background: transparent; border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: var(--slate); transition: all 0.15s;
}
.hdr-btn:hover, .hdr-btn.active { background: var(--lavender); color: var(--plum); }
.status-dot { width: 7px; height: 7px; border-radius: 50%; background: #059669; flex-shrink: 0; }

/* Mode toggle pill */
.mode-toggle {
  display: flex; align-items: center;
  background: rgba(53,43,56,0.08);
  border-radius: 99px; padding: 3px;
  gap: 2px; flex-shrink: 0;
}
.mode-btn {
  font-family: 'Urbanist'; font-size: 12px; font-weight: 600;
  padding: 6px 14px; border-radius: 99px;
  border: none; cursor: pointer;
  color: var(--slate); background: transparent;
  transition: all 0.2s; white-space: nowrap;
  display: flex; align-items: center; gap: 5px;
}
.mode-btn.active {
  background: var(--plum); color: white;
  box-shadow: 0 2px 10px rgba(53,43,56,0.28);
}

/* ═══════════════════════════════════════════════════════════
   SHARED: MESSAGES + BUBBLES
   ═══════════════════════════════════════════════════════════ */
.chat-messages {
  flex: 1; overflow-y: auto;
  padding: 20px 24px;
  display: flex; flex-direction: column; gap: 12px;
  background: var(--lavender-soft, #f0eef9);
}
.message-wrap { display: flex; align-items: flex-end; gap: 8px; }
.message-wrap.user { flex-direction: row-reverse; }
.message-wrap.assistant { flex-direction: row; }
.msg-avatar {
  width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, #352b38, #9b94e8);
  display: flex; align-items: center; justify-content: center; color: white;
}
.socratic-avatar { background: linear-gradient(135deg, #4a3550, #b8b4f0); }
.bubble {
  max-width: 68%; padding: 10px 14px;
  display: flex; flex-direction: column; gap: 4px; word-break: break-word;
}
.bubble.assistant {
  background: white; color: var(--plum);
  border-radius: 4px 14px 14px 14px;
  border: 1px solid var(--lavender-soft);
  box-shadow: 0 2px 8px rgba(53,43,56,0.06);
}
.bubble.user {
  background: var(--plum); color: white;
  border-radius: 14px 4px 14px 14px;
}
.bubble-text { font-size: 14px; line-height: 1.65; white-space: pre-line; }
.bubble-ts { font-size: 10px; opacity: 0.45; align-self: flex-end; }

.state-label-inline {
  font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 99px;
  display: inline-block; margin-bottom: 6px; letter-spacing: 0.3px;
  width: fit-content;
}

/* Typing indicators */
.typing-cursor { animation: blink 0.6s infinite; margin-left: 1px; }
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0; } }
.typing-dots { display: inline-flex; align-items: center; gap: 4px; margin-left: 2px; vertical-align: middle; }
.typing-dots span {
  display: inline-block; width: 5px; height: 5px; border-radius: 50%;
  background: var(--lavender-deep);
  animation: dot-bounce 1.2s infinite ease-in-out;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes dot-bounce { 0%,60%,100% { transform: translateY(0); opacity: 0.4; } 30% { transform: translateY(-4px); opacity: 1; } }

/* ═══════════════════════════════════════════════════════════
   GUIDE MODE
   ═══════════════════════════════════════════════════════════ */
.guide-body {
  flex: 1; display: flex; overflow: hidden; position: relative;
}
.suggestions-bar { display: flex; gap: 8px; flex-wrap: wrap; padding-bottom: 8px; }
.suggestion-chip {
  font-family: 'Urbanist'; font-size: 12px; font-weight: 500;
  color: var(--plum); background: white;
  border: 1.5px solid var(--lavender); border-radius: 99px;
  padding: 7px 14px; cursor: pointer; transition: all 0.15s;
}
.suggestion-chip:hover { background: var(--lavender); }

/* History panel */
.history-panel {
  width: 272px; flex-shrink: 0;
  background: white;
  border-left: 1px solid var(--lavender-soft);
  border-radius: 20px 0 0 20px;
  display: flex; flex-direction: column; overflow: hidden;
  box-shadow: -4px 0 24px rgba(53,43,56,0.06);
}
.history-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 16px 12px;
  border-bottom: 1px solid var(--lavender-soft); flex-shrink: 0;
}
.history-title { font-size: 13px; font-weight: 700; color: var(--plum); }
.history-empty { flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 13px; color: var(--slate); padding: 32px 16px; text-align: center; }
.history-list { flex: 1; overflow-y: auto; padding: 8px; }
.history-item { width: 100%; text-align: left; background: transparent; border: none; cursor: pointer; padding: 10px 12px; border-radius: 12px; transition: background 0.13s; margin-bottom: 2px; }
.history-item:hover { background: var(--lavender-soft); }
.history-item.active { background: var(--lavender); }
.history-item-preview { font-size: 13px; font-weight: 500; color: var(--plum); line-height: 1.4; margin-bottom: 3px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.history-item-meta { font-size: 11px; color: var(--slate); }
.history-slide-enter-active, .history-slide-leave-active { transition: width 0.24s cubic-bezier(0.4,0,0.2,1), opacity 0.2s ease; overflow: hidden; }
.history-slide-enter-from, .history-slide-leave-to { width: 0 !important; opacity: 0; }

/* Socratic history panel */
.soc-history-panel {
  position: absolute; left: 0; top: 0; bottom: 0;
  width: 272px; z-index: 10; flex-shrink: 0;
  background: white;
  border-right: 1px solid var(--lavender-soft);
  border-radius: 0 20px 20px 0;
  display: flex; flex-direction: column; overflow: hidden;
  box-shadow: 4px 0 24px rgba(53,43,56,0.08);
}
.soc-hist-domain {
  font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px;
  color: var(--lavender-deep); margin-bottom: 3px;
}
.hist-complete-pill {
  font-size: 9px; font-weight: 700; background: #d1fae5; color: #065f46;
  border-radius: 99px; padding: 1px 6px; margin-left: 4px; vertical-align: middle;
}
.soc-history-slide-enter-active, .soc-history-slide-leave-active { transition: transform 0.24s cubic-bezier(0.4,0,0.2,1), opacity 0.2s ease; }
.soc-history-slide-enter-from, .soc-history-slide-leave-to { transform: translateX(-100%); opacity: 0; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ═══════════════════════════════════════════════════════════
   LIVE COGNITIVE SIGNALS
   ═══════════════════════════════════════════════════════════ */
.cognitive-signals {
  background: var(--bg, #edeaf4);
  border: 1px solid var(--lavender-soft);
  border-radius: 14px; padding: 12px 14px;
  margin-bottom: 10px; display: flex; flex-direction: column; gap: 8px;
}
.signals-header {
  display: flex; align-items: center; gap: 5px;
  font-size: 10px; font-weight: 700; color: var(--slate);
  text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 2px;
}
.signal-row {
  display: flex; align-items: center; gap: 8px;
}
.signal-name {
  font-size: 11px; font-weight: 600; color: var(--slate);
  width: 52px; flex-shrink: 0;
}
.signal-track {
  flex: 1; height: 5px; background: rgba(155,148,232,0.2);
  border-radius: 99px; overflow: hidden;
}
.signal-fill {
  height: 100%; border-radius: 99px;
  transition: width 0.3s cubic-bezier(0.4,0,0.2,1);
}
.signal-analysis { background: linear-gradient(90deg, #9b94e8, #b8b4f0); }
.signal-depth    { background: linear-gradient(90deg, #34d399, #6ee7b7); }
.signal-clarity  { background: linear-gradient(90deg, #60a5fa, #93c5fd); }
.signal-val {
  font-size: 10px; font-weight: 700; color: var(--slate);
  width: 48px; text-align: right; flex-shrink: 0;
}
.signal-depth-val { color: #059669; }
.signal-clarity-val { color: #2563eb; }

/* Signals transition */
.signals-fade-enter-active { transition: all 0.22s ease; }
.signals-fade-leave-active { transition: all 0.18s ease; }
.signals-fade-enter-from, .signals-fade-leave-to { opacity: 0; transform: translateY(6px); }

/* ═══════════════════════════════════════════════════════════
   SOCRATIC MODE
   ═══════════════════════════════════════════════════════════ */
.socratic-body {
  flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative;
}

/* Mobile strip */
.socratic-strip {
  display: none; /* shown on mobile via media query */
  align-items: center; gap: 10px;
  padding: 8px 16px;
  background: white; border-bottom: 1px solid var(--lavender-soft);
  flex-shrink: 0; overflow-x: auto;
}
.strip-clarity { display: flex; align-items: baseline; gap: 2px; }
.strip-score { font-size: 18px; font-weight: 800; color: var(--plum); }
.strip-label { font-size: 10px; color: var(--slate); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.strip-divider { width: 1px; height: 20px; background: var(--lavender-soft); flex-shrink: 0; }
.strip-turns { font-size: 11px; color: var(--slate); font-weight: 600; white-space: nowrap; margin-left: auto; }
.strip-insight-btn {
  font-family: 'Urbanist'; font-size: 11px; font-weight: 700;
  background: var(--plum); color: white;
  border: none; border-radius: 99px; padding: 4px 12px; cursor: pointer;
  transition: all 0.15s; white-space: nowrap;
  display: flex; align-items: center; gap: 4px;
}
.strip-insight-btn:hover:not(:disabled) { background: #4a3550; }
.strip-insight-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Main split */
.socratic-main {
  flex: 1; display: flex; overflow: hidden;
}
.socratic-chat {
  flex: 1; display: flex; flex-direction: column; overflow: hidden;
  background: var(--lavender-soft);
}

/* Domain selector */
.domain-selector {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 32px 24px; gap: 16px; text-align: center;
}
.domain-icon {
  width: 60px; height: 60px; border-radius: 50%;
  background: linear-gradient(135deg, #dad8f9, #eceaf9);
  display: flex; align-items: center; justify-content: center;
  color: var(--lavender-deep); margin-bottom: 4px;
}
.domain-heading { font-size: 22px; font-weight: 800; color: var(--plum); margin: 0; }
.domain-sub { font-size: 14px; color: var(--slate); max-width: 360px; margin: 0; line-height: 1.55; }
.domain-grid {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 10px; width: 100%; max-width: 420px; margin-top: 4px;
}
.domain-card {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding: 16px 10px; border-radius: 16px;
  background: white; border: 2px solid var(--lavender-soft);
  cursor: pointer; transition: all 0.15s; font-family: 'Urbanist';
}
.domain-card:hover { border-color: var(--lavender); transform: translateY(-2px); box-shadow: 0 4px 16px rgba(53,43,56,0.08); }
.domain-card.selected { border-color: var(--lavender-deep); background: #f4f2ff; box-shadow: 0 0 0 3px rgba(155,148,232,0.15); }
.domain-icon-svg { color: var(--lavender-deep); }
.domain-card.selected .domain-icon-svg { color: var(--plum); }
.domain-label { font-size: 12px; font-weight: 600; color: var(--plum); }
.start-btn {
  display: flex; align-items: center; gap: 8px;
  font-family: 'Urbanist'; font-size: 14px; font-weight: 700;
  background: var(--plum); color: white;
  border: none; border-radius: 12px; padding: 12px 28px;
  cursor: pointer; transition: all 0.18s; margin-top: 4px;
}
.start-btn:hover { background: #4a3550; transform: translateY(-1px); box-shadow: 0 4px 16px rgba(53,43,56,0.22); }

/* Session started — first turn prompt */
.session-prompt {
  display: flex; flex-direction: column; align-items: center;
  text-align: center; gap: 12px;
  margin: auto; max-width: 340px; padding: 24px;
}
.session-prompt-icon {
  width: 44px; height: 44px; border-radius: 50%;
  background: white; border: 1.5px solid var(--lavender);
  display: flex; align-items: center; justify-content: center;
  color: var(--lavender-deep);
}
.session-prompt-text { font-size: 14px; color: var(--slate); line-height: 1.6; }

/* Cognitive panel */
.cognitive-panel {
  width: 264px; flex-shrink: 0;
  background: white;
  border-left: 1px solid var(--lavender-soft);
  border-radius: 20px 0 0 20px;
  overflow-y: auto; padding: 14px 12px;
  display: flex; flex-direction: column; gap: 8px;
  box-shadow: -4px 0 24px rgba(53,43,56,0.05);
}
.panel-section {
  background: var(--bg, #edeaf4);
  border-radius: 14px; padding: 12px 14px;
}
.panel-label { font-size: 10px; font-weight: 700; color: var(--slate); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; }
.panel-divider { display: none; }

/* Clarity */
.clarity-display { display: flex; align-items: baseline; gap: 2px; margin-bottom: 8px; }
.clarity-number { font-size: 40px; font-weight: 900; color: var(--plum); line-height: 1; }
.clarity-max { font-size: 14px; color: var(--slate); }
.clarity-track {
  height: 6px; background: var(--lavender-soft); border-radius: 99px; overflow: hidden; margin-bottom: 6px;
}
.clarity-fill {
  height: 100%; background: linear-gradient(90deg, #9b94e8, #b8b4f0);
  border-radius: 99px; transition: width 0.6s ease;
}
.clarity-hint { font-size: 10px; color: var(--slate); }

/* State badge */
.state-badge-lg {
  display: inline-block; font-size: 12px; font-weight: 700;
  padding: 4px 12px; border-radius: 99px; margin-bottom: 6px; letter-spacing: 0.3px;
}
.state-desc { font-size: 12px; color: var(--slate); line-height: 1.45; }

/* Depth badge */
.depth-badge-lg {
  display: inline-block; font-size: 12px; font-weight: 700;
  padding: 4px 12px; border-radius: 99px; letter-spacing: 0.3px;
}

/* Turn progress */
.turn-display { font-size: 14px; font-weight: 700; color: var(--plum); margin-bottom: 8px; }
.turn-track { height: 4px; background: var(--lavender-soft); border-radius: 99px; overflow: hidden; }
.turn-fill { height: 100%; background: linear-gradient(90deg, #9b94e8, #dad8f9); border-radius: 99px; transition: width 0.4s ease; }

/* Insight button */
.insight-btn {
  display: flex; align-items: center; gap: 6px; width: 100%;
  font-family: 'Urbanist'; font-size: 13px; font-weight: 700;
  background: linear-gradient(135deg, #352b38, #4a3550); color: white;
  border: none; border-radius: 10px; padding: 10px 14px;
  cursor: pointer; transition: all 0.18s;
}
.insight-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(53,43,56,0.24); }
.insight-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
.insight-hint { font-size: 10px; color: var(--slate); margin-top: 6px; }

/* Insight card */
.insight-card {
  background: linear-gradient(135deg, #f4f2ff 0%, #eceaf9 100%);
  border: 1px solid var(--lavender); border-radius: 16px;
  padding: 14px; display: flex; flex-direction: column; gap: 10px;
  box-shadow: 0 2px 12px rgba(155,148,232,0.15);
}
.insight-card-header { display: flex; align-items: center; gap: 5px; font-size: 10px; font-weight: 700; color: var(--lavender-deep); text-transform: uppercase; letter-spacing: 0.8px; }
.insight-concept { font-size: 13px; font-weight: 800; color: var(--plum); }
.insight-text { font-size: 12px; color: var(--plum); line-height: 1.6; }
.gaps-label { font-size: 10px; font-weight: 700; color: var(--slate); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.gaps-pills { display: flex; flex-wrap: wrap; gap: 4px; }
.gap-pill { font-size: 10px; font-weight: 600; background: white; color: var(--plum); border: 1px solid var(--lavender); border-radius: 99px; padding: 2px 8px; }
.insight-next { display: flex; align-items: flex-start; gap: 5px; font-size: 11px; color: var(--slate); line-height: 1.5; font-style: italic; }
.insight-export-btns { display: flex; gap: 6px; margin-top: 4px; }
.export-btn {
  font-family: 'Urbanist'; font-size: 10px; font-weight: 700;
  display: flex; align-items: center; gap: 4px;
  padding: 4px 10px; border-radius: 99px;
  border: 1px solid var(--lavender); background: white;
  color: var(--plum); cursor: pointer; transition: all 0.15s;
}
.export-btn:hover { background: var(--lavender); }

/* ═══════════════════════════════════════════════════════════
   STATE & DEPTH COLOR TOKENS
   ═══════════════════════════════════════════════════════════ */
.state-probe      { background: #dbeafe; color: #1e40af; }
.state-deepen     { background: #d1fae5; color: #065f46; }
.state-scaffold   { background: #fef9c3; color: #92400e; }
.state-rectify    { background: #fee2e2; color: #991b1b; }
.state-redirect   { background: #dad8f9; color: #352b38; }
.state-consolidate { background: #e0f2fe; color: #0c4a6e; }
.state-complete   { background: #d1fae5; color: #065f46; }

.depth-surface    { background: #eceaf9; color: #352b38; }
.depth-conceptual { background: #dbeafe; color: #1e40af; }
.depth-analytical { background: #d1fae5; color: #065f46; }
.depth-synthesis  { background: linear-gradient(135deg, #dad8f9, #f9d8f0); color: #352b38; }

/* State label inline in bubbles */
.state-probe.state-label-inline      { background: #dbeafe; color: #1e40af; }
.state-deepen.state-label-inline     { background: #d1fae5; color: #065f46; }
.state-scaffold.state-label-inline   { background: #fef9c3; color: #92400e; }
.state-rectify.state-label-inline    { background: #fee2e2; color: #991b1b; }
.state-redirect.state-label-inline   { background: #dad8f9; color: #352b38; }
.state-consolidate.state-label-inline { background: #e0f2fe; color: #0c4a6e; }
.state-complete.state-label-inline   { background: #d1fae5; color: #065f46; }

/* ═══════════════════════════════════════════════════════════
   INPUT AREA
   ═══════════════════════════════════════════════════════════ */
.input-area {
  padding: 12px 24px 16px;
  border-top: 1px solid var(--lavender-soft);
  background: white; flex-shrink: 0;
  display: flex; flex-direction: column; gap: 6px;
}
.input-wrap {
  display: flex; align-items: center; gap: 8px;
  background: var(--lavender-soft, #f0eef9);
  border: 1.5px solid var(--lavender);
  border-radius: 12px; padding: 8px 8px 8px 14px;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.input-wrap.focused { border-color: var(--lavender-deep); box-shadow: 0 0 0 3px rgba(155,148,232,0.12); }
.chat-input {
  flex: 1; font-family: 'Urbanist'; font-size: 14px;
  color: var(--plum); background: transparent;
  border: none; outline: none; resize: none;
  line-height: 1.5; max-height: 120px; padding: 2px 0;
}
.chat-input::placeholder { color: var(--slate); opacity: 0.7; }
.send-btn {
  width: 36px; height: 36px; border-radius: 9px;
  background: var(--plum); border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: all 0.15s; color: white;
}
.send-btn:hover:not(:disabled) { background: #4a3550; transform: scale(1.04); }
.send-btn:disabled { opacity: 0.35; cursor: not-allowed; transform: none; }
.safety-notice { font-size: 11px; color: var(--slate); text-align: center; }
.safety-link { color: var(--lavender-deep); font-weight: 600; text-decoration: none; }
.safety-link:hover { text-decoration: underline; }

/* ═══════════════════════════════════════════════════════════
   RESPONSIVE
   ═══════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
  .guide-layout { height: calc(100vh - 56px); margin: -16px; }
  .guide-header { padding: 8px 12px; }
  .header-sub { display: none; }
  .mode-toggle { margin: 0 auto; }
  .chat-messages { padding: 12px; gap: 10px; }
  .bubble { max-width: 85%; }
  .input-area { padding: 8px 12px 12px; }
  .suggestion-chip { font-size: 11px; padding: 6px 10px; }
  .domain-grid { grid-template-columns: repeat(2, 1fr); max-width: 320px; }
  .domain-heading { font-size: 18px; }

  /* Show strip, hide panel */
  .socratic-strip { display: flex; }
  .cognitive-panel { display: none; }

  /* History panel becomes overlay on mobile */
  .history-panel {
    position: absolute; top: 0; right: 0; bottom: 0;
    width: 100% !important; z-index: 10; border-left: none;
    box-shadow: -4px 0 20px rgba(53,43,56,0.12);
  }
}

@media (max-width: 480px) {
  .domain-grid { grid-template-columns: repeat(2, 1fr); }
  .mode-btn { font-size: 11px; padding: 4px 10px; }
}
</style>
