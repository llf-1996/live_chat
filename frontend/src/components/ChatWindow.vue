<template>
  <div class="chat-window-container">
    <!-- 顶部信息栏 -->
    <div v-if="currentConversation" class="chat-header">
      <!-- 买家视图：显示商家信息 -->
      <template v-if="chatStore.currentUser.role === 'buyer'">
        <div class="merchant-badge">店铺</div>
        <span class="merchant-name">{{ currentConversation.merchant?.username }}</span>
        <span 
          class="header-online-status"
          :class="{ 'is-online': chatStore.isUserOnline(currentConversation.merchant_id) }"
        >
          {{ chatStore.isUserOnline(currentConversation.merchant_id) ? '在线' : '离线' }}
        </span>
      </template>
      <!-- 商家视图：显示客户信息 -->
      <template v-else-if="chatStore.currentUser.role === 'merchant'">
        <div class="merchant-badge">客户</div>
        <span class="merchant-name">{{ currentConversation.customer?.username }}</span>
        <span 
          class="header-online-status"
          :class="{ 'is-online': chatStore.isUserOnline(currentConversation.customer_id) }"
        >
          {{ chatStore.isUserOnline(currentConversation.customer_id) ? '在线' : '离线' }}
        </span>
      </template>
      <!-- 管理员视图：显示双方信息 -->
      <template v-else-if="chatStore.currentUser.role === 'admin'">
        <div class="merchant-badge admin-badge">监控</div>
        <span class="conversation-parties">
          <span class="party-customer">
            {{ currentConversation.customer?.username }}
            <span 
              class="inline-status-dot"
              :class="{ 'is-online': chatStore.isUserOnline(currentConversation.customer_id) }"
            ></span>
          </span>
          <el-icon :size="14" class="party-arrow"><Right /></el-icon>
          <span class="party-merchant">
            {{ currentConversation.merchant?.username }}
            <span 
              class="inline-status-dot"
              :class="{ 'is-online': chatStore.isUserOnline(currentConversation.merchant_id) }"
            ></span>
          </span>
        </span>
      </template>
      <el-icon class="more-icon"><MoreFilled /></el-icon>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <el-empty :description="getEmptyDescription()" :image-size="200" />
    </div>

    <!-- 消息列表 -->
    <div v-if="currentConversation" ref="messageListRef" class="message-list" @scroll="handleScroll">
      <!-- 加载更多提示 -->
      <div v-if="chatStore.isLoadingMessages" class="loading-more">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      
      <!-- 没有更多消息提示 -->
      <div v-else-if="!chatStore.hasMoreMessages && messages.length > 0" class="no-more-messages">
        <span>已显示全部消息</span>
      </div>
      
      <div
        v-for="message in messages"
        :key="message.id"
        class="message-wrapper"
        :class="{ 'is-self': message.sender_id === chatStore.currentUser.id }"
      >
        <el-avatar
          :size="40"
          :src="getAvatarUrl(message.sender_id)"
          :style="getAvatarStyle(message.sender_id)"
          class="message-avatar"
        >
          {{ getAvatarText(message.sender_id) }}
        </el-avatar>
        <div class="message-content">
          <div class="message-info">
            <span class="sender-name">{{ getSenderName(message.sender_id) }}</span>
            <span class="message-time">{{ formatTime(message.created_at) }}</span>
          </div>
          <div class="message-bubble">
            <template v-if="message.message_type === 'text'">
              {{ message.content }}
            </template>
            <template v-else-if="message.message_type === 'image'">
              <el-image
                :src="message.content"
                :preview-src-list="[message.content]"
                fit="cover"
                class="message-image"
              />
            </template>
            <template v-else-if="message.message_type === 'file'">
              <div class="file-message">
                <el-icon><Document /></el-icon>
                <a :href="message.content" target="_blank">下载文件</a>
              </div>
            </template>
          </div>
          <!-- 已读/未读状态 -->
          <div v-if="message.sender_id === chatStore.currentUser.id" class="read-status">
            <el-icon v-if="message.is_read" class="read-icon"><Select /></el-icon>
            <span :class="{ 'read-text': message.is_read, 'unread-text': !message.is_read }">
              {{ message.is_read ? '已读' : '未读' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部输入区域 -->
    <MessageInput v-if="currentConversation" ref="messageInputRef" />
  </div>
</template>

<script setup>
import { computed, watch, nextTick, ref } from 'vue'
import { useChatStore } from '../stores/chat'
import MessageInput from './MessageInput.vue'
import { MoreFilled, Document, Right, Select, Loading } from '@element-plus/icons-vue'

const chatStore = useChatStore()
const messageListRef = ref(null)
const messageInputRef = ref(null)
const lastScrollHeight = ref(0) // 记录上次的滚动高度
const lastMessageCount = ref(0) // 记录上次的消息数量

// 暴露方法供外部调用
function setInputMessage(content) {
  if (messageInputRef.value) {
    messageInputRef.value.setInputMessage(content)
  }
}

defineExpose({
  setInputMessage
})

const currentConversation = computed(() => chatStore.currentConversation)
const messages = computed(() => chatStore.messages)

// 获取头像图片URL（优先使用图片）
function getAvatarUrl(senderId) {
  if (senderId === chatStore.currentUser.id) {
    return chatStore.currentUser.avatar || undefined
  }
  
  if (chatStore.currentUser.role === 'admin') {
    if (senderId === currentConversation.value?.customer_id) {
      return currentConversation.value?.customer?.avatar || undefined
    } else if (senderId === currentConversation.value?.merchant_id) {
      return currentConversation.value?.merchant?.avatar || undefined
    }
  }
  
  if (chatStore.currentUser.role === 'buyer') {
    return currentConversation.value?.merchant?.avatar || undefined
  } else {
    return currentConversation.value?.customer?.avatar || undefined
  }
}

// 获取头像显示文字（用户名首字母或角色标识）
function getAvatarText(senderId) {
  const name = getSenderName(senderId)
  return name ? name.charAt(0).toUpperCase() : '?'
}

// 获取头像背景颜色
function getAvatarStyle(senderId) {
  // 根据角色返回不同颜色
  let bgColor = '#909399' // 默认灰色
  
  if (senderId === chatStore.currentUser.id) {
    // 自己的消息：绿色
    bgColor = '#67C23A'
  } else if (chatStore.currentUser.role === 'admin') {
    // 管理员视图：客户蓝色，商户橙色
    if (senderId === currentConversation.value?.customer_id) {
      bgColor = '#5B8FF9' // 客户蓝色
    } else if (senderId === currentConversation.value?.merchant_id) {
      bgColor = '#FA8C16' // 商户橙色
    }
  } else if (chatStore.currentUser.role === 'buyer') {
    // 买家视图：商户橙色
    bgColor = '#FA8C16'
  } else if (chatStore.currentUser.role === 'merchant') {
    // 商户视图：客户蓝色
    bgColor = '#5B8FF9'
  }
  
  return {
    backgroundColor: bgColor,
    color: '#ffffff',
    fontWeight: '500'
  }
}

function getSenderName(senderId) {
  if (senderId === chatStore.currentUser.id) {
    return chatStore.currentUser.username
  }
  
  // 管理员：根据发送者ID判断是客户还是商户
  if (chatStore.currentUser.role === 'admin') {
    if (senderId === currentConversation.value?.customer_id) {
      return currentConversation.value?.customer?.username || '客户'
    } else if (senderId === currentConversation.value?.merchant_id) {
      return currentConversation.value?.merchant?.username || '商户'
    }
  }
  
  // 买家/商家：根据角色返回对方名称
  if (chatStore.currentUser.role === 'buyer') {
    return currentConversation.value?.merchant?.username || '商家'
  } else {
    return currentConversation.value?.customer?.username || '客户'
  }
}

function getEmptyDescription() {
  const descriptions = {
    buyer: '请选择商家开始聊天',
    merchant: '请选择客户开始聊天',
    admin: '请选择会话查看聊天记录'
  }
  return descriptions[chatStore.currentUser.role] || '请选择会话'
}

function formatTime(timestamp) {
  // Unix时间戳（秒）需要转换为毫秒
  const date = new Date(timestamp * 1000)
  const year = date.getFullYear()
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  const seconds = date.getSeconds().toString().padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// 滚动监听：距离顶部100px时自动加载更多
function handleScroll() {
  if (!messageListRef.value) return
  
  const scrollTop = messageListRef.value.scrollTop
  const scrollHeight = messageListRef.value.scrollHeight
  
  // 滚动到顶部附近100px，且有更多消息，且未在加载中
  if (scrollTop < 100 && chatStore.hasMoreMessages && !chatStore.isLoadingMessages) {
    // 记录当前滚动高度
    lastScrollHeight.value = scrollHeight
    
    // 加载更多消息
    chatStore.loadMoreMessages().then(() => {
      // 加载完成后恢复滚动位置
      nextTick(() => {
        if (messageListRef.value) {
          const newScrollHeight = messageListRef.value.scrollHeight
          messageListRef.value.scrollTop = newScrollHeight - lastScrollHeight.value
        }
      })
    })
  }
}

// 自动滚动到底部
function scrollToBottom(smooth = false) {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTo({
        top: messageListRef.value.scrollHeight,
        behavior: smooth ? 'smooth' : 'auto'
      })
    }
  })
}

