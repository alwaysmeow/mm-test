from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT = BASE_DIR / "data" / "encar_cars.json"
DEFAULT_MAX_PAGES = 20
DEFAULT_PAGE_SIZE = 50
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
}
ENCAR_WEB_BASE = "https://www.encar.com"
ENCAR_IMAGE_BASE = "https://ci.encar.com"
ENCAR_IMAGE_QUERY = {
    "impolicy": "heightRate",
    "rh": "192",
    "cw": "320",
    "ch": "192",
    "cg": "Center",
    "wtmk": "https://ci.encar.com/wt_mark/w_mark_04.png",
    "wtmkg": "SouthEast",
    "wtmkw": "70",
    "wtmkh": "30",
}
DEFAULT_SOURCE_URLS = [
    (
        "foreign_general",
        "https://api.encar.com/search/car/list/general"
        "?count=true&q=(And.(And.Hidden.N._.CarType.N.)_.AdType.A.)&sr=%7CModifiedDate%7C0%7C50",
    ),
    (
        "foreign_premium",
        "https://api.encar.com/search/car/list/premium"
        "?count=true&q=(And.(And.Hidden.N._.CarType.N.)_.AdType.B.)&sr=%7CModifiedDate%7C0%7C50",
    ),
    (
        "korean_general",
        "https://api.encar.com/search/car/list/general"
        "?count=true&q=(And.(And.Hidden.N._.CarType.Y.)_.AdType.A.)&sr=%7CModifiedDate%7C0%7C50",
    ),
    (
        "korean_premium",
        "https://api.encar.com/search/car/list/premium"
        "?count=true&q=(And.(And.Hidden.N._.CarType.Y.)_.AdType.B.)&sr=%7CModifiedDate%7C0%7C50",
    ),
]


@dataclass
class CarListing:
    car_id: str | None
    source_kind: str | None
    brand: str | None
    model: str | None
    year: int | None
    mileage_km: int | None
    price: str | None
    photo_url: str | None
    source_url: str | None
    fuel_type: str | None
    location: str | None


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return session


def fetch_json(session: requests.Session, url: str, timeout: int = 30) -> Any:
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or None


def to_int(value: Any) -> int | None:
    if value is None:
        return None
    digits = re.sub(r"[^\d]", "", str(value))
    return int(digits) if digits else None


def full_url(value: Any) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    if text.startswith("http://") or text.startswith("https://"):
        return text
    return f"{ENCAR_WEB_BASE}{text}"


def build_photo_url(value: Any) -> str | None:
    text = clean_text(value)
    if not text:
        return None

    if text.startswith("http://") or text.startswith("https://"):
        return text

    normalized = text if text.startswith("/") else f"/{text}"

    if normalized.startswith("/carpicture"):
        return f"{ENCAR_IMAGE_BASE}/carpicture{normalized}?{urlencode(ENCAR_IMAGE_QUERY)}"

    return f"{ENCAR_WEB_BASE}{normalized}"


def extract_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if not isinstance(payload, dict):
        return []

    value = payload.get("SearchResults")
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]

    value = payload.get("resultList")
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]

    return []


def extract_total_count(payload: Any) -> int | None:
    if not isinstance(payload, dict):
        return None
    count = to_int(payload.get("Count") or payload.get("count"))
    return count


def update_sr(url: str, offset: int, limit: int) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    sr_value = query.get("sr", "|ModifiedDate|0|50")
    sr_parts = sr_value.split("|")

    while len(sr_parts) < 4:
        sr_parts.append("")

    sr_parts[1] = sr_parts[1] or "ModifiedDate"
    sr_parts[2] = str(offset)
    sr_parts[3] = str(limit)
    query["sr"] = "|".join(sr_parts[:4])

    new_query = urlencode(query, doseq=True)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))


def parse_photo_url(item: dict[str, Any]) -> str | None:
    photos = item.get("Photos")
    if isinstance(photos, list):
        for photo in photos:
            if not isinstance(photo, dict):
                continue
            location = build_photo_url(photo.get("location"))
            if location:
                return location
    return build_photo_url(item.get("Photo") or item.get("pic"))


