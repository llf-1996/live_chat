<template>
  <div class="message-input-container">
    <!-- 管理员只读提示 -->
    <div v-if="isAdmin" class="admin-readonly-notice">
      <el-alert
        title="您正在以管理员身份查看此会话，无法发送消息"
        type="info"
        :closable="false"
        show-icon
      />
    </div>

    <!-- 工具栏 -->
    <div v-if="!isAdmin" class="toolbar">
      <div class="toolbar-left">
        <el-upload
          :show-file-list="false"
          :before-upload="handleFileUpload"
          accept="*/*"
          :disabled="isAdmin"
        >
          <el-button :icon="Folder" link :disabled="isAdmin">文件</el-button>
        </el-upload>

        <el-upload
          :show-file-list="false"
          :before-upload="handleImageUpload"
          accept="image/*"
          :disabled="isAdmin"
        >
          <el-button :icon="Picture" link :disabled="isAdmin">图片</el-button>
        </el-upload>
      </div>
      
      <!-- 手机端：更多按钮（只显示图标） -->
      <el-button 
        v-if="isMobile" 
        :icon="MoreFilled" 
        link 
        class="more-button"
        @click="showMoreDrawer = true"
      />
    </div>

    <!-- 手机端：更多菜单半屏弹窗 -->
    <el-drawer
      v-model="showMoreDrawer"
      direction="btt"
      size="70%"
      :modal="true"
      :show-close="true"
      title="更多"
    >
      <OrderPanel @use-quick-reply="handleQuickReply" />
    </el-drawer>

    <!-- 输入框 -->
    <div v-if="!isAdmin" class="input-area">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="3"
        :placeholder="placeholderText"
        :disabled="isAdmin"
        @keydown="handleKeyDown"
        resize="none"
      />
      <el-button
        type="primary"
        class="send-button"
        :disabled="isAdmin || !inputMessage.trim()"
        @click="sendMessage"
      >
        {{ sendButtonText }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import { ElMessage } from 'element-plus'
import { Folder, Picture, MoreFilled } from '@element-plus/icons-vue'
import OrderPanel from './OrderPanel.vue'
import api from '@/api/chat'
import { filterSensitiveWords } from '@/utils'

const chatStore = useChatStore()
const inputMessage = ref('')
const showMoreDrawer = ref(false)

// 检查当前用户是否是管理员（只读权限）
const isAdmin = computed(() => chatStore.currentUser.role === 'admin')

// 响应式判断是否为手机端
const isMobile = ref(window.innerWidth < 768)
const handleResize = () => {
  isMobile.value = window.innerWidth < 768
}
window.addEventListener('resize', handleResize)

// 组件卸载时清理事件监听器
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 根据设备类型显示不同的提示文字
const placeholderText = computed(() => {
  if (isAdmin.value) return '管理员无法发送消息'
  return isMobile.value ? '请输入消息' : '按 Ctrl+Enter 快捷发送'
})

const sendButtonText = computed(() => {
  return isMobile.value ? '发送' : '发送 Enter'
})

// 暴露方法供外部调用
function setInputMessage(content) {
  inputMessage.value = content
}

// 处理快捷消息（手机端弹窗使用）
function handleQuickReply(content) {
  inputMessage.value = content
  showMoreDrawer.value = false // 关闭弹窗
}

defineExpose({
  setInputMessage
})

async function sendMessage() {
  if (!inputMessage.value.trim()) return

  // 过滤敏感词
  const originalText = inputMessage.value
  const filteredText = filterSensitiveWords(originalText)
  
  // 如果内容被过滤，提示用户
  if (filteredText !== originalText) {
    ElMessage.warning('消息中包含敏感词，已自动过滤')
  }
  
  // ✅ 立即清空输入框（乐观更新，提升响应速度）
  inputMessage.value = ''
  
  // 异步发送消息（不阻塞 UI）
  chatStore.sendMessage(filteredText, 'text')
}

function handleKeyDown(event) {
  if (event.ctrlKey && event.key === 'Enter') {
    event.preventDefault()
    sendMessage()
  }
}

async function handleImageUpload(file) {
  try {
    const result = await api.uploadImage(file)
    await chatStore.sendMessage(result.url, 'image')
    ElMessage.success('图片发送成功')
  } catch (error) {
    ElMessage.error('图片上传失败')
    console.error(error)
  }
  return false // 阻止默认上传行为
}

async function handleFileUpload(file) {
  try {
    const result = await api.uploadFile(file)
    await chatStore.sendMessage(`${result.filename}|${result.url}`, 'file')
    ElMessage.success('文件发送成功')
  } catch (error) {
    ElMessage.error('文件上传失败')
    console.error(error)
  }
  return false // 阻止默认上传行为
}
</script>

<style scoped>
.message-input-container {
  background-color: white;
  border-top: 1px solid #e4e7ed;
}

.admin-readonly-notice {
  padding: 12px 16px;
}

.toolbar {
  padding: 8px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
}

.toolbar-left {
  display: flex;
  gap: 4px;
}

.more-button {
  font-size: 20px;
  padding: 8px;
  color: #606266;
}

.more-button:hover {
  color: #409eff;
}

.input-area {
  padding: 12px 16px;
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-area :deep(.el-textarea) {
  flex: 1;
}

.input-area :deep(.el-textarea__inner) {
  border: none;
  box-shadow: none;
  padding: 0;
  font-size: 14px;
}

.input-area :deep(.el-textarea__inner:focus) {
  outline: none;
}

.send-button {
  height: 36px;
}

/* ==================== 响应式媒体查询 ==================== */

/* 手机端 (<768px) */
@media (max-width: 767px) {
  .toolbar {
    padding: 6px 12px;
  }
  
  .input-area {
    padding: 10px 12px;
    gap: 10px;
  }
  
  .input-area :deep(.el-textarea__inner) {
    font-size: 15px; /* 手机端字体稍大，更易输入 */
  }
  
  .send-button {
    height: 38px;
    padding: 0 16px;
  }
}

/* 手机端更多菜单弹窗样式 */
:deep(.el-drawer__body) {
  padding: 0;
  overflow-y: auto;
}

:deep(.el-drawer__header) {
  margin-bottom: 0;
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}
</style>
