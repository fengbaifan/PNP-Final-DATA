# Data dictionary (draft)

## entities.csv

`ku_id` is the stable object identifier (`units/{type}/{slug}`); `type`, `canonical_name`, and `name_en` describe the entity. `source_task` is the project task scope. Card filesystem paths are omitted.

## entity-candidates.csv

`candidate_id` is the stable candidate identifier, not an accepted entity ID. For index-derived rows, `canonical_name` is the original index heading; `sub_entry` can identify the specific work, place, or other item listed under that heading. Keep both fields when interpreting a mention: the heading alone may not name the matched item. `index_entry_id`, `index_source_file`, `detail`, and `index_page_range` retain original index provenance. `status=open|excluded`; `open` means the candidate has not been resolved or accepted, while exclusions require `exclude_reason`. `candidate_origin=accepted-ku` marks candidates created to represent already accepted knowledge units; `body-mention` marks candidates discovered in a reviewed passage. `candidate_source_ref` carries the stable KU or source segment/line reference. A blank candidate origin denotes an index candidate.

## alignment.csv

`alignment_id`, `candidate_id`, `ku_id`, external source and identifier, access date, and `decision`. Decision values are `same`, `new`, `conflict`, `excluded`, or `undecided`. An empty candidate ID, if present in another snapshot, marks an unresolved legacy row.

## enrichment.jsonl

One JSON object per preserved source table row. `enrichment_id` and `ku_id` identify the row and entity. `field`, `value`, and `cells` preserve parsed values and the full original row. `table_section`, `table_header`, `has_header`, `row_index`, and `occurrence_id` preserve card-table context. `evidence` preserves the original evidence cell. `source_ref` preserves the original compact/card-local source notation; `source_id(s)` link to source-registry records; `source_citations` preserve citation strings; `source_urls` preserve extracted URLs; and `accessed_date` retains the recorded access date. These fields are not positional parallel arrays: one source ID can have multiple citation strings, so use explicit source IDs rather than array order to join to `sources.csv`. `origin`, `evidence_status`, and nullable `dispute` retain the recorded state. `unverified` means no semantic verification is asserted.

## relations.csv

`relation_id`, subject/object `ku_id`, directed `predicate`, context (`time`, `role`, `scope`), `origin`, `status`, source identifier, locator (`source_file`, `source_span`), and `note`. `status=formal|pending|rejected`; formal rows are included as accepted relation decisions, pending rows remain uncertain. Internal source paths are converted to the Haskell source ID where applicable.

## sources.csv

`source_id` identifies a source record; `kind`, `label`, `version`, `accessed_date`, `citation`, and `url` describe it. Empty values are unknown, not inferred defaults.

## enrichment-citation-links.csv

One row per `source_citations` item in `enrichment.jsonl`, keyed by (`enrichment_id`, `citation_index`). `source_id` is populated only for a unique exact-text or documented work-identity match to `sources.csv`; `candidate_source_ids` preserves all matching IDs when ambiguous. `no_exact_match` means neither deterministic rule identified a record; it does not mean the citation is false or unsupported. Bibliographic matching is not factual verification.

## portable-references.csv

One row per relative Markdown link occurrence in an enrichment row's `value`, `evidence`, or `cells`. `content_field` identifies the JSONL field and `cell_index` is a zero-based index for `cells`; `link_index` is zero-based within that field/cell. Entity `target_id` values use the stable `units/{type}/{slug}` KU ID and should join to `entities.csv`. Processing-note references use project/task/file/anchor identifiers and have `resolution_status=not_in_package`; their target content is not included.

## wikidata-source-candidates.csv

One row per unverified Wikidata property-like enrichment row with an empty `source_ref`. `candidate_source_ids`, revisions, access dates, and URLs are possible source records derived from a unique `same` entity identity alignment and QID text in `sources.csv`; `pointer_status` distinguishes ambiguous candidates from missing alignment/source records. These are review leads only, not assigned provenance or evidence for the property value.

## s2-coverage.csv

`chapter` and `segment_id` identify each source segment in an S2 scope. `disposition=reviewed|excluded`; `migration_status=pending|partial|complete` distinguishes reviewed coverage from completed table migration. Reviewed rows retain original OCR line ranges and excluded rows carry a reason. Coverage rows do not encode mentions or claims.

## segments.csv

`segment_id` is the stable S0 segment identifier; `source_id` links to `sources.csv`; `source_asset` is a basename rather than a local path. `line_start` and `line_end` identify the segment slice in that asset, and `sha256` verifies the exact decoded line slice. `asset_sha256` identifies the underlying source asset. Segment text is not redistributed.

## mentions.csv

`mention_id`, `segment_id`, and `candidate_id` identify the mention and its candidate. `surface_form` preserves the source spelling (including recorded OCR variants); `start_char` and `end_char` are zero-based Unicode code-point offsets into the decoded segment text, with an exclusive end. `note` records local interpretation and unresolved spelling or identity issues.

## book-statements.jsonl

One JSON object per claim. `statement_id` is stable; `segment_id` and `source_id` connect the claim to the segment and source registry. `predicate` and `qualifiers` carry the claim, speaker, scope, and uncertainty. `original_quote` preserves the cited OCR span, and `source_line_start`/`source_line_end` within `qualifiers` locate it in the named `source_asset`. `subject_candidate_id` and `object_candidate_id` are nullable and are not formal relation records.

## S2 migration state

The package includes all current S2 mention and statement records, plus a coverage ledger that marks complete, partial, pending, and excluded segments. Partial coverage is explicit; the counts do not constitute a chapter-complete extraction.

## Null and licensing

Empty strings and JSON `null` represent unrecorded or unresolved values, not false. Creator metadata, persistent identifier, citation, license, and rights clearance are intentionally unset. Confirm rights for derived content and third-party records before public sharing.
