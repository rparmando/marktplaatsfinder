from config import QUERIES, TOP_N
from fetcher import fetch_all_listings
from scorer import score_listing
from output import print_table, save_json, save_html


def main() -> None:
    print("Fetching listings from Marktplaats...")
    listings = fetch_all_listings(QUERIES)
    print(f"\nTotal unique listings fetched: {len(listings)}")

    print("Scoring listings...")
    for listing in listings:
        listing["_score"] = score_listing(listing)

    listings.sort(key=lambda x: x["_score"], reverse=True)

    print_table(listings, top_n=TOP_N)
    save_json(listings)
    save_html(listings, top_n=TOP_N)


if __name__ == "__main__":
    main()
