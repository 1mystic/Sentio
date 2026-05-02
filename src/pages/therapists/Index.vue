<template>
  <div class="therapists-page">

    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Find a Therapist</h1>
        <p class="page-desc">Connect with mental health professionals who understand cognitive behavioral patterns</p>
      </div>
    </div>

    <div class="main-layout">

      <!-- Filter Sidebar -->
      <aside class="filter-sidebar">

        <div class="filter-block">
          <div class="filter-label">Search</div>
          <div class="search-wrap">
            <span class="search-icon">🔍</span>
            <input v-model="search" class="input search-input" placeholder="Search by name..." />
          </div>
        </div>

        <div class="filter-block">
          <div class="filter-label">Specialization</div>
          <div class="checkbox-list">
            <label v-for="spec in specializations" :key="spec" class="checkbox-item">
              <input type="checkbox" v-model="selectedSpecs" :value="spec" />
              <span>{{ spec }}</span>
            </label>
          </div>
        </div>

        <div class="filter-block">
          <div class="filter-label">Mode</div>
          <div class="radio-list">
            <label v-for="m in modes" :key="m" class="radio-item">
              <input type="radio" v-model="selectedMode" :value="m" />
              <span>{{ m }}</span>
            </label>
          </div>
        </div>

        <div class="filter-block">
          <div class="filter-label">Language</div>
          <div class="checkbox-list">
            <label v-for="lang in languages" :key="lang" class="checkbox-item">
              <input type="checkbox" v-model="selectedLangs" :value="lang" />
              <span>{{ lang }}</span>
            </label>
          </div>
        </div>

        <div class="filter-block">
          <div class="filter-label">Availability</div>
          <div class="radio-list">
            <label v-for="av in availabilityOptions" :key="av" class="radio-item">
              <input type="radio" v-model="selectedAvail" :value="av" />
              <span>{{ av }}</span>
            </label>
          </div>
        </div>

        <button class="btn btn-ghost btn-sm clear-btn" @click="clearFilters">Clear Filters</button>

      </aside>

      <!-- Therapist Grid -->
      <div class="therapist-grid-wrap">
        <div class="results-count">Showing {{ filteredTherapists.length }} therapists</div>
        <div class="therapist-grid">
          <div
            v-for="t in filteredTherapists"
            :key="t.id"
            class="therapist-card card"
          >
            <div class="card-top">
              <div class="avatar" :style="avatarStyle(t)">{{ t.initials }}</div>
              <div class="therapist-info">
                <div class="therapist-name-row">
                  <span class="therapist-name">{{ t.name }}</span>
                  <span class="badge badge-green">✓ Verified</span>
                </div>
                <div class="therapist-creds">{{ t.credentials }}</div>
              </div>
            </div>

            <div class="spec-tags">
              <span v-for="spec in t.specializations" :key="spec" class="badge badge-lavender">{{ spec }}</span>
            </div>

            <div class="therapist-stats">
              <span class="stat">⭐ {{ t.rating }}</span>
              <span class="stat">👥 {{ t.clients }}+ clients</span>
              <span class="stat">📅 {{ t.experience }} yrs exp</span>
            </div>

            <div class="avail-row">
              <span class="avail-dot" :class="{ available: t.available }"></span>
              <span class="avail-label" :class="{ available: t.available }">
                {{ t.available ? 'Available this week' : 'Fully booked' }}
              </span>
            </div>

            <div class="price-row">
              <span class="price">₹{{ t.price }}/session</span>
              <span class="mode-badge">{{ t.mode }}</span>
            </div>

            <div class="card-actions">
              <router-link :to="`/therapists/${t.id}`" class="btn btn-ghost btn-sm">View Profile</router-link>
              <router-link :to="`/therapists/${t.id}`" class="btn btn-primary btn-sm">Book Now</router-link>
            </div>
          </div>
        </div>

        <div v-if="filteredTherapists.length === 0" class="empty-state">
          <div class="empty-icon">🔍</div>
          <p>No therapists match your filters. <button class="link-btn" @click="clearFilters">Clear filters</button></p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const search = ref('')
