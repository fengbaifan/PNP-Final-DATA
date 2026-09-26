# Rights and citation review (unresolved)

This checklist records release dependencies; it is not a legal determination. No license is asserted for the dataset, source excerpts, third-party metadata, or repository code.

| Component | Material present in 0.2-draft | Current status | Required before public release |
|---|---|---|---|
| Source assets | Basenames, line ranges, and hashes in `segments.csv`; source segment text is omitted | Rights and access terms not reviewed | Confirm redistribution and access terms for each included or required source asset |
| Book-derived statements | 172 claims with original quotation excerpts and locators in `book-statements.jsonl` | Third-party quotation rights unresolved | Review quotation permissions/limits and decide whether to retain, redact, or replace excerpts |
| Entity fields and relations | Structured facts, concise prose, citations, URLs, and original table cell text | Source-by-source rights review incomplete; factual accuracy is not a rights determination | Review third-party record terms and distinguish project-authored text from sourced expression |
| Bibliographic/source registry | 1684 source records with citations and URLs | Terms of service and metadata reuse not reviewed | Check source/database reuse conditions and preserve attribution requirements |
| Software | `example_query.py` and project export/validation code | No software license identified | Select and apply a separate code license if the code will be redistributed |
| Attribution and citation | Dataset creator list is empty; persistent identifier and final citation are null | Incomplete | Confirm creator/affiliation metadata, freeze a release version, deposit it in a suitable repository, and create the final citation |

**Release gate:** keep this package private until the project owner confirms creator metadata and the applicable rights/attribution decisions. Do not replace `license: null` or the draft status with a guessed license or identifier.
