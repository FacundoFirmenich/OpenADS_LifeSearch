#!/usr/bin/env python3
"""Sentinel exact normalized-title membership, not a recall estimator."""
import csv
import html
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def norm(s):
    s=unicodedata.normalize('NFKD',html.unescape(s)).casefold()
    return ''.join(c for c in s if c.isalnum())
def main():
    u=defaultdict(list)
    registry=set()
    with (R/'source/raw/all_papers_raw_concat.csv').open(newline='',encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            u[norm(row['title'])].append((row['target'],row['bibcode']))
            registry.add(row['bibcode'])
    with (R/'provenance/external_anchors.tsv').open(newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f,delimiter='\t'))
    for row in rows:
        hits=u[norm(row['title'])]
        row['status']=('TARGET_ASSIGNMENT_FOUND' if any(t==row['target'] for t,_ in hits)
           else 'FOUND_ONLY_FOR_OTHER_TARGET' if hits else 'NO_EXACT_TITLE_MATCH')
        row['archive_matches']=';'.join(sorted({t+':'+b for t,b in hits}))
        row['checked_external_bibcode']=(
            '2020NatAs...4..266P' if row['doi']=='10.1038/s41550-019-0933-6' else '')
        row['external_bibcode_in_archive']=(
            str(row['checked_external_bibcode'] in registry) if row['checked_external_bibcode'] else '')
    with (R/'results/external_anchor_membership.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps(rows,indent=2))
if __name__=='__main__': main()