def parse_source_url(item: dict[str, Any]) -> str | None:
    detail_url = clean_text(item.get("url"))
    if detail_url:
        return full_url(detail_url)

    car_id = clean_text(item.get("Id") or item.get("id"))
    if car_id:
        return f"{ENCAR_WEB_BASE}/dc/dc_cardetailview.do?carid={car_id}"
    return None


def parse_model(item: dict[str, Any]) -> str | None:
    parts = [
        clean_text(item.get("Model")),
        clean_text(item.get("Badge")),
    ]
    return clean_text(" ".join(part for part in parts if part))


def parse_year(item: dict[str, Any]) -> int | None:
    form_year = to_int(item.get("FormYear"))
    if form_year:
        return form_year

    year_value = clean_text(item.get("Year"))
    if not year_value:
        return None
    match = re.match(r"(\d{4})", year_value)
    if match:
        return int(match.group(1))
    return to_int(year_value)


def parse_price(item: dict[str, Any]) -> str | None:
    price = to_int(item.get("Price"))
    if price is None:
        return None
    return str(price)


def normalize_item(item: dict[str, Any]) -> CarListing:
    return CarListing(
        car_id=clean_text(item.get("Id") or item.get("id")),
        source_kind=None,
        brand=clean_text(item.get("Manufacturer") or item.get("mnfcnm")),
        model=parse_model(item) or clean_text(item.get("mdlnm")),
        year=parse_year(item),
        mileage_km=to_int(item.get("Mileage")),
        price=parse_price(item),
        photo_url=parse_photo_url(item),
        source_url=parse_source_url(item),
        fuel_type=clean_text(item.get("FuelType")),
        location=clean_text(item.get("OfficeCityState")),
    )


def save_json(listings: list[CarListing], output_path: Path, source_url: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": source_url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(listings),
        "cars": [asdict(item) for item in listings],
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch ENCAR car list JSON and save normalized data.")
    parser.add_argument(
        "--url",
        action="append",
        dest="urls",
        help="Optional ENCAR API URL. Can be passed multiple times. If omitted, built-in general/premium Korean+foreign sources are used.",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=DEFAULT_PAGE_SIZE,
        help=f"How many cars to request per page via the sr parameter. Default: {DEFAULT_PAGE_SIZE}",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=DEFAULT_MAX_PAGES,
        help=f"Safety limit for number of pages to fetch. Default: {DEFAULT_MAX_PAGES}",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help=f"Where to save JSON output. Default: {DEFAULT_OUTPUT}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    session = build_session()
    listings: list[CarListing] = []
    seen_ids: set[str] = set()
    source_urls = [(f"custom_{index + 1}", url) for index, url in enumerate(args.urls or [])]
    if not source_urls:
        source_urls = list(DEFAULT_SOURCE_URLS)

    for source_kind, base_url in source_urls:
        offset = 0
        total_count: int | None = None

        for page_number in range(1, args.max_pages + 1):
            page_url = update_sr(base_url, offset=offset, limit=args.page_size)
            payload = fetch_json(session, page_url)

            if total_count is None:
                total_count = extract_total_count(payload)

            items = extract_items(payload)
            if not items:
                break

            page_listings = [normalize_item(item) for item in items]
            page_listings = [
                listing
                for listing in page_listings
                if any(
                    [
                        listing.car_id,
                        listing.brand,
                        listing.model,
                        listing.year,
                        listing.mileage_km,
                        listing.price,
                        listing.photo_url,
                    ]
                )
            ]

            added_on_page = 0
            for listing in page_listings:
                listing.source_kind = source_kind
                if listing.car_id and listing.car_id in seen_ids:
                    continue
                if listing.car_id:
                    seen_ids.add(listing.car_id)
                listings.append(listing)
                added_on_page += 1

            if len(items) < args.page_size:
                break
            if total_count is not None and offset + len(items) >= total_count:
                break
            if added_on_page == 0:
                break

            offset += args.page_size

    save_json(
        listings,
        Path(args.output),
        ", ".join(url for _, url in source_urls),
    )
    print(f"Saved {len(listings)} car(s) to {args.output}")


if __name__ == "__main__":
    main()
