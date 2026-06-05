"""异步爬虫服务。"""

from __future__ import annotations

import asyncio
import random
from pathlib import Path

import aiosqlite
import httpx

from app.config import ALL_CATEGORIES, DB_PATH, INDEX_URL, REQUEST_HEADERS
from app.database import init_db, insert_poem
from app.models import CrawlFailure, CrawlResult
from app.parsers import parse_index, parse_poem_detail
from app.text_utils import clean_text


def validate_category(category: str) -> str:
    """校验并规整体裁字段。"""

    category = clean_text(category)
    if category not in ALL_CATEGORIES:
        allowed = "、".join(ALL_CATEGORIES)
        raise ValueError(f"category 必须是以下之一：{allowed}")
    return category


def validate_author(author: str) -> str:
    """校验并规整作者字段。"""

    author = clean_text(author)
    if not author:
        raise ValueError("author 不能为空")
    return author


async def fetch_html(
    client: httpx.AsyncClient,
    url: str,
    retries: int = 3,
    retry_delay: float = 1.5,
) -> str:
    """异步请求 HTML，并对临时网络错误做有限重试。"""

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as exc:
            last_error = exc
            if attempt < retries:
                await asyncio.sleep(retry_delay * attempt)
    raise RuntimeError(f"请求失败：{url}，原因：{last_error}") from last_error


async def crawl_poems(
    category: str,
    author: str,
    db_path: Path = DB_PATH,
    index_url: str = INDEX_URL,
    delay: float = 0.5,
    timeout: float = 20.0,
    retries: int = 3,
) -> CrawlResult:
    """按体裁和作者精确匹配抓取诗文，并增量写入 SQLite。"""

    category = validate_category(category)
    author = validate_author(author)
    await init_db(db_path=db_path)

    timeout_config = httpx.Timeout(timeout)
    async with httpx.AsyncClient(
        headers=REQUEST_HEADERS,
        timeout=timeout_config,
        follow_redirects=True,
    ) as client:
        index_html = await fetch_html(client, index_url, retries=retries)
        links = parse_index(index_html, index_url, (category,))
        matched_links = [link for link in links if clean_text(link.author) == author]

        inserted = 0
        skipped = 0
        failures: list[CrawlFailure] = []
        inserted_titles: list[str] = []

        async with aiosqlite.connect(db_path) as conn:
            for index, link in enumerate(matched_links, 1):
                try:
                    detail_html = await fetch_html(client, link.url, retries=retries)
                    poem = parse_poem_detail(detail_html, link)
                    if await insert_poem(conn, poem):
                        inserted += 1
                        inserted_titles.append(poem.title)
                    else:
                        skipped += 1

                    # 顺序抓取并保留轻微随机延迟，避免对源站造成突发压力。
                    if index < len(matched_links) and delay > 0:
                        await asyncio.sleep(delay + random.uniform(0, delay * 0.4))
                except Exception as exc:  # noqa: BLE001 - 单首失败应进入结果明细，不能中断整批。
                    failures.append(CrawlFailure(title=link.title, url=link.url, error=str(exc)))
            await conn.commit()

    return CrawlResult(
        category=category,
        author=author,
        matched=len(matched_links),
        inserted=inserted,
        skipped=skipped,
        failed=failures,
        inserted_titles=inserted_titles,
    )
