# 在线客服系统

基于 FastAPI + SQLite + Vue3 + WebSocket 的实时在线客服系统

## 🚀 快速访问

启动服务后，使用以下链接快速体验：

| 角色 | 访问链接 | 用户ID | 说明 |
|------|---------|--------|------|
| 买家 | `http://localhost:5173/chat?user_id=b1` | b1 | 浏览商户、发起咨询 |
| 商户 | `http://localhost:5173/chat?user_id=m1` | m1 | 接待客户、回复咨询 |
| 官方客服 | `http://localhost:5173/chat?user_id=p1` | p1 | 官方客服 |
| 管理员 | `http://localhost:5173/admin?user_id=a1` | a1 | 客服后台管理（仅限管理员） |

**用户ID规则：** `b{数字}`买家、`m{数字}`商户、`a{数字}`管理员、`p{数字}`官方客服

## 功能特性

- ✅ 多角色支持（买家、商户、官方客服、管理员）
- ✅ 实时消息推送（WebSocket 一对一精准推送）
- ✅ **用户在线/离线状态**（实时更新，绿点/灰点显示）
- ✅ 平台管理员实时监控（只读权限）
- ✅ 双通道设计（HTTP 持久化 + WebSocket 实时推送）
- ✅ **JWT 管理员登录认证**（7天免登录）
- ✅ **全局异常处理**（友好的错误提示，避免 500 错误）
- ✅ 文件和图片上传
- ✅ 快捷消息功能
- ✅ 历史订单展示
- ✅ 前端路由分离（`/chat`、`/admin`、`/login`）
- ✅ 未读消息计数和红点提示
- ✅ 自动创建会话（`target` 参数）
- ✅ RESTful API 规范
- ✅ 命令行创建管理员工具

## 📸 界面预览

### 管理员登录
<img src="docs/screenshots/login.png" alt="管理员登录页面" width="800">

### 买家视图


### 商户视图


### 管理员视图





## 技术栈

**后端：** Python 3.11 + FastAPI + SQLite + SQLAlchemy + WebSocket  
**前端：** Vue 3 + Vue Router + Vite + Element Plus + Pinia + Axios

## 快速开始

### 1. 环境配置

首次启动前，需要配置环境变量：

```bash
cd backend
# 复制环境变量模板
cp .env.example .env

# （可选）根据需要修改 .env 中的配置
# 默认配置已可直接使用
```

**主要配置项：**
- `DATABASE_URL` - 数据库连接地址（默认 SQLite）
- `PORT` - 后端服务端口（默认 8000）
- `BASE_URL` - 应用基础 URL，用于拼接静态资源完整地址（默认 `http://localhost:8000`）
- `CORS_ORIGINS` - 前端跨域白名单
- `MAX_FILE_SIZE` - 文件上传大小限制（默认 10MB）
- `JWT_SECRET_KEY` - JWT 密钥（⚠️ 生产环境必须修改）
- `JWT_ACCESS_TOKEN_EXPIRE_DAYS` - Token 过期时间（默认 7 天）

> 📖 详细配置说明请查看：[backend/ENV_README.md](backend/ENV_README.md)

### 2. 创建管理员账号

使用命令行工具创建初始管理员账号：

```bash
cd backend
# 格式：python create_admin.py <用户ID> <用户名> <密码>
python create_admin.py a1 supderadmin supderadmin123
```

或交互式创建：

```bash
cd backend
python create_admin.py
```

输出示例：
```
创建管理员账号...
用户ID: admin001
用户名: admin
密码: ********
管理员账号创建成功！

现在可以使用该账号登录客服后台：
   http://localhost:5173/login
```

### 3. 启动服务

```bash
# 后端
cd backend
pip install -r requirements.txt
python main.py

# 前端（新终端）
cd frontend
npm install
npm run dev
```

**访问地址：**
- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 路由系统

| 路由 | 适用角色 | 说明 |
|------|---------|------|
| `/` | 所有 | 自动重定向到 `/chat` |
| `/chat` | 买家、商户、官方客服 | 聊天界面（URL 参数：`user_id`） |
| `/login` | 管理员 | 管理员登录页面 |
| `/admin` | 仅管理员 | 客服后台管理（需要先登录） |

**参数说明：**
- `user_id`：必需，当前登录用户ID
- `target`：可选，自动打开与指定用户的对话（不存在时自动创建）

