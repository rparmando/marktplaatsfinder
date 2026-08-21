import threading
from flask import Flask, jsonify, request, send_file
from fetcher import fetch_all_listings, _seen_ids
from scorer import score_listing
from ai_scorer import apply_ai_scores
from output import save_json, save_html
import config

app = Flask(__name__)
_running = False


@app.route("/")
def index():
    return send_file("results.html")


@app.route("/api/status")
def status():
    return jsonify({"running": _running})


@app.route("/api/run", methods=["POST"])
def run():
    global _running
    if _running:
        return jsonify({"error": "Already running"}), 409

    body = request.get_json(silent=True) or {}
    queries = body.get("queries") or config.QUERIES

    def _execute():
        global _running
        _running = True
        try:
            _seen_ids.clear()
            listings = fetch_all_listings(queries)
            for listing in listings:
                listing["_score"] = score_listing(listing)
            listings.sort(key=lambda x: x["_score"], reverse=True)
            apply_ai_scores(listings, top_n=20)
            listings.sort(key=lambda x: x["_score"], reverse=True)
            save_json(listings)
            save_html(listings, top_n=config.TOP_N)
        finally:
            _running = False

    thread = threading.Thread(target=_execute, daemon=True)
    thread.start()
    return jsonify({"ok": True, "queries": queries})


@app.route("/api/add-query", methods=["POST"])
def add_query():
    import os, re
    body = request.get_json(silent=True) or {}
    q = (body.get("query") or "").strip().lower()
    if not q:
        return jsonify({"error": "empty query"}), 400
    if q in [x.lower() for x in config.QUERIES]:
        return jsonify({"ok": True, "note": "already exists"})

    # Append to the in-memory list so this run picks it up
    config.QUERIES.append(q)

    # Persist to config.py — rewrite QUERIES list from the live in-memory list
    config_path = os.path.join(os.path.dirname(__file__), "config.py")
    with open(config_path, encoding="utf-8") as f:
        src = f.read()

    # Build the new QUERIES block from the current in-memory list
    lines = ",\n    ".join(f'"{x}"' for x in config.QUERIES)
    new_block = f"QUERIES = [\n    {lines},\n]"
    src = re.sub(r"QUERIES\s*=\s*\[.*?\]", new_block, src, flags=re.DOTALL)

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(src)

    return jsonify({"ok": True})


@app.route("/api/results")
def results():
    import json, os
    if not os.path.exists(config.OUTPUT_JSON):
        return jsonify([])
    with open(config.OUTPUT_JSON, encoding="utf-8") as f:
        return jsonify(json.load(f))


if __name__ == "__main__":
    print("Server running at http://localhost:5001")
    app.run(port=5001, debug=False)
