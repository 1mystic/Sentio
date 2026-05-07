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

      <!-- Desktop Filter Sidebar -->
      <aside class="filter-sidebar">
        <div class="filter-block">
          <div class="filter-label">Search</div>
          <div class="search-wrap">
            <Search :size="14" class="search-icon" />
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

        <!-- Mobile filter bar (hidden on desktop) -->
        <div class="mobile-filter-bar">
          <!-- Search row -->
          <div class="mobile-search-row">
            <Search :size="14" class="ms-icon" />
            <input v-model="search" class="mobile-search-input" placeholder="Search therapists..." />
          </div>

          <!-- Chip row -->
          <div class="chip-row">

            <!-- Specialization -->
            <div class="chip-wrap">
              <button
                class="chip"
                :class="{ active: selectedSpecs.length > 0 }"
                @click.stop="toggleDropdown('spec')"
              >
                {{ selectedSpecs.length ? `Spec (${selectedSpecs.length})` : 'Specialization' }}
                <ChevronDown :size="12" class="chip-arrow" :class="{ rotated: activeDropdown === 'spec' }" />
              </button>
              <div v-if="activeDropdown === 'spec'" class="chip-panel" @click.stop>
                <label v-for="spec in specializations" :key="spec" class="panel-opt">
                  <input type="checkbox" v-model="selectedSpecs" :value="spec" />
                  <span>{{ spec }}</span>
                </label>
              </div>
            </div>

            <!-- Mode -->
            <div class="chip-wrap">
              <button
                class="chip"
                :class="{ active: selectedMode !== 'All' }"
                @click.stop="toggleDropdown('mode')"
              >
                {{ selectedMode !== 'All' ? selectedMode : 'Mode' }}
                <ChevronDown :size="12" class="chip-arrow" :class="{ rotated: activeDropdown === 'mode' }" />
              </button>
              <div v-if="activeDropdown === 'mode'" class="chip-panel" @click.stop>
                <label v-for="m in modes" :key="m" class="panel-opt">
                  <input type="radio" v-model="selectedMode" :value="m" />
                  <span>{{ m }}</span>
                </label>
              </div>
            </div>

            <!-- Language -->
            <div class="chip-wrap">
              <button
                class="chip"
                :class="{ active: selectedLangs.length > 0 }"
                @click.stop="toggleDropdown('lang')"
              >
                {{ selectedLangs.length ? `Lang (${selectedLangs.length})` : 'Language' }}
                <ChevronDown :size="12" class="chip-arrow" :class="{ rotated: activeDropdown === 'lang' }" />
              </button>
              <div v-if="activeDropdown === 'lang'" class="chip-panel" @click.stop>
                <label v-for="lang in languages" :key="lang" class="panel-opt">
                  <input type="checkbox" v-model="selectedLangs" :value="lang" />
                  <span>{{ lang }}</span>
                </label>
              </div>
            </div>

            <!-- Availability -->
            <div class="chip-wrap">
              <button
                class="chip"
                :class="{ active: selectedAvail !== 'Any time' }"
                @click.stop="toggleDropdown('avail')"
              >
                {{ selectedAvail !== 'Any time' ? 'Accepting' : 'Availability' }}
                <ChevronDown :size="12" class="chip-arrow" :class="{ rotated: activeDropdown === 'avail' }" />
              </button>
              <div v-if="activeDropdown === 'avail'" class="chip-panel" @click.stop>
                <label v-for="av in availabilityOptions" :key="av" class="panel-opt">
                  <input type="radio" v-model="selectedAvail" :value="av" />
                  <span>{{ av }}</span>
                </label>
              </div>
            </div>

            <!-- Clear pill -->
            <button v-if="activeFilterCount > 0" class="chip chip-clear" @click="clearFilters">
              Clear all
            </button>

          </div>
        </div>

        <div class="results-count">Showing {{ filteredTherapists.length }} therapists</div>

        <div v-if="therapistStore.loading" class="therapist-grid">
          <div v-for="n in 4" :key="n" class="therapist-card card" style="pointer-events:none;">
            <div style="display:flex;gap:14px;align-items:flex-start;">
              <div style="width:56px;height:56px;border-radius:50%;background:var(--lavender);animation:sk-pulse 1.4s ease-in-out infinite;flex-shrink:0;"></div>
              <div style="flex:1;display:flex;flex-direction:column;gap:8px;">
                <div style="height:16px;width:60%;background:var(--lavender);border-radius:6px;animation:sk-pulse 1.4s ease-in-out infinite;"></div>
                <div style="height:12px;width:80%;background:var(--lavender);border-radius:6px;animation:sk-pulse 1.4s ease-in-out infinite;"></div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="therapist-grid">
          <div v-for="t in filteredTherapists" :key="t.id" class="therapist-card card">
            <div class="card-top">
              <div class="avatar" :style="avatarStyle(t)">{{ t.initials }}</div>
              <div class="therapist-info">
                <div class="therapist-name-row">
                  <span class="therapist-name">{{ t.name }}</span>
                  <span class="badge badge-green"><CheckCircle :size="11" style="margin-right:3px;" /> Verified</span>
                </div>
                <div class="therapist-creds">{{ t.credentials }}</div>
              </div>
            </div>
            <div class="spec-tags">
              <span v-for="spec in t.specializations" :key="spec" class="badge badge-lavender">{{ spec }}</span>
            </div>
            <div class="therapist-stats">
              <span v-if="t.city" class="stat"><MapPin :size="12" /> {{ t.city }}</span>
              <span v-if="t.experience" class="stat"><Calendar :size="12" /> {{ t.experience }}</span>
            </div>
            <div class="avail-row">
              <span class="avail-dot" :class="{ available: t.available }"></span>
              <span class="avail-label" :class="{ available: t.available }">
                {{ t.available ? 'Accepting clients' : 'Not accepting' }}
              </span>
            </div>
            <div class="price-row">
              <span class="price">{{ t.price ? '₹' + t.price + '/session' : 'Fee on request' }}</span>
              <span class="mode-badge">{{ t.mode }}</span>
            </div>
            <div class="card-actions">
              <router-link :to="`/therapists/${t.id}`" class="btn btn-ghost btn-sm">View Profile</router-link>
              <a v-if="t.source_url" :href="t.source_url" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm">Connect ↗</a>
              <router-link v-else :to="`/therapists/${t.id}`" class="btn btn-primary btn-sm">Book Now</router-link>
            </div>
          </div>
        </div>

        <div v-if="!therapistStore.loading && filteredTherapists.length === 0" class="empty-state">
          <div class="empty-icon"><Search :size="36" /></div>
          <p>No therapists match your filters. <button class="link-btn" @click="clearFilters">Clear filters</button></p>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useTherapistStore } from '@/stores/therapist.js'
