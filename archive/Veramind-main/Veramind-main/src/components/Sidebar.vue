<template>
  <aside class="sidebar" :class="{ 'sidebar-open': isOpen }">
    <div class="sidebar-header">
      <NuxtLink to="/dashboard" class="sidebar-logo">
        <h1>VeraMind</h1>
      </NuxtLink>
    </div>

    <nav class="sidebar-nav">
      <NuxtLink 
        v-for="item in navItems" 
        :key="item.path"
        :to="item.path"
        class="sidebar-item"
        :class="{ 'active': $route.path === item.path }"
      >
        <span class="sidebar-icon">{{ item.icon }}</span>
        <span class="sidebar-label">{{ item.label }}</span>
      </NuxtLink>
    </nav>

    <div class="sidebar-footer">
      <div class="user-profile">
        <div class="user-avatar">{{ userInitials }}</div>
        <div class="user-info">
          <div class="user-name">{{ user?.user_metadata?.full_name || 'User' }}</div>
          <div class="user-email">{{ user?.email }}</div>
        </div>
      </div>
      <NuxtLink to="/crisis" class="crisis-link">
        🆘 Crisis Support
      </NuxtLink>
      <button class="btn btn-ghost btn-sm" @click="handleSignOut">
        Sign Out
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { useMobile } from '../composables/useMobile'

const router = useRouter()
const route = useRoute()
const { user, signOut } = useAuth()
const { isMobile } = useMobile()

const isOpen = ref(false)

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: '📊' },
  { path: '/assessments', label: 'Assessments', icon: '📝' },
  { path: '/journal', label: 'Journal', icon: '📔' },
  { path: '/insights', label: 'Insights', icon: '💡' },
  { path: '/modules', label: 'Modules', icon: '📚' },
  { path: '/community', label: 'Community', icon: '👥' },
  { path: '/resources', label: 'Resources', icon: '📖' },
  { path: '/settings', label: 'Settings', icon: '⚙️' }
]

const userInitials = computed(() => {
  const name = user.value?.user_metadata?.full_name || 'U'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const handleSignOut = async () => {
  await signOut()
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  width: 256px;
  height: 100vh;
  background-color: var(--mind-purple);
  color: white;
  display: flex;
  flex-direction: column;
  z-index: 200;
  transition: transform var(--transition-base);
}

.sidebar-header {
  padding: var(--spacing-6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-logo {
  color: white;
  text-decoration: none;
}

.sidebar-logo h1 {
  color: white;
  font-size: var(--text-2xl);
  margin: 0;
}

.sidebar-nav {
  flex: 1;
  padding: var(--spacing-4);
  overflow-y: auto;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-2);
  transition: all var(--transition-fast);
}

.sidebar-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.sidebar-item.active {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  font-weight: var(--font-semibold);
}

.sidebar-icon {
  font-size: var(--text-xl);
}

.sidebar-label {
  font-size: var(--text-base);
}

.sidebar-footer {
  padding: var(--spacing-4);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  margin-bottom: var(--spacing-3);
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-semibold);
  font-size: var(--text-sm);
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-email {
  font-size: var(--text-xs);
  opacity: 0.8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.crisis-link {
  display: block;
  width: 100%;
  padding: var(--spacing-3);
  margin-bottom: var(--spacing-2);
  background-color: var(--error);
  color: white;
  text-align: center;
  border-radius: var(--radius-md);
  font-weight: var(--font-semibold);
  text-decoration: none;
  transition: background-color var(--transition-fast);
}

.crisis-link:hover {
  background-color: #dc2626;
}

.sidebar-footer .btn {
  width: 100%;
  color: white;
}

.sidebar-footer .btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
  }

  .sidebar.sidebar-open {
    transform: translateX(0);
  }
}
</style>

