import ipaddress
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class IPWhitelistCache:
    """IP白名单缓存管理器"""
    
    def __init__(self, cache_ttl: int = 300):  # 5分钟缓存
        self.cache_ttl = cache_ttl
        self.cache = {}
        self.last_update = None
        self._lock = asyncio.Lock()
    
    def is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not self.last_update:
            return False
        return datetime.now() - self.last_update < timedelta(seconds=self.cache_ttl)
    
    async def update_cache(self, whitelist_data: List[Dict]):
        """更新缓存"""
        async with self._lock:
            self.cache = {
                ip_data['ip_address']: {
                    'description': ip_data.get('description'),
                    'is_active': ip_data.get('is_active', True)
                }
                for ip_data in whitelist_data
                if ip_data.get('is_active', True)
            }
            self.last_update = datetime.now()
            logger.info(f"IP白名单缓存已更新，共 {len(self.cache)} 个活跃IP")
    
    async def update_cache_from_db(self, db):
        """从数据库主动刷新缓存（需传db会话）"""
        from app.services.ip_whitelist_service import IPWhitelistService
        active_ips = await IPWhitelistService.get_active_whitelist_ips(db)
        await self.update_cache(active_ips)
    
    async def is_ip_allowed(self, client_ip: str, db) -> bool:
        """检查IP是否在白名单中（使用缓存，缓存过期时自动刷新）"""
        if not self.is_cache_valid():
            try:
                await self.update_cache_from_db(db)
                logger.info("IP白名单缓存已自动刷新")
            except Exception as e:
                logger.error(f"刷新IP白名单缓存失败: {e}")
                return False  # 刷新失败时默认拒绝
        try:
            client_ip_obj = ipaddress.ip_address(client_ip)
            for whitelist_ip, config in self.cache.items():
                try:
                    whitelist_ip_obj = ipaddress.ip_address(whitelist_ip)
                    if client_ip_obj == whitelist_ip_obj:
                        return True
                except ValueError:
                    try:
                        network = ipaddress.ip_network(whitelist_ip, strict=False)
                        if client_ip_obj in network:
                            return True
                    except ValueError:
                        logger.warning(f"无效的IP地址: {whitelist_ip}")
                        continue
            return False
        except ValueError:
            logger.warning(f"无效的客户端IP地址: {client_ip}")
            return False
    
    def get_cache_info(self) -> Dict:
        """获取缓存信息"""
        return {
            'cache_size': len(self.cache),
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'is_valid': self.is_cache_valid(),
            'ttl_seconds': self.cache_ttl
        }

# 全局缓存实例
ip_cache = IPWhitelistCache() 