<template>
  <div class="buyer-list">
    <!-- 标题 -->
    <div class="list-header">
      <el-icon :size="20" class="header-icon"><ChatDotRound /></el-icon>
      <h3 class="list-title">聊天列表</h3>
    </div>

    <!-- 搜索框 -->
    <div class="search-box">
      <el-input
        v-model="searchKeyword"
        placeholder="请输入名称"
        :prefix-icon="Search"
        clearable
        @input="handleSearch"
      />
    </div>

    <!-- 会话列表 -->
    <div class="conversations-list">
      <div
        v-for="conversation in filteredConversations"
        :key="conversation.id"
        class="conversation-item"
        :class="{ active: chatStore.currentConversation?.id === conversation.id }"
        @click="selectConversation(conversation)"
      >
        <el-badge :value="conversation.merchant_unread_count" :hidden="conversation.merchant_unread_count === 0">
          <div class="avatar-wrapper">
            <el-avatar 
              :size="45"
              :src="conversation.customer?.avatar || undefined"
              :style="{ backgroundColor: '#5B8FF9', color: '#ffffff', fontWeight: '500' }"
            >
              {{ conversation.customer?.username?.charAt(0).toUpperCase() }}
            </el-avatar>
            <span 
              class="online-status" 
              :class="{ 'is-online': chatStore.isUserOnline(conversation.customer_id) }"
              :title="chatStore.isUserOnline(conversation.customer_id) ? '在线' : '离线'"
            ></span>
          </div>
        </el-badge>
        <div class="conversation-info">
          <div class="conversation-name">
            {{ conversation.customer?.username || '未知用户' }}
          </div>
          <div class="last-message">
            {{ conversation.last_message || '暂无消息' }}
          </div>
        </div>
        <div class="conversation-time">
          {{ formatTime(conversation.last_message_time) }}
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty 
        v-if="filteredConversations.length === 0" 
        :description="searchKeyword ? '未找到匹配的用户' : '暂无咨询'" 
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

// 定义事件
const emit = defineEmits(['conversation-selected'])

// 过滤后的会话列表（根据搜索关键词）
const filteredConversations = computed(() => {
  if (!searchKeyword.value.trim()) {
    return chatStore.conversations
  }
  const keyword = searchKeyword.value.toLowerCase()
  return chatStore.conversations.filter(conversation => 
    conversation.customer?.username?.toLowerCase().includes(keyword)
  )
})

function handleSearch() {
  // 搜索时自动触发（通过 computed 实现）
}

function selectConversation(conversation) {
  chatStore.selectConversation(conversation)
  // 触发事件，通知父组件会话已选中
  emit('conversation-selected')
}

function formatTime(time) {
  if (!time) return ''
  // Unix时间戳（秒）需要转换为毫秒
  const date = new Date(time * 1000)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${date.getMonth() + 1}-${date.getDate()}`
}
</script>

<style scoped>
.buyer-list {
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
  color: #FA8C16;
}

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

/* 会话列表 */
.conversations-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 14px 16px;
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
  border-color: #FA8C16;
  box-shadow: 0 2px 8px rgba(250, 140, 22, 0.1);
}

/* 头像容器和在线状态 */
.avatar-wrapper {
  position: relative;
  display: inline-block;
}

.online-status {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #d9d9d9; /* 离线：灰色 */
  border: 2px solid #ffffff;
  transition: background-color 0.3s;
}

.online-status.is-online {
  background-color: #52c41a; /* 在线：绿色 */
  box-shadow: 0 0 0 2px rgba(82, 196, 26, 0.2);
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f1f1f;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.last-message {
  font-size: 12px;
  color: #8c8c8c;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-time {
  font-size: 12px;
  color: #bfbfbf;
  flex-shrink: 0;
  align-self: flex-start;
}

/* ==================== 响应式媒体查询 ==================== */

/* 平板端 (768px-1023px) */
@media (min-width: 768px) and (max-width: 1023px) {
  .list-header {
    padding: 12px 14px;
  }
  
  .search-box {
    padding: 10px 14px;
  }
  
  .conversation-item {
    padding: 12px 14px;
    gap: 10px;
  }
}

/* 手机端 (<768px) */
@media (max-width: 767px) {
  .list-header {
    padding: 12px 16px;
  }
  
  .list-title {
    font-size: 15px;
  }
  
  .search-box {
    padding: 10px 16px;
  }
  
  .list-container {
    padding: 6px 0;
  }
  
  .conversation-item {
    padding: 12px 16px;
    gap: 10px;
    margin: 0 8px 6px 8px;
  }
  
  .conversation-name {
    font-size: 13px;
  }
  
  .last-message {
    font-size: 11px;
  }
  
  .conversation-time {
    font-size: 11px;
  }
  
  .online-status {
    width: 10px;
    height: 10px;
  }
}
</style>

