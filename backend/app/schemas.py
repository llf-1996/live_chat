from pydantic import BaseModel, Field, field_serializer, model_serializer
from typing import Optional, List, Generic, TypeVar
from .models import UserRole, MessageType
from .utils import build_full_url

# 泛型类型变量，用于分页响应
T = TypeVar('T')


# ===== 通用分页响应 =====
class PaginatedResponse(BaseModel, Generic[T]):
    """RESTful API 列表响应格式"""
    count: int = Field(..., description="总记录数")
    results: List[T] = Field(..., description="结果列表")


# ===== User Schemas =====
class UserBase(BaseModel):
    username: str  # 统一显示名称
    avatar: Optional[str] = None
    role: UserRole
    description: Optional[str] = None  # 描述信息
    status: str = "active"


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None
    avatar: Optional[str] = None
    role: Optional[UserRole] = None
    description: Optional[str] = None
    status: Optional[str] = None


class UserResponse(UserBase):
    id: str  # 字符串类型主键
    created_at: int  # 时间戳

    @field_serializer('avatar')
    def serialize_avatar(self, avatar: Optional[str]) -> Optional[str]:
        """序列化头像 URL，自动拼接完整地址"""
        return build_full_url(avatar) if avatar else None

    class Config:
        from_attributes = True


# ===== Message Schemas =====
class MessageBase(BaseModel):
    content: str
    message_type: MessageType = MessageType.TEXT


class MessageCreate(MessageBase):
    conversation_id: int
    sender_id: str  # 字符串类型用户ID


class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    sender_id: str  # 字符串类型用户ID
    is_read: bool
    created_at: int  # 时间戳
    sender: Optional[UserResponse] = None

    @model_serializer
    def ser_model(self):
        """自定义序列化，处理图片和文件消息的 URL 拼接"""
        # 根据消息类型处理 content
        content = self.content
        if self.message_type in ['image', 'file'] and content:
            content = build_full_url(content)
        
        # 构造返回数据
        data = {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_id': self.sender_id,
            'content': content,
            'message_type': self.message_type,
            'is_read': self.is_read,
            'created_at': self.created_at,
        }
        
        # 如果有 sender 对象，需要调用其 model_dump 来序列化
        if self.sender:
            data['sender'] = self.sender.model_dump() if hasattr(self.sender, 'model_dump') else self.sender
        else:
            data['sender'] = None
        
        return data

    class Config:
        from_attributes = True


# ===== Conversation Schemas =====
class ConversationBase(BaseModel):
    customer_id: str  # 客户ID（role=buyer）字符串类型
    merchant_id: str  # 商家ID（role=merchant）字符串类型


class ConversationCreate(ConversationBase):
    pass


class ConversationResponse(ConversationBase):
    id: int
    customer_unread_count: int  # 客户的未读消息数
    merchant_unread_count: int  # 商家的未读消息数
    last_message: Optional[str] = None
    last_message_time: Optional[int] = None  # 时间戳
    created_at: int  # 时间戳
    updated_at: int  # 时间戳
    customer: Optional[UserResponse] = None  # 客户信息
    merchant: Optional[UserResponse] = None  # 商家信息

    class Config:
        from_attributes = True


class ConversationDetail(ConversationResponse):
    message_count: int  # 消息总数
    messages: Optional[List['MessageResponse']] = None  # 消息列表（可选）


# ===== Quick Reply Schemas =====
class QuickReplyBase(BaseModel):
    content: str
    sort_order: int = 0


class QuickReplyCreate(QuickReplyBase):
    user_id: str  # 用户ID（字符串类型）


class QuickReplyUpdate(BaseModel):
    content: Optional[str] = None
    sort_order: Optional[int] = None


class QuickReplyResponse(QuickReplyBase):
    id: int
    user_id: str  # 用户ID（字符串类型）
    is_active: bool
    created_at: int  # 时间戳

    class Config:
        from_attributes = True


# ===== WebSocket Schemas =====
class WebSocketMessage(BaseModel):
    type: str  # "message", "read", "typing", "status"
    conversation_id: Optional[int] = None
    sender_id: Optional[str] = None  # 字符串类型用户ID
    content: Optional[str] = None
    message_type: Optional[MessageType] = MessageType.TEXT
    timestamp: Optional[int] = None  # 时间戳


# ===== Upload Response =====
class UploadResponse(BaseModel):
    url: str
    filename: str
    file_type: str


# ===== User Ensure Schemas =====
class UserEnsureItem(BaseModel):
    """批量创建/更新用户的单个用户信息"""
    id: str = Field(..., description="用户ID")
    role: UserRole = Field(..., description="用户角色")
    username: Optional[str] = Field(None, description="用户名，不提供则自动生成")
    avatar: Optional[str] = Field(None, description="头像路径，不提供则使用默认头像")
    description: Optional[str] = Field(None, description="用户描述")


class UserEnsureRequest(BaseModel):
    """批量创建/更新用户请求"""
    users: List[UserEnsureItem] = Field(..., description="用户列表")


# ===== Auth Schemas =====
class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(..., description="JWT Token")
    token_type: str = Field(default="bearer", description="Token 类型")
    user: UserResponse = Field(..., description="用户信息")


class TokenPayload(BaseModel):
    """Token 载荷"""
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="用户角色")
