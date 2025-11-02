from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from ..database import get_db
from ..models import User, UserRole
from ..schemas import UserCreate, UserUpdate, UserResponse, PaginatedResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def get_users(
    role: Optional[str] = None,  # 按角色过滤：buyer, merchant, admin
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表（可按角色过滤）"""
    # 构建基础查询
    base_query = select(User)
    
    # 按角色过滤
    if role:
        base_query = base_query.where(User.role == role)
    
    # 获取总数
    count_query = select(func.count()).select_from(User)
    if role:
        count_query = count_query.where(User.role == role)
    count_result = await db.execute(count_query)
    total_count = count_result.scalar()
    
    # 计算偏移量
    skip = (page - 1) * page_size
    
    # 获取分页数据
    query = base_query.offset(skip).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return PaginatedResponse(count=total_count, results=users)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """获取单个用户"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """创建用户"""
    db_user = User(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    """更新用户信息（所有字段）"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 更新字段
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/{user_id}/status", response_model=UserResponse)
async def update_user_status(user_id: str, status: str, db: AsyncSession = Depends(get_db)):
    """更新用户状态（禁用/启用）"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if status not in ["active", "inactive"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'active' or 'inactive'")
    
    user.status = status
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """删除用户（软删除）"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 软删除：设置状态为deleted
    user.status = "deleted"
    await db.commit()
    return {"status": "success", "message": "User deleted successfully"}
