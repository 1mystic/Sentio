<template>
  <div class="app-shell">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed }">
      <div class="sidebar-logo">
        <div class="logo-mark">S</div>
        <span class="logo-text">Sentio</span>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section-label">Main</div>
        <router-link
          v-for="item in mainNav"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path.startsWith(item.path) }"
          :title="collapsed ? item.label : ''"
        >
          <component :is="item.icon" :size="18" class="nav-icon" />
          <span class="nav-label">{{ item.label }}</span>
        </router-link>

        <div class="nav-section-label" style="margin-top:16px">Tools</div>
        <router-link
          v-for="item in toolsNav"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path.startsWith(item.path) }"
          :title="collapsed ? item.label : ''"
        >
          <component :is="item.icon" :size="18" class="nav-icon" />
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- Collapse toggle -->
      <button class="collapse-btn" @click="collapsed = !collapsed" :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'">
        <ChevronLeft v-if="!collapsed" :size="15" />
        <ChevronRight v-else :size="15" />
      </button>

      <div class="sidebar-footer">
        <router-link to="/profile" class="nav-item user-row" :title="collapsed ? userName : ''">
          <div class="user-avatar">{{ userInitial }}</div>
          <div class="user-info">
            <div class="user-name">{{ userName }}</div>
            <div class="user-email">{{ userEmail }}</div>
          </div>
        </router-link>
        <button class="signout-btn" @click="handleSignOut" title="Sign out">
          <LogOut :size="15" />
        </button>
      </div>
    </aside>

    <!-- Main content area -->
    <div class="main-area">
      <!-- Topbar -->
      <header class="topbar">
        <!-- Search -->
        <div class="topbar-search" ref="searchWrap">
          <Search :size="16" class="search-icon" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search biases, journal, assessments…"
            class="search-input"
            @focus="showSearch = true"
            @keydown.escape="closeSearch"
          />
          <!-- Search results dropdown -->
          <div v-if="showSearch && searchQuery.length > 1" class="search-dropdown">
            <div v-if="!searchResults.length" class="search-empty">No results for "{{ searchQuery }}"</div>
            <template v-else>
              <div v-for="group in searchResults" :key="group.type" class="search-group">
                <div class="search-group-label">{{ group.label }}</div>
                <div
                  v-for="item in group.items"
                  :key="item.path"
                  class="search-item"
                  @click="navigateTo(item.path)"
                >
                  <component :is="item.icon" :size="14" class="search-item-icon" />
                  <div class="search-item-text">
                    <div class="search-item-title">{{ item.title }}</div>
                    <div class="search-item-sub">{{ item.sub }}</div>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>

        <div class="topbar-right">
          <!-- Notifications bell -->
          <div class="notif-wrap" ref="notifWrap">
            <button class="btn-icon" title="Notifications" @click="toggleNotifications">
              <Bell :size="18" />
              <span v-if="unreadCount > 0" class="notif-badge">{{ unreadCount }}</span>
            </button>
            <!-- Notifications panel -->
            <div v-if="showNotifications" class="notif-panel">
              <div class="notif-panel-header">
                <span class="notif-panel-title">Notifications</span>
                <button v-if="unreadCount > 0" class="notif-mark-all" @click="markAllRead">Mark all read</button>
              </div>
              <div v-if="notifications.length === 0" class="notif-empty">
                You're all caught up! 🎉
              </div>
              <div
                v-for="n in notifications"
                :key="n.id"
                class="notif-item"
                :class="{ unread: !n.read }"
                @click="handleNotifClick(n)"
              >
                <div class="notif-icon-wrap" :class="`notif-icon-${n.type}`">
                  <component :is="notifIcon(n.type)" :size="14" />
                </div>
                <div class="notif-content">
                  <div class="notif-title">{{ n.title }}</div>
                  <div class="notif-desc">{{ n.message }}</div>
                  <div class="notif-time">{{ n.timeAgo }}</div>
                </div>
              </div>
            </div>
          </div>
          <router-link to="/ai-guide" class="btn-icon" title="AI Guide" style="text-decoration:none"><Sparkles :size="18" /></router-link>
        </div>
      </header>

      <!-- Page content -->
      <main class="page-body">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useUserStore } from '@/stores/user.js'
import { useBiasStore } from '@/stores/bias.js'
import { useJournalStore } from '@/stores/journal.js'
import { useAssessmentStore } from '@/stores/assessment.js'
import client from '@/api/client.js'
import {
  LayoutDashboard, Brain, BookOpen, ClipboardList,
  MessageSquare, UserCheck, TrendingUp, GraduationCap,
  Search, Bell, Sparkles, LogOut,
  CheckCircle, Lightbulb, Flame, Info, Users,
  ChevronLeft, ChevronRight
} from 'lucide-vue-next'

