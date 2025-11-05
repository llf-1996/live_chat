<template>
  <div class="test-user-setup">
    <el-card class="header-card">
      <h2>测试用户初始化</h2>
      <p class="subtitle">快速创建测试用户，用于聊天功能测试</p>
    </el-card>

    <el-card class="form-card">
      <!-- 用户列表 -->
      <div class="users-list">
        <div v-for="(user, index) in users" :key="index" class="user-item">
          <div class="user-item-header">
            <el-tag type="primary">用户 {{ index + 1 }}</el-tag>
            <el-button
              v-if="users.length > 2"
              @click="removeUser(index)"
              type="danger"
              size="small"
              plain
            >
              删除
            </el-button>
          </div>

          <el-form label-width="100px" class="user-form">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="用户ID" required>
                  <el-input
                    v-model="user.id"
                    placeholder="如: b1, m2"
                    clearable
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="角色" required>
                  <el-select v-model="user.role" placeholder="请选择角色">
                    <el-option label="买家 (Buyer)" value="buyer" />
                    <el-option label="商家 (Merchant)" value="merchant" />
                    <el-option label="管理员 (Admin)" value="admin" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="用户名">
                  <el-input
                    v-model="user.username"
                    placeholder="留空自动生成"
                    clearable
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="头像URL">
                  <el-input
                    v-model="user.avatar"
                    placeholder="留空使用默认头像，示例: http://localhost:11075/api/media/avatars/user1.png"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="描述">
              <el-input
                v-model="user.description"
                type="textarea"
                :rows="2"
                placeholder="用户描述信息"
              />
            </el-form-item>
          </el-form>
        </div>
      </div>

      <!-- 添加用户按钮 -->
      <el-button @click="addUser" type="primary" plain class="add-user-btn">
        + 添加用户
      </el-button>

      <!-- 快捷操作 -->
      <el-divider>快捷填充</el-divider>
      <div class="quick-actions">
        <el-button @click="quickFillB1M2" type="success" plain>
          b1 (买家) + m2 (商家)
        </el-button>
        <el-button @click="quickFillB2M1" type="success" plain>
          b2 (买家) + m1 (商家)
        </el-button>
        <el-button @click="quickFillMultiple" type="success" plain>
          b1, b2, m1, m2
        </el-button>
      </div>

      <!-- 跳转设置 -->
      <el-divider>创建成功后跳转设置</el-divider>
      <el-form label-width="130px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="当前用户ID">
              <el-select v-model="redirectUserId" placeholder="请选择">
                <el-option
                  v-for="user in users"
                  :key="user.id"
                  :label="`${user.id} (${getRoleName(user.role)})`"
                  :value="user.id"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="聊天对象ID">
              <el-select v-model="redirectTargetUserId" placeholder="请选择">
                <el-option
                  v-for="user in users"
                  :key="user.id"
                  :label="`${user.id} (${getRoleName(user.role)})`"
                  :value="user.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <!-- 提交按钮 -->
      <div class="submit-section">
        <el-button
          @click="handleSubmit"
          :loading="loading"
          :disabled="!isValid"
          type="primary"
          size="large"
        >
          {{ loading ? '创建中...' : '创建用户并打开聊天' }}
        </el-button>

        <el-alert
          v-if="error"
          :title="error"
          type="error"
          :closable="false"
          style="margin-top: 16px"
        />
        <el-alert
          v-if="success"
          :title="success"
          type="success"
          :closable="false"
          style="margin-top: 16px"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api/chat'

// 用户列表
const users = ref([
  { id: 'b1', role: 'buyer', username: '', avatar: '', description: '' },
  { id: 'm2', role: 'merchant', username: '', avatar: '', description: '' }
])

// 跳转设置
const redirectUserId = ref('b1')
const redirectTargetUserId = ref('m2')

// 状态
const loading = ref(false)
const error = ref('')
const success = ref('')

// 验证表单
const isValid = computed(() => {
  return users.value.every(user => user.id && user.role)
})

// 添加用户
const addUser = () => {
  users.value.push({
    id: '',
    role: 'buyer',
    username: '',
    avatar: '',
    description: ''
  })
}