const selectedSpecs = ref([])
const selectedMode = ref('All')
const selectedLangs = ref([])
const selectedAvail = ref('Any time')

const specializations = ['CBT', 'ACT', 'DBT', 'Mindfulness', 'Trauma', 'ADHD']
const modes = ['All', 'Online', 'In-person', 'Both']
const languages = ['English', 'Hindi', 'Telugu', 'Tamil', 'Bengali']
const availabilityOptions = ['Any time', 'This week', 'This month']

const therapists = ref([
  { id: 1, name: 'Dr. Priya Sharma', initials: 'PS', credentials: 'M.Sc. Clinical Psych, NIMHANS', specializations: ['CBT', 'Anxiety', 'Decision Patterns'], rating: 4.9, clients: 140, experience: 8, price: 900, mode: 'online', available: true, gradient: 'linear-gradient(135deg, #9b94e8, #dad8f9)' },
  { id: 2, name: 'Dr. Arjun Mehta', initials: 'AM', credentials: 'Ph.D. Psychology, IIT Bombay', specializations: ['ACT', 'Cognitive Biases', 'Performance'], rating: 4.8, clients: 95, experience: 6, price: 800, mode: 'both', available: true, gradient: 'linear-gradient(135deg, #88c9a0, #d8f9e8)' },
  { id: 3, name: 'Sneha Krishnan', initials: 'SK', credentials: 'M.Phil. Psychotherapy, DU', specializations: ['Mindfulness', 'Stress', 'Relationships'], rating: 4.7, clients: 80, experience: 5, price: 650, mode: 'online', available: false, gradient: 'linear-gradient(135deg, #e8c56a, #fef9c3)' },
  { id: 4, name: 'Dr. Rohan Patel', initials: 'RP', credentials: 'M.D. Psychiatry, AIIMS', specializations: ['DBT', 'Trauma', 'ADHD'], rating: 4.9, clients: 200, experience: 12, price: 1200, mode: 'in-person', available: true, gradient: 'linear-gradient(135deg, #e88fa0, #f9d8f0)' },
  { id: 5, name: 'Anika Bose', initials: 'AB', credentials: 'M.A. Counselling, Christ University', specializations: ['CBT', 'Depression', 'Self-worth'], rating: 4.6, clients: 65, experience: 4, price: 600, mode: 'online', available: true, gradient: 'linear-gradient(135deg, #8ac4e8, #d8edf9)' },
  { id: 6, name: 'Dr. Vivek Nair', initials: 'VN', credentials: 'Ph.D. Behavioural Psych, Pune', specializations: ['Behavioural Therapy', 'OCD', 'Phobias'], rating: 4.8, clients: 110, experience: 9, price: 950, mode: 'both', available: false, gradient: 'linear-gradient(135deg, #a8b4e8, #dad8f9)' },
])

function avatarStyle(t) {
  return { background: t.gradient }
}

function clearFilters() {
  search.value = ''
  selectedSpecs.value = []
  selectedMode.value = 'All'
  selectedLangs.value = []
  selectedAvail.value = 'Any time'
}

