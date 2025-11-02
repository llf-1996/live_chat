from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from typing import List
import time
from ..database import get_db
from ..models import Message, Conversation
from ..schemas import MessageCreate, MessageResponse, PaginatedResponse

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("/", response_model=PaginatedResponse[MessageResponse])
async def get_all_messages(
    conversation_id: int = None,
    sender_id: str = None,
    message_type: str = None,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """获取所有消息列表（支持筛选、分页）"""
    # 构建基础查询
    base_query = select(Message).options(selectinload(Message.sender))
    
    # 筛选条件
    if conversation_id:
        base_query = base_query.where(Message.conversation_id == conversation_id)
    if sender_id:
        base_query = base_query.where(Message.sender_id == sender_id)
    if message_type:
        base_query = base_query.where(Message.message_type == message_type)
    
    # 获取总数
    count_query = select(func.count()).select_from(Message)
    if conversation_id:
        count_query = count_query.where(Message.conversation_id == conversation_id)
    if sender_id:
        count_query = count_query.where(Message.sender_id == sender_id)
    if message_type:
        count_query = count_query.where(Message.message_type == message_type)
    count_result = await db.execute(count_query)
    total_count = count_result.scalar()
    
    # 计算偏移量
    skip = (page - 1) * page_size
    
    # 分页和排序
    query = base_query.order_by(Message.created_at.desc()).offset(skip).limit(page_size)
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return PaginatedResponse(count=total_count, results=messages)


@router.post("/", response_model=MessageResponse)
async def create_message(message: MessageCreate, db: AsyncSession = Depends(get_db)):
    """发送消息"""
    # 创建消息
    db_message = Message(**message.dict())
    db.add(db_message)

    # 更新会话信息
    result = await db.execute(
        select(Conversation).where(Conversation.id == message.conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if conversation:
        # 根据消息类型设置友好的显示文本
        if message.message_type == "image":
            last_message_text = "[图片]"
        elif message.message_type == "file":
            last_message_text = "[文件]"
        else:
            # 文本消息，限制长度
            last_message_text = message.content[:100]
        
        conversation.last_message = last_message_text
        conversation.last_message_time = int(time.time())
        conversation.updated_at = int(time.time())
        
        # 根据发送者身份，增加对方的未读消息数
        if message.sender_id == conversation.customer_id:
            # 客户发送 → 商家的未读数+1
            conversation.merchant_unread_count += 1
        else:
            # 商家发送 → 客户的未读数+1
            conversation.customer_unread_count += 1

    await db.commit()
    await db.refresh(db_message)

    # 重新加载关联数据
    result = await db.execute(
        select(Message)
        .options(selectinload(Message.sender))
        .where(Message.id == db_message.id)
    )
    return result.scalar_one()


@router.put("/{message_id}/read")
async def mark_message_as_read(message_id: int, db: AsyncSession = Depends(get_db)):
    """标记消息为已读"""
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    message.is_read = True
    await db.commit()
    return {"status": "success"}


@router.delete("/{message_id}")
async def delete_message(message_id: int, db: AsyncSession = Depends(get_db)):
    """删除消息（硬删除）"""
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    await db.delete(message)
    await db.commit()
    return {"status": "success", "message": "Message deleted successfully"}