// 监听消息变化，智能滚动
watch(messages, (newMessages) => {
  if (!currentConversation.value) return
  
  const newLength = newMessages.length
  const oldLength = lastMessageCount.value
  
  if (oldLength === 0 && newLength > 0) {
    // 首次加载消息（切换会话后），直接滚动到底部
    nextTick(() => {
      scrollToBottom() // 直接定位
    })
  } else if (newLength > oldLength) {
    // 消息数量增加
    if (!chatStore.isLoadingMessages) {
      // 不是加载更多状态，说明是新消息到达，滚动到底部
      nextTick(() => {
        scrollToBottom(true) // 平滑滚动
      })
    }
  }
  
  lastMessageCount.value = newLength
}, { deep: true })

// 切换会话时重置计数
watch(currentConversation, () => {
  lastMessageCount.value = 0
})
</script>

<style scoped>
.chat-window-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f7f7f7;
}

.chat-header {
  height: 60px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: white;
  border-bottom: 1px solid #e4e7ed;
}

.merchant-badge {
  padding: 4px 8px;
  background-color: #ff6600;
  color: white;
  font-size: 12px;
  border-radius: 4px;
}

.admin-badge {
  background-color: #E8684A;
}

.merchant-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

/* 头部在线状态 */
.header-online-status {
  margin-left: 12px;
  padding: 2px 8px;
  font-size: 12px;
  border-radius: 10px;
  background-color: #f5f5f5;
  color: #8c8c8c;
  transition: all 0.3s;
}

