#!/usr/bin/env python3
"""
KIM API 公共客户端模块
====================
抽取所有推送脚本共用的 KIM OpenAPI 操作，消除代码重复。

包含:
- 凭证加载（环境变量 > .env 文件 > 硬编码回退）
- Token 获取
- 群列表查询
- 消息发送（带重试）

使用:
    from kim_client import KimConfig, get_access_token, get_bot_groups, send_to_group_with_retry, send_to_user

作者: 林克 (沈浪的AI分身)
版本: 1.0.0
"""

import asyncio
import os
from pathlib import Path
from typing import Optional

try:
    import httpx
except ImportError:
    print("Please install httpx: pip install httpx")
    raise SystemExit(1)


# ============ 配置加载 ============

def _load_env_file():
    """从 .env 文件加载环境变量（简易实现，无需 python-dotenv）"""
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value and key not in os.environ:
                os.environ[key] = value


# 启动时尝试加载 .env
_load_env_file()


class KimConfig:
    """KIM API 配置，优先级: 环境变量 > .env 文件"""
    APP_KEY: str = os.environ.get("KIM_APP_KEY", "")
    SECRET_KEY: str = os.environ.get("KIM_SECRET_KEY", "")
    GATEWAY_URL: str = os.environ.get("KIM_GATEWAY_URL", "https://is-gateway.corp.kuaishou.com")

    # 推送配置
    SEND_INTERVAL: float = 2.5   # 群间发送间隔(秒)
    MAX_RETRIES: int = 3         # 最大重试次数
    RETRY_DELAY: float = 5.0     # 重试间隔(秒)

    @classmethod
    def validate(cls):
        """校验凭证是否已配置"""
        if not cls.APP_KEY or not cls.SECRET_KEY:
            print("KIM credentials not configured.")
            print("Please set environment variables KIM_APP_KEY and KIM_SECRET_KEY,")
            print("or create scripts/.env from scripts/.env.template")
            raise SystemExit(1)


# ============ API 调用 ============

async def get_access_token() -> str:
    """获取林克应用的 Access Token"""
    KimConfig.validate()
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{KimConfig.GATEWAY_URL}/token/get",
            headers={"Content-Type": "application/json"},
            json={
                "appKey": KimConfig.APP_KEY,
                "secretKey": KimConfig.SECRET_KEY,
                "grantType": "client_credentials"
            }
        )
        result = resp.json()
        if result.get("code") == 0:
            return result["result"]["accessToken"]
        raise Exception(f"Token获取失败: {result}")


async def get_bot_groups(token: str) -> list:
    """获取林克机器人所在的所有群（包含群名）"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{KimConfig.GATEWAY_URL}/openapi/v2/group/bot/list",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            json={"pageSize": 50}
        )
        result = resp.json()
        if result.get("code") == 0:
            groups = result.get("data", {}).get("groups", [])
            return [
                {
                    "groupId": g.get("groupId", ""),
                    "groupName": g.get("name", "未知群"),
                    "memberCount": g.get("userCount", 0)
                }
                for g in groups
            ]
        return []


async def send_to_user(
    token: str,
    username: str,
    card: dict,
    dry_run: bool = False
) -> bool:
    """发送消息到个人"""
    if dry_run:
        print(f"   [DRY-RUN] 将发送到用户: {username}")
        return True

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{KimConfig.GATEWAY_URL}/openapi/v2/message/send",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            json={
                "username": username,
                "msgType": "mixCard",
                "mixCard": card
            }
        )
        result = resp.json()
        if result.get("code") == 0:
            return True
        print(f"   Failed: {result}")
        return False


async def send_to_group_with_retry(
    token: str,
    group_id: str,
    group_name: str,
    card: dict,
    dry_run: bool = False
) -> bool:
    """发送消息到群，带重试机制"""
    if dry_run:
        print(f"   [DRY-RUN] 将发送到: {group_name} ({group_id})")
        return True

    for attempt in range(KimConfig.MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{KimConfig.GATEWAY_URL}/openapi/v2/message/send",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}"
                    },
                    json={
                        "groupId": group_id,
                        "msgType": "mixCard",
                        "mixCard": card
                    }
                )
                result = resp.json()

                if result.get("code") == 0:
                    return True

                if result.get("code") == 42900:
                    if attempt < KimConfig.MAX_RETRIES - 1:
                        print(f"   Rate limited, retry in {KimConfig.RETRY_DELAY}s ({attempt + 1}/{KimConfig.MAX_RETRIES})")
                        await asyncio.sleep(KimConfig.RETRY_DELAY)
                        continue
                    else:
                        print(f"   Retried {KimConfig.MAX_RETRIES} times, still failed: {result}")
                        return False
                else:
                    print(f"   Failed: {result}")
                    return False

        except Exception as e:
            if attempt < KimConfig.MAX_RETRIES - 1:
                print(f"   Error, retry in {KimConfig.RETRY_DELAY}s: {e}")
                await asyncio.sleep(KimConfig.RETRY_DELAY)
            else:
                print(f"   Failed: {e}")
                return False

    return False


async def send_to_all_groups(
    token: str,
    card: dict,
    dry_run: bool = False
) -> tuple:
    """
    发送到所有群，返回 (success_count, fail_count)
    """
    groups = await get_bot_groups(token)
    if not groups:
        print("No groups found")
        return 0, 0

    print(f"Groups: {len(groups)}")
    for g in groups:
        print(f"   - {g['groupName']} ({g['groupId']})")

    success_count = 0
    fail_count = 0

    for i, group in enumerate(groups):
        group_id = group["groupId"]
        group_name = group["groupName"]

        print(f"[{i+1}/{len(groups)}] {group_name}")

        success = await send_to_group_with_retry(
            token, group_id, group_name, card, dry_run
        )

        if success:
            print(f"   OK")
            success_count += 1
        else:
            fail_count += 1

        if i < len(groups) - 1 and not dry_run:
            await asyncio.sleep(KimConfig.SEND_INTERVAL)

    return success_count, fail_count
