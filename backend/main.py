from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from contextlib import asynccontextmanager
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

from app.auth import hash_password

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 加载环境变量
load_dotenv()

from app.database import get_db, engine
from app.routers import users, conversations, messages, quick_replies, upload, auth
from app.websocket import manager
from app.models import User, QuickReply, UserRole
from app.exceptions import (
    validation_exception_handler,
    sqlalchemy_exception_handler,
    pydantic_validation_exception_handler,
    general_exception_handler,
    business_exception_handler,
    BusinessException,
)

# 从环境变量读取配置
MEDIA_DIR = os.getenv("MEDIA_DIR")
if MEDIA_DIR is None:
    raise ValueError("MEDIA_DIR 环境变量未设置，请在 .env 文件中配置")


# 数据初始化函数
async def initialize_data():
    """初始化测试数据"""
    from app.database import async_session_maker
    from sqlalchemy import select

    async with async_session_maker() as db:
        # 检查是否已有数据
        result = await db.execute(select(User))
        if result.first():
            return  # 数据已存在

        # 创建测试用户
        users_data = [
            # 平台管理员(固定添加)
            User(
                id="a2",
                username="admin",
                avatar="/api/media/avatars/admin.png",
                role=UserRole.ADMIN,
                description="管理员",
                password_hash=hash_password("admin123"),
            ),
            # 官方客服(固定添加)
            User(
                id="p1",
                username="官方客服",
                avatar="/api/media/avatars/service.png",
                role=UserRole.PLATFORM,
                description="官方客服"
            ),
            # 客户/买家(2个)
            User(
                id="b1",
                username="保安堂药房",
                avatar="/api/media/avatars/buyer1.png",
                description='一家深植于社区的传统药房，秉承"保安康，济天下"的经营理念。除提供各类中西成药外，还提供代客煎药、健康咨询等贴心服务，是街坊邻里信赖的健康守护站。',
                role=UserRole.BUYER.value
            ),
            User(
                id="b2",
                username="异世界药局",
                avatar="/api/media/avatars/buyer2.png",
                role=UserRole.BUYER.value,
                description="一家以创新和客户体验为核心的现代连锁药局。不仅销售药品，还提供个性化的健康解决方案、先进的医疗器械租赁及全程用药指导，旨在成为顾客身边的健康管理伙伴。",
            ),
            # 商家（3个）
            User(
                id="m1",
                username="保和堂医药集团",
                avatar="/api/media/avatars/merchant1.png",
                role=UserRole.MERCHANT,
                description="一家融合了百年传承技艺与现代管理体系的大型医药集团。业务涵盖经典名方的研发、中药饮片生产及现代化中成药制造，致力于让传统智慧为当代健康服务。",
            ),
            User(
                id="m2",
                username="阿纳斯蒂制药",
                avatar="/api/media/avatars/merchant2.png",
                role=UserRole.MERCHANT,
                description="一家专注于神经科学领域前沿研究的创新型药企，以开发调节情绪与认知功能的特种药物而闻名。其产品线基于精准医疗理念，致力于为复杂的神经系统疾病提供突破性治疗方案。"
            ),
            User(
                id="m3",
                username="梅迪西斯制药",
                avatar="/api/media/avatars/user1.png",
                role=UserRole.MERCHANT,
                description="源自古老的医药世家，将传统配方与现代尖端制药技术相结合。该药厂尤其擅长开发天然植物提取物制成的特效药与高品质保健品，在业界享有崇高声誉。"
            )

        ]
        db.add_all(users_data)
        await db.commit()

        # 创建快捷消息（为所有用户创建）
        result = await db.execute(select(User))
        all_users = result.scalars().all()

        quick_replies = []
        for user in all_users:
            # 根据角色创建不同的快捷消息
            if user.role == UserRole.MERCHANT:
                # 商家的快捷消息（初始化3条，可自行添加到10条）
                user_quick_replies = [
                    QuickReply(
                        user_id=user.id,
                        content="您好，欢迎咨询！请问有什么可以帮到您的？",
                        sort_order=0
                    ),
                    QuickReply(
                        user_id=user.id,
                        content="您好，我们提供7天无理由退换货服务，请提供您的订单号，我会马上为您处理。",
                        sort_order=1
                    ),
                    QuickReply(
                        user_id=user.id,
                        content="您好，请提供您的订单号，我会帮您查询订单详情。",
                        sort_order=2
                    ),
                ]
            elif user.role == UserRole.BUYER:
                # 买家的快捷消息（初始化3条，可自行添加到10条）
                user_quick_replies = [
                    QuickReply(
                        user_id=user.id,
                        content="您好，在吗？",
                        sort_order=0
                    ),
                    QuickReply(
                        user_id=user.id,
                        content="您好，我想咨询一下我的订单情况。",
                        sort_order=1
                    ),
                    QuickReply(
                        user_id=user.id,
                        content="您好，请帮我查一下物流信息，谢谢。",
                        sort_order=2
                    ),
                ]
            else:  # UserRole.ADMIN
                # 管理员的快捷消息（初始化3条，可自行添加到10条）
                user_quick_replies = [
                    QuickReply(
                        user_id=user.id,
                        content="您好，我是平台管理员。",
                        sort_order=0
                    ),
                    QuickReply(
                        user_id=user.id,
                        content="您好，这里是平台客服，请问有什么可以帮到您？",
                        sort_order=1
                    ),
                    QuickReply(
                        user_id=user.id,
                        content="您好，我们正在调查相关问题，请提供更多详细信息。",
                        sort_order=2
                    ),
                ]
            
            quick_replies.extend(user_quick_replies)
        
        db.add_all(quick_replies)
        await db.commit()

        print("✅ 测试数据初始化完成")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("🚀 初始化内置数据...")
    # 注意：数据库表结构由 Alembic 管理，不再使用 init_db()
    await initialize_data()
    print("✅ 内置数据初始化完成")

    # 创建媒体文件目录
    Path(MEDIA_DIR).mkdir(parents=True, exist_ok=True)
    print(f"✅ 媒体文件目录创建完成: {MEDIA_DIR}")

    yield

    # 关闭时
    print("👋 应用关闭，清理数据库连接...")
    await engine.dispose()
    print("✅ 数据库连接已关闭")


