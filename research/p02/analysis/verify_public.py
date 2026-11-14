"""Verify the public projection without the restricted ADS input archive."""
import csv
import hashlib
import json
import math
from pathlib import Path

from verify_release import verify_contrasts

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_manifest():
    entries = (ROOT / "PUBLIC_MANIFEST.sha256").read_text().splitlines()
    for entry in entries:
        expected, path = entry.split(maxsplit=1)
        assert digest(ROOT / path) == expected, path
    return len(entries)


def verify_graph():
    companion = ROOT / "companion"
    receipt = json.loads((companion / "BUILD_RECEIPT.json").read_text())
    model_path = companion / "graph_model.json"
    assert digest(model_path) == receipt["model_sha256"]
    model = json.loads(model_path.read_text())
    for source in model["sources"].values():
        assert digest(ROOT / source["path"]) == source["sha256"], source["path"]
    for name, expected in receipt["files"].items():
        html = companion / name
        assert digest(html) == expected, name
        embedded = html.read_text().split('<script id="model" type="application/json">', 1)[1]
        assert json.loads(embedded.split("</script>", 1)[0]) == model, name
    assert len(model["nodes"]) == receipt["counts"]["nodes"] == 155
    assert sum(node["kind"] == "contrast" for node in model["nodes"]) == 90
    return len(model["nodes"])


def verify_sampling_design():
    path = ROOT / "results/retrieval_sampling_design.csv"
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == len({(r["target"], r["period"], r["title_keyword_stratum"]) for r in rows}) == 36
    assert sum(int(r["N_h"]) for r in rows) == 9762
    assert sum(int(r["n_h"]) for r in rows) == 720
    for row in rows:
        assert math.isclose(float(row["inclusion_probability"]), int(row["n_h"]) / int(row["N_h"]))
    return len(rows)


if __name__ == "__main__":
    print(json.dumps({
        "verified_files": verify_manifest(),
        "verified_contrasts": verify_contrasts(),
        "verified_graph_nodes": verify_graph(),
        "verified_sampling_strata": verify_sampling_design(),
    }, indent=2))
