#!/usr/bin/env python3
"""Record-level reconstruction of P02: attention landscapes in astrobiology.

The pipeline is deliberately deterministic, uses only the archived ADS CSV files,
and keeps distinct constructs separate.  It does not estimate labour, mission
value, habitability, or probability of biosignature detection.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import itertools
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.family": "DejaVu Sans"})


TARGETS = ["Enceladus", "Europa", "Mars", "Titan", "Venus", "Ganymede"]
ARCHIVE_BLOCK_ORDER = ["Enceladus", "Europa", "Ganymede", "Mars", "Titan", "Venus"]
ARCHIVE_YEAR_END = 2024
COMPLETE_YEAR_END = 2023
YEARS_ARCHIVE = np.arange(2000, ARCHIVE_YEAR_END + 1)
COMPLETE_WINDOWS = [
    (2000, COMPLETE_YEAR_END, "2000_2023"),
    (2010, COMPLETE_YEAR_END, "2010_2023"),
    (2019, COMPLETE_YEAR_END, "2019_2023"),
]
LEGACY_WINDOWS = [
    (2000, ARCHIVE_YEAR_END, "2000_2024"),
    (2010, ARCHIVE_YEAR_END, "2010_2024"),
    (2019, ARCHIVE_YEAR_END, "2019_2024"),
]
GAIA_ENCELADUS = {
    "2019NatAs...3..932G", "2020MmSAI..91..153C", "2021MNRAS.500.1385H",
    "2022arXiv220409057N", "2022ApJ...934...14H", "2022AJ....164...61M",
    "2024MNRAS.530.2648C",
}

GALACTIC_ENCELADUS_TERMS = re.compile(
    r"\b(?:gaia[- ]enceladus|gaia sausage|milky way|galax(?:y|ies)|galactic|"
    r"stellar ages?|stellar abundances?|population ii|halo stars?|dark matter halo|chemodynamical|"
    r"stellar halo|milky way halo|"
    r"halo merger|accreted halo|galactic archaeology|dwarf galaxy merger|"
    r"globular clusters?|stellar populations?|stellar kinematics|metallicity distribution)\b",
    re.I,
)
PLANETARY_ENCELADUS_TERMS = re.compile(
    r"\b(?:saturn|icy moon|ocean world|plume|cryovolcan|south polar|cassini|"
    r"hydrothermal|subsurface ocean|tiger stripe|astrobiolog|habitabil|biosignature)\b",
    re.I,
)

COUNTRY_PATTERNS = [
    ("USA", r"\b(?:USA|U\.S\.A\.?|United States(?: of America)?)\b"),
    ("GBR", r"\b(?:UK|U\.K\.?|United Kingdom|England|Scotland|Wales|Northern Ireland)\b"),
    ("FRA", r"\bFrance\b"), ("DEU", r"\bGermany\b"),
    ("ITA", r"\bItaly\b"), ("ESP", r"\bSpain\b"),
    ("CHN", r"\b(?:P\.?R\.? China|PR China|People'?s Republic of China|China)\b"),
    ("JPN", r"\bJapan\b"), ("CAN", r"\bCanada\b"),
    ("RUS", r"\b(?:Russia|Russian Federation)\b"),
    ("BEL", r"\bBelgium\b"), ("SWE", r"\bSweden\b"),
    ("CHE", r"\bSwitzerland\b"),
    ("NLD", r"\b(?:The Netherlands|the Netherlands|Netherlands|Holland)\b"),
    ("AUT", r"\bAustria\b"), ("AUS", r"\bAustralia\b"),
    ("IND", r"\bIndia\b"), ("BRA", r"\bBrazil\b"),
    ("CZE", r"\bCzech(?:ia| Republic)\b"),
    ("MEX", r"(?<!New )\b(?:Mexico|México)\b"), ("DNK", r"\bDenmark\b"),
    ("HUN", r"\bHungary\b"), ("POL", r"\bPoland\b"),
    ("PRT", r"\bPortugal\b"), ("CHL", r"\bChile\b"),
    ("GRC", r"\bGreece\b"), ("FIN", r"\bFinland\b"),
    ("UKR", r"\bUkraine\b"), ("NOR", r"\bNorway\b"),
    ("ARG", r"\bArgentina\b"), ("TWN", r"\bTaiwan\b"),
    ("ISR", r"\bIsrael\b"), ("IRN", r"\bIran\b"),
    ("NZL", r"\bNew Zealand\b"),
    ("KOR", r"\b(?:Republic of Korea|South Korea|Korea,? Republic)\b"),
    ("ZAF", r"\bSouth Africa\b"), ("ROU", r"\bRomania\b"),
    ("TUR", r"\b(?:Turkey|Türkiye)\b"), ("IRL", r"\bIreland\b"),
    ("BGR", r"\bBulgaria\b"), ("VEN", r"\bVenezuela\b"),
    ("SVK", r"\bSlovakia\b"), ("SVN", r"\bSlovenia\b"),
    ("HRV", r"\bCroatia\b"), ("SRB", r"\bSerbia\b"),
    ("EST", r"\bEstonia\b"), ("LVA", r"\bLatvia\b"),
    ("LTU", r"\bLithuania\b"), ("ISL", r"\bIceland\b"),
    ("LUX", r"\bLuxembourg\b"), ("COL", r"\bColombia\b"),
    ("PER", r"\bPeru\b"), ("URY", r"\bUruguay\b"),
    ("ECU", r"\bEcuador\b"), ("BOL", r"\bBolivia\b"),
    ("EGY", r"\bEgypt\b"), ("MAR", r"\bMorocco\b"),
    ("DZA", r"\bAlgeria\b"), ("TUN", r"\bTunisia\b"),
    ("SAU", r"\bSaudi Arabia\b"), ("ARE", r"\bUnited Arab Emirates|\bUAE\b"),
    ("QAT", r"\bQatar\b"), ("PAK", r"\bPakistan\b"),
    ("BGD", r"\bBangladesh\b"), ("MYS", r"\bMalaysia\b"),
    ("SGP", r"\bSingapore\b"), ("IDN", r"\bIndonesia\b"),
    ("THA", r"\bThailand\b"), ("VNM", r"\bVietnam\b"),
    ("PHL", r"\bPhilippines\b"), ("KAZ", r"\bKazakhstan\b"),
    ("ARM", r"\bArmenia\b"),
]

AGENCY_PATTERNS = [
    ("NASA", r"\bNASA\b|National Aeronautics and Space Administration|Jet Propulsion Laboratory|\bJPL\b"),
    ("ESA", r"European Space Agency|\bESA(?:/ESTEC)?\b|\bESTEC\b"),
    ("ASI", r"Italian Space Agency|Agenzia Spaziale Italiana|\bASI\b"),
    ("JAXA", r"Japan Aerospace Exploration Agency|\bJAXA\b|\bISAS\b"),
    ("CNES", r"Centre National d['’]Etudes Spatiales|\bCNES\b"),
    ("DLR", r"German Aerospace Center|Deutsches Zentrum für Luft- und Raumfahrt|\bDLR\b"),
    ("CNSA", r"China National Space Administration|\bCNSA\b"),
    ("ISRO", r"Indian Space Research Organi[sz]ation|\bISRO\b"),
    ("UAESA", r"UAE Space Agency|United Arab Emirates Space Agency"),
    ("ROSCOSMOS", r"\bRoscosmos\b|Russian Federal Space Agency"),
    ("RAS_SPACE", r"Space Research Institute.*Russian Academy of Sciences|Institute for Biomedical Problems.*Russian Academy of Sciences|\bIKI(?:/RAS)?\b"),
    ("CAS", r"Chinese Academy of Sciences"),
    ("CAST", r"China Academy of Space Technology"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def parse_array(value) -> list:
    if pd.isna(value) or value == "":
        return []
    out = json.loads(value)
    if not isinstance(out, list):
        raise ValueError("JSON field is not an array")
    return out


def rank_desc(values: pd.Series) -> pd.Series:
    return values.rank(method="min", ascending=False).astype(int)


def annual_slope(years: np.ndarray, values: np.ndarray, robust: bool = False) -> float:
    z = np.log1p(values.astype(float))
    if robust:
        slope = stats.theilslopes(z, years).slope
    else:
        slope = np.polyfit(years, z, 1)[0]
    return float(np.expm1(slope))


def clean_affiliation(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def countries_in_affiliation(s: str) -> tuple[str, ...]:
    s = clean_affiliation(s)
    if not s or s == "-":
        return ()
    found = [code for code, pat in COUNTRY_PATTERNS if re.search(pat, s, re.I)]
    return tuple(dict.fromkeys(found))


def agencies_in_affiliation(s: str) -> tuple[str, ...]:
    s = clean_affiliation(s)
    if not s or s == "-":
        return ()
    found = [name for name, pat in AGENCY_PATTERNS if re.search(pat, s, re.I)]
    return tuple(dict.fromkeys(found))


def load_and_validate(raw_dir: Path) -> tuple[pd.DataFrame, dict]:
    expected_cols = ["bibcode", "title", "author", "aff", "pubdate", "citation_count", "keyword", "doctype", "orcid_pub"]
    frames, hashes, counts = [], {}, {}
    for target in ARCHIVE_BLOCK_ORDER:
        p = raw_dir / f"{target}_ads_raw.csv"
        x = pd.read_csv(p)
        if list(x.columns) != expected_cols:
            raise ValueError(f"Unexpected schema in {p.name}: {list(x.columns)}")
        if x.bibcode.duplicated().any():
            raise ValueError(f"Duplicate bibcode within {target}")
        x["target"] = target
        frames.append(x)
        hashes[p.name] = sha256(p)
        counts[target] = len(x)
    rebuilt = pd.concat(frames, ignore_index=True)
    concat_path = raw_dir / "all_papers_raw_concat.csv"
    archived = pd.read_csv(concat_path)
    hashes[concat_path.name] = sha256(concat_path)
    if list(archived.columns) != expected_cols + ["target"]:
        raise ValueError("Unexpected consolidated schema")
    if not rebuilt.equals(archived):
        raise ValueError("Consolidated CSV is not the exact target-file concatenation")

    for c in ["author", "aff", "keyword", "orcid_pub"]:
        archived[c + "_list"] = archived[c].map(parse_array)
    mismatch = archived.apply(lambda r: len(r.author_list) != len(r.aff_list), axis=1)
    if mismatch.any():
        raise ValueError("Author and affiliation arrays are misaligned")
    archived["year"] = archived.pubdate.astype(str).str[:4].astype(int)
    archived["citation_count"] = pd.to_numeric(archived.citation_count, errors="raise").astype(float)
    archived["n_authors"] = archived.author_list.map(len)
    archived["missing_authors"] = archived.n_authors.eq(0)
    archived["title_l"] = archived.title.fillna("").str.lower()
    archived["keywords_l"] = archived.keyword_list.map(lambda a: " | ".join(map(str, a)).lower())

    meta_cols = ["title", "author", "aff", "pubdate", "citation_count", "keyword", "doctype", "orcid_pub"]
    conflicts = {}
    for col in meta_cols:
        nuniq = archived.groupby("bibcode")[col].nunique(dropna=False)
        conflicts[col] = int((nuniq > 1).sum())
    if any(conflicts.values()):
        raise ValueError(f"Conflicting metadata across targets: {conflicts}")

    degree = archived.groupby("bibcode").target.nunique().value_counts().sort_index()
    qc = {
        "hashes_sha256": hashes,
        "target_assignment_counts": counts,
        "n_assignments": int(len(archived)),
        "n_unique_bibcodes": int(archived.bibcode.nunique()),
        "duplicate_excess": int(len(archived) - archived.bibcode.nunique()),
        "overlap_degree": {str(int(k)): int(v) for k, v in degree.items()},
        "metadata_conflicts": conflicts,
        "missing_author_assignments": int(archived.missing_authors.sum()),
        "year_min": int(archived.year.min()),
        "year_max": int(archived.year.max()),
    }
    return archived, qc


def retrieval_mask(df: pd.DataFrame, mode: str) -> pd.Series:
    if mode == "inclusive":
        return pd.Series(True, index=df.index)
    if mode == "curated_gaia":
        return ~((df.target == "Enceladus") & df.bibcode.isin(GAIA_ENCELADUS))
    if mode == "strict_text":
        return df.apply(lambda r: r.target.lower() in r.title_l or r.target.lower() in r.keywords_l, axis=1)
    raise ValueError(mode)


def team_weights(x: pd.DataFrame, mode: str) -> pd.Series:
    if mode == "unit":
        return pd.Series(1.0, index=x.index)
    if mode == "reciprocal_legacy":
        return 1.0 / x.n_authors.clip(lower=1)
    if mode == "reciprocal_exclude_missing":
        w = 1.0 / x.n_authors.replace(0, np.nan)
        return w.fillna(0.0)
    if mode == "reciprocal_impute":
        med_ty = x.loc[x.n_authors > 0].groupby(["target", "year"]).n_authors.median()
        med_t = x.loc[x.n_authors > 0].groupby("target").n_authors.median()
        vals = []
        for r in x.itertuples():
            n = r.n_authors
            if n == 0:
                n = med_ty.get((r.target, r.year), med_t.get(r.target, 1.0))
            vals.append(1.0 / max(float(n), 1.0))
        return pd.Series(vals, index=x.index)
    raise ValueError(mode)


def add_analysis_weights(x: pd.DataFrame, attribution: str, team_mode: str) -> pd.DataFrame:
    x = x.copy()
    if attribution == "full":
        aw = pd.Series(1.0, index=x.index)
    elif attribution == "target_split":
        k = x.groupby("bibcode").target.transform("nunique")
        aw = 1.0 / k
    else:
        raise ValueError(attribution)
    x["weight"] = aw * team_weights(x, team_mode)
    return x


def citation_reference(x: pd.DataFrame) -> pd.DataFrame:
    u = x.sort_values("bibcode").drop_duplicates("bibcode")[["bibcode", "year", "citation_count"]].copy()
    u["year_mean"] = u.groupby("year").citation_count.transform("mean")
    u["citation_ratio"] = np.where(u.year_mean > 0, u.citation_count / u.year_mean, np.nan)
    u["citation_percentile"] = u.groupby("year").citation_count.rank(method="average", pct=True)
    u["top10"] = (u.citation_percentile >= 0.90).astype(float)
    return u


def compute_metrics(x: pd.DataFrame, year_start: int, year_end: int) -> pd.DataFrame:
    x = x[(x.year >= year_start) & (x.year <= year_end)].copy()
    ref = citation_reference(x)
    x = x.merge(ref[["bibcode", "citation_ratio", "citation_percentile", "top10"]], on="bibcode", how="left")
    unique = x.sort_values("bibcode").drop_duplicates("bibcode")[["bibcode", "year", "citation_count"]]
    rows = []
    years = np.arange(year_start, year_end + 1)
    for target in TARGETS:
        z = x[x.target == target].copy()
        target_bibcodes = set(z.bibcode)
        external = unique[~unique.bibcode.isin(target_bibcodes)].copy()
        external_mean = external.groupby("year").citation_count.mean()
        z["citation_ratio_loo"] = np.where(
            z.year.map(external_mean).gt(0),
            z.citation_count / z.year.map(external_mean),
            np.nan,
        )
        w = z.weight.to_numpy(float)
        denom = w.sum()
        annual = z.groupby("year").weight.sum().reindex(years, fill_value=0).to_numpy()
        def wmean(col):
            a = z[col].to_numpy(float)
            ok = np.isfinite(a) & np.isfinite(w)
            return float(np.average(a[ok], weights=w[ok])) if ok.any() and w[ok].sum() > 0 else np.nan
        rows.append({
            "target": target,
            "scale": float(denom),
            "trend_ols": annual_slope(years, annual, False),
            "trend_theilsen": annual_slope(years, annual, True),
            "citation_ratio": wmean("citation_ratio"),
            "citation_ratio_loo": wmean("citation_ratio_loo"),
            "citation_percentile": wmean("citation_percentile"),
            "top10_share": wmean("top10"),
            "n_assignments": int(len(z)),
            "n_unique_papers": int(z.bibcode.nunique()),
        })
    return pd.DataFrame(rows)


def specification_multiverse(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    retrievals = ["inclusive", "curated_gaia", "strict_text"]
    attributions = ["full", "target_split"]
    teams = ["unit", "reciprocal_legacy", "reciprocal_exclude_missing", "reciprocal_impute"]
    windows = COMPLETE_WINDOWS
    metric_cols = ["scale", "trend_ols", "trend_theilsen", "citation_ratio", "citation_ratio_loo",
                   "citation_percentile", "top10_share"]
    out = []
    spec_id = 0
    for ret, att, team, (ys, ye, win) in itertools.product(retrievals, attributions, teams, windows):
        base = df[retrieval_mask(df, ret)]
        weighted = add_analysis_weights(base, att, team)
        metrics = compute_metrics(weighted, ys, ye)
        for metric in metric_cols:
            ranks = rank_desc(metrics.set_index("target")[metric])
            for r in metrics.itertuples():
                out.append({"spec_id": spec_id, "retrieval": ret, "attribution": att,
                            "team_rule": team, "window": win, "metric": metric,
                            "target": r.target, "value": getattr(r, metric),
                            "rank": int(ranks[r.target])})
        spec_id += 1
    long = pd.DataFrame(out)
    rank_freq = (long.groupby(["metric", "target", "rank"]).size().rename("n")
                 .reset_index())
    rank_freq["share"] = rank_freq.n / rank_freq.groupby(["metric", "target"]).n.transform("sum")
    pairs = []
    for metric, g in long.groupby("metric"):
        wide = g.pivot(index="spec_id", columns="target", values="value")
        for a, b in itertools.combinations(TARGETS, 2):
            pairs.append({"metric": metric, "target_a": a, "target_b": b,
                          "p_a_gt_b": float((wide[a] > wide[b]).mean()),
                          "p_tie": float(np.isclose(wide[a], wide[b]).mean()),
                          "n_specifications": int(len(wide))})
    return long, rank_freq, pd.DataFrame(pairs)


def canonical_outputs(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    x = add_analysis_weights(df, "full", "unit")
    metrics = compute_metrics(x, 2000, COMPLETE_YEAR_END)
    for col in ["scale", "trend_ols", "trend_theilsen", "citation_ratio", "citation_ratio_loo",
                "citation_percentile", "top10_share"]:
        metrics["rank_" + col] = rank_desc(metrics.set_index("target")[col]).reindex(metrics.target).to_numpy()
    annual = (df.groupby(["target", "year"]).size().rename("assignments").reset_index()
              .set_index(["target", "year"]).reindex(pd.MultiIndex.from_product([TARGETS, YEARS_ARCHIVE], names=["target", "year"]), fill_value=0).reset_index())
    return metrics, annual


def exact_metric_correlations(canonical: pd.DataFrame) -> pd.DataFrame:
    cols = ["scale", "trend_ols", "trend_theilsen", "citation_ratio", "citation_ratio_loo",
            "citation_percentile", "top10_share"]
    rows = []
    for a, b in itertools.combinations(cols, 2):
        x = canonical.set_index("target").loc[TARGETS, a].to_numpy()
        y = canonical.set_index("target").loc[TARGETS, b].to_numpy()
        rho = float(stats.spearmanr(x, y).statistic)
        perm = [float(stats.spearmanr(x, y[list(ix)]).statistic) for ix in itertools.permutations(range(len(y)))]
        p = float(np.mean(np.abs(perm) >= abs(rho) - 1e-12))
        rows.append({"metric_a": a, "metric_b": b, "spearman_rho": rho,
                     "exact_two_sided_p": p, "n_targets": len(TARGETS), "n_permutations": math.factorial(len(TARGETS))})
    return pd.DataFrame(rows)


def rank_stability(specs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (metric, target), g in specs.groupby(["metric", "target"]):
        mode = g["rank"].mode().min()
        rows.append({"metric": metric, "target": target, "min_rank": int(g["rank"].min()),
                     "max_rank": int(g["rank"].max()), "modal_rank": int(mode),
                     "modal_share": float((g["rank"] == mode).mean()),
                     "rank1_share": float((g["rank"] == 1).mean()),
                     "n_specifications": int(len(g))})
    return pd.DataFrame(rows)


def pareto_frontier(canonical: pd.DataFrame, inst: pd.DataFrame) -> pd.DataFrame:
    x = canonical.merge(inst[inst.window == "2000_2023"][["target", "country_D1"]], on="target")
    axes = ["scale", "trend_ols", "citation_percentile", "country_D1"]
    vals = x.set_index("target")[axes]
    rows = []
    for target in TARGETS:
        dominators = []
        for other in TARGETS:
            if other == target: continue
            if (vals.loc[other] >= vals.loc[target]).all() and (vals.loc[other] > vals.loc[target]).any():
                dominators.append(other)
        rows.append({"target": target, "pareto_nondominated": not dominators,
                     "dominated_by": "|".join(dominators), **{a: vals.loc[target, a] for a in axes}})
    return pd.DataFrame(rows)


def pareto_null_reference(n_points: int = 6, n_axes: int = 4, n_mc: int = 200_000,
                          seed: int = 20260825) -> pd.DataFrame:
    expected = sum(
        ((-1) ** (k + 1)) * math.comb(n_points, k) / (k ** (n_axes - 1))
        for k in range(1, n_points + 1)
    )
    rng = np.random.default_rng(seed)
    n_all = 0
    processed = 0
    batch_size = 20_000
    while processed < n_mc:
        batch = min(batch_size, n_mc - processed)
        values = rng.random((batch, n_points, n_axes))
        dominates = (values[:, :, None, :] >= values[:, None, :, :]).all(axis=3)
        diagonal = np.arange(n_points)
        dominates[:, diagonal, diagonal] = False
        dominated = dominates.any(axis=1)
        n_all += int((~dominated).all(axis=1).sum())
        processed += batch
    p_all = n_all / n_mc
    se = math.sqrt(p_all * (1 - p_all) / n_mc)
    return pd.DataFrame([{
        "n_points": n_points,
        "n_axes": n_axes,
        "expected_nondominated_exact_iid_continuous": expected,
        "mc_repetitions": n_mc,
        "p_all_nondominated_mc": p_all,
        "mc_standard_error": se,
        "seed": seed,
        "null_model": "independent continuous ranks on all axes",
    }])


def bootstrap_canonical(df: pd.DataFrame, n_boot: int, seed: int,
                        year_start: int = 2000, year_end: int = COMPLETE_YEAR_END
                        ) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df[(df.year >= year_start) & (df.year <= year_end)].copy()
    unique = df.sort_values("bibcode").drop_duplicates("bibcode")[["bibcode", "year", "citation_count"]].reset_index(drop=True)
    bidx = {b: i for i, b in enumerate(unique.bibcode)}
    tidx = {t: i for i, t in enumerate(TARGETS)}
    a_b = df.bibcode.map(bidx).to_numpy()
    a_t = df.target.map(tidx).to_numpy()
    years = unique.year.to_numpy()
    cites = unique.citation_count.to_numpy(float)
    analysis_years = np.arange(year_start, year_end + 1)
    membership = np.zeros((len(unique), len(TARGETS)), dtype=bool)
    membership[a_b, a_t] = True
    rng = np.random.default_rng(seed)
    records = []
    metric_names = ["scale", "trend_ols", "trend_theilsen", "citation_ratio", "citation_ratio_loo"]
    ranks_store = {m: [] for m in metric_names}
    for b in range(n_boot):
        mult = rng.multinomial(len(unique), np.repeat(1 / len(unique), len(unique))).astype(float)
        aw = mult[a_b]
        scale = np.bincount(a_t, weights=aw, minlength=len(TARGETS))
        annual = np.zeros((len(TARGETS), len(analysis_years)))
        for yi, year in enumerate(analysis_years):
            sel = years[a_b] == year
            annual[:, yi] = np.bincount(a_t[sel], weights=aw[sel], minlength=len(TARGETS))
        trend = np.array([annual_slope(analysis_years, annual[j], False) for j in range(len(TARGETS))])
        trend_theilsen = np.array([annual_slope(analysis_years, annual[j], True) for j in range(len(TARGETS))])
        year_mean = {}
        for year in analysis_years:
            sel = years == year
            den = mult[sel].sum()
            year_mean[year] = np.average(cites[sel], weights=mult[sel]) if den > 0 else np.nan
        ratio_u = np.array([c / year_mean[y] if year_mean[y] and np.isfinite(year_mean[y]) else np.nan for c, y in zip(cites, years)])
        ratio_a = ratio_u[a_b]
        citation = np.array([np.average(ratio_a[a_t == j], weights=aw[a_t == j]) if aw[a_t == j].sum() else np.nan for j in range(len(TARGETS))])
        citation_loo = np.full(len(TARGETS), np.nan)
        for j in range(len(TARGETS)):
            external_mean = {}
            for year in analysis_years:
                sel = (years == year) & ~membership[:, j]
                den = mult[sel].sum()
                external_mean[year] = np.average(cites[sel], weights=mult[sel]) if den > 0 else np.nan
            sel_assign = a_t == j
            ratios = np.array([
                cites[bi] / external_mean[years[bi]]
                if external_mean[years[bi]] and np.isfinite(external_mean[years[bi]]) else np.nan
                for bi in a_b[sel_assign]
            ])
            wj = aw[sel_assign]
            ok = np.isfinite(ratios) & np.isfinite(wj)
            if ok.any() and wj[ok].sum() > 0:
                citation_loo[j] = np.average(ratios[ok], weights=wj[ok])
        vals = {"scale": scale, "trend_ols": trend, "trend_theilsen": trend_theilsen,
                "citation_ratio": citation, "citation_ratio_loo": citation_loo}
        for metric, arr in vals.items():
            ranks = stats.rankdata(-arr, method="min")
            ranks_store[metric].append(ranks)
            for j, target in enumerate(TARGETS):
                records.append({"bootstrap": b, "metric": metric, "target": target, "value": arr[j], "rank": int(ranks[j])})
    boot = pd.DataFrame(records)
    summary = (boot.groupby(["metric", "target"]).value.agg(
        median="median", lo=lambda s: s.quantile(.025), hi=lambda s: s.quantile(.975)).reset_index())
    pair_rows = []
    for metric, rank_list in ranks_store.items():
        g = boot[boot.metric == metric].pivot(index="bootstrap", columns="target", values="value")
        for a, b in itertools.combinations(TARGETS, 2):
            pair_rows.append({"metric": metric, "target_a": a, "target_b": b,
                              "p_a_gt_b": float((g[a] > g[b]).mean()),
                              "n_bootstrap": n_boot})
    return summary, pd.DataFrame(pair_rows)


def institutional_outputs(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    paper_aff = df.sort_values("bibcode").drop_duplicates("bibcode")[["bibcode", "year", "aff_list"]].copy()
    paper_country, paper_agency, authorship_rows = {}, {}, []
    for r in paper_aff.itertuples():
        countries, agencies = set(), set()
        for aff in r.aff_list:
            cs = countries_in_affiliation(aff)
            ag = agencies_in_affiliation(aff)
            countries.update(cs); agencies.update(ag)
            authorship_rows.append({"bibcode": r.bibcode, "year": r.year, "affiliation": clean_affiliation(aff),
                                    "countries": "|".join(cs), "agencies": "|".join(ag),
                                    "is_missing": aff == "-", "is_country_mapped": bool(cs)})
        paper_country[r.bibcode] = tuple(sorted(countries))
        paper_agency[r.bibcode] = tuple(sorted(agencies))
    auth = pd.DataFrame(authorship_rows)
    nonmissing = auth[~auth.is_missing]
    coverage = pd.DataFrame([{
        "n_authorship_affiliations": int(len(auth)),
        "n_missing_affiliations": int(auth.is_missing.sum()),
        "n_nonmissing_affiliations": int(len(nonmissing)),
        "n_country_mapped_nonmissing": int(nonmissing.is_country_mapped.sum()),
        "country_mapping_coverage_nonmissing": float(nonmissing.is_country_mapped.mean()),
        "method": "high-specificity country-name matching; no city-only inference",
    }])

    assign = df[["bibcode", "target", "year"]].copy()
    assign["countries"] = assign.bibcode.map(paper_country)
    assign["agencies"] = assign.bibcode.map(paper_agency)
    summary_rows, share_rows, agency_rows, edge_rows = [], [], [], []
    for ys, ye, window in COMPLETE_WINDOWS:
        q = assign[(assign.year >= ys) & (assign.year <= ye)]
        for target in TARGETS:
            z = q[q.target == target]
            credit = Counter(); presence = Counter(); intl = 0; known = 0
            agency_presence = Counter(); edges = Counter()
            for r in z.itertuples():
                cs = r.countries
                if cs:
                    known += 1
                    for c in cs:
                        credit[c] += 1 / len(cs)
                        presence[c] += 1
                    if len(cs) >= 2:
                        intl += 1
                        mass = 2 / (len(cs) * (len(cs) - 1))
                        for a, b in itertools.combinations(cs, 2): edges[(a, b)] += mass
                for a in r.agencies: agency_presence[a] += 1
            vals = np.array(list(credit.values()), float)
            p = vals / vals.sum() if vals.sum() else np.array([])
            d0 = int(len(p)); d1 = float(np.exp(-(p * np.log(p)).sum())) if len(p) else np.nan
            hhi = float((p ** 2).sum()) if len(p) else np.nan
            d2 = float(1 / hhi) if hhi and np.isfinite(hhi) else np.nan
            summary_rows.append({"window": window, "target": target, "n_assignments": len(z),
                                 "n_with_mapped_country": known, "mapped_paper_share": known / len(z) if len(z) else np.nan,
                                 "international_share_among_mapped": intl / known if known else np.nan,
                                 "country_D0": d0, "country_D1": d1, "country_D2": d2, "HHI": hhi,
                                 "top1_share": max(p) if len(p) else np.nan})
            for c, v in credit.items():
                share_rows.append({"window": window, "target": target, "country": c,
                                   "paper_presence_count": presence[c],
                                   "fractional_paper_credit": v, "share": v / vals.sum()})
            for a, v in agency_presence.items():
                agency_rows.append({"window": window, "target": target, "agency_class": a, "paper_presence_count": v})
            for (a, b), v in edges.items():
                edge_rows.append({"window": window, "target": target, "country_a": a, "country_b": b, "normalized_edge_weight": v})
    return coverage, pd.DataFrame(summary_rows), pd.DataFrame(share_rows), pd.DataFrame(agency_rows), pd.DataFrame(edge_rows)


def year_month_coverage(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x["month"] = pd.to_numeric(x.pubdate.astype(str).str.slice(5, 7), errors="coerce").fillna(0).astype(int)
    rows = []
    for (target, year), g in x.groupby(["target", "year"]):
        known = g[g.month.between(1, 12)]
        rows.append({
            "target": target,
            "year": int(year),
            "n_assignments": int(len(g)),
            "n_known_month": int(len(known)),
            "n_unknown_month": int((g.month == 0).sum()),
            "first_known_month": int(known.month.min()) if len(known) else np.nan,
            "last_known_month": int(known.month.max()) if len(known) else np.nan,
            "has_november_record": bool((known.month == 11).any()),
            "has_december_record": bool((known.month == 12).any()),
        })
    return pd.DataFrame(rows)


def enceladus_retrieval_audit(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    x = df[df.target == "Enceladus"].copy()
    text = (x.title.fillna("") + " | " + x.keywords_l.fillna(""))
    x["target_in_title"] = x.title_l.str.contains(r"\benceladus\b", regex=True)
    x["target_in_keywords"] = x.keywords_l.str.contains(r"\benceladus\b", regex=True)
    x["strict_text_pass"] = x.target_in_title | x.target_in_keywords
    x["known_gaia_exclusion"] = x.bibcode.isin(GAIA_ENCELADUS)
    x["galactic_risk_terms"] = text.str.contains(GALACTIC_ENCELADUS_TERMS)
    x["planetary_context_terms"] = text.str.contains(PLANETARY_ENCELADUS_TERMS)
    x["screening_status"] = np.select(
        [
            x.known_gaia_exclusion,
            x.galactic_risk_terms & ~x.planetary_context_terms,
            x.strict_text_pass,
        ],
        [
            "EXCLUDE_KNOWN_GAIA_ENCELADUS",
            "REVIEW_GALACTIC_RISK",
            "LOWER_BOUND_INCLUDED",
        ],
        default="UNRESOLVED_FULLTEXT_ONLY",
    )
    cols = [
        "bibcode", "year", "pubdate", "title", "keyword", "target_in_title",
        "target_in_keywords", "strict_text_pass", "known_gaia_exclusion",
        "galactic_risk_terms", "planetary_context_terms", "screening_status",
    ]
    audit = x[cols].sort_values(["screening_status", "year", "bibcode"]).reset_index(drop=True)
    summary = (audit.groupby("screening_status").size().rename("n_records").reset_index())
    summary["share_of_enceladus_archive"] = summary.n_records / len(audit)
    summary["validation_level"] = "machine screen from archived title and keyword fields; not human/full-text validated"
    return audit, summary


def window_truncation_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    x = add_analysis_weights(df, "full", "unit")
    metrics = ["scale", "trend_ols", "trend_theilsen", "citation_ratio", "citation_ratio_loo",
               "citation_percentile", "top10_share"]
    rows = []
    for (ys, complete_end, complete_label), (_, archive_end, archive_label) in zip(COMPLETE_WINDOWS, LEGACY_WINDOWS):
        complete = compute_metrics(x, ys, complete_end).set_index("target")
        legacy = compute_metrics(x, ys, archive_end).set_index("target")
        for target in TARGETS:
            for metric in metrics:
                a = float(complete.loc[target, metric])
                b = float(legacy.loc[target, metric])
                rows.append({
                    "target": target,
                    "metric": metric,
                    "complete_window": complete_label,
                    "legacy_window": archive_label,
                    "complete_value": a,
                    "legacy_value_including_partial_2024": b,
                    "delta_legacy_minus_complete": b - a,
                })
    return pd.DataFrame(rows)


def pairwise_identification_status(pair_spec: pd.DataFrame, boot_pairs: pd.DataFrame) -> pd.DataFrame:
    x = pair_spec.merge(
        boot_pairs.rename(columns={"p_a_gt_b": "p_a_gt_b_bootstrap"}),
        on=["metric", "target_a", "target_b"],
        how="left",
    )
    statuses = []
    for r in x.itertuples():
        forward = np.isclose(r.p_a_gt_b, 1.0) and np.isclose(r.p_tie, 0.0)
        reverse = np.isclose(r.p_a_gt_b, 0.0) and np.isclose(r.p_tie, 0.0)
        has_boot = np.isfinite(r.p_a_gt_b_bootstrap)
        if forward and has_boot and r.p_a_gt_b_bootstrap >= 0.95:
            status = "ROBUST_INVARIANT_A_GT_B"
        elif reverse and has_boot and r.p_a_gt_b_bootstrap <= 0.05:
            status = "ROBUST_INVARIANT_B_GT_A"
        elif (forward or reverse) and has_boot:
            status = "SAMPLING_SENSITIVE"
        elif forward:
            status = "SPECIFICATION_INVARIANT_A_GT_B_NO_BOOTSTRAP"
        elif reverse:
            status = "SPECIFICATION_INVARIANT_B_GT_A_NO_BOOTSTRAP"
        else:
            status = "SPECIFICATION_SENSITIVE"
        statuses.append(status)
    x["identification_status"] = statuses
    return x


def canonical_table_latex(canonical: pd.DataFrame) -> str:
    rows = []
    for r in canonical.sort_values("rank_scale").itertuples():
        rows.append(
            f"{r.target} & {r.scale:.0f} & {r.rank_scale} & {100*r.trend_ols:.2f} & {r.rank_trend_ols} & "
            f"{r.citation_ratio:.3f} & {r.citation_ratio_loo:.3f} & {r.citation_percentile:.3f} & "
            f"{r.rank_citation_percentile} \\\\"
        )
    body = "\n".join(rows)
    return (
        "\\begin{table*}[t]\n\\centering\n\\small\n\\caption{Canonical complete-year estimates (2000--2023). "
        "The internal CYCR uses the pooled retrieved corpus; LOTO-CYCR uses a leave-one-target-out yearly reference.}\n"
        "\\label{tab:canonical}\n\\begin{tabular}{lrrrrrrrr}\n\\toprule\n"
        "Target & Scale & Rank & OLS (\\% yr$^{-1}$) & Rank & CYCR & LOTO-CYCR & Percentile & Rank \\\\\n"
        "\\midrule\n" + body + "\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n"
    )


def bootstrap_cycr_table_latex(summary: pd.DataFrame) -> str:
    x = summary[summary.metric == "citation_ratio"].copy()
    x["rank"] = rank_desc(x.set_index("target")["median"]).reindex(x.target).to_numpy()
    rows = [
        f"{r.target} & {r.median:.3f} & {r.lo:.3f} & {r.hi:.3f} & {r.rank} \\\\"
        for r in x.sort_values("rank").itertuples()
    ]
    return (
        "\\begin{table}[t]\n\\centering\n\\caption{Paper-cluster bootstrap intervals for canonical internal CYCR (2000--2023).}\n"
        "\\label{tab:bootstrap-cycr}\n\\begin{tabular}{lrrrr}\n\\toprule\n"
        "Target & Median & 2.5th percentile & 97.5th percentile & Rank \\\\\n\\midrule\n"
        + "\n".join(rows)
        + "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
    )


def canonical_full_table_latex(canonical: pd.DataFrame) -> str:
    rows = [
        f"{r.target} & {r.scale:.0f} & {r.trend_ols:.4f} & {r.trend_theilsen:.4f} & "
        f"{r.citation_ratio:.4f} & {r.citation_ratio_loo:.4f} & {r.citation_percentile:.4f} & "
        f"{r.top10_share:.4f} \\\\"
        for r in canonical.itertuples()
    ]
    return (
        "\\begin{table*}[t]\n\\centering\n\\small\n"
        "\\caption{Canonical complete-year values for all released indicators (2000--2023).}\n"
        "\\label{tab:canonical-full}\n\\begin{tabular}{lrrrrrrr}\n\\toprule\n"
        "Target & Scale & OLS $g$ & Theil--Sen $g$ & CYCR & LOTO-CYCR & Percentile & Top-10\\% \\\\\n"
        "\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n"
    )


def geography_table_latex(inst: pd.DataFrame) -> str:
    x = inst[inst.window == "2000_2023"].copy()
    rows = [
        f"{r.target} & {r.mapped_paper_share:.3f} & {r.international_share_among_mapped:.3f} & "
        f"{r.country_D0:d} & {r.country_D1:.2f} & {r.country_D2:.2f} & {r.HHI:.3f} \\\\"
        for r in x.itertuples()
    ]
    return (
        "\\begin{table}[t]\n\\centering\n\\small\n"
        "\\caption{Geographic structure, 2000--2023. International share is conditional on mapped paper geography.}\n"
        "\\label{tab:geography}\n\\begin{tabular}{lrrrrrr}\n\\toprule\n"
        "Target & Mapped share & International share & $D_0$ & $D_1$ & $D_2$ & HHI \\\\\n"
        "\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
    )


def make_figures(out: Path, canonical: pd.DataFrame, annual: pd.DataFrame,
                 specs: pd.DataFrame, inst: pd.DataFrame, shares: pd.DataFrame) -> None:
    figdir = out / "figures"; figdir.mkdir(parents=True, exist_ok=True)
    order = ["scale", "trend_ols", "trend_theilsen", "citation_ratio", "citation_ratio_loo",
             "citation_percentile", "top10_share"]
    rankmat = canonical.set_index("target")[["rank_" + c for c in order]].loc[TARGETS]
    fig, ax = plt.subplots(figsize=(8.4, 4.5))
    im = ax.imshow(rankmat, cmap="viridis_r", vmin=1, vmax=6, aspect="auto")
    ax.set_xticks(range(len(order)), ["Scale", "OLS trajectory", "Theil--Sen", "CYCR", "LOTO-CYCR",
                                          "Year percentile", "Top-10% share"], rotation=25, ha="right")
    ax.set_yticks(range(len(TARGETS)), TARGETS)
    for i in range(len(TARGETS)):
        for j in range(len(order)): ax.text(j, i, int(rankmat.iloc[i, j]), ha="center", va="center", color="white" if rankmat.iloc[i,j] > 3 else "black")
    fig.colorbar(im, ax=ax, label="Rank (1 = highest)")
    ax.set_title("Rank transitions across distinct constructs")
    fig.tight_layout(); fig.savefig(figdir / "fig1_rank_transitions.pdf"); fig.savefig(figdir / "fig1_rank_transitions.png", dpi=220); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    for t in TARGETS:
        z = annual[annual.target == t]
        ax.plot(z.year, z.assignments, label=t, linewidth=1.8)
    ax.axvspan(2023.5, 2024.5, color="0.8", alpha=0.45, zorder=0)
    ax.text(2024, 0.97, "partial", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=8)
    ax.set_yscale("symlog", linthresh=1); ax.set_xlabel("Publication year"); ax.set_ylabel("Target-paper assignments (symlog)")
    ax.set_title("Annual attention trajectories in the legacy retrieval snapshot"); ax.legend(ncol=3, frameon=False)
    fig.tight_layout(); fig.savefig(figdir / "fig2_annual_trajectories.pdf"); fig.savefig(figdir / "fig2_annual_trajectories.png", dpi=220); plt.close(fig)

    g = specs[specs.metric.isin(["scale", "trend_ols", "citation_ratio", "citation_percentile"])].copy()
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharey=True)
    for ax, metric in zip(axes.flat, ["scale", "trend_ols", "citation_ratio", "citation_percentile"]):
        vals = [g[(g.metric == metric) & (g.target == t)]["rank"].to_numpy() for t in TARGETS]
        ax.boxplot(vals, tick_labels=TARGETS, vert=False, whis=(0,100), showfliers=False)
        ax.invert_xaxis(); ax.set_xlim(6.3, .7); ax.set_title(metric.replace("_", " "))
    fig.suptitle("Ranks across 72 defensible specifications (ranges are descriptive)")
    fig.tight_layout(); fig.savefig(figdir / "fig3_specification_rank_ranges.pdf"); fig.savefig(figdir / "fig3_specification_rank_ranges.png", dpi=220); plt.close(fig)

    z = inst[inst.window == "2000_2023"].set_index("target").loc[TARGETS]
    c = canonical.set_index("target").loc[TARGETS]
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sizes = 45 + 18 * z.country_D1.fillna(0)
    ax.scatter(c.scale, c.citation_percentile, s=sizes, c=c.trend_ols, cmap="plasma", edgecolor="black")
    for t in TARGETS: ax.annotate(t, (c.loc[t,"scale"], c.loc[t,"citation_percentile"]), xytext=(5,4), textcoords="offset points")
    ax.set_xscale("log"); ax.set_xlabel("Publication assignments (log scale)"); ax.set_ylabel("Mean within-year citation percentile")
    ax.set_title("Attention landscape: scale, reception, trajectory and geographic breadth")
    fig.tight_layout(); fig.savefig(figdir / "fig4_attention_landscape.pdf"); fig.savefig(figdir / "fig4_attention_landscape.png", dpi=220); plt.close(fig)

    s = shares[shares.window == "2000_2023"]
    top = s.groupby("country").fractional_paper_credit.sum().nlargest(15).index
    mat = s[s.country.isin(top)].pivot(index="country", columns="target", values="share").fillna(0).reindex(columns=TARGETS)
    fig, ax = plt.subplots(figsize=(8.5, 6))
    im = ax.imshow(mat, cmap="magma", aspect="auto", vmin=0)
    ax.set_xticks(range(len(TARGETS)), TARGETS, rotation=25, ha="right"); ax.set_yticks(range(len(mat)), mat.index)
    fig.colorbar(im, ax=ax, label="Fractional country share within target")
    ax.set_title("Geographic composition of target literatures (mapped affiliations)")
    fig.tight_layout(); fig.savefig(figdir / "fig5_country_target_heatmap.pdf"); fig.savefig(figdir / "fig5_country_target_heatmap.png", dpi=220); plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--bootstrap", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20260825)
    args = ap.parse_args()
    out = args.out_dir; out.mkdir(parents=True, exist_ok=True)
    df, qc = load_and_validate(args.raw_dir)
    canonical, annual = canonical_outputs(df)
    specs, rank_freq, pair_spec = specification_multiverse(df)
    correlations = exact_metric_correlations(canonical)
    stability = rank_stability(specs)
    boot_summary, boot_pairs = bootstrap_canonical(df, args.bootstrap, args.seed)
    coverage, inst, shares, agencies, edges = institutional_outputs(df)
    pareto = pareto_frontier(canonical, inst)
    pareto_null = pareto_null_reference(seed=args.seed)
    identification = pairwise_identification_status(pair_spec, boot_pairs)
    month_coverage = year_month_coverage(df)
    retrieval_audit, retrieval_audit_summary = enceladus_retrieval_audit(df)
    truncation = window_truncation_sensitivity(df)

    qc.update({
        "archive_year_end": ARCHIVE_YEAR_END,
        "canonical_complete_year_end": COMPLETE_YEAR_END,
        "partial_year_policy": "2024 remains archived and is reported only as a truncation sensitivity; canonical inference ends in 2023",
        "enceladus_validation_level": "machine screen from archived title and keyword fields; not human/full-text validated",
        "known_gaia_enceladus_exclusions": len(GAIA_ENCELADUS),
    })

    overlap = (df.groupby("bibcode").target.nunique().value_counts().sort_index()
               .rename_axis("n_targets").rename("n_unique_bibcodes").reset_index())
    canonical.to_csv(out / "canonical_metrics.csv", index=False)
    annual.to_csv(out / "annual_assignments.csv", index=False)
    overlap.to_csv(out / "overlap_degree.csv", index=False)
    specs.to_csv(out / "specification_results.csv", index=False)
    rank_freq.to_csv(out / "rank_frequencies.csv", index=False)
    pair_spec.to_csv(out / "pairwise_specification_dominance.csv", index=False)
    correlations.to_csv(out / "canonical_metric_correlations_exact.csv", index=False)
    stability.to_csv(out / "rank_stability.csv", index=False)
    pareto.to_csv(out / "pareto_frontier.csv", index=False)
    pareto_null.to_csv(out / "pareto_null_reference.csv", index=False)
    boot_summary.to_csv(out / "bootstrap_intervals.csv", index=False)
    boot_pairs.to_csv(out / "bootstrap_pairwise_dominance.csv", index=False)
    identification.to_csv(out / "pairwise_identification_status.csv", index=False)
    month_coverage.to_csv(out / "year_month_coverage.csv", index=False)
    retrieval_audit.to_csv(out / "enceladus_retrieval_audit.csv", index=False)
    retrieval_audit_summary.to_csv(out / "enceladus_retrieval_audit_summary.csv", index=False)
    truncation.to_csv(out / "window_truncation_sensitivity.csv", index=False)
    coverage.to_csv(out / "affiliation_country_coverage.csv", index=False)
    inst.to_csv(out / "institutional_target_metrics.csv", index=False)
    shares.to_csv(out / "country_target_shares.csv", index=False)
    agencies.to_csv(out / "agency_affiliation_presence.csv", index=False)
    edges.to_csv(out / "country_collaboration_edges.csv", index=False)
    (out / "generated_canonical_table.tex").write_text(canonical_table_latex(canonical), encoding="utf-8")
    (out / "generated_canonical_full_table.tex").write_text(canonical_full_table_latex(canonical), encoding="utf-8")
    (out / "generated_bootstrap_cycr_table.tex").write_text(bootstrap_cycr_table_latex(boot_summary), encoding="utf-8")
    (out / "generated_geography_table.tex").write_text(geography_table_latex(inst), encoding="utf-8")
    (out / "qc_summary.json").write_text(json.dumps(qc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    make_figures(out, canonical, annual, specs, inst, shares)
    print(json.dumps({"status":"ok", "assignments":qc["n_assignments"], "unique":qc["n_unique_bibcodes"],
                      "specification_rows":len(specs), "bootstrap":args.bootstrap,
                      "country_mapping_coverage":float(coverage.iloc[0].country_mapping_coverage_nonmissing)}, indent=2))


if __name__ == "__main__":
    main()