const auth = useAuthStore()
const userStore = useUserStore()
const biasStore = useBiasStore()
const journalStore = useJournalStore()
const assessStore = useAssessmentStore()
const router = useRouter()

// ── Sidebar collapse ──────────────────────────────────────
const collapsed = ref(window.innerWidth < 768)

function onResize() {
  if (window.innerWidth < 768) collapsed.value = true
}

onMounted(async () => {
  // Wait for the Supabase session to be resolved before firing any authenticated requests.
  // Without this, onMounted fires before the router's beforeEach guard completes on
  // initial app mount, producing 401s because the token hasn't been attached yet.
  await auth.ensureInitialized()
  if (!auth.user) return  // router will redirect to /login

  if (!userStore.profile) userStore.fetchProfile()
  if (!biasStore.biases.length) biasStore.fetchAll().catch(() => {})
  if (!journalStore.entries.length) journalStore.fetchEntries({ limit: 30 }).catch(() => {})
  if (!assessStore.assessments.length) assessStore.fetchList().catch(() => {})
  await loadNotifications()
  document.addEventListener('click', handleOutsideClick)
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
  window.removeEventListener('resize', onResize)
})

const userName = computed(() => userStore.profile?.display_name || userStore.profile?.full_name || auth.user?.user_metadata?.full_name || auth.user?.email?.split('@')[0] || 'User')
const userEmail = computed(() => auth.user?.email || '')
const userInitial = computed(() => userName.value[0]?.toUpperCase() || 'U')

async function handleSignOut() {
  await auth.signOut()
  router.push('/login')
}

// ── Search ──────────────────────────────────────────────
const searchQuery = ref('')
const showSearch = ref(false)
const searchWrap = ref(null)

const searchResults = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (q.length < 2) return []
  const groups = []

  // Biases
  const biasHits = biasStore.biases
    .filter(b => b.name?.toLowerCase().includes(q) || b.description?.toLowerCase().includes(q))
    .slice(0, 4)
    .map(b => ({ title: b.name, sub: b.category, path: `/explore/${b.slug || b.id}`, icon: Brain }))
  if (biasHits.length) groups.push({ type: 'bias', label: 'Biases', items: biasHits })

  // Assessments
  const assessHits = assessStore.assessments
    .filter(a => a.title?.toLowerCase().includes(q))
    .slice(0, 3)
    .map(a => ({ title: a.title, sub: `${a.estimated_minutes || '?'} min`, path: `/assessments/${a.id}`, icon: ClipboardList }))
  if (assessHits.length) groups.push({ type: 'assessment', label: 'Assessments', items: assessHits })

  // Journal entries
  const journalHits = journalStore.entries
    .filter(e => e.content?.toLowerCase().includes(q))
    .slice(0, 3)
    .map(e => ({
      title: e.prompt_used || e.content?.slice(0, 50) || 'Journal entry',
      sub: new Date(e.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }),
      path: `/journal/${e.id}`,
      icon: BookOpen,
    }))
  if (journalHits.length) groups.push({ type: 'journal', label: 'Journal Entries', items: journalHits })

  return groups
})

function closeSearch() {
  showSearch.value = false
  searchQuery.value = ''
}

function navigateTo(path) {
  closeSearch()
  router.push(path)
}

// ── Notifications ────────────────────────────────────────
const showNotifications = ref(false)
const notifications = ref([])
const notifWrap = ref(null)

const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

function notifIcon(type) {
  if (type === 'assessment') return CheckCircle
  if (type === 'insight')   return Lightbulb
  if (type === 'streak')    return Flame
  return Info
}

function timeAgo(isoDate) {
  const diff = Date.now() - new Date(isoDate).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 60) return `${m || 1}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

async function loadNotifications() {
  try {
    const res = await client.get('/users/me/notifications')
    notifications.value = (res.data || []).map(n => ({ ...n, timeAgo: timeAgo(n.created_at) }))
  } catch {
    // backend may not have this endpoint yet — generate client-side from state
    notifications.value = generateLocalNotifications()
  }
}

function generateLocalNotifications() {
  const out = []
  const now = new Date().toISOString()
  // Check if user has completed any assessments (from store)
  if (assessStore.assessments.length > 0) {
    out.push({ id: 'tip-assess', type: 'assessment', title: 'Assessment Available', message: 'Take your first cognitive bias assessment to unlock your archetype.', read: false, created_at: now })
  }
  // Check journal streak
  if (journalStore.entries.length >= 3) {
    out.push({ id: 'streak-3', type: 'streak', title: 'Great momentum!', message: `You've written ${journalStore.entries.length} journal entries. Keep it going!`, read: false, created_at: now })
  } else if (journalStore.entries.length === 0) {
    out.push({ id: 'tip-journal', type: 'insight', title: 'Start journaling', message: 'Write your first entry to unlock AI-powered bias insights.', read: false, created_at: now })
  }
  return out.map(n => ({ ...n, timeAgo: 'just now' }))
}

