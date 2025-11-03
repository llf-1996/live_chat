"""
修改用户密码脚本

使用方法:
    python change_password.py <用户ID> <新密码>
    或
    python change_password.py  # 交互式输入
"""
import asyncio
import sys
import os
from pathlib import Path
from getpass import getpass
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))


async def change_user_password(user_id: str, new_password: str):
    """修改用户密码"""
    # 在函数内导入，避免过早初始化数据库连接
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import select
        from app.models import User
        from app.auth import hash_password
    except ModuleNotFoundError as e:
        print(f"\n❌ 缺少必要的依赖模块: {e}")
        print("\n请先安装依赖:")
        print("  pip install -r requirements.txt")
        print("\n或者安装特定模块:")
        print("  pip install aiomysql sqlalchemy passlib[bcrypt]")
        return False
    
    # 从环境变量读取数据库 URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ 错误：DATABASE_URL 环境变量未设置")
        print("请在 .env 文件中配置数据库连接信息")
        return False
    
    # 创建数据库连接
    engine = create_async_engine(database_url, echo=False)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as db:
        try:
            # 查询用户是否存在
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"❌ 错误: 用户ID '{user_id}' 不存在")
                return False
            
            # 显示用户信息
            print(f"\n📋 找到用户:")
            print(f"  - ID: {user.id}")
            print(f"  - 用户名: {user.username}")
            print(f"  - 角色: {user.role}")
            
            # 确认修改
            confirm = input(f"\n⚠️  确定要修改此用户的密码吗? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y', '是']:
                print("❌ 操作已取消")
                return False
            
            # 加密新密码
            print("\n🔐 正在加密新密码...")
            password_hash = hash_password(new_password)
            
            # 更新密码
            user.password_hash = password_hash
            await db.commit()
            
            print(f"\n✅ 密码修改成功!")
            print(f"  - 用户ID: {user.id}")
            print(f"  - 用户名: {user.username}")
            print(f"  - 新密码: {new_password}")
            
            # 如果是管理员，提示登录地址
            if user.role == "admin":
                print(f"\n🌐 管理员登录地址:")
                print(f"  http://localhost:5173/login")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 修改密码失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await engine.dispose()


def main():
    """主函数"""
    print("=" * 60)
    print("🔑 修改用户密码工具")
    print("=" * 60)
    
    # 解析命令行参数
    if len(sys.argv) == 3:
        # 命令行模式
        user_id = sys.argv[1].strip()
        new_password = sys.argv[2].strip()
    else:
        # 交互式模式
        print("\n请输入以下信息：")
        user_id = input("用户ID: ").strip()
        
        # 使用 getpass 隐藏密码输入
        new_password = getpass("新密码: ").strip()
        new_password_confirm = getpass("确认新密码: ").strip()
        
        # 验证两次密码是否一致
        if new_password != new_password_confirm:
            print("\n❌ 错误: 两次输入的密码不一致")
            return
    
    # 验证输入
    if not user_id:
        print("\n❌ 错误: 用户ID不能为空")
        return
    
    if not new_password:
        print("\n❌ 错误: 密码不能为空")
        return
    
    if len(new_password) < 6:
        print("\n❌ 错误: 密码长度至少为 6 位")
        return
    
    # 执行密码修改
    result = asyncio.run(change_user_password(user_id, new_password))
    
    # 如果失败，退出程序
    if not result:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  操作已中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

