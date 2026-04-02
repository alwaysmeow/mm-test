from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = BASE_DIR / "data" / "encar_cars.json"
DEFAULT_OUTPUT = BASE_DIR / "data" / "encar_cars_en.json"

DEFAULT_USD_KRW_RATE = 1455.0
FRANKFURTER_USD_KRW_URL = "https://api.frankfurter.app/latest?from=USD&to=KRW"

EXACT_VALUE_MAP = {
    "가솔린": "Gasoline",
    "디젤": "Diesel",
    "전기": "Electric",
    "하이브리드": "Hybrid",
    "플러그인 하이브리드": "Plug-in Hybrid",
    "LPG": "LPG",
    "수소": "Hydrogen",
    "서울": "Seoul",
    "경기": "Gyeonggi",
    "인천": "Incheon",
    "부산": "Busan",
    "대구": "Daegu",
    "광주": "Gwangju",
    "대전": "Daejeon",
    "울산": "Ulsan",
    "세종": "Sejong",
    "강원": "Gangwon",
    "강원도": "Gangwon",
    "충북": "North Chungcheong",
    "충남": "South Chungcheong",
    "전북": "North Jeolla",
    "전남": "South Jeolla",
    "경북": "North Gyeongsang",
    "경남": "South Gyeongsang",
    "제주": "Jeju",
    "제주도": "Jeju",
    "벤츠": "Mercedes-Benz",
    "아우디": "Audi",
    "포르쉐": "Porsche",
    "미니": "MINI",
    "랜드로버": "Land Rover",
    "볼보": "Volvo",
    "폭스바겐": "Volkswagen",
    "포드": "Ford",
    "지프": "Jeep",
    "테슬라": "Tesla",
    "렉서스": "Lexus",
    "혼다": "Honda",
    "마세라티": "Maserati",
    "도요타": "Toyota",
    "푸조": "Peugeot",
    "재규어": "Jaguar",
    "캐딜락": "Cadillac",
    "링컨": "Lincoln",
    "인피니티": "Infiniti",
    "닛산": "Nissan",
    "쉐보레(GM대우)": "Chevrolet (GM Daewoo)",
    "기아": "Kia",
    "현대": "Hyundai",
    "제네시스": "Genesis",
    "KG모빌리티(쌍용)": "KG Mobility (SsangYong)",
    "르노코리아": "Renault Korea",
    "르노삼성": "Renault Samsung",
    "쌍용": "SsangYong",
}

PHRASE_MAP = {
    "시리즈": "Series",
    "클래스": "Class",
    "쿠페": "Coupe",
    "카브리올레": "Cabriolet",
    "컨버터블": "Convertible",
    "그란쿠페": "Gran Coupe",
    "슈팅브레이크": "Shooting Brake",
    "왜건": "Wagon",
    "세단": "Sedan",
    "해치백": "Hatchback",
    "스포츠백": "Sportback",
    "스파이더": "Spyder",
    "로드스터": "Roadster",
    "프리미엄": "Premium",
    "익스클루시브": "Exclusive",
    "럭셔리": "Luxury",
    "모던": "Modern",
    "프레스티지": "Prestige",
    "트림": "Trim",
    "아방가르드": "Avantgarde",
    "콰트로": "quattro",
    "가솔린": "Gasoline",
    "디젤": "Diesel",
    "전기": "Electric",
    "하이브리드": "Hybrid",
    "플러그인 하이브리드": "Plug-in Hybrid",
    "터보": "Turbo",
    "스포츠": "Sport",
    "프로": "Pro",
    "그랜드": "Grand",
    "마이스터": "Master",
    "더 뉴": "The New",
    "디 올 뉴": "The All-New",
    "올 뉴": "All-New",
    "뉴": "New",
}


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or None


def translate_exact(value: str | None) -> str | None:
    if value is None:
        return None
    return EXACT_VALUE_MAP.get(value, value)


def translate_phrase(value: str | None) -> str | None:
    if value is None:
        return None

    translated = value
    for source in sorted(PHRASE_MAP, key=len, reverse=True):
        translated = translated.replace(source, PHRASE_MAP[source])

    translated = re.sub(r"\s+", " ", translated).strip()
    return translated or None


def translate_brand(value: str | None) -> str | None:
    return translate_exact(clean_text(value))


def translate_model(value: str | None) -> str | None:
    cleaned = clean_text(value)
    if cleaned is None:
        return None
    return translate_phrase(cleaned)


def translate_fuel_type(value: str | None) -> str | None:
    return translate_exact(clean_text(value))


def translate_location(value: str | None) -> str | None:
    return translate_exact(clean_text(value))


def convert_price_to_usd(value: Any, usd_krw_rate: float) -> str | None:
    text = clean_text(value)
    if text is None:
        return None

    digits = re.sub(r"[^\d]", "", text)
    if not digits:
        return text

    manwon_value = int(digits)
    krw_value = manwon_value * 10_000
    usd_value = round(krw_value / usd_krw_rate)
    return f"${usd_value:,}"


def get_usd_krw_rate(timeout: int = 10) -> float:
    response = requests.get(FRANKFURTER_USD_KRW_URL, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    return float(data["rates"]["KRW"])


def translate_car(car: dict[str, Any], usd_krw_rate: float) -> dict[str, Any]:
    translated = dict(car)
    translated["brand"] = translate_brand(car.get("brand"))
    translated["model"] = translate_model(car.get("model"))
    translated["fuel_type"] = translate_fuel_type(car.get("fuel_type"))
    translated["location"] = translate_location(car.get("location"))
    translated["price"] = convert_price_to_usd(car.get("price"), usd_krw_rate)
    return translated


def translate_payload(payload: dict[str, Any], usd_krw_rate: float) -> dict[str, Any]:
    cars = payload.get("cars", [])
    translated_cars = [
        translate_car(car, usd_krw_rate)
        for car in cars
        if isinstance(car, dict)
    ]

    translated_payload = dict(payload)
    translated_payload["fetched_at"] = datetime.now(timezone.utc).isoformat()
    translated_payload["cars"] = translated_cars
    translated_payload["count"] = len(translated_cars)
    translated_payload["usd_krw_rate"] = usd_krw_rate
    return translated_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Translate ENCAR JSON values from Korean to English and convert prices to USD."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help=f"Source JSON file. Default: {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help=f"Translated JSON file. Default: {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--usd-krw-rate",
        type=float,
        default=None,
        help="Manual KRW per 1 USD. If omitted, the script tries Frankfurter and falls back to 1455.0",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    usd_krw_rate = args.usd_krw_rate

    if usd_krw_rate is None:
        try:
            usd_krw_rate = get_usd_krw_rate()
        except Exception:
            usd_krw_rate = DEFAULT_USD_KRW_RATE

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    translated_payload = translate_payload(payload, usd_krw_rate)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(translated_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Saved translated JSON to {output_path} using USD/KRW rate {usd_krw_rate}")


if __name__ == "__main__":
    main()
