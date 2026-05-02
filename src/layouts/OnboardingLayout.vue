<template>
  <div class="onboarding-shell">
    <div class="onboarding-bg" />
    <div class="onboarding-inner">
      <div class="onboarding-header">
        <div class="onb-logo">
          <div class="logo-mark">S</div>
          <span>Sentio</span>
        </div>
        <div class="onb-progress">
          <div class="progress-text">Step {{ currentStep }} of {{ totalSteps }}</div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: progressPct + '%' }" />
          </div>
        </div>
      </div>
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const steps = ['welcome', 'baseline', 'interests', 'complete']
const currentStep = computed(() => {
  const seg = route.path.split('/').pop()
  const idx = steps.indexOf(seg)
  return idx >= 0 ? idx + 1 : 1
})
const totalSteps = steps.length
const progressPct = computed(() => (currentStep.value / totalSteps) * 100)
</script>

<style scoped>
.onboarding-shell { min-height: 100vh; display: flex; flex-direction: column; position: relative; }
.onboarding-bg { position: absolute; inset: 0; background: linear-gradient(160deg, #f4f3f8 0%, #edeaf4 50%, #e4e1f5 100%); }
.onboarding-inner { position: relative; z-index: 2; max-width: 680px; margin: 0 auto; padding: 40px 24px; width: 100%; }
.onboarding-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 48px; }
.onb-logo { display: flex; align-items: center; gap: 8px; font-size: 18px; font-weight: 800; color: var(--plum); }
.logo-mark {
  width: 30px; height: 30px; border-radius: 8px;
  background: linear-gradient(135deg, #dad8f9, #9b94e8);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 900; color: var(--plum);
}
.onb-progress { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; min-width: 180px; }
.progress-text { font-size: 12px; color: var(--slate); font-weight: 600; }
.progress-track { width: 160px; height: 4px; background: var(--lavender-soft); border-radius: 99px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, var(--lavender-deep), var(--lavender-mid)); border-radius: 99px; transition: width 0.4s ease; }
</style>
