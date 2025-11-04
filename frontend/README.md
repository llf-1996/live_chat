# 前端技术文档

基于 Vue 3 + Vite + Element Plus 的单页应用（SPA）。

## 🛠️ 技术栈

Vue 3 | Vite | Element Plus | Pinia | Vue Router | Axios | WebSocket

## ⚙️ 环境变量

**⚠️ 只配置服务器地址，不含路径！**

```env
# 开发环境（.env）
VITE_API_BASE_URL=http://localhost:11075    # 不含 /api
VITE_WS_BASE_URL=ws://localhost:11075       # 不含 /api/ws
VITE_PORT=5173

# 生产环境（.env.production）
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_WS_BASE_URL=wss://api.yourdomain.com
```

**原因：** 代码中已配置路径前缀
- HTTP: `baseURL: '/api'` → 请求自动拼接为 `/api/auth/login`
- WebSocket: 代码拼接 `/api/ws/{user_id}`

## 🚀 快速开始

```bash
# 安装依赖
pnpm install

# 配置环境变量
cp .env.example .env
# 编辑 .env

# 开发模式
pnpm dev

# 生产构建
pnpm build

# 预览构建
pnpm preview
```

访问：http://localhost:5173

## 📁 目录结构

```
frontend/
├── src/
│   ├── api/
│   │   └── chat.js          # API 封装（Axios）
│   ├── components/
│   │   ├── admin/           # 管理后台组件
│   │   │   ├── AdminDashboard.vue      # 管理后台主框架
│   │   │   ├── RealTimeMonitor.vue     # 实时监控
│   │   │   ├── UserManagement.vue      # 用户管理
│   │   │   ├── ConversationManagement.vue # 会话管理
│   │   │   ├── MessageManagement.vue   # 消息管理
│   │   │   └── TestUserSetup.vue       # 测试初始化（管理后台版）
│   │   ├── ChatWindow.vue   # 聊天窗口
│   │   ├── MessageInput.vue # 消息输入
│   │   └── ...
│   ├── router/
│   │   └── index.js         # 路由配置
│   ├── stores/
│   │   ├── auth.js          # 认证状态
│   │   └── chat.js          # 聊天状态（WebSocket）
│   ├── views/
│   │   ├── LoginView.vue       # 登录页
│   │   ├── ChatView.vue        # 聊天页
│   │   └── AdminView.vue       # 管理后台
│   ├── App.vue              # 根组件
│   ├── main.js              # 应用入口
│   └── style.css            # 全局样式
├── .env                     # 环境变量
└── vite.config.js           # Vite 配置
```

## 🗺️ 路由说明

| 路径 | 组件 | 参数 | 用途 |
|------|------|------|------|
| `/login` | LoginView | - | 登录页（管理员） |
| `/chat` | ChatView | `user_id`, `target_user_id`(可选) | 聊天页 |
| `/admin` | AdminView | - | 管理后台（需登录） |

**参数说明：**
- `user_id`: 当前用户 ID（必需）
- `target_user_id`: 目标用户 ID（可选，自动创建会话）

**示例：**
```
# 买家与商户对话
/chat?user_id=b1&target_user_id=m1

# 商户查看客户列表
/chat?user_id=m1

# 管理员后台（需登录）
/admin
```

### 🧪 测试初始化功能（管理后台）

测试初始化功能集成在管理后台，提供了快速创建测试用户的能力。

**访问方式：**
1. 访问管理后台：`/admin`（需要登录）
2. 点击左侧"测试初始化"菜单

**功能特性：**
- 动态添加/删除用户表单
- 支持配置：
  - ID：用户标识
  - 角色：buyer/merchant/admin
  - 用户名：可选，留空自动生成
  - 头像URL：可选，留空使用默认头像（示例: http://localhost:11075/api/media/avatars/user1.png）
  - 描述：可选
