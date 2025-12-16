import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import CreateSparklet from '../views/CreateSparklet.vue'
import ViewSparklet from '../views/ViewSparklet.vue'
import ManageSparklets from '../views/ManageSparklets.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/create',
    name: 'CreateSparklet',
    component: CreateSparklet
  },
  {
    path: '/sparklet/',
    redirect: '/create'
  },
  {
    path: '/sparklet/:id',
    name: 'ViewSparklet',
    component: ViewSparklet
  },
  {
    path: '/manage',
    name: 'ManageSparklets',
    component: ManageSparklets
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
