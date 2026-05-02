<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const allInterests = [
  { id: 'decision', label: '🧠 Decision Making' },
  { id: 'communication', label: '💬 Communication' },
  { id: 'career', label: '💼 Work & Career' },
  { id: 'relationships', label: '❤️ Relationships' },
  { id: 'finance', label: '💰 Money & Finance' },
  { id: 'learning', label: '🎓 Learning' },
  { id: 'health', label: '🏋️ Health' },
  { id: 'social', label: '🌍 Social Justice' },
  { id: 'science', label: '🔬 Science' },
  { id: 'politics', label: '🗳️ Politics' },
  { id: 'creativity', label: '🎨 Creativity' },
  { id: 'leadership', label: '📈 Leadership' }
]

const selected = ref([])

const isSelected = (id) => selected.value.includes(id)
const meetsMinimum = computed(() => selected.value.length >= 2)

function toggle(id) {
  const idx = selected.value.indexOf(id)
  if (idx === -1) {
    selected.value.push(id)
  } else {
    selected.value.splice(idx, 1)
  }
}

function handleContinue() {
  if (!meetsMinimum.value) return
  // Persist to sessionStorage so Complete.vue can read it
  sessionStorage.setItem('sentio_interests', JSON.stringify(selected.value))
  router.push('/onboarding/complete')
}

function goBack() {
  router.push('/onboarding/baseline')
}
</script>

<template>
  <div class="interests-wrap fade-up">
    <!-- Header -->
    <div class="step-header">
      <span class="badge badge-lavender">Step 3 of 4</span>
      <h2 class="title">What are you here to explore?</h2>
      <p class="description">
        Select all topics that interest you — we'll tailor your bias learning path.
      </p>
    </div>

    <!-- Interest grid -->
    <div class="interest-grid">
      <button
        v-for="item in allInterests"
        :key="item.id"
        type="button"
        class="interest-pill"
        :class="{ selected: isSelected(item.id) }"
        @click="toggle(item.id)"
      >
        {{ item.label }}
      </button>
    </div>

    <!-- Minimum hint -->
    <transition name="hint-fade">
      <p v-if="selected.length > 0 && !meetsMinimum" class="hint-text">
        Select at least 2 topics to continue
      </p>
    </transition>
    <p v-if="selected.length === 0" class="hint-text neutral">
      Choose topics that resonate with you
    </p>

    <!-- Selection count -->
    <div v-if="selected.length >= 2" class="selection-count">
      <span class="badge badge-lavender">{{ selected.length }} selected</span>
    </div>

    <!-- Actions -->
    <div class="actions">
      <button type="button" class="btn btn-ghost" @click="goBack">
        ← Back
      </button>
      <button
        type="button"
        class="btn btn-primary btn-lg"
        :disabled="!meetsMinimum"
        @click="handleContinue"
      >
        Continue →
      </button>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

.interests-wrap {
  font-family: 'Urbanist', sans-serif;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.step-header { display: flex; flex-direction: column; gap: 8px; }
.title { font-size: 24px; font-weight: 700; color: var(--plum); line-height: 1.25; margin: 0; }
.description { font-size: 14px; color: var(--slate); line-height: 1.6; margin: 0; }

/* Interest grid */
.interest-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
@media (max-width: 520px) {
  .interest-grid { grid-template-columns: repeat(2, 1fr); }
}

.interest-pill {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1.5px solid var(--lavender);
  background: white;
  font-family: 'Urbanist', sans-serif;
  font-size: 13px;
  font-weight: 500;
  color: var(--plum);
  cursor: pointer;
  transition: all 0.18s;
  text-align: center;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.interest-pill:hover {
  border-color: var(--lavender-mid);
  background: var(--lavender-soft);
}
.interest-pill.selected {
  background: var(--plum);
  border-color: var(--plum);
  color: white;
  font-weight: 600;
  box-shadow: 0 4px 14px rgba(53,43,56,0.18);
}

/* Hints */
.hint-text {
  font-size: 12px;
  color: #dc2626;
  text-align: center;
  font-weight: 500;
}
.hint-text.neutral { color: var(--slate); }
.hint-fade-enter-active, .hint-fade-leave-active { transition: opacity 0.2s; }
.hint-fade-enter-from, .hint-fade-leave-to { opacity: 0; }

.selection-count { text-align: center; }

/* Actions */
.actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 4px;
}
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; }
</style>
