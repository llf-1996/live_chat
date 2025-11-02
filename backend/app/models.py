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


class MessageType(str, enum.Enum):
    """消息类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"


class User(Base):
    """用户表（统一管理客户、商家、管理员）"""
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)  # 字符串类型主键
    username = Column(String(100), unique=True, nullable=False, index=True)  # 统一显示名称
    password_hash = Column(String(255), nullable=True)  # 密码哈希（仅管理员需要）
    avatar = Column(String(255))
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.BUYER)
    description = Column(Text, nullable=True)  # 描述信息
    status = Column(String(20), default="active")  # 状态：active/inactive
    created_at = Column(Integer, default=get_timestamp)  # 创建时间戳

    # 关联
    sent_messages = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    customer_conversations = relationship("Conversation", back_populates="customer", foreign_keys="Conversation.customer_id")
    merchant_conversations = relationship("Conversation", back_populates="merchant", foreign_keys="Conversation.merchant_id")
    quick_replies = relationship("QuickReply", back_populates="user")


class Conversation(Base):
    """
    会话表
        仅支持单聊,不支持群聊(需调整会话表结构)
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(50), ForeignKey("users.id"), nullable=False)  # 客户ID（role=buyer）
    merchant_id = Column(String(50), ForeignKey("users.id"), nullable=False)  # 商家ID（role=merchant）
    customer_unread_count = Column(Integer, default=0)  # 客户的未读消息数
    merchant_unread_count = Column(Integer, default=0)  # 商家的未读消息数
    last_message = Column(Text)  # 最后一条消息内容
    last_message_time = Column(Integer)  # 最后消息时间戳
    created_at = Column(Integer, default=get_timestamp)  # 创建时间戳
    updated_at = Column(Integer, default=get_timestamp, onupdate=get_timestamp)  # 更新时间戳

    # 关联
    customer = relationship("User", back_populates="customer_conversations", foreign_keys=[customer_id])
    merchant = relationship("User", back_populates="merchant_conversations", foreign_keys=[merchant_id])
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")


class Message(Base):
    """消息表"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(SQLEnum(MessageType), default=MessageType.TEXT)
    is_read = Column(Boolean, default=False)
    created_at = Column(Integer, default=get_timestamp, index=True)  # 创建时间戳

    # 关联
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages", foreign_keys=[sender_id])


class QuickReply(Base):
    """快捷消息表"""
    __tablename__ = "quick_replies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)  # 用户ID
    content = Column(Text, nullable=False)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(Integer, default=get_timestamp)  # 创建时间戳

    # 关联
    user = relationship("User", back_populates="quick_replies")
