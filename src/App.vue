<template>
  <DefaultLayout v-if="isAppLayout" />
  <AuthLayout v-else-if="isAuthLayout" />
  <OnboardingLayout v-else-if="isOnboardingLayout" />
  <router-view v-else />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'
import OnboardingLayout from '@/layouts/OnboardingLayout.vue'

const route = useRoute()

const isAppLayout = computed(() => !route.meta?.layout || route.meta?.layout === 'app')
const isAuthLayout = computed(() => route.meta?.layout === 'auth')
const isOnboardingLayout = computed(() => route.meta?.layout === 'onboarding')
</script>
