import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'
import AdminView from '../views/AdminView.vue'
import LoginView from '../views/LoginView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/chat'
    },
    {
      path: '/chat',
      name: 'chat',
      component: ChatView,
      meta: { 
        title: '聊天' 
      }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { 
        title: '管理员登录'
      }
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: { 
        title: '客服后台',
        requiresAuth: true  // 标记此路由需要认证
      }
    }
  ]
})

// 全局导航守卫 - 检查认证状态
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 在线客服系统`
  }

  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    const authStore = useAuthStore()
    
    // 检查是否有 Token
    if (!authStore.token) {
      // 未登录，跳转到登录页
      next('/login')
      return
    }

    // 验证 Token 有效性
    const isValid = await authStore.checkAuth()
    
    if (isValid) {
      // Token 有效，允许访问
      next()
    } else {
      // Token 无效，跳转到登录页
      next('/login')
    }
  } else {
    // 不需要认证的路由，直接放行
    next()
  }
})

export default router

