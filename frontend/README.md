# 前端技术文档

在线客服系统前端，基于 Vue 3 构建的单页应用（SPA）。

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Vue** | 3.4+ | 渐进式框架 |
| **Vite** | 5.0+ | 构建工具 |
| **Element Plus** | 2.5+ | UI 组件库 |
| **Pinia** | 2.1+ | 状态管理 |
| **Vue Router** | 4.2+ | 路由管理 |
| **Axios** | 1.6+ | HTTP 客户端 |

## 📋 环境要求

- **Node.js 20+**
- **pnpm 8+**（推荐）

## 📁 目录结构

```
frontend/
├── src/
│   ├── api/              # API 封装
│   ├── components/       # 组件
│   │   ├── admin/        # 管理后台组件
│   │   ├── ChatWindow.vue
│   │   └── MessageInput.vue
│   ├── router/           # 路由配置
│   ├── stores/           # Pinia 状态管理
│   ├── views/            # 页面组件
│   ├── App.vue           # 根组件
│   └── main.js           # 应用入口
├── .env                  # 环境变量
└── vite.config.js        # Vite 配置
```

## ⚙️ 环境变量配置

### ⚠️ 重要

**必需配置，无默认值！** 配置缺失时抛出异常。

```javascript
// 使用 is None 验证
const apiBaseUrl = env.VITE_API_BASE_URL
if (!apiBaseUrl) {
  throw new Error('VITE_API_BASE_URL 环境变量未设置')
}
```

### 配置项

- **VITE_API_BASE_URL**: 后端 API 地址（必需）
- **VITE_WS_BASE_URL**: WebSocket 地址（必需）
- **VITE_PORT**: 开发服务器端口（可选，默认 5173）

### 配置示例

**开发环境（.env）**
```env
VITE_API_BASE_URL=http://localhost:11075
VITE_WS_BASE_URL=ws://localhost:11075
VITE_PORT=5173
```

**生产环境（.env.production）**
```env
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_WS_BASE_URL=wss://api.yourdomain.com
```

## 🚀 启动方式

```bash
# 安装依赖
pnpm install

# 开发模式
pnpm dev

# 生产构建
pnpm build

# 预览构建
pnpm preview
```

访问：http://localhost:5173

## 🗺️ 路由说明

### 路由配置

- `/login` - 登录页面
- `/chat?user_id={id}&target={target_id}` - 聊天页面
- `/admin?user_id={id}` - 管理后台

### URL 参数

- `user_id`: 当前用户ID（必需）
- `target`: 对话目标用户ID（可选，聊天页面）

### 路由守卫

- 检查 `user_id` 参数
- 验证用户有效性
- 管理员页面验证 `role === 'admin'`

## 🧩 组件说明

### 页面组件
- **LoginView**: 登录页面
- **ChatView**: 聊天页面（买家、商户、客服）
- **AdminView**: 管理后台（仅管理员）

### 业务组件
- **ChatWindow**: 聊天窗口（消息列表、文件预览）
- **MessageInput**: 消息输入框（文本、文件、快捷键）
- **BuyerList**: 买家列表（商户视角）
- **MerchantList**: 商户列表（买家视角）
- **OrderPanel**: 订单/快捷回复面板

### 管理后台组件
- **AdminDashboard**: 数据总览
- **UserManagement**: 用户管理
- **ConversationManagement**: 会话管理
- **MessageManagement**: 消息管理
- **RealTimeMonitor**: 实时监控

## 📦 状态管理

### Pinia Stores

**authStore** (`stores/auth.js`)
- 当前用户信息（`currentUser`）
- 用户列表（`users`）
- 方法：`fetchUsers()`, `fetchCurrentUser()`

**chatStore** (`stores/chat.js`)
- 会话列表（`conversations`）
- 消息列表（`messages`）
- WebSocket 连接管理
- 方法：`loadConversations()`, `sendMessage()`, `connectWebSocket()`

## 🌐 API 调用

### API 封装 (`api/chat.js`)

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',  // Vite 代理到后端
  timeout: 10000
})

// 示例
export const getUsers = () => api.get('/users/')
export const sendMessage = (data) => api.post('/messages/', data)
```

### Vite 代理配置

```javascript
// vite.config.js
proxy: {
  '/api': {
    target: VITE_API_BASE_URL,
    changeOrigin: true
  },
  '/ws': {
    target: VITE_WS_BASE_URL,
    ws: true
  }
}
```

## 📱 响应式设计

### 断点标准

- 手机：<768px
- 平板：768-1023px
- 桌面：≥1024px

### 移动端优化

**聊天页面 (ChatView)**
- 单栏布局，通过 `activePanel` 切换视图
- 底部导航：联系人、对话、订单
- 全屏聊天窗口

**管理后台 (AdminView)**
- 折叠侧边栏（汉堡菜单）
- 卡片式布局
- 触控友好（按钮 ≥44×44px）

### 媒体查询示例

```css
/* 桌面端 */
.chat-container {
  display: flex;
}

/* 手机端 */
@media (max-width: 767px) {
  .chat-container {
    display: block;
  }
  .sidebar {
    display: none;
  }
}
```

## 🔌 WebSocket 集成

### 连接管理

```javascript
// stores/chat.js
connectWebSocket() {
  const ws = new WebSocket(`${wsBaseUrl}/ws/${this.userId}`)
  
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data)
    this.handleNewMessage(message)
  }
}
```

### 消息处理

- 收到消息 → 更新 `messages` 列表
- 更新会话 `updated_at` 和 `unread_count`
- 当前对话 → 标记已读
- 播放提示音（可选）

## 🎨 样式规范

### 全局样式 (`style.css`)

- 统一字体、颜色
- 滚动条样式
- Element Plus 主题定制

### 组件样式

- 使用 `scoped` CSS
- BEM 命名规范
- 避免深层嵌套（≤3层）

## 🔧 开发指南

### 添加新页面

1. 在 `views/` 创建组件
2. 在 `router/index.js` 注册路由
3. 添加路由守卫（如需要）

### 添加新组件

1. 在 `components/` 创建组件
2. 使用 Composition API
3. 添加 props 和 emits 类型定义

### 添加新 API

1. 在 `api/chat.js` 添加方法
2. 在 store 中调用
3. 处理错误和加载状态

## 🚀 生产部署

### 构建

```bash
pnpm build
# 输出到 dist/
```

### 部署

**静态文件服务器（Nginx）**
```nginx
server {
  listen 80;
  server_name yourdomain.com;
  root /var/www/live_chat/dist;
  
  location / {
    try_files $uri $uri/ /index.html;
  }
  
  location /api {
    proxy_pass http://backend:11075;
  }
}
```

**环境变量**
- 创建 `.env.production`
- 设置正确的 API 和 WebSocket 地址（HTTPS/WSS）

## 🐛 常见问题

**Q: API 请求失败？**  
检查：后端运行、端口正确、CORS 配置、网络连接

**Q: WebSocket 连接失败？**  
检查：后端 WebSocket 服务、URL 格式（ws:// 或 wss://）、防火墙

**Q: 路由参数丢失？**  
使用 `router.push({ query: { user_id } })` 保留参数

**Q: 样式不生效？**  
检查：scoped 属性、CSS 选择器优先级、Element Plus 主题覆盖

**Q: 生产环境白屏？**  
检查：.env.production 配置、控制台错误、路由 mode、资源路径

## 📄 开源协议

本项目采用 MIT 协议开源。
