# P02 v4.2: dated retrospective follow-up

14 November 2026. This procedure is defined after the September descriptive
reversals were known and before computing the new bootstrap. It is not a
prospective preregistration, and the archive is not an independent validation sample.

- Family: both historical growth measures × all 15 unordered target pairs ×
  three historical windows × 24 specifications per window = 2,160 contrasts.
  No selection on the September reversal list enters band calibration.
- Observational unit: unique ADS bibcode; all co-assignments use one multiplicity
  across every variant, target, metric and window. Use the historical fixed
  retrieval and weighting transformations, including fixed imputed author
  medians and fixed target-split weights; do not retrain these transformations.
- Primary resampling: multinomial bibcode bootstrap within each publication year,
  retaining total that year in the union. Sensitivity: one global multinomial,
  allowing the observed pooled annual totals to vary. Both condition on the
  archive as the empirical support; neither models coverage, topic clusters,
  corpus-selection error, or the arrival process over unobserved years.
- 10,000 draws per regime, seeds 2026111401 and 2026111402, and two half-run
  calibrations for stability. For each contrast, scale centered bootstrap errors
  by its bootstrap standard deviation; calibrate a two-sided approximate
  simultaneous 95% band by the 0.95 quantile (higher convention) of the draw-wise
  maximum absolute standardized error over the whole family. Degenerate or
  non-finite components stop calibration rather than being quietly omitted.
- A window's direction is supported only if **all 24** bands exclude zero in
  the same direction. Opposite supported directions across two windows establish
  a conditional reversal under that resampling regime. Record separately
  empirical ranges, pointwise bands, simultaneous bands, and sensitivity to
  resampling scheme. Report a 2-percentage-point signed margin as a transparent
  sensitivity, not a practical or substantive threshold.
- The calculations do not identify calendar change points, causal effects,
  mission priority, or the ranking of the complete relevant literature.
