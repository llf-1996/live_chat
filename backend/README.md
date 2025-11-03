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
| **Pydantic** | 2.12+ | 数据验证 |
| **python-jose** | 3.3+ | JWT 认证 |
| **passlib** | 1.7+ | 密码哈希 |
| **python-dotenv** | 1.0+ | 环境变量 |

## 📋 环境要求

- **Python 3.11+**
- **pip** 或 **pip3**
- **MySQL 5.7+** 或 **MySQL 8.0+**

## 📁 目录结构

```
backend/
├── app/
│   ├── __init__.py                # 应用初始化
│   ├── database.py                # 数据库配置
│   ├── models.py                  # SQLAlchemy 模型
│   ├── schemas.py                 # Pydantic 模型（请求/响应）
│   ├── websocket.py               # WebSocket 连接管理
│   ├── exceptions.py              # 全局异常处理
│   ├── utils/
│   │   └── url_helper.py          # URL 工具函数
│   └── routers/
│       ├── __init__.py
│       ├── users.py               # 用户接口
│       ├── conversations.py       # 会话接口
│       ├── messages.py            # 消息接口
│       ├── quick_replies.py       # 快捷回复接口
│       ├── upload.py              # 文件上传接口
│       └── auth.py                # 认证接口
├── alembic/
│   ├── env.py                     # Alembic 环境配置
│   ├── script.py.mako             # 迁移模板
│   ├── versions/                  # 迁移文件目录
│   │   └── xxx_initial_migration.py
│   └── README                     # Alembic 快速使用
├── media/
│   ├── avatars/                   # 默认头像
│   └── uploads/                   # 用户上传文件
│       └── {year}/{month}/{day}/  # 按日期分类
├── .env.example                   # 环境变量模板
├── alembic.ini                    # Alembic 配置文件
├── main.py                        # 应用入口
├── requirements.txt               # Python 依赖
├── create_admin.py                # 创建管理员脚本
└── change_password.py             # 修改密码脚本
```

## ⚙️ 环境变量配置

### 快速开始

```bash
# 复制环境变量模板
cp .env.example .env
```

### 配置项说明

#### 数据库配置

**DATABASE_URL**
- 说明：数据库连接地址（**必需，无默认值**）
- 格式：`mysql+aiomysql://用户名:密码@主机地址:端口/数据库名`
- 示例：
  - `mysql+aiomysql://root:password@localhost:3306/chat`
  - `mysql+aiomysql://user:pass@192.168.1.100:3306/live_chat`
  - `mysql+aiomysql://yaocai_chat:password@119.45.125.28:11003/chat`

**DEBUG_SQL**
- 说明：是否在控制台打印 SQL 查询语句（调试用）
- 默认值：`False`
- 可选值：`True` / `False`

#### JWT 认证配置

**JWT_SECRET_KEY**
- 说明：JWT Token 加密密钥
- 默认值：`your-secret-key-here-please-change-in-production-09a8f7e6d5c4b3a2`
- ⚠️ 生产环境必须修改为随机的安全字符串
- 生成方式：
  ```python
  import secrets
  print(secrets.token_urlsafe(32))
  ```

**JWT_ALGORITHM**
- 说明：JWT 加密算法
- 默认值：`HS256`
- 推荐：使用默认值

**JWT_ACCESS_TOKEN_EXPIRE_DAYS**
- 说明：JWT Token 过期时间（天数）
- 默认值：`7`（7天）

#### 服务器配置

**HOST**
- 说明：服务器监听地址
- 默认值：`0.0.0.0`（监听所有网卡）
- 示例：
  - `0.0.0.0` - 允许外部访问
  - `127.0.0.1` - 仅本地访问

**PORT**
- 说明：服务器监听端口
- 默认值：`8000`

**RELOAD**
- 说明：代码修改后是否自动重载（开发模式）
- 默认值：`True`
- 注意：生产环境建议设置为 `False`

**DEBUG**
- 说明：调试模式开关，控制错误信息的详细程度
- 默认值：`False`
- 作用：
  - `True`：错误响应包含详细的异常信息和堆栈跟踪（仅开发环境）
  - `False`：错误响应只返回通用错误信息（生产环境推荐）
- ⚠️ 生产环境必须设置为 `False`，避免泄露敏感信息

**BASE_URL**
- 说明：应用的基础 URL，用于拼接完整的静态资源访问地址
- 默认值：`http://localhost:8000`
- 示例：
  - 开发环境：`http://localhost:8000`
  - 生产环境：`https://api.yourdomain.com`
  - 使用 CDN：`https://cdn.yourdomain.com`

