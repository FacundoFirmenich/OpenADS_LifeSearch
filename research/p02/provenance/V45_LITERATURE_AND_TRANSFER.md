# P02 v4.5 — literature frontier and transfer record

Checked 14 November 2026. Baseline: P02 v4.4 ZIP SHA-256
`89a4af6f010c7dfcc0bb9c074b20abac1fd9ae8d49741b7aa876fefb55754b33`.
This is a targeted scoping review and integration, not a formally exhaustive
systematic review, corpus refresh, or a proof of worldwide novelty. The analysis
period stays 2000–2023; the literature context extends to November 2026.

## Search and verification

| Discovery surface | Representative search families | Boundary |
|---|---|---|
| SciX / ADS public discovery and ADS help | `astrobiology bibliometric scientometric analysis astrobiology literature planetary research trends`; `Ocean Worlds comparative astrobiology habitability Enceladus Ganymede Europa Europa Clipper review 2025 2026`; identifiers for omitted and retained observations; `NASA Astrobiology living bibliography` | Two interfaces of one indexing ecosystem, not independent databases. Public discovery/record verification; not a completed authenticated query export. |
| arXiv title/abstract and extended-text discovery | `astrobiology planetary habitability bibliometric scientometric literature survey rankings NASA ADS`; `bibliometric multiverse simultaneous inference robust ordering ranking rank confidence sets partial orders`; exact title of the cross-subfield study; Ganymede, Europa and Enceladus searches | Distinguish versioned preprints from publications; same study is not two observations. |
| bioRxiv public pages and searchable metadata | `bibliometric landscape citation scientific literature communication research maps planetary astrobiology`; `astrobiology habitability biosignature planetary literature comparative Mars Enceladus Venus`; targeted SpaceBio and biomedical landscape lookups | Targeted public discovery; not a bulk categorical scrape. The dedicated DOI helper could not start because its shared source module was unavailable. No endorsement or screening outcome inferred from precedents. |
| Publishers, author archives and authoritative sources | Topic modeling, historical reference-year spectroscopy, marine-science survey, extremophiles/astrobiology, NExSS, Titan challenge/reply, relative recall, PRISMA-S, TARCiS, rank confidence sets | Check primary source or author copy for the strongest overlaps. Where only public abstract/metadata is available, scope the claim accordingly. |

Two passes: concept/synonym discovery, then exact titles/DOIs and backward
links within the closest works; forward discussion checked for the Titan
controversy and the later literature-room competitors. Both passes by the same
reviewer. Searches were predominantly in English; unpublished/inaccessible
work, uncrawled preprints, and records beyond the ranked return may be missed.
The source register is `v45_sources.tsv`; no third-party full text is bundled.

## Transfer decisions

- **Astrobiology already has several measurement maps.** Malaterre & Lareau's
  full-text three-journal topic map is a different sampling frame; Hemavathy &
  Baskaran's November 2026 RPYS work is about years of references. Aguzzi et al.
  use a data-driven bibliographic survey in marine science. Their study can
  seed a future reference frame, not replace blinded eligibility. The
  extremophile and institutional studies are genuine adjacent prior art:
  do not claim first bibliometric map of astrobiology.
- **NASA–SciX is not the population.** Its new living library covers outputs
  funded by NASA Astrobiology in full or in part. Add `bibgroup:"NASA Astrobiology"`
  as a frozen institutional comparison, separately from both search
  templates and from the external DOI-based reference frame. Neither query
  overlap nor that funding-defined slice identifies field-wide recall.
- **Prior method is real; the application is specific.** Simonsohn et al.
  already give joint inference over specifications. The closest
  bibliometric precedent is Leibel & Bornmann. Mogstad et al., Theorems 3.1
  and 3.3, project simultaneous difference sets into rank confidence sets
  for ranks of a specified population feature. P02 deliberately varies
  its measurement rule and window; these theorems do not certify the finite
  behavior of its non-smooth archival slopes or make attention a physical
  ranking. Integrate as attribution and a boundary, not a borrowed theorem.
- **Physical interpretation is revisable.** NExSS supplies local conditions
  and reference life, not an invitation to score worlds by citation counts.
  Titan's historical tidal interpretation now has reanalysis, critique and
  reply nodes. Keep them linked as arguments about interpretation, not
  independent direct samples. Enceladus organics and Mars Jezero chemistry
  are post-cutoff context. The two separately checked 2023 Europa JWST
  identities, both in the archive, supplement but do not amend the original
  15-item audit or yield a coverage denominator.
- **Companion platforms are prior art.** SpaceBio is an adjacent atlas for
  space biology and microgravity, not an equivalent planetary estimator.
  The borrowed scientific idea is navigable evidence with explicit scope;
  no LLM labels are treated as independent gold-standard adjudications.

## CRISPR Observability reference architecture

Public snapshot: [main at 23c4f56](https://github.com/FacundoFirmenich/crispr-observability/tree/23c4f56bbb927121f19d6bf794b2c16b28284c50).
Complete recursive tree: 1,792 entries, not truncated. All 27 HTML files
and 14 PDFs were matched to Git blob identities; one native HTML is an
empty placeholder. HTML titles and report families inspected, PDFs
text-extracted by figure, and graph/lab templates, readers, model builders,
validation and replay documentation inspected selectively at code level.
The reference Supergraph checker rebuilt the HTML byte-identically
(73 nodes, 75 edges, eight gates). This is not an audit of every
scientific claim in that repository or every runtime.

| Source surface | Transferred to P02 | Deliberately not ported |
|---|---|---|
| PDF Article/Overview/Argument | Separate one-glance visual abstract and a static epistemic map at fixed positions | Unreadable global network on one paper page |
| PaperGraph typed relations and local argument inspector | Evidence, derivation, required premises, scope limits; inspectable relation text and DOI/bibcode | Biological assumptions, source data, and code |
| Supergraph guided tour and standalone build | Guided route, upstream tracing, searchable archive, linkable evidence and exports | Copying theme, layout code, lab assays or ornamental graph density |
| Numerical explorer, observation report, lab and replay | Specificity down to two resampling regimes, 24 specifications each, individual year omissions, hashes and checks | WebGL interface that would not add a scientific operation here |

The implementation is independent. No CRISPR sequences, data, assets,
or GPL source code were copied into P02. The public-ready offline companion
projection embeds aggregate checks, archive anchor metadata, DOI links and
conditions; it does not expose raw bibliographic CSVs or the private dossier.
The deliverables are a repository-ready folder and document revisions.
No GitHub push, external deployment, preprint or journal submission was made.
