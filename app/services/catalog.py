from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


CATALOG_PATH = Path(__file__).resolve().parents[2] / "seed_data" / "chapter_catalog.json"


@lru_cache
def load_catalog() -> list[dict[str, Any]]:
    with CATALOG_PATH.open("r", encoding="utf-8") as catalog_file:
        return json.load(catalog_file)


def get_catalog_map() -> dict[str, dict[str, Any]]:
    return {chapter["chapter_id"]: chapter for chapter in load_catalog()}


def get_starting_chapter() -> dict[str, Any]:
    catalog = load_catalog()
    return min(catalog, key=lambda chapter: (chapter["grade"], chapter["difficulty"]))