import { MapPin, Calendar, CheckCircle, Search, ChevronDown } from 'lucide-vue-next'

const therapistStore = useTherapistStore()

const search = ref('')
const selectedSpecs = ref([])
const selectedMode = ref('All')
const selectedLangs = ref([])
const selectedAvail = ref('Any time')
const activeDropdown = ref(null)

const activeFilterCount = computed(() => {
  let n = 0
  if (search.value) n++
  if (selectedSpecs.value.length) n++
  if (selectedMode.value !== 'All') n++
  if (selectedLangs.value.length) n++
  if (selectedAvail.value !== 'Any time') n++
  return n
})

function toggleDropdown(key) {
  activeDropdown.value = activeDropdown.value === key ? null : key
}

function closeDropdowns() {
  activeDropdown.value = null
}

const specializations = ['CBT', 'ACT', 'DBT', 'Mindfulness', 'Trauma', 'ADHD', 'Anxiety', 'Depression', 'OCD', 'Relationships']
const modes = ['All', 'Online', 'In-person', 'Both']
const languages = ['English', 'Hindi', 'Telugu', 'Tamil', 'Bengali', 'Kannada', 'Malayalam', 'Marathi', 'Punjabi']
const availabilityOptions = ['Any time', 'Accepting clients']

const AVATAR_GRADIENTS = [
  'linear-gradient(135deg, #9b94e8, #dad8f9)',
  'linear-gradient(135deg, #88c9a0, #d8f9e8)',
  'linear-gradient(135deg, #e8c56a, #fef9c3)',
  'linear-gradient(135deg, #e88fa0, #f9d8f0)',
  'linear-gradient(135deg, #8ac4e8, #d8edf9)',
  'linear-gradient(135deg, #a8b4e8, #dad8f9)',
]

