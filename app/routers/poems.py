"""诗文查询相关路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.auth import verify_token
from app.cache import get_cache, set_cache
from app.database import get_poems_by_title, get_titles_by_author
from app.schemas import PoemByTitleResponse, PoetTitleResponse


router = APIRouter(dependencies=[Depends(verify_token)])
"""诗文查询路由。"""


@router.get("/poems/by-title", response_model=list[PoemByTitleResponse])
async def poems_by_title(request: Request, title: str = Query(..., min_length=1)) -> list[dict[str, str]]:
    """按标题查询诗文详情，同名诗全部返回。"""

    title = title.strip()
    if not title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="title 不能为空")

    cache_key = f"poem:title:{title}"
    cached = await get_cache(request, cache_key)
    if cached is not None:
        return cached

    poems = await get_poems_by_title(title)
    await set_cache(request, cache_key, poems)
    return poems


@router.get("/poets/{author}/titles", response_model=list[PoetTitleResponse])
async def poet_titles(request: Request, author: str) -> list[dict[str, str]]:
    """查询指定作者的所有诗题和体裁。"""

    author = author.strip()
    if not author:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="author 不能为空")

    cache_key = f"poet:titles:{author}"
    cached = await get_cache(request, cache_key)
    if cached is not None:
        return cached

    titles = await get_titles_by_author(author)
    await set_cache(request, cache_key, titles)
    return titles
