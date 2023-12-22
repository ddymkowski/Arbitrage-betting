from pathlib import Path

# --- Scrapers --- #
BETCLIC_API_LIMIT = 250
BETCLIC_PAGES = 5
LV_BET_DAYS_TO_SCRAPE = 10


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "sqlite.db"
REBUILD_TABLES = False
