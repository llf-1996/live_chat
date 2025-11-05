import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/chat'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('admin_token') || null)
  const adminUser = ref(null)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!adminUser.value)

  // 登录
  async function login(username, password) {
    try {
      const response = await api.login(username, password)
      
      // 保存 Token
      token.value = response.access_token
      localStorage.setItem('admin_token', response.access_token)
      
      // 保存用户信息
      adminUser.value = response.user
      
      return { success: true }
    } catch (error) {
      console.error('登录失败:', error)
      
      // 清理状态
      token.value = null
      adminUser.value = null
      localStorage.removeItem('admin_token')
      
      // 返回错误信息
      const message = error.response?.data?.detail || '登录失败，请检查用户名和密码'
      return { success: false, message }
    }
  }

  // 退出登录
  function logout() {
    token.value = null
    adminUser.value = null
    localStorage.removeItem('admin_token')
  }

  // 检查登录状态
  async function checkAuth() {
    if (!token.value) {
      return false
    }

    try {
      const user = await api.getCurrentUser()
      adminUser.value = user
      return true
    } catch (error) {
      console.error('验证登录状态失败:', error)
      
      // Token 无效，清理状态
      token.value = null
      adminUser.value = null
      localStorage.removeItem('admin_token')
      
      return false
    }
  }

  // 初始化时检查登录状态
  async function initialize() {
    if (token.value) {
      await checkAuth()
    }
  }

  return {
    token,
    adminUser,
    isAuthenticated,
    login,
    logout,
    checkAuth,
    initialize
  }
})

