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
      path: '/discovery-section',
      name: 'discoverySection',
      component: () => import('../views/DiscoverySection.vue'),
    },
    {
      path: '/short-production',
      name: 'videoBuildSection',
      component: () => import('../views/VideoBuildSection.vue'),
    },
  ],
})

export default router
