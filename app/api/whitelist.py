from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.services.ip_whitelist_service import IPWhitelistService
from app.core.security import verify_api_key
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class IPWhitelistRequest(BaseModel):
    ip_address: str
    description: Optional[str] = None

class IPWhitelistResponse(BaseModel):
    id: int
    ip_address: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

class CacheInfoResponse(BaseModel):
    cache_size: int
    last_update: Optional[str]
    is_valid: bool
    ttl_seconds: int

@router.get("/whitelist/list", response_model=List[IPWhitelistResponse])
async def list_whitelist_ips(db: AsyncSession = Depends(get_db)):
    """获取所有IP白名单"""
    ips = await IPWhitelistService.get_all_whitelist_ips(db)
    return [IPWhitelistResponse(**ip) for ip in ips]

@router.post("/whitelist/add")
async def add_ip(
    request: IPWhitelistRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """添加IP到白名单"""
    success = await IPWhitelistService.add_ip_to_whitelist(
        db, 
        request.ip_address, 
        request.description or "",
        "api"
    )
    if success:
        return {"success": True, "message": f"IP {request.ip_address} 已添加到白名单"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"IP {request.ip_address} 添加失败，可能已存在或格式错误"
        )

@router.delete("/whitelist/remove/{ip_address}")
async def remove_ip(
    ip_address: str,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """从白名单中移除IP"""
    success = await IPWhitelistService.remove_ip_from_whitelist(db, ip_address)
    if success:
        return {"success": True, "message": f"IP {ip_address} 已从白名单移除"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IP {ip_address} 不存在或已被移除"
        )

@router.put("/whitelist/update/{ip_address}")
async def update_ip_description(
    ip_address: str,
    request: IPWhitelistRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """更新IP描述"""
    success = await IPWhitelistService.update_ip_description(
        db, ip_address, request.description or ""
    )
    if success:
        return {"success": True, "message": f"IP {ip_address} 描述已更新"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IP {ip_address} 不存在"
        )

@router.post("/whitelist/refresh-cache")
async def refresh_cache(db: AsyncSession = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """刷新IP白名单缓存"""
    await IPWhitelistService.refresh_cache(db)
    return {"success": True, "message": "缓存已刷新"}

@router.get("/whitelist/cache-info", response_model=CacheInfoResponse)
async def get_cache_info():
    """获取缓存信息"""
    return CacheInfoResponse(**IPWhitelistService.get_cache_info())