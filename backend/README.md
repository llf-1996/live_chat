# 后端技术文档

在线客服系统后端，基于 FastAPI 构建的异步 Web 服务。

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.11+ | 编程语言 |
| **FastAPI** | 0.120+ | Web 框架 |
| **MySQL** | 5.7+ / 8.0+ | 数据库 |
| **SQLAlchemy** | 2.0+ | 异步 ORM |
| **Alembic** | 1.12+ | 数据库迁移 |
| **Uvicorn** | 0.38+ | ASGI 服务器 |
| **python-jose** | 3.3+ | JWT 认证 |
| **passlib** | 1.7+ | 密码哈希 |

## 📋 环境要求

- **Python 3.11+**
- **MySQL 5.7+** 或 **MySQL 8.0+**

## 📁 目录结构

```
backend/
├── app/
│   ├── routers/          # API 路由
│   ├── models.py         # 数据库模型
│   ├── schemas.py        # Pydantic 模型
│   ├── database.py       # 数据库配置
│   ├── auth.py           # JWT 认证
│   ├── websocket.py      # WebSocket 管理
│   └── exceptions.py     # 异常处理
├── alembic/              # 数据库迁移
├── main.py               # 应用入口
├── requirements.txt      # 依赖
└── .env                  # 环境变量
```

## ⚙️ 环境变量配置

### ⚠️ 重要

**所有配置必需，无默认值！配置缺失时抛出 `ValueError`。**

使用 `is None` 判断（不用 `if not value`），因为 `"False"`, `"0"`, `""` 都是有效值。

```python
# ✅ 正确
value = os.getenv("DATABASE_URL")
if value is None:
    raise ValueError("DATABASE_URL 环境变量未设置")
```

### 配置项（16项）

#### 数据库
- **DATABASE_URL**: `mysql+aiomysql://用户:密码@主机:端口/数据库`
- **DEBUG_SQL**: `True`/`False`（生产环境 False）

#### JWT 认证
- **JWT_SECRET_KEY**: 加密密钥（生产环境用 `secrets.token_urlsafe(64)` 生成）
- **JWT_ALGORITHM**: `HS256`
- **JWT_ACCESS_TOKEN_EXPIRE_DAYS**: `7`

#### 服务器
- **HOST**: `0.0.0.0`（监听所有）或 `127.0.0.1`（仅本地）
- **PORT**: `11075`
- **RELOAD**: `True`（开发，代码修改自动重载）/`False`（生产，必须！）
- **DEBUG**: `True`（开发）/`False`（生产，必须！）
- **BASE_URL**: `http://localhost:11075` 或 `https://api.yourdomain.com`

#### CORS
- **CORS_ORIGINS**: `http://localhost:5173,http://localhost:3000`（逗号分隔，无空格）

#### 文件上传
- **MEDIA_DIR**: `media`
- **MAX_FILE_SIZE**: `10485760`（10MB = 10485760 字节）

#### 应用信息
- **APP_TITLE**: `在线客服系统`
- **APP_DESCRIPTION**: `基于FastAPI和WebSocket的实时在线客服系统`
- **APP_VERSION**: `1.0.0`

### 配置示例

**开发环境（.env）**
```env
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/chat
DEBUG_SQL=False
JWT_SECRET_KEY=dev-secret-key-please-change
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_DAYS=7
HOST=0.0.0.0
PORT=11075
RELOAD=True
DEBUG=True
BASE_URL=http://localhost:11075
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
MEDIA_DIR=media
MAX_FILE_SIZE=10485760
APP_TITLE=在线客服系统
APP_DESCRIPTION=基于FastAPI和WebSocket的实时在线客服系统
APP_VERSION=1.0.0
```

**生产环境：** `RELOAD=False`, `DEBUG=False`, `DEBUG_SQL=False`, `JWT_SECRET_KEY` 用强密钥

## 🚀 启动方式

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 初始化数据库
```bash
# 生成迁移
alembic revision --autogenerate -m "init"
# 应用迁移
alembic upgrade head
```

### 3. 创建管理员
```bash
python create_admin.py
```

### 4. 启动服务
```bash
python main.py
# 访问: http://localhost:11075
```

## 📡 API 规范

### RESTful 风格

- 资源名称用复数：`/users/`, `/conversations/`, `/messages/`
- HTTP 方法：GET（查询）、POST（创建）、PUT（更新）、DELETE（删除）

### 响应格式

**列表接口：**
```json
{
  "count": 100,
  "results": [...]
}
```

**单个资源：** 直接返回对象  
**错误：** `{"detail": "错误信息"}`

### 分页参数

