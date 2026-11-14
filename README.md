# OpenADS LifeSearch

OpenADS LifeSearch hosts the reproducibility materials for P02 v4.5, a
retrospective study of planetary habitability evidence and research attention
across Enceladus, Europa, Ganymede, Mars, Titan and Venus.

The canonical result is deliberately narrow: **raw scale, team-size discount,
recent activity, fitted trajectory, and internally year-normalized citation
reception are different constructs and produce different target orderings.**

## Frozen-corpus result

The author-held snapshot contains 10,317 target-paper assignments and 9,513
unique bibcodes. A paper may belong to more than one target. The public
repository does not redistribute record-level ADS exports; it publishes their
hashes, deterministic code, aggregate outputs, verification tests and
provenance.

| Construct | Highest-ranked target | Interpretation boundary |
|---|---|---|
| Raw assignments | Mars | Archived scale, not merit or habitability |
| Reciprocal-authorship count | Mars | Team-size discount, not fractional author credit or FTE |
| Recent reciprocal count, 2019-2024 | Mars | Six-year archived activity window |
| Log-linear trajectory, 2000-2024 | Enceladus | Historical fitted trajectory, not forecast |
| Corpus-year citation ratio | Venus | Internal age control, not field-normalized MNCS |

Raw scale and reciprocal-authorship weighting give the same rank order
(exact Spearman rho = 1, two-sided p = 2/720). Raw scale and the internal
citation ratio are inversely ordered (rho = -0.829, exact p = 42/720 =
0.0583). With only six targets, effect direction and magnitude are reported
without binary significance rhetoric.

## Research package

- [P02 methods, data access and replay](research/p02/README.md)
- [Epistemic graph](research/p02/companion/epistemic_graph.html) and
  [Supergraph](research/p02/companion/supergraph.html). Download both HTML
  files into the same directory and open either one locally.
- [Contrast estimates and simultaneous intervals](research/p02/results/joint_trend_contrasts.csv)
- [Affiliation and agency findings for Enceladus](research/p02/provenance/ENCELADUS_AFFILIATIONS.md)
- [Claim ledger](research/p02/provenance/claim_ledger.csv)
- [Software citation](CITATION.cff)

The 2000-2023 complete-year study uses 9,762 assignments and 9,021 unique
papers. Sixteen pair-window-estimator directions receive joint support under
two paper-resampling schemes. The eight descriptive reversals do not receive
joint support in both directions. The archive misses two independently
identified studies in a purposive panel of 15; these cases document specific
omissions and do not supply a recall estimate.

## Repository map

- `research/p02/` - complete non-manuscript P02 v4.5 research package.
- `src/openads_reanalysis.py` - deterministic record-level canonical replay.
- `src/acquire_ads_snapshot.py` - authenticated acquisition of a new,
  time-dependent snapshot under the historical query grammar.
- `results/canonical/` - aggregate outputs, exact correlations and receipts.
- `figures/` - regenerated PDF and PNG canonical figures.
- `tests/` - public aggregate checks and optional full record-level replay.
- `docs/` - scientific audit, claim adjudication and data-governance boundary.
- `archive/legacy_cli/` - original prototypes retained for provenance only.

## Reproduce with the authorized frozen snapshot

Place the six exact CSV files in a private directory and run:

```bash
python src/openads_reanalysis.py \
  --data-dir /private/path/to/raw \
  --output-dir results/canonical \
  --figure-dir figures \
  --strict-expected
```

The command performs no network calls and uses no randomness, simulated
labels, imputation or synthetic observations.

Run public checks:

```bash
python -m pytest -q
```

Run the full replay when the author-held snapshot is available:

```bash
OPENADS_TEST_DATA=/private/path/to/raw python -m pytest -q
```

## Acquire a new snapshot

```bash
export ADS_API_TOKEN="..."
python src/acquire_ads_snapshot.py --output-dir /private/path/to/new_snapshot
```

Never commit credentials or record-level exports. A new retrieval reflects the
current ADS index and is not byte-identical to the frozen 2026 snapshot.

## Scientific and release boundaries

The release does **not** identify researcher FTE, productivity per worker,
mission value, probability of life, biologically available power, detection
probability, budget efficiency or a field-normalized MNCS. Historical claims
of that kind are classified in the claim ledger rather than silently retained.

The manuscript and supplementary material are intentionally not stored in
this public repository. They are maintained as separate author deliverables.

Code is released under GPL-3.0-or-later. Third-party bibliographic metadata is
governed by its source terms. This research made use of NASA's Astrophysics
Data System Bibliographic Services.
