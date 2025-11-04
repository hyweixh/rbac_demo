
import frame from '@/views/frame/frame.vue';
import home from '@/views/home/home.vue';
import sys from '@/views/auth/index.vue';
import user from '@/views/auth/userInfo/userInfo.vue';
import role from '@/views/auth/roleInfo/roleInfo.vue';
import menu from '@/views/auth/menuInfo/menuInfo.vue';
import Forbidden from '@/views/error/401.vue';
import requestLog from '@/views/auth/requestLog/requestLog.vue'; // 审计日志
import server from '@/views/auth/server.vue'; 
import order from '@/views/auth/order.vue'; 

const routes = [
  {
    path: '/',
    name: 'frame',
    component: frame,
    meta: { text: '框架' },
    children: [
      {
        path: '/',
        name: 'home',
        component: home,
        meta: { text: '主页', icon: 'home' }
      },
      // {
      //   path: '/sys',
      //   name: 'app1',
      //   component:'auth' ,
      //   redirect: '/sys/server',
      //   meta: { text: '应用1', icon: 'app' },
      //   children: [
      //     {
      //       path: 'server', // ✅ 相对路径，不要加 /sys/
      //       name: 'server',
      //       component: server,
      //       meta: { text: '服务管理', icon: 'server' }
      //     },
      //     {
      //       path: 'order',
      //       name: 'order',
      //       component: order,
      //       meta: { text: '订单管理', icon: 'order' }
      //     }
      //   ]
      // },     
      
      {
        path: '/sys/',
        name: 'sys',
        component: sys,
        children: [
          {
            path: 'user',
            name: 'user',
            component: user
          },
          {
            path: 'role',
            name: 'role',
            component: role
          },
          {
            path: 'menu',
            name: 'menu',
            component: menu
          },
          {
            path: '/requestLog',
            name: 'requestLog',
            component: requestLog,
            meta: { text: '审计日志', icon: 'Redis' }
          }
        ]
      },
      
      
      {
        path: '/Forbidden',
        name: 'Forbidden',
        component: Forbidden
      },
      
    ]
  }
];

export default routes;
