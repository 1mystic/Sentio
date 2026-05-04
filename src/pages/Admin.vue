<template>
  <div class="admin-root">

    <!-- ══ LOGIN ══ -->
    <div v-if="!authed" class="login-wrap">
      <div class="login-card">
        <div class="login-brand">
          <div class="logo-mark">S</div>
          <span class="logo-text">Sentio Admin</span>
        </div>
        <p class="login-sub">Sign in to access the monitoring dashboard</p>
        <form @submit.prevent="tryLogin" class="login-form">
          <div class="field-group">
            <label class="field-label">Email</label>
            <input v-model="emailInput" type="email" class="field-input" placeholder="admin@example.com" autocomplete="username" />
          </div>
          <div class="field-group">
            <label class="field-label">Password</label>
            <div class="pw-wrap">
              <input v-model="passwordInput" :type="showPassword ? 'text' : 'password'" class="field-input" placeholder="••••••••" autocomplete="current-password" />
              <button type="button" class="pw-toggle" @click="showPassword = !showPassword" tabindex="-1">{{ showPassword ? 'Hide' : 'Show' }}</button>
            </div>
          </div>
          <div v-if="loginError" class="login-error">{{ loginError }}</div>
          <button type="submit" class="btn-signin" :disabled="logging">{{ logging ? 'Signing in…' : 'Sign in →' }}</button>
        </form>
      </div>
    </div>

    <!-- ══ DASHBOARD ══ -->
    <div v-else class="shell">

      <!-- Icon Sidebar -->
      <div class="icon-sidebar">
        <div class="sidebar-logo-mark">S</div>
        <nav class="sidebar-nav">
          <button
            v-for="t in tabs" :key="t.id"
            class="sidebar-btn"
            :class="{ active: activeTab === t.id }"
            @click="activeTab = t.id"
            :title="t.label"
          >
            <span class="sidebar-icon-el">{{ t.icon }}</span>
          </button>
        </nav>
        <div class="sidebar-bottom">
          <button class="sidebar-btn sidebar-btn-ghost" title="Refresh" @click="loadAll" :disabled="loading">↺</button>
          <button class="sidebar-btn sidebar-btn-ghost" title="Sign out" @click="logout">↩</button>
        </div>
      </div>

      <!-- Main Area -->
      <div class="main-area">

        <!-- Topbar -->
        <div class="topbar">
          <div class="topbar-left">
            <div class="topbar-greeting">{{ timeGreeting }}, Admin</div>
            <div class="topbar-sub">{{ tabs.find(t=>t.id===activeTab)?.label }} · Last updated {{ lastRefreshed }}</div>
          </div>
          <div class="topbar-right">
            <div class="search-bar">
              <span class="search-icon">⌕</span>
              <span class="search-placeholder">Search users, biases…</span>
            </div>
            <div class="health-pill" :class="'health-' + healthOverall">
              <span class="health-dot-el">●</span>
              {{ healthOverall === 'ok' ? 'All systems OK' : 'Issues detected' }}
            </div>
          </div>
        </div>

        <!-- Page content -->
        <div class="page-content" v-if="!loading">

          <!-- ── OVERVIEW TAB ── -->
          <div v-if="activeTab === 'overview'" class="tab-pane">

            <!-- Stat Cards Row -->
            <div class="stat-cards-row">
              <!-- Users -->
              <div class="stat-card stat-card-lavender">
                <div class="sc-header">
                  <span class="sc-label">Total Users</span>
                  <div class="sc-icon">👥</div>
                </div>
                <div class="sc-value">{{ stats.users?.total ?? '—' }}</div>
                <div class="sc-change">
                  <span class="sc-badge sc-badge-green">↑ {{ stats.users?.active_last_7d ?? 0 }} active 7d</span>
                  <span class="sc-meta">{{ stats.users?.onboarded ?? 0 }} onboarded</span>
                </div>
                <div class="mini-bars">
                  <div v-for="(h, i) in signupBars" :key="i" class="mini-bar" :style="{ height: h + 'px' }"></div>
                </div>
              </div>

              <!-- Journal Entries -->
              <div class="stat-card stat-card-pink">
                <div class="sc-header">
                  <span class="sc-label">Journal Entries</span>
                  <div class="sc-icon">📓</div>
                </div>
                <div class="sc-value">{{ stats.journal?.total_entries ?? '—' }}</div>
                <div class="sc-change">
                  <span class="sc-badge sc-badge-pink">{{ stats.journal?.entries_last_30d ?? 0 }} last 30d</span>
                  <span class="sc-meta">avg sentiment {{ stats.journal?.avg_sentiment ?? '—' }}</span>
                </div>
                <div class="mini-bars">
                  <div v-for="(h, i) in entryBars" :key="i" class="mini-bar mini-bar-pink" :style="{ height: h + 'px' }"></div>
                </div>
              </div>

              <!-- Bias Detections -->
              <div class="stat-card stat-card-blue">
                <div class="sc-header">
                  <span class="sc-label">Bias Detections</span>
                  <div class="sc-icon">🧠</div>
                </div>
                <div class="sc-value">{{ stats.journal?.total_bias_detections ?? '—' }}</div>
                <div class="sc-change">
                  <span class="sc-badge sc-badge-blue">{{ stats.assessments?.total_submissions ?? 0 }} assessments</span>
                  <span class="sc-meta">{{ stats.knowledge_base?.total_articles ?? 0 }} KB chunks</span>
                </div>
                <div class="mini-bars">
                  <div v-for="(h, i) in detectionBars" :key="i" class="mini-bar mini-bar-blue" :style="{ height: h + 'px' }"></div>
                </div>
              </div>
            </div>

            <!-- Assessment Pipeline Table -->
            <div class="card pipeline-card">
              <div class="card-header-row">
                <h3 class="card-title">Assessment Pipeline</h3>
                <span class="card-meta">{{ assessmentStats.total_submissions ?? 0 }} total submissions across {{ assessmentStats.total_users ?? 0 }} users</span>
              </div>
              <div class="pipeline-table-wrap">
                <table class="pipeline-table">
                  <thead>
                    <tr>
                      <th class="th-label">Assessment</th>
                      <th>Users</th>
                      <th>Submissions</th>
                      <th>Completion Rate</th>
                      <th v-for="col in pipelineCols" :key="col">{{ col }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(a, i) in assessmentStats.assessments" :key="a.id">
                      <td class="td-assess-name">{{ a.title }}</td>
                      <td>
                        <div class="pipeline-cell" :class="rowColors[i % rowColors.length].cell">
                          {{ assessmentStats.total_users ?? '—' }}
                        </div>
                      </td>
                      <td>
                        <div class="pipeline-cell" :class="rowColors[i % rowColors.length].cell">
                          {{ a.total_completions }}
                        </div>
                      </td>
                      <td>
                        <div class="pipeline-cell" :class="rowColors[i % rowColors.length].cell">
                          {{ pct(a.completion_rate) }}
                        </div>
                      </td>
                      <td v-for="(score, key, si) in topScores(a.avg_scores, 3)" :key="key">
                        <div class="pipeline-cell" :class="rowColors[i % rowColors.length].cell">
                          {{ key.split('_').slice(0,2).join(' ') }}: {{ score }}
                        </div>
                      </td>
                      <!-- Empty cells if fewer than 3 scores -->
                      <td v-for="n in Math.max(0, 3 - Object.keys(a.avg_scores || {}).length)" :key="'empty-'+n">
                        <div class="pipeline-cell pipeline-cell-empty"></div>
                      </td>
                    </tr>
                    <tr v-if="!assessmentStats.assessments?.length">
                      <td colspan="7" class="td-empty">No assessment data yet</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

          </div>

          <!-- ── USERS TAB ── -->
          <div v-if="activeTab === 'users'" class="tab-pane">
            <div class="card">
              <div class="card-header-row">
                <h3 class="card-title">Users <span class="count-badge">{{ userList.total }}</span></h3>
                <span class="card-meta">{{ stats.users?.active_last_7d ?? 0 }} active in last 7 days</span>
              </div>
              <div class="table-scroll">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>User</th>
                      <th>Joined</th>
                      <th>Onboarded</th>
                      <th>Entries</th>
                      <th>Assessments</th>
                      <th>Top Bias</th>
                      <th>Archetype</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="u in userList.users" :key="u.id">
                      <td>
                        <div class="user-cell">
                          <div class="user-avatar-sm">{{ (u.name || '?').slice(0,2).toUpperCase() }}</div>
                          <div>
                            <div class="user-name-td">{{ u.name }}</div>
                            <div class="user-email-td">{{ u.email }}</div>
                          </div>
                        </div>
                      </td>
                      <td class="td-dim">{{ u.joined }}</td>
                      <td><span :class="u.onboarded ? 'pill-green' : 'pill-gray'">{{ u.onboarded ? 'Yes' : 'No' }}</span></td>
                      <td class="td-num">{{ u.journal_entries }}</td>
                      <td class="td-num">{{ u.assessments_taken }}</td>
                      <td class="td-bias">{{ u.top_bias ? u.top_bias.replace(/_/g,' ') : '—' }}</td>
                      <td class="td-dim">{{ u.archetype || '—' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ── ML TAB ── -->
          <div v-if="activeTab === 'ml'" class="tab-pane">

            <!-- Classifier metric cards -->
            <div class="metric-cards-row">
              <div v-for="m in classifierCards" :key="m.label" class="metric-mini-card">
                <div class="mmc-val">{{ m.val }}</div>
                <div class="mmc-label">{{ m.label }}</div>
              </div>
            </div>

            <div class="two-col">
              <!-- Confidence distribution -->
              <div class="card">
                <h3 class="card-title" style="margin-bottom:20px">Confidence Distribution</h3>
                <div class="hbar-list">
                  <div v-for="(count, bucket) in mlMetrics.confidence_distribution" :key="bucket" class="hbar-row">
                    <div class="hbar-label">{{ bucket }}</div>
                    <div class="hbar-track"><div class="hbar-fill" :style="{ width: hbarW(count, maxConfCount) + '%' }"></div></div>
                    <div class="hbar-val">{{ count }}</div>
                  </div>
                </div>
              </div>

              <!-- RAG metrics -->
              <div class="card">
                <h3 class="card-title" style="margin-bottom:20px">RAG Knowledge Base</h3>
                <div class="hbar-list">
                  <div v-for="(count, cat) in ragMetrics.knowledge_base?.by_category" :key="cat" class="hbar-row">
                    <div class="hbar-label">{{ cat }}</div>
                    <div class="hbar-track"><div class="hbar-fill hbar-fill-teal" :style="{ width: hbarW(count, maxKbCat) + '%' }"></div></div>
                    <div class="hbar-val">{{ count }}</div>
                  </div>
                </div>
                <div class="rag-meta">
                  <span>Model: <strong>{{ ragMetrics.embedder?.model }}</strong></span>
                  <span>Dims: <strong>{{ ragMetrics.embedder?.dimensions }}</strong></span>
                  <span>Reranker: <strong>{{ ragMetrics.reranker?.provider }}</strong></span>
                </div>
              </div>
            </div>

            <!-- Class distribution -->
            <div class="card">
              <h3 class="card-title" style="margin-bottom:20px">Bias Class Distribution</h3>
              <div class="hbar-list">
                <div v-for="(count, bias) in mlMetrics.class_distribution" :key="bias" class="hbar-row">
                  <div class="hbar-label hbar-label-wide">{{ bias.replace(/_/g,' ') }}</div>
                  <div class="hbar-track"><div class="hbar-fill hbar-fill-plum" :style="{ width: hbarW(count, maxClassCount) + '%' }"></div></div>
                  <div class="hbar-val">{{ count }}</div>
                </div>
              </div>
              <div class="note-pill">
                Detection rate {{ pct(mlMetrics.classifier?.detection_rate) }} ·
                Avg {{ mlMetrics.classifier?.avg_detections_per_entry }} detections/entry ·
                Avg confidence {{ mlMetrics.classifier?.avg_confidence }}
              </div>
            </div>
          </div>

          <!-- ── SERVICES TAB ── -->
          <div v-if="activeTab === 'services'" class="tab-pane">
            <div class="services-grid">
              <div v-for="(svc, name) in serviceHealth.services" :key="name" class="service-card card">
                <div class="svc-card-top">
                  <div class="svc-logo-circle" :class="'svc-bg-' + name">{{ name.slice(0,2).toUpperCase() }}</div>
                  <div>
                    <div class="svc-card-name">{{ name }}</div>
                    <span :class="statusPillClass(svc.status)" class="svc-pill">{{ svc.status }}</span>
                  </div>
                </div>
                <p class="svc-card-detail">{{ svc.detail }}</p>
              </div>
            </div>
            <div class="checked-row">Checked at {{ serviceHealth.checked_at ? new Date(serviceHealth.checked_at).toLocaleTimeString() : '—' }}</div>
          </div>

        </div>

        <!-- Loading state -->
        <div v-else class="loading-center">
          <div class="spinner"></div>
          <p>Loading dashboard…</p>
        </div>
      </div>

      <!-- Right Panel (always visible) -->
      <div class="right-panel">

        <!-- Service Health -->
        <div class="card rp-card">
          <div class="rp-header">
            <span class="rp-title">Service Health</span>
            <span :class="'health-dot-sm health-dot-' + healthOverall">●</span>
          </div>
          <div class="svc-list">
            <div v-for="(svc, name) in serviceHealth.services" :key="name" class="svc-row">
              <div class="svc-mini-logo">{{ name.slice(0,2).toUpperCase() }}</div>
              <div class="svc-row-info">
                <div class="svc-row-name">{{ name }}</div>
                <div class="svc-row-detail">{{ svc.detail?.slice(0, 36) }}{{ svc.detail?.length > 36 ? '…' : '' }}</div>
              </div>
              <span :class="'status-dot status-dot-' + svc.status">●</span>
            </div>
            <div v-if="!Object.keys(serviceHealth.services || {}).length" class="svc-empty">No health data</div>
          </div>
        </div>

        <!-- Recent Users -->
        <div class="card rp-card">
          <div class="rp-header">
            <span class="rp-title">Recent Users</span>
            <span class="rp-count">{{ userList.total }}</span>
          </div>
          <div class="users-list">
            <div v-for="u in (userList.users || []).slice(0, 5)" :key="u.id" class="user-row-rp">
              <div class="user-avatar-rp">{{ (u.name || '?').slice(0,2).toUpperCase() }}</div>
              <div class="user-info-rp">
                <div class="user-name-rp">{{ u.name }}</div>
                <div class="user-email-rp">{{ u.email?.slice(0, 22) }}{{ u.email?.length > 22 ? '…' : '' }}</div>
              </div>
              <span v-if="u.top_bias" class="bias-chip">{{ u.top_bias.replace(/_/g,' ').slice(0,14) }}</span>
            </div>
            <div v-if="!userList.users?.length" class="svc-empty">No users yet</div>
          </div>
        </div>

        <!-- Knowledge Base -->
        <div class="card rp-card">
          <div class="rp-header">
            <span class="rp-title">Knowledge Base</span>
            <span class="rp-count">{{ stats.knowledge_base?.total_articles ?? 0 }}</span>
          </div>
          <div class="hbar-list" style="gap:8px">
            <div v-for="(count, cat) in stats.knowledge_base?.by_category" :key="cat" class="hbar-row hbar-row-sm">
              <div class="hbar-label hbar-label-sm">{{ cat }}</div>
              <div class="hbar-track hbar-track-sm"><div class="hbar-fill hbar-fill-teal" :style="{ width: hbarW(count, maxKbCatStats) + '%' }"></div></div>
              <div class="hbar-val" style="font-size:11px">{{ count }}</div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Auth
const authed     = ref(false)
const emailInput = ref('')
const passwordInput = ref('')
const showPassword  = ref(false)
const adminToken    = ref('')
const loginError    = ref('')
const logging       = ref(false)

// Dashboard
const loading      = ref(false)
const lastRefreshed = ref('—')
const activeTab     = ref('overview')

const tabs = [
  { id: 'overview',  label: 'Overview',       icon: '⌂' },
  { id: 'users',     label: 'Users',           icon: '▦' },
  { id: 'ml',        label: 'ML & Algorithms', icon: '◎' },
  { id: 'services',  label: 'Services',        icon: '⚡' },
]

// Data
const stats          = ref({})
const userList       = ref({ users: [], total: 0 })
const mlMetrics      = ref({ classifier: {}, confidence_distribution: {}, class_distribution: {} })
const ragMetrics     = ref({ knowledge_base: {}, embedder: {}, reranker: {} })
const serviceHealth  = ref({ overall: 'unknown', services: {} })
const assessmentStats = ref({ assessments: [], total_users: 0, total_submissions: 0 })

const rowColors = [
  { cell: 'cell-lavender' },
  { cell: 'cell-pink' },
  { cell: 'cell-blue' },
  { cell: 'cell-green' },
]
const pipelineCols = ['Score 1', 'Score 2', 'Score 3']

// ── Lifecycle ──
onMounted(() => {
  const saved = sessionStorage.getItem('sentio_admin_token')
  if (saved) { adminToken.value = saved; authed.value = true; loadAll() }
})

const timeGreeting = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 18) return 'Good afternoon'
  return 'Good evening'
})