function toggleNotifications() {
  showNotifications.value = !showNotifications.value
  if (showNotifications.value) showSearch.value = false
}

function markAllRead() {
  notifications.value = notifications.value.map(n => ({ ...n, read: true }))
  try { client.post('/users/me/notifications/read-all') } catch {}
}

function handleNotifClick(n) {
  n.read = true
  showNotifications.value = false
  if (n.link) router.push(n.link)
}

function handleOutsideClick(e) {
  if (searchWrap.value && !searchWrap.value.contains(e.target)) {
    showSearch.value = false
  }
  if (notifWrap.value && !notifWrap.value.contains(e.target)) {
    showNotifications.value = false
  }
}

const mainNav = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/explore', icon: Brain, label: 'Bias Explorer' },
  { path: '/journal', icon: BookOpen, label: 'Journal' },
  { path: '/assessments', icon: ClipboardList, label: 'Assessments' },
]

const toolsNav = [
  { path: '/ai-guide', icon: MessageSquare, label: 'AI Guide' },
  { path: '/community', icon: Users, label: 'Community' },
  { path: '/learn', icon: GraduationCap, label: 'Learn' },
  { path: '/therapists', icon: UserCheck, label: 'Find Therapist' },
  { path: '/progress', icon: TrendingUp, label: 'Progress' },
]
</script>

<style scoped>
.app-shell { display: flex; height: 100vh; overflow: hidden; }

.sidebar {
  width: 220px; flex-shrink: 0;
  background: white;
  display: flex; flex-direction: column; height: 100vh; overflow-y: auto;
  overflow-x: hidden;
  transition: width 0.22s ease;
}
.sidebar.collapsed { width: 56px; }

/* hide text labels when collapsed */
.sidebar.collapsed .logo-text,
.sidebar.collapsed .nav-label,
.sidebar.collapsed .nav-section-label,
.sidebar.collapsed .user-info,
.sidebar.collapsed .signout-btn { display: none; }

.sidebar.collapsed .sidebar-logo { justify-content: center; padding: 20px 0; }
.sidebar.collapsed .nav-item { justify-content: center; padding: 9px 0; }
.sidebar.collapsed .nav-icon { opacity: 1; }
.sidebar.collapsed .user-row { justify-content: center; }
.sidebar.collapsed .sidebar-footer { justify-content: center; }

.sidebar-logo {
  display: flex; align-items: center; gap: 10px;
  padding: 20px 20px 20px;
  margin-bottom: 12px;
}
.logo-mark {
  width: 34px; height: 34px; border-radius: 10px;
  background: linear-gradient(135deg, #dad8f9, #9b94e8);
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 900; color: var(--plum);
}
.logo-text { font-size: 18px; font-weight: 800; color: var(--plum); letter-spacing: -0.5px; }

.sidebar-nav { flex: 1; padding: 0 8px; }
.nav-section-label {
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.8px; color: var(--slate); padding: 8px 12px 4px;
}
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 12px; border-radius: 10px; font-size: 14px; font-weight: 500;
  color: var(--slate); text-decoration: none; cursor: pointer;
  transition: all 0.15s;
}
.nav-item:hover { background: var(--lavender-soft); color: var(--plum); }
.nav-item.active { background: var(--lavender); color: var(--plum); font-weight: 600; }
.nav-icon { flex-shrink: 0; opacity: 0.75; display: block; }
.nav-item:hover .nav-icon { opacity: 1; }
.nav-item.active .nav-icon { opacity: 1; }
.nav-label { font-size: 14px; }

/* Collapse toggle button */
.collapse-btn {
  display: flex; align-items: center; justify-content: center;
  margin: 4px 8px; padding: 7px; border-radius: 8px;
  background: transparent; border: 1px solid var(--lavender);
  color: var(--slate); cursor: pointer; transition: all 0.15s;
  flex-shrink: 0;
}
.collapse-btn:hover { background: var(--lavender); color: var(--plum); }
.sidebar.collapsed .collapse-btn { margin: 4px auto; width: 36px; }

