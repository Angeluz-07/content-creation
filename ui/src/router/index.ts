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
      path: '/shorts-prod',
      name: 'shortsProd',
      component: () => import('../views/ShortsProd.vue'),
    },
  ],
})

export default router
