<template>
  <section class="journal-editor">
    <header class="journal-editor__header">
      <div>
        <p class="journal-editor__label">Today's Prompt</p>
        <h3>{{ activePrompt.question }}</h3>
      </div>
      <button class="btn btn-outline btn-sm" type="button" @click="cyclePrompt">Try another prompt</button>
    </header>

    <div class="journal-editor__controls">
      <label class="form-label">Entry Date</label>
      <input type="date" class="form-input" v-model="localEntry.date" />
    </div>

    <label class="form-label">How are you feeling?</label>
    <div class="journal-editor__moods">
      <button
        v-for="mood in moods"
        :key="mood.value"
        type="button"
        class="mood-pill"
        :class="{ active: mood.value === localEntry.mood }"
        @click="localEntry.mood = mood.value"
      >
        {{ mood.label }}
      </button>
    </div>

    <label class="form-label">Entry</label>
    <textarea
      class="form-textarea"
      rows="8"
      v-model="localEntry.content"
      placeholder="Let your thoughts flow..."
    />

    <label class="form-label">Tags</label>
    <input
      class="form-input"
      type="text"
      v-model="tagInput"
      @keyup.enter.prevent="addTag"
      placeholder="Press enter to add a tag"
    />
    <div class="journal-editor__tags">
      <span v-for="tag in localEntry.tags" :key="tag" class="tag-pill">
        {{ tag }}
        <button type="button" @click="removeTag(tag)" aria-label="Remove tag">×</button>
      </span>
    </div>

    <div class="journal-editor__actions">
      <button class="btn btn-outline" type="button" @click="$emit('cancel')">Cancel</button>
      <button class="btn btn-primary" type="button" @click="emitSave">Save Entry</button>
    </div>
  </section>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'

const props = defineProps({
  entry: {
    type: Object,
    default: () => ({
      date: new Date().toISOString().slice(0, 10),
      mood: 'neutral',
      content: '',
      tags: []
    })
  },
  prompts: {
    type: Array,
    default: () => ([
      { id: 1, question: 'What is one small win you had today?' },
      { id: 2, question: 'Which emotion showed up most often today?' },
      { id: 3, question: 'What is something you need to let go of?' }
    ])
  }
})

const emit = defineEmits(['save', 'cancel'])

const localEntry = reactive({ ...props.entry })
const promptIndex = ref(0)
const tagInput = ref('')

const moods = [
  { label: 'Inspired', value: 'inspired' },
  { label: 'Calm', value: 'calm' },
  { label: 'Neutral', value: 'neutral' },
  { label: 'Anxious', value: 'anxious' },
  { label: 'Overwhelmed', value: 'overwhelmed' }
]

const activePrompt = computed(() => props.prompts[promptIndex.value])

watch(() => props.entry, (next) => Object.assign(localEntry, next), { deep: true })

const cyclePrompt = () => {
  promptIndex.value = (promptIndex.value + 1) % props.prompts.length
}

const addTag = () => {
  if (!tagInput.value.trim()) return
  if (!localEntry.tags.includes(tagInput.value.trim())) {
    localEntry.tags.push(tagInput.value.trim())
  }
  tagInput.value = ''
}

const removeTag = (tag) => {
  localEntry.tags = localEntry.tags.filter((item) => item !== tag)
}

const emitSave = () => {
  emit('save', { ...localEntry })
}
</script>

<style scoped>
.journal-editor {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.journal-editor__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-4);
}

.journal-editor__label {
  text-transform: uppercase;
  font-size: var(--text-xs);
  color: var(--mind-gray);
  letter-spacing: 0.08em;
  margin-bottom: var(--spacing-1);
}

.journal-editor__moods {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
}

.mood-pill {
  border: 1px solid var(--mind-gray-border);
  border-radius: var(--radius-full);
  padding: var(--spacing-2) var(--spacing-4);
  background-color: white;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.mood-pill.active {
  background-color: var(--mind-purple-light);
  border-color: var(--mind-purple);
  color: var(--mind-purple);
}

.journal-editor__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
}

.tag-pill {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--radius-full);
  background-color: var(--mind-gray-light);
  font-size: var(--text-sm);
}

.tag-pill button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: var(--text-base);
}

.journal-editor__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-3);
}
</style>
