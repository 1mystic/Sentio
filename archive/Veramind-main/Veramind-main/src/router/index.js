import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../pages/index.vue') },
  { path: '/login', name: 'Login', component: () => import('../pages/login.vue') },
  { path: '/signup', name: 'Signup', component: () => import('../pages/signup.vue') },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../pages/dashboard.vue') },
  { path: '/assessments', name: 'Assessments', component: () => import('../pages/assessments.vue') },
  { path: '/assessment-detail', name: 'AssessmentDetail', component: () => import('../pages/assessment-detail.vue') },
  { path: '/journal', name: 'Journal', component: () => import('../pages/journal.vue') },
  { path: '/insights', name: 'Insights', component: () => import('../pages/insights.vue') },
  { path: '/modules', name: 'Modules', component: () => import('../pages/modules.vue') },
  { path: '/module-detail', name: 'ModuleDetail', component: () => import('../pages/module-detail.vue') },
  { path: '/community', name: 'Community', component: () => import('../pages/community.vue') },
  { path: '/resources', name: 'Resources', component: () => import('../pages/resources.vue') },
  { path: '/educational-materials', name: 'EducationalMaterials', component: () => import('../pages/educational-materials.vue') },
  { path: '/self-help-tools', name: 'SelfHelpTools', component: () => import('../pages/self-help-tools.vue') },
  { path: '/find-help', name: 'FindHelp', component: () => import('../pages/find-help.vue') },
  { path: '/settings', name: 'Settings', component: () => import('../pages/settings.vue') },
  { path: '/not-found', name: 'NotFound', component: () => import('../pages/not-found.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/not-found' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
