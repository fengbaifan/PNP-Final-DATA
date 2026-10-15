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
SEGMENT_ID = "chp-10:10_CHP-10_sec_ii:l224-239"
SEGMENT_SHA256 = "0932b9d6e7b24dc84a8fad20a510cdf979f7af80a8055204c687917e86f684e4"
SEGMENT_ASSET_SHA256 = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
PDF_SHA256 = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
STATEMENT_ID = "st-chp10-p327-n03-pictures-or-prints-exhibited"
EXPECTED_STATEMENTS_SHA256 = "c0beeac3eb5d82c7496d89ccac36e8c5a1871b13bc12bce36fe43d0c424eef3d"
BACKUP_SUFFIX = ".bak-s2-chp10-p327-alternative-object-reason-20261015"
TEMP_SUFFIX = ".tmp-s2-chp10-p327-alternative-object-reason-20261015"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def rows(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Record why the p.327 exhibition claim retains an open object endpoint.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    args = parser.parse_args()
    if sha((ROOT / "02-sources/01-book/CHP-10.pdf").read_bytes()) != PDF_SHA256:
        raise ValueError("Reviewed CHP-10.pdf changed.")
    segments = [r for r in rows(SEGMENTS.read_bytes()) if r.get("segment_id") == SEGMENT_ID]
    if len(segments) != 1:
        raise ValueError("Reviewed p.327 source segment is missing or duplicated.")
    segment = segments[0]
    if segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SEGMENT_ASSET_SHA256:
        raise ValueError("Reviewed p.327 segment metadata changed.")
    lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    source = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(source.encode("utf-8")) != SEGMENT_SHA256:
        raise ValueError("Reviewed p.327 transcription changed.")
    phrase = "the pictures or the prints were exhibited in 1780"
    if source.count(phrase) != 1 or "stated not only by Zannandreis" not in source or "implied by the well-informed Moschini" not in source:
        raise ValueError("The alternatives or supporting-source context changed.")

    raw = STATEMENTS.read_bytes()
    input_hash = sha(raw)
    if input_hash != EXPECTED_STATEMENTS_SHA256:
        raise ValueError(f"Protected statement snapshot changed: {input_hash}")
    statements = rows(raw)
    if len(statements) != 15158:
        raise ValueError("Unexpected statement inventory.")
    found = [r for r in statements if r.get("statement_id") == STATEMENT_ID]
    if len(found) != 1:
        raise ValueError("Target statement is missing or duplicated.")
    updated = json.loads(json.dumps(found[0], ensure_ascii=False))
    q = updated.get("qualifiers") or {}
    if (
        updated.get("segment_id") != SEGMENT_ID
        or updated.get("subject_candidate_id")
        or updated.get("object_candidate_id") != "cand-9792"
        or q.get("relation_candidate") is not True
        or q.get("open_endpoint_reason")
    ):
        raise ValueError("Target statement no longer matches the expected open state.")
    q["open_endpoint_reason"] = "Haskell explicitly leaves the exhibited object as 'the pictures or the prints'. Zannandreis is cited for the exhibition claim, while Moschini is said to imply that Dall'Acqua's prints were at Pisani's entry; neither cited page was independently consulted. Do not select either picture/print candidate as the sole referent or invent a combined work/print object until the medium and referent are established."
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
        raise ValueError("Target statement did not occur exactly once.")
    rewritten = (("\ufeff" if bom else "") + "".join(output)).encode("utf-8")
    after = rows(rewritten)
    open_rows = [r for r in after if (r.get("qualifiers") or {}).get("relation_candidate") is True and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))]
    no_reason = sum(not (r.get("qualifiers") or {}).get("open_endpoint_reason") for r in open_rows)
    if len(open_rows) != 358 or no_reason != 34:
        raise ValueError(f"Unexpected post-edit open endpoint state: open={len(open_rows)}, no_reason={no_reason}")
    print("reviewed=CHP-10 p.327 / PDF physical page 60; footnote alternatives checked against page image")
    print("change=retain missing object; add reason because source preserves unresolved picture-versus-print alternatives")
    print("open_endpoints=358 (unchanged); no_reason_open=35->34")
    print(f"book-statements.jsonl sha256 {input_hash}->{sha(rewritten)}")
    if args.preview:
        return 0
    if args.expected_statements_sha256 != input_hash:
        raise ValueError("Apply requires the input hash printed by this preview.")
    backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
    temp = STATEMENTS.with_name(STATEMENTS.name + TEMP_SUFFIX)
    if backup.exists() or temp.exists():
        raise FileExistsError("Recovery copy or temporary statement file already exists.")
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
