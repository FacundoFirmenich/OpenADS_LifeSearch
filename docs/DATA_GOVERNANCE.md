# Data governance and reproducibility

This repository separates reproducible scientific logic from data that cannot
be redistributed publicly under the source service's terms.

## Public

- acquisition and analysis source code;
- historical query grammar;
- frozen input hashes and row counts;
- aggregate tables and figures;
- deterministic tests and verification receipts;
- claim ledger, methodological audits and provenance documents;
- offline aggregate epistemic graphs.

## Not public

- the six record-level ADS CSV exports;
- concatenated record-level derivatives;
- record-level coding packets derived from the ADS exports;
- manuscript and supplementary-material sources or PDFs.

The manuscript and supplement are maintained as author deliverables outside
the repository. Their absence is deliberate and should not be interpreted as
missing build output.