- 快捷按钮：一键填充常用测试组合
- 自动生成默认用户名（使用时间戳保证唯一性）
- 自动随机分配默认头像（无需查询数据库）
- 创建成功后在新标签页打开聊天页面
- Element Plus 风格，与管理后台统一
- 需要管理员权限

**使用流程：**
1. 登录管理后台
2. 点击左侧"测试初始化"菜单
3. 填写用户信息或点击快捷按钮
4. 设置跳转参数（当前用户 & 聊天对象）
5. 点击"创建用户并打开聊天"
6. 自动创建用户并在新标签页打开聊天页面

**组件：**
- `admin/TestUserSetup.vue` - 管理后台测试初始化组件

**调用的 API：**
```javascript
// src/api/chat.js
api.ensureUsers(users)  // POST /api/users/ensure
```

## 🔌 API 调用

```javascript
// src/api/chat.js
const api = axios.create({
  baseURL: '/api',  // 路径前缀
  timeout: 10000
})

// 自动添加 token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 使用
api.get('/users/')              // → /api/users/
api.post('/messages/', data)    // → /api/messages/
```

## 📊 状态管理（Pinia）

### auth.js - 认证状态

```javascript
const authStore = useAuthStore()

// 登录
await authStore.login('admin', 'password')

// 获取当前用户
await authStore.fetchCurrentUser()

// 登出
authStore.logout()
```

### chat.js - 聊天状态 + WebSocket

```javascript
const chatStore = useChatStore()

// 设置当前用户
chatStore.setCurrentUser(user)

// WebSocket 连接
chatStore.connectWebSocket()  // 自动连接到 /api/ws/{user_id}
chatStore.disconnectWebSocket()

// 发送消息
await chatStore.sendMessage(conversationId, {
  content: '你好',
  content_type: 'text'
})

// 监听消息
watch(() => chatStore.conversations, (newConversations) => {
  // 处理新消息
})
```

## 📱 响应式设计

### 断点

- **手机**: < 768px
- **平板**: 768px - 1023px
- **桌面**: ≥ 1024px

### 布局

| 设备 | 布局 | 交互 |
|------|------|------|
| 手机 | 单栏 + `activePanel` 切换视图 | 触控友好（按钮≥44px） |
| 平板/桌面 | 多栏并列 | 鼠标悬停、快捷键 |

### CSS 示例

```css
/* 手机端 */
@media (max-width: 767px) {
  .chat-container {
    flex-direction: column;
  }
  .user-list {
    display: none;
  }
}

/* 桌面端 */
@media (min-width: 1024px) {
  .chat-container {
    display: grid;
    grid-template-columns: 280px 1fr;
  }
}
```

## 🌐 生产部署

### 构建

```bash
# 使用生产环境变量构建
pnpm build

# 输出到 dist/
# dist/
#   ├── index.html
#   ├── assets/
#   │   ├── index-*.js
#   │   └── index-*.css
#   └── ...
```

### Nginx 配置

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /path/to/frontend/dist;
    index index.html;
    
    # SPA 路由
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # 静态资源缓存
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 🐛 常见问题

**Q: 启动失败 `VITE_API_BASE_URL 环境变量未设置`？**  
检查 `.env` 文件，确保配置了必需的环境变量。

**Q: API 请求 404？**  
检查：
1. `.env` 中 `VITE_API_BASE_URL` 不应包含 `/api`（代码已配置）
2. 后端服务运行在正确端口（11075）
3. Vite 代理配置正确

**Q: WebSocket 连接失败？**  
检查：
1. `.env` 中 `VITE_WS_BASE_URL` 不应包含 `/api/ws`（代码会拼接）
2. 后端 WebSocket 服务运行
3. 用户 ID 有效（不是 null/undefined）

**Q: 打包后路由 404？**  
确保 Nginx 配置了 `try_files $uri $uri/ /index.html`（SPA 路由支持）。

## 📄 开源协议

MIT License
