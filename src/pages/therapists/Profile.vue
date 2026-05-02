<template>
  <div class="therapist-profile-page">

    <!-- Back + Breadcrumb -->
    <div class="page-top">
      <div class="breadcrumb">
        <router-link to="/therapists" class="bc-link">Therapists</router-link>
        <span class="bc-sep">/</span>
        <span class="bc-current">{{ therapist.name }}</span>
      </div>
      <router-link to="/therapists" class="btn btn-ghost btn-sm">← Back</router-link>
    </div>

    <!-- Hero Card -->
    <div class="card hero-card">
      <div class="hero-left">
        <div class="hero-avatar" :style="{ background: therapist.gradient }">{{ therapist.initials }}</div>
        <div class="hero-info">
          <div class="hero-name-row">
            <h1 class="hero-name">{{ therapist.name }}</h1>
            <span class="badge badge-green">✓ Verified</span>
            <span class="badge badge-green">
              <span class="avail-dot-sm"></span> Available
            </span>
          </div>
          <div class="hero-creds">{{ therapist.credentials }}</div>
          <div class="hero-creds">{{ therapist.experience }} years of practice</div>
        </div>
      </div>
      <div class="hero-stats-row">
        <div class="hero-stat">
          <span class="hero-stat-val">⭐ {{ therapist.rating }}</span>
          <span class="hero-stat-label">Rating</span>
        </div>
        <div class="hero-stat">
          <span class="hero-stat-val">{{ therapist.clients }}+</span>
          <span class="hero-stat-label">Clients</span>
        </div>
        <div class="hero-stat">
          <span class="hero-stat-val">{{ therapist.sessions }}+</span>
          <span class="hero-stat-label">Sessions</span>
        </div>
        <div class="hero-stat">
          <span class="hero-stat-val">~{{ therapist.responseTime }}h</span>
          <span class="hero-stat-label">Response Time</span>
        </div>
      </div>
      <div class="hero-actions">
        <button class="btn btn-primary btn-lg">📅 Book a Session</button>
        <button class="btn btn-ghost">💬 Message</button>
      </div>
    </div>

    <!-- 3-col Info Cards -->
    <div class="info-grid">
      <div class="card info-card">
        <div class="info-title">🎓 Education</div>
        <ul class="info-list">
          <li v-for="edu in therapist.education" :key="edu">{{ edu }}</li>
        </ul>
      </div>
      <div class="card info-card">
        <div class="info-title">🧭 Approach</div>
        <ul class="info-list">
          <li v-for="a in therapist.approach" :key="a">{{ a }}</li>
        </ul>
      </div>
      <div class="card info-card">
        <div class="info-title">🌐 Languages</div>
        <ul class="info-list">
          <li v-for="l in therapist.languages" :key="l">{{ l }}</li>
        </ul>
      </div>
    </div>

    <div class="two-col-layout">
      <div class="left-col">

        <!-- About -->
        <div class="card about-card">
          <div class="section-header">
            <span class="section-title">About</span>
          </div>
          <p class="about-text">{{ therapist.bio }}</p>
        </div>

        <!-- Specializations -->
        <div class="card spec-card">
          <div class="section-header">
            <span class="section-title">Specializations</span>
          </div>
          <div class="spec-tags">
            <span v-for="s in therapist.specializations" :key="s" class="badge badge-lavender">{{ s }}</span>
          </div>
        </div>

        <!-- Reviews -->
        <div class="card reviews-card">
          <div class="section-header">
            <span class="section-title">Client Reviews</span>
          </div>
          <div class="reviews-list">
            <div v-for="review in therapist.reviews" :key="review.id" class="review-item">
              <div class="review-top">
                <div class="review-stars">{{ '⭐'.repeat(review.stars) }}</div>
                <span class="review-date">{{ review.date }}</span>
              </div>
              <p class="review-text">{{ review.text }}</p>
              <div class="review-author">— {{ review.author }}</div>
            </div>
          </div>
        </div>

      </div>

      <div class="right-col">

        <!-- Session Info -->
        <div class="card session-card">
          <div class="section-header">
            <span class="section-title">Session Info</span>
          </div>
          <div class="session-rows">
            <div class="session-row">
              <span class="session-label">Price</span>
              <span class="session-val price-val">₹{{ therapist.price }}/session</span>
            </div>
            <div class="session-row">
              <span class="session-label">Duration</span>
              <span class="session-val">50 minutes</span>
            </div>
            <div class="session-row">
              <span class="session-label">Format</span>
              <span class="session-val capitalize">{{ therapist.mode }}</span>
            </div>
            <div class="session-row">
              <span class="session-label">Platform</span>
              <span class="session-val">Google Meet / Zoom</span>
            </div>
          </div>
        </div>

        <!-- Booking CTA -->
        <div class="card booking-card">
          <div class="booking-title">📅 Schedule a Session</div>
          <div class="calendar-placeholder">
            <div class="cal-month">May 2026</div>
            <div class="cal-grid">
              <span v-for="d in calDays" :key="d" class="cal-day" :class="{ available: d.avail, selected: d.selected }">{{ d.day }}</span>
            </div>
          </div>
          <button class="btn btn-primary" style="width: 100%;">Confirm Booking</button>
          <p class="booking-note">You'll receive a confirmation email within 30 minutes</p>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const therapist = ref({
  id: 1,
  name: 'Dr. Priya Sharma',
  initials: 'PS',
  credentials: 'M.Sc. Clinical Psychology, NIMHANS · Registered Therapist',
  experience: 8,
  rating: 4.9,
  clients: 140,
  sessions: 1200,
  responseTime: 2,
  price: 900,
  mode: 'online',
  gradient: 'linear-gradient(135deg, #9b94e8, #dad8f9)',
  bio: 'Dr. Priya Sharma is a licensed clinical psychologist with over 8 years of experience helping individuals identify and overcome cognitive biases that affect their personal and professional lives. She specializes in CBT and has worked extensively with clients dealing with anxiety, decision-making difficulties, and relationship patterns rooted in cognitive distortions.\n\nHer approach is warm, collaborative, and evidence-based. She believes that awareness is the first step toward lasting change.',
  education: ['M.Sc. Clinical Psychology — NIMHANS, Bangalore', 'B.A. Psychology — St. Xavier\'s College, Mumbai', 'Certified CBT Practitioner (Beck Institute)'],
  approach: ['Cognitive Behavioral Therapy (CBT)', 'Acceptance & Commitment Therapy (ACT)', 'Mindfulness-Based Cognitive Therapy', 'Solution-Focused Brief Therapy'],
  languages: ['English', 'Hindi', 'Marathi'],
  specializations: ['CBT', 'Anxiety', 'Decision Patterns', 'Cognitive Biases', 'Self-Esteem', 'Work Stress', 'Perfectionism'],
  reviews: [
    { id: 1, stars: 5, author: 'Anonymous', date: 'April 2026', text: 'Dr. Sharma has been incredibly insightful. She helped me understand how my confirmation bias was affecting my relationship. Highly recommend!' },
    { id: 2, stars: 5, author: 'Anonymous', date: 'March 2026', text: 'I\'ve tried multiple therapists but none as skilled at identifying thinking patterns as Dr. Sharma. The CBT techniques she taught me are practical and effective.' },
    { id: 3, stars: 4, author: 'Anonymous', date: 'February 2026', text: 'Very professional and empathetic. The sessions are well-structured and I always leave with something actionable to practice.' },
  ]
})

