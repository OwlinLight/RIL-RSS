"""Unit tests for rss_reader package."""

import pytest

from rss_reader import RSSItem, display_items, fetch_feed, parse_feed
from rss_reader.web import app


def test_parse_rss_feed_extracts_items():
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


def test_parse_atom_feed_extracts_items():
    atom_feed = b"""<?xml version='1.0' encoding='utf-8'?>
    <feed xmlns='http://www.w3.org/2005/Atom'>
      <title>Example Feed</title>
      <entry>
        <title>Atom Item</title>
        <link href='https://example.com/atom-item' rel='alternate' />
        <updated>2024-01-01T00:00:00Z</updated>
        <summary>Atom summary.</summary>
      </entry>
    </feed>
    """

    items = parse_feed(atom_feed)
    assert len(items) == 1
    assert items[0].title == "Atom Item"
    assert items[0].link == "https://example.com/atom-item"
    assert items[0].description == "Atom summary."


def test_parse_feed_invalid_xml():
    with pytest.raises(ValueError, match="Invalid feed XML"):
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


def test_web_parse_endpoint_success(monkeypatch):
    def fake_parse_feed_url(url):
        assert url == "https://example.com/feed.xml"
        return [RSSItem(title="One", link="https://example.com/1", description="desc", pub_date=None)]

    monkeypatch.setattr("rss_reader.web.parse_feed_url", fake_parse_feed_url)

    client = app.test_client()
    response = client.post("/api/parse", json={"url": "https://example.com/feed.xml"})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["items"][0]["title"] == "One"


def test_web_parse_endpoint_requires_url():
    client = app.test_client()
    response = client.post("/api/parse", json={"url": ""})

    assert response.status_code == 400
    assert "required" in response.get_json()["error"].lower()


def test_web_parse_endpoint_supports_get_query_param(monkeypatch):
    def fake_parse_feed_url(url):
        assert url == "https://example.com/feed.xml"
        return [RSSItem(title="One", link="", description="", pub_date=None)]

    monkeypatch.setattr("rss_reader.web.parse_feed_url", fake_parse_feed_url)

    client = app.test_client()
    response = client.get("/api/parse?url=https://example.com/feed.xml")

    assert response.status_code == 200
    assert response.get_json()["items"][0]["title"] == "One"


def test_fetch_feed_rejects_non_http_urls():
    with pytest.raises(ValueError, match="absolute http\\(s\\) URL"):
        fetch_feed("ftp://example.com/feed.xml")
