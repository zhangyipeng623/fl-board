import {
  createRouter,
  createWebHistory,
  type RouteLocationNormalized,
  type NavigationGuardNext,
} from "vue-router";
import { center, user } from "@/utils/utils";
import { state } from "@/utils/settings";

const beforeEnter = async (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  if (to.name === "login") {
    next(); // 如果是访问登录页面，则直接进入
  } else {
    const userSession = localStorage.getItem("userSession");
    if (!userSession) {
      next({ name: "login" }); // 如果未登录，重定向到登录页面
    } else {
      try {
        const res = await center.get("/check_session"); // 检查session是否有效
        if (res.status === 200) {
          state.updateCenterInfo(true);
          state.updateUserInfo(
            res.data.id,
            res.data.username,
            res.data.ip,
            res.data.port,
            true
          );
          const res_local = await user.get("/check_session");
          if (res_local.status === 200) {
            next(); // 如果Session有效，正常进入
          } else {
            next({ name: "login" }); // 如果Session无效，重定向到登录页面
          }
        } else {
          next({ name: "login" }); // 如果session无效，重定向到登录页面
        }
      } catch (e) {
        next({ name: "login" });
      }
    }
  }
};

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
    },
    {
      path: "/node_info",
      name: "node_info",
      component: () => import("@/views/NodeInfoView.vue"),
      beforeEnter: beforeEnter,
    },
    {
      path: "/",
      name: "home",
      redirect: "/node_info", // 自动重定向到 /node_info
    },
    {
      path: "/original",
      name: "original",
      component: () => import("@/views/OriginalView.vue"),
      beforeEnter: beforeEnter,
    },
    {
      path: "/ruler",
      name: "ruler",
      component: () => import("@/views/RulerView.vue"),
      beforeEnter: beforeEnter,
    },
    {
      path: "/aligned",
      name: "aligned",
      component: () => import("@/views/AlignedView.vue"),
      beforeEnter: beforeEnter,
    },
    {
      path: "/net",
      name: "net",
      component: () => import("@/views/NetView.vue"),
    },
    {
      path: "/job",
      name: "job",
      component: () => import("@/views/JobView.vue"),
    },
  ],
});

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 为所有页面设置统一标题
  document.title = "基于联邦学习的数据管理系统";
  next();
});

export default router;
