#!/usr/bin/env python3
"""Deterministic record-level reanalysis of the frozen six-target ADS snapshot.

The program does not call ADS, impute publications, simulate labels, or use
randomness. It consumes six author-held CSV exports and writes only aggregate
results, diagnostics, figures, and hashes. Raw ADS records are intentionally
not redistributed in this public repository.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGETS = ("Enceladus", "Europa", "Mars", "Titan", "Venus", "Ganymede")
YEARS = np.arange(2000, 2025)
REQUIRED_COLUMNS = {
    "bibcode",
    "title",
    "author",
    "aff",
    "pubdate",
    "citation_count",
    "keyword",
    "doctype",
    "orcid_pub",
}
EXPECTED_RAW_COUNTS = {
    "Enceladus": 741,
    "Europa": 1375,
    "Mars": 5629,
    "Titan": 1649,
    "Venus": 464,
    "Ganymede": 459,
}
EXPECTED_ASSIGNMENTS = 10317
EXPECTED_UNIQUE_BIBCODES = 9513


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_json_list(value: object) -> list:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    parsed = json.loads(str(value))
    if not isinstance(parsed, list):
        raise ValueError(f"Expected a JSON list, got {type(parsed).__name__}")
    return parsed


def load_snapshot(data_dir: Path, strict_expected: bool = False) -> tuple[pd.DataFrame, list[dict]]:
    frames: list[pd.DataFrame] = []
    manifest: list[dict] = []
    for target in TARGETS:
        path = data_dir / f"{target}_ads_raw.csv"
        if not path.is_file():
            raise FileNotFoundError(path)
        frame = pd.read_csv(path)
        missing = REQUIRED_COLUMNS.difference(frame.columns)
        if missing:
            raise ValueError(f"{path.name}: missing columns {sorted(missing)}")
        if frame["bibcode"].isna().any() or frame["bibcode"].duplicated().any():
            raise ValueError(f"{path.name}: null or duplicate bibcodes within target")
        frame = frame.copy()
        frame["target"] = target
        frame["year"] = frame["pubdate"].astype(str).str.slice(0, 4).astype(int)
        frame["citations"] = pd.to_numeric(frame["citation_count"], errors="raise").astype(float)
        if (~np.isfinite(frame["citations"])).any() or (frame["citations"] < 0).any():
            raise ValueError(f"{path.name}: invalid citation counts")
        frame["author_count"] = frame["author"].map(lambda value: len(parse_json_list(value)))
        frame["reciprocal_authorship_weight"] = 1.0 / frame["author_count"].clip(lower=1)
        frames.append(frame)
        manifest.append(
            {
                "file": path.name,
                "target": target,
                "rows": int(len(frame)),
                "bytes": int(path.stat().st_size),
                "sha256": sha256(path),
            }
        )
    data = pd.concat(frames, ignore_index=True)
    if strict_expected:
        observed = data.groupby("target", sort=False).size().to_dict()
        if observed != EXPECTED_RAW_COUNTS:
            raise AssertionError((observed, EXPECTED_RAW_COUNTS))
        if len(data) != EXPECTED_ASSIGNMENTS or data["bibcode"].nunique() != EXPECTED_UNIQUE_BIBCODES:
            raise AssertionError((len(data), data["bibcode"].nunique()))
    return data, manifest


def metadata_conflicts(data: pd.DataFrame) -> pd.DataFrame:
    fields = ("title", "author", "pubdate", "citations", "doctype")
    repeated = data[data.duplicated("bibcode", keep=False)]
    rows: list[dict] = []
    for bibcode, group in repeated.groupby("bibcode", sort=True):
        conflicts = [field for field in fields if group[field].astype(str).nunique(dropna=False) > 1]
        if conflicts:
            rows.append(
                {
                    "bibcode": bibcode,
                    "targets": "|".join(sorted(group["target"].unique())),
                    "conflicting_fields": "|".join(conflicts),
                }
            )
    return pd.DataFrame(rows, columns=("bibcode", "targets", "conflicting_fields"))


def exact_spearman(x: Iterable[float], y: Iterable[float]) -> tuple[float, float]:
    rx = rankdata(np.asarray(tuple(x), dtype=float), method="average")
    ry = rankdata(np.asarray(tuple(y), dtype=float), method="average")
    observed = float(np.corrcoef(rx, ry)[0, 1])
    permuted = []
    for permutation in itertools.permutations(ry.tolist()):
        permuted.append(float(np.corrcoef(rx, np.asarray(permutation))[0, 1]))
    p_value = sum(abs(value) >= abs(observed) - 1e-12 for value in permuted) / len(permuted)
    return observed, float(p_value)


def compute_results(data: pd.DataFrame) -> dict[str, pd.DataFrame | dict]:
    conflicts = metadata_conflicts(data)
    unique = data.drop_duplicates("bibcode", keep="first").copy()
    year_reference = unique.groupby("year")["citations"].mean()
    if year_reference.empty or (year_reference <= 0).any():
        raise ValueError("The within-corpus annual citation reference must be positive")

    annual_rows: list[dict] = []
    target_rows: list[dict] = []
    for target in TARGETS:
        selected = data[data["target"] == target]
        raw_annual = selected.groupby("year").size().reindex(YEARS, fill_value=0).astype(int)
        weighted_annual = (
            selected.groupby("year")["reciprocal_authorship_weight"]
            .sum()
            .reindex(YEARS, fill_value=0.0)
        )
        for year in YEARS:
            annual_rows.append(
                {
                    "target": target,
                    "year": int(year),
                    "raw_count": int(raw_annual.loc[year]),
                    "reciprocal_authorship_count": float(weighted_annual.loc[year]),
                }
            )
        beta = float(np.polyfit(YEARS, np.log1p(raw_annual.to_numpy(dtype=float)), 1)[0])
        citation_ratio = float((selected["citations"] / selected["year"].map(year_reference)).mean())
        target_rows.append(
            {
                "target": target,
                "raw_count": int(len(selected)),
                "missing_author_records": int((selected["author_count"] == 0).sum()),
                "reciprocal_authorship_count": float(selected["reciprocal_authorship_weight"].sum()),
                "recent_reciprocal_count_2019_2024": float(
                    selected.loc[selected["year"].between(2019, 2024), "reciprocal_authorship_weight"].sum()
                ),
                "loglinear_annual_rate_2000_2024": float(np.expm1(beta)),
                "corpus_year_normalized_citation_ratio": citation_ratio,
            }
        )
    metrics = pd.DataFrame(target_rows)
    rank_columns = {
        "raw_count": "rank_raw_count",
        "reciprocal_authorship_count": "rank_reciprocal_authorship",
        "recent_reciprocal_count_2019_2024": "rank_recent_reciprocal",
        "loglinear_annual_rate_2000_2024": "rank_loglinear_rate",
        "corpus_year_normalized_citation_ratio": "rank_citation_ratio",
    }
    for source, destination in rank_columns.items():
        metrics[destination] = metrics[source].rank(ascending=False, method="min").astype(int)

    metric_names = tuple(rank_columns)
    correlation_rows: list[dict] = []
    for metric_a, metric_b in itertools.combinations(metric_names, 2):
        rho, p_value = exact_spearman(metrics[metric_a], metrics[metric_b])
        correlation_rows.append(
            {
                "metric_a": metric_a,
                "metric_b": metric_b,
                "spearman_rho": rho,
                "exact_two_sided_p": p_value,
                "n_targets": len(TARGETS),
                "n_permutations": math.factorial(len(TARGETS)),
            }
        )

    overlap = (
        data.groupby("bibcode")["target"]
        .nunique()
        .value_counts()
        .sort_index()
        .rename_axis("n_targets")
        .reset_index(name="unique_bibcodes")
    )
    annual = pd.DataFrame(annual_rows)
    report = {
        "schema": "openads-lifesearch-canonical-v1",
        "deterministic": True,
        "network_calls": False,
        "randomness": False,
        "synthetic_data": False,
        "raw_assignments": int(len(data)),
        "unique_bibcodes": int(data["bibcode"].nunique()),
        "multi_target_unique_bibcodes": int((data.groupby("bibcode")["target"].nunique() > 1).sum()),
        "multi_target_share": float((data.groupby("bibcode")["target"].nunique() > 1).mean()),
        "metadata_conflicts": int(len(conflicts)),
        "weight_rule": "1 / max(1, parsed_author_count)",
        "trajectory_model": "OLS log(1 + annual raw count) on year, 2000-2024",
        "citation_reference": "mean citations among unique retrieved bibcodes in the same publication year",
        "limitations": [
            "retrieval is an archived, asymmetric historical snapshot, not a census",
            "author strings do not identify persons or labour-time FTE",
            "the citation ratio controls publication year only, not field or document type",
            "six targets provide limited resolution for rank-correlation inference",
        ],
    }
    return {
        "target_metrics": metrics,
        "annual_counts": annual,
        "overlap_degree": overlap,
        "correlations_exact": pd.DataFrame(correlation_rows),
        "metadata_conflicts": conflicts,
        "report": report,
    }


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL)


def render_figures(metrics: pd.DataFrame, annual: pd.DataFrame, figure_dir: Path) -> None:
    figure_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.dpi": 180})

    rank_cols = [
        ("rank_raw_count", "Scale"),
        ("rank_reciprocal_authorship", "Authorship\ndiscount"),
        ("rank_recent_reciprocal", "Recent\ndiscount"),
        ("rank_loglinear_rate", "Trajectory"),
        ("rank_citation_ratio", "Citation\nratio"),
    ]
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    x = np.arange(len(rank_cols))
    for row in metrics.itertuples(index=False):
        ranks = [getattr(row, column) for column, _ in rank_cols]
        ax.plot(x, ranks, marker="o", linewidth=1.6, label=row.target)
    ax.set_xticks(x, [label for _, label in rank_cols])
    ax.set_yticks(range(1, 7))
    ax.set_ylim(6.4, 0.6)
    ax.set_ylabel("Rank (1 = highest)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.15))
    fig.tight_layout()
    fig.savefig(figure_dir / "rank_inversions.pdf", bbox_inches="tight")
    fig.savefig(figure_dir / "rank_inversions.png", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    for target in TARGETS:
        subset = annual[annual["target"] == target]
        ax.plot(subset["year"], subset["raw_count"], linewidth=1.6, label=target)
    ax.set_yscale("symlog", linthresh=1)
    ax.set_xlabel("Publication year")
    ax.set_ylabel("Archived target-paper assignments (symlog)")
    ax.grid(alpha=0.25)
    ax.legend(ncol=3, frameon=False)
    fig.tight_layout()
    fig.savefig(figure_dir / "annual_trajectories.pdf", bbox_inches="tight")
    fig.savefig(figure_dir / "annual_trajectories.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True, help="Directory containing the six *_ads_raw.csv files")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--figure-dir", type=Path)
    parser.add_argument("--strict-expected", action="store_true")
    args = parser.parse_args()

    data, manifest = load_snapshot(args.data_dir, strict_expected=args.strict_expected)
    results = compute_results(data)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name in ("target_metrics", "annual_counts", "overlap_degree", "correlations_exact", "metadata_conflicts"):
        write_csv(args.output_dir / f"{name}.csv", results[name])
    (args.output_dir / "snapshot_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (args.output_dir / "reanalysis_report.json").write_text(
        json.dumps(results["report"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if args.figure_dir:
        render_figures(results["target_metrics"], results["annual_counts"], args.figure_dir)
    print(json.dumps(results["report"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
