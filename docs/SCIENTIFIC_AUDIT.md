# Scientific audit of the canonical release

Date: 2026-11-14

## Gate

**PASS WITH EXPLICIT DATA-ACCESS BOUNDARY.** The numerical analysis is
deterministic and reproducible from the six frozen author-held CSV exports.
The public repository reproduces every aggregate result but does not
redistribute record-level ADS data.

## Verified observations

- 10,317 target-paper assignments.
- 9,513 unique bibcodes.
- 664 multi-target bibcodes (6.98%).
- Overlap degree: 8,849 / 553 / 88 / 19 / 2 / 2 papers assigned to one
  through six targets.
- Zero cross-file conflicts in title, author serialization, publication date,
  citation count, or document type for repeated bibcodes.
- 167 assignments with empty author lists.
- Six raw target counts and all reciprocal-authorship totals reproduced.
- Five construct rankings regenerated.
- All ten pairwise metric correlations evaluated by 720 exact permutations.

## Central corrections

1. Mars is 54.56% of raw assignments, not approximately 74%.
2. The reciprocal-team-size rule increases Mars's share to 55.96%; it does
   not reduce the share.
3. Raw and reciprocal rankings are identical.
4. The defensible inversions are across constructs: scale, recent activity,
   trajectory, and citation reception.
5. The archive cannot identify researcher FTE or productivity per worker.
6. The internal citation ratio is not a field-normalized MNCS.
7. Historical simulated labels and Decadal mappings are excluded from
   scientific evidence.
8. Budget, thermodynamic-power, mission-detection, and mission-value claims
   require data and models outside this corpus.

## Software verification

`src/openads_reanalysis.py` performs schema validation, within-target duplicate
checks, metadata-conflict auditing, JSON author parsing, deterministic metric
calculation, exact permutation inference, aggregate output, input hashing, and
figure generation. It contains no network request, random draw, synthetic
label, or credential.

- Public aggregate suite: 3 passed, 1 full-replay test skipped by design.
- Full author-held replay: 4 passed.
- Manuscript and supplement: compiled twice, no unresolved references, no
  overfull boxes, and visually inspected page by page.

## Public-release exclusions

- six record-level ADS exports and their concatenation;
- record-level derivatives and coder packets derived from those exports;
- manuscript and supplementary PDF/LaTeX files;
- historical manuscript and supplement provenance PDFs.

The exclusions do not conceal numerical inputs: filename, row count, byte
size, and SHA-256 are preserved in the frozen manifest. They enforce the ADS
redistribution boundary and the author's instruction to deliver manuscript
files separately.

## Residual external actions

- Rotate the ADS credential embedded in an earlier public commit.
- Decide separately whether to rewrite Git history; this release removes the
  credential from the current branch but does not rewrite history.
- Before journal submission, confirm author affiliations, correspondence,
  funding, competing interests, and the final data-availability language.
