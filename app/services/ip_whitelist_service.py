from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core import db
from app.models.ip_whitelist import IPWhitelist
from app.core.ip_cache import ip_cache
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class IPWhitelistService:
    """IP白名单服务"""
    
    @staticmethod
    async def get_all_whitelist_ips(db: AsyncSession) -> List[Dict]:
        """获取所有IP白名单"""
        try:
            result = await db.execute(select(IPWhitelist))
            ips = result.scalars().all()
            return [
                {
                    'id': ip.id,
                    'ip_address': ip.ip_address,
                    'description': ip.description,
                    'is_active': ip.is_active,
                    'created_at': ip.created_at,
                    'updated_at': ip.updated_at,
                    'created_by': ip.created_by
                }
                for ip in ips
            ]
        except Exception as e:
            logger.error(f"获取IP白名单失败: {e}")
            return []
    
    @staticmethod
    async def get_active_whitelist_ips(db: AsyncSession) -> List[Dict]:
        """获取活跃的IP白名单"""
        try:
            result = await db.execute(
                select(IPWhitelist).where(IPWhitelist.is_active == True)
            )
            ips = result.scalars().all()
            return [
                {
                    'ip_address': ip.ip_address,
                    'description': ip.description,
                    'is_active': ip.is_active
                }
                for ip in ips
            ]
        except Exception as e:
            logger.error(f"获取活跃IP白名单失败: {e}")
            return []
    
    @staticmethod
    async def add_ip_to_whitelist(
        db: AsyncSession, 
        ip_address: str, 
        description: Optional[str] = None,
        created_by: str = "system"
    ) -> bool:
        """添加IP到白名单"""
        try:
            # 检查是否已存在
            result = await db.execute(
                select(IPWhitelist).where(IPWhitelist.ip_address == ip_address)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                if not existing.is_active:
                    # 重新激活已存在的IP
                    existing.is_active = True
                    existing.description = description
                    await db.commit()
                    logger.info(f"IP {ip_address} 已重新激活")
                else:
                    logger.warning(f"IP {ip_address} 已存在于白名单中")
                    return False
            else:
                # 添加新的IP
                new_ip = IPWhitelist(
                    ip_address=ip_address,
                    description=description,
                    created_by=created_by
                )
                db.add(new_ip)
                await db.commit()
                logger.info(f"IP {ip_address} 已添加到白名单")
            
            # 更新缓存
            await IPWhitelistService._update_cache(db)
            return True
            
        except Exception as e:
            logger.error(f"添加IP到白名单失败: {e}")
            return False
    
    @staticmethod
    async def remove_ip_from_whitelist(db: AsyncSession, ip_address: str) -> bool:
        """从白名单中移除IP（软删除）"""
        try:
            result = await db.execute(
                select(IPWhitelist).where(IPWhitelist.ip_address == ip_address)
            )
            ip_obj = result.scalar_one_or_none()
            
            if ip_obj and ip_obj.is_active:
                ip_obj.is_active = False
                await db.commit()
                logger.info(f"IP {ip_address} 已从白名单移除")
                
                # 更新缓存
                await IPWhitelistService._update_cache(db)
                return True
            
            logger.warning(f"IP {ip_address} 不存在或已被移除")
            return False
            
        except Exception as e:
            logger.error(f"从白名单移除IP失败: {e}")
            return False
    
    @staticmethod
    async def update_ip_description(
        db: AsyncSession, 
        ip_address: str, 
        description: str
    ) -> bool:
        """更新IP描述"""
        try:
            result = await db.execute(
                select(IPWhitelist).where(IPWhitelist.ip_address == ip_address)
            )
            ip_obj = result.scalar_one_or_none()
            
            if ip_obj:
                ip_obj.description = description
                await db.commit()
                logger.info(f"IP {ip_address} 描述已更新")
                
                # 更新缓存
                await IPWhitelistService._update_cache(db)
                return True
            
            logger.warning(f"IP {ip_address} 不存在")
            return False
            
        except Exception as e:
            logger.error(f"更新IP描述失败: {e}")
            return False
    
    @staticmethod
    async def _update_cache(db: AsyncSession):
        """更新缓存"""
        try:
            active_ips = await IPWhitelistService.get_active_whitelist_ips(db)
            await ip_cache.update_cache(active_ips)
        except Exception as e:
            logger.error(f"更新缓存失败: {e}")
    
    @staticmethod
    async def refresh_cache(db: AsyncSession):
        """刷新缓存"""
        await IPWhitelistService._update_cache(db)
        logger.info("IP白名单缓存已刷新")
    
    @staticmethod
    def is_ip_allowed(client_ip: str) -> bool:
        """检查IP是否允许访问（使用缓存）"""
        return ip_cache.is_ip_allowed(client_ip, db)
    
    @staticmethod
    def get_cache_info() -> Dict:
        """获取缓存信息"""
        return ip_cache.get_cache_info()