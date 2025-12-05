from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func, update
from sqlalchemy.orm import selectinload
from typing import List
from ..database import get_db
from ..models import Conversation, User, Message
from ..schemas import ConversationCreate, ConversationResponse, ConversationDetail, MessageResponse, PaginatedResponse

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("/", response_model=PaginatedResponse[ConversationResponse])
async def get_conversations(
    user_id: str = None,      # 通用用户ID过滤（查询该用户参与的所有会话）
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取会话列表"""
    # 构建基础查询
    base_query = select(Conversation).options(
        selectinload(Conversation.participant1),
        selectinload(Conversation.participant2)
    )

    # 获取总数的基础查询
    count_query = select(func.count()).select_from(Conversation)

    # 应用过滤条件
    if user_id:
        # 查询用户参与的所有会话（无论是参与者1还是参与者2）
        filter_condition = or_(
            Conversation.participant1_id == user_id,
            Conversation.participant2_id == user_id
        )
        base_query = base_query.where(filter_condition)
        count_query = count_query.where(filter_condition)
    
    count_result = await db.execute(count_query)
    total_count = count_result.scalar()

    # 计算偏移量
    skip = (page - 1) * page_size

    # 获取分页数据
    query = base_query.order_by(Conversation.updated_at.desc()).offset(skip).limit(page_size)
    result = await db.execute(query)
    conversations = result.scalars().all()
    
    return PaginatedResponse(count=total_count, results=conversations)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个会话"""
    result = await db.execute(
        select(Conversation)
        .options(
            selectinload(Conversation.participant1),
            selectinload(Conversation.participant2)
        )
        .where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.post("/", response_model=ConversationResponse)
async def create_conversation(conversation: ConversationCreate, db: AsyncSession = Depends(get_db)):
    """创建会话"""
    # 检查是否已存在
    result = await db.execute(
        select(Conversation).where(
            or_(
                and_(
                    Conversation.participant1_id == conversation.participant1_id,
                    Conversation.participant2_id == conversation.participant2_id
                ),
                and_(
                    Conversation.participant1_id == conversation.participant2_id,
                    Conversation.participant2_id == conversation.participant1_id
                )
            )
        )
    )
    existing_conversation = result.scalar_one_or_none()
    if existing_conversation:
        return existing_conversation

    # 创建新会话
    db_conversation = Conversation(**conversation.dict())
    db.add(db_conversation)
    await db.commit()
    await db.refresh(db_conversation)
    return db_conversation


@router.get("/{conversation_id}/messages", response_model=PaginatedResponse[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    order: str = 'desc',  # 排序方式：asc（正序，旧→新）或 desc（倒序，新→旧）
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    获取会话的所有历史消息（分页）
    
    Args:
        conversation_id: 会话ID
        order: 排序方式，'asc'（正序，适合聊天界面）或 'desc'（倒序，适合管理界面）
        page: 页码（从1开始）
        page_size: 每页记录数
    
    Returns:
        PaginatedResponse[MessageResponse]: 包含消息列表和总数
    """
    # 检查会话是否存在
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = conv_result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # 获取消息总数
    count_query = select(func.count()).select_from(Message).where(Message.conversation_id == conversation_id)
    count_result = await db.execute(count_query)
    total_count = count_result.scalar()
    
    # 计算偏移量
    skip = (page - 1) * page_size
    
    # 获取消息列表（支持排序）
    query = select(Message).options(selectinload(Message.sender)).where(Message.conversation_id == conversation_id)
    
    # 根据 order 参数排序
    if order == 'asc':
        query = query.order_by(Message.created_at.asc())
    else:
        query = query.order_by(Message.created_at.desc())
    
    query = query.offset(skip).limit(page_size)
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return PaginatedResponse(count=total_count, results=messages)


@router.put("/{conversation_id}/messages/read-all")
async def mark_conversation_messages_as_read(
    conversation_id: int, 
    reader_id: str = None,  # 添加参数：谁标记的已读
    db: AsyncSession = Depends(get_db)
):
    """标记会话中发送给当前用户的所有消息为已读"""
    from ..models import Message
    from ..websocket import manager  # 导入 WebSocket 管理器
    
    # 检查会话是否存在
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = conv_result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # ✅ 只标记发送给 reader_id 的消息为已读（即别人发给我的消息）
    # 不标记 reader_id 自己发送的消息
    if reader_id:
        await db.execute(
            update(Message)
            .where(Message.conversation_id == conversation_id)
            .where(Message.sender_id != reader_id)  # 关键：排除自己发送的消息
            .values(is_read=True)
        )
        await db.commit()
        
        # 通过 WebSocket 实时通知对方消息已读
        await manager.notify_message_read(conversation_id, reader_id)
    else:
        # 如果没有提供 reader_id，则标记所有消息（保持向后兼容）
        await db.execute(
            update(Message)
            .where(Message.conversation_id == conversation_id)
            .values(is_read=True)
        )
        await db.commit()
    
    return {"status": "success"}


@router.get("/{conversation_id}/detail", response_model=ConversationDetail)
async def get_conversation_detail(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """获取会话详情（包含消息统计）"""
    # 获取会话基本信息
    result = await db.execute(
        select(Conversation)
        .options(
            selectinload(Conversation.customer),
            selectinload(Conversation.merchant)
        )
        .where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # 统计消息数量
    count_result = await db.execute(
        select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
    )
    message_count = count_result.scalar()
    
    # 构建响应
    conversation_dict = {
        "id": conversation.id,
        "customer_id": conversation.customer_id,
        "merchant_id": conversation.merchant_id,
        "customer_unread_count": conversation.customer_unread_count,
        "merchant_unread_count": conversation.merchant_unread_count,
        "last_message": conversation.last_message,
        "last_message_time": conversation.last_message_time,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "customer": conversation.customer,
        "merchant": conversation.merchant,
        "message_count": message_count
    }
    
    return conversation_dict


@router.put("/{conversation_id}/read")
async def mark_conversation_as_read(
    conversation_id: int, 
    user_id: str, 
    db: AsyncSession = Depends(get_db)
):
    """标记会话为已读"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # 根据用户ID清零对应的未读数
    if conversation.participant1_id == user_id:
        conversation.participant1_unread = 0
    elif conversation.participant2_id == user_id:
        conversation.participant2_unread = 0
    
    await db.commit()
    return {"status": "success"}
