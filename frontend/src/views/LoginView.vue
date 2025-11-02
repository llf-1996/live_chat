<template>
  <div class="login-container">
    <!-- 装饰性背景圆圈 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <div class="login-box">
      <!-- Logo 区域 -->
      <div class="login-header">
        <div class="logo-wrapper">
          <el-icon :size="48" class="logo-icon">
            <ChatDotRound />
          </el-icon>
        </div>
        <h1 class="login-title">客服后台管理</h1>
        <p class="login-subtitle">Live Chat Admin System</p>
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
            <span v-if="!loading">登 录</span>
            <span v-else>登录中...</span>
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <el-icon class="info-icon"><InfoFilled /></el-icon>
        <p class="footer-text">首次使用请联系技术人员创建管理员账号</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { User, Lock, ChatDotRound, InfoFilled } from '@element-plus/icons-vue'
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
/* ==================== 容器布局 ==================== */
.login-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%);
  padding: 20px;
  overflow: hidden;
}

/* ==================== 装饰性背景 ==================== */
.bg-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  overflow: hidden;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  animation: float 20s infinite ease-in-out;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  right: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: -80px;
  left: -80px;
  animation-delay: 5s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  left: -75px;
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  33% {
    transform: translateY(-20px) rotate(5deg);
  }
  66% {
    transform: translateY(10px) rotate(-5deg);
  }
}

/* ==================== 登录框 ==================== */
.login-box {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 440px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15),
              0 0 1px rgba(0, 0, 0, 0.1);
  padding: 48px 40px;
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ==================== 头部区域 ==================== */
.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 20px;
  margin-bottom: 24px;
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 12px 32px rgba(59, 130, 246, 0.4);
  }
}

.logo-icon {
  color: white;
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
  letter-spacing: 0.5px;
}

.login-subtitle {
  font-size: 13px;
  color: #64748b;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 500;
}

/* ==================== 表单 ==================== */
.login-form {
  margin-top: 0;
}

.login-form .el-form-item {
  margin-bottom: 24px;
}

.login-form .error-message {
  margin-bottom: 20px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s;
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  transition: all 0.3s;
}

.login-button:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
}

.login-button:active {
  transform: translateY(0);
}

/* ==================== 底部提示 ==================== */
.login-footer {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
  text-align: center;
}

.info-icon {
  font-size: 20px;
  color: #3b82f6;
  margin-bottom: 12px;
}

.footer-text {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  line-height: 1.6;
}

/* ==================== 响应式 ==================== */
@media (max-width: 768px) {
  .login-container {
    padding: 16px;
  }

  .login-box {
    padding: 36px 24px;
  }

  .logo-wrapper {
    width: 70px;
    height: 70px;
  }

  .logo-icon {
    font-size: 40px !important;
  }

  .login-title {
    font-size: 24px;
  }

  .login-subtitle {
    font-size: 12px;
  }

  .circle-1 {
    width: 200px;
    height: 200px;
  }

  .circle-2 {
    width: 150px;
    height: 150px;
  }

  .circle-3 {
    display: none;
  }
}
</style>

