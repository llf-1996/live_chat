#!/bin/bash
set -e
echo "======================================"
echo "  Live Chat Backend Startup Script"
echo "======================================"
# 1. 创建日志目录
echo "[1/4] 创建日志目录..."
mkdir -p /var/log/backend/gunicorn/pid
# 2. 安装依赖
echo "[2/4] 安装 Python 依赖..."
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
# 3. 数据库迁移
echo "[3/4] 应用数据库迁移..."
# alembic upgrade head 会自动判断：
# - 如果是全新数据库 → 创建所有表
# - 如果已是最新版本 → 不做任何操作
# - 如果版本落后 → 执行必要的升级
alembic upgrade head
# 4. 启动 Gunicorn 服务
echo "[4/4] 启动 Gunicorn + Uvicorn 服务..."
echo "配置文件: deploy/gunicorn.conf.py"
echo "Worker 类型: uvicorn.workers.UvicornWorker"
# 使用配置文件启动
gunicorn main:app -c deploy/gunicorn.conf.py