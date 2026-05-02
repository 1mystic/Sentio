<template>
  <div class="landing-page">
    <header class="landing-header">
      <nav class="landing-nav">
        <div class="nav-brand">
          <h1>VeraMind</h1>
        </div>
        <div class="nav-links">
          <RouterLink to="/login" class="btn btn-outline">Sign In</RouterLink>
          <RouterLink to="/signup" class="btn btn-primary">Get Started</RouterLink>
        </div>
      </nav>
    </header>

    <main class="landing-main">
      <section class="hero">
        <h1 class="hero-title">AI-Powered Mental Wellness</h1>
        <p class="hero-subtitle">
          Discover your cognitive patterns, manage anxiety, and grow with personalized insights
        </p>
        <div class="hero-actions">
          <RouterLink to="/signup" class="btn btn-primary btn-lg">Start Your Journey</RouterLink>
          <RouterLink to="/about" class="btn btn-outline btn-lg">Learn More</RouterLink>
        </div>
        <div class="hero-disclaimer">
          <p>⚠️ VeraMind is not a replacement for professional therapy. Seek immediate help in crisis situations.</p>
        </div>
      </section>

      <section class="features">
        <h2>Key Features</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Assessments</h3>
            <p>Evidence-based mental health screenings and cognitive assessments</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📔</div>
            <h3>Journaling</h3>
            <p>AI-powered journal insights to understand your patterns</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📚</div>
            <h3>Learning Modules</h3>
            <p>Structured courses on anxiety management and cognitive awareness</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">💡</div>
            <h3>AI Insights</h3>
            <p>Personalized recommendations based on your data</p>
          </div>
        </div>
      </section>
    </main>

    <footer class="landing-footer">
      <p>&copy; {{ currentYear }} VeraMind. All rights reserved.</p>
      <div class="footer-links">
        <RouterLink to="/crisis">Crisis Support</RouterLink>
        <RouterLink to="/terms">Terms</RouterLink>
        <RouterLink to="/privacy">Privacy</RouterLink>
      </div>
    </footer>
  </div>
</template>

<script setup>
const currentYear = new Date().getFullYear()
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.landing-header {
  background-color: white;
  border-bottom: 1px solid var(--mind-gray-border);
  padding: var(--spacing-4) var(--spacing-6);
}

.landing-nav {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand h1 {
  color: var(--mind-purple);
  margin: 0;
  font-size: var(--text-2xl);
}

.nav-links {
  display: flex;
  gap: var(--spacing-3);
}

.landing-main {
  flex: 1;
}

.hero {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--spacing-16) var(--spacing-6);
  text-align: center;
}

.hero-title {
  font-size: var(--text-5xl);
  margin-bottom: var(--spacing-6);
  color: var(--mind-gray-dark);
}

.hero-subtitle {
  font-size: var(--text-xl);
  color: var(--mind-gray);
  margin-bottom: var(--spacing-8);
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: var(--spacing-4);
  justify-content: center;
  margin-bottom: var(--spacing-8);
}

.hero-disclaimer {
  padding: var(--spacing-4);
  background-color: var(--mind-blue-light);
  border-left: 4px solid var(--warning);
  border-radius: var(--radius-md);
  max-width: 600px;
  margin: 0 auto;
}

.hero-disclaimer p {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--mind-gray-dark);
}

.features {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-16) var(--spacing-6);
}

.features h2 {
  text-align: center;
  margin-bottom: var(--spacing-12);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-6);
}

.feature-card {
  background-color: white;
  padding: var(--spacing-6);
  border-radius: var(--radius-lg);
  border: 1px solid var(--mind-gray-border);
  text-align: center;
  transition: all var(--transition-base);
}

.feature-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-4);
}

.feature-card h3 {
  margin-bottom: var(--spacing-3);
}

.feature-card p {
  color: var(--mind-gray);
  margin: 0;
}

.landing-footer {
  background-color: white;
  border-top: 1px solid var(--mind-gray-border);
  padding: var(--spacing-6);
  text-align: center;
}

.footer-links {
  display: flex;
  gap: var(--spacing-4);
  justify-content: center;
  margin-top: var(--spacing-4);
}

.footer-links a {
  color: var(--mind-gray);
  font-size: var(--text-sm);
}
</style>

