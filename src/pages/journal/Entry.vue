<template>
  <div class="entry-page">

    <!-- Breadcrumb + Back -->
    <div class="page-top">
      <div class="breadcrumb">
        <router-link to="/journal" class="bc-link">Journal</router-link>
        <span class="bc-sep">/</span>
        <span class="bc-current">{{ entry.date }}</span>
      </div>
      <router-link to="/journal" class="btn btn-ghost btn-sm">← Back</router-link>
    </div>

    <div class="entry-layout">

      <!-- Main Column -->
      <div class="main-col">

        <!-- Entry Header Card -->
        <div class="card header-card">
          <div class="header-meta">
            <span class="entry-date-full">{{ entry.date }}</span>
            <span class="entry-dot">·</span>
            <span class="entry-time">{{ entry.time }}</span>
          </div>
          <div class="entry-mood-large">{{ entry.mood }}</div>
          <h1 class="entry-title">{{ entry.title }}</h1>
        </div>

        <!-- Entry Content Card -->
        <div class="card content-card">
          <div class="entry-content" v-html="highlightedContent"></div>
        </div>

        <!-- Action Bar -->
        <div class="action-bar">
          <button class="btn btn-ghost">✏️ Edit</button>
          <button class="btn btn-danger btn-sm">🗑 Delete</button>
        </div>

      </div>

      <!-- Sidebar: AI Analysis -->
      <div class="sidebar">
        <div class="card ai-card">
          <div class="ai-header">
            <span>✨</span>
            <span class="ai-title">Sentio Analysis</span>
          </div>

          <div class="bias-list">
            <div v-for="bias in entry.biases" :key="bias.name" class="bias-row">
              <div class="bias-row-top">
                <span class="badge badge-lavender">{{ bias.name }}</span>
                <span class="bias-score">{{ bias.score }}/10</span>
              </div>
              <p class="bias-note">{{ bias.note }}</p>
              <router-link :to="`/explore/${bias.name.toLowerCase().replace(/\s+/g, '-')}`" class="btn btn-secondary btn-sm explore-btn">
                Explore {{ bias.name.split(' ')[0] }} →
              </router-link>
            </div>
          </div>

          <div class="divider"></div>

          <div class="insight-section">
            <div class="insight-label">💡 Overall Insight</div>
            <p class="insight-text">{{ entry.insight }}</p>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const entry = ref({
  id: 1,
  date: 'April 30, 2026',
  time: '9:41 AM',
  mood: '😊',
  title: 'Productive morning session',
  content: `Had a great planning session this morning. I kept dismissing Sarah's timeline concerns without really considering them.\n\nI was so confident my estimate was right that I wasn't even processing her data points. Looking back, I had already decided the timeline was fine before the meeting even started.\n\nMaybe I need to actively seek out dissenting views before I lock in on a position. It's uncomfortable but I notice I do this a lot — I find the evidence that matches what I already think.`,
  biases: [
    { name: 'Confirmation Bias', score: 8.2, note: 'Strong pattern — dismissing contradictory information' },
    { name: 'Overconfidence', score: 6.8, note: 'Expressed high certainty before gathering all data' },
  ],
  insight: 'This entry shows a classic confirmation bias pattern combined with overconfidence. You had a pre-formed conclusion and selectively processed information that confirmed it. The fact that you recognized this in reflection is a great sign — try to catch it in the moment next time.'
})