**示例：**
```bash
# 买家咨询商户（自动创建会话）
http://localhost:5173/chat?user_id=b1&target=m1
```

## 测试用户

| 用户ID | 用户名 | 角色 | 访问方式 | 说明 |
|--------|--------|------|---------|------|
| admin | 系统管理员 | 管理员 | `/login` 登录 | 需使用命令行工具创建 |
| p1 | 官方客服 | 商家 | `?user_id=p1` | 官方客服 |
| b1 | 药师09685 | 客户 | `?user_id=b1` | 普通买家 |
| m1-m9 | 各商户 | 商家 | `?user_id=m1` | 9个测试商户 |

**注意：** 管理员账号需要使用 `python create_admin.py` 命令创建，其他用户通过 URL 参数访问。

## API 规范

### RESTful 响应格式

**列表接口：**
```json
{
  "count": 123,      // 总记录数
  "results": [...]   // 结果列表
}
```

**单个资源：**
```json
{
  "id": "b1",
  "username": "买家1",
  ...
}
```

### 分页参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `page` | int | 1 | 页码（从1开始） |
| `page_size` | int | 20/50 | 每页记录数 |

### 静态资源 URL 处理

**存储与返回机制：**
- **数据库存储**：相对路径（如 `/media/avatar.png`）
- **API 返回**：完整 URL（如 `http://localhost:8000/media/avatar.png`）
- **配置方式**：通过环境变量 `BASE_URL` 配置基础域名

**适用范围：**
- ✅ 用户头像（`avatar` 字段）
- ✅ 图片消息（`message_type: "image"` 的 `content` 字段）
- ✅ 文件消息（`message_type: "file"` 的 `content` 字段）
- ✅ 上传接口返回的 URL

**优势：**
- ✅ 前端无需关心静态资源域名
- ✅ 支持 CDN 部署（修改 `BASE_URL` 即可）
- ✅ 数据库迁移友好（不存储硬编码域名）

**示例：**
```json
// GET /api/users/b1 返回
{
  "id": "b1",
  "username": "买家1",
  "avatar": "http://localhost:8000/media/avatars/buyer.png",  // 自动拼接完整 URL
  ...
}

// GET /api/conversations/1/messages 返回
{
  "results": [
    {
      "id": 123,
      "content": "http://localhost:8000/media/photo_1730505600.jpg",  // 图片消息自动拼接
      "message_type": "image",
      ...
    },
    {
      "id": 124,
      "content": "你好",  // 文本消息保持不变
      "message_type": "text",
      ...
    }
  ]
}
```

**配置：**
```env
# 开发环境
BASE_URL=http://localhost:8000

# 生产环境
BASE_URL=https://api.yourdomain.com

# 使用 CDN
BASE_URL=https://cdn.yourdomain.com
```

### 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/users/` | 获取用户列表 |
| GET | `/api/conversations/` | 获取会话列表 |
| GET | `/api/conversations/{id}/messages` | 获取会话消息（支持 `order` 排序） |
| POST | `/api/messages/` | 发送消息 |
| GET | `/api/quick-replies/user/{id}` | 获取快捷消息 |
| POST | `/api/upload/image` | 上传图片（返回完整 URL） |
| WS | `/ws/{user_id}` | WebSocket 连接 |

**完整接口列表：** http://localhost:8000/docs

## 消息推送机制

### 双通道设计

1. **HTTP 接口**：保存消息到数据库（持久化存储）
2. **WebSocket**：实时推送消息给在线用户（即时推送）

### 推送逻辑

- 买家发送 → 推送给商户 + 所有在线管理员
- 商户回复 → 推送给买家 + 所有在线管理员
- 管理员只能接收，无法发送（只读监控）

## 项目结构

```
live_chat/
├── backend/
│   ├── app/
│   │   ├── routers/          # API 路由
│   │   ├── models.py         # 数据库模型
│   │   ├── schemas.py        # Pydantic 模型
│   │   ├── database.py       # 数据库配置
│   │   └── websocket.py      # WebSocket 管理
│   ├── main.py               # FastAPI 主程序
│   ├── requirements.txt      # Python 依赖
│   ├── .env.example          # 环境变量模板
│   ├── .env                  # 环境变量配置（本地）
│   └── ENV_README.md         # 环境变量配置文档
└── frontend/
    ├── src/
    │   ├── views/            # 页面视图（ChatView, AdminView）
    │   ├── components/       # Vue 组件
    │   ├── router/           # 路由配置
    │   ├── stores/           # Pinia stores
    │   └── api/              # API 封装
    ├── package.json
    └── vite.config.js
```

