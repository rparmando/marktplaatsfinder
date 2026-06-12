POSTCODE = "1018EC"
DISTANCE_METERS = 10000
L1_CATEGORY_ID = 504  # Huis en Inrichting
PAGE_SIZE = 30
PAGES_PER_QUERY = 3
REQUEST_DELAY = 1.5  # seconds between API calls

QUERIES = [
    "opknapper", "defect", "kapot", "niet werkend",
    "zolder opruiming", "mag weg", "gratis ophalen", "gratis",
    "vintage", "retro", "industrieel", "teak", "Deens design",
    "jaren 60", "jaren 70", "antiek",
]

HEADERS = {"User-Agent": "Mozilla/5.0"}

API_URL = "https://www.marktplaats.nl/lrp/api/search"
MARKTPLAATS_BASE = "https://www.marktplaats.nl"

OUTPUT_JSON = "results.json"
OUTPUT_HTML = "results.html"
TOP_N = 50  # how many results to show in terminal table
