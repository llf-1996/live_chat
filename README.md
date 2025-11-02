# 在线客服系统

基于 FastAPI + SQLite + Vue3 + WebSocket 的实时在线客服系统，支持多角色实时沟通，响应式设计适配手机/平板/桌面。

## ✨ 核心特性

- 🎯 **多角色系统** - 买家、商户、官方客服、管理员
- 💬 **实时通信** - WebSocket 双通道（持久化 + 实时推送）
- 🟢 **在线状态** - 实时显示用户在线/离线
- 🔐 **JWT 认证** - 管理员登录系统（7天免登录）
- 📱 **响应式设计** - 完美适配手机/平板/桌面
- 📎 **文件上传** - 支持图片和文件（按日期存储）
- ⚡ **快捷回复** - 商户快捷消息模板
- 🛡️ **异常处理** - 全局友好错误提示

## 📸 界面预览

### 客服后台管理
#### 登录
<img src="docs/screenshots/login.png" alt="管理员登录页面" width="800">

#### 首页
<img src="docs/screenshots/admin_index.png" alt="客服后台管理页面" width="800">

### 聊天界面（桌面端）
<img src="docs/screenshots/chat_pc.png" alt="桌面端聊天界面" width="800">

### 移动端适配
<img src="docs/screenshots/chat_mobile.png" alt="移动端聊天界面" width="280">

<img src="docs/screenshots/chat_mobile_2.png" alt="移动端聊天界面" width="280">

## 🛠️ 技术栈

**后端：** Python 3.11 + FastAPI + SQLite + SQLAlchemy + WebSocket  
**前端：** Vue 3 + Vite + Element Plus + Pinia

## 🚀 快速开始

### 环境要求
- **Python** 3.11+
- **Node.js** 20+
- **pnpm** 8+ （推荐）

安装 pnpm：
```bash
npm install -g pnpm
```

### 1. 配置环境（首次运行）

```bash
cd backend
cp .env.example .env
# 默认配置可直接使用，生产环境需修改 JWT_SECRET_KEY
```

> 📖 详细配置说明：[backend/ENV_README.md](backend/ENV_README.md)


### 2. 创建管理员账号

```bash
cd backend
python create_admin.py a1 admin admin123
```

### 3. 启动服务

```bash
# 后端
cd backend
pip install -r requirements.txt
python main.py

# 前端（新终端）
cd frontend
pnpm install
pnpm dev
```

**访问：**
- 前端：http://localhost:5173
- API 文档：http://localhost:8000/docs（Swagger UI）
- API 文档：http://localhost:8000/redoc（ReDoc）


## 🚀 快速访问

| 角色 | 访问链接 | 用户名 |
|------|---------|--------|
| 买家 | `http://localhost:5173/chat?user_id=b1` | 保安堂药房 |
| 商户 | `http://localhost:5173/chat?user_id=m1` | 保和堂医药集团 |
| 官方客服 | `http://localhost:5173/chat?user_id=p1` | 官方客服 |
| 管理员 | `http://localhost:5173/login` | 需先创建账号 |


## 📌 使用说明

### 内置用户

系统启动时会自动创建以下测试用户：

**管理员**
| 用户ID | 用户名 | 访问方式 |
|--------|--------|---------|
| a1, a2 | admin | 通过 `/login` 登录（需先创建账号） |

**买家**
| 用户ID | 用户名 | 说明 |
|--------|--------|------|
| b1 | 保安堂药房 | 传统药房 |
| b2 | 异世界药局 | 现代连锁药局 |

**商户**
| 用户ID | 用户名 | 说明 |
|--------|--------|------|
| m1 | 保和堂医药集团 | 大型医药集团 |
| m2 | 阿纳斯蒂制药 | 神经科学药企 |
| m3 | 梅迪西斯制药 | 天然植物药厂 |

**官方客服**
| 用户ID | 用户名 | 说明 |
|--------|--------|------|
| p1 | 官方客服 | 平台客服 |

### URL 参数
- `user_id`：必需，当前用户ID
- `target`：可选，自动打开指定会话（不存在时自动创建）

### 示例
```bash
# 买家咨询商户（自动创建会话）
http://localhost:5173/chat?user_id=b1&target=m1

# 商户接待客户
http://localhost:5173/chat?user_id=m1

# 管理员登录后台
http://localhost:5173/login
```

## 📚 技术要点

### API 规范
- **列表格式**：`{ count: 总数, results: [...] }`
- **分页参数**：`page` 和 `page_size`
- **静态资源**：数据库存相对路径，API 返完整 URL（通过 `BASE_URL` 配置）

### 消息推送
- **双通道**：HTTP 持久化 + WebSocket 实时推送
- **推送逻辑**：买家/商户互推，管理员只读监控
- **在线状态**：WebSocket 连接管理，实时广播

### 环境变量
- **配置文件**：`.env`（从 `.env.example` 复制）
- **关键配置**：`DATABASE_URL`、`BASE_URL`、`JWT_SECRET_KEY`
- **详细文档**：[backend/ENV_README.md](backend/ENV_README.md)

## ❓ 常见问题

**Q: 如何创建/修改管理员密码？**  
```bash
python create_admin.py a1 admin admin123      # 创建
python change_password.py a1 new_password     # 修改
```

**Q: 如何测试实时消息？**  
打开两个窗口，分别访问 `?user_id=b1` 和 `?user_id=m1`，双方发送消息会实时互推。

**Q: 数据库如何重置？**  
删除 `backend/live_chat.db` 文件，重启后端即可自动重建。

**Q: 如何修改配置？**  
编辑 `backend/.env` 文件，重启服务生效。详见 [ENV_README.md](backend/ENV_README.md)。

## 📅 更新日志

**2025-11-02**
- ✅ 响应式设计（手机/平板/桌面全适配）
- ✅ 用户在线/离线状态系统
- ✅ JWT 管理员登录认证
- ✅ 全局异常处理
- ✅ 文件上传优化（日期目录 + 原名保留）
- ✅ 静态资源 URL 智能处理（CDN 支持）
- ✅ 环境变量配置系统

**2025-11-01**
- ✅ 前端路由分离（`/chat` 和 `/admin`）
- ✅ RESTful API 规范化
- ✅ 用户ID字符串化
- ✅ 自动创建会话功能

## 🔮 待优化

- [ ] 历史订单
- [ ] 买家/商户注册登录
- [ ] 群聊功能
- [ ] 消息撤回/搜索
- [ ] 表情包/语音/视频
- [ ] 数据统计报表
- [ ] 原生移动端 App
