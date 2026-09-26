#!/usr/bin/env python3
"""Create a non-public, self-contained review package from current tables.

Preview is the default. --apply creates release/v0.2-draft once and refuses to
overwrite an existing directory. The package states that rights and citation
metadata are unresolved; it is not a public release.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import posixpath
import re
import shutil
import unicodedata
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
TABLES = BASE / "04-knowledge" / "tables"
RELEASE = BASE / "release" / "v0.2-draft"
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
PORTABLE_REFERENCE_FIELDS = [
    "reference_id", "enrichment_id", "ku_id", "content_field", "cell_index",
    "link_index", "link_label", "target_type", "target_id", "resolution_status",
]


def read_csv(name: str) -> tuple[list[str], list[dict[str, str]]]:
    with (TABLES / name).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def rows_jsonl(name: str) -> list[dict]:
    return [json.loads(line) for line in (TABLES / name).read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def csv_text(fields: list[str], rows: list[dict]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def portable_reference_rows(
    enrichment: list[dict], card_path_by_ku: dict[str, str], entity_ids: set[str],
) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in enrichment:
        card_path = card_path_by_ku.get(row.get("ku_id", ""), "")
        if not card_path:
            continue
        content_items = [
            ("value", "", [str(row.get("value", ""))]),
            ("evidence", "", [str(row.get("evidence", ""))]),
            ("cells", "", [str(value) for value in row.get("cells", [])]),
        ]
        for content_field, _, values in content_items:
            for cell_index, value in enumerate(values):
                for link_index, match in enumerate(MARKDOWN_LINK_RE.finditer(value)):
                    label, raw_target = match.groups()
                    target = raw_target.replace("\\", "/")
                    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("#"):
                        continue
                    target_path, _, fragment = target.partition("#")
                    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(card_path), target_path))
                    if resolved.startswith("04-knowledge/units/") and resolved.endswith(".md"):
                        target_id = resolved[len("04-knowledge/"):-3]
                        target_type = "entity"
                        status = "resolved_entity" if target_id in entity_ids else "unresolved_entity"
                    elif resolved.startswith("03-processing/"):
                        target_id = resolved[len("03-processing/"):]
                        target_type = "processing_record"
                        status = "not_in_package"
                    else:
                        target_id = resolved
                        target_type = "repository_file"
                        status = "not_in_package"
                    if fragment:
                        target_id += "#" + fragment
                    fingerprint = "|".join((row.get("enrichment_id", ""), content_field,
                                            str(cell_index), str(link_index), target_id, label))
                    reference_id = "ref-" + hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16]
                    refs.append({
                        "reference_id": reference_id,
                        "enrichment_id": row.get("enrichment_id", ""),
                        "ku_id": row.get("ku_id", ""),
                        "content_field": content_field,
                        "cell_index": str(cell_index) if content_field == "cells" else "",
                        "link_index": str(link_index),
                        "link_label": label,
                        "target_type": target_type,
                        "target_id": target_id,
                        "resolution_status": status,
                    })
    return refs


def source_citation_link_rows(enrichment: list[dict], sources: list[dict[str, str]]) -> list[dict[str, str]]:
    def normalize(value: str) -> str:
        return " ".join(unicodedata.normalize("NFKC", value).split()).casefold()

    def work_identity(value: str) -> tuple[str, ...]:
        normalized = normalize(value)
        if "haskell" in normalized and "patrons and painters" in normalized and re.search(r"\b1980\b", normalized):
            return ("haskell", "patrons and painters", "1980")
        return ()

    source_ids_by_citation: dict[str, set[str]] = {}
    source_ids_by_identity: dict[tuple[str, ...], set[str]] = {}
    for source in sources:
        source_id = source.get("source_id", "")
        if not source_id:
            continue
        for field in ("citation", "label"):
            source_text = source.get(field, "")
            citation = normalize(source_text)
            if citation:
                source_ids_by_citation.setdefault(citation, set()).add(source_id)
            identity = work_identity(source_text)
            if identity:
                source_ids_by_identity.setdefault(identity, set()).add(source_id)

    linked: list[dict[str, str]] = []
    for row in enrichment:
        for index, citation in enumerate(row.get("source_citations") or []):
            matches = sorted(source_ids_by_citation.get(normalize(str(citation)), set()))
            method = "normalized_exact_citation" if matches else ""
            if not matches:
                identity = work_identity(str(citation))
                matches = sorted(source_ids_by_identity.get(identity, set())) if identity else []
                if matches:
                    method = "work_author_title_year"
            linked.append({
                "enrichment_id": row.get("enrichment_id", ""),
                "ku_id": row.get("ku_id", ""),
                "citation_index": str(index),
                "source_id": matches[0] if len(matches) == 1 else "",
                "candidate_source_ids": ";".join(matches),
                "match_method": method,
                "resolution_status": "resolved_unique" if len(matches) == 1 else "ambiguous" if matches else "no_exact_match",
            })
    return linked


def build_package() -> tuple[dict[str, str], dict]:
    files: dict[str, str] = {}
    ku_fields, ku_rows = read_csv("ku-manifest.csv")
    public_ku_fields = [field for field in ku_fields if field != "card_path"]
    files["entities.csv"] = csv_text(public_ku_fields, ku_rows)

    cand_fields, cand_rows = read_csv("entity-candidates.csv")
    for row in cand_rows:
        ref = row.get("candidate_source_ref", "")
        if ref.startswith("04-knowledge/units/"):
            ref = ref[len("04-knowledge/"):]
        if ref.startswith("units/"):
            ref = ref.removesuffix(".md")
        row["candidate_source_ref"] = ref
    files["entity-candidates.csv"] = csv_text(cand_fields, cand_rows)

    align_fields, align_rows = read_csv("alignment.csv")
    align_fields = [field for field in align_fields if field not in {"process_ref", "legacy_ku_id"}]
    files["alignment.csv"] = csv_text(align_fields, align_rows)

    source_fields, source_rows = read_csv("sources.csv")
    files["sources.csv"] = csv_text(source_fields, source_rows)

    coverage_fields, coverage_rows = read_csv("s2-coverage.csv")
    files["s2-coverage.csv"] = csv_text(coverage_fields, coverage_rows)
    segment_rows = rows_jsonl("segments.jsonl")
    segment_fields = [
        "segment_id", "source_id", "chapter", "section", "source_asset",
        "line_start", "line_end", "sha256", "asset_sha256", "release_excluded",
    ]
    portable_segments = []
    for row in segment_rows:
        portable_segments.append({
            "segment_id": row.get("segment_id", ""),
            "source_id": row.get("source_id", ""),
            "chapter": row.get("chapter", ""),
            "section": row.get("section", ""),
            "source_asset": row.get("source_file", "").rsplit("/", 1)[-1],
            "line_start": row.get("line_start", ""),
            "line_end": row.get("line_end", ""),
            "sha256": row.get("sha256", ""),
            "asset_sha256": row.get("asset_sha256", ""),
            "release_excluded": row.get("release_excluded", ""),
        })
    files["segments.csv"] = csv_text(segment_fields, portable_segments)

    mention_path = TABLES / "mentions.csv"
    statement_path = TABLES / "book-statements.jsonl"
    mention_fields, mention_rows = read_csv("mentions.csv") if mention_path.exists() else ([], [])
    if mention_path.exists():
        files["mentions.csv"] = csv_text(mention_fields, mention_rows)
    statement_rows = rows_jsonl("book-statements.jsonl") if statement_path.exists() else []
    if statement_path.exists():
        source_id_by_segment = {row.get("segment_id", ""): row.get("source_id", "") for row in segment_rows}
        portable_statements = []
        for row in statement_rows:
            exported = dict(row)
            source_file = exported.pop("source_file", "")
            exported["source_asset"] = source_file.rsplit("/", 1)[-1]
            exported["source_id"] = source_id_by_segment.get(exported.get("segment_id", ""), "")
            portable_statements.append(json.dumps(exported, ensure_ascii=False, separators=(",", ":")))
        files["book-statements.jsonl"] = "\n".join(portable_statements) + "\n"
    complete_reviewed_segments = sum(row.get("disposition") == "reviewed" and row.get("migration_status") == "complete" for row in coverage_rows)
    partial_reviewed_segments = sum(row.get("disposition") == "reviewed" and row.get("migration_status") == "partial" for row in coverage_rows)
    pending_reviewed_segments = sum(row.get("disposition") == "reviewed" and row.get("migration_status") == "pending" for row in coverage_rows)

    rel_fields, rel_rows = read_csv("relations.csv")
    for row in rel_rows:
        if row.get("source_file", "").startswith("02-sources/"):
            row["source_id"] = row.get("source_id") or "haskell-1980-rev-ed"
            row["source_file"] = ""
    files["relations.csv"] = csv_text(rel_fields, rel_rows)

    enrichment = rows_jsonl("enrichment.jsonl")
    citation_link_fields = [
        "enrichment_id", "ku_id", "citation_index", "source_id", "candidate_source_ids",
        "match_method", "resolution_status",
    ]
    citation_links = source_citation_link_rows(enrichment, source_rows)
    files["enrichment-citation-links.csv"] = csv_text(citation_link_fields, citation_links)
    card_path_by_ku = {row["ku_id"]: row["card_path"].replace("\\", "/") for row in ku_rows}
    entity_ids = {row["ku_id"] for row in ku_rows}
    portable_refs = portable_reference_rows(enrichment, card_path_by_ku, entity_ids)
    files["portable-references.csv"] = csv_text(PORTABLE_REFERENCE_FIELDS, portable_refs)
    jsonl_rows = []
    for row in enrichment:
        row.pop("unit_evidence_status", None)
        # Preserve exact evidence cells and source locator data, while keeping
        # card file paths and process-only locators out of the portable export.
        jsonl_rows.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
    files["enrichment.jsonl"] = "\n".join(jsonl_rows) + "\n"

    entity_candidates = len(cand_rows)
    unresolved_alignment = sum(not row.get("candidate_id") for row in align_rows)
    formal_relations = sum(row.get("status") == "formal" for row in rel_rows)
    pending_relations = sum(row.get("status") == "pending" for row in rel_rows)
    unverified_enrichment = sum(row.get("evidence_status") == "unverified" for row in enrichment)
    unverified_without_source_ref = sum(
        row.get("evidence_status") == "unverified" and not row.get("source_ref") for row in enrichment
    )
    unverified_without_ref_rows = [
        row for row in enrichment
        if row.get("evidence_status") == "unverified" and not row.get("source_ref")
    ]
    unverified_with_source_metadata = sum(
        bool(row.get("source_id") or row.get("source_ids") or row.get("source_citations") or row.get("source_urls"))
        for row in unverified_without_ref_rows
    )
    unverified_project_naming = sum(row.get("evidence") == "项目命名" for row in unverified_without_ref_rows)
    unverified_without_evidence_or_source = sum(
        not row.get("evidence") and not row.get("source_id") and not row.get("source_ids")
        and not row.get("source_citations") and not row.get("source_urls")
        for row in unverified_without_ref_rows
    )
    unverified_evidence_text_without_source_metadata = sum(
        bool(row.get("evidence")) and row.get("evidence") != "项目命名"
        and not row.get("source_id") and not row.get("source_ids")
        and not row.get("source_citations") and not row.get("source_urls")
        for row in unverified_without_ref_rows
    )
    unverified_wikidata_evidence_marker = sum(
        "Wikidata" in str(row.get("evidence", ""))
        and not row.get("source_id") and not row.get("source_ids")
        and not row.get("source_citations") and not row.get("source_urls")
        for row in unverified_without_ref_rows
    )
    unverified_other_evidence_without_source_metadata = (
        unverified_evidence_text_without_source_metadata - unverified_wikidata_evidence_marker
    )
    source_citation_cardinality_mismatches = sum(
        bool(row.get("source_citations"))
        and len(row.get("source_ids") or ([row["source_id"]] if row.get("source_id") else []))
        != len(row["source_citations"])
        for row in enrichment
    )
    same_wikidata_ids_by_ku: dict[str, set[str]] = {}
    for row in align_rows:
        if row.get("external_source", "").lower() == "wikidata" and row.get("decision") == "same" and row.get("external_id"):
            same_wikidata_ids_by_ku.setdefault(row.get("ku_id", ""), set()).add(row["external_id"])
    source_rows_by_qid: dict[str, list[dict[str, str]]] = {}
    for row in source_rows:
        source_url = row.get("url", "") or ""
        if row.get("kind") != "external" or "wikidata.org" not in source_url.lower():
            continue
        for qid in set(re.findall(r"\bQ\d+\b", source_url)):
            source_rows_by_qid.setdefault(qid, []).append(row)
    wikidata_property_rows = [
        row for row in unverified_without_ref_rows
        if "Wikidata" in str(row.get("evidence", "")) and re.search(r"\bP\d+\b", str(row.get("evidence", "")))
    ]
    wikidata_property_rows_with_one_alignment = [
        row for row in wikidata_property_rows if len(same_wikidata_ids_by_ku.get(row.get("ku_id", ""), set())) == 1
    ]
    wikidata_rows_linked_to_source_registry = []
    wikidata_qids_linked_to_source_registry: set[str] = set()
    for row in wikidata_property_rows_with_one_alignment:
        qid = next(iter(same_wikidata_ids_by_ku[row.get("ku_id", "")]))
        if source_rows_by_qid.get(qid):
            wikidata_rows_linked_to_source_registry.append(row)
            wikidata_qids_linked_to_source_registry.add(qid)
    duplicate_source_qids = {
        qid for qid in wikidata_qids_linked_to_source_registry
        if len(source_rows_by_qid[qid]) > 1
    }
    same_revision_duplicate_qids = set()
    differing_revision_duplicate_qids = set()
    for qid in duplicate_source_qids:
        revisions = {
            match.group(1)
            for row in source_rows_by_qid[qid]
            if (match := re.search(r"revision\s+(\d+)", row.get("label", "")))
        }
        if len(revisions) == 1:
            same_revision_duplicate_qids.add(qid)
        else:
            differing_revision_duplicate_qids.add(qid)
    wikidata_source_candidate_rows = []
    for row in wikidata_property_rows:
        aligned_qids = same_wikidata_ids_by_ku.get(row.get("ku_id", ""), set())
        qid = next(iter(aligned_qids)) if len(aligned_qids) == 1 else ""
        matches = source_rows_by_qid.get(qid, []) if qid else []
        pointer_status = (
            "candidate_sources_ambiguous" if len(matches) > 1
            else "one_candidate_source" if len(matches) == 1
            else "no_source_record" if qid
            else "no_unique_same_alignment"
        )
        wikidata_source_candidate_rows.append({
            "enrichment_id": row.get("enrichment_id", ""),
            "ku_id": row.get("ku_id", ""),
            "field": row.get("field", ""),
            "value": row.get("value", ""),
            "wikidata_qid": qid,
            "candidate_source_ids": ";".join(source.get("source_id", "") for source in matches),
            "candidate_revisions": ";".join(
                (match.group(1) if (match := re.search(r"revision\s+(\d+)", source.get("label", ""))) else "")
                for source in matches
            ),
            "candidate_accessed_dates": ";".join(
                (match.group(1) if (match := re.search(r"Accessed (\d{4}-\d{2}-\d{2})", source.get("label", ""))) else "")
                for source in matches
            ),
            "candidate_urls": ";".join(source.get("url", "") for source in matches),
            "pointer_status": pointer_status,
            "evidence_marker": row.get("evidence", ""),
        })
    candidate_source_fields = [
        "enrichment_id", "ku_id", "field", "value", "wikidata_qid", "candidate_source_ids",
        "candidate_revisions", "candidate_accessed_dates", "candidate_urls", "pointer_status", "evidence_marker",
    ]
    files["wikidata-source-candidates.csv"] = csv_text(candidate_source_fields, wikidata_source_candidate_rows)
    unresolved_source_refs = sum(bool(row.get("source_ref")) and not row.get("source_ids") for row in enrichment)
    metadata = {
        "dataset_title": "Patrons and Painters Entity and Relation Tables",
        "version": "0.2-draft",
        "created": date.today().isoformat(),
        "publication_status": "draft; not for public distribution",
        "creators": [],
        "identifier": None,
        "rights_review": "pending",
        "license": None,
        "license_status": "undetermined; rights review required before distribution",
        "citation": None,
        "citation_status": "incomplete; creators, persistent identifier, and final version are not supplied",
        "description": "Research tables for knowledge units, candidates, identity alignments, field evidence, S2 source mentions and claims, sources, and relations.",
        "counts": {
            "entities": len(ku_rows), "entity_candidates": entity_candidates,
            "alignment_records": len(align_rows), "alignment_records_without_candidate": unresolved_alignment,
            "enrichment_rows": len(enrichment), "enrichment_unverified": unverified_enrichment,
            "relations": len(rel_rows), "formal_relations": formal_relations,
            "pending_relations": pending_relations, "sources": len(source_rows),
            "source_segments": len(portable_segments),
            "s2_coverage_rows": len(coverage_rows),
            "s2_migrated_segments": complete_reviewed_segments,
            "s2_partial_segments": partial_reviewed_segments, "s2_pending_segments": pending_reviewed_segments,
            "s2_mentions_rows": len(mention_rows), "s2_statement_rows": len(statement_rows),
            "portable_reference_rows": len(portable_refs),
            "portable_entity_references": sum(row["target_type"] == "entity" for row in portable_refs),
            "portable_processing_references": sum(row["target_type"] == "processing_record" for row in portable_refs),
            "enrichment_citation_links": len(citation_links),
            "enrichment_citations_resolved_unique": sum(row["resolution_status"] == "resolved_unique" for row in citation_links),
            "enrichment_citations_resolved_exact": sum(row["match_method"] == "normalized_exact_citation" and row["resolution_status"] == "resolved_unique" for row in citation_links),
            "enrichment_citations_resolved_by_work_identity": sum(row["match_method"] == "work_author_title_year" and row["resolution_status"] == "resolved_unique" for row in citation_links),
            "enrichment_citations_ambiguous": sum(row["resolution_status"] == "ambiguous" for row in citation_links),
            "enrichment_citations_without_deterministic_match": sum(row["resolution_status"] == "no_exact_match" for row in citation_links),
        },
        "provenance_diagnostics": {
            "unverified_empty_source_ref": unverified_without_source_ref,
            "with_source_id_citation_or_url": unverified_with_source_metadata,
            "project_naming_evidence_label": unverified_project_naming,
            "wikidata_evidence_marker_without_source_metadata": unverified_wikidata_evidence_marker,
            "other_nonempty_evidence_without_source_metadata": unverified_other_evidence_without_source_metadata,
            "without_evidence_text_or_structured_source_metadata": unverified_without_evidence_or_source,
            "wikidata_property_rows": len(wikidata_property_rows),
            "wikidata_property_rows_with_unique_same_alignment_and_source_record": len(wikidata_rows_linked_to_source_registry),
            "wikidata_property_qids_with_multiple_source_records": len(duplicate_source_qids),
            "wikidata_property_qids_with_duplicate_records_same_revision": len(same_revision_duplicate_qids),
            "wikidata_property_qids_with_duplicate_records_different_revisions": len(differing_revision_duplicate_qids),
            "wikidata_property_rows_without_unique_same_alignment_or_source_record": len(wikidata_property_rows) - len(wikidata_rows_linked_to_source_registry),
            "wikidata_source_candidate_rows": len(wikidata_source_candidate_rows),
            "source_citation_cardinality_mismatches": source_citation_cardinality_mismatches,
            "interpretation": "These disjoint field-presence buckets are diagnostic; they may represent editorial metadata or unresolved research and do not determine factual support or verification.",
        },
        "known_gaps": [
            f"S2 migration status: {complete_reviewed_segments} reviewed segments complete, {partial_reviewed_segments} partial, and {pending_reviewed_segments} pending ({len(mention_rows)} mentions; {len(statement_rows)} book statements). This is not an independent recall or accuracy estimate. Source segment text is not packaged; source rights remain unresolved.",
            "Alignment identities are restored from the retained evidence JSONL; 25 recorded same/QID outcomes were recovered, while 12 originally unpaired rows remain undecided.",
            f"{unverified_without_source_ref} unverified enrichment rows have an empty source_ref. Disjoint field-presence buckets find {unverified_with_source_metadata} with source IDs/citations/URLs, {unverified_project_naming} labelled as project naming, {unverified_wikidata_evidence_marker} with a Wikidata-related evidence marker but no structured source metadata, {unverified_other_evidence_without_source_metadata} with other evidence text but no structured source metadata, and {unverified_without_evidence_or_source} with neither evidence text nor structured source metadata; these are not semantic classifications. {unresolved_source_refs} retained source_ref values do not map to a card source record.",
            f"Of the Wikidata-marked rows, {len(wikidata_property_rows)} are property-like rows; {len(wikidata_rows_linked_to_source_registry)} map through a unique same-QID alignment to {len(wikidata_qids_linked_to_source_registry)} QIDs in the source registry, but each of those QIDs has multiple source records. {len(same_revision_duplicate_qids)} duplicate-QID groups have one recorded revision and {len(differing_revision_duplicate_qids)} have differing revisions. The wikidata-source-candidates.csv file preserves these review leads, but they are unresolved provenance pointers, not evidence that property values are verified; no source ID was assigned automatically.",
            "A stratified blind review in an isolated Codex context covered 9 segments and cross-checked 363 existing mentions and 69 statements; four high-confidence errors were corrected. This is not formal human acceptance and does not estimate chapter-level precision or recall.",
            "A deterministic surface scan over 27 migrated segments found 13 unmatched typed candidate labels; all 13 were reviewed and linked to existing candidates. The scan cannot identify unlisted entities, validate identity mappings, or estimate semantic recall.",
            f"{len(portable_refs)} relative Markdown links in enrichment fields are mapped in portable-references.csv; entity targets use stable KU IDs, while {sum(row['target_type'] == 'processing_record' for row in portable_refs)} processing-record links point to files not included in the package.",
            f"{source_citation_cardinality_mismatches} enrichment rows have different counts of structured source IDs and citation strings. These fields are preserved independently; array position is not a source-to-citation mapping.",
            f"enrichment-citation-links.csv contains {len(citation_links)} citation occurrences: {sum(row['match_method'] == 'normalized_exact_citation' and row['resolution_status'] == 'resolved_unique' for row in citation_links)} normalized exact-text matches, {sum(row['match_method'] == 'work_author_title_year' and row['resolution_status'] == 'resolved_unique' for row in citation_links)} strict author-title-year identity matches, {sum(row['resolution_status'] == 'ambiguous' for row in citation_links)} ambiguous, and {sum(row['resolution_status'] == 'no_exact_match' for row in citation_links)} without a deterministic match. Bibliographic matching does not verify factual support.",
            "Data and third-party source rights, license, author, and persistent citation are not yet established.",
        ],
    }
    files["metadata.json"] = json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
    files["README.md"] = f"""# {metadata['dataset_title']} ({metadata['version']})

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
"""
    files["rights-review.md"] = f"""# Rights and citation review (unresolved)

