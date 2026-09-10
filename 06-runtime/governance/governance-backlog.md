# Governance Backlog

> Derived status signal; it is not a semantic decision or proof of publication readiness.
> Snapshot: 2026-09-09 23:26
> Structural health: 61/130
> Knowledge units: 298
> Maturity metrics: unscored_semantic_maturity

> 有效知识按 accepted.yml 统计。下面的处理包、候选与 dataflow 项仍为历史库存诊断，不表示本项目已执行，也不自动成为开工或交接门禁。

## System defects - P0

| ID | Issue | Scope | Status |
|---|---|---|---|
| P0-RULE-DRIFT | active rules differ from repository facts | 1 findings | open |

## System defects - P1

| ID | Issue | Scope | Status |
|---|---|---|---|
| P1-TRANSLATION-PERSONS-NAME_ORIGINAL | translation field coverage incomplete: persons.name_original | 134 missing | open |
| P1-TRANSLATION-PERSONS-LANGUAGE_ORIGINAL | translation field coverage incomplete: persons.language_original | 134 missing | open |
| P1-TRANSLATION-PERSONS-NAME_ZH | translation field coverage incomplete: persons.name_zh | 134 missing | open |
| P1-TRANSLATION-PERSONS-TRANSLATION_STATUS | translation field coverage incomplete: persons.translation_status | 134 missing | open |
| P1-TRANSLATION-INSTITUTIONS-NAME_ORIGINAL | translation field coverage incomplete: institutions.name_original | 20 missing | open |
| P1-TRANSLATION-INSTITUTIONS-NAME_ORIGINAL_LANGUAGE | translation field coverage incomplete: institutions.name_original_language | 20 missing | open |
| P1-TRANSLATION-INSTITUTIONS-NAME_ZH | translation field coverage incomplete: institutions.name_zh | 20 missing | open |
| P1-TRANSLATION-INSTITUTIONS-TRANSLATION_STATUS | translation field coverage incomplete: institutions.translation_status | 20 missing | open |
| P1-TRANSLATION-WORKS-TITLE_ORIGINAL | translation field coverage incomplete: works.title_original | 35 missing | open |
| P1-TRANSLATION-WORKS-TITLE_ORIGINAL_LANGUAGE | translation field coverage incomplete: works.title_original_language | 35 missing | open |
| P1-TRANSLATION-WORKS-TITLE_ZH | translation field coverage incomplete: works.title_zh | 35 missing | open |
| P1-TRANSLATION-ARCHIVES-TITLE_ORIGINAL | translation field coverage incomplete: archives.title_original | 41 missing | open |
| P1-TRANSLATION-ARCHIVES-TITLE_ORIGINAL_LANGUAGE | translation field coverage incomplete: archives.title_original_language | 41 missing | open |
| P1-TRANSLATION-ARCHIVES-TITLE_ZH | translation field coverage incomplete: archives.title_zh | 41 missing | open |
| P1-TRANSLATION-TERMS-TERM_ORIGINAL | translation field coverage incomplete: terms.term_original | 30 missing | open |
| P1-TRANSLATION-TERMS-TERM_ZH | translation field coverage incomplete: terms.term_zh | 30 missing | open |
| P1-TRANSLATION-TERMS-ACADEMIC_TRANSLATION_STATUS | translation field coverage incomplete: terms.academic_translation_status | 30 missing | open |
| P1-VERIFY-LEVEL | verification_level missing | 298 files | open |
| P1-DATAFLOW | source-to-processing dataflow is incomplete | 4 findings | open |
| P1-CONTENT-SECTIONS | required content sections missing | 318 files | open |
| P1-INGEST-CHAPTERS_WITHOUT_READING_LEDGER | chapters without reading ledger | 4 packages | open |
| P1-INGEST-CHAPTERS_WITHOUT_CONTINUITY_MAP | chapters without continuity map | 4 packages | open |
| P1-INGEST-CHAPTERS_WITHOUT_SEMANTIC_STITCH_LOG | chapters without semantic stitch log | 4 packages | open |
| P1-INGEST-CHAPTERS_WITHOUT_SOURCE_STRUCTURE_MAP | chapters without source structure map | 4 packages | open |
| P1-INGEST-CHAPTERS_WITHOUT_EXTRACTION_COVERAGE_MATRIX | chapters without extraction coverage matrix | 4 packages | open |
| P1-RECALL-CHAPTERS_WITHOUT_CANDIDATE | chapters without candidate | 4 packages | open |
| P1-RECALL-CHAPTERS_WITHOUT_DECISION | chapters without decision | 4 packages | open |
| P1-RECALL-CHAPTERS_WITHOUT_RECALL | chapters without recall | 4 packages | open |

## System defects - P2

| ID | Issue | Scope | Status |
|---|---|---|---|
| P2-CONTENT-PLACEHOLDER | placeholder content remains | 1 findings | open |

## Research debt (not a system defect)

| ID | Issue | Scope | Status |
|---|---|---|---|
| RD-UNITS_MISSING_HIERARCHY_ASSIGNMENT | knowledge units missing complete hierarchy assignment | 298 | not_in_current_scope |

## Candidate opportunities (not accepted knowledge)

| ID | Issue | Scope | Status |
|---|---|---|---|
| OPP-ISOLATED | isolated units may warrant relation review | 99 | candidate_opportunity |

## Completed mechanical signals

| ID | Issue | Scope | Status |
|---|---|---|---|
| C-FM | required frontmatter coverage complete | 2026-09-09 | completed |
| C-VERIFY | verification state conflicts absent | 2026-09-09 | completed |
| C-SCHEMA | deprecated type drift absent | 2026-09-09 | completed |
