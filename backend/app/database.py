from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL 环境变量未设置，请在 .env 文件中配置")

DEBUG_SQL = os.getenv("DEBUG_SQL", "False").lower() == "true"

engine = create_async_engine(DATABASE_URL, echo=DEBUG_SQL)
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
