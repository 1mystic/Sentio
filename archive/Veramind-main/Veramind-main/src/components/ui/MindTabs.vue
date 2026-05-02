<template>
  <div class="mind-tabs">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      class="mind-tab"
      :class="{ active: tab.value === modelValue }"
      type="button"
      @click="$emit('update:modelValue', tab.value)"
    >
      <span class="mind-tab__label">{{ tab.label }}</span>
      <span v-if="tab.badge" class="mind-tab__badge">{{ tab.badge }}</span>
    </button>
  </div>
</template>

<script setup>
defineProps({
  tabs: {
    type: Array,
    default: () => []
  },
  modelValue: {
    type: [String, Number],
    default: ''
  }
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
.mind-tabs {
  display: inline-flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
  background-color: var(--mind-gray-light);
  padding: var(--spacing-2);
  border-radius: var(--radius-full);
}

.mind-tab {
  border: none;
  background-color: transparent;
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--mind-gray);
  display: inline-flex;
  gap: var(--spacing-2);
  align-items: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.mind-tab.active {
  background-color: white;
  color: var(--mind-purple);
  box-shadow: var(--shadow-sm);
}

.mind-tab__badge {
  background-color: var(--mind-gray-light);
  padding: 0 var(--spacing-2);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
}
</style>
