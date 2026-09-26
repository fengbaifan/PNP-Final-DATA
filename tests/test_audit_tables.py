import csv
import json

from scripts import audit_tables as table_audit
from scripts.audit_tables import audit_s2_artifacts


def test_full_table_audit_rejects_missing_primary_key(monkeypatch):
    original_read_csv = table_audit.read_csv

    def read_with_missing_candidate_id(path):
        rows = original_read_csv(path)
        if path.name == "entity-candidates.csv":
            rows[0]["candidate_id"] = ""
        return rows

    monkeypatch.setattr(table_audit, "read_csv", read_with_missing_candidate_id)
    result = table_audit.audit_tables(strict_stage=True)

    assert any("entity-candidates.csv has duplicate/missing candidate_id" in error for error in result["errors"])


def test_full_table_audit_rejects_duplicate_enrichment_occurrence_id(monkeypatch):
    original_read_jsonl = table_audit.read_jsonl

    def read_with_duplicate_occurrence_id(path):
        rows = original_read_jsonl(path)
        if path.name == "enrichment.jsonl":
            rows[1]["occurrence_id"] = rows[0]["occurrence_id"]
        return rows

    monkeypatch.setattr(table_audit, "read_jsonl", read_with_duplicate_occurrence_id)
    result = table_audit.audit_tables(strict_stage=True)

    assert "enrichment.jsonl has duplicate occurrence_id" in result["errors"]


def test_full_table_audit_rejects_source_asset_hash_mismatch(monkeypatch):
    original_read_jsonl = table_audit.read_jsonl

    def read_with_wrong_asset_hash(path):
        rows = original_read_jsonl(path)
        if path.name == "segments.jsonl":
            rows[0]["asset_sha256"] = "0" * 64
        return rows

    monkeypatch.setattr(table_audit, "read_jsonl", read_with_wrong_asset_hash)
    result = table_audit.audit_tables(strict_stage=True)

    assert any("source asset hash mismatch" in error for error in result["errors"])


def test_csv_row_shape_rejects_extra_and_missing_fields(tmp_path):
    csv_path = tmp_path / "entity-candidates.csv"
    csv_path.write_text(
        "candidate_id,canonical_name\ncand-1,A,shifted\ncand-2\n",
        encoding="utf-8",
    )
    errors = table_audit.csv_row_shape_errors(csv_path.name, table_audit.read_csv(csv_path))

    assert errors == [
        "entity-candidates.csv:2: row has 1 extra CSV field(s)",
        "entity-candidates.csv:3: row has missing field(s): canonical_name",
    ]


