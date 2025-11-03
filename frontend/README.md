# 前端技术文档

在线客服系统前端，基于 Vue 3 构建的单页应用（SPA）。

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Vue** | 3.4+ | 渐进式 JavaScript 框架 |
| **Vite** | 5.0+ | 构建工具 |
| **Element Plus** | 2.5+ | UI 组件库 |
| **Pinia** | 2.1+ | 状态管理 |
| **Vue Router** | 4.2+ | 路由管理 |
| **Axios** | 1.6+ | HTTP 客户端 |
| **@element-plus/icons-vue** | 2.3+ | 图标库 |

## 📋 环境要求

- **Node.js 20+**
- **pnpm 8+**（推荐）

## 📁 目录结构

```
frontend/
├── src/
│   ├── api/
│   │   └── chat.js                # API 封装
│   ├── assets/                    # 静态资源
│   ├── components/
│   │   ├── admin/                 # 管理后台组件
│   │   │   ├── AdminDashboard.vue
│   │   │   ├── ConversationManagement.vue
│   │   │   ├── MessageManagement.vue
│   │   │   ├── RealTimeMonitor.vue
│   │   │   └── UserManagement.vue
│   │   ├── BuyerList.vue          # 买家列表（商户视角）
│   │   ├── MerchantList.vue       # 商户列表（买家视角）
│   │   ├── ChatWindow.vue         # 聊天窗口
│   │   ├── MessageInput.vue       # 消息输入框
│   │   └── OrderPanel.vue         # 订单/快捷回复面板
│   ├── router/
│   │   └── index.js               # 路由配置
│   ├── stores/
│   │   ├── auth.js                # 认证状态
│   │   └── chat.js                # 聊天状态
│   ├── views/
│   │   ├── ChatView.vue           # 聊天页面
│   │   ├── AdminView.vue          # 管理后台
│   │   └── LoginView.vue          # 登录页面
│   ├── App.vue                    # 根组件
│   ├── main.js                    # 应用入口
│   └── style.css                  # 全局样式
├── public/                        # 公共资源
├── index.html                     # HTML 模板
├── vite.config.js                 # Vite 配置
├── package.json                   # 依赖配置
└── pnpm-lock.yaml                 # 依赖锁定文件
```

## ⚙️ 配置说明

### Vite 配置

**文件：** `vite.config.js`

```javascript
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'http://localhost:8000',
        ws: true,
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    }
  }
})
```

**说明：**
- `/api`：代理所有 API 请求到后端
- `/ws`：代理 WebSocket 连接
- `/media`：代理静态资源请求

### 包管理器配置

**文件：** `package.json`

```json
{
  "engines": {
    "node": ">=20.0.0",
    "pnpm": ">=8.0.0"
  },
  "packageManager": "pnpm@8.15.0"
}
```

**说明：**
- `engines`：声明 Node.js 和 pnpm 最低版本
- `packageManager`：推荐的包管理器版本

## 🚀 启动方式

### 1. 安装依赖

```bash
# 使用 pnpm（推荐）
pnpm install

# 或使用 npm
npm install
```

### 2. 开发模式

```bash
pnpm dev
# 或
npm run dev
```

访问：http://localhost:5173

### 3. 生产构建

```bash
pnpm build
# 或
npm run build
```

构建产物：`dist/` 目录

### 4. 预览生产构建

```bash
pnpm preview
# 或
npm run preview
```

## 🗺️ 路由说明

### 路由配置

**文件：** `src/router/index.js`

| 路径 | 组件 | 说明 | 权限 |
|------|------|------|------|
| `/chat` | ChatView | 聊天页面 | 买家、商户、客服 |
| `/admin` | AdminView | 管理后台 | 仅管理员 |
| `/login` | LoginView | 登录页面 | 所有人 |

### URL 参数

**聊天页面（`/chat`）：**
- `user_id`（必需）：当前用户ID
- `target`（可选）：目标会话ID，自动打开指定会话

**示例：**
```
http://localhost:5173/chat?user_id=b1&target=m1
```

### 路由守卫

