import csv
import io
import json

from scripts.export_dataset import build_package, source_citation_link_rows, validate_package


def test_draft_export_includes_portable_s2_evidence_and_current_coverage_state():
    files, metadata = build_package()

    assert validate_package(files) == []
    assert "s2-coverage.csv" in files
    assert "segments.csv" in files
    assert "mentions.csv" in files
    assert "book-statements.jsonl" in files
    assert "wikidata-source-candidates.csv" in files
    assert "portable-references.csv" in files
    assert "enrichment-citation-links.csv" in files
    assert "rights-review.md" in files
    coverage = list(csv.DictReader(io.StringIO(files["s2-coverage.csv"])))
    expected_coverage_counts = {
        "s2_migrated_segments": sum(row["disposition"] == "reviewed" and row["migration_status"] == "complete" for row in coverage),
        "s2_partial_segments": sum(row["disposition"] == "reviewed" and row["migration_status"] == "partial" for row in coverage),
        "s2_pending_segments": sum(row["disposition"] == "reviewed" and row["migration_status"] == "pending" for row in coverage),
        "s2_queued_segments": sum(row["disposition"] == "queued" for row in coverage),
    }
    for key, expected in expected_coverage_counts.items():
        assert metadata["counts"][key] == expected
    assert metadata["counts"]["s2_coverage_rows"] == len(coverage) == metadata["counts"]["source_segments"]
    assert metadata["counts"]["s2_mentions_rows"] == len(list(csv.DictReader(io.StringIO(files["mentions.csv"]))))
    assert metadata["counts"]["s2_statement_rows"] == sum(bool(line) for line in files["book-statements.jsonl"].splitlines())
    assert metadata["counts"]["portable_reference_rows"] > 0
    assert metadata["counts"]["portable_entity_references"] > 0
    assert metadata["counts"]["portable_processing_references"] > 0
    enrichment_rows = [
        json.loads(line) for line in files["enrichment.jsonl"].splitlines() if line
    ]
    unverified_without_ref = [
        row for row in enrichment_rows
        if row.get("evidence_status") == "unverified" and not row.get("source_ref")
    ]
    def has_source_metadata(row):
        return any((
            row.get("source_id"), row.get("source_ids"), row.get("source_citations"), row.get("source_urls")
        ))

    evidence_text_without_source = [
        row for row in unverified_without_ref
        if row.get("evidence") and row.get("evidence") != "项目命名" and not has_source_metadata(row)
    ]
    wikidata_markers = [row for row in evidence_text_without_source if "Wikidata" in str(row.get("evidence", ""))]
    expected_provenance_counts = {
        "unverified_empty_source_ref": len(unverified_without_ref),
        "with_source_id_citation_or_url": sum(has_source_metadata(row) for row in unverified_without_ref),
        "project_naming_evidence_label": sum(row.get("evidence") == "项目命名" for row in unverified_without_ref),
        "wikidata_evidence_marker_without_source_metadata": len(wikidata_markers),
        "other_nonempty_evidence_without_source_metadata": len(evidence_text_without_source) - len(wikidata_markers),
        "without_evidence_text_or_structured_source_metadata": sum(
            not row.get("evidence") and not has_source_metadata(row) for row in unverified_without_ref
        ),
        "source_citation_cardinality_mismatches": sum(
            bool(row.get("source_citations"))
            and len(row.get("source_ids") or ([row["source_id"]] if row.get("source_id") else []))
            != len(row["source_citations"])
            for row in enrichment_rows
        ),
    }
    source_candidates = list(csv.DictReader(io.StringIO(files["wikidata-source-candidates.csv"])))
    ambiguous = [row for row in source_candidates if row["pointer_status"] == "candidate_sources_ambiguous"]
    no_unique_record = [
        row for row in source_candidates
        if row["pointer_status"] in {"no_unique_same_alignment", "no_source_record"}
    ]
    linked_to_source = [
        row for row in source_candidates
        if row["pointer_status"] in {"candidate_sources_ambiguous", "one_candidate_source"}
    ]
    multiple_source_qids = {}
    for row in ambiguous:
        multiple_source_qids[row["wikidata_qid"]] = row["candidate_revisions"].split(";")
    same_revision_qids = sum(
        len({revision for revision in revisions if revision}) == 1
        for revisions in multiple_source_qids.values()
    )
    expected_provenance_counts.update({
        "wikidata_property_rows": len(source_candidates),
        "wikidata_property_rows_with_unique_same_alignment_and_source_record": len(linked_to_source),
        "wikidata_property_qids_with_multiple_source_records": len(multiple_source_qids),
        "wikidata_property_qids_with_duplicate_records_same_revision": same_revision_qids,
        "wikidata_property_qids_with_duplicate_records_different_revisions": len(multiple_source_qids) - same_revision_qids,
        "wikidata_property_rows_without_unique_same_alignment_or_source_record": len(no_unique_record),
        "wikidata_source_candidate_rows": len(source_candidates),
    })
    for key, expected in expected_provenance_counts.items():
        assert metadata["provenance_diagnostics"][key] == expected
    citation_links = list(csv.DictReader(io.StringIO(files["enrichment-citation-links.csv"])))
    expected_citation_counts = {
        "enrichment_citation_links": len(citation_links),
        "enrichment_citations_resolved_unique": sum(row["resolution_status"] == "resolved_unique" for row in citation_links),
        "enrichment_citations_resolved_exact": sum(
            row["match_method"] == "normalized_exact_citation" and row["resolution_status"] == "resolved_unique"
            for row in citation_links
        ),
        "enrichment_citations_resolved_by_work_identity": sum(
            row["match_method"] == "work_author_title_year" and row["resolution_status"] == "resolved_unique"
            for row in citation_links
        ),
        "enrichment_citations_ambiguous": sum(row["resolution_status"] == "ambiguous" for row in citation_links),
        "enrichment_citations_without_deterministic_match": sum(
            row["resolution_status"] == "no_exact_match" for row in citation_links
        ),
    }
    for key, expected in expected_citation_counts.items():
        assert metadata["counts"][key] == expected
    assert sum(metadata["provenance_diagnostics"][key] for key in (
        "with_source_id_citation_or_url",
        "project_naming_evidence_label",
        "wikidata_evidence_marker_without_source_metadata",
        "other_nonempty_evidence_without_source_metadata",
        "without_evidence_text_or_structured_source_metadata",
    )) == metadata["provenance_diagnostics"]["unverified_empty_source_ref"]
    assert "not an independent recall or accuracy estimate" in metadata["known_gaps"][0]
    assert "no source ID was assigned automatically" in metadata["known_gaps"][3]
    assert any("unmatched typed candidate labels" in gap for gap in metadata["known_gaps"])

    assert all(len(row["candidate_source_ids"].split(";")) > 1 for row in ambiguous)

    statements = [line for line in files["book-statements.jsonl"].splitlines() if line]
    assert len(statements) == metadata["counts"]["s2_statement_rows"]
    assert '"source_asset":"01_CHP-1.md"' in statements[0]
    assert "source_file" not in statements[0]
    assert "04-knowledge" not in files["segments.csv"]
    assert "zero files to write across all 1,019 cards" in files["validation-report.md"]
    assert "differs from the CSV-backed preview" not in files["validation-report.md"]
    assert "--full" in files["example_query.py"]
    assert '"fields_omitted"' in files["example_query.py"]
    assert 'read_csv("portable-references.csv")' in files["example_query.py"]
    assert "No license is asserted" in files["rights-review.md"]
    assert "Do not replace `license: null`" in files["rights-review.md"]
    assert "Five consecutive warm-cache runs" in files["validation-report.md"]
    assert "not a before/after speedup claim" in files["validation-report.md"]
    assert "no one-to-one mapping is inferred from array positions" in files["validation-report.md"]
    assert "no positional mapping between the arrays is guaranteed" in files["README.md"]
    assert "Bibliographic matching is not factual verification" in files["schema.md"]
    assert "narrow work-identity rule" in files["README.md"]


