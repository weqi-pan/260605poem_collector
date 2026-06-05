"""应用配置和全局常量。"""

from __future__ import annotations

import os
from pathlib import Path


INDEX_URL = "https://www.gushiwen.cn/gushi/tangshi.aspx"
"""古诗文网唐诗三百首目录页。"""

ALL_CATEGORIES = ("五言绝句", "七言绝句", "五言律诗", "七言律诗", "五言古诗", "七言古诗", "乐府")
"""允许抓取的诗词体裁。"""

DB_PATH = Path(os.getenv("DB_PATH", "data/poems.db"))
"""SQLite 数据库默认路径。"""

LEGACY_JSON_PATH = Path(os.getenv("LEGACY_JSON_PATH", "data/tangshi_selected.json"))
"""历史 JSON 数据路径，用于首次导入 SQLite。"""

API_TOKEN = os.getenv("API_TOKEN", "123456")
"""接口固定令牌，后续可通过环境变量替换。"""

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
"""Redis 连接地址。"""

CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))
"""Redis 缓存默认过期时间。"""

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
"""访问古诗文网页面时使用的请求头。"""
