<template>
  <div class="therapist-profile-page">

    <!-- Back + Breadcrumb -->
    <div class="page-top">
      <div class="breadcrumb">
        <router-link to="/therapists" class="bc-link">Therapists</router-link>
        <span class="bc-sep">/</span>
        <span class="bc-current">{{ therapist?.name || '…' }}</span>
      </div>
      <router-link to="/therapists" class="btn btn-ghost btn-sm">← Back</router-link>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="card hero-card skeleton-card">
      <div class="skel skel-avatar"></div>
      <div class="skel-info">
        <div class="skel skel-line skel-w60"></div>
        <div class="skel skel-line skel-w40"></div>
        <div class="skel skel-line skel-w80"></div>
      </div>
    </div>

    <!-- 404 -->
    <div v-else-if="!therapist" class="card not-found-card">
      <p>Therapist not found. <router-link to="/therapists" class="bc-link">Browse all therapists →</router-link></p>
    </div>

    <template v-else>

      <!-- Hero Card -->
      <div class="card hero-card">
        <div class="hero-left">
          <div v-if="therapist.photo_url" class="hero-avatar hero-avatar-img">
            <img :src="therapist.photo_url" :alt="therapist.name" />
          </div>
          <div v-else class="hero-avatar" :style="{ background: gradient }">{{ initials }}</div>
          <div class="hero-info">
            <div class="hero-name-row">
              <h1 class="hero-name">{{ therapist.name }}</h1>
              <span v-if="therapist.pronouns" class="pronouns-badge">{{ therapist.pronouns }}</span>
              <span class="badge badge-green">✓ Verified</span>
              <span v-if="therapist.accepting_clients !== false" class="badge badge-green">
                <span class="avail-dot-sm"></span> Accepting clients
              </span>
            </div>
            <div v-if="norm.credentials" class="hero-creds">{{ norm.credentials }}</div>
            <div v-if="norm.experience" class="hero-creds">{{ norm.experience }}</div>
            <div v-if="therapist.city" class="hero-creds city-line">📍 {{ therapist.city }}</div>
          </div>
        </div>

        <div class="hero-stats-row">
          <div v-if="norm.fee" class="hero-stat">
            <span class="hero-stat-val">₹{{ norm.fee }}</span>
            <span class="hero-stat-label">Per session</span>
          </div>
          <div v-if="therapist.session_duration" class="hero-stat">
            <span class="hero-stat-val">{{ therapist.session_duration }}</span>
            <span class="hero-stat-label">Duration</span>
          </div>
          <div v-if="norm.sessionFormat" class="hero-stat">
            <span class="hero-stat-val capitalize">{{ norm.sessionFormat }}</span>
            <span class="hero-stat-label">Format</span>
          </div>
          <div v-if="therapist.languages?.length" class="hero-stat">
            <span class="hero-stat-val">{{ therapist.languages.slice(0, 2).join(', ') }}</span>
            <span class="hero-stat-label">Languages</span>
          </div>
        </div>

        <div class="hero-actions">
          <a
            v-if="therapist.source_url"
            :href="therapist.source_url"
            target="_blank"
            rel="noopener noreferrer"
            class="btn btn-primary btn-lg"
          >
            Connect via {{ sourceLabel }} ↗
          </a>
          <a
            v-if="therapist.source_url"
            :href="therapist.source_url"
            target="_blank"
            rel="noopener noreferrer"
            class="btn btn-ghost"
          >
            View full profile ↗
          </a>
        </div>

        <p v-if="therapist.source" class="source-attr">
          Profile sourced from
          <a :href="therapist.source_url" target="_blank" rel="noopener noreferrer">{{ sourceLabel }}</a>
        </p>
      </div>

      <!-- Info cards: Qualifications, Specializations, Languages -->
      <div class="info-grid">
        <div v-if="therapist.qualifications?.length" class="card info-card">
          <div class="info-title">🎓 Qualifications</div>
          <ul class="info-list">
            <li v-for="q in therapist.qualifications" :key="q">{{ q }}</li>
          </ul>
        </div>
        <div v-if="therapist.specializations?.length" class="card info-card">
          <div class="info-title">🧭 Specializations</div>
          <div class="spec-tags-inline">
            <span v-for="s in therapist.specializations" :key="s" class="badge badge-lavender">{{ s }}</span>
          </div>
        </div>
        <div v-if="therapist.languages?.length" class="card info-card">
          <div class="info-title">🌐 Languages</div>
          <ul class="info-list">
            <li v-for="l in therapist.languages" :key="l">{{ l }}</li>
          </ul>
        </div>
      </div>

      <div class="two-col-layout">
        <div class="left-col">

          <!-- Bio -->
          <div v-if="therapist.bio" class="card about-card">
            <div class="section-header">
              <span class="section-title">About</span>
            </div>
            <p class="about-text">{{ therapist.bio }}</p>
          </div>

        </div>

        <div class="right-col">

          <!-- Session Info -->
          <div class="card session-card">
            <div class="section-header">
              <span class="section-title">Session Info</span>
            </div>
            <div class="session-rows">
              <div v-if="norm.fee" class="session-row">
                <span class="session-label">Fee</span>
                <span class="session-val price-val">₹{{ norm.fee }}/session</span>
              </div>
              <div v-if="therapist.session_duration" class="session-row">
                <span class="session-label">Duration</span>
                <span class="session-val">{{ therapist.session_duration }}</span>
              </div>
              <div v-if="norm.sessionFormat" class="session-row">
                <span class="session-label">Format</span>
                <span class="session-val capitalize">{{ norm.sessionFormat }}</span>
              </div>
              <div v-if="therapist.city" class="session-row">
                <span class="session-label">Location</span>
                <span class="session-val">{{ therapist.city }}</span>
              </div>
            </div>
          </div>

          <!-- Connect CTA -->
          <div class="card booking-card">
            <template v-if="therapist.source_url">
              <div class="booking-title">Ready to connect?</div>
              <p class="booking-desc">
                Booking is handled directly through {{ sourceLabel }}.
                Click below to view availability and reach out to {{ firstName }}.
              </p>
              <a
                :href="therapist.source_url"
                target="_blank"
                rel="noopener noreferrer"
                class="btn btn-primary"
                style="width: 100%; justify-content: center;"
              >
                Connect via {{ sourceLabel }} ↗
              </a>
              <p class="booking-note">Opens {{ sourceLabel }} in a new tab</p>
            </template>
            <template v-else>
              <div class="booking-title">Find a therapist</div>
              <p class="booking-desc">
                Browse verified therapists on TheMindClan or Practo to book a session directly.
              </p>
              <a
                href="https://themindclan.com/professionals/"
                target="_blank"
                rel="noopener noreferrer"
                class="btn btn-primary"
                style="width: 100%; justify-content: center;"
              >
                Browse TheMindClan ↗
              </a>
              <a
                href="https://www.practo.com/search/doctors?results_type=doctor&q=psychologist&city=Bangalore"
                target="_blank"
                rel="noopener noreferrer"
                class="btn btn-ghost"
                style="width: 100%; justify-content: center; margin-top: 8px;"
              >
                Browse Practo ↗
              </a>
            </template>
          </div>

        </div>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTherapistStore } from '@/stores/therapist.js'

