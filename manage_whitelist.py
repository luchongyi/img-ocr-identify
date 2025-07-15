#!/usr/bin/env python3
"""
IP白名单管理工具 - 数据库+缓存方案
使用方法：
python manage_whitelist.py add <ip> [description]
python manage_whitelist.py remove <ip>
python manage_whitelist.py list
python manage_whitelist.py refresh-cache
python manage_whitelist.py cache-info
"""

import asyncio
import sys
from app.core.db import engine
from app.services.ip_whitelist_service import IPWhitelistService
from sqlalchemy.ext.asyncio import AsyncSession


def print_usage():
    """打印使用说明"""
    print("""
🔧 IP白名单管理工具 - 数据库+缓存方案

使用方法:
  python manage_whitelist.py add <ip> [description]  # 添加IP到白名单
  python manage_whitelist.py remove <ip>             # 从白名单移除IP
  python manage_whitelist.py list                    # 列出所有IP白名单
  python manage_whitelist.py refresh-cache           # 刷新缓存
  python manage_whitelist.py cache-info              # 查看缓存信息

示例:
  python manage_whitelist.py add 192.168.1.100 "内网服务器"
  python manage_whitelist.py add 10.0.0.0/24 "内网段"
  python manage_whitelist.py remove 192.168.1.100
  python manage_whitelist.py list
  python manage_whitelist.py refresh-cache
""")

async def add_ip(ip: str, description: str = ""):
    """添加IP到白名单"""
    async with AsyncSession(engine) as session:
        success = await IPWhitelistService.add_ip_to_whitelist(
            session, ip, description, "cli"
        )
        if success:
            print(f"✅ IP {ip} 已成功添加到白名单")
        else:
            print(f"❌ IP {ip} 添加失败，可能已存在或格式错误")
            sys.exit(1)

async def remove_ip(ip: str):
    """从白名单中移除IP"""
    async with AsyncSession(engine) as session:
        success = await IPWhitelistService.remove_ip_from_whitelist(session, ip)
        if success:
            print(f"✅ IP {ip} 已从白名单移除")
        else:
            print(f"❌ IP {ip} 移除失败，可能不存在或已被移除")
            sys.exit(1)

async def list_ips():
    """列出所有IP白名单"""
    async with AsyncSession(engine) as session:
        ips = await IPWhitelistService.get_all_whitelist_ips(session)
        
        if not ips:
            print("📝 白名单为空")
            return
        
        print("📋 IP白名单列表:")
        print("-" * 100)
        print(f"{'ID':<5} {'IP地址':<20} {'状态':<8} {'描述':<30} {'创建者':<15} {'创建时间'}")
        print("-" * 100)
        
        for ip in ips:
            status = "✅ 活跃" if ip['is_active'] else "❌ 禁用"
            description = ip['description'] or "无描述"
            created_by = ip['created_by'] or "未知"
            created_time = ip['created_at'].strftime('%Y-%m-%d %H:%M')
            print(f"{ip['id']:<5} {ip['ip_address']:<20} {status:<8} {description:<30} {created_by:<15} {created_time}")

async def refresh_cache():
    """刷新缓存"""
    async with AsyncSession(engine) as session:
        await IPWhitelistService.refresh_cache(session)
        print("✅ IP白名单缓存已刷新")

def show_cache_info():
    """显示缓存信息"""
    cache_info = IPWhitelistService.get_cache_info()
    print("📊 缓存信息:")
    print(f"  缓存大小: {cache_info['cache_size']} 个IP")
    print(f"  最后更新: {cache_info['last_update'] or '从未更新'}")
    print(f"  缓存有效: {'✅ 是' if cache_info['is_valid'] else '❌ 否'}")
    print(f"  TTL时间: {cache_info['ttl_seconds']} 秒")

async def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "add":
        if len(sys.argv) < 3:
            print("❌ 请提供IP地址")
            print_usage()
            sys.exit(1)
        
        ip = sys.argv[2]
        description = sys.argv[3] if len(sys.argv) > 3 else ""
        await add_ip(ip, description)
    
    elif command == "remove":
        if len(sys.argv) < 3:
            print("❌ 请提供要移除的IP地址")
            print_usage()
            sys.exit(1)
        
        ip = sys.argv[2]
        await remove_ip(ip)
    
    elif command == "list":
        await list_ips()
    
    elif command == "refresh-cache":
        await refresh_cache()
    
    elif command == "cache-info":
        show_cache_info()
    
    else:
        print(f"❌ 未知命令: {command}")
        print_usage()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())