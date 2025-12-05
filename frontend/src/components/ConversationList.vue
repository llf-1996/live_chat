<template>
  <div class="conversation-list">
    <!-- 标题 -->
    <div class="list-header">
      <el-icon :size="20" class="header-icon" :class="headerIconClass"><ChatDotRound /></el-icon>
      <h3 class="list-title">聊天列表</h3>
    </div>

    <!-- 搜索框 -->
    <div class="search-box">
      <el-input
        v-model="searchKeyword"
        placeholder="请输入名称"
        :prefix-icon="Search"
        clearable
      />
    </div>

    <!-- 会话列表 -->
    <div class="list-container">
      <div
        v-for="item in filteredItems"
        :key="item.id"
        class="conversation-item"
        :class="{ active: isActive(item) }"
        @click="handleSelect(item)"
      >
        <el-badge
          :value="item.unreadCount"
          :hidden="!item.unreadCount"
          class="badge"
        >
          <div class="avatar-wrapper">
            <el-avatar 
              :size="45"
              :src="item.targetUser?.avatar || undefined"
              :style="getAvatarStyle(item.targetUser)"
            >
              {{ getAvatarText(item.targetUser) }}
            </el-avatar>
            <span 
              class="online-status" 
              :class="{ 'is-online': isOnline(item.targetUser?.id) }"
              :title="isOnline(item.targetUser?.id) ? '在线' : '离线'"
            ></span>
          </div>
        </el-badge>

        <div class="item-info">
          <div class="item-header">
            <span class="item-name">{{ item.targetUser?.username || '未知用户' }}</span>
            <span class="time">{{ formatTime(item.lastTime) }}</span>
          </div>
          <div class="last-message">
            {{ item.lastMessage || '暂无消息' }}
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty 
        v-if="filteredItems.length === 0" 
        :description="searchKeyword ? '未找到匹配的用户' : '暂无会话'" 
        :image-size="80" 
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, ChatDotRound } from '@element-plus/icons-vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const searchKeyword = ref('')

const emit = defineEmits(['conversation-selected'])

// 根据当前用户角色判断显示逻辑
const isBuyer = computed(() => chatStore.currentUser.role === 'buyer')

// 标题图标颜色类
const headerIconClass = computed(() => isBuyer.value ? 'icon-blue' : 'icon-orange')

// 统一数据结构
const displayItems = computed(() => {
  return chatStore.conversations.map(conv => {
    // 动态判断：我是participant1还是participant2
    const isParticipant1 = conv.participant1_id === chatStore.currentUser.id
    const targetUser = isParticipant1 ? conv.participant2 : conv.participant1
    const unreadCount = isParticipant1 ? conv.participant1_unread : conv.participant2_unread
    
    return {
      id: conv.id,
      targetUser,
      unreadCount,
      lastMessage: conv.last_message,
      lastTime: conv.last_message_time,
      conversation: conv
    }
  }).filter(item => item.targetUser != null) // 过滤无效数据
})

// 过滤逻辑
const filteredItems = computed(() => {
  if (!searchKeyword.value.trim()) {
    return displayItems.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return displayItems.value.filter(item => 
    item.targetUser?.username?.toLowerCase().includes(keyword)
  )
})

// 辅助函数
function getAvatarStyle(user) {
  // 默认蓝色 (buyer)
  let color = '#5B8FF9' 
  
  if (user?.role === 'merchant') {
    color = '#FA8C16' // 橙色
  } else if (user?.role === 'platform') {
    color = '#F5222D' // 红色
  }
  
  return { backgroundColor: color, color: '#ffffff', fontWeight: '500' }
}

function getAvatarText(user) {
  return user?.username?.charAt(0).toUpperCase() || '?'
}

function isOnline(userId) {
  return chatStore.isUserOnline(userId)
}

function formatTime(time) {
  if (!time) return ''
  const date = new Date(time * 1000)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${date.getMonth() + 1}-${date.getDate()}`
}

function isActive(item) {
  return chatStore.currentConversation?.id === item.id
}

async function handleSelect(item) {
  await chatStore.selectConversation(item.conversation)
  emit('conversation-selected')
}
</script>

<style scoped>
.conversation-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #f5f5f5;
}

/* 标题区域 */
.list-header {
  padding: 16px 20px;
  background-color: white;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.header-icon {
  transition: color 0.3s;
}
.icon-blue { color: #5B8FF9; }
.icon-orange { color: #FA8C16; }

.list-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f1f1f;
}

/* 搜索框区域 */
.search-box {
  padding: 12px 16px;
  background-color: white;
  flex-shrink: 0;
}

.search-box :deep(.el-input__wrapper) {
  background-color: #f5f5f5;
  box-shadow: none;
}

.search-box :deep(.el-input__wrapper:hover),
.search-box :deep(.el-input__wrapper.is-focus) {
  background-color: #ececec;
  box-shadow: none;
}

/* 列表容器 */
.list-container {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin: 0 8px 8px 8px;
  cursor: pointer;
  background-color: white;
  border-radius: 8px;
  border: 1px solid transparent;
  transition: all 0.2s;
  gap: 12px;
}

.conversation-item:hover {
  background-color: #f8f9fa;
  border-color: #e8e8e8;
  transform: translateX(2px);
}

.conversation-item.active {
  background: linear-gradient(to right, #fff7e6 0%, #fffaf0 100%);
  border-color: #FA8C16; /* 默认用橙色作为高亮色，比较醒目 */
  box-shadow: 0 2px 8px rgba(250, 140, 22, 0.1);
}

/* 头像相关 */
.avatar-wrapper {
  position: relative;
  display: inline-block;
  flex-shrink: 0;
}

.online-status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #bfbfbf;
  border: 2px solid white;
}

.online-status.is-online {
  background-color: #52c41a;
}

/* 内容区域 */
.item-info {
  flex: 1;
  min-width: 0; /* 允许文本截断 */
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-name {
  font-weight: 500;
  color: #1f1f1f;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.time {
  font-size: 12px;
  color: #bfbfbf;
  flex-shrink: 0;
  margin-left: 8px;
}

.last-message {
  font-size: 13px;
  color: #8c8c8c;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>