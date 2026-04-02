from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = BASE_DIR / "data" / "encar_cars_en.json"

app = FastAPI(title="ENCAR Cars API")

def load_payload(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Data file not found: {path}",
        )

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Data file is not valid JSON") from exc

@app.get("/cars")
def get_cars() -> dict[str, Any]:
    return load_payload(DEFAULT_DATA_PATH)
