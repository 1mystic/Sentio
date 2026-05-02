<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-section">
        <h4>VeraMind</h4>
        <p class="footer-disclaimer">
          VeraMind is not a replacement for professional therapy or medical treatment.
          If you're experiencing a crisis, please seek immediate help.
        </p>
      </div>
      <div class="footer-section">
        <h4>Resources</h4>
        <RouterLink to="/crisis" class="footer-link">Crisis Support</RouterLink>
        <RouterLink to="/resources" class="footer-link">Find Help</RouterLink>
        <RouterLink to="/educational-materials" class="footer-link">Educational Materials</RouterLink>
      </div>
      <div class="footer-section">
        <h4>Legal</h4>
        <RouterLink to="/terms" class="footer-link">Terms of Service</RouterLink>
        <RouterLink to="/privacy" class="footer-link">Privacy Policy</RouterLink>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; {{ currentYear }} VeraMind. All rights reserved.</p>
    </div>
  </footer>
</template>

<script setup>
const currentYear = new Date().getFullYear()
</script>

<style scoped>
.footer {
  background-color: white;
  border-top: 1px solid var(--mind-gray-border);
  padding: var(--spacing-8) var(--spacing-6);
  margin-top: auto;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-8);
  margin-bottom: var(--spacing-6);
}

.footer-section h4 {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  margin-bottom: var(--spacing-4);
  color: var(--mind-gray-dark);
}

.footer-disclaimer {
  font-size: var(--text-sm);
  color: var(--mind-gray);
  line-height: 1.6;
}

.footer-link {
  display: block;
  color: var(--mind-gray);
  margin-bottom: var(--spacing-2);
  font-size: var(--text-sm);
  transition: color var(--transition-fast);
}

.footer-link:hover {
  color: var(--mind-purple);
}

.footer-bottom {
  text-align: center;
  padding-top: var(--spacing-6);
  border-top: 1px solid var(--mind-gray-border);
  color: var(--mind-gray);
  font-size: var(--text-sm);
}
</style>

