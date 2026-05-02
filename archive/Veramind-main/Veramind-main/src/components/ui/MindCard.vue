<template>
  <div class="mind-card" :class="variant">
    <header v-if="title || $slots.header" class="mind-card__header">
      <slot name="header">
        <div class="mind-card__title">{{ title }}</div>
        <p v-if="description" class="mind-card__description">{{ description }}</p>
      </slot>
    </header>

    <div class="mind-card__body">
      <slot />
    </div>

    <footer v-if="$slots.footer" class="mind-card__footer">
      <slot name="footer" />
    </footer>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  variant: { type: String, default: '' }
})
</script>

<style scoped>
.mind-card {
  background-color: white;
  border: 1px solid var(--mind-gray-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-6);
  box-shadow: var(--shadow-sm);
  transition: border-color var(--transition-base), box-shadow var(--transition-base);
}

.mind-card.info {
  border-color: var(--mind-blue);
}

.mind-card.success {
  border-color: var(--success);
}

.mind-card.warning {
  border-color: var(--warning);
}

.mind-card__header {
  margin-bottom: var(--spacing-4);
}

.mind-card__title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  margin-bottom: var(--spacing-2);
}

.mind-card__description {
  color: var(--mind-gray);
  margin: 0;
}

.mind-card__body {
  color: var(--mind-gray-dark);
}

.mind-card__footer {
  margin-top: var(--spacing-4);
  padding-top: var(--spacing-3);
  border-top: 1px solid var(--mind-gray-border);
}
</style>
