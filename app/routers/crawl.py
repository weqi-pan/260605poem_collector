"""爬虫任务相关路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth import verify_token
from app.cache import delete_cache
from app.config import ALL_CATEGORIES
from app.crawler import crawl_poems
from app.schemas import CrawlRequest, CrawlResponse


router = APIRouter(dependencies=[Depends(verify_token)])
"""爬虫任务路由。"""


@router.post("/crawl", response_model=CrawlResponse)
async def crawl_endpoint(request: Request, payload: CrawlRequest) -> dict[str, object]:
    """按体裁和作者启动一次异步爬虫任务。"""

    category = payload.category.strip()
    author = payload.author.strip()
    if category not in ALL_CATEGORIES:
        allowed = "、".join(ALL_CATEGORIES)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"category 必须是以下之一：{allowed}")
    if not author:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="author 不能为空")

    result = await crawl_poems(category=category, author=author)
    title_keys = [f"poem:title:{title}" for title in result.inserted_titles]
    await delete_cache(request, f"poet:titles:{author}", *title_keys)
    return result.public_dict()
