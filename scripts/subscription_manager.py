#!/usr/bin/env python3
"""
AI洞察日报订阅管理脚本
==========================
管理订阅用户、发送日志、订阅状态

使用方式:
  python scripts/subscription_manager.py list                    # 列出所有活跃订阅用户
  python scripts/subscription_manager.py add shenlang            # 添加订阅用户
  python scripts/subscription_manager.py remove shenlang         # 取消订阅
  python scripts/subscription_manager.py status shenlang         # 查询订阅状态
  python scripts/subscription_manager.py log 2026-04-17         # 查看发送日志

作者: 林克（沈浪的AI分身）
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

try:
    from appwrite.client import Client
    from appwrite.services.databases import Databases
    from appwrite.query import Query
except ImportError:
    print("❌ 请先安装 appwrite SDK: pip install appwrite")
    raise SystemExit(1)

# 项目路径配置
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from config import APPWRITE_ENDPOINT, APPWRITE_PROJECT_ID

# Appwrite 配置
DATABASE_ID = "INTERNAL_DATABASE_ID"
SUBSCRIBERS_COLLECTION = "INTERNAL_COLLECTION_ID"
LOGS_COLLECTION = "send_logs"


class SubscriptionManager:
    """订阅管理器"""
    
    def __init__(self):
        self.client = Client()
        self.client.set_endpoint(APPWRITE_ENDPOINT)
        self.client.set_project(APPWRITE_PROJECT_ID)
        self.db = Databases(self.client)
    
    async def list_subscribers(self, active_only: bool = True) -> List[Dict]:
        """获取订阅用户列表"""
        from appwrite.services.tables_db import TablesDB
        tables_db = TablesDB(self.client)
        
        queries = []
        if active_only:
            queries.append(Query.equal("is_active", True))
        
        queries.extend([
            Query.order_desc("subscribed_at"),
            Query.limit(1000)
        ])
        
        try:
            result = tables_db.list_rows(
                database_id=DATABASE_ID,
                table_id=SUBSCRIBERS_COLLECTION,
                queries=queries
            )
            return result.get("rows", [])
        except Exception as e:
            print(f"❌ 获取订阅列表失败: {e}")
            return []
    
    async def add_subscriber(self, username: str, employee_name: Optional[str] = None) -> bool:
        """添加订阅用户"""
        try:
            # 检查是否已存在
            existing = await self._get_subscriber_by_username(username)
            
            # 使用 tablesDB API（Appwrite 1.8+）
            from appwrite.services.tables_db import TablesDB
            tables_db = TablesDB(self.client)
            
            if existing:
                # 已存在，激活订阅
                tables_db.update_row(
                    database_id=DATABASE_ID,
                    table_id=SUBSCRIBERS_COLLECTION,
                    row_id=existing["$id"],
                    data={
                        "is_active": True,
                        "subscribed_at": datetime.now().isoformat()
                    }
                )
                print(f"✅ 订阅已重新激活: {username}")
            else:
                # 新增订阅
                tables_db.create_row(
                    database_id=DATABASE_ID,
                    table_id=SUBSCRIBERS_COLLECTION,
                    row_id="unique()",
                    data={
                        "username": username,
                        "employee_name": employee_name or "",
                        "subscribed_at": datetime.now().isoformat(),
                        "is_active": True,
                        "preferences": "{}"
                    }
                )
                print(f"✅ 订阅成功: {username}")
            
            return True
        except Exception as e:
            print(f"❌ 添加订阅失败: {e}")
            return False
    
    async def remove_subscriber(self, username: str) -> bool:
        """取消订阅"""
        try:
            existing = await self._get_subscriber_by_username(username)
            
            if not existing:
                print(f"⚠️ 用户未订阅: {username}")
                return False
            
            # 标记为不活跃
            from appwrite.services.tables_db import TablesDB
            tables_db = TablesDB(self.client)
            
            tables_db.update_row(
                database_id=DATABASE_ID,
                table_id=SUBSCRIBERS_COLLECTION,
                row_id=existing["$id"],
                data={
                    "is_active": False
                }
            )
            print(f"✅ 已取消订阅: {username}")
            return True
        except Exception as e:
            print(f"❌ 取消订阅失败: {e}")
            return False
    
    async def get_status(self, username: str) -> Optional[Dict]:
        """查询订阅状态"""
        try:
            existing = await self._get_subscriber_by_username(username)
            
            if not existing:
                return None
            
            return {
                "username": existing.get("username"),
                "employee_name": existing.get("employee_name"),
                "is_subscribed": existing.get("is_active", False),
                "subscribed_at": existing.get("subscribed_at"),
                "preferences": json.loads(existing.get("preferences", "{}"))
            }
        except Exception as e:
            print(f"❌ 查询状态失败: {e}")
            return None
    
    async def log_send_status(
        self, 
        date: str, 
        username: str, 
        status: str, 
        error_message: Optional[str] = None
    ) -> bool:
        """记录发送状态"""
        try:
            from appwrite.services.tables_db import TablesDB
            tables_db = TablesDB(self.client)
            
            tables_db.create_row(
                database_id=DATABASE_ID,
                table_id=LOGS_COLLECTION,
                row_id="unique()",
                data={
                    "date": date,
                    "username": username,
                    "status": status,
                    "sent_at": datetime.now().isoformat(),
                    "error_message": error_message or ""
                }
            )
            return True
        except Exception as e:
            print(f"❌ 记录日志失败: {e}")
            return False
    
    async def get_send_logs(self, date: str) -> List[Dict]:
        """获取发送日志"""
        from appwrite.services.tables_db import TablesDB
        tables_db = TablesDB(self.client)
        
        try:
            result = tables_db.list_rows(
                database_id=DATABASE_ID,
                table_id=LOGS_COLLECTION,
                queries=[
                    Query.equal("date", date),
                    Query.order_desc("sent_at"),
                    Query.limit(1000)
                ]
            )
            return result.get("rows", [])
        except Exception as e:
            print(f"❌ 获取日志失败: {e}")
            return []
    
    async def _get_subscriber_by_username(self, username: str) -> Optional[Dict]:
        """根据用户名获取订阅记录"""
        from appwrite.services.tables_db import TablesDB
        tables_db = TablesDB(self.client)
        
        try:
            result = tables_db.list_rows(
                database_id=DATABASE_ID,
                table_id=SUBSCRIBERS_COLLECTION,
                queries=[
                    Query.equal("username", username),
                    Query.limit(1)
                ]
            )
            rows = result.get("rows", [])
            return rows[0] if rows else None
        except Exception:
            return None


async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    manager = SubscriptionManager()
    command = sys.argv[1]
    
    if command == "list":
        # 列出所有订阅用户
        subscribers = await manager.list_subscribers()
        
        if not subscribers:
            print("📭 暂无订阅用户")
            return
        
        print(f"📧 订阅用户列表（共{len(subscribers)}人）")
        print("=" * 50)
        
        for i, sub in enumerate(subscribers, 1):
            username = sub.get("username", "unknown")
            employee_name = sub.get("employee_name", "")
            subscribed_at = sub.get("subscribed_at", "")[:10]
            name_display = f"（{employee_name}）" if employee_name else ""
            print(f"{i}. {username}{name_display} - {subscribed_at}")
    
    elif command == "add":
        # 添加订阅
        if len(sys.argv) < 3:
            print("❌ 缺少用户名参数")
            print("💡 用法: python scripts/subscription_manager.py add <username>")
            return
        
        username = sys.argv[2]
        employee_name = sys.argv[3] if len(sys.argv) > 3 else None
        await manager.add_subscriber(username, employee_name)
    
    elif command == "remove":
        # 取消订阅
        if len(sys.argv) < 3:
            print("❌ 缺少用户名参数")
            print("💡 用法: python scripts/subscription_manager.py remove <username>")
            return
        
        username = sys.argv[2]
        await manager.remove_subscriber(username)
    
    elif command == "status":
        # 查询订阅状态
        if len(sys.argv) < 3:
            print("❌ 缺少用户名参数")
            print("💡 用法: python scripts/subscription_manager.py status <username>")
            return
        
        username = sys.argv[2]
        status = await manager.get_status(username)
        
        if not status:
            print(f"📭 用户 {username} 未订阅")
        else:
            subscribed = "✅ 已订阅" if status["is_subscribed"] else "❌ 已取消"
            print(f"📧 订阅状态: {subscribed}")
            print(f"   用户名: {status['username']}")
            print(f"   订阅时间: {status['subscribed_at']}")
    
    elif command == "log":
        # 查看发送日志
        if len(sys.argv) < 3:
            date = datetime.now().strftime("%Y-%m-%d")
        else:
            date = sys.argv[2]
        
        logs = await manager.get_send_logs(date)
        
        if not logs:
            print(f"📭 {date} 暂无发送记录")
            return
        
        success_count = sum(1 for log in logs if log["status"] == "success")
        failed_count = len(logs) - success_count
        
        print(f"📊 {date} 发送统计")
        print("=" * 50)
        print(f"✅ 成功: {success_count}")
        print(f"❌ 失败: {failed_count}")
        print()
        
        for log in logs:
            username = log.get("username")
            status = log.get("status")
            sent_at = log.get("sent_at", "")[:19]
            error = log.get("error_message", "")
            
            status_icon = "✅" if status == "success" else "❌"
            print(f"{status_icon} {username} - {sent_at}")
            if error:
                print(f"   错误: {error}")
    
    else:
        print(f"❌ 未知命令: {command}")
        print(__doc__)


if __name__ == "__main__":
    asyncio.run(main())
