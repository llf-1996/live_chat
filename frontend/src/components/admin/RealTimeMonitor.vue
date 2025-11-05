<template>
  <div class="real-time-monitor">
    <div class="monitor-container">
      <!-- 左侧：会话列表 -->
      <AdminConversationList class="conversation-list" />

      <!-- 中间：聊天窗口 -->
      <ChatWindow class="chat-window" />

      <!-- 右侧：订单面板 -->
      <OrderPanel class="order-panel" @use-quick-reply="() => {}" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'
import AdminConversationList from '@/components/AdminConversationList.vue'
import ChatWindow from '@/components/ChatWindow.vue'
import OrderPanel from '@/components/OrderPanel.vue'

const chatStore = useChatStore()
const authStore = useAuthStore()

onMounted(async () => {
  // 管理员需要实时监控，使用管理员自己的 ID 建立 WebSocket 连接
  if (authStore.adminUser?.id) {
    // 设置管理员的 user_id 到 chatStore
    chatStore.userId = authStore.adminUser.id
    chatStore.currentUser = authStore.adminUser
    
    // 加载会话列表（管理员加载所有会话）
    await chatStore.loadConversations()
    
    // 建立 WebSocket 连接用于实时监控
    chatStore.connectWebSocket()
  }
})

onUnmounted(() => {
  // 离开页面时断开 WebSocket
  chatStore.disconnectWebSocket()
})
</script>

<style scoped>
.real-time-monitor {
  width: 100%;
  height: calc(100vh - 88px);
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.monitor-container {
  display: flex;
  height: 100%;
}

.conversation-list {
  width: 300px;
  flex-shrink: 0;
  border-right: 1px solid #e4e7ed;
}

.chat-window {
  flex: 1;
  border-right: 1px solid #e4e7ed;
}

.order-panel {
  width: 320px;
  flex-shrink: 0;
}
</style>