.sidebar-footer { padding: 12px 8px; display: flex; align-items: center; gap: 4px; }
.user-row { flex: 1; min-width: 0; }
.signout-btn { background: none; border: none; cursor: pointer; color: var(--slate); padding: 8px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: all 0.15s; }
.signout-btn:hover { background: #fee2e2; color: #dc2626; }
.user-avatar {
  width: 32px; height: 32px; border-radius: 99px;
  background: linear-gradient(135deg, var(--lavender), var(--lavender-deep));
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; color: var(--plum); flex-shrink: 0;
}
.user-info { min-width: 0; }
.user-name { font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-email { font-size: 11px; color: var(--slate); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.main-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.topbar {
  position: sticky; top: 0; z-index: 90;
  display: flex; align-items: center; gap: 12px;
  padding: 0 32px; height: 64px;
  background: white;
}
.topbar-search {
  flex: 1; display: flex; align-items: center; gap: 8px;
  background: white; border: 1.5px solid var(--lavender);
  border-radius: 12px; padding: 8px 14px; max-width: 400px;
}
.search-icon { color: var(--slate); flex-shrink: 0; }
.search-input {
  border: none; outline: none;
  font-family: 'Urbanist', sans-serif; font-size: 14px;
  color: var(--plum); background: transparent; width: 100%;
}
.search-input::placeholder { color: var(--slate); }
.topbar-right { display: flex; align-items: center; gap: 8px; margin-left: auto; }

.btn-icon {
  background: transparent; border: none; cursor: pointer;
  color: var(--slate); padding: 6px; border-radius: 8px;
  display: inline-flex; align-items: center; justify-content: center;
  transition: all 0.15s;
}
.btn-icon:hover { background: var(--lavender-soft); color: var(--plum); }

.page-body { flex: 1; overflow-y: auto; 
  border-top-left-radius: 1rem !important;
    background: var(--bg);
  padding: 32px; display: flex; 
  flex-direction: column; gap: 32px; }

/* Search dropdown */
.topbar-search { position: relative; }
.search-dropdown {
  position: absolute; top: calc(100% + 8px); left: 0; right: 0;
  background: white; border: 1.5px solid var(--lavender);
  border-radius: 14px; box-shadow: 0 12px 40px rgba(53,43,56,0.14);
  z-index: 200; max-height: 380px; overflow-y: auto;
  padding: 8px 0;
}
.search-empty { padding: 16px 18px; font-size: 13px; color: var(--slate); text-align: center; }
.search-group { padding: 4px 0; }
.search-group-label {
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.7px; color: var(--slate);
  padding: 8px 18px 4px;
}
.search-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 18px; cursor: pointer; transition: background 0.12s;
}
.search-item:hover { background: var(--lavender-soft); }
.search-item-icon { color: var(--lavender-deep); flex-shrink: 0; }
.search-item-text { min-width: 0; }
.search-item-title { font-size: 14px; font-weight: 600; color: var(--plum); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.search-item-sub { font-size: 11px; color: var(--slate); text-transform: capitalize; }

/* Notifications */
.notif-wrap { position: relative; }
.notif-badge {
  position: absolute; top: 2px; right: 2px;
  width: 16px; height: 16px; border-radius: 50%;
  background: #e88fa0; color: white;
  font-size: 9px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  border: 2px solid var(--bg, #edeaf4);
}
.notif-panel {
  position: absolute; top: calc(100% + 10px); right: 0;
  width: 320px; background: white;
  border: 1.5px solid var(--lavender);
  border-radius: 16px; box-shadow: 0 12px 40px rgba(53,43,56,0.14);
  z-index: 200; overflow: hidden;
}
.notif-panel-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px; border-bottom: 1px solid var(--lavender-soft);
}
.notif-panel-title { font-size: 14px; font-weight: 700; color: var(--plum); }
.notif-mark-all { font-size: 12px; color: var(--lavender-deep); font-weight: 600; background: none; border: none; cursor: pointer; padding: 0; }
.notif-mark-all:hover { text-decoration: underline; }
.notif-empty { padding: 28px 18px; text-align: center; font-size: 13px; color: var(--slate); }
.notif-item {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 14px 18px; cursor: pointer; transition: background 0.12s;
  border-bottom: 1px solid var(--lavender-soft);
}
.notif-item:last-child { border-bottom: none; }
.notif-item:hover { background: var(--lavender-soft); }
.notif-item.unread { background: var(--lavender-soft); }
.notif-icon-wrap {
  width: 32px; height: 32px; border-radius: 99px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.notif-icon-assessment { background: #d1fae5; color: #059669; }
.notif-icon-insight    { background: var(--lavender); color: var(--lavender-deep); }
.notif-icon-streak     { background: #fee2e2; color: #e88fa0; }
.notif-icon-info       { background: var(--lavender-soft); color: var(--slate); }
.notif-content { flex: 1; min-width: 0; }
.notif-title { font-size: 13px; font-weight: 700; color: var(--plum); margin-bottom: 2px; }
.notif-desc { font-size: 12px; color: var(--slate); line-height: 1.5; }
.notif-time { font-size: 11px; color: var(--slate); margin-top: 4px; opacity: 0.7; }

svg { display: block; }
</style>
