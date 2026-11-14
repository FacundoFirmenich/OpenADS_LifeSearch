"""Build P02's independent, offline, source-bound article and research views."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
C=ROOT/"companion"

def csvs(p, sep=","):
    with (ROOT/p).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f,delimiter=sep))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def make():
    files={
       "anchors":"results/physical_evidence_anchor_audit.csv",
       "directions":"results/v44_direction_map.csv",
       "bands":"results/joint_trend_contrasts.csv",
       "years":"results/v44_year_influence.csv",
       "reversals":"results/joint_trend_reversals.csv",
       "literature":"provenance/v45_sources.tsv",
    }
    nodes=[]; edges=[]; gates=[]
    def node(id,label,kind,group,text,limit="",url="",data=None):
        nodes.append(dict(id=id,label=label,kind=kind,group=group,text=text,limit=limit,url=url,data=data))
        return id
    def edge(a,b,kind,note):
        edges.append(dict(source=a,target=b,kind=kind,note=note))
    def gate(id,label,group,premises,result,text):
        node(id,label,"AND gate",group,text)
        for a in premises: edge(a,id,"requires","Required together; no single input suffices.")
        edge(id,result,"derives",text)
        gates.append(dict(id=id,inputs=premises,output=result))

    node("physical","Physical observations","branch","Physical","Primary observations and model-based interpretations by local environment.","No observation of life is inferred.")
    node("audit","Retrieval by identity","operation","Archive","Compare DOI-linked primary records against the historical archive by bibcode and normalized title.","No query or index causation identified.")
    node("archive","Archived ADS","input","Archive","9,021 papers; 9,762 assignments during 2000–2023. One paper can belong to several targets.","Not a census; frozen historical retrieval.")
    node("trends","Publication trajectories","operation","Inference","OLS and Theil–Sen of log(1 + weighted yearly count), transformed back to annual rates.","Neither publication growth nor a citation count measures physical habitability.")
    node("depend","Shared paper draws","condition","Inference","A bibcode receives one draw weight per replicate, reused across targets, specifications and windows.","Both regimes condition on the same archive and fixed weights.")
    node("unanimity","Unanimous point sign","condition","Inference","All 24 observed contrasts in a pair–window–estimator cell have the same strict sign.")
    node("intervals","Simultaneous bands","condition","Inference","2,160 contrasts; observed dependence retained under both paper-resampling regimes.","Approximate conditional coverage, not a guarantee for new years or missing literature.")
    node("joint","16 supported local directions","claim","Inference","The same 16 of 90 cells receive joint support under both resampling schemes.","No opposite directions jointly supported among eight descriptive reversals.")
    node("influence","Delete-one-year influence","check","Inference","All 16 supported cells keep unanimous point sign under every single-year omission. In 2019–2023, 9 of 19 unanimous descriptive cells survive.","Point-estimate influence is not validation of statistical coverage or temporal independence.")
    node("omissions","Two named omissions","claim","Archive","Porco (2006) and Paganini (2020) are not in the archive by bibcode or normalized title.","13/15 selected anchors does not estimate recall.")
    node("scope","Different questions, no common rank","boundary","Scope","The physical record, its retrieval, and support for attention trends are distinct.","Does not rank habitability, probability of life, or mission value.")
    node("recall","Unestimated coverage","boundary","Scope","A frame of 374 date- and type-eligible candidate articles is ready for blind eligibility coding.","No evidence-based recall estimate; late years underrepresented.")
    node("live","Live query comparison pending","boundary","Scope","Historical versus symmetric templates require a valid SciX API credential.","Public discovery did not execute the authenticated comparison.")
    node("lit","State of the art","branch","Literature","Recent and prior work linked by scope and intended transfer.","Literature after 2023 is context, not inserted into historical counts.")
    node("titan_update","Titan: contested interior","claim","Literature","The 2012 ocean interpretation belongs to the historical record. Post-cutoff reanalysis, challenge, and reply must be distinguished.","These works are not independent direct measurements of subsurface water.")
    edge("physical","audit","feeds","Named primary evidence supplies identities to check.")
    edge("archive","audit","feeds","Historical target assignments queried by identity.")
    edge("archive","trends","feeds","Shared assignments become weighted counts.")
    edge("trends","unanimity","derives","Compare the pair's point estimates under 24 variants.")
    edge("trends","intervals","feeds","Bootstrap reuses the measurement operator.")
    edge("depend","intervals","requires","Preserve dependence induced by repeated use of the same paper.")
    gate("g_trend","Direction gate","Inference",["unanimity","intervals"],"joint","Both regimes support the same signed direction in every variant.")
    edge("joint","influence","checked by","Delete a year without claiming new simultaneous coverage.")
    edge("audit","omissions","derives","Two named records lack both expected bibcode and normalized title.")
    edge("omissions","recall","limits","Purposive cases cannot estimate corpus recall.")
    edge("live","omissions","limits","An archive absence alone cannot attribute the cause.")
    for u in ["physical","omissions","joint"]:
        edge(u,"scope","limits","Keep the scope of this branch separate from claims in the other branches.")
    for row in csvs(files["anchors"]):
        i=node("anchor_"+row["id"],row["title"],"anchor","Physical",
               row["limited_inference"],row["interpretation_class"],"https://doi.org/"+row["doi"],row)
        edge(i,"physical","supports","Target and environment-specific observation; respect stated interpretation.")
        edge(i,"omissions" if row["status"]=="NOT_IN_ARCHIVE" else "audit","checked by","Historical membership: "+row["status"])
    detail=defaultdict(list); deletion=defaultdict(list); rev=set()
    key=lambda r:(r["target_a"],r["target_b"],r["window"],r["metric"])
    for r in csvs(files["bands"]): detail[key(r)].append(r)
    for r in csvs(files["years"]): deletion[key(r)].append(r)
    for r in csvs(files["reversals"]):
        if r["descriptive_reversal"]=="True":
            for w in (r["descriptive_positive"]+"|"+r["descriptive_negative"]).split("|"):
                rev.add((r["target_a"],r["target_b"],w,r["metric"]))
    assert len(detail)==len(deletion)==90
    for r in csvs(files["directions"]):
        key0=key(r); assert len(detail[key0])==48
        id="cell_"+"_".join(key0).lower()
        group="Inference"
        node(id,f'{r["target_a"]} / {r["target_b"]} • {r["window"]} • {r["metric"]}',"contrast",group,
             "The sign is for A minus B. Inspect all 24 specifications in each resampling regime and the year-deletion sensitivity.",
             "Short-window non-support is not equality.",data=dict(summary=r,bands=detail[key0],deletions=deletion[key0],reversal=key0 in rev))
        edge("joint" if int(r["joint_sign"]) else "trends",id,"contains","Pair–window–estimator result; scope remains local.")
        edge("influence",id,"checked by","Year-deletion diagnostics for this cell.")
    lrows=csvs(files["literature"],"\t")
    assert len({r["url"] for r in lrows})==len(lrows)
    for n,r in enumerate(lrows,1):
        id=node("ref_"+str(n),r["title"],r["type"],"Literature",r["transfer"],"External source; no change to historical estimates.",r["url"],r)
        edge("lit",id,"contains","Classified by its scope and intended transfer to P02.")
        if r["title"].startswith("Titan tidal"): edge(id,"titan_update","qualifies","Published interpretation, challenge or reply after 2023.")
    ids={n["id"] for n in nodes}
    assert len(ids)==len(nodes) and all({e["source"],e["target"]}<=ids for e in edges)
    assert len({(e["source"],e["target"],e["kind"]) for e in edges})==len(edges)
    for g in gates:
        assert len(set(g["inputs"]))>=2 and g["id"] in ids and set(g["inputs"])<ids and g["output"] in ids
    tours=[
      ["Two missing papers","omissions"],["Six targets and two time regimes","archive"],
      ["Why a direction needs two ingredients","g_trend"],["What one year changes","influence"],
      ["How to read a physical dispute","titan_update"],["What remains unmeasured","recall"]]
    return dict(title="P02 Evidence Atlas",release="v4.5",nodes=nodes,edges=edges,gates=gates,tours=tours,
                article=[n["id"] for n in nodes if n["id"] in {"physical","audit","archive","trends","depend","unanimity","intervals","joint","g_trend","influence","omissions","scope","recall","live"}],
                sources={k:{"path":p,"sha256":sha(ROOT/p)} for k,p in files.items()})

def main():
    model=make()
    text=json.dumps(model,ensure_ascii=False,separators=(",",":"),sort_keys=True)
    safe=text.replace("<","\\u003c")
    tpl=(C/"atlas.template.html").read_text(encoding="utf-8")
    assert tpl.count("__P02_DATA__")==tpl.count("__P02_MODE__")==1
    receipt={"model_sha256":hashlib.sha256(text.encode()).hexdigest(),"counts":dict(
             nodes=len(model["nodes"]),edges=len(model["edges"]),gates=len(model["gates"]),contrast_cells=90,anchors=15),"files":{}}
    (C/"graph_model.json").write_text(text,encoding="utf-8")
    for mode in ["epistemic_graph","supergraph"]:
        p=C/(mode+".html")
        p.write_text(tpl.replace("__P02_MODE__",mode).replace("__P02_DATA__",safe),encoding="utf-8")
        receipt["files"][p.name]=sha(p)
        recovered=p.read_text().split('<script id="model" type="application/json">',1)[1].split("</script>",1)[0]
        assert json.loads(recovered)==model
    (C/"BUILD_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt))

if __name__=="__main__": main()
