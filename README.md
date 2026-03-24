# RIL-RSS Reader

An RSS/Atom reader with both a command-line interface and a lightweight web
frontend. You can provide a feed URL and the app will fetch, parse, and render
its entries.

## Features

- Parse RSS 2.0 and Atom feeds
- CLI usage for quick terminal reading
- Frontend UI with URL input + rendered feed cards
- Vercel-ready deployment config

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## CLI usage

```bash
PYTHONPATH=src python -m rss_reader <rss_feed_url>
```

If no URL is provided as an argument, the program prompts for one.

## Run the frontend locally

```bash
export FLASK_APP=rss_reader.web:app
PYTHONPATH=src flask run --debug
```

Then open `http://127.0.0.1:5000`.

## Deploy on Vercel

This repo includes `vercel.json` and an API entrypoint at `api/index.py`.

1. Push the repo to GitHub.
2. Import the project in Vercel.
3. Keep default settings (Vercel will detect `vercel.json`).
4. Deploy.

## Testing

```bash
PYTHONPATH=src pytest
```
