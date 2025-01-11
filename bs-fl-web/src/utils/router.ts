import { createRouter, createWebHistory,type RouteLocationNormalized, type NavigationGuardNext  } from 'vue-router'

const isLogin = () => {
  return !!sessionStorage.getItem('userToken'); // 示例
}

const beforeEnter = (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  if (!isLogin()) {
    next({ name: 'login' }); // 如果未登录，重定向到登录页面
  } else {
    next(); // 如果已登录，正常进入
  }
}
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import('@/views/LoginView.vue')
    },

    {
      path: '/node_info',
      name: 'node_info',
      component: () => import('@/views/NodeInfoView.vue'),
      // beforeEnter: beforeEnter,
    },

    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      // beforeEnter: beforeEnter,
    },
    
    {
      path: '/about',
      name: 'about',
      component: () => import('@/views/AboutView.vue'),
      // beforeEnter: beforeEnter,
    }
  ]
  
})

export default router
