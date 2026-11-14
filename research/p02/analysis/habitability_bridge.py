#!/usr/bin/env python3
"""Replay a purposive physical-evidence audit; never estimate recall from it."""
import csv
import hashlib
import html
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parents[1]


def norm(text):
    raw = re.sub(r"<[^>]+>", "", html.unescape(text))
    return "".join(c for c in unicodedata.normalize("NFKD", raw).casefold() if c.isalnum())


def split(values):
    return ";".join(sorted(set(values)))


def main():
    raw = R / "source/raw/all_papers_raw_concat.csv"
    expected = json.loads((R / "source/input_sha256.json").read_text())["raw/" + raw.name]
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == expected
    with (R / "provenance/physical_evidence_anchors.tsv").open(encoding="utf-8", newline="") as f:
        anchors = list(csv.DictReader(f, delimiter="\t"))
    for field in ("id", "doi", "bibcode"):
        assert len({a[field] for a in anchors}) == len(anchors), field
    by_id, by_title = defaultdict(list), defaultdict(list)
    with raw.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            by_id[row["bibcode"]].append(row)
            by_title[norm(row["title"])].append(row)
    assert len(by_id) == 9513 and sum(map(len, by_id.values())) == 10317
    for a in anchors:
        rows = by_id.get(a["bibcode"], ())
        title_rows = by_title.get(norm(a["title"]), ())
        expected_rows = [r for r in rows if r["target"] == a["target"]]
        canonical = [r for r in expected_rows if 2000 <= int(r["pubdate"][:4]) <= 2023]
        matching_titles = [r for r in rows if norm(r["title"]) == norm(a["title"])]
        assert not rows or matching_titles, a["id"]
        a.update(status=(
            "EXPECTED_TARGET" if expected_rows else "OTHER_TARGET_ONLY" if rows
            else "SAME_TITLE_DIFFERENT_ID_REVIEW" if title_rows else "NOT_IN_ARCHIVE"),
            matched_targets=split(r["target"] for r in rows),
            matched_expected_complete_year=bool(canonical),
            same_title_other_ids=split(r["bibcode"] for r in title_rows if r["bibcode"] != a["bibcode"]))
    out = R / "results"
    assert not any(a["status"].endswith("_REVIEW") for a in anchors)
    with (out / "physical_evidence_anchor_audit.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(anchors[0]))
        writer.writeheader()
        writer.writerows(anchors)
    by_target = {}
    for t in sorted({a["target"] for a in anchors}):
        by_target[t] = dict(sorted(Counter(a["status"] for a in anchors if a["target"] == t).items()))
    checks = {a["id"]: a["status"] for a in anchors}
    assert len(by_id) == 9513
    assert checks["E01"] == checks["U02"] == "NOT_IN_ARCHIVE"
    assert all(a["matched_expected_complete_year"] for a in anchors if a["status"] == "EXPECTED_TARGET")
    assert next(a for a in anchors if a["id"] == "E02")["same_title_other_ids"] == "2009Natur.460.1164W"
    assert next(a for a in anchors if a["id"] == "V03")["matched_targets"] == "Mars;Venus"
    receipt = {"selection": "Purposive and retrospective; no sampling frame or aggregate recall estimate.",
               "archive_refs": len(by_id), "expected_complete_year": sum(a["matched_expected_complete_year"] for a in anchors),
               "n_anchors": len(anchors), "statuses": dict(sorted(Counter(checks.values()).items())), "by_target": by_target,
               "missing_anchor_ids": [a["id"] for a in anchors if a["status"] == "NOT_IN_ARCHIVE"]}
    (out / "physical_evidence_anchor_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
