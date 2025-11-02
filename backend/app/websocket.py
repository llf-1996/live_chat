from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import time
from app.utils import build_full_url


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 用户连接：{user_id: WebSocket}
        self.active_connections: Dict[int, WebSocket] = {}
        # 在线用户
        self.online_users: Set[int] = set()
        # 平台管理员用户ID集合
        self.admin_users: Set[int] = set()

    async def connect(self, websocket: WebSocket, user_id: int, role: str = "buyer"):
        """建立连接"""
        await websocket.accept()
        
        # 所有用户使用统一的用户级连接
        self.active_connections[user_id] = websocket
        self.online_users.add(user_id)
        
        # 如果是平台管理员，加入管理员集合
        if role == "admin":
            self.admin_users.add(user_id)

        # 1. 先发送当前所有在线用户列表给新连接的用户
        online_users_list = list(self.online_users - {user_id})  # 排除自己
        if online_users_list:
            await websocket.send_json({
                "type": "online_users",
                "users": online_users_list,
                "timestamp": int(time.time())
            })
        
        # 2. 再广播新用户上线给其他人
        await self.broadcast_status(user_id, "online")

    async def disconnect(self, user_id: int, role: str = "buyer"):
        """断开连接"""
        # 移除用户连接
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # 移除在线状态
        if user_id in self.online_users:
            self.online_users.remove(user_id)
        
        # 如果是管理员，从管理员集合中移除
        if role == "admin" and user_id in self.admin_users:
            self.admin_users.remove(user_id)
        
        # 广播离线状态
        await self.broadcast_status(user_id, "offline")

    async def send_personal_message(self, message: dict, user_id: int):
        """发送个人消息"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except:
                # 连接已断开
                self.disconnect(user_id)

    async def send_to_conversation_participants(self, message: dict, sender_id: int, conversation_id: int):
        """发送消息给会话的参与者（一对一）+ 平台管理员（监控）"""
        from app.database import async_session_maker
        from app.models import Conversation
        from sqlalchemy import select
        
        # 查询会话信息，获取买家和商户
        async with async_session_maker() as db:
            result = await db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                return
            
            customer_id = conversation.customer_id
            merchant_id = conversation.merchant_id
        
        # 获取消息内容和类型
        content = message.get("content")
        message_type = message.get("message_type", "text")
        
        # 如果是图片或文件消息，拼接完整 URL
        if message_type in ["image", "file"] and content:
            content = build_full_url(content)
        
        # 构造消息数据
        message_data = {
            "type": "message",
            "conversation_id": conversation_id,
            "sender_id": sender_id,
            "content": content,
            "message_type": message_type,
            "timestamp": int(time.time())
        }
        
        # 判断发送者身份，推送给对应的接收者
        # 如果发送者是客户，推送给商家
        if sender_id == customer_id:
            await self.send_personal_message(message_data, merchant_id)
        # 否则，推送给客户
        else:
            await self.send_personal_message(message_data, customer_id)
        
        # 同时推送给所有在线的平台管理员（实时监控）
        for admin_id in list(self.admin_users):
            # 不重复发送给发送者本人
            if admin_id != sender_id:
                await self.send_personal_message(message_data, admin_id)

    async def broadcast_status(self, user_id: int, status: str):
        """广播用户状态"""
        status_message = {
            "type": "status",
            "user_id": user_id,
            "status": status,
            "timestamp": int(time.time())
        }

        for uid, websocket in list(self.active_connections.items()):
            if uid != user_id:
                try:
                    await websocket.send_json(status_message)
                except Exception as e:
                    # 连接失败，静默处理，连接管理器会在下次发送时清理
                    print(f"发送状态消息失败 (用户{uid}): {e}")

    async def notify_unread(self, user_id: int, conversation_id: int, count: int):
        """通知未读消息数"""
        message = {
            "type": "unread",
            "conversation_id": conversation_id,
            "count": count,
            "timestamp": int(time.time())
        }
        await self.send_personal_message(message, user_id)

    async def notify_message_read(self, conversation_id: int, reader_id: str):
        """通知会话参与者消息已读"""
        from app.database import async_session_maker
        from app.models import Conversation
        from sqlalchemy import select
        
        # 查询会话信息
        async with async_session_maker() as db:
            result = await db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                return
            
            customer_id = conversation.customer_id
            merchant_id = conversation.merchant_id
        
        # 构造已读通知消息
        read_message = {
            "type": "read",
            "conversation_id": conversation_id,
            "reader_id": reader_id,  # 谁标记的已读
            "timestamp": int(time.time())
        }
        
        # 通知会话的另一方（发送者）
        if reader_id == customer_id:
            # 客户标记已读 → 通知商户
            await self.send_personal_message(read_message, merchant_id)
        else:
            # 商户标记已读 → 通知客户
            await self.send_personal_message(read_message, customer_id)

    def is_online(self, user_id: int) -> bool:
        """检查用户是否在线"""
        return user_id in self.online_users


# 全局连接管理器实例
manager = ConnectionManager()
