import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const routes = [
  { path: '/', component: () => import('@/pages/Landing.vue'), meta: { layout: 'public' } },
  { path: '/login', component: () => import('@/pages/auth/Login.vue'), meta: { layout: 'auth' } },
  { path: '/signup', component: () => import('@/pages/auth/Signup.vue'), meta: { layout: 'auth' } },
  { path: '/onboarding', component: () => import('@/pages/onboarding/Index.vue'), meta: { layout: 'onboarding', requiresAuth: true } },
  { path: '/onboarding/welcome', component: () => import('@/pages/onboarding/Welcome.vue'), meta: { layout: 'onboarding', requiresAuth: true } },
  { path: '/onboarding/baseline', component: () => import('@/pages/onboarding/Baseline.vue'), meta: { layout: 'onboarding', requiresAuth: true } },
  { path: '/onboarding/interests', component: () => import('@/pages/onboarding/Interests.vue'), meta: { layout: 'onboarding', requiresAuth: true } },
  { path: '/onboarding/complete', component: () => import('@/pages/onboarding/Complete.vue'), meta: { layout: 'onboarding', requiresAuth: true } },
  { path: '/dashboard', component: () => import('@/pages/Dashboard.vue'), meta: { requiresAuth: true } },
  { path: '/explore', component: () => import('@/pages/explore/Index.vue'), meta: { requiresAuth: true } },
  { path: '/explore/:slug', component: () => import('@/pages/explore/BiasDetail.vue'), meta: { requiresAuth: true } },
  { path: '/assessments', component: () => import('@/pages/assessments/Index.vue'), meta: { requiresAuth: true } },
  { path: '/assessments/:id', component: () => import('@/pages/assessments/Take.vue'), meta: { requiresAuth: true } },
  { path: '/assessments/:id/results', component: () => import('@/pages/assessments/Results.vue'), meta: { requiresAuth: true } },
  { path: '/journal', component: () => import('@/pages/journal/Index.vue'), meta: { requiresAuth: true } },
  { path: '/journal/new', component: () => import('@/pages/journal/New.vue'), meta: { requiresAuth: true } },
  { path: '/journal/:id', component: () => import('@/pages/journal/Entry.vue'), meta: { requiresAuth: true } },
  { path: '/therapists', component: () => import('@/pages/therapists/Index.vue'), meta: { requiresAuth: true } },
  { path: '/therapists/:id', component: () => import('@/pages/therapists/Profile.vue'), meta: { requiresAuth: true } },
  { path: '/ai-guide', component: () => import('@/pages/AIGuide.vue'), meta: { requiresAuth: true } },
  { path: '/profile', component: () => import('@/pages/Profile.vue'), meta: { requiresAuth: true } },
  { path: '/progress', component: () => import('@/pages/Progress.vue'), meta: { requiresAuth: true } },
  { path: '/admin', component: () => import('@/pages/Admin.vue'), meta: { layout: 'public' } },
  { path: '/:pathMatch(.*)*', component: () => import('@/pages/NotFound.vue'), meta: { layout: 'public' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  // Wait for Supabase session to load before making any auth decisions.
  // Without this, auth.user is always null on hard refresh / initial load.
  await auth.ensureInitialized()

  if (!auth.user && to.meta.requiresAuth) return '/login'
  if (auth.user && (to.path === '/login' || to.path === '/signup')) return '/dashboard'
})

export default router
