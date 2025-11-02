<template>
  <div class="chat-view">
    <!-- 无权访问提示页面 -->
    <div v-if="!chatStore.userId || !chatStore.currentUser.id" class="access-denied">
      <el-result
        icon="error"
        title="访问受限"
        sub-title="您没有权限访问此页面"
      />
    </div>

    <!-- 正常显示聊天界面 -->
    <div v-else class="chat-container">
      <!-- 顶部：个人信息栏（横跨整行） -->
      <div class="user-header" :class="'user-header-' + chatStore.currentUser.role">
        <el-avatar :size="50" :src="chatStore.currentUser.avatar || '/avatars/default.png'">
          {{ chatStore.currentUser.username?.charAt(0) }}
        </el-avatar>
        <div class="user-info">
          <div class="user-name">{{ chatStore.currentUser.username }}</div>
          <div class="role-tag">
            <el-tag size="small" :type="getRoleTagType(chatStore.currentUser.role)">
              {{ getRoleLabel(chatStore.currentUser.role) }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 下方：左中右三栏 -->
      <div class="main-content">
        <!-- 左侧：根据角色显示不同列表 -->
        <!-- 买家：显示商户列表 -->
        <MerchantList v-if="chatStore.currentUser.role === 'buyer'" class="merchant-list" />
        <!-- 商户客服：显示买家列表 -->
        <BuyerList v-else-if="chatStore.currentUser.role === 'merchant'" class="merchant-list" />

        <!-- 中间：聊天窗口 -->
        <ChatWindow ref="chatWindowRef" class="chat-window" />

        <!-- 右侧：订单面板 -->
        <OrderPanel class="order-panel" @use-quick-reply="handleUseQuickReply" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '../stores/chat'
import MerchantList from '../components/MerchantList.vue'
import BuyerList from '../components/BuyerList.vue'
import ChatWindow from '../components/ChatWindow.vue'
import OrderPanel from '../components/OrderPanel.vue'

const chatStore = useChatStore()
const chatWindowRef = ref(null)

function handleUseQuickReply(content) {
  if (chatWindowRef.value) {
    chatWindowRef.value.setInputMessage(content)
  }
}

function getRoleLabel(role) {
  const labels = {
    buyer: '客',
    merchant: '商',
    admin: '平'
  }
  return labels[role] || role
}

function getRoleTagType(role) {
  const types = {
    buyer: 'primary',
    merchant: 'success',
    admin: 'warning'
  }
  return types[role] || 'info'
}

onMounted(async () => {
  // 如果没有userId，不执行任何加载操作
  if (!chatStore.userId) {
    console.warn('访问受限：缺少必要的访问凭证')
    return
  }
  // 1. 首先加载当前用户信息（从数据库获取角色等信息）
  await chatStore.loadCurrentUser()
  
  // 2. 加载会话列表（所有角色都需要）
  await chatStore.loadConversations()
  
  // 3. 根据角色加载快捷消息（管理员不需要，只读权限）
  if (chatStore.currentUser.role === 'buyer' || chatStore.currentUser.role === 'merchant') {
    await chatStore.loadQuickReplies(chatStore.currentUser.id)
  }

  // 4. 如果有target参数，自动打开对话
  if (chatStore.targetUserId) {
    await chatStore.openConversationWithUser(chatStore.targetUserId)
  }

  // 5. 建立WebSocket连接（所有角色都需要）
  chatStore.connectWebSocket()
})

onUnmounted(() => {
  // 断开WebSocket连接
  chatStore.disconnectWebSocket()
})
</script>

<style scoped>
.chat-view {
  width: 100%;
  height: 100vh;
  background-color: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 无权访问提示页面 */
.access-denied {
  width: 500px;
  max-width: 90vw;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 40px;
}

/* 聊天容器 */
.chat-container {
  width: 1400px;
  height: 900px;
  max-width: 95vw;
  max-height: 95vh;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部个人信息栏 - 横跨整行 */
.user-header {
  width: 100%;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

/* 买家（客户）- 柔和蓝色渐变 */
.user-header-buyer {
  background: linear-gradient(135deg, #5B8FF9 0%, #4B7CC4 100%);
  border-bottom: 2px solid #3A6399;
}

/* 商家（商户）- 柔和橙色渐变 */
.user-header-merchant {
  background: linear-gradient(135deg, #FA8C16 0%, #D87607 100%);
  border-bottom: 2px solid #B86200;
}

/* 管理员（平台）- 柔和红色渐变 */
.user-header-admin {
  background: linear-gradient(135deg, #E8684A 0%, #CF5B47 100%);
  border-bottom: 2px solid #A8432F;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  margin-bottom: 4px;
}

.role-tag :deep(.el-tag) {
  background-color: rgba(255, 255, 255, 0.25);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.4);
  font-weight: 500;
}

/* 主内容区 - 左中右三栏 */
.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

.merchant-list {
  width: 280px;
  flex-shrink: 0;
  border-right: 1px solid #e4e7ed;
}

.chat-window {
  flex: 1;
  min-width: 0;
  border-right: 1px solid #e4e7ed;
}

.order-panel {
  width: 320px;
  flex-shrink: 0;
}
</style>

