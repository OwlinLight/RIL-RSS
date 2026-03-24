"""RSS reader library with CLI and web-friendly helpers."""

from __future__ import annotations

import json
import sys
import textwrap
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class RSSItem:
    """Represents a single item within an RSS/Atom feed."""

    title: str
    link: str
    description: str
    pub_date: Optional[str] = None


def fetch_feed(url: str, timeout: float = 10.0) -> bytes:
    """Fetch feed bytes from a URL."""

    request = urllib.request.Request(url, headers={"User-Agent": "RIL-RSS Reader/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.URLError as exc:  # pragma: no cover - network errors tested via ValueError
        raise ValueError(f"Unable to retrieve RSS feed: {exc}") from exc


def parse_feed(feed_data: bytes) -> List[RSSItem]:
    """Parse RSS/Atom XML data into RSSItem instances."""

    try:
        root = ET.fromstring(feed_data)
    except ET.ParseError as exc:
        raise ValueError("Invalid feed XML data") from exc

    tag_name = _strip_namespace(root.tag)
    if tag_name == "rss":
        return _parse_rss(root)
    if tag_name == "feed":
        return _parse_atom(root)

    raise ValueError("Unsupported feed format")


def _parse_rss(root: ET.Element) -> List[RSSItem]:
    channel = _find_child(root, "channel")
    if channel is None:
        raise ValueError("Missing channel element in RSS feed")

    items: List[RSSItem] = []
    for item in _find_children(channel, "item"):
        title = _get_text(item, "title") or "Untitled"
        link = _get_text(item, "link") or ""
        description = _get_text(item, "description") or _get_text(item, "content") or ""
        pub_date = _get_text(item, "pubDate")
        items.append(RSSItem(title=title, link=link, description=description, pub_date=pub_date))
    return items


def _parse_atom(root: ET.Element) -> List[RSSItem]:
    items: List[RSSItem] = []
    for entry in _find_children(root, "entry"):
        title = _get_text(entry, "title") or "Untitled"
        link = _extract_atom_link(entry)
        description = _get_text(entry, "summary") or _get_text(entry, "content") or ""
        pub_date = _get_text(entry, "updated") or _get_text(entry, "published")
        items.append(RSSItem(title=title, link=link, description=description, pub_date=pub_date))
    return items


def _extract_atom_link(entry: ET.Element) -> str:
    for child in entry:
        if _strip_namespace(child.tag) != "link":
            continue
        rel = child.attrib.get("rel", "alternate")
        href = child.attrib.get("href", "")
        if rel == "alternate" and href:
            return href
        if href:
            return href
    return ""


def _find_child(parent: ET.Element, name: str) -> Optional[ET.Element]:
    for child in parent:
        if _strip_namespace(child.tag) == name:
            return child
    return None


def _find_children(parent: ET.Element, name: str) -> List[ET.Element]:
    return [child for child in parent if _strip_namespace(child.tag) == name]


def _get_text(parent: ET.Element, tag: str) -> Optional[str]:
    child = _find_child(parent, tag)
    if child is not None and child.text:
        return child.text.strip()
    return None


def _strip_namespace(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def display_items(items: List[RSSItem]) -> None:
    """Display feed items to stdout."""

    if not items:
        print("No items found in feed.")
        return

    for index, item in enumerate(items, start=1):
        print(f"Item {index}: {item.title}")
        if item.pub_date:
            print(f"  Published: {item.pub_date}")
        if item.link:
            print(f"  Link: {item.link}")
        if item.description:
            wrapped = textwrap.fill(item.description, width=76)
            print("  Description:")
            for line in wrapped.splitlines():
                print(f"    {line}")
        print()


def parse_feed_url(url: str) -> List[RSSItem]:
    """Fetch and parse a feed URL in one step."""

    return parse_feed(fetch_feed(url))


def items_to_json(items: List[RSSItem]) -> str:
    """Serialize feed items as JSON for the web frontend."""

    payload: List[Dict[str, Any]] = [asdict(item) for item in items]
    return json.dumps(payload)


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point for the CLI."""

    argv = list(sys.argv[1:] if argv is None else argv)
    url = argv[0] if argv else input("Enter RSS feed URL: ").strip()

    if not url:
        print("RSS feed URL is required.", file=sys.stderr)
        return 1

    try:
        items = parse_feed_url(url)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    display_items(items)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
