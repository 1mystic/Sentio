<template>
  <div class="app-shell">
    <!-- Sidebar -->
    <aside class="sidebar">
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
          :class="{ active: $route.path === item.path }"
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
          :class="{ active: $route.path === item.path }"
        >
          <component :is="item.icon" :size="18" class="nav-icon" />
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <router-link to="/profile" class="nav-item">
          <div class="user-avatar">{{ userInitial }}</div>
          <div class="user-info">
            <div class="user-name">{{ userName }}</div>
            <div class="user-email">{{ userEmail }}</div>
          </div>
        </router-link>
      </div>
    </aside>

    <!-- Main content area -->
    <div class="main-area">
      <!-- Topbar -->
      <header class="topbar">
        <div class="topbar-search">
          <Search :size="16" class="search-icon" />
          <input type="text" placeholder="Search biases, journal, assessments…" class="search-input" />
        </div>
        <div class="topbar-right">
          <button class="btn-icon" title="Notifications"><Bell :size="18" /></button>
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
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useUserStore } from '@/stores/user.js'
import {
  LayoutDashboard, Brain, BookOpen, ClipboardList,
  MessageSquare, UserCheck, TrendingUp,
  Search, Bell, Sparkles
} from 'lucide-vue-next'

const auth = useAuthStore()
const userStore = useUserStore()

const userName = computed(() => userStore.profile?.display_name || auth.user?.email?.split('@')[0] || 'User')
const userEmail = computed(() => auth.user?.email || '')
const userInitial = computed(() => userName.value[0]?.toUpperCase() || 'U')

const mainNav = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/explore', icon: Brain, label: 'Bias Explorer' },
  { path: '/journal', icon: BookOpen, label: 'Journal' },
  { path: '/assessments', icon: ClipboardList, label: 'Assessments' },
]

const toolsNav = [
  { path: '/ai-guide', icon: MessageSquare, label: 'AI Guide' },
  { path: '/therapists', icon: UserCheck, label: 'Find Therapist' },
  { path: '/progress', icon: TrendingUp, label: 'Progress' },
]
</script>

<style scoped>
.app-shell { display: flex; height: 100vh; overflow: hidden; }

.sidebar {
  width: 220px; flex-shrink: 0;
  background: white; border-right: 1px solid var(--lavender-soft);
  display: flex; flex-direction: column; height: 100vh; overflow-y: auto;
}

.sidebar-logo {
  display: flex; align-items: center; gap: 10px;
  padding: 20px 20px 20px; border-bottom: 1px solid var(--lavender-soft);
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

.sidebar-footer { padding: 12px 8px; border-top: 1px solid var(--lavender-soft); }
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
  background: rgba(244,243,248,0.85); backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--lavender-soft);
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

.page-body { flex: 1; overflow-y: auto; padding: 32px; display: flex; flex-direction: column; gap: 32px; }

svg { display: block; }
</style>
