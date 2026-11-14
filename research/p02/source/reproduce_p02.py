"""Bounded, real-corpus P02 reproduction and additive jurisdictional analysis.

Never edits the recovered release. No Monte Carlo or observational synthesis.
The archived bootstrap is disclosed as historical, not rerun or posterior.
"""
from pathlib import Path
from collections import Counter, defaultdict
import csv
import hashlib
import importlib.util
import itertools
import json
import math
import platform
import statistics
import ast
import types

import numpy as np
import pandas as pd
import scipy

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "p02_recuperado"
OUT = ROOT / "p02_revision_ejecutada"
OUT.mkdir(exist_ok=True)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


manifest = {}
for line in (ROOT / "P02_DRIVE_MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
    if line.strip():
        expected, name = line.split(maxsplit=1)
        manifest[name.lstrip("*").removeprefix("./")] = expected
available = []
for name, expected in manifest.items():
    path = SRC / name
    if path.is_file():
        actual = digest(path)
        assert actual == expected, (name, actual, expected)
        available.append(name)
raw_hashes = {n: manifest[n] for n in available if n.startswith("data/raw/")}
assert len(raw_hashes) == 7

# Independent standard-library calculation, without calling release functions.
records = rows(SRC / "data/raw/all_papers_raw_concat.csv")
unique = {}
targets = list(dict.fromkeys(r["target"] for r in records))
for rec in records:
    rec["y"] = int(rec["pubdate"][:4])
    rec["c"] = float(rec["citation_count"])
    assert math.isfinite(rec["c"]) and rec["c"] >= 0
    unique.setdefault(rec["bibcode"], rec)
assert len(records) == 10317 and len(unique) == 9513
complete = [r for r in records if 2000 <= r["y"] <= 2023]
unique_complete = {r["bibcode"]: r for r in complete}
by_year = defaultdict(list)
for rec in unique_complete.values():
    by_year[rec["y"]].append(rec)
means = {y: statistics.mean(r["c"] for r in rr) for y, rr in by_year.items()}
assert all(v > 0 for v in means.values())
percentiles = {}
reference_audit = []
for year, rr in sorted(by_year.items()):
    frequency = Counter(r["c"] for r in rr)
    lower = 0
    ranks = {}
    for value, frequency_count in sorted(frequency.items()):
        ranks[value] = (lower + (frequency_count + 1) / 2) / len(rr)
        lower += frequency_count
    for rec in rr:
        percentiles[rec["bibcode"]] = ranks[rec["c"]]
    actual_share = sum(ranks[r["c"]] >= .90 for r in rr) / len(rr)
    reference_audit.append({"year": year, "n_unique": len(rr),
                            "mean_citations": means[year],
                            "share_average_rank_ge_090": actual_share,
                            "n_in_tied_citation_groups": sum(n for n in frequency.values() if n > 1)})

computed = []
reference_loto = []
years = list(range(2000, 2024))
xmean = statistics.mean(years)
xss = sum((y - xmean) ** 2 for y in years)
for target in targets:
    selected = [r for r in complete if r["target"] == target]
    annual = Counter(r["y"] for r in selected)
    logcounts = [math.log1p(annual[y]) for y in years]
    zmean = statistics.mean(logcounts)
    ols = sum((y - xmean) * (z - zmean) for y, z in zip(years, logcounts)) / xss
    slopes = [(logcounts[j] - logcounts[i]) / (years[j] - years[i])
              for i in range(len(years)) for j in range(i + 1, len(years))]
    own = {r["bibcode"] for r in selected}
    external = {y: [r["c"] for r in rr if r["bibcode"] not in own] for y, rr in by_year.items()}
    ext_means = {y: statistics.mean(v) if v else None for y, v in external.items()}
    assert all(ext_means[r["y"]] is not None and ext_means[r["y"]] > 0 for r in selected)
    for y in years:
        reference_loto.append({"target": target, "year": y, "n_external": len(external[y]),
                               "mean_external_citations": ext_means[y]})
    computed.append({"target": target, "scale": len(selected),
                     "trend_ols": math.expm1(ols), "trend_theilsen": math.expm1(statistics.median(slopes)),
                     "citation_ratio": statistics.mean(r["c"] / means[r["y"]] for r in selected),
                     "citation_ratio_loo": statistics.mean(r["c"] / ext_means[r["y"]] for r in selected),
                     "citation_percentile": statistics.mean(percentiles[r["bibcode"]] for r in selected),
                     "top10_share": statistics.mean(percentiles[r["bibcode"]] >= .9 for r in selected)})
canonical = pd.DataFrame(computed).set_index("target").sort_index()
archived = pd.read_csv(SRC / "results/canonical_metrics.csv").set_index("target").sort_index()
assert canonical.index.equals(archived.index)
columns = list(canonical.columns)
np.testing.assert_allclose(canonical[columns], archived[columns], rtol=1e-10, atol=1e-12)
independent_max_error = float(np.max(np.abs(canonical[columns].to_numpy() - archived[columns].to_numpy())))
canonical.to_csv(OUT / "canonical_independent.csv")
pd.DataFrame(reference_audit).to_csv(OUT / "year_reference_audit.csv", index=False)
pd.DataFrame(reference_loto).to_csv(OUT / "loto_reference_audit.csv", index=False)
print("Independent canonical reproduction: 42 values PASS", flush=True)

# The full 886-line source was read. Only plotting setup is omitted in the
# execution view: no numerical function is changed; no dummy module is injected.
# This avoids requiring a GUI/graphics dependency for a non-graphical audit.
source_text = (SRC / "src/p02_pipeline.py").read_text(encoding="utf-8")
tree = ast.parse(source_text)
omitted = []
body = []
for node in tree.body:
    statement = ast.get_source_segment(source_text, node)
    if statement == "import matplotlib.pyplot as plt" or statement.startswith("plt.rcParams.update("):
        omitted.append(statement)
    else:
        body.append(node)
assert len(omitted) == 2
tree.body = body
P = types.ModuleType("p02_verified_numeric_view")
exec(compile(tree, str(SRC / "src/p02_pipeline.py"), "exec"), P.__dict__)
df, qc = P.load_and_validate(SRC / "data/raw")
rerun_canonical, _ = P.canonical_outputs(df)
np.testing.assert_allclose(rerun_canonical.set_index("target").sort_index()[columns], canonical[columns], rtol=1e-10, atol=1e-12)
rerun_specs, _, rerun_pairs = P.specification_multiverse(df)
old_specs = pd.read_csv(SRC / "results/specification_results.csv")
keys = ["spec_id", "retrieval", "attribution", "team_rule", "window", "metric", "target"]
fresh = rerun_specs.set_index(keys).sort_index()
old = old_specs.set_index(keys).sort_index()
assert fresh.index.equals(old.index) and len(fresh) == 3024
np.testing.assert_allclose(fresh.value, old.value, rtol=1e-10, atol=1e-12)
np.testing.assert_array_equal(fresh["rank"], old["rank"])
fresh.reset_index().to_csv(OUT / "specifications_reproduced.csv", index=False)
print("All 72 specifications / 3024 metric-target values and ranks: PASS", flush=True)

# Additive edge classification: exhaustive direction partition with a declared
# numerical tolerance, not a statistical equivalence region.
ATOL, RTOL = 1e-12, 1e-9
boot = pd.read_csv(SRC / "results/bootstrap_pairwise_dominance.csv")
boot_lookup = {(r.metric, r.target_a, r.target_b): r for r in boot.itertuples()}
edge_rows = []
for dimension in ["ALL", "window", "retrieval", "attribution", "team_rule"]:
    groups = [("ALL", rerun_specs)] if dimension == "ALL" else rerun_specs.groupby(dimension, sort=True)
    for value, group in groups:
        for metric, gg in group.groupby("metric", sort=True):
            wide = gg.pivot(index="spec_id", columns="target", values="value")
            for a, b in itertools.combinations(P.TARGETS, 2):
                av, bv = wide[a].to_numpy(), wide[b].to_numpy()
                finite = np.isfinite(av) & np.isfinite(bv)
                tol = ATOL + RTOL * np.maximum(np.abs(av), np.abs(bv))
                tie = finite & (np.abs(av - bv) <= tol)
                ahead = finite & (av - bv > tol)
                behind = finite & (bv - av > tol)
                n, nt, na, nb, invalid = len(wide), int(tie.sum()), int(ahead.sum()), int(behind.sum()), int((~finite).sum())
                assert nt + na + nb + invalid == n
                status = ("NOT_ESTIMABLE" if invalid else "A_GT_B_IN_TESTED_SEGMENT" if na == n else
                          "B_GT_A_IN_TESTED_SEGMENT" if nb == n else "NUMERICAL_TIE" if nt == n else
                          "DIRECTION_DEPENDS_ON_SPECIFICATION")
                historical = boot_lookup.get((metric, a, b))
                # Bootstrap covers only the canonical full/unit/inclusive 2000-2023
                # specification. It is never inherited by other segments.
                edge_rows.append({"segment_dimension": dimension, "segment_value": value,
                                  "metric": metric, "target_a": a, "target_b": b,
                                  "n_specifications": n, "n_a_gt_b": na, "n_b_gt_a": nb,
                                  "n_numerical_tie": nt, "n_nonfinite": invalid, "local_status": status,
                                  "canonical_bootstrap_fraction_a_gt_b_archived": historical.p_a_gt_b if dimension == "ALL" and historical else None,
                                  "canonical_bootstrap_n_archived": historical.n_bootstrap if dimension == "ALL" and historical else None,
                                  "segment_joint_sampling_coverage": "NOT_ESTIMATED"})
edges = pd.DataFrame(edge_rows)
edges.to_csv(OUT / "local_jurisdiction_edges.csv", index=False)
global_edges = edges[edges.segment_dimension == "ALL"]
window_edges = edges[edges.segment_dimension == "window"]
reversals = []
for (metric, a, b), g in window_edges.groupby(["metric", "target_a", "target_b"]):
    aa = g.loc[g.local_status == "A_GT_B_IN_TESTED_SEGMENT", "segment_value"].tolist()
    bb = g.loc[g.local_status == "B_GT_A_IN_TESTED_SEGMENT", "segment_value"].tolist()
    if aa and bb:
        reversals.append({"metric": metric, "target_a": a, "target_b": b,
                          "a_gt_b_windows": "|".join(aa), "b_gt_a_windows": "|".join(bb)})
pd.DataFrame(reversals, columns=["metric", "target_a", "target_b", "a_gt_b_windows", "b_gt_a_windows"]).to_csv(OUT / "window_direction_reversals.csv", index=False)

# Compare general substring retrieval to the word-boundary audit on REAL records.
enc = df[df.target == "Enceladus"]
audit, audit_summary = P.enceladus_retrieval_audit(df)
general_ids = set(enc.loc[P.retrieval_mask(enc, "strict_text"), "bibcode"])
audit_ids = set(audit.loc[audit.strict_text_pass, "bibcode"])
old_summary = pd.read_csv(SRC / "results/enceladus_retrieval_audit_summary.csv")
assert dict(zip(audit_summary.screening_status, audit_summary.n_records)) == dict(zip(old_summary.screening_status, old_summary.n_records))
audit["historical_screening_status"] = audit.screening_status
audit["screening_status"] = audit.screening_status.replace({"LOWER_BOUND_INCLUDED": "TEXT_MATCH_NOT_RELEVANCE_VALIDATED"})
audit.to_csv(OUT / "enceladus_screening_semantics_corrected.csv", index=False)
reference_share = [r["share_average_rank_ge_090"] for r in reference_audit]
report = {
    "schema": "p02-real-corpus-reproduction-v1", "date": "2026-09-08",
    "runtime": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__},
    "manifest_members_verified": len(available), "manifest_members_total": len(manifest),
    "missing_members": sorted(set(manifest) - set(available)), "raw_hashes": raw_hashes,
    "source_pipeline_sha256": digest(SRC / "src/p02_pipeline.py"),
    "numerical_execution_view_omitted_plotting_setup_only": omitted,
    "raw_assignments": len(records), "raw_unique": len(unique), "complete_assignments": len(complete),
    "complete_unique": len(unique_complete), "independent_canonical_values": 42,
    "independent_canonical_max_abs_error": independent_max_error,
    "specifications_reproduced": 72, "specification_values_reproduced": 3024,
    "specification_max_abs_error": float(np.max(np.abs(fresh.value.to_numpy() - old.value.to_numpy()))),
    "global_edge_status_counts": global_edges.local_status.value_counts().to_dict(),
    "window_edge_status_counts": window_edges.local_status.value_counts().to_dict(),
    "segment_edge_count": len(edges), "window_reversals": reversals,
    "numerical_tolerance": {"atol": ATOL, "rtol": RTOL, "meaning": "numeric equality only; not practical equivalence"},
    "canonical_loto_min_external_n": min(r["n_external"] for r in reference_loto),
    "canonical_loto_min_external_mean": min(r["mean_external_citations"] for r in reference_loto),
    "pooled_year_top10_actual_share_range": [min(reference_share), max(reference_share)],
    "enceladus_strict_mask_symmetric_difference_bibcodes": sorted(general_ids ^ audit_ids),
    "renamed_machine_screen_records": int((audit.historical_screening_status == "LOWER_BOUND_INCLUDED").sum()),
    "bootstrap": "ARCHIVED_2000_REPLICATES_NOT_RERUN; canonical only; not posterior or joint coverage",
    "historical_acceptance_suite": "NOT_EXECUTED_AS_A_WHOLE; deterministic reproduction performed separately",
    "synthetic_observational_data": "NONE", "null_monte_carlo": "NOT_EXECUTED",
    "scientific_boundary": "Conditional on archived retrieval, tested specifications and numeric definitions; no mission-value ranking",
    "gate": "PASS"
}
(OUT / "REPRODUCTION_REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
