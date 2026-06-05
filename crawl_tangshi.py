#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""古诗异步爬虫 CLI 入口。"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from app.config import ALL_CATEGORIES, DB_PATH, INDEX_URL
from app.crawler import crawl_poems


def build_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器。"""

    parser = argparse.ArgumentParser(description="异步抓取古诗文网唐诗三百首并写入 SQLite")
    parser.add_argument("--category", required=True, choices=ALL_CATEGORIES, help="要抓取的体裁")
    parser.add_argument("--author", required=True, help="要抓取的作者，精确匹配")
    parser.add_argument("--db", default=str(DB_PATH), help="SQLite 数据库路径")
    parser.add_argument("--index-url", default=INDEX_URL, help="唐诗三百首目录页 URL")
    parser.add_argument("--delay", type=float, default=0.5, help="详情页请求间隔秒数")
    parser.add_argument("--timeout", type=float, default=20.0, help="请求超时秒数")
    parser.add_argument("--retries", type=int, default=3, help="失败重试次数")
    return parser


async def async_main() -> None:
    """解析 CLI 参数并执行异步爬虫。"""

    args = build_parser().parse_args()
    result = await crawl_poems(
        category=args.category,
        author=args.author,
        db_path=Path(args.db),
        index_url=args.index_url,
        delay=args.delay,
        timeout=args.timeout,
        retries=args.retries,
    )
    print(json.dumps(result.public_dict(), ensure_ascii=False, indent=2))


def main() -> None:
    """CLI 同步入口，用于启动 asyncio 事件循环。"""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
