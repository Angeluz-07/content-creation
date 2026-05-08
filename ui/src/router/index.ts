import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/download-section',
      name: 'downloadSection',
      component: () => import('../views/DownloadSection.vue'),
    },
    {
      path: '/short-production',
      name: 'shortProductionSection',
      component: () => import('../views/ShortProductionSection.vue'),
    },
  ],
})

export default router
