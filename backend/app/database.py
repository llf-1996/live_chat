from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL 环境变量未设置，请在 .env 文件中配置")

debug_sql_str = os.getenv("DEBUG_SQL")
if debug_sql_str is None:
    raise ValueError("DEBUG_SQL 环境变量未设置，请在 .env 文件中配置")
DEBUG_SQL = debug_sql_str.lower() == "true"

# ================== 连接池与断连防护（必填） ==================
# 说明：与其它环境变量保持一致风格：仅在未设置（None）时报错；
# "False"、"0"、""（空字符串）均视为有效值，但数值型配置不建议使用空字符串。

pool_pre_ping_str = os.getenv("DB_POOL_PRE_PING")
if pool_pre_ping_str is None:
    raise ValueError("DB_POOL_PRE_PING 环境变量未设置，请在 .env 文件中配置")
pool_pre_ping = pool_pre_ping_str.lower() == "true"

pool_recycle_str = os.getenv("DB_POOL_RECYCLE")
if pool_recycle_str is None:
    raise ValueError("DB_POOL_RECYCLE 环境变量未设置，请在 .env 文件中配置")
pool_recycle = int(pool_recycle_str)

pool_size_str = os.getenv("DB_POOL_SIZE")
if pool_size_str is None:
    raise ValueError("DB_POOL_SIZE 环境变量未设置，请在 .env 文件中配置")
pool_size = int(pool_size_str)

max_overflow_str = os.getenv("DB_MAX_OVERFLOW")
if max_overflow_str is None:
    raise ValueError("DB_MAX_OVERFLOW 环境变量未设置，请在 .env 文件中配置")
max_overflow = int(max_overflow_str)

pool_timeout_str = os.getenv("DB_POOL_TIMEOUT")
if pool_timeout_str is None:
    raise ValueError("DB_POOL_TIMEOUT 环境变量未设置，请在 .env 文件中配置")
pool_timeout = int(pool_timeout_str)

# 注：对 mysql+aiomysql 来说，常见的 connect_args 参数通常无需设置。
# 若需要限制初始连接等待，可按需加入：connect_args={"connect_timeout": 10}

engine = create_async_engine(
    DATABASE_URL,
    echo=DEBUG_SQL,
    pool_pre_ping=pool_pre_ping,
    pool_recycle=pool_recycle,
    pool_size=pool_size,
    max_overflow=max_overflow,
    pool_timeout=pool_timeout,
)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session_maker() as session:
        yield session


# ==================== 已废弃 ====================
# 注意：自从引入 Alembic 后，不应该再使用此函数！
# 数据库表结构应该通过 Alembic 迁移管理：
#   alembic revision --autogenerate -m "描述"
#   alembic upgrade head
# ===============================================

# async def init_db():
#     """已废弃：请使用 Alembic 管理数据库结构"""
#     from .models import Base
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
