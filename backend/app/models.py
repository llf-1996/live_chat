from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
import time
import enum

# 创建 Base 类（用于 Alembic 迁移）
Base = declarative_base()


def get_timestamp():
    """获取当前时间戳（整数）"""
    return int(time.time())


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    BUYER = "buyer"  # 客户/买家
    MERCHANT = "merchant"  # 商家
    ADMIN = "admin"  # 平台管理员
    PLATFORM = "platform"  # 平台客服


class MessageType(str, enum.Enum):
    """消息类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"


class User(Base):
    """用户表（统一管理客户、商家、管理员）"""
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True, comment="字符串类型主键")  # 字符串类型主键
    username = Column(String(100), unique=True, nullable=False, index=True, comment="统一显示名称")  # 统一显示名称
    password_hash = Column(String(255), nullable=True, comment="密码哈希（仅管理员需要）")  # 密码哈希（仅管理员需要）
    avatar = Column(String(255), comment="头像URL")
    # 使用 SQLEnum 确保类型安全，同时为了避免 Alembic 自动生成的迁移文件为空，
    # 我们在 env.py 中开启了 compare_type=True
    # 指定 values_callable 以确保数据库中使用小写值
    role = Column(SQLEnum(UserRole, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=UserRole.BUYER, comment="用户角色：buyer/merchant/admin/platform")
    description = Column(Text, nullable=True, comment="描述信息")  # 描述信息
    status = Column(String(20), default="active", comment="状态：active/inactive")  # 状态：active/inactive
    created_at = Column(Integer, default=get_timestamp, comment="创建时间戳")  # 创建时间戳

    # 关联
    sent_messages = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    conversations_as_p1 = relationship("Conversation", back_populates="participant1", foreign_keys="Conversation.participant1_id")
    conversations_as_p2 = relationship("Conversation", back_populates="participant2", foreign_keys="Conversation.participant2_id")
    quick_replies = relationship("QuickReply", back_populates="user")


class Conversation(Base):
    """
    会话表
        仅支持单聊,不支持群聊(需调整会话表结构)
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, comment="自增主键")
    # 使用更通用的命名：发起者(initiator)和接收者(receiver)，或者参与者1(participant1)和参与者2(participant2)
    # 这里采用 participant1_id 和 participant2_id，并约定 id 较小的在 participant1，较大的在 participant2，保证唯一性（或者不强制，由业务逻辑控制）
    # 简单起见，我们暂不强制 id 大小顺序，而是通过业务逻辑确保 (p1, p2) 和 (p2, p1) 指向同一个逻辑会话
    
    participant1_id = Column(String(50), ForeignKey("users.id"), nullable=False, comment="会话参与者1ID")
    participant2_id = Column(String(50), ForeignKey("users.id"), nullable=False, comment="会话参与者2ID")
    
    participant1_unread = Column(Integer, default=0, comment="参与者1的未读消息数")
    participant2_unread = Column(Integer, default=0, comment="参与者2的未读消息数")
    
    last_message = Column(Text, comment="最后一条消息内容")  # 最后一条消息内容
    last_message_time = Column(Integer, comment="最后消息时间戳")  # 最后消息时间戳
    created_at = Column(Integer, default=get_timestamp, comment="创建时间戳")  # 创建时间戳
    updated_at = Column(Integer, default=get_timestamp, onupdate=get_timestamp, comment="更新时间戳")  # 更新时间戳

    # 关联
    participant1 = relationship("User", back_populates="conversations_as_p1", foreign_keys=[participant1_id])
    participant2 = relationship("User", back_populates="conversations_as_p2", foreign_keys=[participant2_id])
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")


class Message(Base):
    """消息表"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, comment="自增主键")
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, comment="会话ID")
    sender_id = Column(String(50), ForeignKey("users.id"), nullable=False, comment="发送者ID")
    content = Column(Text, nullable=False, comment="消息内容")
    message_type = Column(SQLEnum(MessageType, values_callable=lambda obj: [e.value for e in obj]), default=MessageType.TEXT, comment="消息类型：text/image/file")
    is_read = Column(Boolean, default=False, comment="是否已读")
    created_at = Column(Integer, default=get_timestamp, index=True, comment="创建时间戳")  # 创建时间戳

    # 关联
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages", foreign_keys=[sender_id])


class QuickReply(Base):
    """快捷消息表"""
    __tablename__ = "quick_replies"

    id = Column(Integer, primary_key=True, index=True, comment="自增主键")
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, comment="用户ID")  # 用户ID
    content = Column(Text, nullable=False, comment="快捷回复内容")
    sort_order = Column(Integer, default=0, comment="排序权重")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(Integer, default=get_timestamp, comment="创建时间戳")  # 创建时间戳

    # 关联
    user = relationship("User", back_populates="quick_replies")
