# 后端技术文档

基于 FastAPI + MySQL + WebSocket 的异步后端服务。

## 🛠️ 技术栈

Python 3.11+ | FastAPI | MySQL + aiomysql | SQLAlchemy (异步) | Alembic | Uvicorn | JWT

## ⚙️ 环境变量（16项必需）

**⚠️ 所有配置必需，无默认值！使用 `is None` 验证（`"False"`, `"0"`, `""` 都是有效值）**

```env
# 数据库（2项）
DATABASE_URL=mysql+aiomysql://user:pass@host:port/db
DEBUG_SQL=False

# JWT认证（3项）
JWT_SECRET_KEY=your-secret-key-min-64-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_DAYS=7

# 服务器（5项）
HOST=0.0.0.0
PORT=11075
RELOAD=True              # 开发: True, 生产: False
DEBUG=True               # 开发: True, 生产: False
BASE_URL=http://localhost:11075

# CORS（1项）
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# 文件上传（2项）
MEDIA_DIR=media
MAX_FILE_SIZE=10485760   # 10MB

# 应用信息（3项）
APP_TITLE=在线客服系统
APP_DESCRIPTION=基于FastAPI和WebSocket的实时在线客服系统
APP_VERSION=1.0.0
```

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，配置所有16项

# 3. 初始化数据库
alembic upgrade head

# 4. 创建管理员
python create_admin.py

# 5. 启动服务
python main.py
```

访问：
- API 文档: http://localhost:11075/api/docs
- 健康检查: http://localhost:11075/api/health

## 📁 目录结构

```
backend/
├── app/
│   ├── routers/          # API 路由
│   │   ├── auth.py       # 认证
│   │   ├── users.py      # 用户管理
│   │   ├── conversations.py  # 会话
│   │   ├── messages.py   # 消息
│   │   ├── quick_replies.py  # 快捷回复
│   │   └── upload.py     # 文件上传
│   ├── models.py         # 数据库模型
│   ├── schemas.py        # Pydantic 模型
│   ├── database.py       # 数据库配置
│   ├── auth.py           # JWT 工具
│   ├── websocket.py      # WebSocket 管理
│   └── exceptions.py     # 异常处理
├── alembic/              # 数据库迁移
├── media/                # 静态文件
├── main.py               # 应用入口
└── .env                  # 环境变量
```

## 📊 数据库

### 模型

- **User**: 用户（买家、商户、客服、管理员）
- **Conversation**: 会话
- **Message**: 消息
- **QuickReply**: 快捷回复

### 迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

## 🔌 API 路径规范

**所有接口在 `/api` 路径下：**

- `/api/auth/` - 认证（登录、验证）
- `/api/users/` - 用户管理
  - `POST /api/users/ensure` - 批量创建/更新用户（测试用）
- `/api/conversations/` - 会话管理
- `/api/messages/` - 消息管理
- `/api/quick-replies/` - 快捷回复
- `/api/upload/` - 文件上传
- `/api/ws/{user_id}` - WebSocket 连接
- `/api/media/*` - 静态文件

### 批量用户创建接口

**用于测试环境快速创建用户：**

```python
# 批量创建/更新用户
POST /api/users/ensure
{
  "users": [
    {
      "id": "b1",
      "role": "buyer",
      "username": "买家1",      # 可选，留空自动生成
      "avatar": "/path/to/avatar",  # 可选，留空使用默认头像
      "description": "用户描述"  # 可选
    },
    {
      "id": "m2",
      "role": "merchant"
    }
  ]
}
→ 返回创建/更新的用户列表

# 特性：
# - 用户已存在时自动跳过
# - 自动生成默认用户名（使用时间戳，如买家1730812345678）
# - 自动随机分配默认头像（buyer1/buyer2, merchant1/merchant2）
# - 无需查询数据库，性能更优
```

## 🔐 认证流程

```python
# 1. 登录获取 token
POST /api/auth/login
{ "username": "admin", "password": "admin123" }
→ { "access_token": "...", "user": {...} }

# 2. 请求携带 token
GET /api/users/
Headers: { "Authorization": "Bearer {token}" }
```

## 🌐 生产部署

### 1. Gunicorn 启动

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:11075 \
  --daemon
```

### 2. Nginx 配置

```nginx
# WebSocket 升级配置
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    # ⚠️ 静态文件必须在 /api/ 之前
    location /api/media/ {
        alias /path/to/backend/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # API 接口（包括 WebSocket）
    location /api/ {
        proxy_pass http://127.0.0.1:11075;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        
        # 传递客户端信息（必需）
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
        
        # 缓冲设置（避免参数丢失）
        proxy_buffering off;
        proxy_request_buffering off;
    }
}
```

**关键点：**
- 静态文件由 Nginx 直接提供（性能提升 10-100 倍）
- WebSocket 需要 HTTP/1.1 和 Upgrade 头
- `proxy_pass` 末尾不加 `/`（保留完整路径）
- 必须配置 `X-Forwarded-*` 头（传递客户端信息）
- 关闭缓冲（`proxy_buffering off`）避免参数丢失

### 3. systemd 服务

```bash
# /etc/systemd/system/chat-backend.service
[Unit]
Description=Chat Backend
After=network.target mysql.service

[Service]
User=www-data
WorkingDirectory=/path/to/backend
ExecStart=/path/to/gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:11075
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🐛 常见问题

**Q: 启动失败 `ValueError: XXX 环境变量未设置`？**  
检查 `.env` 文件，确保所有 16 项配置都已设置。

**Q: MySQL 连接失败？**  
检查：MySQL 服务运行、DATABASE_URL 格式、用户权限、防火墙。

**Q: 多个进程端口冲突？**  
清理占用端口的进程：
```bash
# Windows
netstat -ano | findstr :11075
taskkill /F /PID <PID>

# Linux
lsof -ti:11075 | xargs kill -9
```

**Q: WebSocket 502 Bad Gateway？**  
检查 Nginx 配置中 `map $http_upgrade` 和 `proxy_set_header Upgrade`。

**Q: Nginx 代理后请求参数丢失？**  
必须配置以下代理头：
```nginx
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_buffering off;              # 避免大请求体丢失
proxy_request_buffering off;      # 避免参数丢失
```

**Q: 静态文件 404？**  
1. Nginx 配置中 `/api/media/` 必须在 `/api/` 之前
2. 检查 `alias` 路径是否以 `/` 结尾
3. 检查文件权限：`chmod -R 755 media`

## 📄 开源协议

MIT License
