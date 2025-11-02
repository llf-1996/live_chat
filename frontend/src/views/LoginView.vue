<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1 class="login-title">客服后台登录</h1>
        <p class="login-subtitle">在线客服系统</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item v-if="errorMessage" class="error-message">
          <el-alert :title="errorMessage" type="error" :closable="false" show-icon />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <p>提示：只有管理员可以登录此页面</p>
        <p>如需创建管理员账号，请使用命令行工具</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

// 表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 4, message: '密码长度至少为 4 位', trigger: 'blur' }
  ]
}

// 表单引用
const loginFormRef = ref(null)
const loading = ref(false)
const errorMessage = ref('')

// 处理登录
async function handleLogin() {
  if (!loginFormRef.value) return

  // 验证表单
  const valid = await loginFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  errorMessage.value = ''

  try {
    const result = await authStore.login(loginForm.username, loginForm.password)

    if (result.success) {
      ElMessage.success('登录成功')
      
      // 跳转到管理页面
      router.push('/admin')
    } else {
      errorMessage.value = result.message
    }
  } catch (error) {
    console.error('登录错误:', error)
    errorMessage.value = '登录失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 挂载时检查是否已登录
onMounted(async () => {
  if (authStore.isAuthenticated) {
    // 已登录，直接跳转到管理页面
    router.replace('/admin')
  }
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-box {
  width: 100%;
  max-width: 420px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 40px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.login-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.login-form {
  margin-top: 0;
}

.login-form .el-form-item {
  margin-bottom: 24px;
}

.login-form .error-message {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
}

.login-footer {
  margin-top: 30px;
  text-align: center;
  font-size: 13px;
  color: #909399;
  line-height: 1.6;
}

.login-footer p {
  margin: 4px 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .login-box {
    padding: 30px 20px;
  }

  .login-title {
    font-size: 24px;
  }
}
</style>

