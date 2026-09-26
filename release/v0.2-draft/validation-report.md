# Validation report (0.2-draft)

## Mechanical checks

- Current tables: 1,019 entities; 3,593 candidates; 335 alignment rows; 10,149 enrichment rows; 1,227 relations; 1,684 sources.
- S2 coverage ledger: 30 segment dispositions; 27 reviewed segment(s) complete, 0 partial, and 0 pending; the package includes 665 mention rows and 172 statement rows.
- Formal relations: 1,225; pending relations: 2.
- Unverified enrichment rows: 1,501.
- Among unverified rows with empty `source_ref`, 83 retain source IDs/citations/URLs in other fields; 464 carry the `项目命名` evidence label; 469 have a Wikidata-related evidence marker but no structured source metadata; 377 have other evidence text but no structured source metadata; 106 contain neither evidence text nor structured source metadata. These disjoint field-presence buckets are not semantic classifications.
- Wikidata provenance diagnostic: 465 unverified rows have a property-like Wikidata marker; 403 map through a unique `same` QID alignment to 52 QIDs in `sources.csv`, but each QID has multiple source records (44 groups with one recorded revision; 8 with differing revisions). No source ID was assigned automatically.
- `wikidata-source-candidates.csv` contains 465 review-only rows. Candidate QIDs and source records are identity-based pointers, not property evidence or factual verification.
- Alignment rows without a candidate ID: 0.
- Portable references: 3781 relative Markdown link occurrences mapped; 3751 entity targets use KU IDs and 30 processing-note targets are not bundled.
- `audit_tables.py --summary`: no structural errors; unresolved rows are reported as warnings.
- `audit_tables.py --strict-stage --summary`: no structural or migration errors. It reports two unresolved source markers as warnings; complete migration does not establish semantic recall or independent claim accuracy.
- 138 enrichment rows have unequal counts of structured source IDs and citation strings. These fields are preserved independently; no one-to-one mapping is inferred from array positions.
- `enrichment-citation-links.csv`: 12254 citation occurrences; 9328 normalized exact-text matches, 2873 strict author-title-year identity matches, 0 ambiguous matches, and 53 without a deterministic source-record match. These are bibliographic links, not evidence verification.
- `build_cards.py --check`: post-render full preflight on 2026-09-26 reported zero files to write across all 1,019 cards; the CSV-backed card views match the current structured tables.
- The table audit independently re-scans card Markdown: 2,608 tables and 10,149 rows match the exported source cells and layout metadata exactly.

## Known unresolved issues

- The coverage ledger does not establish sentence-level entity recall or independent claim-level accuracy. Source segment text is omitted, and quote redistribution rights are unresolved.
- A read-only exact-surface scan of typed candidate labels found 13 uncovered spans across the 27 migrated segments; these were manually reviewed and added as mentions. This scan only finds names already present in the candidate table, so it cannot establish candidate recall, identity accuracy, or overall semantic quality.
- All 335 alignment rows link to a KU and candidate. Twenty-five same/QID outcomes are directly restored from retained evidence; 12 originally unpaired rows remain undecided.
- 1,501 enrichment rows remain unverified; 1,499 have an empty `source_ref`. See the provenance diagnostic above before interpreting an empty locator as absent evidence. 2 retained source markers do not resolve to a source record.
- Wikidata identity alignment does not verify the aligned entity's property values. The property-like row matches above remain without an unambiguous version-level source pointer; source-record duplicates are referenced and have not been merged.
- A stratified blind review in an isolated Codex context covered 9 segments and cross-checked 363 existing mentions and 69 statements; four high-confidence errors were corrected. This is not formal human acceptance and does not estimate chapter-level precision or recall. Rights review, license, author metadata, DOI, and final citation remain unresolved.
- No representative extraction-throughput benchmark was recorded during the original semantic processing; wall time for mechanical audit/render checks is not an extraction-speed estimate.

## Local runtime observation

Five consecutive warm-cache runs on Windows 11 with Python 3.14.4 (2026-09-26), including process startup: S0 segment preview, 62 files/953 segments, median 0.166 s (range 0.164–0.173); S1 candidate preview, 2,930 index rows/3,593 candidates, median 0.132 s (0.125–0.146); S5 field-table preview, 1,019 cards/10,149 rows, median 3.358 s (3.182–3.517); strict-stage table audit, median 1.271 s (1.176–1.346); full render preflight, 1,019 cards, median 4.403 s (4.017–4.913); dataset export preview, median 0.719 s (0.719–0.751). Commands ran sequentially and read-only. These machine-specific observations measure parsing, reconciliation, validation, and serialization; they do not measure model reasoning or semantic extraction throughput and are not a before/after speedup claim.

This report establishes portability and mechanical table integrity only. It does not establish extraction precision, recall, factual accuracy, or publication readiness.