const FALLBACK_THERAPISTS = [
  { id: 'f1', name: 'Dr. Priya Sharma', qualifications: ['M.Sc. Clinical Psych, NIMHANS'], specializations: ['CBT', 'Anxiety', 'Decision Patterns'], experience: '8 years', fee: 900, session_format: 'online', accepting_clients: true, city: 'Bangalore' },
  { id: 'f2', name: 'Dr. Arjun Mehta', qualifications: ['Ph.D. Psychology, IIT Bombay'], specializations: ['ACT', 'Cognitive Biases', 'Performance'], experience: '6 years', fee: 800, session_format: 'both', accepting_clients: true, city: 'Mumbai' },
  { id: 'f3', name: 'Sneha Krishnan', qualifications: ['M.Phil. Psychotherapy, DU'], specializations: ['Mindfulness', 'Stress', 'Relationships'], experience: '5 years', fee: 650, session_format: 'online', accepting_clients: false, city: 'Delhi' },
  { id: 'f4', name: 'Dr. Rohan Patel', qualifications: ['M.D. Psychiatry, AIIMS'], specializations: ['DBT', 'Trauma', 'ADHD'], experience: '12 years', fee: 1200, session_format: 'in-person', accepting_clients: true, city: 'Delhi' },
  { id: 'f5', name: 'Anika Bose', qualifications: ['M.A. Counselling, Christ University'], specializations: ['CBT', 'Depression', 'Self-worth'], experience: '4 years', fee: 600, session_format: 'online', accepting_clients: true, city: 'Hyderabad' },
  { id: 'f6', name: 'Dr. Vivek Nair', qualifications: ['Ph.D. Behavioural Psych, Pune'], specializations: ['Behavioural Therapy', 'OCD', 'Phobias'], experience: '9 years', fee: 950, session_format: 'both', accepting_clients: false, city: 'Pune' },
]

onMounted(() => {
  therapistStore.fetchList()
  document.addEventListener('click', closeDropdowns)
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdowns)
})

function normalizeTherapist(t, idx) {
  const nameParts = (t.name || '').trim().split(' ')
  const initials = nameParts.map(w => w[0]).join('').slice(0, 2).toUpperCase() || '?'

  // qualifications (new) or credentials (old ARRAY) → display string
  const quals = t.qualifications?.length ? t.qualifications : (t.credentials || [])
  const credentials = Array.isArray(quals) ? quals.join(' · ') : (quals || '')

  // session_format (new text) or session_formats (old ARRAY)
  const rawMode = t.session_format || (t.session_formats?.[0]) || t.mode || 'online'
  const mode = rawMode.toLowerCase()

  // fee (new int) or price_range (old jsonb) or price (manual)
  const price = t.fee ?? t.price ?? t.price_range?.min ?? t.price_range?.amount ?? null

  // experience: new text field or old integer
  const experience = t.experience || (t.experience_years ? `${t.experience_years} years` : null)

  return {
    ...t,
    initials: t.initials || initials,
    credentials,
    specializations: t.specializations || [],
    experience,
    price,
    mode,
    available: t.available ?? t.accepting_clients ?? true,
    gradient: AVATAR_GRADIENTS[idx % AVATAR_GRADIENTS.length],
  }
}

const therapistSource = computed(() => {
  const raw = therapistStore.therapists.length > 0 ? therapistStore.therapists : FALLBACK_THERAPISTS
  return raw.map(normalizeTherapist)
})

function avatarStyle(t) {
  return { background: t.gradient }
}

function clearFilters() {
  search.value = ''
  selectedSpecs.value = []
  selectedMode.value = 'All'
  selectedLangs.value = []
  selectedAvail.value = 'Any time'
  activeDropdown.value = null
}

