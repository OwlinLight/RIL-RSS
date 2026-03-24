"""Unit tests for rss_reader module."""

import pytest

from rss_reader import RSSItem, display_items, parse_feed


def test_parse_feed_extracts_items():
    sample_feed = b"""<?xml version='1.0' encoding='UTF-8'?>
    <rss version='2.0'>
        <channel>
            <title>Sample Feed</title>
            <item>
                <title>First Item</title>
                <link>https://example.com/first</link>
                <description>First description.</description>
                <pubDate>Mon, 01 Jan 2024 00:00:00 GMT</pubDate>
            </item>
            <item>
                <title>Second Item</title>
                <link>https://example.com/second</link>
                <description>Second description.</description>
            </item>
        </channel>
    </rss>
    """
    items = parse_feed(sample_feed)
    assert len(items) == 2
    assert items[0].title == "First Item"
    assert items[0].pub_date == "Mon, 01 Jan 2024 00:00:00 GMT"
    assert items[1].title == "Second Item"
    assert items[1].pub_date is None


def test_parse_feed_missing_channel():
    with pytest.raises(ValueError, match="Missing channel"):
        parse_feed(b"""<rss version='2.0'></rss>""")


def test_parse_feed_invalid_xml():
    with pytest.raises(ValueError, match="Invalid RSS"):
        parse_feed(b"not xml")


def test_display_items_handles_empty(capsys):
    display_items([])
    captured = capsys.readouterr()
    assert "No items found" in captured.out


def test_display_items_outputs_item_details(capsys):
    items = [
        RSSItem(
            title="Example",
            link="https://example.com",
            description="An example description that should wrap correctly.",
            pub_date="Mon, 01 Jan 2024 00:00:00 GMT",
        )
    ]

    display_items(items)
    captured = capsys.readouterr()
    assert "Item 1: Example" in captured.out
    assert "Published: Mon, 01 Jan 2024" in captured.out
    assert "Link: https://example.com" in captured.out
    assert "Description" in captured.out
