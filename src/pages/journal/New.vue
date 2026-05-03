<template>
  <div class="new-entry-page">

    <!-- Back + Title -->
    <div class="page-top">
      <router-link to="/journal" class="btn btn-ghost btn-sm">← Back to Journal</router-link>
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

        <!-- Content Textarea -->
        <textarea
          v-model="content"
          class="content-textarea"
          placeholder="Write freely... your thoughts, decisions, feelings, conflicts..."
        ></textarea>

        <!-- Writing Prompts -->
        <div class="prompts-section">
          <button class="btn btn-ghost btn-sm prompts-toggle" @click="showPrompts = !showPrompts">
            ✨ Need inspiration? <span class="toggle-arrow">{{ showPrompts ? '▲' : '▼' }}</span>
          </button>
          <div v-if="showPrompts" class="prompts-list">
            <button
              v-for="prompt in prompts"
              :key="prompt"
              class="prompt-chip"
              @click="content += (content ? '\n\n' : '') + prompt"
            >{{ prompt }}</button>
          </div>
        </div>

        <!-- Action Bar -->
        <div class="action-bar">
          <button class="btn btn-ghost" @click="saveEntry(false)" :disabled="saving">
            {{ saving ? 'Saving…' : 'Save Draft' }}
          </button>
          <button class="btn btn-primary" @click="saveEntry(true)" :disabled="saving">
            {{ saving ? 'Publishing…' : 'Publish Entry' }}
          </button>
        </div>

      </div>

      <!-- Right Sidebar -->
      <div class="sidebar">

        <!-- AI Analysis Pane -->
        <div class="card ai-card">
          <div class="ai-header">
            <span class="ai-icon">✨</span>
            <span class="ai-label">Real-time Analysis</span>
          </div>
          <div v-if="!content.trim()" class="ai-empty">
            <p>Start writing to see your patterns...</p>
          </div>
          <div v-else class="ai-results">
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
            <span class="meta-label">Est. read time</span>
            <span class="meta-value">{{ readTime }} min</span>
          </div>
        </div>

        <!-- Tags -->
        <div class="card tags-card">
          <div class="tags-header">Tags</div>
          <div class="tags-wrap">
            <span v-for="tag in tags" :key="tag" class="tag-chip">
              {{ tag }} <button class="tag-remove" @click="removeTag(tag)">×</button>
            </span>
          </div>
          <div class="tag-input-wrap">
            <input
              v-model="tagInput"
              class="input tag-input"
              placeholder="Add a tag..."
              @keydown.enter.prevent="addTag"
            />
          </div>
        </div>

      </div>
    </div>

    <!-- Toast -->
    <div v-if="toastVisible" class="toast">✓ Entry saved!</div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useJournalStore } from '@/stores/journal.js'

const router = useRouter()
const journalStore = useJournalStore()
const title = ref('')
const content = ref('')
const mood = ref('😊')
const moods = ['😊', '😐', '😔', '😤', '😴']
const showPrompts = ref(false)
const saving = ref(false)
const toastVisible = ref(false)
const tagInput = ref('')
const tags = ref([])

const prompts = ref([
  'Describe a decision you made today — what information did you rely on?',
  'Was there a moment when you felt defensive? What triggered it?',
  'Did you change your mind about anything today? What caused it?',
  'What assumptions are you making about an ongoing situation?',
])

const wordCount = computed(() => content.value.trim().split(/\s+/).filter(Boolean).length)
const readTime = computed(() => Math.max(1, Math.ceil(wordCount.value / 200)))

const detectedBiases = computed(() => {
  const text = content.value.toLowerCase()
  const found = []
  if (text.includes('always') || text.includes('knew it') || text.includes('confirmed')) {
    found.push({ name: 'Confirmation Bias', note: 'Seeking confirming evidence' })
  }
  if (text.includes('everyone') || text.includes('no one') || text.includes('always')) {
    found.push({ name: 'Overgeneralization', note: 'Broad sweeping conclusions' })
  }
  if (text.includes('sunk') || text.includes('already spent') || text.includes('wasted')) {
    found.push({ name: 'Sunk Cost Fallacy', note: 'Valuing past investment over future outcome' })
  }
  if (text.includes('definitely') || text.includes('certain') || text.includes('obviously')) {
    found.push({ name: 'Overconfidence', note: 'High certainty without full data' })
  }
  return found
})

function addTag() {
  const t = tagInput.value.trim()
  if (t && !tags.value.includes(t)) tags.value.push(t)
  tagInput.value = ''
}

function removeTag(tag) {
  tags.value = tags.value.filter(t => t !== tag)
}

async function saveEntry(publish) {
  saving.value = true
  const { data, error: err } = await journalStore.createEntry({
    content: content.value,
    prompt_used: title.value || null,
    mood: mood.value,
  })
  saving.value = false
  if (err) {
    // Show error toast (use inline error state)
    console.error('Failed to save:', err)
    toastVisible.value = true
    setTimeout(() => { toastVisible.value = false }, 2500)
  } else {
    router.push('/journal')
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

/* Inputs */
.title-input { font-family: 'Urbanist'; font-size: 20px; font-weight: 700; color: var(--plum); border: none; border-bottom: 2px solid var(--lavender); outline: none; padding: 8px 0; width: 100%; background: transparent; transition: border-color 0.15s; }
.title-input:focus { border-bottom-color: var(--lavender-deep); }
.title-input::placeholder { color: var(--lavender-mid); font-weight: 500; }

.content-textarea { font-family: 'Urbanist'; font-size: 15px; line-height: 1.8; color: var(--plum); border: none; border-bottom: 1.5px solid var(--lavender-soft); outline: none; padding: 8px 0; width: 100%; min-height: 300px; background: transparent; resize: none; transition: border-color 0.15s; }
.content-textarea:focus { border-bottom-color: var(--lavender-deep); }
.content-textarea::placeholder { color: var(--lavender-mid); }

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
.ai-icon { font-size: 16px; }
.ai-label { font-size: 13px; font-weight: 700; color: var(--plum); text-transform: uppercase; letter-spacing: 0.05em; }
.ai-empty p { font-size: 13px; color: var(--slate); margin: 0; font-style: italic; }
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
.tag-remove { border: none; background: none; cursor: pointer; font-size: 14px; color: var(--plum); line-height: 1; padding: 0; opacity: 0.6; }
.tag-remove:hover { opacity: 1; }
.tag-input { font-size: 13px; padding: 8px 12px; }

/* Toast */
.toast { position: fixed; bottom: 32px; right: 32px; background: var(--plum); color: white; font-weight: 600; font-size: 14px; padding: 12px 24px; border-radius: 12px; box-shadow: 0 8px 32px rgba(53,43,56,0.18); z-index: 1000; }
</style>
