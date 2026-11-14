from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_frozen_aggregate_invariants():
    metrics = pd.read_csv(ROOT / "results/canonical/target_metrics.csv").set_index("target")
    assert metrics["raw_count"].to_dict() == {
        "Enceladus": 741,
        "Europa": 1375,
        "Mars": 5629,
        "Titan": 1649,
        "Venus": 464,
        "Ganymede": 459,
    }
    assert round(metrics["reciprocal_authorship_count"].sum(), 9) == round(3641.9765573514214, 9)
    assert metrics["rank_raw_count"].tolist() == metrics["rank_reciprocal_authorship"].tolist()
    assert metrics.loc["Enceladus", "rank_loglinear_rate"] == 1
    assert metrics.loc["Venus", "rank_citation_ratio"] == 1


def test_exact_rank_results():
    correlations = pd.read_csv(ROOT / "results/canonical/correlations_exact.csv")
    key = correlations.set_index(["metric_a", "metric_b"])
    raw_weighted = key.loc[("raw_count", "reciprocal_authorship_count")]
    raw_citations = key.loc[("raw_count", "corpus_year_normalized_citation_ratio")]
    assert round(raw_weighted.spearman_rho, 12) == 1.0
    assert round(raw_weighted.exact_two_sided_p, 12) == round(2 / 720, 12)
    assert round(raw_citations.spearman_rho, 12) == round(-29 / 35, 12)
    assert round(raw_citations.exact_two_sided_p, 12) == round(42 / 720, 12)


def test_overlap_accounting():
    overlap = pd.read_csv(ROOT / "results/canonical/overlap_degree.csv")
    assert dict(zip(overlap.n_targets, overlap.unique_bibcodes)) == {1: 8849, 2: 553, 3: 88, 4: 19, 5: 2, 6: 2}
    assert int((overlap.n_targets * overlap.unique_bibcodes).sum()) == 10317
    assert int(overlap.unique_bibcodes.sum()) == 9513
