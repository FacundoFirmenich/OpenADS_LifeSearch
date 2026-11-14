# Prospective symmetric retrieval and validation protocol

Protocol version: 1.0.0  
Frozen: 2026-08-25  
Status: prospective; no result from a future retrieval may be merged into the
legacy-snapshot estimands without a versioned amendment.

## Objective

Estimate and compare target-specific literature constructs under a retrieval
design whose syntax, fields, eligibility rule, and validation burden are
symmetric across Enceladus, Europa, Mars, Titan, Venus, and Ganymede. This
protocol does not estimate mission value, habitability, labour productivity, or
the probability of detecting life.

## Retrieval families

Two query families will be executed for every target with the target name as the
only substituted token:

1. High recall: target name in ADS indexed full text.
2. High precision: target name in title or keyword.

The publication-year interval, document-property filter, requested fields,
sorting, page size, pagination rule, and synonym-expansion setting must be
identical for all six targets. `property:article` and `property:refereed` are
distinct analyses, never synonyms. Exact executable query strings will be
archived before inspecting target-level counts.

Each API response must be stored byte-for-byte together with retrieval UTC,
endpoint, request parameters, response headers, ADS client and API versions,
page number, returned-count total, and SHA-256 digest. Deduplication is by
bibcode. A paper may retain multiple target assignments.

## Eligibility construct

A record is relevant when its scientific object materially includes the named
Solar System body, its environment, its origin/evolution, mission observation,
or implications for astrobiology/planetary science. Mere use of a homonymous
galactic structure, author name, acronym, bibliography-only mention, or generic
comparison without target-specific analysis is irrelevant. Ambiguous cases are
not forced into binary certainty: coders may use `UNCERTAIN`, followed by
adjudication with the reason preserved.

## Human gold standard for precision

Sampling is stratified by target, retrieval family, decade, and machine-screen
evidence class (title, keyword, abstract/full-text only, homonym-risk). Random
seeds and sampled bibcodes are frozen before coding. Two independent coders,
blinded to target ranks and aggregate outcomes, label every sampled record.
Disagreements are adjudicated by a third reviewer who did not see aggregate
results. Raw labels, timestamps, rationales, and adjudications are released.

For a target-by-family precision estimate with worst-case 95% Wald half-width
0.05, the initial sample is 385 records before finite-population correction.
Wilson intervals are reported. When a stratum contains fewer records, it is
censused. Cohen's kappa is secondary to the confusion matrix and category-wise
agreement because prevalence can distort kappa.

## Independent benchmark for recall

Recall cannot be estimated from records returned by the query being evaluated.
The benchmark is assembled independently from authoritative review
bibliographies, mission-instrument bibliographies, curated planetary-science
indexes, and backward/forward citation expansion seeded before ADS query results
are inspected. Benchmark provenance is recorded per bibcode. Recall and its
Wilson interval are reported separately by target, source, decade, and retrieval
family; no single pooled recall number is used to hide target heterogeneity.

## Analysis freeze and admissible outcomes

Primary analyses use complete publication years only. The final calendar year
is included only after a documented completeness check; otherwise it is a
separate sensitivity. Citation reception is reported both against the pooled
same-year corpus and a leave-one-target-out same-year reference. Team-size
discounts remain descriptive and are never called fractional authorship or FTE.

Admissible outcomes are:

- a pairwise ordering invariant to the preregistered specifications and stable
  under paper-cluster resampling;
- specification-sensitive ordering;
- sampling-sensitive ordering;
- retrieval-not-validated or recall-not-identified;
- no unique optimum under declared non-commensurable constructs.

No specification may be removed, query narrowed, year window shortened, or
target relabelled after inspecting target-level ranks without a timestamped
amendment and parallel reporting of the frozen analysis.