# 验证应用配置
APP_TITLE = os.getenv("APP_TITLE")
if APP_TITLE is None:
    raise ValueError("APP_TITLE 环境变量未设置，请在 .env 文件中配置")

APP_DESCRIPTION = os.getenv("APP_DESCRIPTION")
if APP_DESCRIPTION is None:
    raise ValueError("APP_DESCRIPTION 环境变量未设置，请在 .env 文件中配置")

APP_VERSION = os.getenv("APP_VERSION")
if APP_VERSION is None:
    raise ValueError("APP_VERSION 环境变量未设置，请在 .env 文件中配置")

# 创建FastAPI应用
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",      # Swagger UI 文档路径
    redoc_url="/api/redoc",    # ReDoc 文档路径
    openapi_url="/api/openapi.json"  # OpenAPI schema 路径
)

# 配置CORS
cors_origins = os.getenv("CORS_ORIGINS")
if cors_origins is None:
    raise ValueError("CORS_ORIGINS 环境变量未设置，请在 .env 文件中配置")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins.split(","),  # 从环境变量读取，多个地址用逗号分隔
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册全局异常处理器
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 挂载静态文件（媒体文件目录）
app.mount("/api/media", StaticFiles(directory=MEDIA_DIR), name="media")

# 注册路由
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(conversations.router)
app.include_router(messages.router)
app.include_router(quick_replies.router)
app.include_router(upload.router)


