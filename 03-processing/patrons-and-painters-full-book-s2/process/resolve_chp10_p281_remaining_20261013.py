from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
SEGMENT = "chp-10:10_CHP-10_intro:l125-139"
TARGETS = {
    "st-chp10-p281-brydges-created-duke",
    "st-chp10-p281-brydges-fortune-paymaster",
    "st-chp10-p281-english-support-venetian-painters",
    "st-chp10-p281-english-work-assessment",
    "st-chp10-p281-european-centres-venetian-artists",
    "st-chp10-p281-sheffield-ceiling-description",
    "st-chp10-p281-sheffield-social-position",
}
EXPECTED_HASHES = {
    STATEMENTS: "253f1edb34a5cba03c26503c9c30f6b89e3821b74f74bedd870cce8c865f2473",
    CANDIDATES: "7fabf2d3b66a7e5be63eaa4c0ff73c2de23ab129d9d0f710951d3d982d6865dd",
    MENTIONS: "c7b8d32482cf4d963e6cd77c992022eee9bd563f729c15c2e37aaf5777926dac",
    COVERAGE: "55de8f8eeb940d6cab7552e755a096d0fe95b6b647ae068ce87b8734167f27e3",
}
SOURCE_SHA256 = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp10-p281-semantic-20261013"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp10-p281-entities-20261013"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp10-p281-semantic-20261013"),
    COVERAGE: COVERAGE.with_name("s2-coverage.csv.bak-s2-chp10-p281-semantic-20261013"),
}
OLD_COVERAGE_NOTE = (
    "Printed p.281 body read against CHP-10.pdf physical page 10. Completed the Prince Eugene characterization begun at p.280 L61; recorded Sheffield's favour under Queen Anne, retirement and social position; Bellucci's Sheffield-mansion decorations; James Brydges/Canons, its London house and chapel, Handel/Pepusch concerts, Bellucci-Bagutti-Sleter decoration and the Canons canvas programme; the English patronage context, Pellegrini/Ricci/Bellucci assessment, Düsseldorf-London movements, Damini and Leoni, and Johann Wilhelm's Palatinate rule. OCR corrections recorded in S2 only: L126 'Arme'->'Anne' and 'andesteemed'->'and esteemed'; L137 'tfie-more'->'the more'; S0 remains unchanged. Footnote 1 at L128 and footnote 2 at L133 point to p.281 notes at source L518-L519 in the queued consolidated notes segment L491-634; note content remains pending. L139's revolt sentence was closed using p.282 L142 in the existing statement; the revolt remains unnamed and cross-page provenance is retained. P.281 footnote 1 at L518 and footnote 2 at L519 are now linked to the consolidated notes segment."
)
NEW_COVERAGE_NOTE = (
    "印刷p.281原有7条未分类statement现已完成S2裁决，并拆出Brydges年龄/贫困/任职及Sheffield年龄四项。"
    "将Duke of Chandos称号、Paymaster职务、Sheffield未识别天花板装饰及Düsseldorf-London-Paris城市组分别登记为来源限定候选；"
    "英语绘画评价保留为Haskell转述的学术判断。此前已完成的正文、跨页句、OCR校读和脚注挂点继续有效。"
    "注1/2由后置合并段L491-634承载，L518/L519挂点已建立；注释内容仍按该合并段自身进度处理。"
)
FALSE_NOTE = "This is a source-attributed descriptive, biographical, or critical claim; it does not assert a relation between the represented entities."
TRUE_NOTE = "This is an explicit source-attributed relation candidate; it remains at S2 and creates no formal S6 edge."


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(text: str) -> str:
    return " ".join(text.split())


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader), raw.startswith(b"\xef\xbb\xbf")


