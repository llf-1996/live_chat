<template>
  <div class="conversation-management">
    <div class="page-header">
      <h2>会话管理</h2>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索客户或商户"
        :prefix-icon="Search"
        clearable
        style="width: 300px"
        @input="filterConversations"
      />
    </div>

    <!-- 会话列表表格 -->
    <el-table :data="filteredConversations" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="会话ID" width="100" />
      <el-table-column label="参与者1" min-width="150">
        <template #default="{ row }">
          <div style="display: flex; align-items: center;">
            <el-avatar :size="32" :src="row.participant1?.avatar" style="margin-right: 8px">
              {{ row.participant1?.username?.charAt(0) }}
            </el-avatar>
            <span>{{ row.participant1?.username }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="参与者2" min-width="150">
        <template #default="{ row }">
          <div style="display: flex; align-items: center;">
            <el-avatar :size="32" :src="row.participant2?.avatar" style="margin-right: 8px">
              {{ row.participant2?.username?.charAt(0) }}
            </el-avatar>
            <span>{{ row.participant2?.username }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="最后消息" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.last_message || '暂无消息' }}
        </template>
      </el-table-column>
      <el-table-column label="未读数" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.participant1_unread > 0" type="primary" size="small">
            P1: {{ row.participant1_unread }}
          </el-tag>
          <el-tag v-if="row.participant2_unread > 0" type="warning" size="small" style="margin-left: 4px">
            P2: {{ row.participant2_unread }}
          </el-tag>
          <span v-if="row.participant1_unread === 0 && row.participant2_unread === 0">-</span>
        </template>
      </el-table-column>
      <el-table-column label="更新时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.updated_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="showDetailDrawer(row)">
            查看详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 会话详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      title="会话详情"
      size="60%"
    >
      <div v-if="currentConversation" class="conversation-detail">
        <!-- 基本信息 -->
        <div class="detail-section">
          <div class="section-title">基本信息</div>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="会话ID">{{ currentConversation.id }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatTime(currentConversation.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="参与者1">
              <div style="display: flex; align-items: center;">
                <el-avatar :size="32" :src="currentConversation.participant1?.avatar" style="margin-right: 8px">
                  {{ currentConversation.participant1?.username?.charAt(0) }}
                </el-avatar>
                <span>{{ currentConversation.participant1?.username }}</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="参与者2">
              <div style="display: flex; align-items: center;">
                <el-avatar :size="32" :src="currentConversation.participant2?.avatar" style="margin-right: 8px">
                  {{ currentConversation.participant2?.username?.charAt(0) }}
                </el-avatar>
                <span>{{ currentConversation.participant2?.username }}</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="参与者1未读数">
              {{ currentConversation.participant1_unread }}
            </el-descriptions-item>
            <el-descriptions-item label="参与者2未读数">
              {{ currentConversation.participant2_unread }}
            </el-descriptions-item>
            <el-descriptions-item label="消息总数">
              {{ conversationMessages.length }}
            </el-descriptions-item>
            <el-descriptions-item label="更新时间">
              {{ formatTime(currentConversation.updated_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 历史消息 -->
        <div class="detail-section">
          <div class="section-title">历史消息</div>
          <div class="messages-container" v-loading="messagesLoading">
            <div 
              v-for="message in conversationMessages" 
              :key="message.id"
              class="message-item"
              :class="{ 'is-customer': message.sender_id === currentConversation.participant1_id }"
            >
              <div class="message-header">
                <el-avatar :size="28" :src="message.sender?.avatar">
                  {{ message.sender?.username?.charAt(0) }}
                </el-avatar>
                <span class="sender-name">{{ message.sender?.username }}</span>
                <span class="message-time">{{ formatTime(message.created_at) }}</span>
              </div>
              <div class="message-content">{{ message.content }}</div>
            </div>
            <el-empty v-if="conversationMessages.length === 0" description="暂无消息" :image-size="80" />
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import api from '@/api/chat'

const conversations = ref([])
const totalConversations = ref(0)
const loading = ref(false)
const searchKeyword = ref('')

const drawerVisible = ref(false)
const currentConversation = ref(null)
const conversationMessages = ref([])
const messagesLoading = ref(false)

const filteredConversations = computed(() => {
  if (!searchKeyword.value.trim()) {
    return conversations.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return conversations.value.filter(conv =>
    conv.participant1?.username.toLowerCase().includes(keyword) ||
    conv.participant2?.username.toLowerCase().includes(keyword)
  )
})

onMounted(() => {
  loadConversations()
})

async function loadConversations() {
  loading.value = true
  try {
    const response = await api.get('/conversations/')
    conversations.value = response.results
    totalConversations.value = response.count
  } catch (error) {
    ElMessage.error('加载会话列表失败')
  } finally {
    loading.value = false
  }
}

function filterConversations() {
  // 筛选已经通过 computed 实现
}

async function showDetailDrawer(conversation) {
  currentConversation.value = conversation
  drawerVisible.value = true
  await loadConversationMessages(conversation.id)
}

async function loadConversationMessages(conversationId) {
  messagesLoading.value = true
  try {
    // 管理端使用倒序（新消息在前）
    const response = await api.get(`/conversations/${conversationId}/messages`, {
      params: { order: 'desc' }
    })
    conversationMessages.value = response.results
  } catch (error) {
    ElMessage.error('加载历史消息失败')
    conversationMessages.value = []
  } finally {
    messagesLoading.value = false
  }
}

function formatTime(timestamp) {
  if (!timestamp) return '-'
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.conversation-management {
  background-color: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.filter-bar {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.conversation-detail {
  padding: 16px;
}

.detail-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.messages-container {
  max-height: 500px;
  overflow-y: auto;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.message-item {
  margin-bottom: 16px;
  padding: 12px;
  background-color: #fff;
  border-radius: 8px;
  border-left: 3px solid #f39c12;
}

.message-item.is-customer {
  border-left-color: #3498db;
}

.message-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.sender-name {
  margin-left: 8px;
  font-weight: 600;
  color: #303133;
}

.message-time {
  margin-left: auto;
  font-size: 12px;
  color: #909399;
}

.message-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  word-break: break-word;
}
</style>

