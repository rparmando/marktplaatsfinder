import json
from config import MARKTPLAATS_BASE, OUTPUT_JSON, OUTPUT_HTML
from rich.console import Console
from rich.table import Table

console = Console()


def print_table(listings: list[dict], top_n: int = 50) -> None:
    table = Table(title="Marktplaats Vintage Treasure Finder", show_lines=False)
    table.add_column("RANK", style="bold cyan", width=5)
    table.add_column("SCORE", style="bold green", width=6)
    table.add_column("PRICE", width=10)
    table.add_column("DIST", width=7)
    table.add_column("TITLE", width=40)
    table.add_column("URL")

    for i, listing in enumerate(listings[:top_n], 1):
        table.add_row(
            str(i),
            str(listing["_score"]),
            _format_price(listing),
            _format_distance(listing),
            listing.get("title", "")[:40],
            MARKTPLAATS_BASE + listing.get("vipUrl", ""),
        )
    console.print(table)


def save_json(listings: list[dict]) -> None:
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)
    console.print(f"[dim]Saved {len(listings)} results to {OUTPUT_JSON}[/dim]")


def save_html(listings: list[dict], top_n: int = 50) -> None:
    data = []
    for i, listing in enumerate(listings[:top_n], 1):
        pics = listing.get("pictures", [])
        data.append({
            "rank": i,
            "score": listing["_score"],
            "title": listing.get("title", ""),
            "description": listing.get("description", "")[:200],
            "price": _format_price(listing),
            "priceCents": listing.get("priceInfo", {}).get("priceCents", 0),
            "distance": _format_distance(listing),
            "distanceMeters": listing.get("location", {}).get("distanceMeters", 99999),
            "city": listing.get("location", {}).get("cityName", ""),
            "url": MARKTPLAATS_BASE + listing.get("vipUrl", ""),
            "thumb": pics[0].get("mediumUrl", "") if pics else "",
            "date": listing.get("date", ""),
            "seller": listing.get("sellerInformation", {}).get("sellerName", ""),
        })

    data_json = json.dumps(data, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <title>Marktplaats Treasure Finder</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f5f0eb; color: #2c2c2c; min-height: 100vh; }}

    header {{ background: #d95c00; color: white; padding: 18px 24px; display: flex; align-items: center; gap: 12px; }}
    header h1 {{ font-size: 1.3rem; font-weight: 700; letter-spacing: -0.3px; }}
    header span {{ font-size: 0.85rem; opacity: 0.85; margin-left: auto; }}

    .controls {{ padding: 16px 24px; display: flex; gap: 12px; flex-wrap: wrap; align-items: center; background: white; border-bottom: 1px solid #e0d9d0; }}
    .controls input {{ flex: 1; min-width: 200px; padding: 8px 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 0.9rem; }}
    .controls select {{ padding: 8px 10px; border: 1px solid #ccc; border-radius: 6px; font-size: 0.9rem; background: white; }}
    .controls label {{ font-size: 0.85rem; color: #666; display: flex; align-items: center; gap: 6px; }}
    .controls input[type=range] {{ width: 100px; }}
    #count {{ font-size: 0.85rem; color: #888; margin-left: auto; white-space: nowrap; }}

    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; padding: 20px 24px; }}

    .card {{ background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.08); transition: transform 0.15s, box-shadow 0.15s; display: flex; flex-direction: column; }}
    .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.13); }}

    .card-img {{ width: 100%; height: 180px; object-fit: cover; background: #eee; display: block; }}
    .card-img-placeholder {{ width: 100%; height: 180px; background: #e8e2da; display: flex; align-items: center; justify-content: center; color: #aaa; font-size: 2rem; }}

    .card-body {{ padding: 12px 14px; flex: 1; display: flex; flex-direction: column; gap: 6px; }}
    .card-title {{ font-size: 0.92rem; font-weight: 600; line-height: 1.3; color: #1a1a1a; }}
    .card-desc {{ font-size: 0.78rem; color: #777; line-height: 1.4; flex: 1; }}
    .card-meta {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-top: 4px; }}

    .badge-score {{ background: #d95c00; color: white; border-radius: 20px; padding: 2px 10px; font-size: 0.78rem; font-weight: 700; }}
    .badge-score.high {{ background: #2e7d32; }}
    .badge-score.mid {{ background: #e65100; }}
    .badge-price {{ background: #fff3e0; color: #bf360c; border-radius: 4px; padding: 2px 7px; font-size: 0.78rem; font-weight: 600; }}
    .badge-dist {{ background: #e8f5e9; color: #2e7d32; border-radius: 4px; padding: 2px 7px; font-size: 0.78rem; }}
    .badge-date {{ font-size: 0.75rem; color: #999; margin-left: auto; }}

    .card-link {{ display: block; text-align: center; margin: 10px 14px 12px; padding: 7px; background: #d95c00; color: white; border-radius: 6px; text-decoration: none; font-size: 0.82rem; font-weight: 600; transition: background 0.15s; }}
    .card-link:hover {{ background: #b84e00; }}

    .rank {{ font-size: 0.7rem; color: #bbb; text-align: right; padding: 6px 10px 0; }}

    #empty {{ display: none; text-align: center; padding: 60px; color: #aaa; font-size: 1rem; grid-column: 1/-1; }}
  </style>
</head>
<body>
  <header>
    <h1>🔍 Marktplaats Treasure Finder</h1>
    <span id="count"></span>
  </header>
  <div class="controls">
    <input type="text" id="search" placeholder="Zoek op titel of omschrijving...">
    <select id="sort">
      <option value="score">Sorteer: Score</option>
      <option value="price_asc">Sorteer: Prijs laag-hoog</option>
      <option value="price_desc">Sorteer: Prijs hoog-laag</option>
      <option value="distance">Sorteer: Afstand</option>
    </select>
    <label>Max prijs: €<span id="priceVal">500</span>
      <input type="range" id="maxPrice" min="0" max="500" step="5" value="500">
    </label>
    <label>Max afstand: <span id="distVal">10</span>km
      <input type="range" id="maxDist" min="1" max="10" step="1" value="10">
    </label>
  </div>
  <div class="grid" id="grid">
    <div id="empty">Geen resultaten gevonden.</div>
  </div>

  <script>
    const ALL = {data_json};

    const grid = document.getElementById('grid');
    const emptyMsg = document.getElementById('empty');
    const countEl = document.getElementById('count');

    function scoreClass(s) {{
      if (s >= 65) return 'high';
      if (s >= 55) return 'mid';
      return '';
    }}

    function render(items) {{
      const cards = items.map(d => {{
        const img = d.thumb
          ? `<img class="card-img" src="${{d.thumb}}" loading="lazy" alt="">`
          : `<div class="card-img-placeholder">🪑</div>`;
        return `
          <div class="card">
            <div class="rank">#${{d.rank}}</div>
            <a href="${{d.url}}" target="_blank">${{img}}</a>
            <div class="card-body">
              <div class="card-title">${{d.title}}</div>
              <div class="card-desc">${{d.description}}</div>
              <div class="card-meta">
                <span class="badge-score ${{scoreClass(d.score)}}">${{d.score}} pts</span>
                <span class="badge-price">${{d.price}}</span>
                <span class="badge-dist">${{d.distance}}</span>
                <span class="badge-date">${{d.date}}</span>
              </div>
            </div>
            <a class="card-link" href="${{d.url}}" target="_blank">Bekijk op Marktplaats →</a>
          </div>`;
      }}).join('');
      grid.innerHTML = cards + '<div id="empty" style="display:none"></div>';
      countEl.textContent = `${{items.length}} van ${{ALL.length}} resultaten`;
      if (items.length === 0) {{
        grid.innerHTML = '<div style="text-align:center;padding:60px;color:#aaa;grid-column:1/-1">Geen resultaten gevonden.</div>';
      }}
    }}

    function filter() {{
      const q = document.getElementById('search').value.toLowerCase();
      const sort = document.getElementById('sort').value;
      const maxPrice = parseInt(document.getElementById('maxPrice').value);
      const maxDist = parseInt(document.getElementById('maxDist').value) * 1000;

      let items = ALL.filter(d => {{
        if (q && !d.title.toLowerCase().includes(q) && !d.description.toLowerCase().includes(q)) return false;
        if (d.priceCents > 0 && d.priceCents / 100 > maxPrice) return false;
        if (d.distanceMeters > maxDist) return false;
        return true;
      }});

      if (sort === 'price_asc') items.sort((a,b) => a.priceCents - b.priceCents);
      else if (sort === 'price_desc') items.sort((a,b) => b.priceCents - a.priceCents);
      else if (sort === 'distance') items.sort((a,b) => a.distanceMeters - b.distanceMeters);
      else items.sort((a,b) => b.score - a.score);

      render(items);
    }}

    document.getElementById('search').addEventListener('input', filter);
    document.getElementById('sort').addEventListener('change', filter);
    document.getElementById('maxPrice').addEventListener('input', e => {{
      document.getElementById('priceVal').textContent = e.target.value;
      filter();
    }});
    document.getElementById('maxDist').addEventListener('input', e => {{
      document.getElementById('distVal').textContent = e.target.value;
      filter();
    }});

    filter();
  </script>
</body>
</html>"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    console.print(f"[dim]Saved HTML to {OUTPUT_HTML}[/dim]")


def _format_price(listing: dict) -> str:
    price_info = listing.get("priceInfo", {})
    price_type = price_info.get("priceType", "")
    cents = price_info.get("priceCents", 0)
    if price_type == "FAST_BID" and cents == 0:
        return "€0 (bid)"
    if price_type == "MIN_BID":
        return f"€{cents // 100} (bod)"
    return f"€{cents // 100}"


def _format_distance(listing: dict) -> str:
    d = listing.get("location", {}).get("distanceMeters", 0)
    if d >= 1000:
        return f"{d / 1000:.1f}km"
    return f"{d}m"
