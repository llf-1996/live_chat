# 前端环境变量配置说明

## 快速配置

复制 `.env.example` 文件为 `.env`：

```bash
cp .env.example .env
```

## 环境变量详解

### `VITE_API_BASE_URL`
- **说明**：后端 API 服务地址
- **默认值**：`http://localhost:8000`
- **开发环境示例**：`http://localhost:8000`
- **生产环境示例**：`https://api.yourdomain.com`

### `VITE_WS_BASE_URL`
- **说明**：WebSocket 服务地址
- **默认值**：`ws://localhost:8000`
- **开发环境示例**：`ws://localhost:8000`
- **生产环境示例**：`wss://api.yourdomain.com`

### `VITE_PORT`
- **说明**：前端开发服务器端口
- **默认值**：`5173`
- **可选值**：任意未被占用的端口号

## 配置示例

### 开发环境 (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_PORT=5173
```

### 生产环境 (.env.production)

```env
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_WS_BASE_URL=wss://api.yourdomain.com
VITE_PORT=5173
```

## 注意事项

1. **环境变量前缀**：Vite 要求客户端环境变量必须以 `VITE_` 开头
2. **重启服务**：修改环境变量后需要重启开发服务器
3. **WebSocket 协议**：
   - 开发环境使用 `ws://`
   - 生产环境（HTTPS）必须使用 `wss://`
4. **代理配置**：开发环境的 API 和 WebSocket 请求会通过 Vite 代理转发到后端服务

## 如何创建 .env 文件

### 方法一：复制示例文件（推荐）

```bash
cd frontend
cp .env.example .env
```

### 方法二：手动创建

在 `frontend/` 目录下创建 `.env` 文件，内容如下：

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_PORT=5173
```

## 验证配置

启动开发服务器后，打开浏览器控制台，应该能看到：

```
WebSocket 连接成功
```

如果看到连接失败，请检查：
1. 后端服务是否启动（http://localhost:8000）
2. 环境变量配置是否正确
3. 端口是否被占用