# WebSocket端点
@app.websocket("/api/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str
):
    """WebSocket连接端点"""
    # 从数据库查询用户信息
    from app.models import User
    from app.database import async_session_maker
    from sqlalchemy import select
    
    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            await websocket.close(code=1008, reason="User not found")
            return
        
        role = user.role
    
    await manager.connect(websocket, user_id, role)
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)

            # 处理不同类型的消息
            message_type = message.get("type")

            if message_type == "message":
                conversation_id = message.get("conversation_id")
                content = message.get("content")
                msg_content_type = message.get("message_type", "text")

                # 获取会话信息以确定接收者
                from sqlalchemy import select
                from app.models import Conversation
                import time

                async with async_session_maker() as db:
                    result = await db.execute(
                        select(Conversation).where(Conversation.id == conversation_id)
                    )
                    conversation = result.scalar_one_or_none()
                    
                    if conversation:
                        # 确定参与者
                        participant1_id = conversation.participant1_id
                        participant2_id = conversation.participant2_id
                        
                        # 构造消息数据
                        message_data = {
                            "type": "message",
                            "conversation_id": conversation_id,
                            "sender_id": user_id,
                            "content": content,
                            "message_type": msg_content_type,
                            "timestamp": int(time.time())
                        }
                        
                        # 发送给对方
                        if user_id == participant1_id:
                            await manager.send_personal_message(message_data, participant2_id)
                        else:
                            await manager.send_personal_message(message_data, participant1_id)
                            
                        # 发送给所有管理员
                        for admin_id in list(manager.admin_users):
                            if admin_id != user_id:
                                await manager.send_personal_message(message_data, admin_id)

            elif message_type == "read":
                # 标记消息已读
                conversation_id = message.get("conversation_id")
                if conversation_id:
                    from sqlalchemy import select
                    from app.models import Conversation, Message
                    from sqlalchemy import update

                    async with async_session_maker() as db:
                        # 更新会话未读数
                        # 需要根据 user_id 判断是清空 participant1_unread 还是 participant2_unread
                        result = await db.execute(
                            select(Conversation).where(Conversation.id == conversation_id)
                        )
                        conversation = result.scalar_one_or_none()
                        
                        if conversation:
                            if conversation.participant1_id == user_id:
                                conversation.participant1_unread = 0
                            elif conversation.participant2_id == user_id:
                                conversation.participant2_unread = 0
                            
                            # 标记消息为已读
                            await db.execute(
                                update(Message)
                                .where(Message.conversation_id == conversation_id)
                                .where(Message.sender_id != user_id) # 只标记对方发的消息
                                .values(is_read=True)
                            )
                            await db.commit()

            elif message_type == "typing":
                # 发送输入状态给会话参与者
                conversation_id = message.get("conversation_id")
                if conversation_id:
                    # 获取会话信息以确定接收者
                    from sqlalchemy import select
                    from app.models import Conversation

                    async with async_session_maker() as db:
                        result = await db.execute(
                            select(Conversation).where(Conversation.id == conversation_id)
                        )
                        conversation = result.scalar_one_or_none()
                        
                        if conversation:
                            participant1_id = conversation.participant1_id
                            participant2_id = conversation.participant2_id
                            
                            typing_message = {
                                "type": "typing",
                                "user_id": user_id,
                                "conversation_id": conversation_id,
                                "is_typing": message.get("is_typing", True)
                            }
                            
                            # 发送给对方
                            if user_id == participant1_id:
                                await manager.send_personal_message(typing_message, participant2_id)
                            else:
                                await manager.send_personal_message(typing_message, participant1_id)

    except WebSocketDisconnect:
        await manager.disconnect(user_id, role)
        print(f"用户 {user_id} 断开连接")


@app.get("/api/")
async def root():
    """根路径"""
    return {
        "message": "在线客服系统 API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    # 验证服务器配置
    host = os.getenv("HOST")
    if host is None:
        raise ValueError("HOST 环境变量未设置，请在 .env 文件中配置")
    
    port_str = os.getenv("PORT")
    if port_str is None:
        raise ValueError("PORT 环境变量未设置，请在 .env 文件中配置")
    
    reload_str = os.getenv("RELOAD")
    if reload_str is None:
        raise ValueError("RELOAD 环境变量未设置，请在 .env 文件中配置")
    reload = reload_str.lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=int(port_str),
        reload=reload
    )
