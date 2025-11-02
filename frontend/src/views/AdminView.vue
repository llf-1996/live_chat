<template>
  <div class="admin-view">
    <!-- 管理员后台 -->
    <AdminDashboard class="admin-container" />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import AdminDashboard from '../components/admin/AdminDashboard.vue'

const authStore = useAuthStore()

onMounted(async () => {
  // 确保已登录
  if (!authStore.isAuthenticated) {
    console.warn('未登录，请先登录')
    return
  }

  console.log('管理员已登录:', authStore.adminUser?.username)
  // 管理后台通过 JWT 认证，不需要 WebSocket 连接
  // 数据通过 API 接口获取
})
</script>

<style scoped>
.admin-view {
  width: 100%;
  height: 100vh;
  background-color: #f0f2f5;
}

/* 无权访问提示页面 */
.access-denied {
  width: 500px;
  max-width: 90vw;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 40px;
  margin: 100px auto;
}

/* 管理员后台容器 */
.admin-container {
  width: 100%;
  height: 100vh;
}
</style>

