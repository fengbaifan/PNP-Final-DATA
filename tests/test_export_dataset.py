import csv
import io

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
    assert metadata["counts"]["s2_migrated_segments"] == 27
    assert metadata["counts"]["s2_partial_segments"] == 0
    assert metadata["counts"]["s2_pending_segments"] == 0
    assert metadata["counts"]["s2_mentions_rows"] == 665
    assert metadata["counts"]["s2_statement_rows"] == 172
    assert metadata["counts"]["portable_reference_rows"] > 0
    assert metadata["counts"]["portable_entity_references"] > 0
    assert metadata["counts"]["portable_processing_references"] > 0
    assert metadata["provenance_diagnostics"]["unverified_empty_source_ref"] == 1499
    assert metadata["provenance_diagnostics"]["with_source_id_citation_or_url"] == 83
    assert metadata["provenance_diagnostics"]["project_naming_evidence_label"] == 464
    assert metadata["provenance_diagnostics"]["wikidata_evidence_marker_without_source_metadata"] == 469
    assert metadata["provenance_diagnostics"]["other_nonempty_evidence_without_source_metadata"] == 377
    assert metadata["provenance_diagnostics"]["without_evidence_text_or_structured_source_metadata"] == 106
    assert metadata["provenance_diagnostics"]["wikidata_property_rows"] == 465
    assert metadata["provenance_diagnostics"]["wikidata_property_rows_with_unique_same_alignment_and_source_record"] == 403
    assert metadata["provenance_diagnostics"]["wikidata_property_qids_with_multiple_source_records"] == 52
    assert metadata["provenance_diagnostics"]["wikidata_property_qids_with_duplicate_records_same_revision"] == 44
    assert metadata["provenance_diagnostics"]["wikidata_property_qids_with_duplicate_records_different_revisions"] == 8
    assert metadata["provenance_diagnostics"]["wikidata_property_rows_without_unique_same_alignment_or_source_record"] == 62
    assert metadata["provenance_diagnostics"]["wikidata_source_candidate_rows"] == 465
    assert metadata["provenance_diagnostics"]["source_citation_cardinality_mismatches"] == 138
    assert metadata["counts"]["enrichment_citation_links"] == 12254
    assert metadata["counts"]["enrichment_citations_resolved_unique"] == 12201
    assert metadata["counts"]["enrichment_citations_resolved_exact"] == 9328
    assert metadata["counts"]["enrichment_citations_resolved_by_work_identity"] == 2873
    assert metadata["counts"]["enrichment_citations_ambiguous"] == 0
    assert metadata["counts"]["enrichment_citations_without_deterministic_match"] == 53
    assert sum(metadata["provenance_diagnostics"][key] for key in (
        "with_source_id_citation_or_url",
        "project_naming_evidence_label",
        "wikidata_evidence_marker_without_source_metadata",
        "other_nonempty_evidence_without_source_metadata",
        "without_evidence_text_or_structured_source_metadata",
    )) == metadata["provenance_diagnostics"]["unverified_empty_source_ref"]
    assert "not an independent recall or accuracy estimate" in metadata["known_gaps"][0]
    assert "no source ID was assigned automatically" in metadata["known_gaps"][3]
    assert any("13 unmatched typed candidate labels" in gap for gap in metadata["known_gaps"])

    source_candidates = list(csv.DictReader(io.StringIO(files["wikidata-source-candidates.csv"])))
    assert len(source_candidates) == 465
    assert sum(row["pointer_status"] == "candidate_sources_ambiguous" for row in source_candidates) == 403
    assert sum(row["pointer_status"] == "no_unique_same_alignment" for row in source_candidates) == 62
    ambiguous = [row for row in source_candidates if row["pointer_status"] == "candidate_sources_ambiguous"]
    assert len({row["wikidata_qid"] for row in ambiguous}) == 52
    assert all(len(row["candidate_source_ids"].split(";")) == 2 for row in ambiguous)

    statements = [line for line in files["book-statements.jsonl"].splitlines() if line]
    assert len(statements) == 172
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
    assert sum(row["match_method"] == "work_author_title_year" and row["resolution_status"] == "resolved_unique" for row in rows) == 2873
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

