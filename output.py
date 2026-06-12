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
    rows = ""
    for i, listing in enumerate(listings[:top_n], 1):
        url = MARKTPLAATS_BASE + listing.get("vipUrl", "")
        thumb = ""
        pics = listing.get("pictures", [])
        if pics:
            thumb = f'<img src="{pics[0].get("mediumUrl", "")}" width="80">'
        rows += f"""
        <tr>
          <td>{i}</td>
          <td><b>{listing["_score"]}</b></td>
          <td>{thumb}</td>
          <td>{_format_price(listing)}</td>
          <td>{_format_distance(listing)}</td>
          <td><a href="{url}" target="_blank">{listing.get("title", "")}</a></td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <title>Marktplaats Treasure Finder</title>
  <style>
    body {{ font-family: sans-serif; padding: 20px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ padding: 8px 12px; border: 1px solid #ddd; vertical-align: middle; }}
    th {{ background: #f4f4f4; }}
    tr:nth-child(even) {{ background: #fafafa; }}
    a {{ color: #e05c00; }}
  </style>
</head>
<body>
  <h1>Marktplaats Vintage Treasure Finder</h1>
  <table>
    <thead>
      <tr><th>#</th><th>Score</th><th>Photo</th><th>Price</th><th>Distance</th><th>Title</th></tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
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