// ── Auth ──
async function tryLogin() {
  loginError.value = ''
  logging.value = true
  try {
    const res = await fetch(`${API_BASE}/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: emailInput.value, password: passwordInput.value }),
    })
    const body = await res.json().catch(() => ({}))
    if (res.status === 401) { loginError.value = 'Incorrect email or password.'; return }
    if (res.status === 503) { loginError.value = 'Admin not configured on server.'; return }
    if (!res.ok)            { loginError.value = 'Server error — is the backend running?'; return }
    adminToken.value = body.token
    sessionStorage.setItem('sentio_admin_token', body.token)
    authed.value = true
    await loadAll()
  } catch {
    loginError.value = 'Cannot reach backend at ' + API_BASE
  } finally {
    logging.value = false
  }
}

function logout() {
  sessionStorage.removeItem('sentio_admin_token')
  authed.value = false
  adminToken.value = ''
  emailInput.value = ''
  passwordInput.value = ''
}

async function apiFetch(path) {
  const res = await fetch(`${API_BASE}${path}`, { headers: { 'X-Admin-Token': adminToken.value } })
  if (res.status === 403) { logout(); return {} }
  if (!res.ok) throw new Error(`${path} → ${res.status}`)
  return res.json()
}

async function loadAll() {
  loading.value = true
  try {
    const [s, u, ml, rag, sh, as] = await Promise.all([
      apiFetch('/admin/stats'),
      apiFetch('/admin/users?limit=100'),
      apiFetch('/admin/ml/metrics'),
      apiFetch('/admin/ml/rag'),
      apiFetch('/admin/services/health'),
      apiFetch('/admin/assessments/stats'),
    ])
    stats.value = s
    userList.value = u
    mlMetrics.value = ml
    ragMetrics.value = rag
    serviceHealth.value = sh
    assessmentStats.value = as
    lastRefreshed.value = new Date().toLocaleTimeString()
  } catch (e) {
    console.error('Admin load error:', e)
  } finally {
    loading.value = false
  }
}

// ── Computed helpers ──
const healthOverall  = computed(() => serviceHealth.value.overall || 'unknown')
const maxConfCount   = computed(() => Math.max(1, ...Object.values(mlMetrics.value.confidence_distribution || {})))
const maxClassCount  = computed(() => Math.max(1, ...Object.values(mlMetrics.value.class_distribution || {})))
const maxKbCat       = computed(() => Math.max(1, ...Object.values(ragMetrics.value.knowledge_base?.by_category || {})))
const maxKbCatStats  = computed(() => Math.max(1, ...Object.values(stats.value.knowledge_base?.by_category || {})))

function pct(val) { return val == null ? '—' : (val * 100).toFixed(1) + '%' }
function hbarW(count, max) { return Math.max(3, Math.round((count / Math.max(max, 1)) * 100)) }
function topScores(obj, n) {
  if (!obj) return {}
  return Object.fromEntries(Object.entries(obj).sort((a, b) => b[1] - a[1]).slice(0, n))
}

// Mini bars from time-series (last 10 data points, normalized to 0-40px)
function makeBars(dayMap, maxH = 40) {
  const vals = Object.values(dayMap || {}).slice(-10)
  if (!vals.length) return Array(10).fill(4)
  const mx = Math.max(...vals, 1)
  return [...Array(10)].map((_, i) => {
    const v = vals[i] ?? 0
    return Math.max(4, Math.round((v / mx) * maxH))
  })
}
const signupBars    = computed(() => makeBars(stats.value.users?.signups_last_30d))
const entryBars     = computed(() => makeBars(stats.value.journal?.entries_by_day))
const detectionBars = computed(() => {
  // Synthetic: use entries_by_day scaled by avg detection rate
  const rate = mlMetrics.value.classifier?.detection_rate || 0.5
  const raw = {}
  for (const [d, v] of Object.entries(stats.value.journal?.entries_by_day || {})) {
    raw[d] = Math.round(v * rate * 2)
  }
  return makeBars(raw)
})

const classifierCards = computed(() => {
  const c = mlMetrics.value.classifier || {}
  return [
    { label: 'Model',             val: c.model?.replace('claude-haiku-','Haiku ') || '—' },
    { label: 'Bias Classes',      val: c.taxonomy_size ?? '—' },
    { label: 'Processed',         val: c.total_entries_processed ?? '—' },
    { label: 'Pending',           val: c.total_entries_pending ?? '—' },
    { label: 'Total Detections',  val: c.total_detections ?? '—' },
    { label: 'Detection Rate',    val: pct(c.detection_rate) },
    { label: 'Avg / Entry',       val: c.avg_detections_per_entry ?? '—' },
    { label: 'Avg Confidence',    val: c.avg_confidence ?? '—' },
  ]
})

function statusPillClass(s) {
  return { 'pill-ok': s === 'ok', 'pill-warn': s === 'degraded' || s === 'not_configured', 'pill-err': s === 'error' || s === 'not_installed' }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.admin-root {
  height: 100vh;
  overflow: hidden;
  font-family: 'Urbanist', sans-serif;
  background: #edeaf4;
  color: #352b38;
}

/* ── Login ── */
.login-wrap {
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh;
  background: linear-gradient(160deg, #f4f3f8 0%, #edeaf4 35%, #e4e1f5 65%, #dbd6f5 100%);
}
.login-card {
  background: white; border-radius: 24px; padding: 40px;
  width: 400px; box-shadow: 0 20px 60px rgba(53,43,56,0.12);
  border: 1px solid rgba(218,216,249,0.5);
  display: flex; flex-direction: column; gap: 20px;
}
.login-brand { display: flex; align-items: center; gap: 12px; }
.logo-mark {
  width: 40px; height: 40px; border-radius: 12px;
  background: linear-gradient(135deg, #dad8f9, #9b94e8);
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; font-weight: 900; color: #352b38;
}
.logo-text { font-size: 20px; font-weight: 800; color: #352b38; letter-spacing: -0.3px; }
.login-sub { font-size: 13.5px; color: #7e808c; line-height: 1.5; }
.login-form { display: flex; flex-direction: column; gap: 14px; }
.field-group { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: 12px; font-weight: 700; color: #7e808c; text-transform: uppercase; letter-spacing: 0.5px; }
.field-input {
  font-family: 'Urbanist', sans-serif; font-size: 14px;
  background: white; border: 1.5px solid #dad8f9; border-radius: 10px;
  padding: 10px 14px; outline: none; width: 100%;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.field-input:focus { border-color: #9b94e8; box-shadow: 0 0 0 3px rgba(155,148,232,0.15); }
.pw-wrap { position: relative; display: flex; align-items: center; }
.pw-wrap .field-input { padding-right: 56px; }
.pw-toggle { position: absolute; right: 12px; background: none; border: none; font-size: 12px; font-weight: 700; color: #9b94e8; cursor: pointer; font-family: 'Urbanist', sans-serif; }
.login-error { font-size: 12px; color: #dc2626; background: #fee2e2; border-radius: 8px; padding: 8px 12px; }
.btn-signin {
  font-family: 'Urbanist', sans-serif; font-size: 15px; font-weight: 700;
  background: #352b38; color: white; border: none; cursor: pointer;
  padding: 13px 28px; border-radius: 12px; transition: all 0.18s;
}
.btn-signin:hover:not(:disabled) { background: #4a3550; transform: translateY(-1px); box-shadow: 0 4px 16px rgba(53,43,56,0.22); }
.btn-signin:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── Shell layout ── */
.shell {
  display: flex; height: 100vh; overflow: hidden;
}

/* ── Icon Sidebar ── */
.icon-sidebar {
  width: 64px; flex-shrink: 0;
  background: #352b38;
  display: flex; flex-direction: column; align-items: center;
  padding: 20px 0;
  position: sticky; top: 0; height: 100vh;
  gap: 4px;
}
.sidebar-logo-mark {
  width: 36px; height: 36px; border-radius: 10px;
  background: linear-gradient(135deg, #dad8f9, #9b94e8);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 900; color: #352b38;
  margin-bottom: 20px; flex-shrink: 0;
}
.sidebar-nav { display: flex; flex-direction: column; gap: 4px; width: 100%; padding: 0 10px; }
.sidebar-btn {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  border: none; cursor: pointer; transition: all 0.18s;
  font-size: 18px; background: transparent; color: rgba(218,216,249,0.5);
  align-self: center;
}
.sidebar-btn:hover { background: rgba(218,216,249,0.12); color: rgba(218,216,249,0.9); }
.sidebar-btn.active { background: rgba(155,148,232,0.25); color: #dad8f9; }
.sidebar-btn-ghost { color: rgba(218,216,249,0.4); font-size: 16px; }
.sidebar-bottom { margin-top: auto; display: flex; flex-direction: column; gap: 4px; padding: 0 10px; }

/* ── Main area ── */
.main-area {
  flex: 1; display: flex; flex-direction: column; min-width: 0;
  background: #edeaf4; overflow: hidden;
}

/* ── Topbar ── */
.topbar {
  position: sticky; top: 0; z-index: 90;
  background: rgba(237,234,244,0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #eceaf9;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 28px; height: 68px; flex-shrink: 0;
}
.topbar-greeting { font-size: 17px; font-weight: 800; color: #352b38; letter-spacing: -0.3px; }
.topbar-sub { font-size: 12px; color: #7e808c; margin-top: 2px; }
.topbar-right { display: flex; align-items: center; gap: 12px; }
.search-bar {
  display: flex; align-items: center; gap: 8px;
  background: white; border: 1.5px solid #dad8f9; border-radius: 12px;
  padding: 8px 16px; font-size: 13px; color: #7e808c; width: 220px;
}
.search-icon { font-size: 16px; }
.health-pill {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; font-weight: 700; padding: 6px 12px; border-radius: 99px;
  border: 1.5px solid;
}
.health-ok   { background: #d1fae5; color: #065f46; border-color: #6ee7b7; }
.health-degraded, .health-unknown { background: #fef9c3; color: #92400e; border-color: #fcd34d; }

/* ── Page Content ── */
.page-content { padding: 24px 28px; display: flex; flex-direction: column; gap: 0; flex: 1; min-height: 0; overflow-y: auto; }

/* Tab pane fills parent height and owns its own gap */
.tab-pane { display: flex; flex-direction: column; gap: 16px; flex: 1; min-height: 0; }

/* ── Stat Cards ── */
.stat-cards-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; flex-shrink: 0; }
.stat-card { border-radius: 16px; padding: 22px 20px 16px; box-shadow: 0 4px 24px rgba(53,43,56,0.07); display: flex; flex-direction: column; gap: 10px; min-height: 190px; }
.stat-card-lavender { background: linear-gradient(135deg, #dad8f9 0%, #eceaf9 100%); }
.stat-card-pink     { background: linear-gradient(135deg, #f9d8f0 0%, #fde8f9 100%); }
.stat-card-blue     { background: linear-gradient(135deg, #d8edf9 0%, #e8f4fd 100%); }
.sc-header { display: flex; align-items: center; justify-content: space-between; }
.sc-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #7e808c; }
.sc-icon { font-size: 20px; }
.sc-value { font-size: 36px; font-weight: 900; color: #352b38; letter-spacing: -1.5px; line-height: 1; }
.sc-change { display: flex; align-items: center; gap: 8px; }
.sc-badge { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 99px; }
.sc-badge-green  { background: rgba(255,255,255,0.7); color: #059669; }
.sc-badge-pink   { background: rgba(255,255,255,0.7); color: #9d174d; }
.sc-badge-blue   { background: rgba(255,255,255,0.7); color: #1d4ed8; }
.sc-meta { font-size: 11px; color: #7e808c; }

/* Mini bars */
.mini-bars { display: flex; align-items: flex-end; gap: 3px; height: 44px; margin-top: 4px; }
.mini-bar { flex: 1; border-radius: 2px 2px 0 0; background: rgba(53,43,56,0.15); min-height: 4px; }
.mini-bar-pink { background: rgba(157,23,77,0.2); }
.mini-bar-blue { background: rgba(29,78,216,0.18); }

/* ── Pipeline Table ── */
.pipeline-card { }
.card {
  background: white; border-radius: 16px;
  padding: 24px; box-shadow: 0 4px 24px rgba(53,43,56,0.07);
}
.card-header-row { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 20px; }
.card-title { font-size: 16px; font-weight: 700; color: #352b38; }
.card-meta  { font-size: 12px; color: #7e808c; }
.count-badge { font-size: 11px; font-weight: 700; background: #eceaf9; color: #352b38; padding: 2px 8px; border-radius: 99px; margin-left: 6px; }

.pipeline-table-wrap { overflow-x: auto; }
.pipeline-table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 13px; }
.pipeline-table th {
  font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
  color: #7e808c; background: #eceaf9; padding: 8px 12px; text-align: left; white-space: nowrap;
}
.pipeline-table th:first-child { border-radius: 8px 0 0 8px; }
.pipeline-table th:last-child  { border-radius: 0 8px 8px 0; }
.pipeline-table td { padding: 8px 6px; border-bottom: 1px solid #f4f3f8; vertical-align: middle; }
.pipeline-table tr:last-child td { border-bottom: none; }
.pipeline-table tr:hover td { background: #fafafd; }
.th-label { text-align: left; }
.td-assess-name { font-weight: 700; color: #352b38; padding-left: 2px !important; white-space: nowrap; }
.td-empty { text-align: center; color: #7e808c; padding: 24px !important; font-size: 13px; }

.pipeline-cell {
  border-radius: 8px; padding: 6px 12px; font-size: 12px; font-weight: 700;
  text-align: center; white-space: nowrap; min-width: 60px;
}
.pipeline-cell-empty { background: transparent; }
.cell-lavender { background: #dad8f9; color: #352b38; }
.cell-pink     { background: #f9d8f0; color: #9d174d; }
.cell-blue     { background: #d8edf9; color: #1e40af; }
.cell-green    { background: #d8f9e8; color: #065f46; }

/* ── Users Table ── */
.table-scroll { overflow-x: auto; }
.data-table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 13px; }
.data-table th {
  font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
  color: #7e808c; background: #eceaf9; padding: 10px 14px; text-align: left; white-space: nowrap;
}
.data-table th:first-child { border-radius: 8px 0 0 8px; }
.data-table th:last-child  { border-radius: 0 8px 8px 0; }
.data-table td { padding: 12px 14px; border-bottom: 1px solid #eceaf9; vertical-align: middle; }
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: #fafafd; }
.user-cell { display: flex; align-items: center; gap: 10px; }
.user-avatar-sm {
  width: 32px; height: 32px; border-radius: 10px; flex-shrink: 0;
  background: linear-gradient(135deg, #dad8f9, #9b94e8);
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; color: #352b38;
}
.user-name-td  { font-size: 13px; font-weight: 600; color: #352b38; }
.user-email-td { font-size: 11px; color: #7e808c; }
.td-dim  { font-size: 12px; color: #7e808c; }
.td-num  { font-weight: 700; text-align: center; }
.td-bias { font-size: 12px; color: #6b5bd6; text-transform: capitalize; }
.pill-green { font-size: 10px; font-weight: 700; background: #d1fae5; color: #065f46; padding: 3px 10px; border-radius: 99px; }
.pill-gray  { font-size: 10px; font-weight: 700; background: #eceaf9; color: #7e808c; padding: 3px 10px; border-radius: 99px; }

/* ── ML Tab ── */
.metric-cards-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.metric-mini-card { background: white; border-radius: 12px; padding: 16px; box-shadow: 0 4px 24px rgba(53,43,56,0.07); text-align: center; }
.mmc-val   { font-size: 20px; font-weight: 800; color: #352b38; word-break: break-all; }
.mmc-label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #7e808c; margin-top: 4px; }

.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.hbar-list { display: flex; flex-direction: column; gap: 12px; }
.hbar-row  { display: flex; align-items: center; gap: 10px; }
.hbar-row-sm { gap: 6px; }
.hbar-label { width: 140px; font-size: 12px; color: #352b38; flex-shrink: 0; text-align: right; text-transform: capitalize; }
.hbar-label-wide { width: 180px; }
.hbar-label-sm { width: 100px; font-size: 11px; }
.hbar-track { flex: 1; height: 10px; background: #eceaf9; border-radius: 99px; overflow: hidden; }
.hbar-track-sm { height: 7px; }
.hbar-fill { height: 100%; background: linear-gradient(90deg, #9b94e8, #b8b4f0); border-radius: 99px; transition: width 0.4s; }
.hbar-fill-plum { background: linear-gradient(90deg, #6b5bd6, #9b94e8); }
.hbar-fill-teal { background: linear-gradient(90deg, #5bc4b7, #81d4cf); }
.hbar-val { width: 36px; font-size: 12px; font-weight: 700; color: #7e808c; text-align: right; }

.rag-meta { display: flex; gap: 16px; margin-top: 16px; padding-top: 14px; border-top: 1px solid #eceaf9; font-size: 12px; color: #7e808c; flex-wrap: wrap; }
.rag-meta strong { color: #352b38; }
.note-pill { font-size: 12px; color: #7e808c; background: #fef9c3; border-radius: 8px; padding: 8px 14px; margin-top: 16px; line-height: 1.5; }

/* ── Services Tab ── */
.services-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.service-card { display: flex; flex-direction: column; gap: 12px; }
.svc-card-top { display: flex; align-items: center; gap: 14px; }
.svc-logo-circle {
  width: 48px; height: 48px; border-radius: 14px; flex-shrink: 0;
  background: #eceaf9; display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 800; color: #352b38;
}
.svc-card-name { font-size: 15px; font-weight: 700; color: #352b38; text-transform: capitalize; margin-bottom: 4px; }
.svc-pill { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 99px; text-transform: uppercase; }
.pill-ok   { background: #d1fae5; color: #065f46; }
.pill-warn { background: #fef9c3; color: #92400e; }
.pill-err  { background: #fee2e2; color: #991b1b; }
.svc-card-detail { font-size: 12px; color: #7e808c; line-height: 1.5; }
.checked-row { font-size: 11px; color: #7e808c; text-align: center; padding-top: 4px; }

/* ── Right Panel ── */
.right-panel {
  width: 260px; flex-shrink: 0;
  background: #edeaf4;
  padding: 28px 20px 28px 0;
  display: flex; flex-direction: column; gap: 14px;
  overflow-y: auto;
}
.rp-card { padding: 18px; }
.rp-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.rp-title { font-size: 13px; font-weight: 700; color: #352b38; }
.rp-count { font-size: 11px; font-weight: 700; background: #eceaf9; color: #352b38; padding: 2px 8px; border-radius: 99px; }

.health-dot-sm { font-size: 14px; }
.health-dot-ok      { color: #059669; }
.health-dot-degraded, .health-dot-unknown { color: #d97706; }

/* Service health list */
.svc-list { display: flex; flex-direction: column; gap: 10px; }
.svc-row  { display: flex; align-items: center; gap: 10px; }
.svc-mini-logo {
  width: 30px; height: 30px; border-radius: 8px; flex-shrink: 0;
  background: #eceaf9; display: flex; align-items: center; justify-content: center;
  font-size: 9px; font-weight: 800; color: #352b38;
}
.svc-row-info { flex: 1; min-width: 0; }
.svc-row-name { font-size: 12px; font-weight: 600; color: #352b38; text-transform: capitalize; }
.svc-row-detail { font-size: 10px; color: #7e808c; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.status-dot { font-size: 12px; flex-shrink: 0; }
.status-dot-ok          { color: #059669; }
.status-dot-degraded,
.status-dot-not_configured { color: #d97706; }
.status-dot-error,
.status-dot-not_installed { color: #dc2626; }
.svc-empty { font-size: 12px; color: #7e808c; text-align: center; padding: 8px 0; }

/* Recent users list */
.users-list { display: flex; flex-direction: column; gap: 12px; }
.user-row-rp { display: flex; align-items: center; gap: 10px; }
.user-avatar-rp {
  width: 32px; height: 32px; border-radius: 10px; flex-shrink: 0;
  background: linear-gradient(135deg, #dad8f9, #9b94e8);
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; color: #352b38;
}
.user-info-rp { flex: 1; min-width: 0; }
.user-name-rp  { font-size: 12px; font-weight: 600; color: #352b38; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-email-rp { font-size: 10px; color: #7e808c; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bias-chip { font-size: 9px; font-weight: 700; background: #dad8f9; color: #352b38; padding: 2px 7px; border-radius: 99px; white-space: nowrap; flex-shrink: 0; text-transform: capitalize; }

/* ── Loading ── */
.loading-center { display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 80px; color: #7e808c; }
.spinner { width: 32px; height: 32px; border: 3px solid #eceaf9; border-top-color: #9b94e8; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Responsive ── */
@media (max-width: 1100px) { .right-panel { display: none; } }
@media (max-width: 800px)  { .stat-cards-row { grid-template-columns: 1fr; } .two-col { grid-template-columns: 1fr; } .metric-cards-row { grid-template-columns: repeat(2, 1fr); } }
</style>
