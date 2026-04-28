import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
     {
      path: "/shorts-prod",
      name: "shortsProd",
      component: () => import("../views/ShortsProd.vue"),
    },
  ],
})

export default router
