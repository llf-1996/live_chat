<template>
  <div class="admin-dashboard">
    <el-container>
      <!-- 左侧导航菜单 -->
      <el-aside width="220px" class="admin-aside">
        <div class="admin-logo">
          <h2>客服后台管理</h2>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="admin-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="monitor">
            <el-icon><Monitor /></el-icon>
            <span>实时监控</span>
          </el-menu-item>
          <el-menu-item index="users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="conversations">
            <el-icon><ChatDotRound /></el-icon>
            <span>会话管理</span>
          </el-menu-item>
          <el-menu-item index="messages">
            <el-icon><ChatLineRound /></el-icon>
            <span>消息管理</span>
          </el-menu-item>
        </el-menu>

        <!-- 管理员信息和退出登录 -->
        <div class="admin-user-info">
          <div class="user-info-content">
            <el-icon class="user-icon"><UserFilled /></el-icon>
            <div class="user-details">
              <div class="user-name">{{ authStore.adminUser?.username }}</div>
              <div class="user-role">管理员</div>
            </div>
          </div>
          <el-button
            type="danger"
            size="small"
            plain
            class="logout-button"
            @click="handleLogout"
          >
            退出登录
          </el-button>
        </div>
      </el-aside>

      <!-- 右侧内容区 -->
      <el-main class="admin-main">
        <RealTimeMonitor v-if="activeMenu === 'monitor'" />
        <UserManagement v-else-if="activeMenu === 'users'" />
        <ConversationManagement v-else-if="activeMenu === 'conversations'" />
        <MessageManagement v-else-if="activeMenu === 'messages'" />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { Monitor, User, ChatDotRound, ChatLineRound, UserFilled } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import RealTimeMonitor from './RealTimeMonitor.vue'
import UserManagement from './UserManagement.vue'
import ConversationManagement from './ConversationManagement.vue'
import MessageManagement from './MessageManagement.vue'

const router = useRouter()
const authStore = useAuthStore()

const activeMenu = ref('monitor')

function handleMenuSelect(index) {
  activeMenu.value = index
}

// 退出登录
async function handleLogout() {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '退出确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch {
    // 用户取消退出
  }
}
</script>

<style scoped>
.admin-dashboard {
  width: 100%;
  height: 100vh;
  background-color: #f0f2f5;
}

.admin-aside {
  background-color: #001529;
  height: 100vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.admin-logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #002140;
}

.admin-logo h2 {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.admin-menu {
  border-right: none;
  background-color: #001529;
  flex: 1;
}

.admin-user-info {
  margin-top: auto;
  padding: 16px;
  border-top: 1px solid #002140;
  background-color: #002140;
}

.user-info-content {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.user-icon {
  font-size: 32px;
  color: #409eff;
  margin-right: 12px;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 4px;
}

.user-role {
  font-size: 12px;
  color: #8c8c8c;
}

.logout-button {
  width: 100%;
}

.admin-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.65);
}

.admin-menu :deep(.el-menu-item:hover) {
  background-color: #1890ff !important;
  color: #fff;
}

.admin-menu :deep(.el-menu-item.is-active) {
  background-color: #1890ff;
  color: #fff;
}

.admin-main {
  padding: 24px;
  background-color: #f0f2f5;
  height: 100vh;
  overflow-y: auto;
}
</style>