This checklist records release dependencies; it is not a legal determination. No license is asserted for the dataset, source excerpts, third-party metadata, or repository code.

| Component | Material present in {metadata['version']} | Current status | Required before public release |
|---|---|---|---|
| Source assets | Basenames, line ranges, and hashes in `segments.csv`; source segment text is omitted | Rights and access terms not reviewed | Confirm redistribution and access terms for each included or required source asset |
| Book-derived statements | {len(statement_rows)} claims with original quotation excerpts and locators in `book-statements.jsonl` | Third-party quotation rights unresolved | Review quotation permissions/limits and decide whether to retain, redact, or replace excerpts |
| Entity fields and relations | Structured facts, concise prose, citations, URLs, and original table cell text | Source-by-source rights review incomplete; factual accuracy is not a rights determination | Review third-party record terms and distinguish project-authored text from sourced expression |
| Bibliographic/source registry | {len(source_rows)} source records with citations and URLs | Terms of service and metadata reuse not reviewed | Check source/database reuse conditions and preserve attribution requirements |
| Software | `example_query.py` and project export/validation code | No software license identified | Select and apply a separate code license if the code will be redistributed |
| Attribution and citation | Dataset creator list is empty; persistent identifier and final citation are null | Incomplete | Confirm creator/affiliation metadata, freeze a release version, deposit it in a suitable repository, and create the final citation |

