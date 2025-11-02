# 环境变量配置说明

## 快速开始

### 1. 创建环境配置文件

项目根目录已包含 `.env.example` 模板文件。首次运行项目时，请复制该文件：

```bash
# 在 backend 目录下执行
cp .env.example .env
```

### 2. 修改配置（可选）

根据你的实际需求修改 `.env` 文件中的配置值。

---

## 环境变量详解

### 数据库配置

#### `DATABASE_URL`
- **说明**：数据库连接地址
- **默认值**：`sqlite+aiosqlite:///./live_chat.sqlite`
- **示例**：
  - SQLite：`sqlite+aiosqlite:///./live_chat.sqlite`
  - MySQL：`mysql+aiomysql://user:password@localhost/dbname`
  - PostgreSQL：`postgresql+asyncpg://user:password@localhost/dbname`

#### `DEBUG_SQL`
- **说明**：是否在控制台打印 SQL 查询语句（调试用）
- **默认值**：`False`
- **可选值**：`True` / `False`

---

### JWT 认证配置

#### `JWT_SECRET_KEY`
- **说明**：JWT Token 加密密钥
- **默认值**：`your-secret-key-here-please-change-in-production-09a8f7e6d5c4b3a2`
- **重要**：⚠️ 生产环境必须修改为随机的安全字符串
- **生成方式**：
  ```python
  import secrets
  print(secrets.token_urlsafe(32))
  ```

#### `JWT_ALGORITHM`
- **说明**：JWT 加密算法
- **默认值**：`HS256`
- **可选值**：`HS256`, `HS384`, `HS512`
- **推荐**：使用默认值 `HS256`

#### `JWT_ACCESS_TOKEN_EXPIRE_DAYS`
- **说明**：JWT Token 过期时间（天数）
- **默认值**：`7`（7天）
- **示例**：
  - `1` - 1天（每天需要重新登录）
  - `7` - 7天（一周）
  - `30` - 30天（一个月）

---

### 服务器配置

#### `HOST`
- **说明**：服务器监听地址
- **默认值**：`0.0.0.0`（监听所有网卡）
- **示例**：
  - `0.0.0.0` - 允许外部访问
  - `127.0.0.1` - 仅本地访问

#### `PORT`
- **说明**：服务器监听端口
- **默认值**：`8000`
- **示例**：`8000`, `8080`, `3000`

#### `RELOAD`
- **说明**：代码修改后是否自动重载（开发模式）
- **默认值**：`True`
- **可选值**：`True` / `False`
- **注意**：生产环境建议设置为 `False`

#### `DEBUG`
- **说明**：调试模式开关，控制错误信息的详细程度
- **默认值**：`False`
- **可选值**：`True` / `False`
- **作用**：
  - `True`：错误响应包含详细的异常信息和堆栈跟踪（仅开发环境）
  - `False`：错误响应只返回通用错误信息（生产环境推荐）
- **安全提示**：⚠️ 生产环境必须设置为 `False`，避免泄露敏感信息

#### `BASE_URL`
- **说明**：应用的基础 URL，用于拼接完整的静态资源访问地址
- **默认值**：`http://localhost:8000`
- **示例**：
  - 开发环境：`http://localhost:8000`
  - 生产环境：`https://api.yourdomain.com`
  - 使用 CDN：`https://cdn.yourdomain.com`
- **用途**：
  - 拼接用户头像完整 URL
  - 拼接上传文件完整 URL
  - 数据库只存储相对路径（如 `/media/avatar.png`）
  - 接口返回时自动拼接为完整 URL（如 `https://cdn.yourdomain.com/media/avatar.png`）

---

### CORS 跨域配置

#### `CORS_ORIGINS`
- **说明**：允许跨域访问的前端地址列表
- **默认值**：`http://localhost:5173,http://localhost:3000`
- **格式**：多个地址用英文逗号分隔，不要有空格
- **示例**：
  ```
  CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://example.com
  ```

---

### 媒体文件配置

