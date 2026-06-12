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
<html lang="nl" class="bg-white text-black">
<head>
  <meta charset="utf-8">
  <title>Marktplaats Treasure Finder</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    input[type=range] {{ accent-color: black; }}
  </style>
</head>
<body class="min-h-screen bg-white text-black font-sans">

  <!-- Header -->
  <header class="border-b border-black px-6 py-4 flex items-center justify-between">
    <h1 class="text-sm font-semibold tracking-widest uppercase">Marktplaats Treasure Finder</h1>
    <span id="count" class="text-xs text-neutral-400"></span>
  </header>

  <!-- Controls -->
  <div class="border-b border-neutral-200 px-6 py-3 flex flex-wrap gap-4 items-center bg-white">
    <input
      id="search"
      type="text"
      placeholder="Search..."
      class="flex-1 min-w-48 text-sm border border-neutral-300 px-3 py-1.5 focus:outline-none focus:border-black"
    >
    <select id="sort" class="text-sm border border-neutral-300 px-3 py-1.5 focus:outline-none focus:border-black bg-white">
      <option value="score">Score</option>
      <option value="price_asc">Price: low to high</option>
      <option value="price_desc">Price: high to low</option>
      <option value="distance">Distance</option>
    </select>
    <label class="text-xs text-neutral-500 flex items-center gap-2">
      Max €<span id="priceVal" class="text-black font-medium">500</span>
      <input type="range" id="maxPrice" min="0" max="500" step="5" value="500" class="w-24">
    </label>
    <label class="text-xs text-neutral-500 flex items-center gap-2">
      Max <span id="distVal" class="text-black font-medium">10</span>km
      <input type="range" id="maxDist" min="1" max="10" step="1" value="10" class="w-20">
    </label>
  </div>

  <!-- Grid -->
  <div id="grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-px bg-neutral-200 border-b border-neutral-200"></div>

  <script>
    const ALL = {data_json};
    const grid = document.getElementById('grid');
    const countEl = document.getElementById('count');

    function render(items) {{
      if (items.length === 0) {{
        grid.innerHTML = '<p class="col-span-full text-center text-neutral-400 text-sm py-20">No results.</p>';
        countEl.textContent = '0 results';
        return;
      }}
      grid.innerHTML = items.map(d => {{
        const img = d.thumb
          ? `<img src="${{d.thumb}}" loading="lazy" class="w-full h-44 object-cover bg-neutral-100" alt="">`
          : `<div class="w-full h-44 bg-neutral-100 flex items-center justify-center text-neutral-300 text-3xl">—</div>`;
        return `
          <a href="${{d.url}}" target="_blank" class="bg-white flex flex-col group hover:bg-neutral-50 transition-colors">
            ${{img}}
            <div class="p-4 flex flex-col gap-2 flex-1">
              <p class="text-xs font-semibold leading-snug line-clamp-2 group-hover:underline">${{d.title}}</p>
              <p class="text-xs text-neutral-400 leading-relaxed line-clamp-2 flex-1">${{d.description}}</p>
              <div class="flex items-center gap-2 flex-wrap pt-1">
                <span class="text-xs font-bold tabular-nums">${{d.score}}</span>
                <span class="text-xs text-neutral-400">·</span>
                <span class="text-xs font-medium">${{d.price}}</span>
                <span class="text-xs text-neutral-400">·</span>
                <span class="text-xs text-neutral-500">${{d.distance}}</span>
                <span class="text-xs text-neutral-300 ml-auto">${{d.date}}</span>
              </div>
            </div>
          </a>`;
      }}).join('');
      countEl.textContent = `${{items.length}} of ${{ALL.length}}`;
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
