<template>
  <div class="message-management">
    <div class="page-header">
      <h2>消息管理</h2>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索消息内容"
        :prefix-icon="Search"
        clearable
        style="width: 300px"
        @input="loadMessages"
      />
      <el-select
        v-model="filterType"
        placeholder="消息类型"
        clearable
        style="width: 150px; margin-left: 16px"
        @change="loadMessages"
      >
        <el-option label="全部类型" value="" />
        <el-option label="文本" value="text" />
        <el-option label="图片" value="image" />
        <el-option label="文件" value="file" />
      </el-select>
      <el-input-number
        v-model="filterConversationId"
        placeholder="会话ID"
        :min="0"
        controls-position="right"
        style="width: 150px; margin-left: 16px"
        @change="loadMessages"
      />
    </div>

    <!-- 消息列表表格 -->
    <el-table :data="messages" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="消息ID" width="100" />
      <el-table-column label="会话ID" width="100">
        <template #default="{ row }">
          {{ row.conversation_id }}
        </template>
      </el-table-column>
      <el-table-column label="发送者" min-width="150">
        <template #default="{ row }">
          <div style="display: flex; align-items: center;">
            <el-avatar :size="32" :src="row.sender?.avatar" style="margin-right: 8px">
              {{ row.sender?.username?.charAt(0) }}
            </el-avatar>
            <div>
              <div>{{ row.sender?.username }}</div>
              <el-tag size="small" :type="getRoleTagType(row.sender?.role)" style="margin-top: 4px">
                {{ getRoleLabel(row.sender?.role) }}
              </el-tag>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="消息内容" min-width="250" show-overflow-tooltip>
        <template #default="{ row }">
          {{ getMessagePreview(row) }}
        </template>
      </el-table-column>
      <el-table-column label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="getTypeTagType(row.message_type)" size="small">
            {{ getTypeLabel(row.message_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="已读" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_read ? 'success' : 'info'" size="small">
            {{ row.is_read ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="发送时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="showDetailDialog(row)">
            查看详情
          </el-button>
          <el-button link type="danger" size="small" @click="deleteMessage(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[20, 50, 100, 200]"
        :total="totalMessages"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadMessages"
        @current-change="loadMessages"
      />
    </div>

    <!-- 消息详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="消息详情"
      width="600px"
    >
      <div v-if="currentMessage" class="message-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="消息ID">{{ currentMessage.id }}</el-descriptions-item>
          <el-descriptions-item label="会话ID">{{ currentMessage.conversation_id }}</el-descriptions-item>
          <el-descriptions-item label="发送者">
            <div style="display: flex; align-items: center;">
              <el-avatar :size="32" :src="currentMessage.sender?.avatar" style="margin-right: 8px">
                {{ currentMessage.sender?.username?.charAt(0) }}
              </el-avatar>
              <span>{{ currentMessage.sender?.username }}</span>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="消息类型">
            <el-tag :type="getTypeTagType(currentMessage.message_type)">
              {{ getTypeLabel(currentMessage.message_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="已读状态">
            <el-tag :type="currentMessage.is_read ? 'success' : 'info'">
              {{ currentMessage.is_read ? '已读' : '未读' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="发送时间">
            {{ formatTime(currentMessage.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="消息内容">
            <div class="message-content-detail">
              <template v-if="currentMessage.message_type === 'text'">
                {{ currentMessage.content }}
              </template>
              <template v-else-if="currentMessage.message_type === 'image'">
                <el-image 
                  :src="currentMessage.content" 
                  fit="contain" 
                  style="max-width: 100%; max-height: 300px"
                  :preview-src-list="[currentMessage.content]"
                />
              </template>
              <template v-else-if="currentMessage.message_type === 'file'">
                <el-link :href="currentMessage.content" target="_blank" type="primary">
                  <el-icon><Download /></el-icon>
                  下载文件
                </el-link>
              </template>
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Download } from '@element-plus/icons-vue'
import api from '@/api/chat'

const messages = ref([])
const totalMessages = ref(0)
const loading = ref(false)
const searchKeyword = ref('')
const filterType = ref('')
const filterConversationId = ref(null)

const currentPage = ref(1)
const pageSize = ref(50)

const detailDialogVisible = ref(false)
const currentMessage = ref(null)

onMounted(() => {
  loadMessages()
})

async function loadMessages() {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    if (filterConversationId.value) {
      params.conversation_id = filterConversationId.value
    }
    if (filterType.value) {
      params.message_type = filterType.value
    }

    const response = await api.get('/messages/', { params })
    messages.value = response.results
    totalMessages.value = response.count

    // 客户端搜索过滤
    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase()
      messages.value = messages.value.filter(msg =>
        msg.content.toLowerCase().includes(keyword)
      )
    }

    totalMessages.value = messages.value.length
  } catch (error) {
    ElMessage.error('加载消息列表失败')
  } finally {
    loading.value = false
  }
}

function showDetailDialog(message) {
  currentMessage.value = message
  detailDialogVisible.value = true
}

async function deleteMessage(message) {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条消息吗？此操作不可恢复！',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error'
      }
    )

    await api.delete(`/messages/${message.id}`)
    ElMessage.success('删除成功')
    loadMessages()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function getRoleLabel(role) {
  const roleMap = {
    buyer: '买家',
    merchant: '商户',
    admin: '管理员',
    platform: '平台客服'
  }
  return roleMap[role] || role
}

function getRoleTagType(role) {
  const typeMap = {
    buyer: 'primary',
    merchant: 'warning',
    admin: 'danger',
    platform: 'success'
  }
  return typeMap[role] || 'info'
}

function getTypeLabel(type) {
  const typeMap = {
    text: '文本',
    image: '图片',
    file: '文件'
  }
  return typeMap[type] || type
}

function getTypeTagType(type) {
  const typeMap = {
    text: '',
    image: 'success',
    file: 'warning'
  }
  return typeMap[type] || 'info'
}

function getMessagePreview(message) {
  if (message.message_type === 'text') {
    return message.content.length > 50 
      ? message.content.substring(0, 50) + '...' 
      : message.content
  } else if (message.message_type === 'image') {
    return '[图片消息]'
  } else if (message.message_type === 'file') {
    return '[文件消息]'
  }
  return message.content
}

function formatTime(timestamp) {
  if (!timestamp) return '-'
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.message-management {
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

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.message-detail {
  padding: 16px;
}

.message-content-detail {
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  line-height: 1.6;
  word-break: break-word;
}
</style>

