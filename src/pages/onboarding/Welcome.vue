<script setup>
import { useRouter } from 'vue-router'
import { Brain, Check } from 'lucide-vue-next'
const router = useRouter()
</script>

<template>
  <div class="welcome-wrap fade-up">
    <!-- Brain icon -->
    <div class="icon-circle">
      <Brain :size="40" class="brain-icon" />
    </div>

    <div class="text-center">
      <h1 class="title">Welcome to Sentio</h1>
      <p class="subtitle">
        We're going to help you understand the hidden patterns in how you think.
        This short setup <strong>(3 mins)</strong> personalizes your experience.
      </p>
    </div>

    <!-- Feature list -->
    <ul class="feature-list">
      <li class="feature-item">
        <span class="feature-badge"><Check :size="13" /></span>
        <span>Discover your cognitive biases</span>
      </li>
      <li class="feature-item">
        <span class="feature-badge"><Check :size="13" /></span>
        <span>Get personalized insights</span>
      </li>
      <li class="feature-item">
        <span class="feature-badge"><Check :size="13" /></span>
        <span>Track your mental growth</span>
      </li>
    </ul>

    <!-- CTA -->
    <div class="actions">
      <button class="btn btn-primary btn-xl cta-btn" @click="router.push('/onboarding/baseline')">
        Let's get started →
      </button>
      <button class="skip-link" @click="router.push('/dashboard')">
        Skip for now
      </button>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

.welcome-wrap {
  font-family: 'Urbanist', sans-serif;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 28px;
  text-align: center;
  padding: 16px 0 32px;
}

/* Brain icon circle */
.icon-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--lavender), var(--lavender-soft));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 28px rgba(155,148,232,0.25);
  border: 2px solid rgba(218,216,249,0.6);
}
.brain-icon {
  color: var(--lavender-deep);
}

/* Text */
.text-center { max-width: 480px; }
.title {
  font-size: 32px;
  font-weight: 800;
  color: var(--plum);
  margin-bottom: 12px;
  line-height: 1.2;
}
.subtitle {
  font-size: 16px;
  color: var(--slate);
  line-height: 1.65;
}
.subtitle strong { color: var(--plum); font-weight: 700; }

/* Features */
.feature-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  max-width: 340px;
}
.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  font-weight: 500;
  color: var(--plum);
}
.feature-badge {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--lavender);
  color: var(--lavender-deep);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 800;
  flex-shrink: 0;
  border: 1.5px solid var(--lavender-mid);
}

/* Actions */
.actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  margin-top: 4px;
}
.cta-btn {
  padding: 16px 36px;
  font-size: 18px;
  border-radius: 14px;
  font-weight: 700;
  letter-spacing: -0.2px;
}
.skip-link {
  background: none;
  border: none;
  cursor: pointer;
  font-family: 'Urbanist', sans-serif;
  font-size: 13px;
  color: var(--slate);
  text-decoration: underline;
  text-underline-offset: 3px;
  padding: 4px;
  transition: color 0.15s;
}
.skip-link:hover { color: var(--plum); }
</style>
