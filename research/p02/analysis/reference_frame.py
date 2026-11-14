"""Fetch a provenance-bearing candidate frame from publisher-deposited references."""
import concurrent.futures
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import time
import urllib.request
import urllib.parse

ROOT=Path(__file__).resolve().parents[1]
SOURCES={"HEN":"10.1089/ast.2018.1955","COC":"10.1089/ast.2015.1295","NEV":"10.1089/ast.2017.1773"}


def fetch(path, query=None):
    url="https://api.crossref.org/works"+path
    if query: url += "?" + urllib.parse.urlencode(query)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"P02-ReferenceFrame/4.4 (bibliographic research)"}),timeout=20) as r:
                return r.read()
        except (OSError, TimeoutError):
            if attempt==2: raise
            time.sleep(attempt+1)


def csvfile(out, rows, names):
    with out.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=names);w.writeheader();w.writerows(rows)


def main():
    out=ROOT/"results/reference_frame"
    out.mkdir(exist_ok=False)
    stamp=dt.datetime.now(dt.timezone.utc).isoformat()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        sources=list(ex.map(lambda d:fetch("/"+d), SOURCES.values()))
    slots=[]
    counts={}
    for (s,d),raw in zip(SOURCES.items(),sources):
        (out/f"{s}.crossref.json").write_bytes(raw)
        m=json.loads(raw)["message"]
        refs=m.get("reference",[])
        counts[s]={"doi":d,"reported_references":m.get("reference-count"),"exposed":len(refs),"doi_slots":sum(bool(r.get("DOI")) for r in refs)}
        for n,a in enumerate(refs,1):
            slots.append(dict(source=s,source_doi=d,position=n,doi=a.get("DOI","").strip().lower()))
    ids=sorted({r["doi"] for r in slots if r["doi"]})
    if not ids: raise RuntimeError("no DOI-bearing references returned")
    batches=[ids[k:k+15] for k in range(0,len(ids),15)]

    def batch(b):
        return fetch("",dict(filter=",".join("doi:"+d for d in b),rows=len(b),select="DOI,title,type,published,author"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        replies=list(ex.map(batch,batches))
    metadata={}
    for n,data in enumerate(replies):
        (out/f"metadata.{n:03}.crossref.json").write_bytes(data)
        for m in json.loads(data)["message"]["items"]:
            doi=m["DOI"].lower()
            assert doi in batches[n] and doi not in metadata
            metadata[doi]=m
    source_ids={doi:sorted({r["source"] for r in slots if r["doi"]==doi}) for doi in ids}
    frame,packet=[],[]
    for doi in ids:
        row=metadata.get(doi)
        year=((row or {}).get("published",{}).get("date-parts") or [[None]])[0][0]
        title=((row or {}).get("title") or [""])[0]
        typ=(row or {}).get("type","")
        ident=hashlib.sha256(doi.encode()).hexdigest()[:16]
        status=("UNRESOLVED_METADATA" if not row or not year else "CANDIDATE_UNLABELED" if
                typ=="journal-article" and 2000<=year<=2023 else "OUTSIDE_TYPE_YEAR")
        frame.append(dict(id=ident,doi=doi,year=year,type=typ,title=title,sources=";".join(source_ids[doi]),state=status))
        if status=="CANDIDATE_UNLABELED":
            packet.append(dict(id=ident,doi=doi,year=year,title=title))
    assert len({r["id"] for r in frame})==len(ids)
    csvfile(out/"reference_slots.csv",slots,["source","source_doi","position","doi"])
    csvfile(out/"candidate_frame.csv",frame,["id","doi","year","type","title","sources","state"])
    csvfile(out/"blinded_reference_packet.csv",packet,["id","doi","year","title"])
    receipt=dict(retrieved_utc=stamp,sources=counts,reference_slots=len(slots),unique_dois=len(ids),
                 candidate_articles=len(packet),unresolved_metadata=sum(r["state"]=="UNRESOLVED_METADATA" for r in frame),
                 doi_free_slots=sum(not r["doi"] for r in slots),
                 status="No independent eligibility labels or recall estimate")
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2))


if __name__=="__main__":
    main()
