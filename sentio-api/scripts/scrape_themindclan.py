"""
TheMindClan therapist scraper — populates the Supabase `therapists` table.

Install deps (one-time, not needed in prod):
    pip install requests beautifulsoup4 python-dotenv supabase

Usage:
    cd sentio-api
    python scripts/scrape_themindclan.py

Set SUPABASE_URL and SUPABASE_SERVICE_KEY in sentio-api/.env (service role key
is needed for upsert without RLS restrictions).
"""

import os
import re
import time
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

import requests
from bs4 import BeautifulSoup
from supabase import create_client

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

SUPABASE_URL = os.environ["SUPABASE_URL"]
# Use service role key so upserts bypass RLS
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ["SUPABASE_ANON_KEY"]

BASE_URL = "https://themindclan.com/professionals/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; SentioBot/1.0; "
        "educational portfolio project - not for commercial use)"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Polite crawl delay (seconds between requests)
CRAWL_DELAY = 1.5


def get_all_profile_links(session: requests.Session) -> list[str]:
    """Crawl paginated listing to collect all /professionals/<slug>/ URLs."""
    links: set[str] = set()
    page_url = BASE_URL

    while page_url:
        log.info("Fetching listing page: %s", page_url)
        resp = session.get(page_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for a in soup.select("a[href*='/professionals/']"):
            href = a["href"].strip()
            # Skip the directory root itself and non-profile pages
            if href.rstrip("/") == "/professionals" or href == BASE_URL:
                continue
            # Normalise to absolute URL
            if href.startswith("/"):
                href = "https://themindclan.com" + href
            if "/professionals/" in href and href != BASE_URL:
                links.add(href.rstrip("/") + "/")

        # Follow "next page" pagination if present
        next_link = soup.select_one("a.next.page-numbers")
        page_url = next_link["href"] if next_link else None
        if page_url:
            time.sleep(CRAWL_DELAY)

    return list(links)


def _text(el) -> str:
    return el.get_text(separator=" ", strip=True) if el else ""


def _find_field(soup: BeautifulSoup, label: str) -> str:
    """Search all list items and paragraphs for a labelled field value."""
    for tag in soup.select("li, p, div"):
        text = _text(tag)
        if text.lower().startswith(label.lower()):
            return text[len(label):].strip(":•– ").strip()
    return ""


def scrape_profile(session: requests.Session, profile_url: str) -> dict | None:
    resp = session.get(profile_url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        log.warning("HTTP %s for %s", resp.status_code, profile_url)
        return None
    soup = BeautifulSoup(resp.text, "html.parser")

    # ── Name + pronouns ──────────────────────────────────────────────────────
    h2 = soup.find("h2")
    raw_name = _text(h2) if h2 else ""
    pronouns = ""
    if "(" in raw_name:
        name = raw_name.split("(")[0].strip()
        pronouns = raw_name.split("(")[1].rstrip(")").strip()
    else:
        name = raw_name.strip()

    if not name:
        log.warning("No name found at %s — skipping", profile_url)
        return None

    # ── Photo ─────────────────────────────────────────────────────────────────
    photo_img = (
        soup.select_one("img[alt*='Picture']")
        or soup.select_one("img[alt*='photo']")
        or soup.select_one(".wp-post-image")
    )
    photo_url = photo_img["src"] if photo_img else ""

    # ── Specializations (support_type tags) ──────────────────────────────────
    specializations = [
        a.get_text(strip=True).replace("​", "").strip()
        for a in soup.select("a[href*='/support_type/'], a[href*='/specialization/']")
        if a.get_text(strip=True)
    ]

    # ── City / location ───────────────────────────────────────────────────────
    city_tag = (
        soup.select_one("a[href*='/city/']")
        or soup.select_one("a[href*='/location/']")
    )
    city = _text(city_tag).replace("Online", "").strip() if city_tag else ""

    # ── Session format ────────────────────────────────────────────────────────
    medium_tag = (
        soup.select_one("a[href*='/medium/']")
        or soup.select_one("a[href*='/session-format/']")
        or soup.select_one("a[href*='/mode/']")
    )
    raw_format = _text(medium_tag) if medium_tag else ""
    # Normalise to online / in-person / both
    f_lower = raw_format.lower()
    if "offline" in f_lower or "in-person" in f_lower or "in person" in f_lower:
        session_format = "in-person"
    elif "both" in f_lower or ("online" in f_lower and "offline" in f_lower):
        session_format = "both"
    else:
        session_format = "online"

    # ── Languages ─────────────────────────────────────────────────────────────
    languages = [
        a.get_text(strip=True)
        for a in soup.select("a[href*='/languages_spoken/'], a[href*='/language/']")
        if a.get_text(strip=True)
    ]

    # ── Fee ───────────────────────────────────────────────────────────────────
    fee_text = _find_field(soup, "Fee")
    fee: int | None = None
    if fee_text:
        match = re.search(r"[\d,]+", fee_text)
        if match:
            fee = int(match.group().replace(",", ""))

    # ── Session duration ──────────────────────────────────────────────────────
    session_duration = _find_field(soup, "Session Duration") or _find_field(soup, "Duration")

    # ── Experience ────────────────────────────────────────────────────────────
    experience = _find_field(soup, "Age & Experience") or _find_field(soup, "Experience")

    # ── Qualifications ────────────────────────────────────────────────────────
    qualifications: list[str] = []
    qual_text = _find_field(soup, "Qualifications")
    if qual_text:
        qualifications = [q.strip("•– ").strip() for q in re.split(r"[•\n]", qual_text) if q.strip()]

    # ── Bio ───────────────────────────────────────────────────────────────────
    # Take the longest paragraph that isn't a field label
    bio = ""
    for p in soup.select("p"):
        txt = _text(p)
        if len(txt) > len(bio) and not any(
            txt.lower().startswith(lbl.lower())
            for lbl in ("fee", "session", "qualific", "language", "age", "experience")
        ):
            bio = txt

    # Build price_range jsonb to match existing schema column
    price_range = {"min": fee, "max": fee} if fee else None

    return {
        # ── New scraper fields ────────────────────────────────────────────────
        "name": name,
        "pronouns": pronouns,
        "photo_url": photo_url,
        "city": city,
        "session_format": session_format,       # singular text
        "languages": languages,
        "specializations": specializations,
        "fee": fee,
        "session_duration": session_duration,
        "experience": experience,
        "qualifications": qualifications,
        "bio": bio,
        "source": "themindclan",
        "source_url": profile_url,
        "verified": True,
        "accepting_clients": True,
        # ── Legacy columns (keep existing data consistent) ────────────────────
        "credentials": qualifications,          # ARRAY — same data, old column name
        "session_formats": [session_format],    # ARRAY — wrap singular format
        "price_range": price_range,             # jsonb — {"min": N, "max": N}
    }


def upsert_one(supabase, data: dict) -> bool:
    """Upsert a single therapist record; returns True on success."""
    try:
        result = supabase.table("therapists").upsert(
            data, on_conflict="source_url"
        ).execute()
        # supabase-py returns an APIResponse; errors surface as exceptions in v2
        return True
    except Exception as exc:
        log.error("  DB error for %s: %s", data.get("source_url", "?"), exc)
        return False


def load_from_json(json_path: Path | None = None):
    """Re-insert all records from the backup JSON into Supabase.

    Use this after running the SQL migration if the first scrape
    failed to write to the DB.

    Usage:
        python scripts/scrape_themindclan.py --from-json
    """
    backup_path = json_path or Path(__file__).parent / "therapists_themindclan.json"
    if not backup_path.exists():
        log.error("Backup JSON not found at %s — run without --from-json first", backup_path)
        return

    with open(backup_path, encoding="utf-8") as f:
        records = json.load(f)

    log.info("Loading %d records from %s", len(records), backup_path)
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    ok = fail = 0
    for i, data in enumerate(records, 1):
        if upsert_one(supabase, data):
            ok += 1
            if i % 10 == 0:
                log.info("  %d/%d inserted...", i, len(records))
        else:
            fail += 1

    log.info("Done — %d inserted, %d failed", ok, fail)


def run():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    session = requests.Session()

    log.info("Collecting profile links from %s", BASE_URL)
    links = get_all_profile_links(session)
    log.info("Found %d profile links", len(links))

    scraped: list[dict] = []
    failed: list[str] = []

    for i, url in enumerate(links, 1):
        log.info("[%d/%d] Scraping %s", i, len(links), url)
        try:
            data = scrape_profile(session, url)
            if data:
                scraped.append(data)
                if not upsert_one(supabase, data):
                    failed.append(url)
                else:
                    log.info("  ✓ inserted")
            time.sleep(CRAWL_DELAY)
        except Exception as exc:
            log.error("  ✗ Failed %s: %s", url, exc)
            failed.append(url)

    backup_path = Path(__file__).parent / "therapists_themindclan.json"
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(scraped, f, ensure_ascii=False, indent=2)

    log.info("\nDone — %d scraped, %d DB-failed", len(scraped), len(failed))
    log.info("Backup saved to %s", backup_path)
    if failed:
        log.warning("Failed URLs:\n%s", "\n".join(failed))


if __name__ == "__main__":
    import sys
    if "--from-json" in sys.argv:
        load_from_json()
    else:
        run()