**权限验证：**
```javascript
router.beforeEach((to, from, next) => {
  const userId = to.query.user_id
  
  // 检查 user_id
  if (to.path === '/chat' && !userId) {
    next('/login')
    return
  }
  
  // 检查管理员权限
  if (to.meta.requiresAdmin && userRole !== 'admin') {
    next('/chat')
    return
  }
  
  next()
})
```

## 🧩 组件说明

### 页面组件

#### ChatView.vue - 聊天页面

**功能：**
- 多角色视图切换（买家/商户/客服）
- 响应式布局（手机/平板/桌面）
- WebSocket 连接管理

**响应式断点：**
- 手机端：`< 768px`（单栏 + 底部导航）
- 平板端：`768-1023px`（双栏）
- 桌面端：`≥ 1024px`（三栏）

#### AdminView.vue - 管理后台

**功能：**
- 侧边栏导航
- 多标签页切换
- 数据统计与监控

#### LoginView.vue - 登录页面

**功能：**
- JWT 登录认证
- 表单验证
- 记住登录状态

### 业务组件

#### MerchantList.vue - 商户列表

**作用：** 买家视角，显示已咨询的商户

**功能：**
- 会话列表
- 未读消息数
- 最后一条消息预览
- 在线状态显示

#### BuyerList.vue - 买家列表

**作用：** 商户视角，显示咨询的客户

**功能：**
- 客户列表
- 未读消息数
- 最后一条消息预览
- 在线状态显示

#### ChatWindow.vue - 聊天窗口

**功能：**
- 消息列表展示
- 消息类型渲染（文字/图片/文件）
- 自动滚动到底部
- 消息已读状态

#### MessageInput.vue - 消息输入框

**功能：**
- 文字输入
- 图片上传
- 文件上传
- 快捷回复（手机端弹窗）
- 发送快捷键（桌面端 Ctrl+Enter）

#### OrderPanel.vue - 订单/快捷回复面板

**功能：**
- 商户信息展示
- 快捷回复管理
- 历史订单（待实现）

## 📦 状态管理

### Pinia Stores

#### auth.js - 认证状态

**状态：**
- `token`：JWT Token
- `user`：当前用户信息
- `isAuthenticated`：是否已登录

**方法：**
- `login(username, password)`：登录
- `logout()`：登出
- `checkAuth()`：检查登录状态

#### chat.js - 聊天状态

**状态：**
- `currentUser`：当前用户
- `conversations`：会话列表
- `currentConversation`：当前会话
- `messages`：消息列表
- `onlineUsers`：在线用户集合
- `ws`：WebSocket 连接

**方法：**
- `connectWebSocket(userId, role)`：连接 WebSocket
- `disconnectWebSocket()`：断开连接
- `loadConversations()`：加载会话列表
- `loadMessages(conversationId)`：加载消息列表
- `sendMessage(content, type)`：发送消息
- `markAsRead(conversationId, role)`：标记已读
- `isUserOnline(userId)`：检查用户是否在线

## 🌐 API 调用

### API 封装

**文件：** `src/api/chat.js`

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',  // ← 注意：不要重复 /api
  timeout: 10000,
})

// 请求拦截器
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api
```

### API 调用示例

```javascript
import api from '@/api/chat'

// 获取用户列表
const users = await api.get('/users/', {
  params: { page: 1, page_size: 20 }
})
// 返回：{ count: 100, results: [...] }

// 发送消息
const message = await api.post('/messages/', {
  conversation_id: 'conv_123',
  content: 'Hello',
  message_type: 'text'
})
// 返回：{ id: 'msg_456', ... }
```

**注意事项：**
- ✅ 路径从资源名开始：`/users/`
- ❌ 不要重复 baseURL：`/api/users/`（错误）
- ✅ 列表数据从 `response.results` 获取
- ✅ 总数从 `response.count` 获取

## 📱 响应式设计

### 断点标准

| 设备 | 宽度 | 布局 |
|------|------|------|
| **手机端** | < 768px | 单栏 + 底部导航 |
| **平板端** | 768-1023px | 双栏 |
| **桌面端** | ≥ 1024px | 三栏 |

### 响应式判断

```javascript
import { ref, onMounted, onUnmounted } from 'vue'

