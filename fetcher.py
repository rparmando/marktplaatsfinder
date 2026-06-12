import time
import requests
from config import (
    API_URL, HEADERS, POSTCODE, DISTANCE_METERS,
    L1_CATEGORY_ID, PAGE_SIZE, PAGES_PER_QUERY, REQUEST_DELAY,
)

_seen_ids: set[str] = set()


def fetch_all_listings(queries: list[str]) -> list[dict]:
    results = []
    for query in queries:
        listings = fetch_query(query)
        results.extend(listings)
        print(f"  [{query}] {len(listings)} new listings")
    return results


def fetch_query(query: str) -> list[dict]:
    listings = []
    for page in range(PAGES_PER_QUERY):
        offset = page * PAGE_SIZE
        batch = fetch_page(query, offset)
        if not batch:
            break
        listings.extend(batch)
        time.sleep(REQUEST_DELAY)
    return listings


def fetch_page(query: str, offset: int) -> list[dict]:
    params = {
        "query": query,
        "postcode": POSTCODE,
        "distanceMeters": DISTANCE_METERS,
        "l1CategoryId": L1_CATEGORY_ID,
        "limit": PAGE_SIZE,
        "offset": offset,
        "searchInTitleAndDescription": "true",
        "viewOptions": "list-view",
    }
    try:
        resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"    fetch error (query={query}, offset={offset}): {e}")
        return []

    filtered = []
    for listing in data.get("listings", []):
        if not _passes_filter(listing):
            continue
        item_id = listing.get("itemId")
        if item_id in _seen_ids:
            continue
        _seen_ids.add(item_id)
        listing["_query"] = query
        filtered.append(listing)
    return filtered


def _passes_filter(listing: dict) -> bool:
    traits = listing.get("traits", [])
    if "ADMARKT_CONSOLE" in traits:
        return False
    if listing.get("reserved"):
        return False
    price_type = listing.get("priceInfo", {}).get("priceType", "")
    if price_type == "SEE_DESCRIPTION":
        return False
    return True
