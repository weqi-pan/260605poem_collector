"""SQLite 初始化、导入和查询函数。"""

from __future__ import annotations

import json
from pathlib import Path

import aiosqlite

from app.config import DB_PATH, LEGACY_JSON_PATH
from app.models import Poem
from app.text_utils import clean_text, normalize_lines


CREATE_POEMS_SQL = """
CREATE TABLE IF NOT EXISTS poems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    dynasty TEXT NOT NULL,
    content TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""
"""诗文主表建表语句。"""

CREATE_INDEXES_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_poems_title ON poems(title);",
    "CREATE INDEX IF NOT EXISTS idx_poems_author ON poems(author);",
    "CREATE INDEX IF NOT EXISTS idx_poems_category ON poems(category);",
)
"""查询接口需要的索引。"""


async def init_db(
    db_path: Path = DB_PATH,
    legacy_json_path: Path = LEGACY_JSON_PATH,
    import_legacy: bool = True,
) -> int:
    """初始化 SQLite 表结构，并按需导入历史 JSON 数据。"""

    db_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(db_path) as conn:
        await conn.execute(CREATE_POEMS_SQL)
        for sql in CREATE_INDEXES_SQL:
            await conn.execute(sql)
        await conn.commit()

        if import_legacy:
            return await import_legacy_json(conn, legacy_json_path)
    return 0


async def import_legacy_json(conn: aiosqlite.Connection, legacy_json_path: Path = LEGACY_JSON_PATH) -> int:
    """把历史 JSON 文件导入已打开的 SQLite 连接，重复 URL 自动跳过。"""

    if not legacy_json_path.exists():
        return 0

    with legacy_json_path.open("r", encoding="utf-8") as file:
        rows = json.load(file)

    inserted = 0
    for row in rows:
        poem = Poem(
            category=clean_text(row.get("category", "")),
            title=clean_text(row.get("title", "")),
            author=clean_text(row.get("author", "")),
            dynasty=clean_text(row.get("dynasty", "")),
            content=normalize_lines(row.get("content", "")),
            url=clean_text(row.get("url", "")),
        )
        if not poem.url or not poem.title:
            continue
        if await insert_poem(conn, poem):
            inserted += 1
    await conn.commit()
    return inserted


async def insert_poem(conn: aiosqlite.Connection, poem: Poem) -> bool:
    """插入单首诗；如果 URL 已存在则跳过并返回 False。"""

    cursor = await conn.execute(
        """
        INSERT OR IGNORE INTO poems
            (category, title, author, dynasty, content, url, created_at, updated_at)
        VALUES
            (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """,
        (poem.category, poem.title, poem.author, poem.dynasty, poem.content, poem.url),
    )
    return cursor.rowcount == 1


async def get_poems_by_title(title: str, db_path: Path = DB_PATH) -> list[dict[str, str]]:
    """按标题查询诗文详情，同名诗会以列表形式全部返回。"""

    await init_db(db_path=db_path)
    async with aiosqlite.connect(db_path) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            """
            SELECT title, author, dynasty, content
            FROM poems
            WHERE title = ?
            ORDER BY id ASC
            """,
            (clean_text(title),),
        )
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_titles_by_author(author: str, db_path: Path = DB_PATH) -> list[dict[str, str]]:
    """查询指定作者的所有诗题和对应体裁。"""

    await init_db(db_path=db_path)
    async with aiosqlite.connect(db_path) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            """
            SELECT title, category
            FROM poems
            WHERE author = ?
            ORDER BY category ASC, id ASC
            """,
            (clean_text(author),),
        )
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]
