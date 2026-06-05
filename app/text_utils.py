"""文本清洗工具。"""

from __future__ import annotations

import re
from html import unescape


def clean_text(text: str) -> str:
    """清理 HTML 文本中的实体、空白和首尾不可见字符。"""

    text = unescape(text).replace("\xa0", " ")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s+", "\n", text)
    return text.strip()


def normalize_lines(text: str) -> str:
    """把多行诗文正文规整为非空行组成的字符串。"""

    lines = [clean_text(line) for line in text.splitlines()]
    return "\n".join(line for line in lines if line)
