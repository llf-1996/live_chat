"""URL 辅助函数"""
import os
from dotenv import load_dotenv

load_dotenv()

# 从环境变量获取基础 URL
BASE_URL = os.getenv("BASE_URL")
if not BASE_URL:
    raise ValueError("BASE_URL 环境变量未设置，请在 .env 文件中配置")


def build_full_url(path: str) -> str:
    """
    将相对路径转换为完整 URL
    
    Args:
        path: 相对路径，如 "/api/media/avatar.png" 或 None
        
    Returns:
        完整 URL，如 "http://localhost:11075/api/media/avatar.png"
        如果 path 为 None 或空字符串，返回 None
    """
    if not path:
        return None
    
    # 如果已经是完整 URL，直接返回
    if path.startswith(('http://', 'https://')):
        return path
    
    # 确保 path 以 / 开头
    if not path.startswith('/'):
        path = '/' + path
    
    # 确保 BASE_URL 不以 / 结尾
    base = BASE_URL.rstrip('/')
    
    return f"{base}{path}"


def extract_relative_path(url: str) -> str:
    """
    从完整 URL 中提取相对路径（用于存储到数据库）
    
    Args:
        url: 完整 URL，如 "http://localhost:11075/api/media/avatar.png"
        
    Returns:
        相对路径，如 "/api/media/avatar.png"
    """
    if not url:
        return None
    
    # 如果不是完整 URL，直接返回
    if not url.startswith(('http://', 'https://')):
        return url
    
    # 提取路径部分
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.path

