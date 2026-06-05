"""FastAPI 请求和响应模型。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CrawlRequest(BaseModel):
    """启动爬虫接口的请求体。"""

    category: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)


class CrawlFailureResponse(BaseModel):
    """单首诗抓取失败的响应项。"""

    title: str
    url: str
    error: str


class CrawlResponse(BaseModel):
    """爬虫接口响应体。"""

    category: str
    author: str
    matched: int
    inserted: int
    skipped: int
    failed: list[CrawlFailureResponse]


class PoemByTitleResponse(BaseModel):
    """按标题查询接口的单条响应。"""

    title: str
    author: str
    dynasty: str
    content: str


class PoetTitleResponse(BaseModel):
    """按作者查询标题接口的单条响应。"""

    title: str
    category: str
