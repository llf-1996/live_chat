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
        <el-avatar :size="isMobile ? 40 : 50" :src="chatStore.currentUser.avatar || '/avatars/default.png'">
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

      <!-- 手机端：单栏显示 + 底部导航 -->
      <div v-if="isMobile" class="mobile-layout">
        <div class="mobile-content">
          <!-- 左侧：会话列表 -->
          <ConversationList 
            v-show="activePanel === 'list'" 
            class="conversation-list"
            @conversation-selected="handleConversationSelected"
          />

          <!-- 中间：聊天窗口（手机端的"更多"功能已集成到聊天窗口的输入框工具栏） -->
          <ChatWindow ref="chatWindowRef" v-show="activePanel === 'chat'" class="chat-window" />
        </div>

        <!-- 底部导航栏（手机端只显示会话和聊天） -->
        <div class="mobile-nav">
          <div 
            class="nav-item" 
            :class="{ active: activePanel === 'list' }"
            @click="activePanel = 'list'"
          >
            <el-icon :size="24"><ChatDotRound /></el-icon>
            <span>会话</span>
          </div>
          <div 
            class="nav-item" 
            :class="{ active: activePanel === 'chat' }"
            @click="activePanel = 'chat'"
          >
            <el-icon :size="24"><ChatLineRound /></el-icon>
            <span>聊天</span>
          </div>
        </div>
      </div>

      <!-- 桌面/平板端：三栏布局 -->
      <div v-else class="main-content">
        <!-- 左侧：会话列表 -->
        <ConversationList class="conversation-list" />

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
import { useChatStore } from '@/stores/chat'
import ConversationList from '@/components/ConversationList.vue'
import ChatWindow from '@/components/ChatWindow.vue'
import OrderPanel from '@/components/OrderPanel.vue'
import { ChatDotRound, ChatLineRound } from '@element-plus/icons-vue'

const chatStore = useChatStore()
const chatWindowRef = ref(null)

// 响应式状态管理
const isMobile = ref(window.innerWidth < 768)
// 手机端：如果没有 target 参数，默认显示会话列表；否则显示聊天窗口
const activePanel = ref(
  isMobile.value && !chatStore.targetUserId ? 'list' : 'chat'
) // 'list' | 'chat' | 'panel'

// 监听窗口大小变化
const handleResize = () => {
  const wasMobile = isMobile.value
  isMobile.value = window.innerWidth < 768
  
  // 从桌面切换到手机时，根据是否有当前会话决定显示哪个面板
  if (!wasMobile && isMobile.value) {
    activePanel.value = chatStore.currentConversation ? 'chat' : 'list'
  }
}

window.addEventListener('resize', handleResize)

function handleUseQuickReply(content) {
  if (chatWindowRef.value) {
    chatWindowRef.value.setInputMessage(content)
  }
}

// 手机端：会话选中后自动切换到聊天窗口
function handleConversationSelected() {
  if (isMobile.value) {
    activePanel.value = 'chat'
  }
}

function getRoleLabel(role) {
  const labels = {
    buyer: '客',
    merchant: '商',
    admin: '平',
    platform: '服'
  }
  return labels[role] || role
}

function getRoleTagType(role) {
  const types = {
    buyer: 'primary',
    merchant: 'success',
    admin: 'warning',
    platform: 'danger'
  }
  return types[role] || 'info'
}

onMounted(async () => {
  // 如果没有userId，不执行任何加载操作
  if (!chatStore.userId) {
    console.warn('访问受限：缺少必要的访问凭证')
    return
  }
  
  // 1. 并行加载用户信息和快捷回复（无依赖关系，可同时执行）
  await Promise.all([
    chatStore.loadCurrentUser(),
    chatStore.loadQuickReplies(chatStore.userId)
  ])
  
  // 2. 如果有 target_user_id，先创建会话（不加载列表，不选中）
  if (chatStore.targetUserId) {
    await chatStore.ensureConversationExists(chatStore.targetUserId)
  }
  
  // 3. 加载会话列表（此时新创建的会话已存在）
  await chatStore.loadConversations()
  
  // 4. 如果有 target_user_id，从已加载的列表中选中会话
  //    selectConversation 会自动加载消息
  if (chatStore.targetUserId) {
    await chatStore.selectConversationByUserId(chatStore.targetUserId)
  }

  // 5. 建立WebSocket连接（所有角色都需要）
  chatStore.connectWebSocket()
})

onUnmounted(() => {
  // 断开WebSocket连接
  chatStore.disconnectWebSocket()
  // 清理事件监听器
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.chat-view {
  width: 100vw;
  height: 100vh;
  background-color: #f5f5f5;
}

/* 无权访问提示页面 */
.access-denied {
  width: 500px;
  max-width: 90vw;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 40px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* 聊天容器 - 全屏显示 */
.chat-container {
  width: 100vw;
  height: 100vh;
  background-color: white;
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

/* 手机端布局 */
.mobile-layout {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.mobile-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.mobile-content > * {
  flex: 1;
  overflow: auto;
}

/* 底部导航栏 */
.mobile-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  width: 100vw;
  height: 60px;
  background: white;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 1000;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  color: #909399;
  transition: all 0.3s;
  padding: 8px 0;
}

.nav-item span {
  font-size: 12px;
}

.nav-item.active {
  color: #5B8FF9;
}

.nav-item:active {
  background-color: #f5f5f5;
}

/* 手机端时，内容区留出底部导航空间 */
.mobile-layout .mobile-content {
  padding-bottom: 60px;
}

/* ==================== 响应式媒体查询 ==================== */

/* 平板端 (768px-1023px) */
@media (min-width: 768px) and (max-width: 1023px) {
  .merchant-list {
    width: 240px;
  }
  
  .order-panel {
    width: 280px;
  }
  
  .user-header {
    padding: 12px 16px;
  }
  
  .user-name {
    font-size: 16px;
  }
}

/* 手机端 (<768px) */
@media (max-width: 767px) {
  .user-header {
    padding: 12px 16px;
  }
  
  .user-name {
    font-size: 16px;
  }
  
  .merchant-list,
  .chat-window,
  .order-panel {
    width: 100vw;
  }
}
</style>