const filteredTherapists = computed(() => {
  return therapistSource.value.filter(t => {
    if (search.value && !t.name.toLowerCase().includes(search.value.toLowerCase())) return false
    if (selectedSpecs.value.length > 0 && !selectedSpecs.value.some(s => t.specializations.includes(s))) return false
    if (selectedMode.value !== 'All' && t.mode !== selectedMode.value.toLowerCase()) return false
    if (selectedAvail.value === 'Accepting clients' && !t.available) return false
    return true
  })
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.therapists-page { display: flex; flex-direction: column; gap: 28px; }
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

/* ── Layout ── */
.main-layout { display: grid; grid-template-columns: 240px 1fr; gap: 28px; align-items: start; }

/* ── Desktop Sidebar ── */
.filter-sidebar {
  background: white; border-radius: 16px;
  box-shadow: 0 4px 24px rgba(53,43,56,0.07);
  padding: 24px; display: flex; flex-direction: column; gap: 20px;
  position: sticky; top: 20px;
}
.filter-block { display: flex; flex-direction: column; gap: 10px; }
.filter-label { font-size: 12px; font-weight: 700; color: var(--plum); text-transform: uppercase; letter-spacing: 0.06em; }
.search-wrap { display: flex; align-items: center; gap: 8px; background: white; border: 1.5px solid var(--lavender); border-radius: 10px; padding: 0 12px; }
.search-icon { color: var(--slate); flex-shrink: 0; }
.search-input { padding-left: 0 !important; border: none !important; box-shadow: none !important; background: transparent; }
.checkbox-list, .radio-list { display: flex; flex-direction: column; gap: 6px; }
.checkbox-item, .radio-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--plum); cursor: pointer; }
.checkbox-item input, .radio-item input { accent-color: var(--lavender-deep); }
.clear-btn { align-self: flex-start; }

/* ── Mobile filter bar (hidden on desktop) ── */
.mobile-filter-bar { display: none; }

/* ── Therapist grid ── */
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
.stat { font-size: 12px; color: var(--slate); font-weight: 500; display: inline-flex; align-items: center; gap: 4px; }
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
.empty-icon { color: var(--slate); margin-bottom: 12px; display: flex; justify-content: center; }
.empty-state p { font-size: 15px; color: var(--slate); }
@keyframes sk-pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 0.3; } }

/* ── Responsive ── */
@media (max-width: 900px) {
  .therapists-page { gap: 16px; }
  .page-title { font-size: 22px; }

  /* Switch to single column, sidebar off */
  .main-layout { grid-template-columns: 1fr; }
  .filter-sidebar { display: none; }

  /* Show mobile filter bar */
  .mobile-filter-bar {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  /* Search row */
  .mobile-search-row {
    display: flex;
    align-items: center;
    gap: 8px;
    background: white;
    border: 1.5px solid var(--lavender);
    border-radius: 12px;
    padding: 0 14px;
  }
  .ms-icon { color: var(--slate); flex-shrink: 0; }
  .mobile-search-input {
    flex: 1;
    border: none;
    outline: none;
    padding: 11px 0;
    font-family: 'Urbanist', sans-serif;
    font-size: 14px;
    color: var(--plum);
    background: transparent;
  }
  .mobile-search-input::placeholder { color: var(--slate); opacity: 0.7; }

  /* Chip row */
  .chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  /* Individual chip wrapper — needed for dropdown positioning */
  .chip-wrap { position: relative; }

  /* Chip button */
  .chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 8px 13px;
    border-radius: 99px;
    border: 1.5px solid var(--lavender);
    background: white;
    color: var(--plum);
    font-family: 'Urbanist', sans-serif;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
    white-space: nowrap;
  }
  .chip:hover { background: var(--lavender-soft); }
  .chip.active {
    background: var(--plum);
    color: white;
    border-color: var(--plum);
  }
  .chip-clear {
    background: #fee2e2;
    color: #dc2626;
    border-color: #fecaca;
  }
  .chip-clear:hover { background: #fecaca; }

  .chip-arrow { transition: transform 0.2s ease; flex-shrink: 0; }
  .chip-arrow.rotated { transform: rotate(180deg); }

  /* Dropdown panel */
  .chip-panel {
    position: absolute;
    top: calc(100% + 6px);
    left: 0;
    z-index: 200;
    background: white;
    border: 1.5px solid var(--lavender);
    border-radius: 14px;
    box-shadow: 0 8px 28px rgba(53,43,56,0.14);
    min-width: 170px;
    padding: 6px;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .panel-opt {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    border-radius: 8px;
    font-size: 13px;
    color: var(--plum);
    cursor: pointer;
    transition: background 0.12s;
  }
  .panel-opt:hover { background: var(--lavender-soft); }
  .panel-opt input { accent-color: var(--lavender-deep); flex-shrink: 0; }
}

@media (max-width: 640px) {
  .therapist-grid { grid-template-columns: 1fr; }
}
</style>