const route = useRoute()
const therapistStore = useTherapistStore()

const loading = ref(true)
const therapist = ref(null)

const AVATAR_GRADIENTS = [
  'linear-gradient(135deg, #9b94e8, #dad8f9)',
  'linear-gradient(135deg, #88c9a0, #d8f9e8)',
  'linear-gradient(135deg, #e8c56a, #fef9c3)',
  'linear-gradient(135deg, #e88fa0, #f9d8f0)',
  'linear-gradient(135deg, #8ac4e8, #d8edf9)',
]

// Normalise raw DB row — handles both old-format and new TheMindClan fields
const norm = computed(() => {
  const t = therapist.value
  if (!t) return null

  const quals = t.qualifications?.length ? t.qualifications : (t.credentials || [])
  const credentials = Array.isArray(quals) ? quals.join(' · ') : (quals || '')

  const sessionFormat = t.session_format || t.session_formats?.[0] || ''

  const fee = t.fee ?? t.price_range?.min ?? t.price_range?.amount ?? null

  const experience = t.experience || (t.experience_years ? `${t.experience_years} years` : '')

  return { credentials, sessionFormat, fee, experience }
})

const gradient = computed(() => {
  if (!therapist.value) return AVATAR_GRADIENTS[0]
  const code = therapist.value.name?.charCodeAt(0) ?? 0
  return AVATAR_GRADIENTS[code % AVATAR_GRADIENTS.length]
})