#### CORS 跨域配置

**CORS_ORIGINS**
- 说明：允许跨域访问的前端地址列表
- 默认值：`http://localhost:5173,http://localhost:3000`
- 格式：多个地址用英文逗号分隔，不要有空格

#### 媒体文件配置

**MEDIA_DIR**
- 说明：媒体文件根目录
- 默认值：`media`
- 目录结构：
  ```
  media/
  ├── avatars/           # 默认头像
  └── uploads/           # 用户上传的文件
      └── {年}/{月}/{日}/  # 自动创建，如 2025/11/02/
  ```

**MAX_FILE_SIZE**
- 说明：单个文件上传的最大大小（字节）
- 默认值：`10485760`（10 MB）
- 计算方式：1 MB = 1048576 字节

### 不同环境的配置示例

**开发环境：**
```env
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/live_chat_dev
HOST=0.0.0.0
PORT=8000
RELOAD=True
DEBUG=True
BASE_URL=http://localhost:8000
DEBUG_SQL=True
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**生产环境：**
```env
DATABASE_URL=mysql+aiomysql://live_chat:SecurePass123@db-server:3306/live_chat_prod
HOST=0.0.0.0
PORT=80
RELOAD=False
DEBUG=False
BASE_URL=https://api.yourdomain.com
DEBUG_SQL=False
CORS_ORIGINS=https://yourdomain.com
```

## 🚀 启动方式

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
# 应用所有迁移，创建数据库表
alembic upgrade head
```

### 3. 创建管理员账号

```bash
python create_admin.py <user_id> <username> <password>

# 示例
python create_admin.py a1 admin admin123
```

### 4. 启动服务

```bash
python main.py
```

**访问地址：**
- API 服务：http://localhost:8000
- Swagger 文档：http://localhost:8000/docs
- ReDoc 文档：http://localhost:8000/redoc

## 📡 API 规范

### RESTful 风格

- **资源名称**：使用复数（`/users/`, `/conversations/`, `/messages/`）
- **HTTP 方法**：
  - `GET` - 查询
  - `POST` - 创建
  - `PUT` - 更新
  - `DELETE` - 删除

### 响应格式

**列表接口：**
```json
{
  "count": 100,
  "results": [
    {"id": "1", "name": "User 1"},
    {"id": "2", "name": "User 2"}
  ]
}
```

**单个资源：**
```json
{
  "id": "1",
  "name": "User 1",
  "created_at": 1730000000
}
```

**错误响应：**
```json
{
  "detail": "错误信息"
}
```

### 分页参数

- `page`：页码（从 1 开始）
- `page_size`：每页记录数

**示例：**
```
GET /api/users/?page=1&page_size=20
```

### 静态资源 URL

- **数据库存储**：相对路径（如 `/media/avatars/default.png`）
- **API 返回**：完整 URL（如 `http://localhost:8000/media/avatars/default.png`）
- **配置**：通过 `BASE_URL` 环境变量控制

## 🗄️ 数据库设计

### 核心模型

#### User（用户表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String(50) | 主键，格式：{角色首字母}{数字} |
| username | String(100) | 用户名，唯一 |
| password_hash | String(255) | 密码哈希（管理员） |
| role | String(20) | 角色：buyer/merchant/admin/platform |
| avatar | String(500) | 头像 URL |
| created_at | Integer | 创建时间（时间戳） |

#### Conversation（会话表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String(50) | 主键 |
| customer_id | String(50) | 客户ID（买家） |
| merchant_id | String(50) | 商户ID |
| last_message | Text | 最后一条消息 |
| last_message_time | Integer | 最后消息时间 |
| customer_unread | Integer | 客户未读数 |
| merchant_unread | Integer | 商户未读数 |
| created_at | Integer | 创建时间 |
| updated_at | Integer | 更新时间 |

#### Message（消息表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String(50) | 主键 |
| conversation_id | String(50) | 会话ID |
| sender_id | String(50) | 发送者ID |
| content | Text | 消息内容 |
| message_type | String(20) | 类型：text/image/file |
| is_read | Boolean | 是否已读 |
| created_at | Integer | 创建时间 |

#### QuickReply（快捷回复表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String(50) | 主键 |
| user_id | String(50) | 用户ID |
| content | Text | 回复内容 |
| created_at | Integer | 创建时间 |

