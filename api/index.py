"""Vercel entrypoint for the Flask RSS reader app."""

from rss_reader.web import app

__all__ = ["app"]
