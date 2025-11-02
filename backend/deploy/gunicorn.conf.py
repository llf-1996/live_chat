import os

# ==================== 基础配置 ====================

# 监听地址和端口
bind = '0.0.0.0:11010'

# 设置守护进程（False 可以交给 supervisor/systemd 管理）
daemon = False

# 进程命名（方便 ps 命令查看）
proc_name = 'live_chat'

# ==================== Worker 配置 ====================

# 并行工作进程数
# 推荐公式：(CPU核心数 × 2) + 1
# 可根据服务器性能调整，4-8 个 worker 通常足够
workers = 4

# Worker 类型：使用 Uvicorn 的 ASGI Worker（支持 FastAPI 异步特性和 WebSocket）
worker_class = 'uvicorn.workers.UvicornWorker'

# ==================== 超时配置 ====================

# Worker 超时时间（秒）
# 如果请求处理时间超过此值，worker 会被杀死并重启
timeout = 90

# 优雅关闭超时（秒）
# 在重启/停止时，给 worker 处理完现有请求的时间
graceful_timeout = 30

# Keepalive 连接超时
keepalive = 5

# ==================== 性能优化 ====================

# 最大请求数（防止内存泄漏）
# Worker 处理完指定数量的请求后会自动重启
max_requests = 1000
max_requests_jitter = 100  # 随机偏移，避免所有 worker 同时重启

# ==================== 日志配置 ====================

# 设置进程文件目录
pidfile = '/var/log/backend/gunicorn/pid/gunicorn.pid'

# 访问日志（设置为 '-' 输出到 stdout）
accesslog = '/var/log/backend/gunicorn/access.log'
# accesslog = '-'  # 输出到 stdout（推荐用于 Docker/systemd）

# 错误日志（设置为 '-' 输出到 stderr）
errorlog = '/var/log/backend/gunicorn/error.log'
# errorlog = '-'  # 输出到 stderr（推荐用于 Docker/systemd）

# 日志级别：debug, info, warning, error, critical
loglevel = 'info'

# 访问日志格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ==================== 安全配置 ====================

# 限制请求行大小（字节）
limit_request_line = 4096

# 限制请求头字段数量
limit_request_fields = 100

# 限制请求头大小（字节）
limit_request_field_size = 8190

# ==================== 其他配置 ====================

# 预加载应用（节省内存，但不支持热重载）
# preload_app = True

# 临时文件目录
# tmp_upload_dir = '/tmp'

# ==================== 钩子函数 ====================

def on_starting(server):
    """服务器启动时调用"""
    print(f"Gunicorn 正在启动... (PID: {os.getpid()})")

def on_reload(server):
    """重新加载配置时调用"""
    print("Gunicorn 配置已重新加载")

def when_ready(server):
    """服务器准备就绪时调用"""
    print(f"Gunicorn 已就绪，监听 {bind}")

def worker_int(worker):
    """Worker 收到 SIGINT 信号时调用"""
    print(f"Worker {worker.pid} 收到中断信号")

def worker_abort(worker):
    """Worker 异常退出时调用"""
    print(f"Worker {worker.pid} 异常退出")

def post_worker_init(worker):
    """Worker 初始化完成后调用"""
    print(f"Worker {worker.pid} 已启动")
