"""Flask web app for rendering the RSS reader frontend."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from . import parse_feed_url

app = Flask(__name__, template_folder="templates")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/parse")
@app.get("/api/parse")
def parse_url():
    payload = request.get_json(silent=True) or {}
    url = (payload.get("url") or request.args.get("url") or "").strip()

    if not url:
        return jsonify({"error": "RSS feed URL is required."}), 400

    try:
        items = parse_feed_url(url)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "items": [
                {
                    "title": item.title,
                    "link": item.link,
                    "description": item.description,
                    "pub_date": item.pub_date,
                }
                for item in items
            ]
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
