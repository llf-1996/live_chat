<template>
  <div class="merchant-list-container">
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

    <!-- 商户列表 -->
    <div class="list-container">
      <div
        v-for="merchant in filteredMerchants"
        :key="merchant.id"
        class="merchant-item"
        :class="{ active: isCurrentMerchant(merchant) }"
        @click="handleMerchantClick(merchant)"
      >
        <el-badge
          :value="getUnreadCount(merchant.id)"
          :hidden="getUnreadCount(merchant.id) === 0"
          class="badge"
        >
          <div class="avatar-wrapper">
            <el-avatar 
              :size="45"
              :src="merchant.avatar || undefined"
              :style="{ backgroundColor: '#FA8C16', color: '#ffffff', fontWeight: '500' }"
            >
              {{ merchant.username?.charAt(0).toUpperCase() }}
            </el-avatar>
            <span 
              class="online-status" 
              :class="{ 'is-online': chatStore.isUserOnline(merchant.id) }"
              :title="chatStore.isUserOnline(merchant.id) ? '在线' : '离线'"
            ></span>
          </div>
        </el-badge>

        <div class="merchant-info">
          <div class="merchant-header">
            <span class="merchant-name">{{ merchant.username }}</span>
            <span class="time">{{ getLastTime(merchant.id) }}</span>
          </div>
          <div class="last-message">
            {{ getLastMessage(merchant.id) }}
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="filteredMerchants.length === 0" description="未找到匹配的用户" :image-size="80" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, ChatDotRound } from '@element-plus/icons-vue'
import { useChatStore } from '../stores/chat'

const chatStore = useChatStore()
const searchKeyword = ref('')

// 从会话列表中提取商户（买家只看到与自己有会话的商户）
const merchants = computed(() => {
  return chatStore.conversations
    .map(conv => conv.merchant)
    .filter(merchant => merchant != null) // 过滤掉null值
})

// 过滤后的商家列表（根据搜索关键词）
const filteredMerchants = computed(() => {
  if (!searchKeyword.value.trim()) {
    return merchants.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return merchants.value.filter(merchant => 
    merchant.username.toLowerCase().includes(keyword)
  )
})

function handleSearch() {
  // 搜索时自动触发（通过 computed 实现）
}

function getUnreadCount(merchantId) {
  const conv = chatStore.conversations.find(c => c.merchant_id === merchantId)
  // 买家视图：显示客户的未读消息数（对方发给我的）
  return conv ? conv.customer_unread_count : 0
}

function getLastMessage(merchantId) {
  const conv = chatStore.conversations.find(c => c.merchant_id === merchantId)
  return conv && conv.last_message ? conv.last_message : '点击开始聊天'
}

function getLastTime(merchantId) {
  const conv = chatStore.conversations.find(c => c.merchant_id === merchantId)
  if (!conv || !conv.last_message_time) return ''

  // Unix时间戳（秒）需要转换为毫秒
  const date = new Date(conv.last_message_time * 1000)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`

  return `${date.getMonth() + 1}-${date.getDate()}`
}

function isCurrentMerchant(merchant) {
  return chatStore.currentConversation?.merchant_id === merchant.id
}

async function handleMerchantClick(merchant) {
  // 从会话列表中查找对应的会话
  let conversation = chatStore.conversations.find(c => c.merchant_id === merchant.id)

  if (conversation) {
    await chatStore.selectConversation(conversation)
  }
}
</script>

<style scoped>
.merchant-list-container {
  height: 100%;
  display: flex;
  flex-direction: column;
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
  color: #5B8FF9;
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

/* 列表容器 */
.list-container {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.merchant-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  margin: 0 8px 8px 8px;
  cursor: pointer;
  transition: all 0.2s;
  background-color: white;
  border-radius: 8px;
  border: 1px solid transparent;
}

.merchant-item:hover {
  background-color: #f8f9fa;
  border-color: #e8e8e8;
  transform: translateX(2px);
}

.merchant-item.active {
  background: linear-gradient(to right, #e8f4ff 0%, #f0f8ff 100%);
  border-color: #5B8FF9;
  box-shadow: 0 2px 8px rgba(91, 143, 249, 0.1);
}

.badge {
  flex-shrink: 0;
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

.merchant-info {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.merchant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.merchant-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f1f1f;
}

.time {
  font-size: 12px;
  color: #8c8c8c;
}

.last-message {
  font-size: 13px;
  color: #8c8c8c;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
