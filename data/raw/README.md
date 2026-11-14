# Raw snapshot access boundary

The six record-level CSV exports used for the frozen analysis are not
redistributed in this public repository. ADS API terms prohibit onward
redistribution of data obtained from the service. The public release therefore
contains:

- exact filenames, row counts, byte sizes and SHA-256 digests in
  `results/canonical/snapshot_manifest.json`;
- the historical query grammar in `src/acquire_ads_snapshot.py`;
- deterministic reanalysis code;
- aggregate outputs, tests, figures and claim-level provenance.

Authorized authors can place the six files in this directory and run:

```bash
python src/openads_reanalysis.py \
  --data-dir data/raw \
  --output-dir results/canonical \
  --figure-dir figures \
  --strict-expected
```

A newly acquired ADS snapshot is time-dependent and must not be represented as
byte-identical to the archived 2026 snapshot.
