import threading
from flask import Flask, jsonify, request, send_file
from fetcher import fetch_all_listings, _seen_ids
from scorer import score_listing
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
            save_json(listings)
            save_html(listings, top_n=config.TOP_N)
        finally:
            _running = False

    thread = threading.Thread(target=_execute, daemon=True)
    thread.start()
    return jsonify({"ok": True, "queries": queries})


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