## 环境变量配置

项目使用 `.env` 文件管理配置，支持以下环境变量：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./live_chat.db` | 数据库连接地址 |
| `HOST` | `0.0.0.0` | 服务器监听地址 |
| `PORT` | `8000` | 服务器端口 |
| `RELOAD` | `True` | 开发模式热重载 |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | 跨域白名单 |
| `MEDIA_DIR` | `media` | 媒体文件目录 |
| `MAX_FILE_SIZE` | `10485760` | 最大文件大小（10MB） |
| `DEBUG_SQL` | `False` | 显示 SQL 日志 |
| **`JWT_SECRET_KEY`** | **见配置文件** | **JWT 密钥（生产环境必须修改）** |
| **`JWT_ALGORITHM`** | **`HS256`** | **JWT 加密算法** |
| **`JWT_ACCESS_TOKEN_EXPIRE_DAYS`** | **`7`** | **Token 过期时间（天）** |

**配置步骤：**
```bash
cd backend
cp .env.example .env
# 根据需要修改 .env 中的值
```

**详细文档：** [backend/ENV_README.md](backend/ENV_README.md)

## 常见问题

### Q: 如何切换不同角色？
A: 通过 URL 参数 `user_id` 切换：
- 买家：`/chat?user_id=b1`
- 商户：`/chat?user_id=m1`
- 管理员：`/admin?user_id=a1`

### Q: 如何测试实时消息？
A: 打开两个浏览器窗口，使用不同的 `user_id`：
```bash
# 窗口1（买家）
http://localhost:5173/chat?user_id=b1&target=m1

# 窗口2（商户）
http://localhost:5173/chat?user_id=m1&target=b1
```
双方发送的消息会实时互相推送。

### Q: 如何创建管理员账号？
A: 使用命令行工具（需要提供用户ID、用户名、密码）：
```bash
cd backend
python create_admin.py a1 supderadmin supderadmin123
```
或交互式创建：
```bash
python create_admin.py
```

### Q: 忘记管理员密码怎么办？
A: 使用 `change_password.py` 脚本修改密码：
```bash
cd backend
# 格式：python change_password.py <用户ID> <新密码>
python change_password.py a1 admin123