def csv_bytes(fields: list[str], rows: list[dict[str, str]], bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\r\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + buffer.getvalue().encode("utf-8")


def add_candidate(cid: str, name: str, kind: str, detail: str, line: int) -> dict[str, str]:
    return {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{line}",
    }


def add_mention(mid: str, cid: str, surface: str, note: str, text: str, occurrence: int = 0) -> dict[str, str]:
    positions = []
    cursor = 0
    while (index := text.find(surface, cursor)) >= 0:
        positions.append(index)
        cursor = index + 1
    if occurrence >= len(positions):
        raise SystemExit(f"mention not found: {mid} / {surface}")
    start = positions[occurrence]
    return {"mention_id": mid, "segment_id": SEGMENT, "candidate_id": cid,
            "surface_form": surface, "start_char": str(start),
            "end_char": str(start + len(surface)), "note": note}


def add_statement(sid: str, subject: str | None, object_: str | None, predicate: str,
                  quote: str, claim: str, first: int, last: int, mentioned: list[str],
                  relation: bool, note: str, qualification: str, *, extra: dict | None = None) -> dict:
    q = {
        "source_line_start": first, "source_line_end": last,
        "printed_page": 281, "pdf_physical_page": 10, "claim": claim,
        "speaker": "Haskell", "text_layer": "authorial narrative",
        "qualification": qualification, "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation, "relation_candidate_note": note,
    }
    if extra:
        q.update(extra)
    return {"statement_id": sid, "segment_id": SEGMENT,
            "subject_candidate_id": subject, "object_candidate_id": object_,
            "predicate": predicate, "qualifiers": q, "original_quote": quote,
            "origin": "book", "source_file": SOURCE_FILE}


def build() -> dict[Path, bytes]:
    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if sha256(raw[path]) != expected:
            raise SystemExit(f"input SHA mismatch: {path.relative_to(ROOT)}")
    source_bytes = SOURCE.read_bytes()
    if sha256(source_bytes) != SOURCE_SHA256:
        raise SystemExit("S0 source SHA mismatch")
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit("p.281 backup already exists; refusing to overwrite")
    lines = source_bytes.decode("utf-8").splitlines()
    segment_text = "\n".join(lines[124:139])
    if segment_text[117:127] != "Queen Arme":
        raise SystemExit("p.281 mention offset basis changed")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8").splitlines() if line.strip()]
    by_id = {r["statement_id"]: r for r in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs in source table")
    targets = {sid for sid, r in by_id.items() if r.get("segment_id") == SEGMENT and r["qualifiers"].get("relation_candidate") is None}
    if targets != TARGETS:
        raise SystemExit(f"p.281 unset target set changed: {sorted(targets)}")

    cfields, candidates, cbom = read_csv(CANDIDATES)
    mfields, mentions, mbom = read_csv(MENTIONS)
    covfields, coverage, covbom = read_csv(COVERAGE)
    candidate_ids = {r["candidate_id"] for r in candidates}
    mention_ids = {r["mention_id"] for r in mentions}
    new_candidates = [
        add_candidate("cand-11966", "Unidentified ceiling decoration with figures of gods and goddesses at Sheffield’s London mansion", "work",
                      "The contents of the mansion ceiling as described in Sheffield's quoted words. No maker, individual figures, or separate title is identified in this passage.", 126),
        add_candidate("cand-11967", "Düsseldorf, London, and Paris as centres for adventurous Venetian artists", "",
                      "Source-defined collective of the three named cities in Haskell's qualified account; membership is explicit and the 'great centres' assessment remains his.", 137),
        add_candidate("cand-11968", "First Duke of Chandos peerage title created for James Brydges in 1719", "term",
                      "The named title is represented separately from James Brydges as a person; the source gives the creation year and age, not the patent or grantor.", 128),
        add_candidate("cand-11969", "Office of Paymaster to the Forces", "term",
                      "Named office held by James Brydges for eight years according to Haskell; the exact dates and appointing authority are not supplied here.", 128),
    ]
    if any(r["candidate_id"] in candidate_ids for r in new_candidates):
        raise SystemExit("planned p.281 candidate ID already exists")
    new_mentions = [
        add_mention("m-chp10-p281-paymaster-office", "cand-11969", "Paymaster to the Forces",
                    "Named office held by James Brydges for eight years in Haskell's account.", segment_text),
        add_mention("m-chp10-p281-sheffield-ceiling-work", "cand-11966", "the ceiling",
                    "Unidentified decorative ceiling in Sheffield's mansion, distinguished from the separately described ceiling tribute in another room.", segment_text, occurrence=0),
        add_mention("m-chp10-p281-european-centres-group", "cand-11967", "Düsseldorf was with London and Paris",
                    "Collective location reference in Haskell's qualified account of centres for Venetian artists.", segment_text),
    ]
    if any(r["mention_id"] in mention_ids for r in new_mentions):
        raise SystemExit("planned p.281 mention ID already exists")
    mention_by_id = {r["mention_id"]: r for r in mentions}
    title_mention = mention_by_id["m-chp10-p281-duke_of_chandos"]
    title_mention["candidate_id"] = "cand-11968"
    title_mention["note"] = "The peerage title is distinct from James Brydges as a person; title candidate remains open for later alignment."

    quotes = {
        "st-chp10-p281-brydges-created-duke": (128, 128, "James Brydges, who managed to get himself created first Duke of Chandos in 1719"),
        "st-chp10-p281-brydges-fortune-paymaster": (128, 128, "he acquired an immense fortune from war profiteering"),
        "st-chp10-p281-english-support-venetian-painters": (134, 134, "Thus for a decade before about 1720 Venetian history painters received wide support in England."),
        "st-chp10-p281-english-work-assessment": (134, 134, "Most historians are agreed that the English work of Pellegrini, Ricci and Bellucci constitutes their greatest achievements."),
        "st-chp10-p281-european-centres-venetian-artists": (137, 137, "In fact, for a short time, Düsseldorf was with London and Paris one of the great centres of tfie-more adventurous Venetian artists."),
        "st-chp10-p281-sheffield-ceiling-description": (126, 126, "while the ceiling was, in his own words, ‘filled with figures of gods and goddesses’,"),
        "st-chp10-p281-sheffield-social-position": (126, 126, "despite his political affiliations had acquired a great and influential position in society."),
    }
    for sid, (first, last, quote) in quotes.items():
        row = by_id[sid]
        if row.get("source_file") != SOURCE_FILE or row["qualifiers"].get("relation_candidate") is not None:
            raise SystemExit(f"p.281 target changed: {sid}")
        span = " ".join(lines[first - 1:last])
        if normalize(quote) not in normalize(span):
            raise SystemExit(f"source quote mismatch: {sid}")

    def revise(sid: str, subject: str | None, object_: str | None, predicate: str,
               claim: str, is_relation: bool, note: str, mentioned: list[str],
               qualification: str, *, quote: str | None = None) -> None:
        row = by_id[sid]
        first, last, original = quotes[sid]
        if quote is not None:
            original = quote
        row["original_quote"] = original
        row["subject_candidate_id"], row["object_candidate_id"] = subject, object_
        row["predicate"] = predicate
        q = row["qualifiers"]
        q.update({"source_line_start": first, "source_line_end": last, "claim": claim,
                  "relation_candidate": is_relation, "relation_candidate_note": note,
                  "mentioned_candidate_ids": mentioned, "qualification": qualification})

    revise("st-chp10-p281-brydges-created-duke", "cand-0647", "cand-11968",
           "brydges-created-first-duke-of-chandos-title-in-1719",
           "Haskell says James Brydges managed to have himself created the first Duke of Chandos in 1719.",
           True, TRUE_NOTE, ["cand-0647", "cand-11968"],
           "The title is distinct from the person. The source says Brydges managed to get himself created; it does not identify the grantor. Age 46 is recorded separately.",
           quote="James Brydges, who managed to get himself created first Duke of Chandos in 1719")
    revise("st-chp10-p281-brydges-fortune-paymaster", "cand-0647", None,
           "brydges-acquires-fortune-from-war-profiteering",
           "Haskell says Brydges acquired an immense fortune from war profiteering.",
           False, FALSE_NOTE, ["cand-0647"],
           "This is Haskell's biographical attribution; the passage names no particular war or specific profiteering transaction.",
           quote="he acquired an immense fortune from war profiteering")
    revise("st-chp10-p281-english-support-venetian-painters", "cand-8948", "cand-4439",
           "venetian-history-painters-receive-wide-support-in-england-before-c1720",
           "Haskell says Venetian history painters received wide support in England for about a decade before c.1720.",
           True, TRUE_NOTE, ["cand-4439", "cand-8948", "cand-8949"],
           "This is a broad, approximate pattern, not an exhaustive list of painters or patrons.")
    revise("st-chp10-p281-english-work-assessment", None, None,
           "haskell-reports-historians-assess-english-work-as-greatest-achievements",
           "Haskell reports that most historians regarded the English work of Pellegrini, Ricci, and Bellucci as their greatest achievements.",
           False, FALSE_NOTE, ["cand-0282", "cand-1870", "cand-2154"],
           "This is Haskell's report of an unnamed scholarly consensus and a comparative critical judgment; neither individual historians nor works are identified.")
    revise("st-chp10-p281-european-centres-venetian-artists", "cand-11967", "cand-8948",
           "dusseldorf-london-paris-centres-for-adventurous-venetian-artists",
           "Haskell says Düsseldorf, London, and Paris were briefly among the great centres for more adventurous Venetian artists.",
           True, TRUE_NOTE, ["cand-11967", "cand-0955", "cand-1422", "cand-4653", "cand-8948"],
           "The duration is qualified as short; 'great centres' remains Haskell's assessment. The existing OCR correction 'tfie-more' to 'the more' is retained.")
    revise("st-chp10-p281-sheffield-ceiling-description", "cand-0465", "cand-11966",
           "sheffield-describes-unidentified-mansion-ceiling-as-filled-with-gods-and-goddesses",
           "Haskell quotes Sheffield describing the ceiling in his mansion as filled with figures of gods and goddesses.",
           True, TRUE_NOTE, ["cand-0465", "cand-11966", "cand-8928"],
           "Nested direct quotation attributed to Sheffield; no maker, individual figures, or separate title is identified. Keep it distinct from the allegorical ceiling tribute in another room.")
    revise("st-chp10-p281-sheffield-social-position", "cand-0465", None,
           "sheffield-acquires-influential-social-position",
           "Haskell says Sheffield had acquired a great and influential position in society despite his political affiliations.",
           False, FALSE_NOTE, ["cand-0465"],
           "This is Haskell's biographical and evaluative description; the political affiliations are not specified.",
           quote="despite his political affiliations had acquired a great and influential position in society.")

    extra = [
        add_statement("st-chp10-p281-brydges-age-at-ducal-creation", "cand-0647", None,
                      "brydges-aged-46-at-creation-of-ducal-title", "at the age of 46",
                      "Haskell says James Brydges was 46 when created first Duke of Chandos.",
                      128, 128, ["cand-0647", "cand-11968"], False, FALSE_NOTE,
                      "The age and title are Haskell's report; the note marker refers to the same consolidated footnote source as the title statement.",
                      extra={"footnote_marker": 1, "footnote_text_pending": False,
                             "footnote_link_status": "resolved_source_migration",
                             "footnote_segment": "chp-10:10_CHP-10_intro:l491-634",
                             "footnote_source_line": 518, "footnote_note_statement_ids": []}),
        add_statement("st-chp10-p281-brydges-born-in-poverty", "cand-0647", None,
                      "brydges-born-in-poverty", "Though born in poverty",
                      "Haskell says James Brydges was born in poverty.",
                      128, 128, ["cand-0647"], False, FALSE_NOTE,
                      "This is Haskell's biographical claim; no independent evidence is asserted here."),
        add_statement("st-chp10-p281-brydges-paymaster-service", "cand-0647", "cand-11969",
                      "brydges-served-as-paymaster-to-the-forces-for-eight-years",
                      "after having served for eight years as Paymaster to the Forces.",
                      "Haskell says Brydges served as Paymaster to the Forces for eight years before acquiring his fortune.",
                      128, 128, ["cand-0647", "cand-11969"], True, TRUE_NOTE,
                      "No exact dates or appointing authority are supplied; keep the office distinct from the person."),
        add_statement("st-chp10-p281-sheffield-aged-67", "cand-0465", None,
                      "sheffield-aged-67-by-time-of-queen-annes-death",
                      "He was by then aged 67",
                      "Haskell says Sheffield was 67 by the time Queen Anne died.",
                      126, 126, ["cand-0465", "cand-0110"], False, FALSE_NOTE,
                      "'By then' refers to the period after Anne's death, as stated in the preceding sentence."),
    ]
    for row in extra:
        if row["statement_id"] in by_id:
            raise SystemExit(f"new statement ID already exists: {row['statement_id']}")
        quote = row["original_quote"]
        first, last = row["qualifiers"]["source_line_start"], row["qualifiers"]["source_line_end"]
        if normalize(quote) not in normalize(" ".join(lines[first - 1:last])):
            raise SystemExit(f"new quote mismatch: {row['statement_id']}")

    all_candidate_ids = candidate_ids | {r["candidate_id"] for r in new_candidates}
    for row in extra:
        for cid in [row.get("subject_candidate_id"), row.get("object_candidate_id"),
                    *row["qualifiers"].get("mentioned_candidate_ids", [])]:
            if cid and cid not in all_candidate_ids:
                raise SystemExit(f"new statement candidate missing: {row['statement_id']} -> {cid}")
    for row in new_mentions:
        a, b = int(row["start_char"]), int(row["end_char"])
        if segment_text[a:b] != row["surface_form"]:
            raise SystemExit(f"new mention span mismatch: {row['mention_id']}")
    for row in mentions:
        if row["mention_id"] == "m-chp10-p281-duke_of_chandos" and row["candidate_id"] != "cand-11968":
            raise SystemExit("Duke of Chandos mention remap failed")

    new_coverage_rows = 0
    for row in coverage:
        if row.get("segment_id") == SEGMENT:
            new_coverage_rows += 1
            if row.get("note") != OLD_COVERAGE_NOTE:
                raise SystemExit("p.281 coverage row preflight failed")
            row["note"] = NEW_COVERAGE_NOTE
    if new_coverage_rows != 1:
        raise SystemExit(f"expected one p.281 coverage row, found {new_coverage_rows}")

    out_statements: list[dict] = []
    added_ids = {r["statement_id"] for r in extra}
    for row in rows:
        out_statements.append(row)
        if row["statement_id"] == "st-chp10-p281-brydges-created-duke":
            out_statements.append(extra[0])
        elif row["statement_id"] == "st-chp10-p281-brydges-fortune-paymaster":
            out_statements.extend(extra[1:3])
        elif row["statement_id"] == "st-chp10-p281-sheffield-social-position":
            out_statements.append(extra[3])
    if len(out_statements) != len(rows) + len(extra):
        raise SystemExit("statement insertion count mismatch")
    p281 = [r for r in out_statements if r.get("segment_id") == SEGMENT]
    if any(r["qualifiers"].get("relation_candidate") not in (True, False) for r in p281):
        raise SystemExit("p.281 segment still contains unclassified statements")

    return {
        STATEMENTS: ("\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in out_statements) + "\n").encode("utf-8"),
        CANDIDATES: csv_bytes(cfields, candidates + new_candidates, cbom),
        MENTIONS: csv_bytes(mfields, mentions + new_mentions, mbom),
        COVERAGE: csv_bytes(covfields, coverage, covbom),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve remaining S2 statements in CHP-10 p.281.")
    parser.add_argument("--apply", action="store_true", help="write after protected dry-run checks pass")
    args = parser.parse_args()
    outputs = build()
    print("p.281 semantic preflight: PASS")
    print("classified: 7 existing statements; added: 4 atomic statements, 4 candidates, 3 mentions")
    if not args.apply:
        print("dry-run only; no files written")
        return
    for path, expected in EXPECTED_HASHES.items():
        if sha256(path.read_bytes()) != expected:
            raise SystemExit(f"input changed after preflight: {path.relative_to(ROOT)}")
    for original, backup in BACKUPS.items():
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(original, backup)
    temp_paths: dict[Path, Path] = {}
    try:
        for target, data in outputs.items():
            fd, name = tempfile.mkstemp(prefix=f".{target.stem}.p281-", dir=target.parent)
            with os.fdopen(fd, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            temp_paths[target] = Path(name)
        for target, temp in temp_paths.items():
            os.replace(temp, target)
    finally:
        for temp in temp_paths.values():
            if temp.exists():
                temp.unlink()
    print("p.281 protected apply: PASS")
    for path in outputs:
        print(f"{path.relative_to(ROOT)} sha256={sha256(path.read_bytes())}")


if __name__ == "__main__":
    main()
