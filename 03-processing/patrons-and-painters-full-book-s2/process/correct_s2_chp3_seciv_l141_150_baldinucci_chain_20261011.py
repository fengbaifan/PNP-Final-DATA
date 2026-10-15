from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
PRE_HASHES = {
    STATEMENTS.name: "7a7cb77f6bb2345dc394970304299553b6d064a1bc9f295db45d05496220b0ef",
    CANDIDATES.name: "9e45914be1a9797f0bb30a15e0f2cbfe4856cc574427ae4c9ca8f18d4b63bba8",
}
BACKUP_SUFFIX = ".bak-s2-chp3-seciv-l141-150-baldinucci-chain-20261011"
OLD = "p.89 n.3 to p.87 n.5"
NEW = "p.89 n.3 to p.88 n.5"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode_jsonl_preserving_unchanged(records: list[dict], raw: bytes) -> bytes:
    raw_lines = raw.splitlines(keepends=True)
    rows_by_id = {row["statement_id"]: row for row in records}
    eol = "\r\n" if b"\r\n" in raw else "\n"
    bom = raw.startswith(b"\xef\xbb\xbf")
    out: list[bytes] = []
    seen: set[str] = set()
    for index, line in enumerate(raw_lines):
        if not line.strip():
            out.append(line)
            continue
        original = json.loads(line.decode("utf-8-sig"))
        sid = original["statement_id"]
        updated = rows_by_id[sid]
        seen.add(sid)
        if original == updated:
            out.append(line)
        else:
            encoded = (json.dumps(updated, ensure_ascii=False, separators=(",", ":")) + eol).encode("utf-8")
            if index == 0 and bom:
                encoded = b"\xef\xbb\xbf" + encoded
            out.append(encoded)
    if seen != set(rows_by_id):
        raise SystemExit("unexpected statement additions or removals")
    return b"".join(out)


def encode_csv(fields: list[str], rows: list[dict], eol: str, bom: bool) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="raise", lineterminator=eol)
    writer.writeheader()
    writer.writerows(rows)
    return (("\ufeff" if bom else "") + output.getvalue()).encode("utf-8")


def prepare() -> dict[Path, bytes]:
    statement_raw = STATEMENTS.read_bytes()
    candidate_raw = CANDIDATES.read_bytes()
    for path, raw in ((STATEMENTS, statement_raw), (CANDIDATES, candidate_raw)):
        if sha(raw) != PRE_HASHES[path.name]:
            raise SystemExit(f"unexpected {path.name} hash; correction precondition failed")
    records = [json.loads(line) for line in statement_raw.decode("utf-8-sig").splitlines() if line.strip()]
    target = [row for row in records if row["statement_id"] == "st-chp3-seciv-l141-150-dome-reputation-led-to-vault-idea"]
    if len(target) != 1:
        raise SystemExit("the p.90 biographer statement is not unique")
    q = target[0]["qualifiers"]
    if OLD not in q.get("qualification", ""):
        raise SystemExit("statement does not contain the expected page-chain typo")
    q["qualification"] = q["qualification"].replace(OLD, NEW)

    bom = candidate_raw.startswith(b"\xef\xbb\xbf")
    candidate_text = candidate_raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in candidate_text else "\n"
    reader = csv.DictReader(io.StringIO(candidate_text, newline=""))
    fields = list(reader.fieldnames or [])
    candidates = list(reader)
    author = [row for row in candidates if row.get("candidate_id") == "cand-5388"]
    if len(author) != 1 or OLD not in author[0].get("detail", ""):
        raise SystemExit("unidentified-biographer candidate lacks the expected page-chain text")
    author[0]["detail"] = author[0]["detail"].replace(OLD, NEW)
    return {
        STATEMENTS: encode_jsonl_preserving_unchanged(records, statement_raw),
        CANDIDATES: encode_csv(fields, candidates, eol, bom),
    }


def main() -> None:
    prepared = prepare()
    print("correct page chain: p.90 n.2 -> p.89 n.3 -> p.88 n.5")
    print("no entity identity or relation endpoint changes")
    if not __import__("sys").argv[1:] or "--apply" not in __import__("sys").argv[1:]:
        print("DRY-RUN PASS; no files written")
        return
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in prepared}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("recovery copy already exists; refusing to overwrite")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    temps: list[tuple[Path, Path]] = []
    try:
        for path, data in prepared.items():
            temp = path.with_name(path.name + ".tmp-write")
            if temp.exists():
                raise SystemExit(f"temporary output already exists: {temp.name}")
            temp.write_bytes(data)
            temps.append((temp, path))
        for temp, path in temps:
            os.replace(temp, path)
        for path, data in prepared.items():
            if path.read_bytes() != data:
                raise SystemExit(f"post-write byte check failed: {path.name}")
    except Exception:
        for temp, _ in temps:
            if temp.exists():
                temp.unlink()
        for path, backup in backups.items():
            if backup.exists():
                shutil.copy2(backup, path)
        raise
    print("APPLY PASS")
    for path in prepared:
        print(f"post_sha256 {path.name} {sha(path.read_bytes())}")


if __name__ == "__main__":
    main()
