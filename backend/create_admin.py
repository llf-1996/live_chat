"""
创建管理员账号的命令行工具

使用方法：
    python create_admin.py <user_id> <username> <password>
    
或交互式创建：
    python create_admin.py
"""
import sys
import asyncio
from getpass import getpass
from sqlalchemy import select
from app.database import async_session_maker, init_db
from app.models import User, UserRole
from app.auth import hash_password


async def create_admin_user(user_id: str, username: str, password: str):
    """
    创建管理员账号
    
    Args:
        user_id: 用户ID
        username: 用户名
        password: 密码
    """
    async with async_session_maker() as db:
        # 检查用户ID是否已存在
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"❌ 错误：用户ID '{user_id}' 已存在")
            return False
        
        # 检查用户名是否已存在
        result = await db.execute(
            select(User).where(User.username == username)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"❌ 错误：用户名 '{username}' 已存在")
            return False
        
        # 加密密码
        try:
            password_hash = hash_password(password)
        except Exception as e:
            print(f"❌ 加密密码失败：{e}")
            return False
        
        # 创建管理员用户
        admin_user = User(
            id=user_id,
            username=username,
            password_hash=password_hash,
            role=UserRole.ADMIN,
            description="平台管理员",
            status="active"
        )
        
        db.add(admin_user)
        await db.commit()
        
        print("\n✅ 管理员账号创建成功！")
        print(f"   用户ID: {user_id}")
        print(f"   用户名: {username}")
        print(f"   密码: {'*' * len(password)}")
        print(f"   角色: 管理员")
        print("\n现在可以使用该账号登录客服后台")
        print("   (访问前端登录页面，默认: http://localhost:5173/login)")
        
        return True


async def main():
    """主函数"""
    print("=" * 60)
    print("  在线客服系统 - 创建管理员账号")
    print("=" * 60)
    print()
    
    # 初始化数据库
    print("正在初始化数据库...")
    await init_db()
    print("✓ 数据库初始化完成\n")
    
    # 获取用户ID、用户名和密码
    if len(sys.argv) >= 4:
        # 命令行参数模式：python create_admin.py <user_id> <username> <password>
        user_id = sys.argv[1]
        username = sys.argv[2]
        password = sys.argv[3]
        print(f"用户ID: {user_id}")
        print(f"用户名: {username}")
        print(f"密码: {'*' * len(password)}")
        print()
    else:
        # 交互式模式
        print("请输入管理员账号信息：\n")
        
        user_id = input("用户ID: ").strip()
        
        if not user_id:
            print("❌ 错误：用户ID不能为空")
            return
        
        username = input("用户名: ").strip()
        
        if not username:
            print("❌ 错误：用户名不能为空")
            return
        
        password = getpass("密码: ").strip()
        
        if not password:
            print("❌ 错误：密码不能为空")
            return
        
        password_confirm = getpass("确认密码: ").strip()
        
        if password != password_confirm:
            print("❌ 错误：两次输入的密码不一致")
            return
        
        print()
    
    # 创建管理员账号
    print("正在创建管理员账号...")
    await create_admin_user(user_id, username, password)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

