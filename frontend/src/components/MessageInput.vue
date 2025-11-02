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

    <!-- 输入框 -->
    <div v-if="!isAdmin" class="input-area">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="3"
        :placeholder="isAdmin ? '管理员无法发送消息' : '按 Ctrl+Enter 快捷发送'"
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
        发送 Enter
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useChatStore } from '../stores/chat'
import { ElMessage } from 'element-plus'
import { Folder, Picture } from '@element-plus/icons-vue'
import api from '../api/chat'

const chatStore = useChatStore()
const inputMessage = ref('')

// 检查当前用户是否是管理员（只读权限）
const isAdmin = computed(() => chatStore.currentUser.role === 'admin')

// 暴露方法供外部调用
function setInputMessage(content) {
  inputMessage.value = content
}

defineExpose({
  setInputMessage
})

async function sendMessage() {
  if (!inputMessage.value.trim()) return

  await chatStore.sendMessage(inputMessage.value, 'text')
  inputMessage.value = ''
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
  gap: 4px;
  border-bottom: 1px solid #f0f0f0;
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
</style>
