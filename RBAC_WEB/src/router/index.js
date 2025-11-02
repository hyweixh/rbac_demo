import { createRouter, createWebHashHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import frame_routes from '@/router/frame';
import login_routes from '@/router/login';

// 路由注册
const routes = [...frame_routes, ...login_routes];

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: routes
});

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  // 登录页和激活页不做权限检查
  if (to.name !== 'staff_activite' && to.name !== 'login') {
    // 如果用户未登录并且访问的不是登录页
    if (!authStore.is_logined) {
      // 如果用户访问了一个不存在的路由（如路径匹配失败），重定向到登录页
      if (to.name === null || to.name === undefined) {
        return next({ name: 'login' });
      }
      // 否则跳转到登录页
      return next({ name: 'login' });
    } else {
      // 如果用户已登录，检查是否有权限访问该路由
      const hasPermission = authStore.menu.some((menuItem) => {
        return menuItem.path === to.path || (menuItem.children && menuItem.children.some((child) => child.path === to.path));
      });

      // 如果没有权限，重定向到首页或Forbidden页面
      if (!hasPermission  && to.name !== 'Forbidden' && to.name !== 'usercenter') {
        return next({ name: 'Forbidden' }); // 或者使用 404 页面
      }
    }
  }

  // 继续路由导航
  next();
});

export default router;