const initials = computed(() => {
  if (!therapist.value?.name) return '?'
  return therapist.value.name
    .trim()
    .split(' ')
    .map(w => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
})

const sourceLabel = computed(() => {
  const src = therapist.value?.source || ''
  if (src === 'themindclan') return 'TheMindClan'
  if (src === 'practo') return 'Practo'
  return 'profile'
})

const firstName = computed(() => {
  return therapist.value?.name?.split(' ').at(-1) || 'this therapist'
})

onMounted(async () => {
  const data = await therapistStore.fetchOne(route.params.id)
  therapist.value = data
  loading.value = false
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.therapist-profile-page { display: flex; flex-direction: column; gap: 24px; }

/* Breadcrumb */
.page-top { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
.breadcrumb { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.bc-link { color: var(--lavender-deep); font-weight: 600; text-decoration: none; }
.bc-link:hover { text-decoration: underline; }
.bc-sep { color: var(--slate); }
.bc-current { color: var(--slate); }

/* Buttons */
.btn { display: inline-flex; align-items: center; gap: 6px; font-family: 'Urbanist'; font-weight: 600; border: none; cursor: pointer; transition: all 0.18s; outline: none; text-decoration: none; }
.btn-primary { background: var(--plum); color: white; padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-primary:hover { background: #4a3550; transform: translateY(-1px); }
.btn-ghost { background: transparent; color: var(--plum); border: 1.5px solid var(--lavender); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-ghost:hover { background: var(--lavender-soft); }
.btn-sm { padding: 6px 14px !important; font-size: 13px !important; border-radius: 8px !important; }
.btn-lg { padding: 13px 28px !important; font-size: 16px !important; border-radius: 12px !important; }

.card { background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(53,43,56,0.07); padding: 24px; }
.badge { font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 99px; display: inline-flex; align-items: center; gap: 5px; }
.badge-lavender { background: var(--lavender); color: var(--plum); }
.badge-green { background: #d1fae5; color: #059669; }
.avail-dot-sm { width: 6px; height: 6px; border-radius: 50%; background: #059669; }

/* Skeleton */
.skeleton-card { display: flex; gap: 20px; align-items: flex-start; }
.skel { background: var(--lavender); border-radius: 8px; animation: sk-pulse 1.4s ease-in-out infinite; }
.skel-avatar { width: 80px; height: 80px; border-radius: 50%; flex-shrink: 0; }
.skel-info { flex: 1; display: flex; flex-direction: column; gap: 10px; }
.skel-line { height: 16px; }
.skel-w60 { width: 60%; }
.skel-w40 { width: 40%; }
.skel-w80 { width: 80%; }
@keyframes sk-pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 0.3; } }

/* Not found */
.not-found-card { text-align: center; padding: 48px; font-size: 15px; color: var(--slate); }

/* Hero Card */
.hero-card { display: flex; flex-direction: column; gap: 24px; }
.hero-left { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.hero-avatar {
  width: 80px; height: 80px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 24px; font-weight: 700; color: white; flex-shrink: 0;
  text-shadow: 0 1px 4px rgba(0,0,0,0.2);
}
.hero-avatar-img { padding: 0; overflow: hidden; }
.hero-avatar-img img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
.hero-info { flex: 1; display: flex; flex-direction: column; gap: 6px; }
.hero-name-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.hero-name { font-size: 26px; font-weight: 700; color: var(--plum); margin: 0; }
.pronouns-badge { font-size: 12px; color: var(--slate); font-weight: 500; padding: 2px 8px; border-radius: 99px; border: 1px solid var(--lavender); }
.hero-creds { font-size: 14px; color: var(--slate); }
.city-line { color: var(--lavender-deep); font-weight: 500; }
.hero-stats-row { display: flex; gap: 24px; padding: 16px 0; border-top: 1px solid var(--lavender-soft); border-bottom: 1px solid var(--lavender-soft); flex-wrap: wrap; }
.hero-stat { display: flex; flex-direction: column; gap: 2px; }
.hero-stat-val { font-size: 17px; font-weight: 700; color: var(--plum); }
.hero-stat-label { font-size: 11px; color: var(--slate); font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.hero-actions { display: flex; gap: 12px; flex-wrap: wrap; }
.source-attr { font-size: 11px; color: var(--slate); margin: 0; }
.source-attr a { color: var(--lavender-deep); text-decoration: underline; }

/* Info Grid */
.info-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
@media (max-width: 700px) { .info-grid { grid-template-columns: 1fr; } }
.info-card { display: flex; flex-direction: column; gap: 12px; }
.info-title { font-size: 14px; font-weight: 700; color: var(--plum); }
.info-list { margin: 0; padding: 0 0 0 16px; display: flex; flex-direction: column; gap: 6px; }
.info-list li { font-size: 13px; color: var(--slate); line-height: 1.4; }
.spec-tags-inline { display: flex; flex-wrap: wrap; gap: 6px; }

/* Two col layout */
.two-col-layout { display: grid; grid-template-columns: 1fr 320px; gap: 24px; align-items: start; }
@media (max-width: 900px) { .two-col-layout { grid-template-columns: 1fr; } }
.left-col, .right-col { display: flex; flex-direction: column; gap: 20px; }

/* Section Header */
.section-header { display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; border-bottom: 1.5px solid var(--lavender-soft); margin-bottom: 16px; }
.section-title { font-size: 16px; font-weight: 700; color: var(--plum); }

/* About */
.about-text { font-size: 14px; color: var(--slate); line-height: 1.7; margin: 0; white-space: pre-line; }

/* Session Info */
.session-rows { display: flex; flex-direction: column; }
.session-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--lavender-soft); }
.session-row:last-child { border-bottom: none; }
.session-label { font-size: 13px; color: var(--slate); font-weight: 500; }
.session-val { font-size: 13px; font-weight: 700; color: var(--plum); }
.price-val { font-size: 16px; color: var(--lavender-deep); }
.capitalize { text-transform: capitalize; }

/* Connect / Booking */
.booking-card { display: flex; flex-direction: column; gap: 14px; }
.booking-title { font-size: 15px; font-weight: 700; color: var(--plum); }
.booking-desc { font-size: 13px; color: var(--slate); line-height: 1.6; margin: 0; }
.booking-note { font-size: 12px; color: var(--slate); text-align: center; margin: 0; font-style: italic; }
</style>
