"""Verify the two additional named, non-panel Europa archive matches."""
import csv
import html
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
    "2023Sci...381.1305V":"Endogenous CO2 ice mixture on the surface of Europa and no detection of plume activity",
    "2023Sci...381.1308T":"The distribution of CO2 on Europa indicates an internal source of carbon",
}
with (ROOT/"source/raw/all_papers_raw_concat.csv").open(encoding="utf-8-sig",newline="") as f:
    matches=[r for r in csv.DictReader(f) if r["target"]=="Europa" and r["bibcode"] in EXPECTED]
def title(r):
    return ' '.join(re.sub(r"<[^>]+>","",html.unescape(r["title"])).split())
assert len(matches)==2 and {r["bibcode"]:title(r) for r in matches}==EXPECTED
for r in sorted(matches,key=lambda row:row["bibcode"]):
    print(r["bibcode"],r["target"],title(r))
