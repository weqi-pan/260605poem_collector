"""古诗文网页面的 HTML 解析器。"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Iterable
from urllib.parse import urljoin

from app.models import Poem, PoemLink
from app.text_utils import clean_text, normalize_lines


class TangshiIndexParser(HTMLParser):
    """解析唐诗目录页，并按体裁收集诗文链接。"""

    def __init__(self, base_url: str, categories: Iterable[str]) -> None:
        """初始化目录页解析器。"""

        super().__init__(convert_charrefs=False)
        self.base_url = base_url
        self.categories = set(categories)
        self.current_category: str | None = None
        self.links: list[PoemLink] = []
        self._tag_stack: list[str] = []
        self._capture_heading = False
        self._heading_parts: list[str] = []
        self._pending_link: dict[str, str] | None = None
        self._pending_author = False
        self._text_after_link: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """处理开始标签，识别体裁标题和诗文链接。"""

        self._tag_stack.append(tag)
        attr = dict(attrs)

        if tag in {"h1", "h2", "h3", "strong", "b"}:
            self._capture_heading = True
            self._heading_parts = []

        if self.current_category and tag == "a":
            href = attr.get("href") or ""
            if "/shiwenv_" in href:
                self._pending_link = {"title": "", "url": urljoin(self.base_url, href)}
                self._text_after_link = []

    def handle_endtag(self, tag: str) -> None:
        """处理结束标签，并在链接块结束时落入结果列表。"""

        if tag in {"h1", "h2", "h3", "strong", "b"} and self._capture_heading:
            heading = clean_text("".join(self._heading_parts))
            if heading in self.categories:
                self.current_category = heading
            elif heading:
                self.current_category = None
            self._capture_heading = False
            self._heading_parts = []

        if tag == "a" and self._pending_link:
            self._pending_author = True

        if tag in {"p", "div", "br"}:
            self._flush_pending_link()

        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        """收集标题、链接文本和作者文本。"""

        if self._capture_heading:
            self._heading_parts.append(data)

        if self._pending_link is not None:
            if self._tag_stack and self._tag_stack[-1] == "a":
                self._pending_link["title"] += data
            elif self._pending_author:
                self._text_after_link.append(data)
                if ")" in data or "）" in data:
                    self._flush_pending_link()

    def close(self) -> None:
        """关闭解析器前刷新最后一个尚未写入的链接。"""

        self._flush_pending_link()
        super().close()

    def _flush_pending_link(self) -> None:
        """把当前正在收集的目录链接转换为 PoemLink。"""

        if not self.current_category or not self._pending_link:
            self._pending_link = None
            self._pending_author = False
            self._text_after_link = []
            return

        title = clean_text(self._pending_link["title"])
        author_text = clean_text("".join(self._text_after_link))
        match = re.search(r"[（(]\s*([^()（）]+?)\s*[)）]", author_text)
        author = clean_text(match.group(1)) if match else ""

        if title:
            self.links.append(
                PoemLink(
                    category=self.current_category,
                    title=title,
                    author=author,
                    url=self._pending_link["url"],
                )
            )

        self._pending_link = None
        self._pending_author = False
        self._text_after_link = []


class PoemDetailParser(HTMLParser):
    """解析诗文详情页中的第一个诗文卡片。"""

    def __init__(self) -> None:
        """初始化详情页解析器。"""

        super().__init__(convert_charrefs=False)
        self.title = ""
        self.author = ""
        self.dynasty = ""
        self.content = ""
        self._sons_depth = 0
        self._in_first_sons = False
        self._done_first_sons = False
        self._capture_title = False
        self._title_parts: list[str] = []
        self._capture_source = False
        self._source_parts: list[str] = []
        self._capture_content = False
        self._content_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """处理开始标签，进入标题、作者朝代或正文采集状态。"""

        attr = dict(attrs)
        classes = set((attr.get("class") or "").split())
        element_id = attr.get("id") or ""

        if tag == "div" and "sons" in classes and not self._done_first_sons:
            self._in_first_sons = True
            self._sons_depth = 1
            return

        if self._in_first_sons and tag == "div":
            self._sons_depth += 1

        if not self._in_first_sons:
            return

        if tag == "h1":
            self._capture_title = True
            self._title_parts = []
        elif tag == "p" and "source" in classes:
            self._capture_source = True
            self._source_parts = []
        elif tag == "div" and ("contson" in classes or element_id.startswith("contson")):
            self._capture_content = True
            self._content_parts = []
        elif self._capture_content and tag == "br":
            self._content_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        """处理结束标签，并在采集块结束时写入解析结果。"""

        if self._capture_title and tag == "h1":
            self.title = clean_text("".join(self._title_parts))
            self._capture_title = False

        if self._capture_source and tag == "p":
            self._set_source(clean_text("".join(self._source_parts)))
            self._capture_source = False

        if self._capture_content and tag == "div":
            self.content = normalize_lines("".join(self._content_parts))
            self._capture_content = False

        if self._in_first_sons and tag == "div":
            self._sons_depth -= 1
            if self._sons_depth <= 0:
                self._in_first_sons = False
                self._done_first_sons = True

    def handle_data(self, data: str) -> None:
        """按当前采集状态收集文本节点。"""

        if self._capture_title:
            self._title_parts.append(data)
        elif self._capture_source:
            self._source_parts.append(data)
        elif self._capture_content:
            self._content_parts.append(data)

    def _set_source(self, text: str) -> None:
        """从“作者〔朝代〕”格式中拆出作者和朝代。"""

        match = re.match(r"(.+?)\s*[〔\[]\s*(.+?)\s*[〕\]]", text)
        if match:
            self.author = clean_text(match.group(1))
            self.dynasty = clean_text(match.group(2))
        else:
            self.author = clean_text(text)


def parse_index(html: str, base_url: str, categories: Iterable[str]) -> list[PoemLink]:
    """解析目录页 HTML，并按 URL 去重。"""

    parser = TangshiIndexParser(base_url, categories)
    parser.feed(html)
    parser.close()

    seen: set[str] = set()
    unique_links: list[PoemLink] = []
    for link in parser.links:
        if link.url in seen:
            continue
        seen.add(link.url)
        unique_links.append(link)
    return unique_links


def parse_poem_detail(html: str, link: PoemLink) -> Poem:
    """解析详情页 HTML，并用目录页信息补齐缺失字段。"""

    parser = PoemDetailParser()
    parser.feed(html)
    parser.close()
    return Poem(
        category=link.category,
        title=parser.title or link.title,
        author=parser.author or link.author,
        dynasty=parser.dynasty,
        content=parser.content,
        url=link.url,
    )