## 📊 数据库迁移管理

本项目使用 Alembic 进行数据库版本管理，可以自动追踪模型变更并生成迁移脚本。

### 初始化数据库（首次部署）

```bash
# 应用所有迁移，创建数据库表结构
alembic upgrade head
```

**说明：**
- ⚠️ `alembic init` 用于初始化 Alembic 环境（本项目已完成，不需要运行）
- ✅ `alembic upgrade head` 用于初始化数据库表结构（应用迁移文件）

### 常用操作

#### 生成迁移文件

当你修改了 `app/models.py` 中的模型后：

```bash
alembic revision --autogenerate -m "Add user avatar field"
```

**注意：** 生成迁移文件后，请检查 `alembic/versions/` 目录下生成的文件，确认迁移内容正确。

#### 应用迁移

```bash
# 应用所有未执行的迁移
alembic upgrade head

# 应用到指定版本
alembic upgrade <revision_id>
```

#### 回退迁移

```bash
# 回退一个版本
alembic downgrade -1

# 回退到指定版本
alembic downgrade <revision_id>

# 回退到初始状态（清空数据库）
alembic downgrade base
```

#### 查看迁移历史

```bash
# 查看所有迁移历史
alembic history

# 查看当前数据库版本
alembic current

# 查看详细历史
alembic history --verbose
```

### 工作流程示例

#### 场景 1：新增字段

1. 修改 `app/models.py`
   ```python
   class User(Base):
       __tablename__ = "users"
       # ... 其他字段
       avatar = Column(String(500))  # 新增字段
   ```

2. 生成迁移
   ```bash
   alembic revision --autogenerate -m "Add avatar field to User model"
   ```

3. 检查迁移文件
   - 打开 `alembic/versions/` 下最新的文件
   - 确认 `upgrade()` 和 `downgrade()` 函数正确

4. 应用迁移
   ```bash
   alembic upgrade head
   ```

#### 场景 2：重命名字段

Alembic 无法自动检测字段重命名，会当作删除旧字段 + 新增新字段处理。

1. 手动创建迁移文件
   ```bash
   alembic revision -m "Rename user_name to username"
   ```

2. 编辑迁移文件
   ```python
   def upgrade():
       op.alter_column('users', 'user_name', 
                       new_column_name='username')
   
   def downgrade():
       op.alter_column('users', 'username', 
                       new_column_name='user_name')
   ```

3. 应用迁移
   ```bash
   alembic upgrade head
   ```

### Alembic 命令速查表

| 操作 | 命令 | 说明 |
|------|------|------|
| **查看帮助** | `alembic --help` | 显示所有命令 |
| **初始化数据库** | `alembic upgrade head` | ✅ 应用迁移，创建数据库表结构 |
| **生成迁移** | `alembic revision --autogenerate -m "msg"` | 自动检测模型变更 |
| **创建空迁移** | `alembic revision -m "msg"` | 手动编写迁移 |
| **应用迁移** | `alembic upgrade head` | 应用所有迁移 |
| **应用到指定版本** | `alembic upgrade <revision>` | 升级到指定版本 |
| **回退一个版本** | `alembic downgrade -1` | 回退上一个迁移 |
| **回退到指定版本** | `alembic downgrade <revision>` | 回退到指定版本 |
| **回退所有** | `alembic downgrade base` | 清空数据库 |
| **查看当前版本** | `alembic current` | 显示当前数据库版本 |
| **查看历史** | `alembic history` | 显示迁移历史 |
| **详细历史** | `alembic history --verbose` | 显示详细信息 |
| **标记版本** | `alembic stamp head` | 手动标记版本（危险操作）|

### 生产环境部署流程

```bash
# 1. 拉取最新代码
git pull

# 2. 安装/更新依赖
pip install -r requirements.txt

# 3. 备份数据库（建议在 MySQL 中执行）
# mysqldump -u用户名 -p密码 数据库名 > backup_$(date +%Y%m%d_%H%M%S).sql

# 4. 应用迁移
alembic upgrade head

# 5. 重启服务
# systemctl restart live_chat
```

## 🔌 WebSocket 说明

### 连接管理

**连接端点：** `ws://localhost:8000/ws/{user_id}`

**连接参数：**
- `user_id`：用户ID
- `role`（可选）：用户角色（admin 会自动加入监控池）

