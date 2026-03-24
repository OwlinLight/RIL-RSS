# RIL-RSS Reader

A simple RSS reader that fetches an RSS feed from a provided URL and displays
its entries in the terminal.

## Installation

This project has no external dependencies beyond the Python standard library
for the application itself. The test suite relies on `pytest`.

## Usage

Run the reader via the module entry point:

```bash
python -m rss_reader <rss_feed_url>
```

If no URL is provided as an argument, the program will prompt for one.

## Testing

Install `pytest` if it is not available and run:

```bash
pytest
```
