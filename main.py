from config import QUERIES, TOP_N
from fetcher import fetch_all_listings
from scorer import score_listing
from ai_scorer import apply_ai_scores
from output import print_table, save_json, save_html


def main() -> None:
    print("Fetching listings from Marktplaats...")
    listings = fetch_all_listings(QUERIES)
    print(f"\nTotal unique listings fetched: {len(listings)}")

    print("Scoring listings...")
    for listing in listings:
        listing["_score"] = score_listing(listing)

    listings.sort(key=lambda x: x["_score"], reverse=True)

    print("Running AI bonus scoring on top 20...")
    apply_ai_scores(listings, top_n=20)
    listings.sort(key=lambda x: x["_score"], reverse=True)

    print_table(listings, top_n=TOP_N)
    save_json(listings)
    save_html(listings, top_n=TOP_N)


if __name__ == "__main__":
    main()