**示例：**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/b1?role=buyer');
```

### 消息格式

**接收消息：**
```json
{
  "type": "message",
  "conversation_id": "conv_123",
  "sender_id": "m1",
  "content": "你好",
  "message_type": "text",
  "timestamp": 1730000000
}
```

**在线状态通知：**
```json
{
  "type": "status",
  "user_id": "m1",
  "status": "online",
  "timestamp": 1730000000
}
```

**在线用户列表：**
```json
{
  "type": "online_users",
  "users": ["m1", "b1", "b2"],
  "timestamp": 1730000000
}
```

### 推送规则

1. **买家发送消息** → 推送给商户 + 所有在线管理员
2. **商户发送消息** → 推送给买家 + 所有在线管理员
3. **管理员** → 只读监控，不能发送消息

## 🛡️ 异常处理

### 全局异常捕获

系统对以下异常进行全局处理：

| 异常类型 | HTTP 状态码 | 说明 |
|----------|------------|------|
| RequestValidationError | 422 | 请求参数验证失败 |
| SQLAlchemyError | 500 | 数据库操作错误 |
| IntegrityError | 400 | 数据完整性错误（如重复） |
| ValidationError | 400 | Pydantic 验证错误 |
| BusinessException | 400 | 业务逻辑错误 |
| Exception | 500 | 未知错误 |

### 自定义异常

```python
from app.exceptions import BusinessException

# 抛出业务异常
raise BusinessException(status_code=400, detail="用户不存在")
```

## 🔧 开发指南

### 添加新接口

1. 在 `app/routers/` 创建或修改路由文件
2. 定义 Pydantic schema（`app/schemas.py`）
3. 列表接口使用 `PaginatedResponse[T]`
4. 在 `main.py` 注册路由

**示例：**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import PaginatedResponse, UserResponse

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/", response_model=PaginatedResponse[UserResponse])
async def get_users(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    # 业务逻辑
    return PaginatedResponse(count=total, results=users)
```

### 修改数据库模型

1. 修改 `app/models.py`
2. 生成迁移：`alembic revision --autogenerate -m "描述变更"`
3. 检查迁移文件（`alembic/versions/`）
4. 应用迁移：`alembic upgrade head`
5. 更新对应的 Pydantic schema

### WebSocket 扩展

编辑 `app/websocket.py`：

```python
from app.websocket import manager

# 发送给指定用户
await manager.send_to_user(message_dict, user_id)

# 广播给所有人
await manager.broadcast(message_dict)

# 广播在线状态
await manager.broadcast_status(user_id, "online")
```

## 📊 性能优化

### 数据库优化

- 使用索引（已在模型中定义）
- 异步查询（SQLAlchemy AsyncSession）
- 分页查询（避免一次性加载大量数据）

### 静态资源优化

- 配置 CDN（修改 `BASE_URL`）
- 使用 Nginx 作为反向代理
- 启用 Gzip 压缩

### WebSocket 优化

- 连接池管理
- 心跳检测（待实现）
- 断线重连（客户端实现）

## 🐛 常见问题

**Q: 如何切换到 PostgreSQL/MySQL？**  
修改 `.env` 中的 `DATABASE_URL`，例如：
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
```

**Q: 如何启用 SQL 调试日志？**  
修改 `.env`：
```env
DEBUG_SQL=True
```

**Q: 环境变量没有生效？**  
1. 确认 `.env` 文件在 `backend` 目录下
2. 确认环境变量名拼写正确
3. 重启后端服务
4. 检查是否有同名的系统环境变量

**Q: 上传文件失败？**  
1. 确认 `MEDIA_DIR` 目录存在且有写入权限
2. 确认文件大小未超过 `MAX_FILE_SIZE` 限制
3. 检查文件类型是否在允许列表中

**Q: 生成的迁移文件为空？**  
1. 确认 `alembic/env.py` 正确导入了 `Base`
2. 确认模型继承自正确的 `Base`
3. 尝试手动创建迁移：`alembic revision -m "description"`

**Q: MySQL 连接失败怎么办？**  
检查以下几点：
1. MySQL 服务是否正常运行
2. 数据库是否已创建（需手动创建）
3. 用户名、密码、主机地址、端口是否正确
4. 防火墙是否允许访问
5. MySQL 用户是否有足够权限

**Q: 如何部署到生产环境？**  
1. 修改 `.env` 中的 `JWT_SECRET_KEY`
2. 设置 `DEBUG=False`
3. 使用 Gunicorn + Uvicorn：
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📄 开源协议

本项目采用 MIT 协议开源。
