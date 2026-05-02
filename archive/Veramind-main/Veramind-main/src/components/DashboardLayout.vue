<template>
  <div class="dashboard-layout">
    <Sidebar />
    <div class="dashboard-content">
      <Navbar />
      <main class="main-content">
        <slot />
      </main>
      <Footer />
    </div>
  </div>
</template>

<script setup>
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
import Footer from './Footer.vue'
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--mind-gray-light);
}

.dashboard-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 256px; /* Sidebar width */
}

.main-content {
  flex: 1;
  padding: var(--spacing-6);
}

@media (max-width: 768px) {
  .dashboard-content {
    margin-left: 0;
  }
}
</style>

