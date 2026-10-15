from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp3-seci-l26-33-open-endpoints-20261015")

TARGETS = {
    "st-chp3-seci-l26-33-church-decoration-synthesis",
    "st-chp3-seci-l26-33-families-superiority-legal-financial",
    "st-chp3-seci-l26-33-secular-princes-claims-first",
}
CONTEXT_IDS = {
    "st-chp3-seci-l26-33-orders-call-great-artists-after-source-dries",
    "st-chp3-seci-l26-33-duchess-wanted-ciro-ferri",
    "st-chp3-seci-l26-33-ferri-engagements-with-nuns",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def transform(raw: bytes) -> tuple[bytes, dict[str, dict]]:
    lines = raw.decode("utf-8").splitlines(keepends=True)
    found: dict[str, dict] = {}
    all_ids: set[str] = set()
    for i, line in enumerate(lines):
        item = json.loads(line)
        sid = item.get("statement_id")
        if sid:
            all_ids.add(sid)
        if sid not in TARGETS:
            continue
        if item.get("segment_id") != "chp-3:03_CHP-3_sec_i:l26-33":
            raise ValueError(f"Unexpected segment for {sid}: {item.get('segment_id')}")
        found[sid] = item
        q = item.setdefault("qualifiers", {})
        if sid == "st-chp3-seci-l26-33-church-decoration-synthesis":
            if item.get("object_candidate_id"):
                raise ValueError(f"Expected open object for {sid}")
            q["open_endpoint_reason"] = (
                "The phrase 'synthesis derived from conflicting forces' describes an unenumerated combination. "
                "The surrounding patron examples clarify context but do not identify one bounded object or assign "
                "the forces to individual churches."
            )
        elif sid == "st-chp3-seci-l26-33-families-superiority-legal-financial":
            if item.get("object_candidate_id"):
                raise ValueError(f"Expected open object for {sid}")
            q["open_endpoint_reason"] = (
                "The source names legal and financial forces generically and gives expropriation/dispossession as "
                "one legal example; it does not identify the financial forces or delimit the full set as one endpoint."
            )
        elif sid == "st-chp3-seci-l26-33-secular-princes-claims-first":
            if item.get("object_candidate_id"):
                raise ValueError(f"Expected open object for {sid}")
            item["object_candidate_id"] = "cand-2114"
            q["claim"] = (
                "Haskell says secular princes' claims took precedence over religious orders' calls on great artists "
                "in the context of papal/court patronage receding."
            )
            q["qualification"] = (
                "The preceding sentence identifies religious Orders, especially the Jesuits, as able to call on great "
                "artists after papal/court patronage receded. The Duchess of Savoy/Ciro Ferri anecdote illustrates "
                "the precedence claim but is not treated as an exhaustive list of competing claims."
            )
            q["relation_candidate_note"] = (
                "The preceding sentence ties 'even then' to the religious Orders' renewed calls on great artists; "
                "the Duchess of Savoy/Ciro Ferri example illustrates one case of princely priority over Ferri's "
                "existing engagements with nuns. Map the comparison to existing candidate cand-2114 for religious-order "
                "patronage; the anecdote is illustrative, not exhaustive."
            )
            q.pop("open_endpoint_reason", None)
            q["related_statement_ids"] = sorted(CONTEXT_IDS)
        lines[i] = json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"

    missing = TARGETS - found.keys()
    if missing:
        raise ValueError(f"Missing target statements: {sorted(missing)}")
    missing_context = CONTEXT_IDS - all_ids
    if missing_context:
        raise ValueError(f"Missing contextual statements: {sorted(missing_context)}")
    return "".join(lines).encode("utf-8"), found


def count_open(data: bytes) -> int:
    count = 0
    for line in data.decode("utf-8").splitlines():
        item = json.loads(line)
        q = item.get("qualifiers") or {}
        if q.get("relation_candidate") is True and (
            not item.get("subject_candidate_id") or not item.get("object_candidate_id")
        ):
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    before = TABLE.read_bytes()
    after, targets = transform(before)
    print(f"table={TABLE.relative_to(ROOT)}")
    print(f"before_sha256={digest(before)}")
    print(f"after_sha256={digest(after)}")
    print(f"open_endpoints={count_open(before)}->{count_open(after)}")
    print("changes:")
    for sid in sorted(targets):
        old = targets[sid]
        q = old.get("qualifiers") or {}
        if sid.endswith("secular-princes-claims-first"):
            print(f"  {sid}: object (open)->cand-2114; add 3 contextual statement links")
        elif sid.endswith("church-decoration-synthesis"):
            print(f"  {sid}: retain open object; add explicit open-endpoint reason")
        else:
            print(f"  {sid}: retain open object; add explicit open-endpoint reason")

    if args.preview:
        return 0
    if BACKUP.exists():
        raise FileExistsError(f"Refusing to overwrite recovery copy: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    temp = TABLE.with_suffix(TABLE.suffix + ".tmp")
    temp.write_bytes(after)
    temp.replace(TABLE)
    print(f"backup={BACKUP.relative_to(ROOT)}")
    print(f"applied_sha256={digest(TABLE.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