// 删除用户
const removeUser = (index) => {
  users.value.splice(index, 1)
  
  // 更新跳转设置（如果删除的用户是选中的）
  if (!users.value.find(u => u.id === redirectUserId.value)) {
    redirectUserId.value = users.value[0]?.id || ''
  }
  if (!users.value.find(u => u.id === redirectTargetUserId.value)) {
    redirectTargetUserId.value = users.value[1]?.id || ''
  }
}

// 快捷填充
const quickFillB1M2 = () => {
  users.value = [
    { id: 'b1', role: 'buyer', username: '', avatar: '', description: '' },
    { id: 'm2', role: 'merchant', username: '', avatar: '', description: '' }
  ]
  redirectUserId.value = 'b1'
  redirectTargetUserId.value = 'm2'
}

const quickFillB2M1 = () => {
  users.value = [
    { id: 'b2', role: 'buyer', username: '', avatar: '', description: '' },
    { id: 'm1', role: 'merchant', username: '', avatar: '', description: '' }
  ]
  redirectUserId.value = 'b2'
  redirectTargetUserId.value = 'm1'
}

const quickFillMultiple = () => {
  users.value = [
    { id: 'b1', role: 'buyer', username: '', avatar: '', description: '' },
    { id: 'b2', role: 'buyer', username: '', avatar: '', description: '' },
    { id: 'm1', role: 'merchant', username: '', avatar: '', description: '' },
    { id: 'm2', role: 'merchant', username: '', avatar: '', description: '' }
  ]
  redirectUserId.value = 'b1'
  redirectTargetUserId.value = 'm2'
}

// 获取角色名称
const getRoleName = (role) => {
  const roleMap = {
    buyer: '买家',
    merchant: '商家',
    admin: '管理员'
  }
  return roleMap[role] || role
}

// 提交表单
const handleSubmit = async () => {
  if (!isValid.value) {
    error.value = '请填写所有必填字段'
    return
  }

  if (!redirectUserId.value || !redirectTargetUserId.value) {
    error.value = '请设置跳转参数'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    // 过滤掉空字符串字段
    const usersToCreate = users.value.map(user => {
      const userData = {
        id: user.id,
        role: user.role
      }
      
      if (user.username) userData.username = user.username
      if (user.avatar) userData.avatar = user.avatar
      if (user.description) userData.description = user.description
      
      return userData
    })

    // 调用接口创建用户
    const createdUsers = await api.ensureUsers(usersToCreate)
    console.log('用户创建成功:', createdUsers)
    
    // 验证跳转所需的用户是否都创建成功
    const userIds = createdUsers.map(u => u.id)
    if (!userIds.includes(redirectUserId.value)) {
      error.value = `用户 ${redirectUserId.value} 创建失败，请重试`
      return
    }
    if (!userIds.includes(redirectTargetUserId.value)) {
      error.value = `用户 ${redirectTargetUserId.value} 创建失败，请重试`
      return
    }
    
    success.value = '用户创建成功！正在打开聊天页面...'
    ElMessage.success('用户创建成功')
    
    // 延迟打开（增加延迟确保数据库写入完成）
    setTimeout(() => {
      // 构造完整的 URL
      const chatUrl = `/chat?user_id=${redirectUserId.value}&target_user_id=${redirectTargetUserId.value}`
      
      // 在新标签页打开
      window.open(chatUrl, '_blank')
      
      // 停止加载状态
      loading.value = false
      
      // 清空成功消息
      setTimeout(() => {
        success.value = ''
      }, 2000)
    }, 1500)
  } catch (err) {
    console.error('创建用户失败:', err)
    error.value = err.response?.data?.detail || '创建用户失败，请重试'
    ElMessage.error(error.value)
    loading.value = false
  }
}
</script>

<style scoped>
.test-user-setup {
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
}

.header-card h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
}

.subtitle {
  color: #909399;
  margin: 0;
  font-size: 14px;
}

.form-card {
  margin-bottom: 20px;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 20px;
}

.user-item {
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 20px;
  background: #fafafa;
}

.user-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.user-form {
  margin-top: 16px;
}

.add-user-btn {
  width: 100%;
  margin-bottom: 24px;
}

.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.submit-section {
  margin-top: 24px;
  text-align: center;
}

.submit-section .el-button {
  width: 100%;
}
</style>

