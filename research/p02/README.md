# P02 v4.5 reproducibility materials

This directory contains the analysis code, model specifications, derived
tables, figures, provenance, and the two offline graph interfaces. The
paper and supplement are distributed through the authors. The frozen
study window is 2000–2023. The 2024 slice is partial. Literature checks
extend through November 2026 and sit outside the historical counts.

## Verify the public results

Run the following commands from `research/p02` with Python 3.11 or later.

```sh
python3 analysis/verify_public.py
python3 analysis/build_companion.py
```

The public check verifies the SHA-256 manifest, reconstructs the joint
adjudications from the 4,320 contrast rows, checks the 36 precision-sampling
strata, and verifies the graph model and both offline HTML files. The graph
builder uses the archived derived results. For interactive QA, install
Linkedom 0.18.15 and run `node analysis/check_atlas.cjs`.

## Replay against the frozen archive

The [ADS/SciX terms](https://ui.adsabs.harvard.edu/help/terms/) restrict
redistribution of API data. The seven source CSVs (six exports and their
concatenation), row-level ADS audit files, and precision-coding identities
are held in the author archive. The [input hashes](source/input_sha256.json)
and the [original author-pack manifest](provenance/P02_V45_AUTHOR_MANIFEST.sha256)
identify those exact inputs. The Crossref frame is provided with abstracts
omitted from the source deposits. It includes 374 unclassified candidates
and provides no validated eligibility or recall estimate.

With authorized access to the original `P02_v4_5_Literature_Paper_and_Graphs.zip`,
run from `research/p02` in a disposable checkout:

```sh
unzip -n /path/to/P02_v4_5_Literature_Paper_and_Graphs.zip 'source/raw/*.csv'
python3 -m pip install -r requirements-replay.txt
OPENBLAS_NUM_THREADS=1 python3 analysis/joint_trends.py
OPENBLAS_NUM_THREADS=1 python3 analysis/revision_diagnostics.py
python3 analysis/anchor_probe.py
python3 analysis/habitability_bridge.py
python3 analysis/retrieval_sample.py
python3 analysis/verify_sota_followup.py
python3 analysis/build_companion.py
```

The joint-trend script checks the inputs against their archived SHA-256
values before reading records. It defaults to 10,000 real-paper resamples
for each of the two retrospective regimes, sharing each
draw's paper weight across targets. The original full-bundle verifier,
`analysis/verify_release.py`, runs in the complete author archive, where
its historical document and per-record checks have their original inputs.

The archived v4.1 pipeline also runs directly on authorized CSVs:
`python3 analysis/p02_pipeline.py --raw-dir source/raw --out-dir /path/to/new-results`.
The archived independent reconstruction, `source/reproduce_p02.py`, requires
the original Drive directory layout described in its source.

## Retrieval and scope

`python3 analysis/scix_comparison.py --print-queries` shows the historical
and symmetric query templates. The authenticated comparison is a new
acquisition and requires an authorized SciX/ADS credential. It can quantify
set differences. Its outputs cannot themselves establish scientific recall.
The independent reference frame uses publisher-deposited DOI references and
requires blind eligibility coding before it can report coverage for that frame.

- [Analysis contract](provenance/ANALYSIS_CONTRACT.md)
- [Retrieval protocol](provenance/V44_RETRIEVAL_CONTRACT.md)
- [Claim ledger](provenance/claim_ledger.csv)
- [Literature overlap and scope](provenance/V45_LITERATURE_AND_TRANSFER.md)
- [Agency affiliation evidence for Enceladus](provenance/ENCELADUS_AFFILIATIONS.md)

This research made use of the Astrophysics Data System, funded by NASA under
Cooperative Agreement 80NSSC25M7105.
