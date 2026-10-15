#!/usr/bin/env python3
"""Controlled S2 refinement for CHP-13 printed p.346 (source lines 173-177)."""
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
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
SEGMENT = "chp-13:13_CHP-13_intro:l173-177"
SOURCE_FILE = "02-sources/02-Markdown/13_CHP-13_intro.md"
BACKUP_SUFFIX = ".bak-s2-ch13-p346-semantic-review-20261014"
EXPECTED = {
    STATEMENTS: "357fc817001590c0141793f8886acea11a0c95a4bd634de4f57e1c2e5f80235c",
    CANDIDATES: "0a066d8745f077d1744fd23520bb5f05c856e5ff58f95a63943c36cf019ff64e",
    MENTIONS: "b727de764da5d73f00ed12a54cc97161a3594bed2c4d5812a0ea14b252d7a58d",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def dump_jsonl(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def load_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def dump_csv(headers: list[str], rows: list[dict]) -> bytes:
    from io import StringIO

    out = StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=headers, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + out.getvalue()).encode("utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    for path, expected in EXPECTED.items():
        actual = sha(path)
        if actual != expected:
            raise SystemExit(f"precondition failed: {path.relative_to(ROOT)} sha256={actual}, expected={expected}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[172:177])

    def exact_quote(start: int, end: int, quote: str) -> str:
        scoped = "\n".join(source_lines[start - 1 : end])
        if quote not in scoped:
            raise ValueError(f"quote is not exact S0 text at L{start}-L{end}: {quote!r}")
        return quote

    statements = load_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    if len(page_rows) != 6:
        raise SystemExit(f"expected six existing p.346 statements, found {len(page_rows)}")
    candidate_headers, candidates = load_csv(CANDIDATES)
    by_candidate = {row["candidate_id"]: row for row in candidates}
    mention_headers, mentions = load_csv(MENTIONS)
    if any(row.get("segment_id") == SEGMENT for row in mentions):
        raise SystemExit("expected no existing p.346 mentions")

    def refine(sid: str, *, start: int, end: int, quote: str, claim: str,
               relation: bool, predicate: str | None = None,
               subject: str | None = None, obj: str | None = None,
               mentioned: list[str] | None = None, qualification: str = "",
               relation_note: str | None = None) -> None:
        row = by_id[sid]
        row["original_quote"] = exact_quote(start, end, quote)
        if predicate is not None:
            row["predicate"] = predicate
        if subject is not None or "subject_candidate_id" in row:
            row["subject_candidate_id"] = subject
        if obj is not None or "object_candidate_id" in row:
            row["object_candidate_id"] = obj
        q = row.setdefault("qualifiers", {})
        q.update({"source_line_start":start,"source_line_end":end,"printed_page":346,"pdf_physical_page":19,
                  "claim":claim,"speaker":"Haskell","text_layer":"authorial narrative","qualification":qualification,
                  "relation_candidate":relation})
        if mentioned is not None:
            q["mentioned_candidate_ids"] = mentioned
        if relation_note:
            q["relation_candidate_note"] = relation_note
        elif "relation_candidate_note" in q:
            del q["relation_candidate_note"]

    new_candidate = {
        "candidate_id":"cand-12181","index_entry_id":"",
        "canonical_name":"Collectors for whom Don Pietro Antonio Toni acted as agent, including named Venetian and foreign collectors",
        "index_page_range":"","suggested_type":"term","status":"open","index_source_file":"","sub_entry":"",
        "detail":"A source-defined group of collectors Haskell says Toni served as agent for on p.346, including Zaccaria Sagredo, a surname-only Zanetti, Consul Smith, and various foreign visitors. Preserve the page's identity limits; do not infer additional members.",
        "exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{SEGMENT}#L174-L175"
    }
    if new_candidate["candidate_id"] in by_candidate:
        raise SystemExit("planned candidate cand-12181 already exists")
    candidates.append(new_candidate)
    by_candidate[new_candidate["candidate_id"]] = new_candidate

    refine("st-chp13-p346-toni-dealer-agent-role", start=174, end=175,
           quote="agent for many far more important collectors than himself, such as Zaccaria Sagredo,\nZanetti, Consul Smith and various foreign visitors",
           claim="Haskell says Toni acted as agent for a source-defined group of collectors described as more important than himself, including the named collectors and foreign visitors.",
           predicate="acted_as_agent_for", subject="cand-2640", obj="cand-12181", relation=True,
           mentioned=["cand-2640","cand-12181","cand-2329","cand-2838","cand-2440"],
           qualification="The sentence completes the p.345 line 'He was also a dealer, and he acted as'. The named collector identities retain their existing limits; no commission, date, or object is supplied.",
           relation_note="The source directly reports Toni's agency for a source-defined collector group and separately names examples; members beyond those stated are not inferred.")
    refine("st-chp13-p346-toni-agent-for-zaccaria-sagredo", start=174, end=174,
           quote="Zaccaria Sagredo", claim="Haskell names Zaccaria Sagredo as one of the collectors for whom Toni acted as an agent.",
           relation=True, mentioned=["cand-2640","cand-2329"],
           qualification="The index candidate is reused pending S3 alignment. The passage supplies no individual commission, date, or object for this agency.",
           relation_note="The passage explicitly names Sagredo as one collector served by Toni as agent.")
    refine("st-chp13-p346-toni-agent-for-zanetti", start=175, end=175,
           quote="Zanetti", claim="Haskell names a Zanetti as one of the collectors for whom Toni acted as an agent.",
           relation=True, mentioned=["cand-2640","cand-2838"],
           qualification="Surname only. The elder-Zanetti candidate is provisional from context; the sentence does not disambiguate identity. No individual commission, date, or object is supplied.",
           relation_note="The passage explicitly names a Zanetti as one collector served by Toni; identity alignment remains unresolved.")
    refine("st-chp13-p346-toni-agent-for-consul-smith", start=175, end=175,
           quote="Consul Smith", claim="Haskell names Consul Smith as one of the collectors for whom Toni acted as an agent.",
           relation=True, mentioned=["cand-2640","cand-2440"],
           qualification="The index candidate is Joseph Smith, but this passage gives title and surname only; retain that identity limit. No individual commission, date, or object is supplied.",
           relation_note="The passage explicitly names Consul Smith as one collector served by Toni; the candidate identity remains provisional.")
    refine("st-chp13-p346-haskell-characterizes-venetian-art-world", start=176, end=176,
           quote="the flourishing and parasitic art world of Venice",
           claim="Haskell characterizes Venice's art world as flourishing and parasitic.",
           relation=False, mentioned=["cand-2719"],
           qualification="This preserves Haskell's evaluative language as authorial interpretation rather than a neutral measured description. 'With Toni as guide' is narrative framing.")
    refine("st-chp13-p346-toni-would-buy-prints-from-pasquetti", start=176, end=176,
           quote="he would go and buy prints from the hunchback Leonardo Pasquetti",
           claim="Haskell says Toni habitually went to buy prints from Leonardo Pasquetti.",
           relation=True, predicate="would_buy_prints_from", subject="cand-2640", obj="cand-1853",
           mentioned=["cand-2640","cand-1853","cand-10126"],
           qualification="The source uses habitual/illustrative 'would'; it does not identify a dated purchase, individual print, count, or exact stall. The Merceria candidate remains unresolved at site level.",
           relation_note="The passage describes Toni as a recurring buyer from Pasquetti; preserve its habitual form and do not infer an individual transaction.")

    mention_specs = [
        ("cand-2640","Toni as guide","Narrative framing of Toni's role in the transition."),
        ("cand-2640","himself","Toni is the referent in Haskell's comparison of collectors."),
        ("cand-12181","many far more important collectors","Source-defined group Toni served as agent for."),
        ("cand-2329","Zaccaria Sagredo","Named collector; candidate alignment remains pending."),
        ("cand-2838","Zanetti","Surname only; identity remains unresolved in the agency statement."),
        ("cand-2440","Consul Smith","Title and surname only; identity remains provisional."),
        ("cand-12181","various foreign visitors","Unnamed members of the agent's collector group."),
        ("cand-2640","Toni","Toni as guide in Haskell's narrative transition."),
        ("cand-2719","Venice","The place whose art world Haskell characterizes."),
        ("cand-2640","him","Anaphoric reference to Toni."),
        ("cand-10126","the Merceria","Location of the print stall; exact site unresolved."),
        ("cand-1853","the hunchback Leonardo Pasquetti","Pasquetti as named print seller; retain the source's epithet as description."),
    ]
    additions = []
    for candidate_id, surface, note in mention_specs:
        if candidate_id not in by_candidate:
            raise ValueError(f"mention candidate missing: {candidate_id}")
        start = 0
        found = []
        while True:
            index = segment_text.find(surface, start)
            if index < 0:
                break
            found.append(index)
            start = index + 1
        if not found:
            raise ValueError(f"mention surface missing from exact segment: {surface!r}")
        for index in found:
            additions.append({"mention_id":"","segment_id":SEGMENT,"candidate_id":candidate_id,
                              "surface_form":surface,"start_char":str(index),"end_char":str(index+len(surface)),"note":note})
    additions.sort(key=lambda row:(int(row["start_char"]),-int(row["end_char"]),row["candidate_id"]))
    filtered=[]
    seen=set()
    for row in additions:
        key=(row["candidate_id"],row["start_char"],row["end_char"])
        if key in seen:
            continue
        seen.add(key)
        start,end=int(row["start_char"]),int(row["end_char"])
        if any(prev["candidate_id"]==row["candidate_id"] and int(prev["start_char"])<=start and end<=int(prev["end_char"]) for prev in filtered):
            continue
        filtered.append(row)
    additions=filtered
    existing_ids={row["mention_id"] for row in mentions}
    for index,row in enumerate(additions,1):
        row["mention_id"]=f"m-s2-ch13-p346-{index:03d}"
        if row["mention_id"] in existing_ids:
            raise ValueError(f"mention ID collision: {row['mention_id']}")
        start,end=int(row["start_char"]),int(row["end_char"])
        if segment_text[start:end]!=row["surface_form"]:
            raise ValueError(f"mention span mismatch: {row}")
    mentions.extend(additions)

    for row in statements:
        if row.get("segment_id")!=SEGMENT:
            continue
        if "relation_candidate" not in row["qualifiers"]:
            raise ValueError(f"unclassified statement remains: {row['statement_id']}")
        q=row["qualifiers"]
        scoped="\n".join(source_lines[q["source_line_start"]-1:q["source_line_end"]])
        if row["original_quote"] not in scoped:
            raise ValueError(f"quote anchor mismatch: {row['statement_id']}")
        for candidate_id in (row.get("subject_candidate_id"),row.get("object_candidate_id")):
            if candidate_id and candidate_id not in by_candidate:
                raise ValueError(f"missing endpoint candidate: {row['statement_id']} -> {candidate_id}")

    print(f"p346 statements: {len(page_rows)}; classifications true={sum(r['qualifiers']['relation_candidate'] is True for r in page_rows)} false={sum(r['qualifiers']['relation_candidate'] is False for r in page_rows)}")
    print(f"new candidates: 1; p346 mentions: {len(additions)}")
    print("validated exact source quotes, candidate endpoints, and mention spans")
    if not args.apply:
        print("DRY-RUN only; no tables changed")
        return

    for path in (STATEMENTS,CANDIDATES,MENTIONS):
        backup=path.with_name(path.name+BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"recovery copy already exists: {backup.name}")
        shutil.copy2(path,backup)
    STATEMENTS.write_bytes(dump_jsonl(statements))
    CANDIDATES.write_bytes(dump_csv(candidate_headers,candidates))
    MENTIONS.write_bytes(dump_csv(mention_headers,mentions))
    for path in (STATEMENTS,CANDIDATES,MENTIONS):
        print(f"wrote {path.relative_to(ROOT)} sha256={sha(path)}")
    print(f"recovery copies created with suffix {BACKUP_SUFFIX}")


if __name__=="__main__":
    main()
