#!/usr/bin/env python3
"""Apply the source-backed S2 review stage for current order 1001-1300.

Run without --apply for a dry-run. The H9622 event ledger and relations.csv
are read-only invariants.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[3]
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process"
TABLES = ROOT / "04-knowledge/tables"
ROSTER_PATH = PROCESS / "s2-current-review-roster.csv"
LEDGER_PATH = PROCESS / "s2-history-9622-review-events.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
MENTIONS_PATH = TABLES / "mentions.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
RELATIONS_PATH = TABLES / "relations.csv"
STAGE_ID = "2026-11-02-s2-current-review-stage-b401-b403-order-1001-1300"
PDF_HASHES = {
    "02-sources/01-book/CHP-1.pdf": "0b9a3ca88e6f09209bd20185948e18a68f527d0628e893940a7e3f07f6d22c86",
    "02-sources/01-book/CHP-2.pdf": "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e",
}
SOURCE_HASHES = {
    "02-sources/02-Markdown/01_CHP-1_sec_ii.md": "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
    "02-sources/02-Markdown/02_CHP-2_sec_i.md": "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")
    return sha256(data)


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader), list(reader.fieldnames or [])


def write_csv(rows: list[dict[str, str]], fields: list[str],
              line_ending: str = "\n") -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=line_ending,
                            extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return b"\xef\xbb\xbf" + stream.getvalue().encode("utf-8")


def read_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    lines = path.read_text(encoding="utf-8-sig").splitlines(keepends=True)
    return [json.loads(line) for line in lines if line.strip()], lines


def git_mentions(revision: str, segment_id: str) -> dict[str, dict[str, str]]:
    raw = subprocess.check_output(
        ["git", "show", f"{revision}:04-knowledge/tables/mentions.csv"],
        cwd=ROOT,
    ).decode("utf-8-sig")
    return {
        row["mention_id"]: row
        for row in csv.DictReader(io.StringIO(raw, newline=""))
        if row["segment_id"] == segment_id
    }


def append_once(value: str, suffix: str) -> str:
    return value if suffix in value else value.rstrip() + " " + suffix


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    for rel, expected in {**PDF_HASHES, **SOURCE_HASHES}.items():
        actual = sha256((ROOT / rel).read_bytes())
        if actual != expected:
            raise SystemExit(f"Source changed: {rel}: {actual}")

    pdf1 = fitz.open(ROOT / "02-sources/01-book/CHP-1.pdf")
    pdf2 = fitz.open(ROOT / "02-sources/01-book/CHP-2.pdf")
    if "Gualandi" not in pdf1[7].get_text() or "23" not in pdf1[21].get_text():
        raise SystemExit("CHP-1 PDF page locator check failed")
    for page_no, needle in [(8, "Their main resources"), (9, "most hedonistic society"),
                            (10, "effeminate young boys")]:
        if needle not in pdf2[page_no - 1].get_text():
            raise SystemExit(f"CHP-2 PDF page locator check failed: p.{page_no}")

    segments = {}
    for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            row = json.loads(line)
            segments[row["segment_id"]] = row
    source_cache: dict[str, str] = {}

    def source_text(segment_id: str) -> str:
        if segment_id not in source_cache:
            segment = segments[segment_id]
            lines = (ROOT / segment["source_file"]).read_text(
                encoding="utf-8-sig"
            ).splitlines()
            source_cache[segment_id] = "\n".join(
                lines[segment["line_start"] - 1:segment["line_end"]]
            )
        return source_cache[segment_id]

    statements, statement_lines = read_jsonl(STATEMENTS_PATH)
    statement_by_id = {row["statement_id"]: row for row in statements}
    mentions, mention_fields = read_csv(MENTIONS_PATH)
    alignments, alignment_fields = read_csv(ALIGNMENT_PATH)
    roster, roster_fields = read_csv(ROSTER_PATH)
    by_alignment = {row["candidate_id"]: row for row in alignments}
    by_mention = {row["mention_id"]: row for row in mentions}
    roster_rows = {
        row["statement_id"]: row for row in roster
        if 1001 <= int(row["current_order"]) <= 1300
    }
    if len(roster_rows) != 300:
        raise SystemExit(f"Expected 300 roster rows; found {len(roster_rows)}")

    initial = Counter(row["current_review_status"] for row in roster_rows.values())
    if initial != Counter({"reviewed_current_pass": 267, "reviewed_current_pending": 33}):
        raise SystemExit(f"Unexpected stage-entry statuses: {initial}")

    mentions_by_segment: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in mentions:
        mentions_by_segment[row["segment_id"]].append(row)
    touched_segments = {
        "chp-1:01_CHP-1_sec_ii:l168-239",
        "chp-2:02_CHP-2_sec_i:l82-93",
        "chp-2:02_CHP-2_sec_i:l95-106",
    }
    for row in roster_rows.values():
        sid = row["statement_id"]
        statement = statement_by_id[sid]
        segment = segments[statement["segment_id"]]
        actual_source_hash = sha256((ROOT / segment["source_file"]).read_bytes())
        if row["current_statement_sha256"] != canonical_hash(statement):
            raise SystemExit(f"Statement fingerprint mismatch before review: {sid}")
        if row["segment_sha256"] != segment["sha256"]:
            raise SystemExit(f"Segment fingerprint mismatch before review: {sid}")
        if row["source_asset_sha256"] != segment["asset_sha256"]:
            raise SystemExit(f"Source asset fingerprint mismatch before review: {sid}")
        if row["source_asset_sha256"] != actual_source_hash:
            raise SystemExit(f"Current Markdown asset mismatch: {sid}")
        seg_id = statement["segment_id"]
        if row["current_segment_mention_count"] != str(len(mentions_by_segment[seg_id])):
            raise SystemExit(f"Mention count mismatch before review: {sid}")
        if row["current_segment_mentions_sha256"] != canonical_hash(
                sorted(mentions_by_segment[seg_id], key=lambda item: item["mention_id"])):
            raise SystemExit(f"Mention fingerprint mismatch before review: {sid}")

    new_mentions: list[dict[str, str]] = []

    def add_mention(mid: str, segment_id: str, candidate_id: str, surface: str,
                    occurrence: int, note: str) -> None:
        if mid in by_mention or any(row["mention_id"] == mid for row in new_mentions):
            raise SystemExit(f"Duplicate mention id: {mid}")
        text = source_text(segment_id)
        starts = []
        cursor = 0
        while True:
            found = text.find(surface, cursor)
            if found < 0:
                break
            starts.append(found)
            cursor = found + 1
        if occurrence >= len(starts):
            raise SystemExit(f"Exact source surface not found: {mid}: {surface}")
        start = starts[occurrence]
        if text[start:start + len(surface)] != surface:
            raise SystemExit(f"Span assertion failed: {mid}")
        row = {
            "mention_id": mid,
            "segment_id": segment_id,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(start + len(surface)),
            "note": note,
        }
        new_mentions.append(row)

    ch1 = "chp-1:01_CHP-1_sec_ii:l168-239"
    ch2p28 = "chp-2:02_CHP-2_sec_i:l82-93"
    ch2p29 = "chp-2:02_CHP-2_sec_i:l95-106"
    add_mention(
        "m-chp1-secii-20261102-gualandi-volume-i-p9", ch1, "cand-6608",
        "Gualandi, I, p. 91", 0,
        "Printed p.9 n.2 locator for Gualandi volume I; cited contents not independently consulted.",
    )
    add_mention(
        "m-chp1-secii-20261102-gualandi-volume-i-p13", ch1, "cand-6608",
        "Gualandi, I, p. 91", 1,
        "Printed p.13 n.4 locator for Gualandi volume I; cited contents not independently consulted.",
    )
    add_mention(
        "m-chp1-secii-20261102-ferri-laparelli-altarpiece", ch1, "cand-3190",
        "an altarpiece in Cortona for Annibale Laparclli", 0,
        "Exact footnote mention; source OCR spelling is retained in the span and corrected to Laparelli from CHP-1.pdf.",
    )
    add_mention(
        "m-chp1-secii-20261102-cortona-modelli-series", ch1, "cand-11872",
        "a series of modelli by Pietro da Cortona", 0,
        "Exact p.12 n.1 work-group anchor; Haskell reports the attribution as disputed.",
    )
    add_mention(
        "m-chp1-secii-20261102-procaccini-parents", ch1, "cand-11866",
        "Andrea Procaccini’s parents", 0,
        "Exact p.20 n.4 source-defined parent-group anchor; individual identities remain unnamed.",
    )
    add_mention(
        "m-chp2-seci-l82-93-20261102-joint-pope-ludovisi", ch2p28, "cand-11578",
        "The new Pope and his vigorous young nephew Ludovico\nLudovisi", 0,
        "Exact joint-actor group anchor; do not assign separate agency to either person.",
    )
    add_mention(
        "m-chp2-seci-l82-93-20261102-pincio-hedonistic-society", ch2p28, "cand-11579",
        "the most hedonistic society that Rome had known since the Renaissance", 0,
        "Exact source-defined unnamed social-collective anchor; membership and type remain open.",
    )
    add_mention(
        "m-chp2-seci-l95-106-20261102-caravaggio-canvases", ch2p29, "cand-4305",
        "a series of canvases of effeminate young boys", 0,
        "Exact anchor for the untitled, uncounted Caravaggio work group; distinct from the Giustiniani set.",
    )
    mentions_after = mentions + new_mentions
    if len({row["mention_id"] for row in mentions_after}) != len(mentions_after):
        raise SystemExit("Mention id collision")
    for row in new_mentions:
        mentions_by_segment[row["segment_id"]].append(row)
    for row in mentions_after[-len(new_mentions):]:
        text = source_text(row["segment_id"])
        start, end = int(row["start_char"]), int(row["end_char"])
        if text[start:end] != row["surface_form"]:
            raise SystemExit(f"Final source-span assertion failed: {row['mention_id']}")

    changed_statement_ids: set[str] = set()

    def update_statement(statement_id: str, mutate) -> None:
        statement = statement_by_id[statement_id]
        before = json.dumps(statement, ensure_ascii=False, sort_keys=True)
        mutate(statement)
        after = json.dumps(statement, ensure_ascii=False, sort_keys=True)
        if before != after:
            changed_statement_ids.add(statement_id)

    def set_page(statement: dict, printed: int, physical: int) -> None:
        q = statement["qualifiers"]
        q["printed_page"] = printed
        q["pdf_physical_page"] = physical

    def fix_gualandi_p9(statement: dict) -> None:
        statement["object_candidate_id"] = "cand-6608"
        q = statement["qualifiers"]
        q["claim"] = (
            "Haskell cites Gualandi, volume I, page 91, for the account of Camillo "
            "Gavasetti receiving the subject and freedom to elaborate it."
        )
        q["qualification"] = (
            "This records Haskell’s citation path and locator only. Map the volume-I "
            "locator to cand-6608, distinct from the six-volume bibliography set "
            "cand-11348; the cited page contents were not independently consulted."
        )
        q["mentioned_candidate_ids"] = [
            "cand-3477", "cand-6608", "cand-1124", "cand-3194"
        ]
        q["citation_candidate_id"] = "cand-3477"
        q["citation_publication_candidate_id"] = "cand-6608"
        q["citation_locator"] = "Gualandi, I, p. 91"
        q["citations"] = [{
            "source_candidate_id": "cand-3477",
            "publication_candidate_id": "cand-6608",
            "locator": "Gualandi, I, p. 91",
        }]
        q["citation_mention_ids"] = ["m-chp1-secii-20261102-gualandi-volume-i-p9"]
        q["cited_material_not_independently_consulted"] = True
        q["relation_candidate_note"] = (
            "This records Haskell’s citation path and locator; it does not independently "
            "verify the cited contents."
        )

    update_statement("st-chp1-secii-p9-n2-cites-gualandi-i-p91", fix_gualandi_p9)

    def fix_gualandi_p13(statement: dict) -> None:
        q = statement["qualifiers"]
        q["citation_mention_ids"] = [
            "m-chp1-secii-20261102-gualandi-volume-i-p13"
        ]
        q["relation_candidate_note"] = (
            "This records Haskell’s citation path and locator to the volume-I candidate "
            "cand-6608; it does not independently verify the cited contents."
        )

    update_statement("st-chp1-secii-p13-n4-cites-gualandi-i-p91-gavasetti", fix_gualandi_p13)

    for sid in [
        "st-chp1-secii-l971-n1-cites-ruffo-correspondence-p172",
        "st-chp1-secii-l971-n1-derosis-letter-addressed-to",
        "st-chp1-secii-l971-n1-derosis-letter-authored-by",
        "st-chp1-secii-l971-973-06",
        "st-chp1-secii-l973-n2-cites-baldinucci-vol6-p579",
        "st-chp1-secii-l974-n3-cites-ruffo-correspondence-p298",
        "st-chp1-secii-l974-n3-ferri-letter-addressed-to",
        "st-chp1-secii-l974-n3-ferri-letter-authored-by",
        "st-chp1-secii-l974-980-07",
        "st-chp1-secii-l978-980-n3-cites-pascoli-vol1-p233",
    ]:
        update_statement(sid, lambda statement: set_page(statement, 23, 22))

    def fix_maderno(statement: dict) -> None:
        q = statement["qualifiers"]
        q["claim"] = (
            "Haskell attributes the proposal to add a nave to St Peter’s to Carlo Maderno."
        )
        q["qualification"] = (
            "The source clause continues from the preceding segment; this statement records "
            "Maderno as proposer and does not duplicate the preceding claim about Paul V "
            "and Michelangelo’s plan."
        )

    update_statement("st-chp2-seci-l71-80-maderno-nave-continuation", fix_maderno)

    antecedent = "st-chp2-seci-l55-69-paul-michelangelo-plan"

    def link_maffeo(statement: dict, extra_qualification: str) -> None:
        q = statement["qualifiers"]
        related = q.setdefault("related_body_statement_ids", [])
        linked = q.setdefault("linked_body_statement_ids", [])
        if antecedent not in related:
            related.append(antecedent)
        if antecedent not in linked:
            linked.append(antecedent)
        q["related_segment"] = "chp-2:02_CHP-2_sec_i:l55-69"
        q["relation_candidate_note"] = extra_qualification

    update_statement(
        "st-chp2-seci-l71-80-spoleto-bishopric",
        lambda statement: link_maffeo(
            statement,
            "The continued pronoun is linked to the preceding Maffeo Barberini statement. "
            "The source names Spoleto and the bishopric; appointing authority and exact date remain unstated.",
        ),
    )
    update_statement(
        "st-chp2-seci-l71-80-bologna-legate",
        lambda statement: link_maffeo(
            statement,
            "The continued pronoun is linked to the preceding Maffeo Barberini statement. "
            "Haskell reports Bologna and the 1611 legateship and evaluates the post; no appointing authority is inferred.",
        ),
    )

    def qualify_agucchi(statement: dict) -> None:
        q = statement["qualifiers"]
        q["claim"] = (
            "Haskell says Agucchi sketched out a theory of art from his artist contacts and "
            "literary reading, especially Aristotle, and—tentatively, in Haskell’s words, "
            "“no doubt”—from his temperament, during retirement from public life between 1607 and 1615."
        )
        q["qualification"] = (
            "Haskell’s “no doubt” marks the proposed influence of Agucchi’s temperament as "
            "the author’s conjecture, not a documented cause. The source gives a period, "
            "not exact start or end dates."
        )

    update_statement("st-chp2-seci-l82-93-agucchi-theory-development", qualify_agucchi)

    alignment_additions = {
        "cand-6608": (
            "S2 current review adds exact volume-I locator anchors "
            "m-chp1-secii-20261102-gualandi-volume-i-p9 and "
            "m-chp1-secii-20261102-gualandi-volume-i-p13 and corrects the p.9 citation "
            "from set-level cand-11348 to volume-I candidate cand-6608. Keep the volume "
            "candidate distinct from the six-volume set; title/edition remain unspecified, "
            "so this alignment stays undecided."
        ),
        "cand-3190": (
            "S2 current review adds exact altarpiece mention "
            "m-chp1-secii-20261102-ferri-laparelli-altarpiece at p.13 n.1; the printed "
            "name correction and citation limitation remain explicit."
        ),
        "cand-11872": (
            "S2 current review adds exact disputed-series mention "
            "m-chp1-secii-20261102-cortona-modelli-series; Haskell’s non-acceptance "
            "qualification is preserved and the same KU remains distinct from other modelli."
        ),
        "cand-11578": (
            "S2 current review adds exact joint-actor mention "
            "m-chp2-seci-l82-93-20261102-joint-pope-ludovisi; the group remains untyped "
            "and no separate agency is assigned."
        ),
        "cand-11579": (
            "S2 current review adds exact unnamed-social-collective mention "
            "m-chp2-seci-l82-93-20261102-pincio-hedonistic-society; membership and type "
            "remain unresolved."
        ),
    }
    for candidate_id, suffix in alignment_additions.items():
        row = by_alignment[candidate_id]
        if candidate_id == "cand-6608" and row["decision"] != "undecided":
            raise SystemExit("Unexpected cand-6608 alignment decision")
        row["resolution_note"] = append_once(row["resolution_note"], suffix)

    set_row = by_alignment["cand-11348"]
    old_ref = "st-chp1-secii-p9-n2-cites-gualandi-i-p91,"
    set_row["resolution_note"] = set_row["resolution_note"].replace(old_ref, "")
    set_row["resolution_note"] = append_once(
        set_row["resolution_note"],
        "S2 p.9 n.2 is now anchored to volume-I citation candidate cand-6608; retain this "
        "candidate as the distinct six-volume bibliography-level set.",
    )

    parent_alignment = by_alignment["cand-11866"]
    parent_alignment["resolution_note"] = (
        "group=sg3-term-cand-11866; source_ref=chp-1:01_CHP-1_sec_ii:l168-239#L850; "
        "current S2 mention=m-chp1-secii-20261102-procaccini-parents@chars=8561-8588 "
        "(Andrea Procaccini’s parents). This anchors the source-defined group but does not "
        "identify either parent or resolve the group’s type; retain undecided. Pascoli, "
        "II, p.400 was not independently consulted."
    )
    canvas_alignment = by_alignment["cand-4305"]
    canvas_alignment["resolution_note"] = (
        "source_ref=entity-candidates.csv#cand-4305; "
        "candidate_source_ref=chp-2:02_CHP-2_sec_i:l95-106#L97; "
        "current S2 mention=m-chp2-seci-l95-106-20261102-caravaggio-canvases@chars=370-415. "
        "The anchor supports an untitled, uncounted work group attributed by Haskell to "
        "Caravaggio; no unique existing work KU or exact object identity is established, "
        "so retain undecided."
    )

    pass_notes = {
        "st-chp1-secii-p9-n2-cites-gualandi-i-p91": "印刷p.9注2与PDF物理页8逐字核对；新增卷I定位mention，并将publication端点从六卷集合cand-11348改为卷I候选cand-6608。只记录Haskell引文路径，不声称已读Gualandi原页。",
        "st-chp1-secii-p12-n1-grassi-cortona-series-claim": "印刷p.12注1明言Grassi提出该系列归属且Haskell说明未获普遍接受；补入系列作品组的精确mention，保留争议限定，relation_candidate仍为false。",
        "st-chp1-secii-p13-n1-ferri-laparelli-altarpiece-payment": "印刷p.13注1核对deposit、完成付款及Laparelli委托；补入altarpiece精确mention。名称OCR校读有原页依据，Gualandi页未独立查阅。",
        "st-chp1-secii-p13-n4-cites-gualandi-i-p91-gavasetti": "印刷p.13注4核对Gualandi卷I页91定位；新增出版物locator mention并沿用卷I候选cand-6608，不据此声称已查阅被引页。",
        "st-chp1-secii-l657-n1-cites-malvasia-vol2-p27": "印刷p.16注1明确以“corre voce”引出对Paul V言论的审慎归属；既有formal引证rel-2095指向书目所列1841版，未把被引页内容当作已核实事实。",
        "st-chp1-secii-p19-n6-cerquozzi-passeri-citation": "印刷p.19注6直接写“Of Michelangelo Cerquozzi—Passeri, p.285”；本行保留脚注对前述引文的归属语境，relation_candidate=false，单独的cites=true statement承载正式引用，不重复建立边。",
        "st-chp1-secii-notes-procaccini-parents": "印刷p.20注4直接报告Procaccini父母的态度及未阻止其从业；新增父母组精确mention。Pascoli页未独立查阅，父母身份和组类型继续在S3待决。",
        "st-chp1-secii-l971-n1-cites-ruffo-correspondence-p172": "印刷p.23注1核对V. Ruffo出版物页172的引文定位；补足来源印刷页和PDF物理页，不声称已查阅被引信件。",
        "st-chp1-secii-l971-n1-derosis-letter-addressed-to": "印刷p.23注1明确该1663年信件收件人为Don Antonio Ruffo；补足来源页码，不推断持续通信关系。",
        "st-chp1-secii-l971-n1-derosis-letter-authored-by": "印刷p.23注1明确该1663年信件作者为Giuseppe de Rosis；补足来源页码，不推断持续通信关系。",
        "st-chp1-secii-l973-n2-cites-baldinucci-vol6-p579": "印刷p.23注2明确引Baldinucci第VI卷579页；补足来源页码，引用内容未独立查阅。",
        "st-chp1-secii-l974-n3-cites-ruffo-correspondence-p298": "印刷p.23注3明确以Ruffo出版物第298页定位Ferri的1672年信件；补足来源页码，不推断持续通信关系。",
        "st-chp1-secii-l974-n3-ferri-letter-addressed-to": "印刷p.23注3明确Ferri信件收件人为Don Antonio Ruffo；补足来源页码，保留单封信件角色。",
        "st-chp1-secii-l974-n3-ferri-letter-authored-by": "印刷p.23注3明确Ferri为该信作者；补足来源页码，保留单封信件角色。",
        "st-chp1-secii-l978-980-n3-cites-pascoli-vol1-p233": "印刷p.23注3明确引Pascoli第I卷233页；补足来源页码，引用内容未独立查阅。",
        "st-chp2-seci-l71-80-maderno-nave-continuation": "印刷p.27正文完成跨段句子，明确Maderno为增建圣彼得中殿方案的提出者；只记录提出者，不重复前段对Paul V与Michelangelo方案的陈述。",
        "st-chp2-seci-l71-80-spoleto-bishopric": "印刷p.27正文以跨段代词承接前段已识别的Maffeo；链接前段statement后可确定所指。原文只称其被任命为主教，不补造任命者或日期。",
        "st-chp2-seci-l71-80-bologna-legate": "印刷p.27正文以同一跨段代词承接Maffeo；原文明载1611年前往Bologna任legate，保留Haskell对职位的评价，不推断任命者。",
        "st-chp2-seci-l71-80-arpino-picture-seizure": "印刷p.27正文明确Scipione以没收方式从d’Arpino处取得105幅画并含数量未明的Caravaggio作品；现有画组和d’Arpino mention均可精确定位，不补造单件作品。",
        "st-chp2-seci-l71-80-deposition-removal": "印刷p.27正文明确Deposition来自Baglioni家族礼拜堂、奉Scipione之命夜间转入其收藏；各端点mention已有锚点，不推断后续所有权或现藏地。",
        "st-chp2-seci-l71-80-domenichino-commission": "印刷p.27正文明确Aldobrandini委托Domenichino创作Hunt of Diana；按原文保留红衣主教称谓与作品，不补造未出现的名字或委托执行结果。",
        "st-chp2-seci-l71-80-domenichino-imprisonment": "印刷p.27正文直接称Domenichino因履行与Aldobrandini的合同而入狱；保留未说明的监禁执行者，不作归因。",
        "st-chp2-seci-l82-93-reni-commission": "印刷p.28正文明确Scipione委托Guido Reni、Bernini及其他艺术家，并以Aurora为Reni实例；保持对Reni的具体范围，不概括到全部艺术家。",
        "st-chp2-seci-l82-93-villa-social-setting": "印刷p.28正文直接称Pincio别墅是该社会群体的中心；新增精确群体mention。成员、边界和类型仍未定，S3保持undecided，未建S6边。",
        "st-chp2-seci-l82-93-domenichino-supremacy": "印刷p.28正文明确新教皇及其侄子Ludovico共同作用；新增joint-group mention，保留共同主体，类型仍待S3厘清。",
        "st-chp2-seci-l82-93-guercino-supremacy": "印刷p.28正文明确新教皇及其侄子Ludovico共同作用；新增joint-group mention，保留共同主体，类型仍待S3厘清。",
        "st-chp2-seci-l82-93-agucchi-theory-development": "印刷p.28正文的“no doubt”明确是Haskell对Agucchi temperament影响的推测；已将不确定性写回claim/qualification，保留1607–1615为时期而非精确起讫日期。",
        "st-chp2-seci-l95-106-canvases-by-caravaggio": "印刷p.29正文直接归于Caravaggio一组描绘effeminate young boys的画布；新增精确作品组mention。标题和数量仍未知，并与Giustiniani十三幅画分开。",
    }
    retain_notes = {
        "st-chp1-secii-l971-973-06": "印刷p.23注1、注2分别谈De Rosis信件和Baldinucci引文；当前statement将两项合并，且person-to-person端点与独立信件角色statement重复。保留pending，待拆分/去重后再评。",
        "st-chp1-secii-l974-980-07": "印刷p.23注3并列Ferri与Luti两项不同patronage主张；当前statement合并两人且端点落在相邻信件收件人Ruffo。保留pending，待分拆各自主张并校正端点。",
        "st-chp2-seci-l71-80-resources-st-peters": "印刷p.27的“their”指Paul V与Scipione的共同资源，当前仅有Paul V端点且无对应来源组候选；保留pending，不把共同主体归给一人。",
        "st-chp2-seci-l71-80-smm-family-chapel-comparison": "印刷p.27称S. Maria Maggiore的“family chapel”，但该处语境同时提Paul V、Scipione及Barberini；当前候选的家族身份仍需S3核明，保留pending。",
        "st-chp2-seci-l71-80-scipione-art-change": "印刷p.27的“these changes”回指前段多项艺术变化，当前statement把Paul V设为对象而无对应term端点；保留pending，待正确对象候选建立。",
    }
    if set(pass_notes) & set(retain_notes) or set(pass_notes) | set(retain_notes) != {
            sid for sid, row in roster_rows.items()
            if row["current_review_status"] == "reviewed_current_pending"}:
        raise SystemExit("Decision notes do not cover exactly the 33 current pending statements")

    batch_specs = [
        (1001, 1100, "S2-B401-CH1-SECII-1001-1100", "2026-11-02-s2-current-review-b401-order-1001-1100"),
        (1101, 1200, "S2-B402-CH1-SECII-1101-1200", "2026-11-02-s2-current-review-b402-order-1101-1200"),
        (1201, 1300, "S2-B403-CH1-CH2-1201-1300", "2026-11-02-s2-current-review-b403-order-1201-1300"),
    ]
    changed_segments = {row["segment_id"] for row in new_mentions}
    statement_hashes = {sid: canonical_hash(row) for sid, row in statement_by_id.items()}
    for row in roster:
        sid = row["statement_id"]
        statement = statement_by_id[sid]
        segment = segments[statement["segment_id"]]
        seg_mentions = mentions_by_segment[statement["segment_id"]]
        order = int(row["current_order"]) if row["current_order"] else -1
        if 1001 <= order <= 1300:
            batch_id, anchor = next(
                (batch, ref) for lo, hi, batch, ref in batch_specs if lo <= order <= hi
            )
            previous_ref = row["review_evidence_ref"]
            row["review_batch_id"] = batch_id
            row["review_evidence_ref"] = "stages.md#" + anchor
            if sid in pass_notes:
                row["current_review_status"] = "reviewed_current_pass"
                row["review_outcome"] = "current_pending_finding_resolved_after_original_page_review"
                row["follow_up_note"] = pass_notes[sid] + " 前次记录：" + previous_ref + "。"
            elif sid in retain_notes:
                row["current_review_status"] = "reviewed_current_pending"
                row["review_outcome"] = "current_open_finding_retained_after_original_page_review"
                row["follow_up_note"] = retain_notes[sid] + " 前次记录：" + previous_ref + "。"
            else:
                row["review_outcome"] = "reused_exact_current_pass_after_targeted_stage_review"
                row["follow_up_note"] = (
                    "复用既有当前PASS；本行完整statement和来源定位未变。本阶段新增的mention锚点仅对应单独重审的pending statement。前次记录："
                    + previous_ref + "。"
                )
        if sid in changed_statement_ids:
            row["current_statement_sha256"] = statement_hashes[sid]
            if int(row["history_9622_event_count"] or "0") > 0:
                match = (
                    "exact"
                    if row["history_9622_latest_statement_sha256"] == statement_hashes[sid]
                    else "changed"
                )
                row["history_9622_current_statement_match"] = match
                row["prior_review_match"] = (
                    "exact_object_and_source_segment"
                    if match == "exact" and row["history_9622_source_match"] == "true"
                    else "historical_object_or_source_differs"
                )
        if segment["segment_id"] in changed_segments:
            row["current_segment_mention_count"] = str(len(seg_mentions))
            row["current_segment_mentions_sha256"] = canonical_hash(
                sorted(seg_mentions, key=lambda item: item["mention_id"])
            )

    historical_cache: dict[tuple[str, str], dict[str, dict[str, str]]] = {}
    for row in roster:
        segment_id = row["segment_id"]
        if (int(row["history_9622_event_count"] or "0") <= 0
                or segment_id not in changed_segments):
            continue
        revision = row["history_9622_latest_review_commit"]
        cache_key = (revision, segment_id)
        if cache_key not in historical_cache:
            historical_cache[cache_key] = git_mentions(*cache_key)
        old = historical_cache[cache_key]
        current = {item["mention_id"]: item for item in mentions_by_segment[segment_id]}
        changed = sorted(mid for mid in old.keys() & current.keys() if old[mid] != current[mid])
        removed = sorted(old.keys() - current.keys())
        added = sorted(current.keys() - old.keys())
        row["history_9622_mention_delta"] = json.dumps(
            {"changed": changed, "removed": removed, "added": added},
            ensure_ascii=False, separators=(",", ":"),
        )

    status_after = Counter(row["current_review_status"] for row in roster)
    stage_after = Counter(row["current_review_status"] for row in roster_rows.values())
    if stage_after != Counter({"reviewed_current_pass": 295, "reviewed_current_pending": 5}):
        raise SystemExit(f"Unexpected stage-final status totals: {stage_after}")
    if status_after != Counter({"reviewed_current_pass": 8637, "reviewed_current_pending": 6868}):
        raise SystemExit(f"Unexpected full-roster status totals: {status_after}")

    changed_lines = []
    for line in statement_lines:
        if not line.strip():
            changed_lines.append(line)
            continue
        row = json.loads(line)
        sid = row["statement_id"]
        if sid not in changed_statement_ids:
            changed_lines.append(line)
            continue
        ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        changed_lines.append(
            json.dumps(statement_by_id[sid], ensure_ascii=False, separators=(",", ":")) + ending
        )

    ledger_hash = sha256(LEDGER_PATH.read_bytes())
    relations_hash = sha256(RELATIONS_PATH.read_bytes())
    result = {
        "stage": STAGE_ID,
        "order_range": "1001-1300",
        "current_pass_reused": 267,
        "pending_re_reviewed": 33,
        "pending_resolved_to_pass": len(pass_notes),
        "pending_retained": len(retain_notes),
        "stage_after_pass_pending": [stage_after["reviewed_current_pass"],
                                     stage_after["reviewed_current_pending"]],
        "full_roster_after_pass_pending": [status_after["reviewed_current_pass"],
                                           status_after["reviewed_current_pending"]],
        "changed_statement_ids": sorted(changed_statement_ids),
        "new_mentions": len(new_mentions),
        "changed_mention_segments": sorted(changed_segments),
        "history_ledger_sha256": ledger_hash,
        "relations_sha256": relations_hash,
        "apply": args.apply,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    changed_statements_raw = b"\xef\xbb\xbf" + "".join(changed_lines).encode("utf-8")
    STATEMENTS_PATH.write_bytes(changed_statements_raw)
    MENTIONS_PATH.write_bytes(write_csv(mentions_after, mention_fields))
    ALIGNMENT_PATH.write_bytes(write_csv(alignments, alignment_fields))
    ROSTER_PATH.write_bytes(write_csv(roster, roster_fields, "\r\n"))
    if sha256(LEDGER_PATH.read_bytes()) != ledger_hash:
        raise SystemExit("H9622 historical event ledger changed unexpectedly")
    if sha256(RELATIONS_PATH.read_bytes()) != relations_hash:
        raise SystemExit("relations.csv changed unexpectedly")
    print("applied_stage_1001_1300_without_changing_H9622_or_relations")


if __name__ == "__main__":
    main()