const highlightedContent = computed(() => {
  let text = entry.value.content
  // Replace newlines with paragraph breaks
  text = text.split('\n\n').map(p => `<p>${p}</p>`).join('')
  // Highlight bias-related phrases
  const highlights = [
    { phrase: "dismissing Sarah's timeline concerns", label: 'Confirmation Bias' },
    { phrase: 'so confident my estimate was right', label: 'Overconfidence' },
    { phrase: "already decided the timeline was fine", label: 'Confirmation Bias' },
    { phrase: 'find the evidence that matches what I already think', label: 'Confirmation Bias' },
  ]
  highlights.forEach(h => {
    text = text.replace(h.phrase, `<mark class="bias-mark" title="${h.label}">${h.phrase}</mark>`)
  })
  return text
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.entry-page { display: flex; flex-direction: column; gap: 24px; }

/* Breadcrumb */
.page-top { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
.breadcrumb { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.bc-link { color: var(--lavender-deep); font-weight: 600; text-decoration: none; }
.bc-link:hover { text-decoration: underline; }
.bc-sep { color: var(--slate); }
.bc-current { color: var(--slate); }

/* Buttons */
.btn { display: inline-flex; align-items: center; gap: 6px; font-family: 'Urbanist'; font-weight: 600; border: none; cursor: pointer; transition: all 0.18s; outline: none; text-decoration: none; }
.btn-ghost { background: transparent; color: var(--plum); border: 1.5px solid var(--lavender); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-ghost:hover { background: var(--lavender-soft); }
.btn-secondary { background: var(--lavender); color: var(--plum); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-secondary:hover { background: var(--lavender-mid); }
.btn-sm { padding: 6px 14px !important; font-size: 13px !important; border-radius: 8px !important; }
.btn-danger { background: #fee2e2; color: #dc2626; border: none; padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-danger:hover { background: #fecaca; }

/* Cards */
.card { background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(53,43,56,0.07); padding: 28px; }
.badge { font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 99px; display: inline-flex; align-items: center; }
.badge-lavender { background: var(--lavender); color: var(--plum); }

/* Layout */
.entry-layout { display: grid; grid-template-columns: 1fr 300px; gap: 24px; align-items: start; }
@media (max-width: 900px) { .entry-layout { grid-template-columns: 1fr; } }

.main-col { display: flex; flex-direction: column; gap: 20px; }

/* Header Card */
.header-card { background: linear-gradient(135deg, var(--lavender-soft), white); }
.header-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.entry-date-full { font-size: 13px; font-weight: 600; color: var(--slate); }
.entry-dot { color: var(--slate); }
.entry-time { font-size: 13px; color: var(--slate); }
.entry-mood-large { font-size: 32px; margin-bottom: 8px; }
.entry-title { font-size: 24px; font-weight: 700; color: var(--plum); margin: 0; }

/* Content */
.content-card { padding: 32px; }
.entry-content { font-size: 15px; line-height: 1.8; color: var(--plum); }
.entry-content :deep(p) { margin: 0 0 16px; }
.entry-content :deep(p:last-child) { margin-bottom: 0; }
.entry-content :deep(.bias-mark) { background: var(--lavender); color: var(--plum); padding: 2px 4px; border-radius: 4px; font-style: normal; cursor: help; border-bottom: 2px solid var(--lavender-deep); }

/* Action Bar */
.action-bar { display: flex; gap: 12px; align-items: center; }

/* Sidebar */
.sidebar {}
.ai-card { display: flex; flex-direction: column; gap: 20px; }
.ai-header { display: flex; align-items: center; gap: 8px; }
.ai-title { font-size: 15px; font-weight: 700; color: var(--plum); }

.bias-list { display: flex; flex-direction: column; gap: 16px; }
.bias-row { display: flex; flex-direction: column; gap: 6px; }
.bias-row-top { display: flex; align-items: center; justify-content: space-between; }
.bias-score { font-size: 12px; font-weight: 700; color: var(--lavender-deep); }
.bias-note { font-size: 12px; color: var(--slate); margin: 0; line-height: 1.4; }
.explore-btn { align-self: flex-start; }

.divider { height: 1px; background: var(--lavender-soft); }

.insight-section { display: flex; flex-direction: column; gap: 8px; }
.insight-label { font-size: 13px; font-weight: 700; color: var(--plum); }
.insight-text { font-size: 13px; color: var(--slate); line-height: 1.6; margin: 0; }
</style>