**Release gate:** keep this package private until the project owner confirms creator metadata and the applicable rights/attribution decisions. Do not replace `license: null` or the draft status with a guessed license or identifier.
"""
    files["schema.md"] = """# Data dictionary (draft)

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
"""
    files["validation-report.md"] = f"""# Validation report ({metadata['version']})

## Mechanical checks

- Current tables: 1,019 entities; {entity_candidates:,} candidates; {len(align_rows)} alignment rows; {len(enrichment):,} enrichment rows; {len(rel_rows):,} relations; {len(source_rows):,} sources.
- S2 coverage ledger: {len(coverage_rows)} segment dispositions; {complete_reviewed_segments} reviewed segment(s) complete, {partial_reviewed_segments} partial, and {pending_reviewed_segments} pending; the package includes {len(mention_rows)} mention rows and {len(statement_rows)} statement rows.
- Formal relations: {formal_relations:,}; pending relations: {pending_relations}.
- Unverified enrichment rows: {unverified_enrichment:,}.
- Among unverified rows with empty `source_ref`, {unverified_with_source_metadata} retain source IDs/citations/URLs in other fields; {unverified_project_naming} carry the `项目命名` evidence label; {unverified_wikidata_evidence_marker} have a Wikidata-related evidence marker but no structured source metadata; {unverified_other_evidence_without_source_metadata} have other evidence text but no structured source metadata; {unverified_without_evidence_or_source} contain neither evidence text nor structured source metadata. These disjoint field-presence buckets are not semantic classifications.
- Wikidata provenance diagnostic: {len(wikidata_property_rows)} unverified rows have a property-like Wikidata marker; {len(wikidata_rows_linked_to_source_registry)} map through a unique `same` QID alignment to {len(wikidata_qids_linked_to_source_registry)} QIDs in `sources.csv`, but each QID has multiple source records ({len(same_revision_duplicate_qids)} groups with one recorded revision; {len(differing_revision_duplicate_qids)} with differing revisions). No source ID was assigned automatically.
- `wikidata-source-candidates.csv` contains {len(wikidata_source_candidate_rows)} review-only rows. Candidate QIDs and source records are identity-based pointers, not property evidence or factual verification.
- Alignment rows without a candidate ID: {unresolved_alignment}.
- Portable references: {len(portable_refs)} relative Markdown link occurrences mapped; {sum(row['target_type'] == 'entity' for row in portable_refs)} entity targets use KU IDs and {sum(row['target_type'] == 'processing_record' for row in portable_refs)} processing-note targets are not bundled.
- `audit_tables.py --summary`: no structural errors; unresolved rows are reported as warnings.
- `audit_tables.py --strict-stage --summary`: no structural or migration errors. It reports two unresolved source markers as warnings; complete migration does not establish semantic recall or independent claim accuracy.
- {source_citation_cardinality_mismatches} enrichment rows have unequal counts of structured source IDs and citation strings. These fields are preserved independently; no one-to-one mapping is inferred from array positions.
- `enrichment-citation-links.csv`: {len(citation_links)} citation occurrences; {sum(row['match_method'] == 'normalized_exact_citation' and row['resolution_status'] == 'resolved_unique' for row in citation_links)} normalized exact-text matches, {sum(row['match_method'] == 'work_author_title_year' and row['resolution_status'] == 'resolved_unique' for row in citation_links)} strict author-title-year identity matches, {sum(row['resolution_status'] == 'ambiguous' for row in citation_links)} ambiguous matches, and {sum(row['resolution_status'] == 'no_exact_match' for row in citation_links)} without a deterministic source-record match. These are bibliographic links, not evidence verification.
- `build_cards.py --check`: post-render full preflight on 2026-09-26 reported zero files to write across all 1,019 cards; the CSV-backed card views match the current structured tables.
- The table audit independently re-scans card Markdown: 2,608 tables and 10,149 rows match the exported source cells and layout metadata exactly.

