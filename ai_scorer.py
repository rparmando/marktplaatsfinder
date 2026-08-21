import base64
import json
from typing import Optional
import anthropic
import requests

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def _fetch_image_b64(url: str) -> Optional[tuple]:
    """Download an image and return (base64_data, media_type), or None on failure."""
    try:
        resp = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            return None
        content_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
        if content_type not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
            content_type = "image/jpeg"
        return base64.standard_b64encode(resp.content).decode("utf-8"), content_type
    except Exception:
        return None


def ai_bonus_score(listing: dict) -> tuple[int, str, str]:
    """Return (bonus 0-15, reason, market_value_estimate)."""
    title = listing.get("title", "")
    description = listing.get("description", "") or listing.get("categorySpecificDescription", "")
    price_cents = listing.get("priceInfo", {}).get("priceCents", 0)
    price = price_cents / 100 if price_cents else 0
    condition = next(
        (a.get("value", "") for a in listing.get("attributes", []) if a.get("key") == "condition"),
        "unknown",
    )
    distance = listing.get("location", {}).get("distanceMeters", 99999)

    text_block = {
        "type": "text",
        "text": (
            f"You are a vintage treasure hunter in Amsterdam. Score this Marktplaats listing for hidden gem potential.\n"
            f"Title: {title}\n"
            f"Description: {description}\n"
            f"Price: €{price:.2f}\n"
            f"Condition: {condition}\n"
            f"Distance: {distance}m\n"
            f"Score from 0-15 based on: restoration potential, uniqueness, undervalued?, seller seems unaware of value?\n"
            f"Also estimate the realistic resale/market value range for this item (e.g. '€40–80' or 'unknown').\n"
            f'Respond with ONLY a JSON object: {{"score": <int>, "reason": "<one sentence>", "market_value": "<range or null>"}}'
        ),
    }

    content: list = []

    # Attach image if available
    pics = listing.get("pictures", [])
    if pics:
        img_url = pics[0].get("mediumUrl", "") or pics[0].get("largeUrl", "")
        if img_url:
            img = _fetch_image_b64(img_url)
            if img:
                b64_data, media_type = img
                content.append({
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": b64_data},
                })

    content.append(text_block)

    try:
        message = _get_client().messages.create(
            model="claude-opus-4-8",
            max_tokens=128,
            messages=[{"role": "user", "content": content}],
        )
        text = message.content[0].text.strip()
        data = json.loads(text)
        score = max(0, min(15, int(data["score"])))
        reason = str(data.get("reason", ""))
        market_value = str(data.get("market_value") or "")
        return score, reason, market_value
    except Exception:
        return 0, "", ""


def apply_ai_scores(listings: list[dict], top_n: int = 20) -> None:
    for listing in listings[:top_n]:
        bonus, reason, market_value = ai_bonus_score(listing)
        listing["_score"] += bonus
        listing["_ai_reason"] = reason
        listing["_market_value"] = market_value
        # Track AI bonus separately for the breakdown tooltip
        bd = listing.setdefault("_breakdown", {})
        bd["ai"] = bonus