# 或交互式修改（会隐藏密码输入）
python change_password.py
```

### Q: 管理员登录失败？
A: 检查：
1. 管理员账号是否已创建
2. 用户名和密码是否正确
3. Token 是否过期（默认 7 天）
4. 浏览器是否支持 localStorage

### Q: 首次运行缺少 .env 文件？
A: 执行以下命令创建配置文件：
```bash
cd backend
cp .env.example .env
```

### Q: 如何修改服务器端口？
A: 编辑 `backend/.env` 文件，修改 `PORT` 的值，然后重启服务。

### Q: 用户ID不存在会怎样？
A: 显示"访问受限"提示页面，不暴露用户是否存在的信息。

### Q: 为什么用户ID是字符串？
A: 
- 可读性强（`b1`、`m1` 一眼识别）
- 扩展性好（支持UUID等格式）
- 安全性高（不暴露用户数量）

### Q: 时间字段为什么用时间戳？
A: Unix时间戳（整数）性能更优、存储更小、跨平台兼容。

### Q: WebSocket 连接失败？
A: 确保后端服务运行正常，检查防火墙设置。

### Q: 数据库需要重置？
A: 删除 `backend/live_chat.db` 文件，重启后端即可。

### Q: 上传文件失败？
A: 检查 `MAX_FILE_SIZE` 配置，默认限制 10MB。可在 `.env` 中调整。

## 管理员登录系统

### 功能特性

- 🔐 **JWT 认证**：基于 JSON Web Token 的安全认证
- 🔒 **密码加密**：使用 bcrypt_sha256 加密存储密码
- ⏰ **长期登录**：Token 有效期 7 天（可配置）
- 🚀 **自动跳转**：登录成功自动跳转到客服后台
- 🛡️ **路由守卫**：未登录自动重定向到登录页
- 💻 **命令行工具**：创建管理员账号、修改用户密码

### 使用流程

1. **创建管理员账号**
   ```bash
   cd backend
   # 格式：python create_admin.py <用户ID> <用户名> <密码>
   python create_admin.py admin001 admin admin123
   
   # 或交互式创建（会隐藏密码输入）
   python create_admin.py
   ```

2. **修改密码（可选）**
   ```bash
   cd backend
   # 格式：python change_password.py <用户ID> <新密码>
   python change_password.py a1 admin123
   
   # 或交互式修改（会隐藏密码输入）
   python change_password.py
   ```

3. **访问登录页面**
   ```
   http://localhost:5173/login
   ```

4. **输入用户名和密码**
   - 用户名：admin
   - 密码：admin123

5. **登录成功**
   - 自动跳转到客服后台
   - Token 保存在 localStorage
   - 7 天内无需重复登录

5. **退出登录**
   - 点击左侧菜单底部的"退出登录"按钮

### 安全性

- ✅ 密码使用 bcrypt_sha256 加密存储（更安全，无长度限制）
- ✅ JWT Token 有过期时间
- ✅ 使用环境变量配置密钥
- ✅ 登录失败不暴露用户信息
- ✅ Token 验证失败自动跳转登录页

## 更新日志

### 2025-11-02

- ✅ **用户在线/离线状态系统**
  - 实时追踪用户在线状态（WebSocket 连接/断开监听）
  - 用户头像显示在线状态指示器（绿点：在线 / 灰点：离线）
  - 聊天窗口顶部显示对方在线状态
  - 管理员视图显示双方在线状态
  - 自动广播状态变更（上线/离线）
  - 响应式状态更新（Vue 3 Proxy）
- ✅ **JWT 管理员登录系统**
  - 登录页面和认证流程
  - JWT Token 生成和验证（使用 `bcrypt_sha256`，无密码长度限制）
  - 路由守卫保护管理页面
  - 命令行工具创建管理员
  - 密码加密存储
- ✅ **全局异常处理系统**
  - 捕获所有未处理的异常，避免 500 错误
  - 请求参数验证错误处理（422）
  - 数据库异常处理（唯一性约束、外键约束等）
  - 业务逻辑异常处理
  - 详细的错误日志记录
  - 开发/生产环境错误信息分级（`DEBUG` 配置）
- ✅ **静态资源 URL 智能处理**
  - 数据库存储相对路径
  - API 返回完整 URL（支持 CDN 配置）
  - `BASE_URL` 环境变量控制域名
  - 上传文件自动拼接完整 URL
  - 消息中的图片/文件 URL 自动拼接（HTTP + WebSocket）
- ✅ **会话列表消息显示优化**
  - 图片消息显示为 `[图片]`（不显示 URL 路径）
  - 文件消息显示为 `[文件]`（不显示文件路径）
  - 文本消息显示实际内容（最多100字符）
- ✅ **文件上传优化**
  - 保留原始文件名（格式：`原文件名_时间戳.扩展名`）
  - 按日期目录存储（格式：`media/uploads/{年}/{月}/{日}/`）
  - 重构上传代码，提取公共函数
  - 统一挂载点从 `/uploads` 改为 `/media`
- ✅ 环境变量配置系统（支持 `.env` 文件）
- ✅ 创建 `.env.example` 模板文件
- ✅ 详细的环境变量配置文档（`ENV_README.md`）
- ✅ 所有配置项可通过环境变量自定义
- ✅ 支持动态配置数据库、端口、CORS 等

### 2025-11-01

- ✅ 实现前端路由分离（`/chat` 和 `/admin`）
- ✅ 客服后台权限控制（仅管理员访问）
- ✅ 自动创建会话功能（`target` 参数）
- ✅ 用户ID字符串化（`b1`、`m1`、`a1`、`p1`）
- ✅ RESTful API 规范化（`{ count, results }` 格式）
- ✅ 分页参数标准化（`page` + `page_size`）
- ✅ API 接口整合优化

## 待优化功能

- [ ] 用户认证和登录系统
- [ ] 群聊功能
- [ ] 消息撤回
- [ ] 表情包支持
- [ ] 语音消息
- [ ] 视频通话
- [ ] 消息搜索
- [ ] 数据统计和报表
- [ ] 移动端适配