#### `MEDIA_DIR`
- **说明**：媒体文件根目录，包含用户上传的文件和默认资源
- **默认值**：`media`
- **示例**：`media`, `static/media`, `/data/media`
- **目录结构**：
  ```
  media/
  ├── avatars/           # 默认头像（提交到 Git）
  └── uploads/           # 用户上传的文件（按日期存储）
      └── {年}/{月}/{日}/  # 自动创建，如 2025/11/02/
  ```
- **注意**：
  - 相对路径相对于项目根目录
  - 用户上传的文件按日期自动组织：`uploads/{年}/{月}/{日}/`
  - 默认头像存放在 `avatars/` 子目录
  - 目录会自动创建，无需手动创建

#### `MAX_FILE_SIZE`
- **说明**：单个文件上传的最大大小（字节）
- **默认值**：`10485760`（10 MB）
- **计算方式**：
  - 1 MB = 1048576 字节
  - 10 MB = 10485760 字节
  - 50 MB = 52428800 字节

---

### 应用配置

#### `APP_TITLE`
- **说明**：应用标题（显示在 API 文档中）
- **默认值**：`在线客服系统`

#### `APP_DESCRIPTION`
- **说明**：应用描述（显示在 API 文档中）
- **默认值**：`基于FastAPI和WebSocket的实时在线客服系统`

#### `APP_VERSION`
- **说明**：应用版本号
- **默认值**：`1.0.0`

---

## 不同环境的配置示例

### 开发环境 (.env.development)

```env
DATABASE_URL=sqlite+aiosqlite:///./live_chat_dev.db
HOST=0.0.0.0
PORT=8000
RELOAD=True
DEBUG=True
BASE_URL=http://localhost:8000
DEBUG_SQL=True
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
MEDIA_DIR=media
MAX_FILE_SIZE=10485760
```

### 生产环境 (.env.production)

```env
DATABASE_URL=postgresql+asyncpg://user:password@db-server/live_chat_prod
HOST=0.0.0.0
PORT=80
RELOAD=False
DEBUG=False
BASE_URL=https://api.yourdomain.com
DEBUG_SQL=False
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
MEDIA_DIR=/data/media
MAX_FILE_SIZE=5242880
```

---

## 注意事项

1. **安全性**
   - ⚠️ `.env` 文件包含敏感信息，已被 `.gitignore` 排除
   - ⚠️ 不要将 `.env` 文件提交到版本控制系统
   - ⚠️ 不要在 `.env` 文件中存储明文密码（生产环境）

2. **环境变量优先级**
   - 系统环境变量 > `.env` 文件
   - 如果系统已设置同名环境变量，将优先使用系统的值

3. **修改配置后**
   - 需要重启后端服务才能生效
   - 如果启用了 `RELOAD=True`，部分配置可能自动重载

4. **团队协作**
   - `.env.example` 应该提交到 Git 供团队成员参考
   - 每个开发者维护自己的 `.env` 文件
   - 修改 `.env.example` 时，记得通知团队成员同步更新

---

## 故障排查

### 问题：找不到 .env 文件

**解决方案**：
```bash
cd backend
cp .env.example .env
```

### 问题：环境变量没有生效

**检查清单**：
1. 确认 `.env` 文件在 `backend` 目录下
2. 确认环境变量名拼写正确
3. 重启后端服务
4. 检查是否有同名的系统环境变量

### 问题：上传文件失败

**检查清单**：
1. 确认 `MEDIA_DIR` 目录存在且有写入权限
2. 确认文件大小未超过 `MAX_FILE_SIZE` 限制
3. 检查文件类型是否在允许列表中
4. 确认 `media/avatars/` 目录存在（用于默认头像）
5. 检查日期目录（如 `media/uploads/2025/11/02/`）的写入权限

---

## 查看当前配置

访问 API 文档查看当前应用配置：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

在文档页面的标题和描述部分会显示 `APP_TITLE` 和 `APP_DESCRIPTION` 的值。