## Known unresolved issues

- The coverage ledger does not establish sentence-level entity recall or independent claim-level accuracy. Source segment text is omitted, and quote redistribution rights are unresolved.
- A read-only exact-surface scan of typed candidate labels found 13 uncovered spans across the 27 migrated segments; these were manually reviewed and added as mentions. This scan only finds names already present in the candidate table, so it cannot establish candidate recall, identity accuracy, or overall semantic quality.
- All 335 alignment rows link to a KU and candidate. Twenty-five same/QID outcomes are directly restored from retained evidence; 12 originally unpaired rows remain undecided.
- {unverified_enrichment:,} enrichment rows remain unverified; {unverified_without_source_ref:,} have an empty `source_ref`. See the provenance diagnostic above before interpreting an empty locator as absent evidence. {unresolved_source_refs} retained source markers do not resolve to a source record.
- Wikidata identity alignment does not verify the aligned entity's property values. The property-like row matches above remain without an unambiguous version-level source pointer; source-record duplicates are referenced and have not been merged.
- A stratified blind review in an isolated Codex context covered 9 segments and cross-checked 363 existing mentions and 69 statements; four high-confidence errors were corrected. This is not formal human acceptance and does not estimate chapter-level precision or recall. Rights review, license, author metadata, DOI, and final citation remain unresolved.
- No representative extraction-throughput benchmark was recorded during the original semantic processing; wall time for mechanical audit/render checks is not an extraction-speed estimate.

