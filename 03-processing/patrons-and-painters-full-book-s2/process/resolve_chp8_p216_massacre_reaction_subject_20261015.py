from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l21-35"
SEGMENT_SHA256 = "4f5d502c755d5a791200895b453b3a196db68632297a0864a37c4995a91c1039"
SEGMENT_ASSET_SHA256 = "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6"
PDF_SHA256 = "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3"
STATEMENT_ID = "st-chp8-p216-governors-pleased-with-massacre"
EXPECTED_STATEMENTS_SHA256 = "8b2a8ef29c6b18b6f7d7611e2827f40a597c07abd0955debeeb5092187c7145d"
BACKUP_SUFFIX = ".bak-s2-chp8-p216-reaction-subject-20261015"
TEMP_SUFFIX = ".tmp-s2-chp8-p216-reaction-subject-20261015"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def rows(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve the p.216 pronoun in the reaction to Padre Massimo's painting.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preview", action="store_true")
    group.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    args = parser.parse_args()

    pdf = ROOT / "02-sources/01-book/CHP-8.pdf"
    if sha(pdf.read_bytes()) != PDF_SHA256:
        raise ValueError("Reviewed CHP-8.pdf changed.")
    segments = rows(SEGMENTS.read_bytes())
    matches = [row for row in segments if row.get("segment_id") == SEGMENT_ID]
    if len(matches) != 1:
        raise ValueError("Reviewed p.216 source segment is missing or duplicated.")
    segment = matches[0]
    if segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SEGMENT_ASSET_SHA256:
        raise ValueError("Reviewed p.216 segment metadata changed.")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    source_text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(source_text.encode("utf-8")) != SEGMENT_SHA256:
        raise ValueError("Reviewed p.216 transcription changed.")
    if "The committee’s one attempt" not in source_text or "So pleased were they with the work" not in source_text:
        raise ValueError("The pronoun antecedent context changed.")

    raw = STATEMENTS.read_bytes()
    input_hash = sha(raw)
    if input_hash != EXPECTED_STATEMENTS_SHA256:
        raise ValueError(f"Protected statement snapshot changed: {input_hash}")
    statement_rows = rows(raw)
    if len(statement_rows) != 15158:
        raise ValueError("Unexpected statement inventory.")
    matches = [row for row in statement_rows if row.get("statement_id") == STATEMENT_ID]
    if len(matches) != 1:
        raise ValueError("Target statement is missing or duplicated.")
    updated = json.loads(json.dumps(matches[0], ensure_ascii=False))
    q = updated.get("qualifiers") or {}
    if (
        updated.get("segment_id") != SEGMENT_ID
        or updated.get("subject_candidate_id")
        or updated.get("object_candidate_id") != "cand-7653"
        or q.get("relation_candidate") is not True
        or q.get("open_endpoint_reason")
        or updated.get("original_quote") != "So pleased were they with the work"
    ):
        raise ValueError("Reviewed statement no longer matches its expected open state.")
    updated["subject_candidate_id"] = "cand-7641"
    q["claim"] = "Haskell says the Santa Maria Maggiore committee was pleased with Padre Massimo's Massacre of the Innocents."
    q["qualification"] = "The immediate antecedent of 'they' is the committee that commissioned the work; the preceding satisfaction clause does not make the whole city the subject of this reaction."
    q["mentioned_candidate_ids"] = ["cand-7641", "cand-7653"]
    q["relation_candidate_note"] = "The source links the committee's positive reaction to the specific commissioned painting; its following appeal to the Capuchins confirms the committee's continuing action."
    q.pop("open_endpoint_reason", None)
    updated["qualifiers"] = q

    bom = raw.startswith(b"\xef\xbb\xbf")
    output: list[str] = []
    seen = 0
    for line in raw.decode("utf-8-sig").splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        row = json.loads(body)
        if row.get("statement_id") == STATEMENT_ID:
            output.append(json.dumps(updated, ensure_ascii=False, separators=(",", ":")) + ending)
            seen += 1
        else:
            output.append(line)
    if seen != 1:
        raise ValueError("Statement update target did not occur exactly once.")
    rewritten = (("\ufeff" if bom else "") + "".join(output)).encode("utf-8")
    after_rows = rows(rewritten)
    opened = [
        row for row in after_rows
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
    ]
    no_reason = sum(not (row.get("qualifiers") or {}).get("open_endpoint_reason") for row in opened)
    if len(opened) != 360 or no_reason != 38:
        raise ValueError(f"Unexpected post-edit open endpoint inventory: {len(opened)}, no_reason={no_reason}")
    print("reviewed=CHP-8 p.216 / PDF physical page 14; pronoun antecedent checked in page image and surrounding text")
    print("change=subject cand-7641 (committee); object cand-7653 (Massacre of the Innocents)")
    print("open_endpoints=361->360; no_reason_open=39->38")
    print(f"book-statements.jsonl sha256 {input_hash}->{sha(rewritten)}")
    if args.preview:
        return 0
    if args.expected_statements_sha256 != input_hash:
        raise ValueError("Apply requires the input hash printed by this preview.")
    backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
    temp = STATEMENTS.with_name(STATEMENTS.name + TEMP_SUFFIX)
    if backup.exists() or temp.exists():
        raise FileExistsError("Recovery copy or temporary statement table already exists.")
    shutil.copy2(STATEMENTS, backup)
    try:
        temp.write_bytes(rewritten)
        temp.replace(STATEMENTS)
    except Exception:
        if temp.exists():
            temp.unlink()
        shutil.copy2(backup, STATEMENTS)
        raise
    print("applied=yes")
    print(f"backup={backup.relative_to(ROOT)}")
    print(f"applied_sha256={sha(STATEMENTS.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
