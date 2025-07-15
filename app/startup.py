import asyncio
import logging
from app.core.db import engine
from app.services.ip_whitelist_service import IPWhitelistService
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

async def init_cache():
    """初始化IP白名单缓存"""
    try:
        async with AsyncSession(engine) as session:
            await IPWhitelistService.refresh_cache(session)
            logger.info("✅ IP白名单缓存初始化完成")
    except Exception as e:
        logger.error(f"❌ IP白名单缓存初始化失败: {e}")

async def startup_event():
    """应用启动事件"""
    logger.info("🚀 应用启动中...")
    await init_cache()
    logger.info("✅ 应用启动完成")

async def shutdown_event():
    """应用关闭事件"""
    logger.info("🛑 应用关闭中...")
    logger.info("✅ 应用关闭完成")