<template>
  <div class="journal-entry-list">
    <header class="journal-entry-list__header">
      <h3>Past Entries</h3>
      <div class="filters">
        <select class="form-select" v-model="localFilters.mood">
          <option value="">All moods</option>
          <option v-for="mood in moods" :key="mood" :value="mood">{{ mood }}</option>
        </select>
        <select class="form-select" v-model="localFilters.tag">
          <option value="">All tags</option>
          <option v-for="tag in tags" :key="tag" :value="tag">{{ tag }}</option>
        </select>
      </div>
    </header>

    <p v-if="filteredEntries.length === 0" class="empty-state">
      No entries match your filters yet.
    </p>

    <article
      v-for="entry in filteredEntries"
      :key="entry.id"
      class="entry-card"
    >
      <header>
        <div>
          <p class="entry-date">{{ entry.date }}</p>
          <h4>{{ entry.title }}</h4>
        </div>
        <span class="entry-mood">{{ entry.mood }}</span>
      </header>
      <p class="entry-preview">{{ entry.content }}</p>
      <footer>
        <div class="entry-tags">
          <span v-for="tag in entry.tags" :key="tag" class="tag-pill">{{ tag }}</span>
        </div>
        <div class="entry-actions">
          <button class="btn btn-ghost btn-sm" type="button" @click="$emit('edit', entry)">Edit</button>
          <button class="btn btn-ghost btn-sm" type="button" @click="$emit('export', entry)">Export</button>
          <button class="btn btn-ghost btn-sm" type="button" @click="$emit('delete', entry)">Delete</button>
        </div>
      </footer>
    </article>
  </div>
</template>

<script setup>
import { computed, reactive } from 'vue'

const props = defineProps({
  entries: {
    type: Array,
    default: () => []
  },
  tags: {
    type: Array,
    default: () => []
  }
})

const localFilters = reactive({ mood: '', tag: '' })

const moods = ['Inspired', 'Calm', 'Neutral', 'Anxious', 'Overwhelmed']

const filteredEntries = computed(() => {
  return props.entries.filter((entry) => {
    const moodMatch = localFilters.mood ? entry.mood === localFilters.mood : true
    const tagMatch = localFilters.tag ? entry.tags.includes(localFilters.tag) : true
    return moodMatch && tagMatch
  })
})
</script>

<style scoped>
.journal-entry-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.journal-entry-list__header {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--spacing-3);
  align-items: center;
}

.filters {
  display: flex;
  gap: var(--spacing-2);
}

.empty-state {
  text-align: center;
  color: var(--mind-gray);
  margin: var(--spacing-8) 0;
}

.entry-card {
  border: 1px solid var(--mind-gray-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-5);
  background-color: white;
  box-shadow: var(--shadow-sm);
}

.entry-card header,
.entry-card footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-4);
}

.entry-date {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--mind-gray);
}

.entry-mood {
  text-transform: uppercase;
  font-size: var(--text-xs);
  letter-spacing: 0.08em;
  color: var(--mind-purple);
}

.entry-preview {
  color: var(--mind-gray-dark);
  margin: var(--spacing-4) 0;
}

.entry-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
}

.entry-actions {
  display: inline-flex;
  gap: var(--spacing-2);
}
</style>