- `page`: 页码（从1开始）
- `page_size`: 每页记录数（默认20）
- 计算 skip: `skip = (page - 1) * page_size`

## 🗄️ 数据库设计

### 核心模型

**User（用户表）**
- `id`: String(50)，格式 `{角色首字母}{数字}`（b1, m1, a1, p1）
- `username`: 用户名
- `role`: 角色（buyer/merchant/admin/service）
- `password_hash`: 密码哈希（可选）

**Conversation（会话表）**
- `id`: String(50)
- `customer_id`: 客户ID
- `merchant_id`: 商户ID
- `created_at`: Unix 时间戳

**Message（消息表）**
- `id`: String(50)
- `conversation_id`: 会话ID
- `sender_id`: 发送者ID
- `content`: 消息内容
- `message_type`: 类型（text/image/file）
- `created_at`: Unix 时间戳

**QuickReply（快捷回复表）**
- `id`: String(50)
- `user_id`: 用户ID
- `content`: 回复内容

### 关系
- User ←→ Conversation: customer/merchant 关系
- Conversation ←→ Message: 一对多
- User ←→ Message: sender 关系

## 📊 数据库迁移管理

### 常用命令

```bash
# 生成迁移文件（自动检测模型变化）
alembic revision --autogenerate -m "描述变更"

# 应用迁移
alembic upgrade head

# 回退一个版本
alembic downgrade -1

# 查看历史
alembic history

# 查看当前版本
alembic current
```

### 工作流程

1. **修改模型** (`app/models.py`)
2. **生成迁移**: `alembic revision --autogenerate -m "add field"`
3. **检查迁移文件** (`alembic/versions/`)
4. **应用迁移**: `alembic upgrade head`
5. **更新 Pydantic schema**

### 生产环境

⚠️ **迁移前务必备份数据库！**

```bash
# 备份
mysqldump -u用户 -p 数据库名 > backup.sql

# 应用迁移
alembic upgrade head
```

## 🔌 WebSocket 说明

### 连接管理

```python
# WebSocket 连接: ws://localhost:11075/ws/{user_id}
active_connections: Dict[str, WebSocket]  # user_id → WebSocket
admin_users: Set[str]  # 管理员ID集合
```

### 消息格式

```json
{
  "id": "msg_123",
  "conversation_id": "conv_456",
  "sender_id": "b1",
  "content": "消息内容",
  "message_type": "text",
  "created_at": 1730000000
}
```

### 推送规则

1. 买家发送 → 推送给商户 + 所有在线管理员
2. 商户发送 → 推送给买家 + 所有在线管理员
3. 管理员只读，不能发送

## 🛡️ 异常处理

### DEBUG 模式控制

```python
# DEBUG=True（开发环境）
{
  "detail": "服务器内部错误",
  "error_type": "ValueError",
  "error_message": "具体错误",
  "traceback": [...]
}

# DEBUG=False（生产环境）
{
  "detail": "服务器内部错误，请稍后重试",
  "error_type": "internal_error"
}
```

## 🔧 开发指南

### 添加新API

1. 在 `app/routers/` 创建路由文件
2. 定义 Pydantic schema (`app/schemas.py`)
3. 列表接口使用 `PaginatedResponse[T]`
4. 在 `main.py` 注册路由

### 修改数据库模型

1. 修改 `app/models.py`
2. 生成迁移: `alembic revision --autogenerate -m "描述"`
3. 检查迁移文件
4. 应用迁移: `alembic upgrade head`
5. 更新 schema

### 添加环境变量

1. 在 `.env` 和 `.env.example` 添加配置
2. 在代码中验证:
   ```python
   VALUE = os.getenv("NEW_VAR")
   if VALUE is None:
       raise ValueError("NEW_VAR 环境变量未设置")
   ```

## 🐛 常见问题

**Q: MySQL 连接失败？**  
检查：MySQL 运行、数据库已创建、用户权限、防火墙、配置正确

**Q: Event loop closed 错误？**  
应用关闭时添加: `await engine.dispose()`

**Q: 多进程端口冲突？**  
原因：后台启动多个进程导致端口被占用  
解决：检查并清理占用端口的进程
```bash
# 查看占用端口的进程
netstat -ano | findstr :11075
# 停止进程
taskkill /F /PID <进程ID>
```

**Q: 环境变量未生效？**  
1. 确认 `.env` 在 `backend` 目录
2. 检查拼写
3. 重启服务
4. 检查系统环境变量

**Q: 如何部署到生产？**
1. `DEBUG=False`
2. `DEBUG_SQL=False`
3. `JWT_SECRET_KEY` 用强密钥
4. 使用 Gunicorn:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:11075
   ```

## 📄 开源协议

本项目采用 MIT 协议开源。
