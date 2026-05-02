<template>
  <nav class="navbar">
    <div class="navbar-content">
      <div class="navbar-left">
        <button 
          v-if="isMobile" 
          class="menu-toggle"
          @click="$emit('toggle-sidebar')"
        >
          ☰
        </button>
        <h2 class="navbar-title">{{ title }}</h2>
      </div>
      <div class="navbar-right">
        <slot name="actions" />
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useMobile } from '../composables/useMobile'

const props = defineProps({
  title: {
    type: String,
    default: 'Dashboard'
  }
})

defineEmits(['toggle-sidebar'])

const { isMobile } = useMobile()
</script>

<style scoped>
.navbar {
  background-color: white;
  border-bottom: 1px solid var(--mind-gray-border);
  padding: var(--spacing-4) var(--spacing-6);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

.menu-toggle {
  background: none;
  border: none;
  font-size: var(--text-2xl);
  cursor: pointer;
  padding: var(--spacing-2);
  color: var(--mind-gray-dark);
}

.navbar-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  margin: 0;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}
</style>