def test_s2_audit_rejects_broken_foreign_keys_and_empty_evidence(tmp_path):
    with (tmp_path / "s2-coverage.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["chapter", "segment_id", "disposition", "migration_status", "source_line_ranges", "note"])
        writer.writeheader()
        writer.writerow({"chapter": "chp-1", "segment_id": "chp-1:sec:l1-2", "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L1-2"})
    with (tmp_path / "mentions.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["mention_id", "segment_id", "candidate_id", "surface_form", "start_char", "end_char"],
        )
        writer.writeheader()
        writer.writerow({"mention_id": "m-1", "segment_id": "missing-segment", "candidate_id": "missing-candidate", "surface_form": "X", "start_char": 0, "end_char": 1})

    statement = {
        "statement_id": "s-1", "segment_id": "chp-1:sec:l1-2", "subject_candidate_id": None,
        "object_candidate_id": None, "predicate": "describes", "qualifiers": [],
        "original_quote": "", "origin": "external", "source_file": "missing.md",
    }
    (tmp_path / "book-statements.jsonl").write_text(json.dumps(statement) + "\n", encoding="utf-8")

    result = audit_s2_artifacts(tmp_path, {"cand-1"}, {"chp-1:sec:l1-2"})

    assert any("unknown or empty segment_id" in error for error in result["errors"])
    assert any("unknown or empty candidate_id" in error for error in result["errors"])
    assert any("qualifiers must be an object" in error for error in result["errors"])
    assert any("original_quote is empty" in error for error in result["errors"])
    assert any("origin must be 'book'" in error for error in result["errors"])
    assert any("source_file is missing" in error for error in result["errors"])
    assert any("not fully migrated" in warning for warning in result["warnings"])
    strict = audit_s2_artifacts(tmp_path, {"cand-1"}, {"chp-1:sec:l1-2"}, strict_stage=True)
    assert any("migration is partial, expected complete" in error for error in strict["errors"])


def test_s2_audit_checks_mention_surface_offsets(tmp_path):
    with (tmp_path / "s2-coverage.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["chapter", "segment_id", "disposition", "migration_status", "source_line_ranges", "note"])
        writer.writeheader()
        writer.writerow({"chapter": "chp-1", "segment_id": "chp-1:sec:l1-2", "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L1-2"})
    with (tmp_path / "mentions.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["mention_id", "segment_id", "candidate_id", "surface_form", "start_char", "end_char"])
        writer.writeheader()
        writer.writerow({"mention_id": "m-1", "segment_id": "chp-1:sec:l1-2", "candidate_id": "cand-1", "surface_form": "wor", "start_char": 0, "end_char": 3})
        writer.writerow({"mention_id": "m-2", "segment_id": "chp-1:sec:l1-2", "candidate_id": "cand-1", "surface_form": "ord", "start_char": 1, "end_char": 4})
    (tmp_path / "book-statements.jsonl").write_text("", encoding="utf-8")

    result = audit_s2_artifacts(
        tmp_path, {"cand-1"}, {"chp-1:sec:l1-2"}, segment_texts={"chp-1:sec:l1-2": "word"}
    )

    assert any("duplicate or crossing mention offsets" in error for error in result["errors"])


def test_s2_audit_allows_nested_entity_mentions(tmp_path):
    with (tmp_path / "s2-coverage.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["chapter", "segment_id", "disposition", "migration_status", "source_line_ranges", "note"])
        writer.writeheader()
        writer.writerow({"chapter": "chp-1", "segment_id": "chp-1:sec:l1-2", "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L1-2"})
    with (tmp_path / "mentions.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["mention_id", "segment_id", "candidate_id", "surface_form", "start_char", "end_char"])
        writer.writeheader()
        writer.writerow({"mention_id": "m-work", "segment_id": "chp-1:sec:l1-2", "candidate_id": "cand-work", "surface_form": "Relatione di Roma", "start_char": 0, "end_char": 17})
        writer.writerow({"mention_id": "m-place", "segment_id": "chp-1:sec:l1-2", "candidate_id": "cand-place", "surface_form": "Roma", "start_char": 13, "end_char": 17})
    (tmp_path / "book-statements.jsonl").write_text("", encoding="utf-8")

    result = audit_s2_artifacts(
        tmp_path, {"cand-work", "cand-place"}, {"chp-1:sec:l1-2"},
        segment_texts={"chp-1:sec:l1-2": "Relatione di Roma"}
    )

    assert not any("mention offsets" in error for error in result["errors"])


def test_s2_audit_requires_every_segment_in_a_covered_chapter(tmp_path):
    with (tmp_path / "s2-coverage.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["chapter", "segment_id", "disposition", "migration_status", "source_line_ranges", "note"])
        writer.writeheader()
        writer.writerow({"chapter": "chp-1", "segment_id": "chp-1:sec:l1-2", "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L1-2"})

    result = audit_s2_artifacts(tmp_path, set(), {"chp-1:sec:l1-2", "chp-1:sec:l3-4"})

    assert any("chp-1 coverage incomplete (1/2 segments)" in error for error in result["errors"])


def test_s2_audit_checks_statement_quote_against_original_source_lines(tmp_path):
    with (tmp_path / "source.md").open("w", encoding="utf-8") as handle:
        handle.write("Haskell says Urban VIII increased patronage.\n")
    with (tmp_path / "s2-coverage.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["chapter", "segment_id", "disposition", "migration_status", "source_line_ranges", "note"])
        writer.writeheader()
        writer.writerow({"chapter": "chp-1", "segment_id": "chp-1:sec:l1-1", "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L1-1"})
    with (tmp_path / "mentions.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["mention_id", "segment_id", "candidate_id", "surface_form", "start_char", "end_char"])
        writer.writeheader()
    statement = {
        "statement_id": "s-quote", "segment_id": "chp-1:sec:l1-1", "subject_candidate_id": None,
        "object_candidate_id": None, "predicate": "describes", "qualifiers": {"source_line_start": 1, "source_line_end": 1},
        "original_quote": "Urban IX increased patronage.", "origin": "book", "source_file": "source.md",
    }
    (tmp_path / "book-statements.jsonl").write_text(json.dumps(statement) + "\n", encoding="utf-8")

    result = audit_s2_artifacts(
        tmp_path, set(), {"chp-1:sec:l1-1"}, source_root=tmp_path
    )

    assert any("original_quote does not match cited source lines" in error for error in result["errors"])


def test_s2_audit_requires_artifacts_in_strict_mode(tmp_path):
    result = audit_s2_artifacts(tmp_path, set(), set(), strict_stage=True)

    assert set(result["missing"]) == {"s2-coverage.csv", "mentions.csv", "book-statements.jsonl"}
    assert any("required for release" in error for error in result["errors"])