def test_export_validator_requires_one_coverage_disposition_per_segment():
    files, _ = build_package()
    coverage_lines = files["s2-coverage.csv"].splitlines()
    files["s2-coverage.csv"] = "\n".join(coverage_lines[:-1]) + "\n"

    errors = validate_package(files)

    assert "S2 coverage does not dispose every canonical source segment" in errors


def test_portable_reference_registry_must_cover_every_relative_enrichment_link():
    files, _ = build_package()
    lines = files["portable-references.csv"].splitlines()
    assert len(lines) > 2
    files["portable-references.csv"] = "\n".join(lines[:-1]) + "\n"

    errors = validate_package(files)

    assert "portable reference registry does not cover every relative enrichment link" in errors


def test_portable_reference_registry_must_preserve_exact_target_mapping():
    files, _ = build_package()
    rows = list(csv.DictReader(io.StringIO(files["portable-references.csv"])))
    rows[0]["target_id"] = "units/persons/wrong-target"
    fields = list(rows[0])
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    files["portable-references.csv"] = output.getvalue()

    errors = validate_package(files)

    assert "portable reference registry content differs from source link occurrences" in errors


def test_enrichment_citation_links_must_match_deterministic_source_mapping():
    files, _ = build_package()
    rows = list(csv.DictReader(io.StringIO(files["enrichment-citation-links.csv"])))
    assert rows
    assert any(row["resolution_status"] == "resolved_unique" for row in rows)
    anthology_url_citation = next(
        row for row in rows if row["enrichment_id"] == "enr-00215" and row["citation_index"] == "0"
    )
    assert anthology_url_citation["resolution_status"] == "no_exact_match"
    assert anthology_url_citation["source_id"] == ""
    rows[0]["source_id"] = "invented-source-id"
    fields = list(rows[0])
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    files["enrichment-citation-links.csv"] = output.getvalue()

    errors = validate_package(files)

    assert "enrichment citation links differ from deterministic citation-to-source matching" in errors


def test_work_identity_match_requires_a_unique_source_record():
    enrichment = [{
        "enrichment_id": "enr-test",
        "ku_id": "units/archives/test",
        "source_citations": [
            "Francis Haskell, Patrons and Painters, revised edition, Yale University Press, 1980, p. 9."
        ],
    }]
    sources = [
        {"source_id": "haskell-1980-rev-ed", "label": "Francis Haskell, Patrons and Painters (1980)."},
        {"source_id": "duplicate-haskell-record", "label": "Haskell, Patrons and Painters, 1980 edition."},
    ]

    links = source_citation_link_rows(enrichment, sources)

    assert links == [{
        "enrichment_id": "enr-test",
        "ku_id": "units/archives/test",
        "citation_index": "0",
        "source_id": "",
        "candidate_source_ids": "duplicate-haskell-record;haskell-1980-rev-ed",
        "match_method": "work_author_title_year",
        "resolution_status": "ambiguous",
    }]

