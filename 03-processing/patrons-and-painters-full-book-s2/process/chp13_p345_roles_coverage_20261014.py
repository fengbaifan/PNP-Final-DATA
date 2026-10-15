#!/usr/bin/env python3
"""Add three narrowly scoped role claims omitted from the p.345 migration."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
SEGMENT = "chp-13:13_CHP-13_intro:l161-171"
BACKUP_SUFFIX = ".bak-s2-ch13-p345-roles-20261014"
EXPECTED = {
    STATEMENTS: "18e56061ee5076f4c91bb3ae2aefb540a6a3ecd7f887327e9eb81a87006e8125",
    MENTIONS: "f6bda72538327a1a4b89b8c7dcf248fb1aa0a220f84a3b6078b64d281d7719b4",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--apply",action="store_true")
    args=ap.parse_args()
    for path,expected in EXPECTED.items():
        actual=sha(path)
        if actual!=expected:
            raise SystemExit(f"precondition failed: {path.name} sha256={actual}")
    src=SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text="\n".join(src[160:171])
    statements=[json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    if sum(row.get("segment_id")==SEGMENT for row in statements)!=56:
        raise SystemExit("expected 56 reviewed p.345 statements")
    ids={row["statement_id"] for row in statements}
    new_rows=[
        {"statement_id":"st-chp13-p345-monaco-engraver-role","segment_id":SEGMENT,"subject_candidate_id":"cand-1682","object_candidate_id":None,"predicate":"identified_as_engraver","qualifiers":{"source_line_start":165,"source_line_end":165,"printed_page":345,"pdf_physical_page":18,"claim":"Haskell identifies Pietro Monaco as an engraver.","speaker":"Haskell","text_layer":"authorial narrative","qualification":"This is the occupational description in Haskell's account; no guild or institutional affiliation is inferred.","relation_candidate":False,"mentioned_candidate_ids":["cand-1682"]},"original_quote":"the engraver Pietro Monaco","origin":"book","source_file":"02-sources/02-Markdown/13_CHP-13_intro.md"},
        {"statement_id":"st-chp13-p345-toni-priest-role","segment_id":SEGMENT,"subject_candidate_id":"cand-2640","object_candidate_id":None,"predicate":"identified_as_priest","qualifiers":{"source_line_start":169,"source_line_end":169,"printed_page":345,"pdf_physical_page":18,"claim":"Haskell introduces Don Pietro Antonio Toni as a priest.","speaker":"Haskell","text_layer":"authorial narrative","qualification":"This records the role stated in the passage; no religious institution or office is inferred.","relation_candidate":False,"mentioned_candidate_ids":["cand-2640"]},"original_quote":"the priest Don Pietro Antonio Toni","origin":"book","source_file":"02-sources/02-Markdown/13_CHP-13_intro.md"},
        {"statement_id":"st-chp13-p345-toni-dealer-role","segment_id":SEGMENT,"subject_candidate_id":"cand-2640","object_candidate_id":None,"predicate":"identified_as_dealer","qualifiers":{"source_line_start":170,"source_line_end":170,"printed_page":345,"pdf_physical_page":18,"claim":"Haskell says Toni was also a dealer.","speaker":"Haskell","text_layer":"authorial narrative","qualification":"The agency relation continues on p.346 and is recorded separately; this row captures the occupational role only.","relation_candidate":False,"mentioned_candidate_ids":["cand-2640"],"cross_reference_segments":["chp-13:13_CHP-13_intro:l173-177"]},"original_quote":"He was also a dealer","origin":"book","source_file":"02-sources/02-Markdown/13_CHP-13_intro.md"},
    ]
    for row in new_rows:
        if row["statement_id"] in ids: raise SystemExit(f"statement collision: {row['statement_id']}")
        q=row["qualifiers"]; scoped="\n".join(src[q["source_line_start"]-1:q["source_line_end"]])
        if row["original_quote"] not in scoped: raise ValueError(f"bad quote: {row['statement_id']}")
        statements.append(row)
    with MENTIONS.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f); mention_headers=list(reader.fieldnames or []); mentions=list(reader)
    if any(row.get("segment_id")==SEGMENT and row.get("mention_id","" ).endswith(("055","056","057")) for row in mentions):
        raise SystemExit("planned p.345 role mention IDs already exist")
    mention_specs=[
        ("m-s2-ch13-p345-055","cand-1682","the engraver Pietro Monaco","Monaco's occupational description in the source."),
        ("m-s2-ch13-p345-056","cand-2640","the priest Don Pietro Antonio Toni","Toni's stated clerical role."),
        ("m-s2-ch13-p345-057","cand-2640","He was also a dealer","Anaphoric subject is Toni; the agency clause continues on p.346."),
    ]
    for mention_id,candidate_id,surface,note in mention_specs:
        start=segment_text.find(surface)
        if start<0: raise ValueError(f"mention phrase absent: {surface!r}")
        end=start+len(surface)
        mentions.append({"mention_id":mention_id,"segment_id":SEGMENT,"candidate_id":candidate_id,"surface_form":surface,"start_char":str(start),"end_char":str(end),"note":note})
        if segment_text[start:end]!=surface: raise ValueError(f"mention span mismatch: {mention_id}")
    print("p345 statements 56 -> 59; new mentions 3; exact quote and span checks passed")
    if not args.apply:
        print("DRY-RUN only; no tables changed")
        return
    for path in (STATEMENTS,MENTIONS):
        backup=path.with_name(path.name+BACKUP_SUFFIX)
        if backup.exists(): raise SystemExit(f"recovery copy already exists: {backup.name}")
        shutil.copy2(path,backup)
    STATEMENTS.write_text("\n".join(json.dumps(row,ensure_ascii=False,separators=(",",":")) for row in statements)+"\n",encoding="utf-8",newline="\n")
    from io import StringIO
    out=StringIO(newline=""); writer=csv.DictWriter(out,fieldnames=mention_headers,lineterminator="\n");writer.writeheader();writer.writerows(mentions)
    MENTIONS.write_bytes(("\ufeff"+out.getvalue()).encode("utf-8"))
    for path in (STATEMENTS,MENTIONS): print(f"wrote {path.relative_to(ROOT)} sha256={sha(path)}")
    print(f"recovery copies created with suffix {BACKUP_SUFFIX}")


if __name__=="__main__":main()