const calDays = ref([
  { day: 1, avail: false }, { day: 2, avail: false }, { day: 3, avail: false }, { day: 4, avail: true },
  { day: 5, avail: true }, { day: 6, avail: false }, { day: 7, avail: false }, { day: 8, avail: false },
  { day: 9, avail: true }, { day: 10, avail: true }, { day: 11, avail: true, selected: true }, { day: 12, avail: false },
  { day: 13, avail: false }, { day: 14, avail: false }, { day: 15, avail: false }, { day: 16, avail: true },
  { day: 17, avail: true }, { day: 18, avail: false }, { day: 19, avail: false }, { day: 20, avail: false },
  { day: 21, avail: true }, { day: 22, avail: true }, { day: 23, avail: true }, { day: 24, avail: false },
  { day: 25, avail: false }, { day: 26, avail: false }, { day: 27, avail: true }, { day: 28, avail: true },
])
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

/* Hero Card */
.hero-card { display: flex; flex-direction: column; gap: 24px; }
.hero-left { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.hero-avatar { width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 700; color: white; flex-shrink: 0; text-shadow: 0 1px 4px rgba(0,0,0,0.2); }
.hero-info { flex: 1; display: flex; flex-direction: column; gap: 6px; }
.hero-name-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.hero-name { font-size: 28px; font-weight: 700; color: var(--plum); margin: 0; }
.hero-creds { font-size: 14px; color: var(--slate); }
.hero-stats-row { display: flex; gap: 24px; padding: 16px 0; border-top: 1px solid var(--lavender-soft); border-bottom: 1px solid var(--lavender-soft); flex-wrap: wrap; }
.hero-stat { display: flex; flex-direction: column; gap: 2px; }
.hero-stat-val { font-size: 18px; font-weight: 700; color: var(--plum); }
.hero-stat-label { font-size: 11px; color: var(--slate); font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.hero-actions { display: flex; gap: 12px; flex-wrap: wrap; }

/* Info Grid */
.info-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
@media (max-width: 700px) { .info-grid { grid-template-columns: 1fr; } }
.info-card { display: flex; flex-direction: column; gap: 12px; }
.info-title { font-size: 14px; font-weight: 700; color: var(--plum); }
.info-list { margin: 0; padding: 0 0 0 16px; display: flex; flex-direction: column; gap: 6px; }
.info-list li { font-size: 13px; color: var(--slate); line-height: 1.4; }

/* Two col layout */
.two-col-layout { display: grid; grid-template-columns: 1fr 320px; gap: 24px; align-items: start; }
@media (max-width: 900px) { .two-col-layout { grid-template-columns: 1fr; } }
.left-col, .right-col { display: flex; flex-direction: column; gap: 20px; }

/* Section Header */
.section-header { display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; border-bottom: 1.5px solid var(--lavender-soft); margin-bottom: 16px; }
.section-title { font-size: 16px; font-weight: 700; color: var(--plum); }

/* About */
.about-text { font-size: 14px; color: var(--slate); line-height: 1.7; margin: 0; white-space: pre-line; }

/* Spec Tags */
.spec-tags { display: flex; gap: 8px; flex-wrap: wrap; }

/* Reviews */
.reviews-list { display: flex; flex-direction: column; gap: 20px; }
.review-item { display: flex; flex-direction: column; gap: 6px; }
.review-top { display: flex; align-items: center; justify-content: space-between; }
.review-stars { font-size: 13px; }
.review-date { font-size: 12px; color: var(--slate); }
.review-text { font-size: 13px; color: var(--slate); line-height: 1.6; margin: 0; font-style: italic; }
.review-author { font-size: 12px; color: var(--lavender-deep); font-weight: 600; }

/* Session Info */
.session-rows { display: flex; flex-direction: column; gap: 0; }
.session-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--lavender-soft); }
.session-row:last-child { border-bottom: none; }
.session-label { font-size: 13px; color: var(--slate); font-weight: 500; }
.session-val { font-size: 13px; font-weight: 700; color: var(--plum); }
.price-val { font-size: 16px; color: var(--lavender-deep); }
.capitalize { text-transform: capitalize; }

/* Booking */
.booking-card { display: flex; flex-direction: column; gap: 16px; }
.booking-title { font-size: 15px; font-weight: 700; color: var(--plum); }
.calendar-placeholder { background: var(--lavender-soft); border-radius: 12px; padding: 16px; }
.cal-month { font-size: 13px; font-weight: 700; color: var(--plum); text-align: center; margin-bottom: 12px; }
.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; }
.cal-day { aspect-ratio: 1; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-size: 12px; font-weight: 600; color: var(--slate); background: transparent; }
.cal-day.available { background: white; color: var(--plum); cursor: pointer; }
.cal-day.available:hover { background: var(--lavender); }
.cal-day.selected { background: var(--lavender-deep) !important; color: white !important; }
.booking-note { font-size: 12px; color: var(--slate); text-align: center; margin: 0; font-style: italic; }
</style>
