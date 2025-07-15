from fastapi import Depends, HTTPException, status, Request
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.future import select
from app.core.db import get_db
from app.models.api_key import APIKey
from sqlalchemy.ext.asyncio import AsyncSession
from config.config import settings
from app.services.ip_whitelist_service import IPWhitelistService
import logging
from datetime import datetime
import hashlib
import secrets

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-KEY")

# 安全配置
MAX_REQUESTS_PER_MINUTE = 25
REQUEST_LOG_ENABLED = True

def get_client_ip(request: Request) -> str:
    """获取客户端真实IP地址"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def log_api_request(request: Request, api_key: str, success: bool):
    """记录API请求日志"""
    if not REQUEST_LOG_ENABLED:
        return
    
    client_ip = get_client_ip(request)
    timestamp = datetime.now().isoformat()
    
    # 记录请求信息（不记录敏感数据）
    log_data = {
        "timestamp": timestamp,
        "client_ip": client_ip,
        "method": request.method,
        "path": request.url.path,
        "api_key_hash": hashlib.sha256(api_key.encode()).hexdigest()[:8],  # 只记录哈希值前8位
        "success": success,
        "user_agent": request.headers.get("User-Agent", "Unknown")
    }
    
    logger.info(f"API Request: {log_data}")

async def verify_api_key(
    request: Request,
    api_key: str = Depends(api_key_header),
    db: AsyncSession = Depends(get_db)
):
    """验证API密钥和IP白名单"""
    try:
        # 检查IP白名单（使用缓存）
        client_ip = get_client_ip(request)
        if not IPWhitelistService.is_ip_allowed(client_ip):
            logger.warning(f"Unauthorized IP access attempt: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"IP地址 {client_ip} 不在白名单中"
            )
        
        # 验证API密钥（增加有效期判断）
        now = datetime.utcnow()
        result = await db.execute(select(APIKey).where(
            APIKey.key == api_key,
            APIKey.is_active == True,
            (APIKey.expires_at == None) | (APIKey.expires_at > now)
        ))
        key_obj = result.scalar_one_or_none()
        
        if not key_obj:
            log_api_request(request, api_key, False)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效或已过期的API密钥"
            )
        
        # 记录成功的请求
        log_api_request(request, api_key, True)
        
        return api_key
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API key verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )

def generate_secure_api_key() -> str:
    """生成安全的API密钥"""
    return secrets.token_urlsafe(32)

def validate_api_key_format(api_key: str) -> bool:
    """验证API密钥格式"""
    # 检查长度和字符集
    if len(api_key) < 32:
        return False
    return True