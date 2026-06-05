"""FastAPI 应用工厂和生命周期配置。"""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.cache import close_redis_client, create_redis_client
from app.database import init_db
from app.routers.crawl import router as crawl_router
from app.routers.poems import router as poems_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用启动时初始化数据库和 Redis，关闭时释放 Redis 连接。"""

    await init_db()
    app.state.redis = await create_redis_client()
    yield
    await close_redis_client(getattr(app.state, "redis", None))


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例。"""

    application = FastAPI(title="古诗爬虫 API", version="1.0.0", lifespan=lifespan)
    application.include_router(poems_router)
    application.include_router(crawl_router)
    return application


app = create_app()
"""ASGI 应用实例。"""