const isMobile = ref(window.innerWidth < 768)

const handleResize = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
```

### 移动端优化

**手机端特性：**
- 单栏显示（`activePanel` 控制视图切换）
- 底部导航（2 个按钮：会话/聊天）
- 隐藏键盘快捷键提示
- 半屏弹窗（`el-drawer` direction="btt"）
- 触控友好按钮（最小 44×44px）

**CSS 示例：**
```css
/* 手机端 */
@media (max-width: 767px) {
  .chat-header {
    height: 50px;
    padding: 0 12px;
    font-size: 14px;
  }
  
  .mobile-layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }
}

/* 平板端 */
@media (min-width: 768px) and (max-width: 1023px) {
  .chat-header {
    height: 54px;
    padding: 0 16px;
  }
}

/* 桌面端 */
@media (min-width: 1024px) {
  .chat-header {
    height: 60px;
    padding: 0 20px;
  }
}
```

## 🔌 WebSocket 集成

### 连接管理

**位置：** `src/stores/chat.js`

```javascript
connectWebSocket(userId, role) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.host}/ws/${userId}?role=${role}`
  
  this.ws = new WebSocket(wsUrl)
  
  this.ws.onopen = () => {
    console.log('WebSocket 已连接')
  }
  
  this.ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    this.handleWebSocketMessage(data)
  }
  
  this.ws.onerror = (error) => {
    console.error('WebSocket 错误:', error)
  }
  
  this.ws.onclose = () => {
    console.log('WebSocket 已断开')
  }
}
```

### 消息处理

```javascript
handleWebSocketMessage(data) {
  switch (data.type) {
    case 'message':
      // 新消息
      this.messages.push(data)
      this.updateConversation(data.conversation_id)
      break
      
    case 'status':
      // 在线状态
      if (data.status === 'online') {
        this.onlineUsers.add(data.user_id)
      } else {
        this.onlineUsers.delete(data.user_id)
      }
      break
      
    case 'online_users':
      // 在线用户列表
      this.onlineUsers = new Set(data.users)
      break
  }
}
```

## 🎨 样式规范

### 全局样式

**文件：** `src/style.css`

```css
/* 全屏容器 */
#app {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}
```

### 组件样式

使用 `scoped` CSS：

```vue
<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}
</style>
```

## 🔧 开发指南

### 添加新页面

1. 在 `src/views/` 创建页面组件
2. 在 `src/router/index.js` 添加路由
3. 设置路由元数据（`meta.requiresAdmin` 等）

### 添加新组件

1. 在 `src/components/` 创建组件
2. 使用 Composition API
3. 使用 Pinia 管理状态
4. 支持响应式设计

### 添加新 API

1. 在 `src/api/chat.js` 添加方法
2. 使用封装的 `api` 实例
3. 处理错误和加载状态

## 🚀 生产部署

### 构建项目

```bash
pnpm build
```

### 部署到 Nginx

**Nginx 配置示例：**

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # 前端静态文件
    root /var/www/live_chat/frontend/dist;
    index index.html;
    
    # 前端路由
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # 后端 API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 静态资源
    location /media/ {
        proxy_pass http://localhost:8000/media/;
    }
}
```

## 📚 相关文档

- [后端 API 文档](../backend/README.md)
- [项目规则](../.cursor/rules/project.mdc)
- [Vite 文档](https://vitejs.dev/)
- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [Pinia 文档](https://pinia.vuejs.org/)

## 🐛 常见问题

**Q: API 请求 404？**  
检查 API 路径是否从 `/api` 开始，不要重复 `baseURL`。

**Q: WebSocket 连接失败？**  
检查后端是否启动，检查代理配置是否正确。

**Q: 样式不生效？**  
检查是否使用了 `scoped` CSS，检查选择器优先级。

**Q: 响应式布局异常？**  
检查 CSS 媒体查询断点，检查 `isMobile` 状态是否正确。

**Q: 如何调试？**  
使用浏览器开发者工具（F12），查看 Console、Network、WebSocket 标签。

## 📄 开源协议

本项目采用 MIT 协议开源。

