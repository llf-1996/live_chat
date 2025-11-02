from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from ..database import get_db
from ..models import QuickReply
from ..schemas import QuickReplyCreate, QuickReplyUpdate, QuickReplyResponse

router = APIRouter(prefix="/api/quick-replies", tags=["quick-replies"])

# 快捷消息最大数量限制
MAX_QUICK_REPLIES = 10


@router.get("/user/{user_id}", response_model=List[QuickReplyResponse])
async def get_quick_replies(
    user_id: str,  # 用户ID（role=merchant）
    db: AsyncSession = Depends(get_db)
):
    """获取商家用户的快捷回复列表"""
    result = await db.execute(
        select(QuickReply)
        .where(QuickReply.user_id == user_id, QuickReply.is_active == True)
        .order_by(QuickReply.sort_order)
    )
    quick_replies = result.scalars().all()
    return quick_replies


# 向后兼容：保留旧的API路径
@router.get("/merchant/{merchant_id}", response_model=List[QuickReplyResponse])
async def get_quick_replies_compat(
    merchant_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取商家的快捷回复列表（兼容旧版API）"""
    return await get_quick_replies(merchant_id, db)


@router.post("/", response_model=QuickReplyResponse)
async def create_quick_reply(
    quick_reply: QuickReplyCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建快捷消息（最多10条）"""
    # 检查当前用户的快捷消息数量
    result = await db.execute(
        select(func.count(QuickReply.id))
        .where(QuickReply.user_id == quick_reply.user_id, QuickReply.is_active == True)
    )
    count = result.scalar()
    
    if count >= MAX_QUICK_REPLIES:
        raise HTTPException(
            status_code=400, 
            detail=f"最多只能创建{MAX_QUICK_REPLIES}条快捷消息"
        )
    
    db_quick_reply = QuickReply(**quick_reply.dict())
    db.add(db_quick_reply)
    await db.commit()
    await db.refresh(db_quick_reply)
    return db_quick_reply


@router.put("/{quick_reply_id}", response_model=QuickReplyResponse)
async def update_quick_reply(
    quick_reply_id: int,
    quick_reply_update: QuickReplyUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新快捷消息"""
    result = await db.execute(
        select(QuickReply).where(QuickReply.id == quick_reply_id)
    )
    quick_reply = result.scalar_one_or_none()
    if not quick_reply:
        raise HTTPException(status_code=404, detail="快捷消息不存在")
    
    # 更新字段
    update_data = quick_reply_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(quick_reply, field, value)
    
    await db.commit()
    await db.refresh(quick_reply)
    return quick_reply


@router.delete("/{quick_reply_id}")
async def delete_quick_reply(
    quick_reply_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除快捷消息（软删除）"""
    result = await db.execute(
        select(QuickReply).where(QuickReply.id == quick_reply_id)
    )
    quick_reply = result.scalar_one_or_none()
    if not quick_reply:
        raise HTTPException(status_code=404, detail="快捷消息不存在")

    quick_reply.is_active = False
    await db.commit()
    return {"status": "success", "message": "删除成功"}
