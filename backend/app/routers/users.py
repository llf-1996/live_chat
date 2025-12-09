from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from ..database import get_db
from ..models import User, UserRole, Conversation
from ..schemas import UserCreate, UserUpdate, UserResponse, PaginatedResponse, UserEnsureRequest, UserEnsureItem

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


@router.post("/ensure", response_model=List[UserResponse])
async def ensure_users(request: UserEnsureRequest, db: AsyncSession = Depends(get_db)):
    """
    会话检测接口
    
    功能说明：
        1. 批量创建/更新用户（幂等性：用户已存在则跳过）
        2. 自动填充默认值：
           - username 未提供 → 自动生成（角色名 + 毫秒时间戳）
           - avatar 未提供 → 根据角色随机分配默认头像
        3. 自动创建会话：当请求中有且只有2个用户时，自动为他们创建会话
    
    参数：
        request: UserEnsureRequest
            - users: List[UserEnsureItem] - 用户列表
                - id: 用户ID（必需）
                - role: 用户角色（必需）buyer/merchant/admin/platform
                - username: 用户名（可选）
                - avatar: 头像URL（可选）
                - description: 描述（可选）
    
    返回：
        List[UserResponse]: 创建或已存在的用户列表
    
    特性：
        - 幂等性：多次调用不会重复创建用户或会话
        - 智能默认值：自动生成用户名和头像，减少配置
        - 自动会话：2个用户自动创建会话，简化测试流程
    
    示例：
        # 创建2个用户并自动创建会话
        POST /api/users/ensure
        {
            "users": [
                {"id": "b1", "role": "buyer"},
                {"id": "m2", "role": "merchant"}
            ]
        }
        → 创建用户 b1, m2，并自动创建会话 b1 ↔ m2
        
        # 创建1个或3+个用户（不创建会话）
        POST /api/users/ensure
        {
            "users": [
                {"id": "b1", "role": "buyer"}
            ]
        }
        → 只创建用户，不创建会话
    """
    created_or_existing_users = []
    
    for user_item in request.users:
        # 检查用户是否已存在
        result = await db.execute(
            select(User).where(User.id == user_item.id)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            # 用户已存在，直接返回
            created_or_existing_users.append(existing_user)
        else:
            # 用户不存在，创建新用户
            
            # 生成默认用户名（如果未提供）
            username = user_item.username
            if not username:
                # 使用时间戳（毫秒）作为后缀
                import time
                timestamp_ms = int(time.time() * 1000)
                
                # 生成默认用户名
                role_name_map = {
                    UserRole.BUYER: "买家",
                    UserRole.MERCHANT: "商家",
                    UserRole.ADMIN: "管理员",
                    UserRole.PLATFORM: "平台客服"
                }
                username = f"{role_name_map.get(user_item.role, '用户')}{timestamp_ms}"
            
            # 生成默认头像（如果未提供）
            avatar = user_item.avatar
            if not avatar:
                # 根据角色选择默认头像（随机 1 或 2）
                import random
                
                if user_item.role == UserRole.BUYER:
                    # buyer1.png 和 buyer2.png 随机选择
                    avatar = f"/api/media/avatars/buyer{random.randint(1, 2)}.png"
                elif user_item.role == UserRole.MERCHANT:
                    # merchant1.png 和 merchant2.png 随机选择
                    avatar = f"/api/media/avatars/merchant{random.randint(1, 2)}.png"
                else:  # ADMIN
                    avatar = "/api/media/avatars/admin.png"
            
            # 创建新用户
            new_user = User(
                id=user_item.id,
                username=username,
                avatar=avatar,
                role=user_item.role,
                description=user_item.description,
                status="active"
            )
            
            db.add(new_user)
            created_or_existing_users.append(new_user)
    
    # 提交所有更改
    await db.commit()
    
    # 刷新所有用户对象
    for user in created_or_existing_users:
        await db.refresh(user)
    
    # ========== 自动创建会话记录 ==========
    # 如果请求中有且只有2个用户，自动为他们创建会话
    if len(created_or_existing_users) == 2:
        user1, user2 = created_or_existing_users[0], created_or_existing_users[1]
        
        # 检查会话是否已存在（支持双向查询）
        result = await db.execute(
            select(Conversation).where(
                or_(
                    and_(
                        Conversation.participant1_id == user1.id,
                        Conversation.participant2_id == user2.id
                    ),
                    and_(
                        Conversation.participant1_id == user2.id,
                        Conversation.participant2_id == user1.id
                    )
                )
            )
        )
        existing_conversation = result.scalar_one_or_none()
        
        if not existing_conversation:
            # 会话不存在，创建新会话
            new_conversation = Conversation(
                participant1_id=user1.id,
                participant2_id=user2.id
            )
            db.add(new_conversation)
            await db.commit()
            print(f"✅ 自动创建会话：{user1.id} ↔ {user2.id}")
        else:
            print(f"ℹ️  会话已存在：{user1.id} ↔ {user2.id}")
    
    return created_or_existing_users