## Local runtime observation

Five consecutive warm-cache runs on Windows 11 with Python 3.14.4 (2026-09-26), including process startup: S0 segment preview, 62 files/953 segments, median 0.166 s (range 0.164–0.173); S1 candidate preview, 2,930 index rows/3,593 candidates, median 0.132 s (0.125–0.146); S5 field-table preview, 1,019 cards/10,149 rows, median 3.358 s (3.182–3.517); strict-stage table audit, median 1.271 s (1.176–1.346); full render preflight, 1,019 cards, median 4.403 s (4.017–4.913); dataset export preview, median 0.719 s (0.719–0.751). Commands ran sequentially and read-only. These machine-specific observations measure parsing, reconciliation, validation, and serialization; they do not measure model reasoning or semantic extraction throughput and are not a before/after speedup claim.

This report establishes portability and mechanical table integrity only. It does not establish extraction precision, recall, factual accuracy, or publication readiness.
"""
    files["example_query.py"] = '''#!/usr/bin/env python3
import argparse
import csv
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description="Query one entity from this dataset package.")
parser.add_argument("ku_id", nargs="?", default="units/persons/guercino")
parser.add_argument("--full", action="store_true", help="include complete evidence and relation rows")
args = parser.parse_args()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def read_csv(name):
    with (root / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

entity = next((r for r in read_csv("entities.csv") if r["ku_id"] == args.ku_id), None)
if entity is None:
    raise SystemExit(f"Unknown ku_id: {args.ku_id}")
enrichment = [json.loads(line) for line in (root / "enrichment.jsonl").read_text(encoding="utf-8").splitlines() if line]
relations = read_csv("relations.csv")
fields = [r for r in enrichment if r["ku_id"] == args.ku_id]
field_ids = {r["enrichment_id"] for r in fields}
references = [r for r in read_csv("portable-references.csv") if r["enrichment_id"] in field_ids]
outgoing = [r for r in relations if r["subject_ku_id"] == args.ku_id]
incoming = [r for r in relations if r["object_ku_id"] == args.ku_id]
if args.full:
    result = {"entity": entity, "fields": fields, "portable_references": references,
              "outgoing_relations": outgoing, "incoming_relations": incoming}
else:
    field_sample = fields[:5]
    result = {
        "entity": entity,
        "field_count": len(fields),
        "fields_sample": [{key: row.get(key, "") for key in ("field", "value", "evidence_status", "source_ref")} for row in field_sample],
        "fields_omitted": max(0, len(fields) - len(field_sample)),
        "portable_reference_count": len(references),
        "portable_references_sample": references[:5],
        "portable_references_omitted": max(0, len(references) - 5),
        "outgoing_relations": [{key: row.get(key, "") for key in ("relation_id", "object_ku_id", "predicate", "status", "source_id")} for row in outgoing],
        "incoming_relations": [{key: row.get(key, "") for key in ("relation_id", "subject_ku_id", "predicate", "status", "source_id")} for row in incoming],
    }
print(json.dumps(result, ensure_ascii=False, indent=2))
'''
    return files, metadata


def validate_package(files: dict[str, str]) -> list[str]:
    def table(name: str) -> list[dict[str, str]]:
        return list(csv.DictReader(io.StringIO(files[name], newline="")))

    entities = table("entities.csv")
    entity_ids = {row["ku_id"] for row in entities}
    candidates = table("entity-candidates.csv")
    candidate_ids = {row["candidate_id"] for row in candidates}
    coverage = table("s2-coverage.csv")
    coverage_by_segment = {row.get("segment_id", ""): row for row in coverage}
    segments = table("segments.csv")
    segment_ids = {row["segment_id"] for row in segments}
    alignments = table("alignment.csv")
    relations = table("relations.csv")
    sources = table("sources.csv")
    source_ids = {row["source_id"] for row in sources}
    enrichments = [json.loads(line) for line in files["enrichment.jsonl"].splitlines() if line.strip()]
    errors: list[str] = []
    if len(entity_ids) != len(entities): errors.append("duplicate entity ku_id")
    if len(candidate_ids) != len(candidates): errors.append("duplicate candidate_id")
    if len(segment_ids) != len(segments): errors.append("duplicate segment_id")
    for row in coverage:
        if row.get("segment_id") not in segment_ids:
            errors.append(f"{row.get('segment_id')}: coverage has no segment manifest row")
    for row in candidates:
        ref = row.get("candidate_source_ref", "")
        origin = row.get("candidate_origin", "")
        if origin == "accepted-ku":
            if ref and ref not in entity_ids:
                errors.append(f"{row['candidate_id']}: unresolved accepted-KU candidate_source_ref")
        elif origin == "body-mention":
            match = re.fullmatch(r"(.+)#L(\d+)", ref)
            if not match or match.group(1) not in coverage_by_segment:
                errors.append(f"{row['candidate_id']}: unresolved body-mention source reference")
            else:
                segment_id, line = match.group(1), int(match.group(2))
                coverage_row = coverage_by_segment[segment_id]
                ranges = [(int(a), int(z)) for a, z in re.findall(r"L(\d+)-(\d+)", coverage_row.get("source_line_ranges", ""))]
                if coverage_row.get("disposition") != "reviewed" or not any(start <= line <= end for start, end in ranges):
                    errors.append(f"{row['candidate_id']}: body-mention line is outside reviewed source coverage")
        elif ref:
            errors.append(f"{row['candidate_id']}: candidate_source_ref has no supported candidate_origin")
    for row in alignments:
        if row.get("candidate_id") and row["candidate_id"] not in candidate_ids:
            errors.append(f"{row['alignment_id']}: unresolved candidate_id")
        if row.get("ku_id") and row["ku_id"] not in entity_ids:
            errors.append(f"{row['alignment_id']}: unresolved ku_id")
    for row in relations:
        if row["subject_ku_id"] not in entity_ids or row["object_ku_id"] not in entity_ids:
            errors.append(f"{row['relation_id']}: unresolved relation endpoint")
        if row.get("source_id") and row["source_id"] not in source_ids:
            errors.append(f"{row['relation_id']}: unresolved source_id")
    for row in enrichments:
        if row.get("ku_id") not in entity_ids:
            errors.append(f"{row.get('enrichment_id')}: unresolved ku_id")
        if any(source_id not in source_ids for source_id in row.get("source_ids", [])):
            errors.append(f"{row.get('enrichment_id')}: unresolved source_ids")
    if "enrichment-citation-links.csv" not in files:
        errors.append("missing enrichment-citation-links.csv")
    else:
        citation_links = table("enrichment-citation-links.csv")
        citation_keys = [(row.get("enrichment_id", ""), row.get("citation_index", "")) for row in citation_links]
        if len(citation_keys) != len(set(citation_keys)):
            errors.append("duplicate enrichment citation link key")
        if citation_links != source_citation_link_rows(enrichments, sources):
            errors.append("enrichment citation links differ from deterministic citation-to-source matching")
    wikidata_candidates = table("wikidata-source-candidates.csv") if "wikidata-source-candidates.csv" in files else []
    wikidata_candidate_ids = [row.get("enrichment_id", "") for row in wikidata_candidates]
    if len(wikidata_candidate_ids) != len(set(wikidata_candidate_ids)):
        errors.append("duplicate Wikidata source-candidate enrichment_id")
    for row in wikidata_candidates:
        for source_id in filter(None, row.get("candidate_source_ids", "").split(";")):
            if source_id not in source_ids:
                errors.append(f"{row.get('enrichment_id')}: unresolved candidate source_id {source_id}")
    for row in segments:
        if row.get("source_id") and row["source_id"] not in source_ids:
            errors.append(f"{row['segment_id']}: unresolved source_id")
        if row.get("line_start") and int(row["line_start"]) < 1:
            errors.append(f"{row['segment_id']}: invalid line_start")
        if row.get("line_end") and int(row["line_end"]) < int(row.get("line_start", "0")):
            errors.append(f"{row['segment_id']}: invalid line_end")
    mention_rows = table("mentions.csv") if "mentions.csv" in files else []
    mention_ids = [row.get("mention_id", "") for row in mention_rows]
    if len(mention_ids) != len(set(mention_ids)):
        errors.append("duplicate mention_id")
    for row in mention_rows:
        if row.get("segment_id") not in segment_ids:
            errors.append(f"{row.get('mention_id')}: unresolved segment_id")
        if row.get("candidate_id") not in candidate_ids:
            errors.append(f"{row.get('mention_id')}: unresolved candidate_id")
        try:
            if int(row.get("start_char", "")) < 0 or int(row.get("end_char", "")) <= int(row.get("start_char", "")):
                errors.append(f"{row.get('mention_id')}: invalid character offsets")
        except ValueError:
            errors.append(f"{row.get('mention_id')}: invalid character offsets")
    statement_rows = [json.loads(line) for line in files.get("book-statements.jsonl", "").splitlines() if line.strip()]
    statement_ids = [row.get("statement_id", "") for row in statement_rows]
    if len(statement_ids) != len(set(statement_ids)):
        errors.append("duplicate statement_id")
    for row in statement_rows:
        if row.get("segment_id") not in segment_ids:
            errors.append(f"{row.get('statement_id')}: unresolved segment_id")
        if row.get("source_id") and row["source_id"] not in source_ids:
            errors.append(f"{row.get('statement_id')}: unresolved source_id")
        for key in ("subject_candidate_id", "object_candidate_id"):
            if row.get(key) and row[key] not in candidate_ids:
                errors.append(f"{row.get('statement_id')}: unresolved {key}")
    reference_rows = table("portable-references.csv") if "portable-references.csv" in files else []
    reference_ids = [row.get("reference_id", "") for row in reference_rows]
    if len(reference_ids) != len(set(reference_ids)):
        errors.append("duplicate portable reference_id")
    enrichment_by_id = {row.get("enrichment_id", ""): row for row in enrichments}
    for row in reference_rows:
        enrichment_row = enrichment_by_id.get(row.get("enrichment_id", ""))
        if enrichment_row is None:
            errors.append(f"{row.get('reference_id')}: unresolved enrichment_id")
            continue
        if row.get("ku_id") != enrichment_row.get("ku_id"):
            errors.append(f"{row.get('reference_id')}: ku_id disagrees with enrichment row")
        if row.get("target_type") == "entity" and row.get("target_id", "").split("#", 1)[0] not in entity_ids:
            errors.append(f"{row.get('reference_id')}: unresolved portable entity target")
        if row.get("target_type") == "entity" and row.get("resolution_status") != "resolved_entity":
            errors.append(f"{row.get('reference_id')}: invalid entity resolution status")
        if row.get("target_type") == "processing_record" and row.get("resolution_status") != "not_in_package":
            errors.append(f"{row.get('reference_id')}: invalid processing-reference status")
    expected_references = portable_reference_rows(
        enrichments, {ku_id: f"04-knowledge/{ku_id}.md" for ku_id in entity_ids}, entity_ids,
    )
    expected_by_id = {row["reference_id"]: row for row in expected_references}
    actual_by_id = {row.get("reference_id", ""): row for row in reference_rows}
    if set(reference_ids) != set(expected_by_id):
        errors.append("portable reference registry does not cover every relative enrichment link")
    if actual_by_id != expected_by_id:
        errors.append("portable reference registry content differs from source link occurrences")
    for name in ("entities.csv", "entity-candidates.csv", "alignment.csv", "relations.csv", "sources.csv", "segments.csv", "mentions.csv"):
        for row in table(name):
            for value in row.values():
                if value and re.search(r"(^|[\\/])(?:04-knowledge|03-processing|02-sources)[\\/]", value):
                    errors.append(f"{name}: local repository path leaked into package")
                    break
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--apply", action="store_true", help="create release/v0.2-draft once")
    action.add_argument("--update-draft", action="store_true", help="refresh files in an existing draft package")
    args = parser.parse_args()
    files, metadata = build_package()
    errors = validate_package(files)
    if errors:
        raise SystemExit("Draft package validation failed:\n- " + "\n- ".join(errors[:20]))
    print(json.dumps({"directory": str(RELEASE.relative_to(BASE)), "files": list(files), "counts": metadata["counts"],
                      "status": metadata["publication_status"], "license": metadata["license"]}, ensure_ascii=False, indent=2))
    if not args.apply and not args.update_draft:
        print("preview only; pass --apply to create or --update-draft to refresh the draft directory")
        return 0
    if RELEASE.exists() and not args.update_draft:
        raise SystemExit(f"Refusing to overwrite existing draft directory: {RELEASE}")
    if args.update_draft and not RELEASE.is_dir():
        raise SystemExit(f"Draft directory does not exist: {RELEASE}")
    if args.update_draft:
        extras = sorted(path.name for path in RELEASE.iterdir() if path.name not in files)
        if extras:
            raise SystemExit(f"Refusing to update draft with unrelated files present: {extras}")
    RELEASE.mkdir(parents=True, exist_ok=True)
    try:
        for name, content in files.items():
            (RELEASE / name).write_text(content, encoding="utf-8", newline="\n")
    except OSError:
        shutil.rmtree(RELEASE)
        raise
    print(f"{'updated' if args.update_draft else 'created'}={RELEASE.relative_to(BASE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