.header-online-status.is-online {
  background-color: #f6ffed;
  color: #52c41a;
  font-weight: 500;
}

/* 管理员视图：双方信息 */
.conversation-parties {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
}

.party-customer {
  font-weight: 500;
  color: #5B8FF9; /* 客户蓝色 */
}

.party-arrow {
  color: #bfbfbf;
}

.party-merchant {
  font-weight: 500;
  color: #FA8C16; /* 商户橙色 */
}

/* 管理员视图：内联状态点 */
.inline-status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #d9d9d9; /* 离线：灰色 */
  margin-left: 6px;
  vertical-align: middle;
  transition: background-color 0.3s;
}

.inline-status-dot.is-online {
  background-color: #52c41a; /* 在线：绿色 */
  box-shadow: 0 0 0 2px rgba(82, 196, 26, 0.2);
}

.more-icon {
  margin-left: auto;
  font-size: 20px;
  color: #909399;
  cursor: pointer;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-list {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.message-wrapper {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message-wrapper.is-self {
  flex-direction: row-reverse;
}

.message-wrapper.is-self .message-content {
  align-items: flex-end;
}

.message-wrapper.is-self .message-bubble {
  background-color: #95ec69;
  color: #000;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 60%;
}

.message-info {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.message-bubble {
  padding: 10px 14px;
  background-color: white;
  border-radius: 8px;
  word-break: break-word;
  line-height: 1.5;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.message-image {
  max-width: 200px;
  border-radius: 4px;
  cursor: pointer;
}

.file-message {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-message a {
  color: #409eff;
  text-decoration: none;
}

.file-message a:hover {
  text-decoration: underline;
}

.read-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  margin-top: 4px;
}

.read-icon {
  color: #67c23a;
  font-size: 14px;
}

.read-text {
  color: #67c23a;
}

.unread-text {
  color: #909399;
}

/* 加载提示样式 */
.loading-more, .no-more-messages {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  font-size: 12px;
  color: #909399;
}

.loading-more {
  color: #409eff;
}
</style>
