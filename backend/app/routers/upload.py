from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from typing import Tuple
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from ..schemas import UploadResponse
from ..utils import build_full_url

# 加载环境变量
load_dotenv()

router = APIRouter(prefix="/api/upload", tags=["upload"])

# 媒体文件目录（从环境变量读取）
media_dir_str = os.getenv("MEDIA_DIR")
if media_dir_str is None:
    raise ValueError("MEDIA_DIR 环境变量未设置，请在 .env 文件中配置")
MEDIA_DIR = Path(media_dir_str)
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# 允许的文件类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_FILE_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain"
}

# 最大文件大小（从环境变量读取）
max_file_size_str = os.getenv("MAX_FILE_SIZE")
if max_file_size_str is None:
    raise ValueError("MAX_FILE_SIZE 环境变量未设置，请在 .env 文件中配置")
MAX_FILE_SIZE = int(max_file_size_str)


async def _save_uploaded_file(file: UploadFile, allowed_types: set) -> Tuple[str, str]:
    """
    通用文件上传处理函数
    
    Args:
        file: 上传的文件对象
        allowed_types: 允许的文件类型集合
        
    Returns:
        tuple: (文件访问URL, 文件名)
        
    Raises:
        HTTPException: 文件类型不合法或文件过大
    """
    # 验证文件类型
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # 读取文件内容
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    # 获取当前日期
    now = datetime.now()
    year = now.strftime("%Y")   # 4位年份
    month = now.strftime("%m")  # 2位月份
    day = now.strftime("%d")    # 2位日期
    
    # 创建日期目录结构：media/uploads/{年}/{月}/{日}/
    date_dir = MEDIA_DIR / "uploads" / year / month / day
    date_dir.mkdir(parents=True, exist_ok=True)

    # 生成唯一文件名（保留原文件名 + 时间戳）
    original_name = Path(file.filename).stem  # 文件名（不含扩展名）
    file_extension = Path(file.filename).suffix  # 扩展名
    timestamp = int(time.time())  # 秒级时间戳
    filename = f"{original_name}_{timestamp}{file_extension}"
    file_path = date_dir / filename

    # 保存文件
    with open(file_path, "wb") as f:
        f.write(contents)

    # 返回完整 URL
    relative_path = f"/media/uploads/{year}/{month}/{day}/{filename}"
    full_url = build_full_url(relative_path)
    return full_url, file.filename


@router.post("/image", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """上传图片"""
    url, original_filename = await _save_uploaded_file(file, ALLOWED_IMAGE_TYPES)
    return UploadResponse(
        url=url,
        filename=original_filename,
        file_type="image"
    )


@router.post("/file", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """上传文件（支持图片和文档）"""
    all_allowed_types = ALLOWED_IMAGE_TYPES | ALLOWED_FILE_TYPES
    url, original_filename = await _save_uploaded_file(file, all_allowed_types)
    return UploadResponse(
        url=url,
        filename=original_filename,
        file_type="file"
    )