const filteredTherapists = computed(() => {
  return therapists.value.filter(t => {
    if (search.value && !t.name.toLowerCase().includes(search.value.toLowerCase())) return false
    if (selectedSpecs.value.length > 0 && !selectedSpecs.value.some(s => t.specializations.includes(s))) return false
    if (selectedMode.value !== 'All' && t.mode !== selectedMode.value.toLowerCase()) return false
    if (selectedAvail.value === 'This week' && !t.available) return false
    return true
  })
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.therapists-page { display: flex; flex-direction: column; gap: 28px; }
.page-header {}
.page-title { font-size: 28px; font-weight: 800; color: var(--plum); margin: 0 0 6px; }
.page-desc { font-size: 14px; color: var(--slate); margin: 0; }

/* Buttons */
.btn { display: inline-flex; align-items: center; gap: 6px; font-family: 'Urbanist'; font-weight: 600; border: none; cursor: pointer; transition: all 0.18s; outline: none; text-decoration: none; }
.btn-primary { background: var(--plum); color: white; padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-primary:hover { background: #4a3550; transform: translateY(-1px); }
.btn-ghost { background: transparent; color: var(--plum); border: 1.5px solid var(--lavender); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-ghost:hover { background: var(--lavender-soft); }
.btn-sm { padding: 6px 14px !important; font-size: 13px !important; border-radius: 8px !important; }
.link-btn { background: none; border: none; color: var(--lavender-deep); font-weight: 600; cursor: pointer; font-size: 14px; text-decoration: underline; }

.card { background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(53,43,56,0.07); padding: 20px; }
.badge { font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 99px; display: inline-flex; align-items: center; }
.badge-lavender { background: var(--lavender); color: var(--plum); }
.badge-green { background: #d1fae5; color: #059669; }
.input { font-family: 'Urbanist'; font-size: 14px; color: var(--plum); background: white; border: 1.5px solid var(--lavender); border-radius: 10px; padding: 10px 14px; outline: none; transition: all 0.15s; width: 100%; }
.input:focus { border-color: var(--lavender-deep); box-shadow: 0 0 0 3px rgba(155,148,232,0.15); }

/* Layout */
.main-layout { display: grid; grid-template-columns: 240px 1fr; gap: 28px; align-items: start; }
@media (max-width: 900px) { .main-layout { grid-template-columns: 1fr; } }

/* Sidebar */
.filter-sidebar { background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(53,43,56,0.07); padding: 24px; display: flex; flex-direction: column; gap: 20px; position: sticky; top: 20px; }
.filter-block { display: flex; flex-direction: column; gap: 10px; }
.filter-label { font-size: 12px; font-weight: 700; color: var(--plum); text-transform: uppercase; letter-spacing: 0.06em; }
.search-wrap { position: relative; }
.search-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); font-size: 13px; pointer-events: none; }
.search-input { padding-left: 32px; font-size: 13px; }
.checkbox-list, .radio-list { display: flex; flex-direction: column; gap: 6px; }
.checkbox-item, .radio-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--plum); cursor: pointer; }
.checkbox-item input, .radio-item input { accent-color: var(--lavender-deep); }
.clear-btn { align-self: flex-start; }

/* Grid */
.therapist-grid-wrap { display: flex; flex-direction: column; gap: 16px; }
.results-count { font-size: 13px; color: var(--slate); font-weight: 500; }
.therapist-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }

/* Therapist Card */
.therapist-card { display: flex; flex-direction: column; gap: 14px; transition: box-shadow 0.18s, transform 0.18s; }
.therapist-card:hover { box-shadow: 0 8px 32px rgba(53,43,56,0.10); transform: translateY(-2px); }

.card-top { display: flex; gap: 14px; align-items: flex-start; }
.avatar { width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 700; color: white; flex-shrink: 0; text-shadow: 0 1px 3px rgba(0,0,0,0.2); }
.therapist-info { flex: 1; min-width: 0; }
.therapist-name-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.therapist-name { font-size: 16px; font-weight: 700; color: var(--plum); }
.therapist-creds { font-size: 12px; color: var(--slate); margin-top: 3px; }

.spec-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.therapist-stats { display: flex; gap: 14px; flex-wrap: wrap; }
.stat { font-size: 12px; color: var(--slate); font-weight: 500; }

.avail-row { display: flex; align-items: center; gap: 7px; }
.avail-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--slate); opacity: 0.4; }
.avail-dot.available { background: #059669; opacity: 1; }
.avail-label { font-size: 12px; color: var(--slate); font-weight: 500; }
.avail-label.available { color: #059669; }

.price-row { display: flex; align-items: center; justify-content: space-between; }
.price { font-size: 15px; font-weight: 700; color: var(--plum); }
.mode-badge { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 99px; background: var(--lavender-soft); color: var(--slate); text-transform: capitalize; }

.card-actions { display: flex; gap: 8px; padding-top: 4px; border-top: 1px solid var(--lavender-soft); }

/* Empty */
.empty-state { text-align: center; padding: 60px 20px; }
.empty-icon { font-size: 36px; margin-bottom: 12px; }
.empty-state p { font-size: 15px; color: var(--slate); }
</style>
