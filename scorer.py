def score_listing(listing: dict) -> int:
    text = _full_text(listing).lower()
    traits = listing.get("traits", [])
    price_info = listing.get("priceInfo", {})
    price_type = price_info.get("priceType", "")
    price = price_info.get("priceCents", 0) / 100
    distance = listing.get("location", {}).get("distanceMeters", 99999)
    condition = _attribute(listing, "condition")
    delivery = _attribute(listing, "delivery")

    score = 0
    score += _urgency_score(text, traits, price_type)
    score += _gem_score(text)
    score += _price_score(price, price_type)
    score += _proximity_score(distance, delivery)
    score -= _penalties(text, traits, condition, price)

    return max(0, min(100, score))


def _urgency_score(text: str, traits: list, price_type: str) -> int:
    score = 0
    if "URGENCY" in traits:
        score += 15
    if price_type == "FAST_BID":
        score += 10
    keywords = {
        "mag weg": 10, "moet weg": 10, "zolder opruiming": 8,
        "opruiming": 6, "gratis ophalen": 8, "snel weg": 7,
        "verhuizing": 5, "inboedel": 5,
    }
    for kw, pts in keywords.items():
        if kw in text:
            score += pts
    return min(score, 25)


def _gem_score(text: str) -> int:
    score = 0
    keywords = {
        "opknapper": 12, "defect": 10, "kapot": 10,
        "niet werkend": 10, "beschadigd": 7, "restauratie": 8,
        "te restaureren": 10, "onderdelen": 5,
        "teak": 8, "eiken": 5, "massief hout": 6,
        "deens design": 10, "industrieel": 7,
        "jaren 60": 8, "jaren 70": 6, "jaren 80": 4,
        "vintage": 5, "retro": 4, "antiek": 6,
        "messing": 6, "gietijzer": 7, "emaille": 6,
    }
    for kw, pts in keywords.items():
        if kw in text:
            score += pts
    return min(score, 30)


def _price_score(price: float, price_type: str) -> int:
    if price_type == "FREE" or (price_type == "FIXED" and price == 0):
        return 25
    if price_type == "FAST_BID" and price == 0:
        return 10
    if 5 <= price <= 50:
        return 25
    if 50 < price <= 150:
        return 20
    if 150 < price <= 400:
        return 12
    if price > 400:
        return 5
    if 0 < price < 5:
        return 15
    return 0


def _proximity_score(distance: int, delivery: str) -> int:
    score = 0
    if delivery == "Ophalen":
        score += 10
    if distance <= 2000:
        score += 10
    elif distance <= 5000:
        score += 7
    elif distance <= 10000:
        score += 4
    return score


def _penalties(text: str, traits: list, condition: str, price: float) -> int:
    penalty = 0
    if "nieuw in doos" in text:
        penalty += 10
    if "winkelprijs" in text:
        penalty += 8
    if "reproductie" in text:
        penalty += 10
    if condition == "Nieuw" and "opknapper" not in text:
        penalty += 5
    if "DAG_TOPPER_7DAYS" in traits and price > 200:
        penalty += 3
    return penalty


def _full_text(listing: dict) -> str:
    parts = [
        listing.get("title", ""),
        listing.get("description", ""),
        listing.get("categorySpecificDescription", ""),
    ]
    return " ".join(parts)


def _attribute(listing: dict, key: str) -> str:
    for attr in listing.get("attributes", []):
        if attr.get("key") == key:
            return attr.get("value", "")
    return ""
