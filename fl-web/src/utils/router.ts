import { createRouter, createWebHistory,type RouteLocationNormalized, type NavigationGuardNext  } from 'vue-router'
import axios from 'axios';
import { state } from '@/utils/settings';



const beforeEnter = async (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const userSession = localStorage.getItem('userSession');
  const localSession = localStorage.getItem('localSession');
  if (!userSession || !localSession) {
    next({ name: 'login' }); // 如果未登录，重定向到登录页面
  } else {
    try {
			const res = await axios.get(
				"http://" + state.center.ip + ":" + state.center.port + "/check_session",
				{
					params: {
						session: localStorage.getItem("userSession"),
					},
				}
			); // 检查session是否有效
      if (res.status === 200) {
          state.updateCenterInfo(true);
          state.updateUserInfo(res.data.id,res.data.username,res.data.ip,res.data.port,true);
          const res_local = await axios.get(
            "http://" + state.user.ip + ":" + state.user.port + "/check_session",
            {
              params: {
                session: localStorage.getItem("localSession"),
              },
            }
          );
          if (res_local.status === 200) {
            next(); // 如果localSession有效，正常进入
          } else {
            next({ name: 'login' }); // 如果localSession无效，重定向到登录页面
          }
      } else {
        next({ name: 'login' }); // 如果session无效，重定向到登录页面
      }
    } catch (e) {
      next({ name: 'login' });
    }
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
      beforeEnter: beforeEnter, 
    },

    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      beforeEnter: beforeEnter,
    },
    
    {
      path: '/original',
      name: 'original',
      component: () => import('@/views/OriginalView.vue'),
      beforeEnter: beforeEnter,
    },

    {
      path: '/ruler',
      name: 'ruler',
      component: () => import('@/views/RulerView.vue'),
      beforeEnter: beforeEnter,
    },

    {
      path: '/aligned',
      name: 'aligned',
      component: () => import('@/views/AlignedView.vue'),
      beforeEnter: beforeEnter,
    },

    {
      path: '/net',
      name: 'net',
      component: () => import('@/views/NetView.vue')
    },
    {
      path:'/job',
      name:'job',
      component:()=>import('@/views/JobView.vue')
    }
  ]
  
})


export default router
