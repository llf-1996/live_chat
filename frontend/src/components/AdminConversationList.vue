<template>
  <div class="admin-conversation-list">
    <!-- 标题 -->
    <div class="list-header">
      <el-icon :size="20" class="header-icon"><Monitor /></el-icon>
      <h3 class="list-title">会话监控</h3>
      <el-tag size="small" type="danger" effect="plain" class="admin-badge">管理员</el-tag>
    </div>

    <!-- 搜索框 -->
    <div class="search-box">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索客户或商户名称"
        :prefix-icon="Search"
        clearable
        @input="handleSearch"
      />
    </div>

    <!-- 会话统计 -->
    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-value">{{ chatStore.conversations.length }}</span>
        <span class="stat-label">总会话</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ totalUnreadCount }}</span>
        <span class="stat-label">未读消息</span>
      </div>
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
        <!-- 双方头像 -->
        <div class="avatars-group">
          <el-avatar 
            :size="36"
            :src="conversation.customer?.avatar || undefined"
            class="avatar-customer"
          >
            {{ conversation.customer?.username?.charAt(0).toUpperCase() }}
          </el-avatar>
          <el-avatar 
            :size="36"
            :src="conversation.merchant?.avatar || undefined"
            class="avatar-merchant"
          >
            {{ conversation.merchant?.username?.charAt(0).toUpperCase() }}
          </el-avatar>
        </div>

        <!-- 会话信息 -->
        <div class="conversation-info">
          <div class="participants">
            <span class="customer-name">{{ conversation.customer?.username || '未知客户' }}</span>
            <el-icon :size="12" class="arrow-icon"><Right /></el-icon>
            <span class="merchant-name">{{ conversation.merchant?.username || '未知商户' }}</span>
          </div>
          <div class="last-message">
            {{ conversation.last_message || '暂无消息' }}
          </div>
          <div class="conversation-time">
            {{ formatTime(conversation.last_message_time) }}
          </div>
        </div>

        <!-- 右侧信息 -->
        <div class="conversation-meta">
          <el-badge 
            v-if="getTotalUnread(conversation) > 0" 
            :value="getTotalUnread(conversation)"
            class="unread-badge"
          />
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty 
        v-if="filteredConversations.length === 0" 
        :description="searchKeyword ? '未找到匹配的会话' : '暂无会话'" 
        :image-size="80"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, Monitor, Right } from '@element-plus/icons-vue'
import { useChatStore } from '../stores/chat'

const chatStore = useChatStore()
const searchKeyword = ref('')

// 过滤后的会话列表（根据搜索关键词搜索客户或商户名）
const filteredConversations = computed(() => {
  if (!searchKeyword.value.trim()) {
    return chatStore.conversations
  }
  const keyword = searchKeyword.value.toLowerCase()
  return chatStore.conversations.filter(conversation => 
    conversation.customer?.username?.toLowerCase().includes(keyword) ||
    conversation.merchant?.username?.toLowerCase().includes(keyword)
  )
})

// 计算总未读消息数
const totalUnreadCount = computed(() => {
  return chatStore.conversations.reduce((sum, conv) => 
    sum + (conv.customer_unread_count || 0) + (conv.merchant_unread_count || 0), 0
  )
})

function handleSearch() {
  // 搜索时自动触发（通过 computed 实现）
}

function selectConversation(conversation) {
  chatStore.selectConversation(conversation)
}

// 获取单个会话的总未读数（客户+商户）
function getTotalUnread(conversation) {
  return (conversation.customer_unread_count || 0) + (conversation.merchant_unread_count || 0)
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
.admin-conversation-list {
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
  color: #E8684A; /* 管理员红色主题 */
}

.list-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f1f1f;
  flex: 1;
}

.admin-badge {
  font-size: 12px;
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

/* 统计栏 */
.stats-bar {
  padding: 12px 16px;
  background-color: white;
  display: flex;
  gap: 24px;
  border-top: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #E8684A;
}

.stat-label {
  font-size: 12px;
  color: #8c8c8c;
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
  background: linear-gradient(to right, #fff0f0 0%, #fff5f5 100%); /* 红色渐变 */
  border-color: #E8684A;
  box-shadow: 0 2px 8px rgba(232, 104, 74, 0.1);
}

/* 双方头像组 */
.avatars-group {
  position: relative;
  width: 52px;
  height: 36px;
  flex-shrink: 0;
}

.avatar-customer {
  position: absolute;
  left: 0;
  top: 0;
  border: 2px solid white;
  background-color: #5B8FF9 !important; /* 客户蓝色 */
  color: white !important;
  font-weight: 500;
  z-index: 2;
}

.avatar-merchant {
  position: absolute;
  right: 0;
  top: 0;
  border: 2px solid white;
  background-color: #FA8C16 !important; /* 商户橙色 */
  color: white !important;
  font-weight: 500;
  z-index: 1;
}

/* 会话信息 */
.conversation-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.participants {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
}

.customer-name {
  font-weight: 500;
  color: #5B8FF9; /* 客户蓝色 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 0 1 auto;
  max-width: 100px;
}

.arrow-icon {
  color: #bfbfbf;
  flex-shrink: 0;
}

.merchant-name {
  font-weight: 500;
  color: #FA8C16; /* 商户橙色 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 0 1 auto;
  max-width: 100px;
}

.last-message {
  font-size: 12px;
  color: #8c8c8c;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-time {
  font-size: 11px;
  color: #bfbfbf;
  margin-top: 2px;
}

/* 右侧元信息 */
.conversation-meta {
  align-self: flex-start;
  flex-shrink: 0;
  padding-top: 2px;
}
</style>

