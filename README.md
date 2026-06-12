# Marktplaats Vintage Treasure Finder

A Python CLI tool that fetches listings from Marktplaats, scores them for "hidden gem" potential, and outputs a ranked list of the best finds.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
cd marktplaats_finder
python main.py
```

The tool will:
1. Run 15 search queries across Marktplaats (3 pages each)
2. Deduplicate and filter out ads, reserved, and no-price listings
3. Score each listing 0–100 based on urgency, gem potential, price, and proximity
4. Print a ranked table in the terminal
5. Save `results.json` and `results.html` (with thumbnails) to the current directory

## Configuration

Edit `config.py` to change:
- `POSTCODE` and `DISTANCE_METERS` — your location and search radius
- `QUERIES` — the search terms to run
- `TOP_N` — how many results to show in the terminal table

## Scoring

| Component         | Max pts |
|-------------------|---------|
| Urgency           | 25      |
| Gem potential     | 30      |
| Price sweet spot  | 25      |
| Pickup/proximity  | 20      |

Penalties are subtracted for commercial signals (new-in-box, retail price, reproductions).

## Output

- Terminal: ranked table via `rich`
- `results.json`: full scored listing data
- `results.html`: visual table with thumbnails and clickable links
