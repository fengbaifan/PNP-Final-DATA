# Patrons and Painters Entity and Relation Tables (0.2-draft)

**Status: draft; do not distribute publicly.** The project and third-party rights have not been reviewed, so no license is asserted. Citation metadata is incomplete.

## Contents

- `entities.csv`: current 1,019 knowledge unit identifiers, type, and bilingual names.
- `entity-candidates.csv`: index-derived, accepted-unit, and source-derived mention candidates, including explicit exclusions. `candidate_source_ref` uses a stable `units/...` ID for accepted-unit candidates and a segment/line locator for reviewed source mentions.
- `alignment.csv`: identity decisions. Empty `candidate_id` means unresolved, not a negative match.
- `enrichment.jsonl`: one preserved structured-table occurrence per row, with original cells, section, evidence text, source references, and verification status.
- `relations.csv`: formal and pending directed relations, context, evidence locator, and note.
- `portable-references.csv`: registry of relative Markdown links retained in enrichment values/evidence/cells. Links to entity cards resolve to stable KU IDs; processing-note targets are identified but their files are not bundled.
- `sources.csv`: source registry.
- `enrichment-citation-links.csv`: one row per citation string in enrichment, linked by normalized exact citation text or the documented Haskell book author-title-year identity rule; ambiguous and unmatched citations stay explicit.
- `wikidata-source-candidates.csv`: review-only candidate source records for unverified Wikidata property rows. Candidate records are derived from entity identity alignment and QID mentions in the source registry; they do not support the property's value and do not assign a `source_id` to the enrichment row.
- `s2-coverage.csv`: chapter-level segment disposition ledger. `reviewed` links the original OCR line ranges to the existing processing record; `excluded` rows include a reason. This proves coverage disposition only, not semantic quality.
- `segments.csv`: portable source segment manifest with source IDs, asset basenames, line intervals, and hashes. Segment text is omitted.
- `mentions.csv`: S2 entity mentions with stable candidate and segment IDs and character offsets into the segment source text.
- `book-statements.jsonl`: S2 claims, qualifications, original quotations, and source line locators. Quotes are included only in this restricted draft; source rights must be reviewed before distribution.
- `schema.md`: field definitions and status semantics.
- `metadata.json`: version, counts, release limits, and unresolved publication requirements.
- `rights-review.md`: component-by-component clearance checklist; no legal status or license is inferred.
- `example_query.py`: standard-library example for loading and querying the tables.

## Load and query

Run `python example_query.py [ku_id]` for a compact entity, field, relation, and portable-reference query; add `--full` to include complete evidence rows. For example, `python example_query.py units/persons/guercino`.

Source citations may contain external URLs or source IDs. Enrichment retains original Markdown link text; use `portable-references.csv` to resolve entity-card links to stable KU IDs. Project processing notes are identified by task/file/anchor but are not included. Source segment text is omitted; use `segments.csv` and `sources.csv` to resolve locators against separately obtained source assets.

## Evidence and limits

`formal` is a relation decision; it does not mean every underlying historical proposition has undergone an independent review. `pending` means the relation remains unresolved. Enrichment `evidence_status` is per extracted row; `unverified` must not be treated as confirmed. `source_ref` and `source_citations` preserve the card's source notation and citation text.

Some unverified Wikidata-property rows have no row-level source pointer even when the entity has a Wikidata identity alignment. The validation report counts these cases and source-registry duplicates; do not infer property support from identity alignment alone.

`source_ref` preserves the original compact/card-local source notation. `source_id` or `source_ids` link to records in `sources.csv`; `source_citations` preserve human-readable citation strings, and `source_urls` preserve extracted URLs. These fields are independent: citation strings may describe multiple pages or locations for one source ID, and no positional mapping between the arrays is guaranteed. Use explicit source IDs to join to `sources.csv`; do not infer a source-to-citation match by list position. The validation report counts rows where source-ID and citation-string counts differ.

`enrichment-citation-links.csv` supplies a separate deterministic bridge for each citation-string occurrence. It first matches normalized exact text (Unicode NFKC, whitespace collapsed, case-insensitive) against `sources.csv` citation/label values. If that fails, a narrow work-identity rule matches citations naming Haskell, *Patrons and Painters*, and 1980 to source records with the same author, title, and year. This distinguishes page locators from the edition-level source ID. A unique match fills `source_id`; multiple matching records remain `ambiguous`, and absent matches remain `no_exact_match`. Matching identifies a bibliographic record only; it does not prove that the source supports the field value.

This is a portability review package, not a publication-ready dataset. See `validation-report.md` before reuse.
