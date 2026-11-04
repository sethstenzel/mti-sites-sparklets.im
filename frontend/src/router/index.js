import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const routes = [
  { path: '/', name: 'Home', component: Home, meta: { fullTitle: 'Sparklets — little photo notes, shared by QR code' } },
  {
    path: '/create',
    name: 'CreateSparklet',
    component: () => import('../views/CreateSparklet.vue'),
    meta: { title: 'Create a sparklet' }
  },
  {
    // public ids are 22-char random tokens; anything else falls through to NotFound
    path: '/s/:token([A-Za-z0-9_-]{22})',
    name: 'ViewSparklet',
    component: () => import('../views/ViewSparklet.vue'),
    meta: { title: 'A sparklet for you' }
  },
  {
    path: '/example',
    name: 'Example',
    component: () => import('../views/ViewSparklet.vue'),
    meta: { title: 'Example sparklet', example: true }
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: () => import('../views/Privacy.vue'),
    meta: { title: 'Privacy policy' }
  },
  {
    path: '/manage',
    name: 'ManageSparklets',
    component: () => import('../views/ManageSparklets.vue'),
    meta: { title: 'Manage sparklets' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: { title: 'Page not found' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, saved) {
    return saved || { top: 0 }
  }
})

router.afterEach((to) => {
  document.title = to.meta.fullTitle || (to.meta.title ? `${to.meta.title} · Sparklets` : 'Sparklets')
})

export default router
