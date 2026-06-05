"""爬虫和持久化层使用的数据模型。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class PoemLink:
    """目录页中的一条诗文链接。"""

    category: str
    title: str
    author: str
    url: str


@dataclass(frozen=True)
class Poem:
    """详情页解析出的完整诗文数据。"""

    category: str
    title: str
    author: str
    dynasty: str
    content: str
    url: str


@dataclass(frozen=True)
class CrawlFailure:
    """单首诗抓取失败时返回给调用方的失败明细。"""

    title: str
    url: str
    error: str


@dataclass(frozen=True)
class CrawlResult:
    """一次爬虫任务的汇总结果。"""

    category: str
    author: str
    matched: int
    inserted: int
    skipped: int
    failed: list[CrawlFailure] = field(default_factory=list)
    inserted_titles: list[str] = field(default_factory=list)

    def public_dict(self) -> dict[str, object]:
        """返回 API/CLI 对外展示的结果，隐藏内部缓存失效辅助字段。"""

        return {
            "category": self.category,
            "author": self.author,
            "matched": self.matched,
            "inserted": self.inserted,
            "skipped": self.skipped,
            "failed": [asdict(item) for item in self.failed],
        }
