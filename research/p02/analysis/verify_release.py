"""Verify provenance and independently reconstruct the published adjudications."""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    with (ROOT / "results" / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def verify_sources():
    manifest = {}
    for line in (ROOT / "provenance/P02_DRIVE_MANIFEST.sha256").read_text().splitlines():
        if not line.strip():
            continue
        h, p = line.split(maxsplit=1)
        manifest[p.removeprefix("./")] = h
    paths = {
        "analysis/p02_pipeline.py": "src/p02_pipeline.py",
        "source/manuscript_v4_1.pdf": "final/P02_attention_landscapes_manuscript_v4.1.0.pdf",
        "source/supplement_v4_1.pdf": "final/P02_attention_landscapes_supplement_v4.1.0.pdf",
    }
    for pattern, prefix in (("source/raw/*.csv", "data/raw/"),
                            ("source/v41_tables/*.csv", "results/"),
                            ("paper/figures/fig*.pdf", "results/figures/")):
        paths.update({str(f.relative_to(ROOT)): prefix + f.name for f in ROOT.glob(pattern)})
    assert len(paths) == 37
    for p, original in paths.items():
        assert hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == manifest[original], p
    return len(paths)


def verify_contrasts():
    receipt = json.loads((ROOT / "results/joint_trends_receipt.json").read_text())
    detail = read("joint_trend_contrasts.csv")
    assert len(detail) == 4320
    dims = ("regime", "window", "metric", "target_a", "target_b")
    ids = set()
    groups = defaultdict(list)
    for r in detail:
        key = tuple(r[k] for k in dims)
        ident = key + (r["spec_id"],)
        assert ident not in ids
        ids.add(ident)
        x, s, lo, hi, pl, ph = (float(r[k]) for k in (
            "estimate_pp", "bootstrap_sd_pp", "joint_low_pp", "joint_high_pp",
            "percentile_low_pp", "percentile_high_pp"))
        assert s > 0 and all(map(math.isfinite, (x, s, lo, hi, pl, ph))) and pl <= ph
        delta = receipt["regimes"][r["regime"]]["max_critical"] * s
        assert math.isclose(x - delta, lo, abs_tol=2e-12)
        assert math.isclose(x + delta, hi, abs_tol=2e-12)
        groups[key].append((x, lo, hi))
    expected_window = read("joint_trend_windows.csv")
    assert len(expected_window) == len(groups) == 180
    states = defaultdict(dict)
    counts = Counter()
    for row in expected_window:
        key = tuple(row[k] for k in dims)
        group = groups.pop(key)
        assert len(group) == 24
        x, lo, hi = zip(*group)
        extrema = {"estimate_min_pp": min(x), "estimate_max_pp": max(x),
                   "band_envelope_min_pp": min(lo), "band_envelope_max_pp": max(hi)}
        assert all(math.isclose(v, float(row[k]), abs_tol=1e-12) for k, v in extrema.items())
        numpos, numneg = sum(a > 0 for a in lo), sum(b < 0 for b in hi)
        assert (numpos, numneg) == (int(row["n_joint_positive"]), int(row["n_joint_negative"]))
        state = "A_GT_B" if numpos == 24 else "B_GT_A" if numneg == 24 else "UNRESOLVED"
        assert state == row["joint_state"]
        margin = min(lo) > 2 or max(hi) < -2
        assert (str(min(lo) > 2), str(max(hi) < -2)) == (
            row["all_positive_beyond_2pp"], row["all_negative_beyond_2pp"])
        regime, window, metric, a, b = key
        states[regime, metric, a, b][window] = (min(x) > 0, max(x) < 0, numpos == 24, numneg == 24)
        counts[regime, window] += state != "UNRESOLVED"
        counts[regime, "margin"] += margin
    expected_reverse = read("joint_trend_reversals.csv")
    assert len(expected_reverse) == len(states) == 60
    assert {k[1:]: v for k, v in states.items() if k[0] == "global"} == {
        k[1:]: v for k, v in states.items() if k[0] == "year_stratified"}
    for r in expected_reverse:
        key = tuple(r[k] for k in ("regime", "metric", "target_a", "target_b"))
        flags = states.pop(key)
        sequences = {k: "|".join(w for w in sorted(flags) if flags[w][i])
                     for i, k in enumerate(("descriptive_positive", "descriptive_negative",
                                           "supported_positive", "supported_negative"))}
        assert all(v == r[k] for k, v in sequences.items())
        for prefix in ("descriptive", "supported"):
            reversal = bool(sequences[prefix + "_positive"] and sequences[prefix + "_negative"])
            assert str(reversal) == r[prefix + "_reversal"]
            counts[r["regime"], prefix] += reversal
    for regime in receipt["regimes"]:
        assert [counts[regime, k] for k in (
            "2000_2023", "2010_2023", "2019_2023", "margin", "descriptive", "supported"
        )] == [10, 6, 0, 9, 8, 0]
    return len(detail)


def verify_retrieval():
    anchors = read("external_anchor_membership.csv")
    assert Counter(r["status"] for r in anchors) == {
        "TARGET_ASSIGNMENT_FOUND": 8, "NO_EXACT_TITLE_MATCH": 1}
    missing = next(r for r in anchors if r["status"] == "NO_EXACT_TITLE_MATCH")
    assert (missing["checked_external_bibcode"], missing["external_bibcode_in_archive"]) == (
        "2020NatAs...4..266P", "False")
    packet = read("retrieval_coder_packet.csv")
    sample = read("retrieval_sampling_key.csv")
    assert len(packet) == len(sample) == 720
    assert len({r["bibcode"] for r in packet}) == 707
    assert len({r["id"] for r in sample}) == 720
    assert {r["id"]: r["target"] for r in packet} == {r["id"]: r["target"] for r in sample}
    strata = Counter((r["target"], r["period"], r["title_keyword_stratum"]) for r in sample)
    assert len(strata) == 36 and set(strata.values()) == {20}
    assert all(math.isclose(float(r["inclusion_probability"]), 20 / int(r["N_h"])) for r in sample)
    return len(packet)


if __name__ == "__main__":
    print(json.dumps({"verified_source_files": verify_sources(), "verified_contrast_rows": verify_contrasts(),
                      "verified_unlabeled_assignments": verify_retrieval()}, indent=2))
