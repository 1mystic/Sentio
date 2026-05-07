<template>
  <div class="new-entry-page">

    <!-- Back + Title -->
    <div class="page-top">
      <router-link to="/journal" class="btn btn-ghost btn-sm">
        <ArrowLeft :size="14" /> Back to Journal
      </router-link>
      <h1 class="page-title">New Journal Entry</h1>
    </div>

    <div class="editor-layout">

      <!-- Main Editor Card -->
      <div class="editor-card card">

        <!-- Mood Selector -->
        <div class="mood-section">
          <span class="mood-label">How are you feeling?</span>
          <div class="mood-row">
            <button
              v-for="m in moods"
              :key="m"
              class="mood-btn"
              :class="{ selected: mood === m }"
              @click="mood = m"
            >{{ m }}</button>
          </div>
        </div>

        <div class="divider"></div>

        <!-- Title Input -->
        <input
          v-model="title"
          class="title-input"
          placeholder="What's on your mind?"
          maxlength="120"
        />

        <!-- Markdown Toolbar + Write/Preview toggle -->
        <div class="editor-topbar">
          <div class="md-toolbar">
            <button class="tb-btn" title="Bold (Ctrl+B)" @click="wrapSelection('**', '**')"><Bold :size="13" /></button>
            <button class="tb-btn" title="Italic (Ctrl+I)" @click="wrapSelection('_', '_')"><Italic :size="13" /></button>
            <button class="tb-btn" title="Heading" @click="insertLinePrefix('## ')"><Heading2 :size="13" /></button>
            <button class="tb-btn" title="Bullet list" @click="insertLinePrefix('- ')"><List :size="13" /></button>
            <button class="tb-btn" title="Inline code" @click="wrapSelection('`', '`')"><Code :size="13" /></button>
            <button class="tb-btn" title="Code block" @click="wrapSelection('\n```\n', '\n```\n')"><CodeXml :size="13" /></button>
            <button class="tb-btn" title="Quote" @click="insertLinePrefix('> ')"><Quote :size="13" /></button>
            <div class="tb-divider"></div>
            <span class="md-hint">Markdown supported</span>
          </div>
          <div class="view-toggle">
            <button class="view-btn" :class="{ active: editorMode === 'write' }" @click="editorMode = 'write'">
              <Pen :size="12" /> Write
            </button>
            <button class="view-btn" :class="{ active: editorMode === 'preview' }" @click="editorMode = 'preview'">
              <Eye :size="12" /> Preview
            </button>
          </div>
        </div>

        <!-- Write mode textarea -->
        <textarea
          v-show="editorMode === 'write'"
          ref="textareaEl"
          v-model="content"
          class="content-textarea"
          placeholder="Write freely... supports **bold**, _italic_, ## headings, - lists, `code`"
          @keydown="handleKeydown"
        ></textarea>

        <!-- Preview mode rendered output -->
        <div
          v-show="editorMode === 'preview'"
          class="md-preview"
          v-html="renderedPreview || '<p class=\'preview-empty\'>Nothing to preview yet…</p>'"
        ></div>

        <!-- Writing Prompts -->
        <div class="prompts-section">
          <button class="btn btn-ghost btn-sm prompts-toggle" @click="showPrompts = !showPrompts">
            <Sparkles :size="14" /> Need inspiration?
            <span class="toggle-arrow">{{ showPrompts ? '▲' : '▼' }}</span>
          </button>
          <div v-if="showPrompts" class="prompts-list">
            <button
              v-for="prompt in prompts"
              :key="prompt"
              class="prompt-chip"
              @click="appendPrompt(prompt)"
            >{{ prompt }}</button>
          </div>
        </div>

        <!-- Action Bar -->
        <div class="action-bar">
          <button class="btn btn-ghost" @click="saveEntry(true)" :disabled="saving || !content.trim()">
            {{ saving ? 'Saving…' : 'Save & Keep Editing' }}
          </button>
          <button class="btn btn-primary" @click="saveEntry(false)" :disabled="saving || !content.trim()">
            {{ saving ? 'Saving…' : 'Save Entry' }}
          </button>
        </div>

      </div>

      <!-- Right Sidebar -->
      <div class="sidebar">

        <!-- AI Analysis Pane -->
        <div class="card ai-card">
          <div class="ai-header">
            <Sparkles :size="16" class="ai-icon" />
            <span class="ai-label">Real-time Analysis</span>
          </div>
          <div v-if="!content.trim()" class="ai-empty">
            <p>Start writing to see your patterns...</p>
          </div>
          <div v-else class="ai-results">
            <div v-if="!detectedBiases.length" class="ai-none">No strong patterns detected yet.</div>
            <div v-for="bias in detectedBiases" :key="bias.name" class="detected-bias">
              <span class="badge badge-lavender">{{ bias.name }}</span>
              <span class="bias-note">{{ bias.note }}</span>
            </div>
          </div>
        </div>

        <!-- Word Count -->
        <div class="card meta-card">
          <div class="meta-row">
            <span class="meta-label">Words</span>
            <span class="meta-value">{{ wordCount }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-label">Characters</span>
            <span class="meta-value">{{ content.length }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-label">Est. read time</span>
            <span class="meta-value">{{ readTime }} min</span>
          </div>
        </div>

        <!-- Tags -->
        <div class="card tags-card">
          <div class="tags-header">Tags</div>
          <div class="tags-wrap">
            <span v-for="tag in tags" :key="tag" class="tag-chip">
              {{ tag }} <button class="tag-remove" @click="removeTag(tag)"><X :size="12" /></button>
            </span>
          </div>
          <div class="tag-input-wrap">
            <input
              v-model="tagInput"
              class="input tag-input"
              placeholder="Add a tag…"
              @keydown.enter.prevent="addTag"
            />
          </div>
        </div>

      </div>
    </div>

    <!-- Toast -->
    <div v-if="toastVisible" class="toast" :class="{ 'toast-error': toastError }">
      <Check v-if="!toastError" :size="14" />
      {{ toastError ? 'Failed to save. Please try again.' : 'Saved!' }}
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useJournalStore } from '@/stores/journal.js'
import { marked } from 'marked'
import {
  Sparkles, ArrowLeft, X, Check,
  Bold, Italic, Heading2, List, Code, CodeXml, Quote, Pen, Eye,
} from 'lucide-vue-next'

marked.setOptions({ breaks: true, gfm: true })

const router = useRouter()
const journalStore = useJournalStore()

const title = ref('')
const content = ref('')
const mood = ref('😊')
const moods = ['😊', '😐', '😔', '😤', '😴']
const showPrompts = ref(false)
const saving = ref(false)
const toastVisible = ref(false)
const toastError = ref(false)
const tagInput = ref('')
const tags = ref([])
const editorMode = ref('write') // 'write' | 'preview'
const textareaEl = ref(null)

const prompts = ref([
  'Describe a decision you made today — what information did you rely on?',
  'Was there a moment when you felt defensive? What triggered it?',
  'Did you change your mind about anything today? What caused it?',
  'What assumptions are you making about an ongoing situation?',
])

// ── Reactive markdown preview ──────────────────────────────────────────────────
const renderedPreview = computed(() => content.value.trim() ? marked.parse(content.value) : '')

// ── Stats ──────────────────────────────────────────────────────────────────────
const wordCount = computed(() => content.value.trim().split(/\s+/).filter(Boolean).length)
const readTime = computed(() => Math.max(1, Math.ceil(wordCount.value / 200)))

// ── Bias detection ─────────────────────────────────────────────────────────────
const detectedBiases = computed(() => {
  const text = content.value.toLowerCase()
  const found = []
  if (/\b(always knew|confirmed|knew it|as i expected)\b/.test(text))
    found.push({ name: 'Confirmation Bias', note: 'Seeking confirming evidence' })
  if (/\b(everyone|no one|nobody|always|never)\b/.test(text))
    found.push({ name: 'Overgeneralization', note: 'Broad sweeping conclusions' })
  if (/\b(sunk|already spent|already invested|wasted|can't back out)\b/.test(text))
    found.push({ name: 'Sunk Cost Fallacy', note: 'Valuing past investment over future outcome' })
  if (/\b(definitely|certain|obviously|clearly|without a doubt)\b/.test(text))
    found.push({ name: 'Overconfidence', note: 'High certainty without full data' })
  if (/\b(everyone else|most people|the crowd|popular opinion)\b/.test(text))
    found.push({ name: 'Bandwagon Effect', note: 'Following the majority' })
  if (/\b(first impression|initially thought|original price|started at)\b/.test(text))
    found.push({ name: 'Anchoring Bias', note: 'Over-relying on first information' })
  return found
})

// ── Markdown toolbar helpers ───────────────────────────────────────────────────
function wrapSelection(before, after) {
  const el = textareaEl.value
  if (!el) return
  editorMode.value = 'write'
  const start = el.selectionStart
  const end = el.selectionEnd
  const selected = content.value.slice(start, end)
  const replacement = before + (selected || 'text') + after
  content.value = content.value.slice(0, start) + replacement + content.value.slice(end)
  // Restore selection inside the markers
  const cursorStart = start + before.length
  const cursorEnd = cursorStart + (selected || 'text').length
  el.focus()
  setTimeout(() => el.setSelectionRange(cursorStart, cursorEnd), 0)
}

function insertLinePrefix(prefix) {
  const el = textareaEl.value
  if (!el) return
  editorMode.value = 'write'
  const start = el.selectionStart
  const lineStart = content.value.lastIndexOf('\n', start - 1) + 1
  content.value = content.value.slice(0, lineStart) + prefix + content.value.slice(lineStart)
  el.focus()
  setTimeout(() => el.setSelectionRange(lineStart + prefix.length, lineStart + prefix.length), 0)
}

function handleKeydown(e) {
  // Ctrl+B / Ctrl+I shortcuts
  if (e.ctrlKey || e.metaKey) {
    if (e.key === 'b') { e.preventDefault(); wrapSelection('**', '**') }
    if (e.key === 'i') { e.preventDefault(); wrapSelection('_', '_') }
  }
  // Tab → insert 2 spaces
  if (e.key === 'Tab') {
    e.preventDefault()
    const el = textareaEl.value
    const s = el.selectionStart
    content.value = content.value.slice(0, s) + '  ' + content.value.slice(el.selectionEnd)
    setTimeout(() => el.setSelectionRange(s + 2, s + 2), 0)
  }
}

function appendPrompt(prompt) {
  content.value += (content.value ? '\n\n' : '') + prompt
}

// ── Tags ───────────────────────────────────────────────────────────────────────
function addTag() {
  const t = tagInput.value.trim()
  if (t && !tags.value.includes(t)) tags.value.push(t)
  tagInput.value = ''
}

function removeTag(tag) {
  tags.value = tags.value.filter(t => t !== tag)
}

// ── Save ───────────────────────────────────────────────────────────────────────
async function saveEntry(keepEditing = false) {
  if (!content.value.trim()) return
  saving.value = true
  const { data, error: err } = await journalStore.createEntry({
    content: content.value,
    prompt_used: title.value || null,
  })
  saving.value = false
  if (err) {
    toastError.value = true
    toastVisible.value = true
    setTimeout(() => { toastVisible.value = false; toastError.value = false }, 3000)
  } else if (keepEditing) {
    toastVisible.value = true
    setTimeout(() => { toastVisible.value = false }, 2000)
  } else {
    router.push(`/journal/${data.id}`)
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

:root {
  --plum: #352b38;
  --slate: #7e808c;
  --lavender: #dad8f9;
  --lavender-deep: #9b94e8;
  --lavender-mid: #b8b4f0;
  --lavender-soft: #eceaf9;
}

.new-entry-page { display: flex; flex-direction: column; gap: 24px; }
.page-top { display: flex; flex-direction: column; gap: 12px; }
.page-title { font-size: 28px; font-weight: 800; color: var(--plum); margin: 0; }

/* Buttons */
.btn { display: inline-flex; align-items: center; gap: 6px; font-family: 'Urbanist'; font-weight: 600; border: none; cursor: pointer; transition: all 0.18s; outline: none; text-decoration: none; }
.btn-primary { background: var(--plum); color: white; padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-primary:hover:not(:disabled) { background: #4a3550; transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-ghost { background: transparent; color: var(--plum); border: 1.5px solid var(--lavender); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-ghost:hover:not(:disabled) { background: var(--lavender-soft); }
.btn-ghost:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-sm { padding: 6px 14px !important; font-size: 13px !important; border-radius: 8px !important; }

/* Cards */
.card { background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(53,43,56,0.07); padding: 24px; }
.input { font-family: 'Urbanist'; font-size: 14px; color: var(--plum); background: white; border: 1.5px solid var(--lavender); border-radius: 10px; padding: 10px 14px; outline: none; transition: all 0.15s; width: 100%; }
.input:focus { border-color: var(--lavender-deep); box-shadow: 0 0 0 3px rgba(155,148,232,0.15); }
.badge { font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 99px; display: inline-flex; align-items: center; }
.badge-lavender { background: var(--lavender); color: var(--plum); }

/* Layout */
.editor-layout { display: grid; grid-template-columns: 1fr 280px; gap: 24px; align-items: start; }
@media (max-width: 900px) { .editor-layout { grid-template-columns: 1fr; } }

/* Editor Card */
.editor-card { display: flex; flex-direction: column; gap: 20px; padding: 32px; }

/* Mood */
.mood-section { display: flex; flex-direction: column; gap: 12px; }
.mood-label { font-size: 13px; font-weight: 600; color: var(--slate); text-transform: uppercase; letter-spacing: 0.05em; }
.mood-row { display: flex; gap: 10px; }
.mood-btn { width: 48px; height: 48px; border-radius: 50%; border: 2px solid transparent; background: var(--lavender-soft); font-size: 22px; cursor: pointer; transition: all 0.15s; display: flex; align-items: center; justify-content: center; }
.mood-btn:hover { border-color: var(--lavender-deep); background: var(--lavender); }
.mood-btn.selected { background: var(--lavender); border-color: var(--lavender-deep); transform: scale(1.1); }

.divider { height: 1px; background: var(--lavender-soft); }

/* Title */
.title-input { font-family: 'Urbanist'; font-size: 20px; font-weight: 700; color: var(--plum); border: none; border-bottom: 2px solid var(--lavender); outline: none; padding: 8px 0; width: 100%; background: transparent; transition: border-color 0.15s; }
.title-input:focus { border-bottom-color: var(--lavender-deep); }
.title-input::placeholder { color: var(--lavender-mid); font-weight: 500; }

/* Toolbar */
.editor-topbar {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; flex-wrap: wrap;
}
.md-toolbar {
  display: flex; align-items: center; gap: 2px;
  background: var(--lavender-soft); border-radius: 10px; padding: 4px 8px;
  flex-wrap: wrap;
}
.tb-btn {
  width: 30px; height: 28px; border-radius: 7px;
  background: transparent; border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: var(--slate); transition: all 0.13s;
}
.tb-btn:hover { background: white; color: var(--plum); box-shadow: 0 1px 4px rgba(53,43,56,0.1); }
.tb-divider { width: 1px; height: 18px; background: var(--lavender); margin: 0 4px; }
.md-hint { font-size: 10px; font-weight: 600; color: var(--slate); opacity: 0.7; white-space: nowrap; margin-left: 2px; }

/* Write/Preview toggle */
.view-toggle {
  display: flex; gap: 2px;
  background: var(--lavender-soft); border-radius: 8px; padding: 3px;
  flex-shrink: 0;
}
.view-btn {
  font-family: 'Urbanist'; font-size: 12px; font-weight: 600;
  display: flex; align-items: center; gap: 4px;
  padding: 5px 12px; border-radius: 6px; border: none; cursor: pointer;
  color: var(--slate); background: transparent; transition: all 0.15s;
}
.view-btn.active { background: white; color: var(--plum); box-shadow: 0 1px 4px rgba(53,43,56,0.1); }

/* Textarea */
.content-textarea {
  font-family: 'Urbanist'; font-size: 15px; line-height: 1.8; color: var(--plum);
  border: none; border-bottom: 1.5px solid var(--lavender-soft);
  outline: none; padding: 8px 0; width: 100%; min-height: 320px;
  background: transparent; resize: none; transition: border-color 0.15s;
}
.content-textarea:focus { border-bottom-color: var(--lavender-deep); }
.content-textarea::placeholder { color: var(--lavender-mid); }

/* MD Preview */
.md-preview {
  min-height: 320px; padding: 8px 0;
  border-bottom: 1.5px solid var(--lavender-soft);
  font-size: 15px; line-height: 1.8; color: var(--plum);
  overflow-y: auto;
}
.md-preview :deep(h1) { font-size: 22px; font-weight: 800; margin: 0 0 12px; color: var(--plum); }
.md-preview :deep(h2) { font-size: 18px; font-weight: 700; margin: 20px 0 10px; color: var(--plum); }
.md-preview :deep(h3) { font-size: 15px; font-weight: 700; margin: 16px 0 8px; color: var(--plum); }
.md-preview :deep(p) { margin: 0 0 14px; }
.md-preview :deep(p:last-child) { margin-bottom: 0; }
.md-preview :deep(strong) { font-weight: 700; color: var(--plum); }
.md-preview :deep(em) { font-style: italic; }
.md-preview :deep(ul), .md-preview :deep(ol) { padding-left: 22px; margin: 0 0 14px; }
.md-preview :deep(li) { margin-bottom: 4px; }
.md-preview :deep(blockquote) { border-left: 3px solid var(--lavender-deep); padding: 4px 14px; margin: 12px 0; color: var(--slate); font-style: italic; background: var(--lavender-soft); border-radius: 0 8px 8px 0; }
.md-preview :deep(code) { font-family: 'Courier New', monospace; font-size: 13px; background: var(--lavender-soft); color: var(--plum); padding: 2px 6px; border-radius: 4px; }
.md-preview :deep(pre) { background: #2d2b3a; border-radius: 10px; padding: 16px; overflow-x: auto; margin: 12px 0; }
.md-preview :deep(pre code) { background: none; color: #e2e0ff; padding: 0; font-size: 13px; }
.md-preview :deep(hr) { border: none; border-top: 1px solid var(--lavender); margin: 20px 0; }
.md-preview :deep(.preview-empty) { color: var(--lavender-mid); font-style: italic; }

/* Prompts */
.prompts-section { display: flex; flex-direction: column; gap: 12px; }
.prompts-toggle { justify-content: flex-start; }
.toggle-arrow { margin-left: 4px; }
.prompts-list { display: flex; flex-direction: column; gap: 8px; }
.prompt-chip { font-family: 'Urbanist'; font-size: 13px; font-weight: 500; color: var(--plum); background: var(--lavender-soft); border: 1.5px solid var(--lavender); border-radius: 8px; padding: 10px 14px; cursor: pointer; text-align: left; transition: all 0.15s; }
.prompt-chip:hover { background: var(--lavender); border-color: var(--lavender-deep); }

/* Action Bar */
.action-bar { display: flex; gap: 12px; justify-content: flex-end; padding-top: 8px; border-top: 1.5px solid var(--lavender-soft); }

/* Sidebar */
.sidebar { display: flex; flex-direction: column; gap: 16px; }

/* AI Card */
.ai-card { padding: 20px; }
.ai-header { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.ai-icon { color: var(--lavender-deep); }
.ai-label { font-size: 13px; font-weight: 700; color: var(--plum); text-transform: uppercase; letter-spacing: 0.05em; }
.ai-empty p { font-size: 13px; color: var(--slate); margin: 0; font-style: italic; }
.ai-none { font-size: 12px; color: var(--slate); font-style: italic; }
.ai-results { display: flex; flex-direction: column; gap: 10px; }
.detected-bias { display: flex; flex-direction: column; gap: 4px; }
.bias-note { font-size: 11px; color: var(--slate); }

/* Meta Card */
.meta-card { padding: 16px 20px; }
.meta-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; }
.meta-row + .meta-row { border-top: 1px solid var(--lavender-soft); }
.meta-label { font-size: 12px; color: var(--slate); font-weight: 600; }
.meta-value { font-size: 14px; font-weight: 700; color: var(--plum); }

/* Tags Card */
.tags-card { padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.tags-header { font-size: 13px; font-weight: 700; color: var(--plum); text-transform: uppercase; letter-spacing: 0.05em; }
.tags-wrap { display: flex; flex-wrap: wrap; gap: 6px; min-height: 24px; }
.tag-chip { background: var(--lavender); color: var(--plum); font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 99px; display: inline-flex; align-items: center; gap: 4px; }
.tag-remove { border: none; background: none; cursor: pointer; color: var(--plum); line-height: 1; padding: 0; opacity: 0.6; display: inline-flex; align-items: center; }
.tag-remove:hover { opacity: 1; }
.tag-input { font-size: 13px; padding: 8px 12px; }

/* Toast */
.toast { position: fixed; bottom: 32px; right: 32px; background: var(--plum); color: white; font-weight: 600; font-size: 14px; padding: 12px 24px; border-radius: 12px; box-shadow: 0 8px 32px rgba(53,43,56,0.18); z-index: 1000; display: inline-flex; align-items: center; gap: 8px; }
.toast-error { background: #dc2626; }

svg { display: block; }

@media (max-width: 640px) {
  .editor-card { padding: 20px; }
  .editor-topbar { flex-direction: column; align-items: flex-start; gap: 8px; }
  .action-bar { flex-direction: column; }
  .action-bar .btn { justify-content: center; }
}
</style>
