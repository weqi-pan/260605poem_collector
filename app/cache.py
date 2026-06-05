"""Redis 缓存封装。"""

from __future__ import annotations

import json
from typing import Any

from fastapi import Request
from redis import asyncio as redis
from redis.exceptions import RedisError

from app.config import CACHE_TTL_SECONDS, REDIS_URL


async def create_redis_client() -> redis.Redis | None:
    """创建 Redis 客户端；连接失败时返回 None 以允许服务无缓存运行。"""

    client = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        await client.ping()
    except RedisError:
        await client.aclose()
        return None
    return client


def get_redis_client(request: Request) -> redis.Redis | None:
    """从 FastAPI app.state 中读取 Redis 客户端。"""

    return getattr(request.app.state, "redis", None)


async def close_redis_client(client: redis.Redis | None) -> None:
    """关闭 Redis 客户端连接。"""

    if client is not None:
        await client.aclose()


async def get_cache(request: Request, key: str) -> Any | None:
    """读取 JSON 缓存；缓存不存在、解析失败或 Redis 不可用时返回 None。"""

    client = get_redis_client(request)
    if client is None:
        return None
    try:
        cached = await client.get(key)
        if cached is None:
            return None
        return json.loads(cached)
    except (RedisError, json.JSONDecodeError):
        return None


async def set_cache(request: Request, key: str, payload: Any) -> None:
    """写入 JSON 缓存；Redis 异常时静默跳过。"""

    client = get_redis_client(request)
    if client is None:
        return
    try:
        await client.setex(key, CACHE_TTL_SECONDS, json.dumps(payload, ensure_ascii=False))
    except RedisError:
        return


async def delete_cache(request: Request, *keys: str) -> None:
    """删除一个或多个缓存 key；Redis 异常时静默跳过。"""

    client = get_redis_client(request)
    if client is None or not keys:
        return
    try:
        await client.delete(*keys)
    except RedisError:
        return
