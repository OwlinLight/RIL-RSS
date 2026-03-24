"""Simple RSS reader CLI.

This script allows users to input an RSS feed URL and prints the parsed
entries including title, publication date, and description.
"""

from __future__ import annotations

import sys
import textwrap
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RSSItem:
    """Represents a single item within an RSS feed."""

    title: str
    link: str
    description: str
    pub_date: Optional[str] = None


def fetch_feed(url: str, timeout: float = 10.0) -> bytes:
    """Fetch RSS feed from a URL.

    Args:
        url: The RSS feed URL.
        timeout: Timeout for the network request in seconds.

    Returns:
        Raw bytes of the RSS feed.

    Raises:
        ValueError: If the URL cannot be retrieved.
    """

    request = urllib.request.Request(url, headers={"User-Agent": "RIL-RSS Reader/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.URLError as exc:  # pragma: no cover - network errors tested via ValueError
        raise ValueError(f"Unable to retrieve RSS feed: {exc}") from exc


def parse_feed(feed_data: bytes) -> List[RSSItem]:
    """Parse RSS XML data into RSSItem instances."""

    try:
        root = ET.fromstring(feed_data)
    except ET.ParseError as exc:
        raise ValueError("Invalid RSS feed data") from exc

    channel = root.find("channel")
    if channel is None:
        raise ValueError("Missing channel element in RSS feed")

    items: List[RSSItem] = []
    for item in channel.findall("item"):
        title = _get_text(item, "title") or "Untitled"
        link = _get_text(item, "link") or ""
        description = _get_text(item, "description") or ""
        pub_date = _get_text(item, "pubDate")
        items.append(RSSItem(title=title, link=link, description=description, pub_date=pub_date))

    return items


def _get_text(parent: ET.Element, tag: str) -> Optional[str]:
    element = parent.find(tag)
    if element is not None and element.text:
        return element.text.strip()
    return None


def display_items(items: List[RSSItem]) -> None:
    """Display RSS items to stdout."""

    if not items:
        print("No items found in RSS feed.")
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


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point for the CLI."""

    argv = list(sys.argv[1:] if argv is None else argv)

    if argv:
        url = argv[0]
    else:
        url = input("Enter RSS feed URL: ").strip()

    if not url:
        print("RSS feed URL is required.", file=sys.stderr)
        return 1

    try:
        feed_data = fetch_feed(url)
        items = parse_feed(feed_data)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    display_items(items)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
