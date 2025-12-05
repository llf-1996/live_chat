from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import time
from app.utils import build_full_url


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 用户连接：{user_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # 在线用户
        self.online_users: Set[str] = set()
        # 平台管理员用户ID集合
        self.admin_users: Set[str] = set()

    async def connect(self, websocket: WebSocket, user_id: str, role: str = "buyer"):
        """建立连接"""
        await websocket.accept()
        
        # 所有用户使用统一的用户级连接
        self.active_connections[user_id] = websocket
        self.online_users.add(user_id)
        
        print(f"用户上线: {user_id}, 当前在线: {list(self.online_users)}")
        
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

    async def disconnect(self, user_id: str, role: str = "buyer"):
        """断开连接"""
        # 移除用户连接
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # 移除在线状态
        if user_id in self.online_users:
            self.online_users.remove(user_id)
            
        print(f"用户下线: {user_id}, 当前在线: {list(self.online_users)}")
        
        # 如果是管理员，从管理员集合中移除
        if role == "admin" and user_id in self.admin_users:
            self.admin_users.remove(user_id)
        
        # 广播离线状态
        await self.broadcast_status(user_id, "offline")

    async def send_personal_message(self, message: dict, user_id: str):
        """发送个人消息"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except:
                # 连接已断开
                await self.disconnect(user_id)

    async def send_to_conversation_participants(self, message_data: dict, sender_id: str, conversation_id: int):
        """
        发送消息给会话参与者（根据会话ID查找参与者）
        注意：这个方法现在需要传入 sender_id 和 conversation_id，
        但在 WebSocketManager 内部很难直接访问数据库获取 participant1/participant2。
        
        通常是在业务层（routers）获取到会话信息后，调用此方法并传入明确的接收者ID。
        或者重构此方法，接受 receiver_id。
        
        这里为了兼容旧代码，我们暂时假设调用者会先处理好逻辑，或者我们在 WebSocket 路由中处理。
        
        更好的方式是：
        async def send_message(self, message_data: dict, sender_id: str, receiver_id: str):
             ...
             
        目前的 send_to_conversation_participants 是用于 typing 状态等，
        如果无法直接获取 receiver_id，可能需要从数据库查（不推荐在 ws 中查库）。
        
        修改策略：
        让调用者（main.py 中的 websocket_endpoint）负责查询会话信息并传递 participant1_id 和 participant2_id。
        """
        # 这是一个占位符，实际逻辑在 main.py 中实现
        pass

    async def broadcast_status(self, user_id: str, status: str):
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

    async def notify_unread(self, user_id: str, conversation_id: int, count: int):
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
            
            participant1_id = conversation.participant1_id
            participant2_id = conversation.participant2_id
        
        # 构造已读通知消息
        read_message = {
            "type": "read",
            "conversation_id": conversation_id,
            "reader_id": reader_id,  # 谁标记的已读
            "timestamp": int(time.time())
        }
        
        # 通知会话的另一方（发送者）
        if reader_id == participant1_id:
            # 参与者1标记已读 → 通知参与者2
            await self.send_personal_message(read_message, participant2_id)
        else:
            # 参与者2标记已读 → 通知参与者1
            await self.send_personal_message(read_message, participant1_id)

    def is_online(self, user_id: str) -> bool:
        """检查用户是否在线"""
        return user_id in self.online_users


# 全局连接管理器实例
manager = ConnectionManager()
