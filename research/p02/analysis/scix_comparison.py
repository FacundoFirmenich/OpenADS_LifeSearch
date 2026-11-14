"""Replay historical and symmetric retrieval with an authorized SciX token."""
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

from p02_pipeline import TARGETS

R = Path(__file__).resolve().parents[1]
URL = "https://api.adsabs.harvard.edu/v1/search/query"
ADD = {"Europa":"Jupiter","Ganymede":"Jupiter","Titan":"Saturn","Mars":"astrobiology","Venus":"atmosphere"}
FILTER = "year:[2000 TO 2023] AND property:article"


def query(target, regime):
    q = f'full:"{target}"'
    if regime == "legacy_current" and target in ADD:
        q += f' AND full:"{ADD[target]}"'
    return q + " AND " + FILTER


def fetch(q, tag, out, token):
    page, start, expected, ids, evidence = 0, 0, None, {}, []
    # Explicit stable sort and start/rows pagination; fail closed on truncation.
    while True:
        params = dict(q=q, fl="bibcode,identifier,doi", sort="bibcode asc", start=start, rows=2000)
        req = urllib.request.Request(URL+"?"+urllib.parse.urlencode(params),
                                     headers={"Authorization":"Bearer "+token,"Accept":"application/json"})
        started = dt.datetime.now(dt.timezone.utc).isoformat()
        try:
            with urllib.request.urlopen(req, timeout=40) as f:
                data, headers = f.read(), dict(f.headers.items())
        except urllib.error.HTTPError as e:
            raise SystemExit(f"SciX {tag}: HTTP {e.code}; partial run not valid for inference") from None
        (out/f"{tag}.{page:03}.json").write_bytes(data)
        evidence.append(dict(utc=started, params=params, sha256=hashlib.sha256(data).hexdigest(), headers=headers))
        (out/f"{tag}.requests.json").write_text(json.dumps(evidence,indent=2)+"\n")
        ans = json.loads(data)["response"]
        if expected is None: expected = ans["numFound"]
        if ans["numFound"] != expected or ans["start"] != start:
            raise SystemExit(f"SciX {tag}: pagination/count drift")
        for row in ans["docs"]:
            b = row["bibcode"]
            if b in ids:
                raise SystemExit(f"SciX {tag}: duplicate bibcode across pages")
            ids[b] = row
        start += len(ans["docs"])
        if start == expected:
            return ids
        if not ans["docs"] or start > expected:
            raise SystemExit(f"SciX {tag}: short/invalid pagination")
        page += 1
        time.sleep(.25)


def write(name, rows, root):
    with (root/name).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def stats(a,b):
    return dict(n_left=len(a),n_right=len(b),intersection=len(a&b),only_left=len(a-b),
                only_right=len(b-a),jaccard=len(a&b)/len(a|b) if a|b else None)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path)
    ap.add_argument("--print-queries",action="store_true")
    args=ap.parse_args()
    regimes = ("legacy_current","symmetric_current")
    if args.print_queries:
        print(json.dumps({t:{r:query(t,r) for r in regimes} for t in TARGETS},indent=2));return
    if not args.output: ap.error("--output is required")
    token = os.getenv("SCIX_API_TOKEN") or os.getenv("ADS_API_TOKEN")
    if not token: raise SystemExit("BLOCKED_NO_CONFIGURED_TOKEN")
    out=args.output;out.mkdir(parents=True,exist_ok=False)
    with (R/"source/raw/all_papers_raw_concat.csv").open(newline="",encoding="utf-8-sig") as f:
        archive={t:set() for t in TARGETS}
        for row in csv.DictReader(f):
            if 2000 <= int(row["pubdate"][:4]) <= 2023:
                archive[row["target"]].add(row["bibcode"])
    with (R/"provenance/physical_evidence_anchors.tsv").open(newline="",encoding="utf-8") as f:
        anchors=list(csv.DictReader(f,delimiter="\t"))
    resolved={}
    for a in anchors:
        hits=fetch(f'identifier:"{a["bibcode"]}" OR doi:"{a["doi"]}"',"anchor_"+a["id"],out,token)
        # Prefer DOI-consistent records; retain multiple IDs as ambiguous, not misses.
        doi=a["doi"].casefold()
        matching={b for b,r in hits.items() if doi in {d.casefold() for d in r.get("doi",[])}}
        resolved[a["id"]]=(matching if matching else set(hits),bool(matching))
    result, panel=[],[]
    for t in TARGETS:
        one,two=(fetch(query(t,r),f"{r}_{t}",out,token) for r in regimes)
        if t=="Enceladus" and set(one)!=set(two):
            raise SystemExit("Identical Enceladus query changed within session; invalidate comparison")
        sets=(("archive_vs_legacy_current",archive[t],set(one)),
              ("legacy_current_vs_symmetric_current",set(one),set(two)),
              ("archive_vs_symmetric_current",archive[t],set(two)))
        result.extend(dict(target=t,comparison=label,**stats(a,b)) for label,a,b in sets)
        for a in (p for p in anchors if p["target"]==t):
            ids,consistent=resolved[a["id"]]
            row=dict(id=a["id"],target=t,archived_id=a["bibcode"],live_ids=";".join(sorted(ids)),
                     archive_expected=a["bibcode"] in archive[t],
                     identity_state="VERIFIED" if consistent and len(ids)==1 else "AMBIGUOUS" if ids else "NO_LIVE_IDENTIFIER_HIT",
                     legacy_current=bool(ids&one.keys()) if consistent and len(ids)==1 else None,
                     symmetric_current=bool(ids&two.keys()) if consistent and len(ids)==1 else None)
            panel.append(row)
    write("pairwise_set_comparisons.csv",result,out)
    write("anchor_live_membership.csv",panel,out)
    print("Complete: 18 set comparisons and 15 anchor membership records.")


if __name__=="__main__":
    main()
