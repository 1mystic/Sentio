<template>
  <DefaultLayout v-if="isAppLayout" />
  <AuthLayout v-else-if="isAuthLayout" />
  <OnboardingLayout v-else-if="isOnboardingLayout" />
  <router-view v-else />
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'
import OnboardingLayout from '@/layouts/OnboardingLayout.vue'

const route = useRoute()
const auth = useAuthStore()

onMounted(() => auth.initialize())

const isAppLayout = computed(() => !route.meta?.layout || route.meta?.layout === 'app')
const isAuthLayout = computed(() => route.meta?.layout === 'auth')
const isOnboardingLayout = computed(() => route.meta?.layout === 'onboarding')
</script>
