#!/usr/bin/env python3
"""Acquire a new six-target ADS snapshot under the historical query grammar.

This creates a *new* time-dependent snapshot. It cannot recreate the frozen
2026 archive byte-for-byte. An ADS token must be supplied through
ADS_API_TOKEN or ADS_DEV_KEY; no credential is bundled or logged.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

import ads


QUERIES = {
    "Enceladus": 'full:"Enceladus" AND property:article year:2000-2024',
    "Europa": 'full:"Europa" AND full:"Jupiter" AND property:article year:2000-2024',
    "Mars": 'full:"Mars" AND full:"astrobiology" AND property:article year:2000-2024',
    "Titan": 'full:"Titan" AND full:"Saturn" AND property:article year:2000-2024',
    "Venus": 'full:"Venus" AND full:"atmosphere" AND property:article year:2000-2024',
    "Ganymede": 'full:"Ganymede" AND full:"Jupiter" AND property:article year:2000-2024',
}
FIELDS = ("bibcode", "title", "author", "aff", "pubdate", "citation_count", "keyword", "doctype", "orcid_pub")


def serializable(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-pages", type=int, default=200)
    args = parser.parse_args()
    token = os.getenv("ADS_API_TOKEN") or os.getenv("ADS_DEV_KEY")
    if not token:
        raise SystemExit("Set ADS_API_TOKEN or ADS_DEV_KEY; credentials are never stored in this repository.")
    ads.config.token = token
    args.output_dir.mkdir(parents=True, exist_ok=True)

    receipt = {"queries": QUERIES, "fields": FIELDS, "outputs": {}}
    for target, query in QUERIES.items():
        search = ads.SearchQuery(q=query, fl=list(FIELDS), rows=2000, max_pages=args.max_pages)
        rows = []
        for paper in search:
            row = {}
            for field in FIELDS:
                value = serializable(getattr(paper, field, None))
                row[field] = json.dumps(value, ensure_ascii=False) if isinstance(value, list) else value
            rows.append(row)
        path = args.output_dir / f"{target}_ads_raw.csv"
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        receipt["outputs"][target] = {"file": path.name, "rows": len(rows)}
    (args.output_dir / "acquisition_receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
