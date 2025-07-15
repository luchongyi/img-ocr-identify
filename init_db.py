import asyncio
from app.core.db import engine
from app.models.api_key import Base as APIKeyBase, APIKey
from app.models.ip_whitelist import Base as IPWhitelistBase, IPWhitelist
from app.models.user import Base as UserBase, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta

async def init():
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(APIKeyBase.metadata.create_all)
        await conn.run_sync(IPWhitelistBase.metadata.create_all)
        await conn.run_sync(UserBase.metadata.create_all)
    
    # 插入默认API Key（兼容新字段）
    async with AsyncSession(engine) as session:
        result = await session.execute(select(APIKey).where(APIKey.key == "your-secret-key"))
        if not result.scalar_one_or_none():
            session.add(APIKey(
                key="your-secret-key",
                description="默认Key",
                user_id=None,
                expires_at=datetime.utcnow() + timedelta(days=365),
                is_active=True
            ))
            await session.commit()
    
    # 插入默认IP白名单
    async with AsyncSession(engine) as session:
        # 检查是否已有IP白名单数据
        result = await session.execute(select(IPWhitelist))
        if not result.scalars().first():
            # 添加默认IP地址
            default_ips = [
                IPWhitelist(ip_address="127.0.0.1", description="本地测试", created_by="system"),
                IPWhitelist(ip_address="::1", description="本地IPv6测试", created_by="system"),
            ]
            for ip in default_ips:
                session.add(ip)
            await session.commit()
            print("✅ 已创建默认IP白名单")
    
    # 插入默认用户
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        if not result.scalar_one_or_none():
            import bcrypt
            password = "admin123"
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            session.add(User(username="admin", password_hash=password_hash))
            await session.commit()
            print("✅ 已创建默认用户：admin / admin123")

if __name__ == "__main__":
    asyncio.run(init())