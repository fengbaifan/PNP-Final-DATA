#!/usr/bin/env python3
"""Apply the source-backed S2 review stage for current order 1301-1600.

The 300 current rows are fingerprint-checked first. Existing PASS and pending
decisions are reused where their source/version remains exact; only directly
resolved findings receive statement and mention edits. Run without --apply to
preview. The H9622 event ledger and relations.csv are read-only invariants.
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
STAGE_ID = "2026-11-02-s2-current-review-stage-b404-b406-order-1301-1600"
PDF_HASH = "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e"
SOURCE_HASH = "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_i.md"


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
        ["git", "show", f"{revision}:04-knowledge/tables/mentions.csv"], cwd=ROOT
    ).decode("utf-8-sig")
    return {
        row["mention_id"]: row
        for row in csv.DictReader(io.StringIO(raw, newline=""))
        if row["segment_id"] == segment_id
    }


def append_once(value: str, suffix: str) -> str:
    return value if suffix in value else value.rstrip() + " " + suffix


def append_ids(values: list[str], *candidate_ids: str) -> list[str]:
    result = list(values)
    for candidate_id in candidate_ids:
        if candidate_id not in result:
            result.append(candidate_id)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if sha256((ROOT / "02-sources/01-book/CHP-2.pdf").read_bytes()) != PDF_HASH:
        raise SystemExit("CHP-2.pdf changed")
    if sha256((ROOT / SOURCE_FILE).read_bytes()) != SOURCE_HASH:
        raise SystemExit("Current CHP-2 Markdown changed")
    pdf = fitz.open(ROOT / "02-sources/01-book/CHP-2.pdf")
    if "29" not in pdf[9].get_text() or "the artistic revolution" not in pdf[10].get_text():
        raise SystemExit("CHP-2 printed p.29/p.30 page locator check failed")

    segments = {
        row["segment_id"]: row
        for line in (TABLES / "segments.jsonl").read_text(
                encoding="utf-8-sig").splitlines() if line.strip()
        for row in [json.loads(line)]
    }
    source_cache: dict[str, str] = {}

    def source_text(segment_id: str) -> str:
        if segment_id not in source_cache:
            segment = segments[segment_id]
            lines = (ROOT / segment["source_file"]).read_text(
                encoding="utf-8-sig").splitlines()
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
    target_rows = {
        row["statement_id"]: row for row in roster
        if 1301 <= int(row["current_order"]) <= 1600
    }
    if len(target_rows) != 300:
        raise SystemExit(f"Expected 300 roster rows; found {len(target_rows)}")
    initial = Counter(row["current_review_status"] for row in target_rows.values())
    if initial != Counter({"reviewed_current_pass": 163,
                           "reviewed_current_pending": 137}):
        raise SystemExit(f"Unexpected stage-entry status totals: {initial}")

    mentions_by_segment: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in mentions:
        mentions_by_segment[row["segment_id"]].append(row)

    for row in target_rows.values():
        sid = row["statement_id"]
        statement = statement_by_id[sid]
        segment = segments[statement["segment_id"]]
        if row["current_statement_sha256"] != canonical_hash(statement):
            raise SystemExit(f"Current statement fingerprint mismatch: {sid}")
        if row["segment_sha256"] != segment["sha256"]:
            raise SystemExit(f"Current segment fingerprint mismatch: {sid}")
        source_hash = sha256((ROOT / segment["source_file"]).read_bytes())
        if row["source_asset_sha256"] != source_hash:
            raise SystemExit(f"Current source asset fingerprint mismatch: {sid}")
        seg_id = statement["segment_id"]
        current_mentions = sorted(mentions_by_segment[seg_id],
                                  key=lambda item: item["mention_id"])
        if row["current_segment_mention_count"] != str(len(current_mentions)):
            raise SystemExit(f"Current mention count mismatch: {sid}")
        if row["current_segment_mentions_sha256"] != canonical_hash(current_mentions):
            raise SystemExit(f"Current mention fingerprint mismatch: {sid}")

    p29 = "chp-2:02_CHP-2_sec_i:l95-106"
    p30 = "chp-2:02_CHP-2_sec_i:l108-119"
    p25_31 = "chp-2:02_CHP-2_sec_i:l124-157"
    new_mentions: list[dict[str, str]] = []

    def add_mention(mid: str, segment_id: str, candidate_id: str,
                    surface: str, note: str) -> None:
        if mid in by_mention or any(row["mention_id"] == mid for row in new_mentions):
            raise SystemExit(f"Duplicate mention id: {mid}")
        text = source_text(segment_id)
        if text.count(surface) != 1:
            raise SystemExit(f"Source span is not unique: {mid}: {surface!r}")
        start = text.index(surface)
        if text[start:start + len(surface)] != surface:
            raise SystemExit(f"Source span assertion failed: {mid}")
        new_mentions.append({
            "mention_id": mid,
            "segment_id": segment_id,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(start + len(surface)),
            "note": note,
        })

    add_mention(
        "m-chp2-seci-20261102-additional-giustiniani-room-works", p29,
        "cand-11568",
        "along with others by the\nCarracci, the great masters of the Venetian High Renaissance and by Luca Cambiaso",
        "Exact p.29 source-defined group of additional paintings; distinct from the thirteen Caravaggio paintings cand-4316.",
    )
    add_mention(
        "m-chp2-seci-20261102-large-room-old-pictures", p29, "cand-4315",
        "the ‘large room with old pictures’ in his palace",
        "Exact local place span for the room in which the source reports the paintings were hung.",
    )
    add_mention(
        "m-chp2-seci-20261102-venetian-masters-collective", p29, "cand-11569",
        "the great masters of the Venetian High Renaissance",
        "Exact source-defined creator collective; membership and taxonomy type remain open.",
    )
    add_mention(
        "m-chp2-seci-20261102-contemporary-art", p29, "cand-4338",
        "contemporary art",
        "Exact p.29 concept anchor for Haskell's interpretation of Giustiniani's display arrangement.",
    )
    add_mention(
        "m-chp2-seci-20261102-giustiniani-essay", p29, "cand-4322",
        "an essay",
        "Exact anchor for the untitled essay Haskell says Giustiniani wrote; title and publication details remain unspecified.",
    )
    add_mention(
        "m-chp2-seci-20261102-salerno-inventory-citation", p29, "cand-4324",
        "the inventory of his pictures published by Salerno",
        "Exact p.29 n.5 short-form citation anchor; mapped to the unique Salerno bibliography item, citation pointer only.",
    )
    add_mention(
        "m-chp2-seci-20261102-hopf-investigators", p29, "cand-11580",
        "Dr. Salerno and other investigators",
        "Exact source-defined collective; unnamed members and organizational identity remain unresolved.",
    )
    add_mention(
        "m-chp2-seci-20261102-maffeo-old-master-paintings", p30, "cand-11567",
        "paintings—by old masters such as Raphael, Correggio, Andrea del Sarto,\nGiulio Romano, Parmigianino and others",
        "Exact non-exhaustive group of old-master paintings Haskell says decorated Maffeo Barberini's palace.",
    )
    add_mention(
        "m-chp2-seci-20261102-paul-scipione-joint-actor", p30, "cand-11582",
        "Pope Paul V and his nephew Scipione Borghese",
        "Exact joint-actor group span; the source does not allocate individual works or commissions between them.",
    )
    add_mention(
        "m-chp2-seci-20261102-artistic-revolution", p30, "cand-11875",
        "artistic revolution that had occurred at the end of the sixteenth century",
        "Exact retrospective term span; identity/scope remains for S3 and is not merged by wording alone.",
    )
    add_mention(
        "m-chp2-seci-20261102-bizoni-giustiniani", p25_31, "cand-1200",
        "Giustiniani’s",
        "Exact local person anchor in the p.30 n.1 phrase ‘Giustiniani’s friend Bernardo Bizoni’; no longer friendship is inferred.",
    )

    mentions_after = mentions + new_mentions
    if len({row["mention_id"] for row in mentions_after}) != len(mentions_after):
        raise SystemExit("Mention ID collision")
    for row in new_mentions:
        text = source_text(row["segment_id"])
        start, end = int(row["start_char"]), int(row["end_char"])
        if text[start:end] != row["surface_form"]:
            raise SystemExit(f"Final exact-span assertion failed: {row['mention_id']}")
        mentions_by_segment[row["segment_id"]].append(row)

    changed_statement_ids: set[str] = set()

    def update_statement(sid: str, mutate) -> None:
        statement = statement_by_id[sid]
        before = json.dumps(statement, ensure_ascii=False, sort_keys=True)
        mutate(statement)
        after = json.dumps(statement, ensure_ascii=False, sort_keys=True)
        if before != after:
            changed_statement_ids.add(sid)

    def add_candidates(statement: dict, *candidate_ids: str) -> None:
        q = statement["qualifiers"]
        q["mentioned_candidate_ids"] = append_ids(
            q.get("mentioned_candidate_ids", []), *candidate_ids
        )

    def fix_collection_claim(statement: dict) -> None:
        q = statement["qualifiers"]
        q["claim"] = (
            "Haskell says Vincenzo was filling his palace near S. Luigi dei Francesi "
            "and country house at Bassano di Sutri with antique sculpture and one of "
            "Rome's most remarkable collections of paintings."
        )
        q["qualification"] = (
            "‘Most remarkable’ and ‘in Rome’ are Haskell's comparative scope and "
            "evaluation, not an objective ranking or a claim about every work in the collection."
        )

    update_statement("st-chp2-seci-l95-106-collection-holdings", fix_collection_claim)

    candidate_additions = {
        "st-chp2-seci-l95-106-other-paintings-part-of-collection": ("cand-11568",),
        "st-chp2-seci-l95-106-thirteen-displayed": ("cand-4315",),
        "st-chp2-seci-l95-106-cambiaso-collection": ("cand-11568",),
        "st-chp2-seci-l95-106-carracci-collection": ("cand-11568",),
        "st-chp2-seci-l95-106-other-paintings-location": ("cand-4315", "cand-11568"),
        "st-chp2-seci-l95-106-venetian-collection": ("cand-11569", "cand-11568"),
        "st-chp2-seci-l95-106-contemporary-art-level": ("cand-4338",),
        "st-chp2-seci-l95-106-essay-authored": ("cand-4322",),
        "st-chp2-seci-l95-106-essay-purpose": ("cand-4322",),
        "st-chp2-seci-l95-106-citation-faldi": ("cand-4331",),
        "st-chp2-seci-l95-106-citation-portoghesi": ("cand-4326",),
        "st-chp2-seci-l95-106-citation-salerno": ("cand-4324",),
        "st-chp2-seci-l95-106-hopf-untraceable": ("cand-11580",),
        "st-chp2-seci-l108-119-recognised-artistic-revolution": ("cand-11875",),
        "st-chp2-seci-l108-119-palace-paintings-by-andrea-del-sarto": ("cand-11567",),
        "st-chp2-seci-l108-119-palace-paintings-by-correggio": ("cand-11567",),
        "st-chp2-seci-l108-119-palace-paintings-by-raphael": ("cand-11567",),
        "st-chp2-seci-l108-119-palace-paintings-by-giulio-romano": ("cand-11567",),
        "st-chp2-seci-l108-119-palace-paintings-by-parmigianino": ("cand-11567",),
        "st-chp2-seci-l108-119-paul-v-and-scipione-patronage": ("cand-11582",),
        "st-chp2-seci-l124-157-giustiniani-friend-bizoni": ("cand-1200",),
    }
    for sid, candidate_ids in candidate_additions.items():
        update_statement(sid, lambda statement, ids=candidate_ids:
                         add_candidates(statement, *ids))

    citation_mentions = {
        "st-chp2-seci-l95-106-citation-salerno":
            "m-chp2-seci-20261102-salerno-inventory-citation",
        "st-chp2-seci-l95-106-citation-portoghesi":
            "m-chp2-seci-l95-106-0075",
        "st-chp2-seci-l95-106-citation-faldi":
            "m-chp2-seci-l95-106-0077",
    }
    for sid, mid in citation_mentions.items():
        update_statement(sid, lambda statement, mention_id=mid:
                         statement["qualifiers"].__setitem__(
                             "citation_mention_ids", [mention_id]))

    alignment_additions = {
        "cand-11567": (
            "S2 adds exact non-exhaustive old-master paintings anchor "
            "m-chp2-seci-20261102-maffeo-old-master-paintings; no titles, count, or complete membership inferred."
        ),
        "cand-11568": (
            "S2 adds exact additional-paintings group anchor "
            "m-chp2-seci-20261102-additional-giustiniani-room-works; keep distinct from the thirteen Caravaggio works cand-4316."
        ),
        "cand-11569": (
            "S2 adds exact source-defined collective anchor "
            "m-chp2-seci-20261102-venetian-masters-collective; creator-group type and membership remain unresolved."
        ),
        "cand-11580": (
            "S2 adds exact unnamed-investigators group anchor m-chp2-seci-20261102-hopf-investigators; members/type remain unresolved."
        ),
        "cand-11582": (
            "S2 adds exact joint-actor anchor m-chp2-seci-20261102-paul-scipione-joint-actor; the source does not allocate individual works to either person."
        ),
        "cand-11875": (
            "S2 adds exact term anchor m-chp2-seci-20261102-artistic-revolution; keep its retrospective scope distinct pending S3."
        ),
        "cand-4315": (
            "S2 adds exact local place anchor m-chp2-seci-20261102-large-room-old-pictures; the room is identified as the location for the displayed works."
        ),
        "cand-4322": (
            "S2 adds exact mention m-chp2-seci-20261102-giustiniani-essay for the source's untitled essay; title/date/publication remain unspecified."
        ),
        "cand-4324": (
            "S2 adds p.29 n.5 citation anchor m-chp2-seci-20261102-salerno-inventory-citation; cited article contents not consulted."
        ),
        "cand-4326": (
            "p.29 n.5 uses the existing exact local author mention m-chp2-seci-l95-106-0075; the unique author/year and book bibliography identify the publication candidate, while the cited article was not independently consulted."
        ),
        "cand-4331": (
            "p.29 n.5 uses the existing exact local author mention m-chp2-seci-l95-106-0077; the unique author/year and book bibliography identify the publication candidate, while the cited article was not independently consulted."
        ),
        "cand-4338": (
            "S2 adds exact concept anchor m-chp2-seci-20261102-contemporary-art; type/identity mapping remains undecided."
        ),
    }
    for candidate_id, suffix in alignment_additions.items():
        row = by_alignment[candidate_id]
        row["resolution_note"] = append_once(row["resolution_note"], suffix)

    # Replace stale statements in S3 notes where the only prior blocker was a missing anchor.
    for candidate_id in ("cand-11567", "cand-4315", "cand-4338"):
        row = by_alignment[candidate_id]
        row["resolution_note"] = row["resolution_note"].replace(
            "有 candidate_source_ref，但 mentions.csv 未提供对应提及行；缺少 S2 mention-level 锚点，待补核后再裁决。",
            ""
        ).replace(
            "Index locator only; no linked S2 mention establishes the referent sufficiently for same/new. Retain for source-level identity review.",
            ""
        )

    pass_notes = {
        "st-chp2-seci-l95-106-other-paintings-part-of-collection": "p.29正文同段先报告Giustiniani的painting collection，再明确称large room中的additional paintings；新增cand-11568精确组mention，与现有collection mention对应。保持作品组与集合边界，不指认具体作品。",
        "st-chp2-seci-l95-106-collection-holdings": "p.29正文核对并恢复‘one of the most remarkable collections of paintings in Rome’的比较级与地域范围；保留Haskell评价，不作客观排名。",
        "st-chp2-seci-l95-106-thirteen-displayed": "p.29明确‘large room with old pictures’陈列thirteen by Caravaggio；补地点cand-4315的本地mention，沿用既有作品组cand-4316锚点，不补造作品题名。",
        "st-chp2-seci-l95-106-cambiaso-collection": "p.29正文明确Giustiniani房间中的additional paintings包括Luca Cambiaso作品；补cand-11568作品组锚点，原文不提供单件题名。",
        "st-chp2-seci-l95-106-carracci-collection": "p.29正文明确Giustiniani房间中的additional paintings包括Carracci作品；补cand-11568作品组锚点，保留Carracci collective，不拆成未命名个人。",
        "st-chp2-seci-l95-106-other-paintings-location": "p.29正文明确additional paintings与thirteen Caravaggio works一同悬挂在large room；补房间cand-4315及作品组cand-11568精确mention。",
        "st-chp2-seci-l95-106-contemporary-art-level": "p.29正文直接以‘contemporary art’描述Giustiniani陈列安排所体现的艺术排序；补cand-4338精确术语span，保留Haskell解释性而非量化排名。",
        "st-chp2-seci-l95-106-essay-authored": "p.29正文直接称Giustiniani wrote an essay；补未题名essay候选cand-4322的精确mention，不补题名、日期或出版信息。",
        "st-chp2-seci-l95-106-essay-purpose": "p.29正文说明该essay用于理论化eclecticism并显示对多种风格的辨识；补cand-4322 mention，保留essay未题名及内容未独立查阅。",
        "st-chp2-seci-l95-106-citation-faldi": "p.29注5列出Italo Faldi的1957年文章；该作者/年份与书目唯一Faldi文章对应。复用既有原文作者mention m-chp2-seci-l95-106-0077作为引注锚点，只记录Haskell的引注路径，不声称已读该文。",
        "st-chp2-seci-l95-106-citation-portoghesi": "p.29注5列出Paolo Portoghesi的1957年文章；与书目唯一Portoghesi article title对应。复用既有原文作者mention m-chp2-seci-l95-106-0075作为引注锚点，只记录引注路径。",
        "st-chp2-seci-l95-106-citation-salerno": "p.29注5将Giustiniani picture inventory归于Salerno；新增该inventory citation mention并沿用书目唯一候选cand-4324，不声称查阅Salerno文章。",
        "st-chp2-seci-l95-106-hopf-untraceable": "p.29正文明确Dr. Salerno与other investigators未能追查Hopf的作品；新增来源定义的群体mention，成员/机构身份继续由S3处理。",
        "st-chp2-seci-l108-119-recognised-artistic-revolution": "印刷p.30正文直接称Giustiniani almost alone realised the full implications of an artistic revolution at the end of the sixteenth century；新增cand-11875原文跨度，保留Haskell回顾性判断。",
        "st-chp2-seci-l108-119-palace-paintings-by-andrea-del-sarto": "印刷p.30直接列出Maffeo palace中的old-master paintings by Andrea del Sarto；新增非穷尽作品组cand-11567的精确mention。",
        "st-chp2-seci-l108-119-palace-paintings-by-correggio": "印刷p.30直接列出Maffeo palace中的old-master paintings by Correggio；新增非穷尽作品组cand-11567的精确mention。",
        "st-chp2-seci-l108-119-palace-paintings-by-raphael": "印刷p.30直接列出Maffeo palace中的old-master paintings by Raphael；新增非穷尽作品组cand-11567的精确mention。",
        "st-chp2-seci-l108-119-palace-paintings-by-giulio-romano": "印刷p.30直接列出Maffeo palace中的old-master paintings by Giulio Romano；新增非穷尽作品组cand-11567的精确mention。",
        "st-chp2-seci-l108-119-palace-paintings-by-parmigianino": "印刷p.30直接列出Maffeo palace中的old-master paintings by Parmigianino；新增非穷尽作品组cand-11567的精确mention。",
        "st-chp2-seci-l108-119-paul-v-and-scipione-patronage": "印刷p.30明确Paul V与Scipione Borghese这一共同主体及Ludovisi时期对Bernini output的对照；补cand-11582精确group mention，不将共同概括拆成二人各自委托。",
        "st-chp2-seci-l124-157-giustiniani-friend-bizoni": "印刷p.30注1明确‘Giustiniani’s friend Bernardo Bizoni’；补Vincenzo Giustiniani在该局部语境的mention，限于来源所称friend，不推断关系持续时间。",
    }
    if len(pass_notes) != 21:
        raise SystemExit(f"Expected 21 resolved pending findings, got {len(pass_notes)}")
    if not set(pass_notes).issubset(target_rows):
        raise SystemExit("Resolved statement falls outside this stage")
    if any(target_rows[sid]["current_review_status"] != "reviewed_current_pending"
           for sid in pass_notes):
        raise SystemExit("A resolved statement was not pending at stage entry")

    batch_specs = [
        (1301, 1400, "S2-B404-CH2-1301-1400",
         "2026-11-02-s2-current-review-b404-order-1301-1400"),
        (1401, 1500, "S2-B405-CH2-1401-1500",
         "2026-11-02-s2-current-review-b405-order-1401-1500"),
        (1501, 1600, "S2-B406-CH2-1501-1600",
         "2026-11-02-s2-current-review-b406-order-1501-1600"),
    ]
    changed_segments = {row["segment_id"] for row in new_mentions}
    statement_hashes = {sid: canonical_hash(row) for sid, row in statement_by_id.items()}
    for row in roster:
        sid = row["statement_id"]
        statement = statement_by_id[sid]
        segment = segments[statement["segment_id"]]
        order = int(row["current_order"]) if row["current_order"] else -1
        if 1301 <= order <= 1600:
            batch_id, anchor = next(
                (batch, ref) for lo, hi, batch, ref in batch_specs if lo <= order <= hi
            )
            previous_ref = row["review_evidence_ref"]
            row["review_batch_id"] = batch_id
            row["review_evidence_ref"] = "stages.md#" + anchor
            if sid in pass_notes:
                row["current_review_status"] = "reviewed_current_pass"
                row["review_outcome"] = "current_pending_finding_resolved_after_source_anchor_review"
                row["follow_up_note"] = pass_notes[sid] + " 前次记录：" + previous_ref + "。"
            elif row["current_review_status"] == "reviewed_current_pending":
                row["review_outcome"] = "current_open_finding_retained_after_exact_version_check"
                row["follow_up_note"] = (
                    row["follow_up_note"] +
                    " 本阶段核对当前statement/source/mention指纹与既有原页审读一致；未发现新增依据，沿用原finding并保留pending。前次记录：" +
                    previous_ref + "。"
                )
            else:
                row["review_outcome"] = "reused_exact_current_pass_after_targeted_stage_review"
                row["follow_up_note"] = (
                    "复用既有当前PASS；本行当前statement/source/mention指纹与原页审读一致。前次记录："
                    + previous_ref + "。"
                )
        if sid in changed_statement_ids:
            row["current_statement_sha256"] = statement_hashes[sid]
            if int(row["history_9622_event_count"] or "0") > 0:
                match = ("exact" if row["history_9622_latest_statement_sha256"]
                         == statement_hashes[sid] else "changed")
                row["history_9622_current_statement_match"] = match
                row["prior_review_match"] = (
                    "exact_object_and_source_segment"
                    if match == "exact" and row["history_9622_source_match"] == "true"
                    else "historical_object_or_source_differs"
                )
        if segment["segment_id"] in changed_segments:
            seg_mentions = sorted(mentions_by_segment[segment["segment_id"]],
                                  key=lambda item: item["mention_id"])
            row["current_segment_mention_count"] = str(len(seg_mentions))
            row["current_segment_mentions_sha256"] = canonical_hash(seg_mentions)

    historical_cache: dict[tuple[str, str], dict[str, dict[str, str]]] = {}
    history_delta_rows_changed = 0
    for row in roster:
        segment_id = row["segment_id"]
        if (int(row["history_9622_event_count"] or "0") <= 0
                or segment_id not in changed_segments):
            continue
        cache_key = (row["history_9622_latest_review_commit"], segment_id)
        if cache_key not in historical_cache:
            historical_cache[cache_key] = git_mentions(*cache_key)
        prior = historical_cache[cache_key]
        current = {item["mention_id"]: item
                   for item in mentions_by_segment[segment_id]}
        delta = {
            "changed": sorted(mid for mid in prior.keys() & current.keys()
                              if prior[mid] != current[mid]),
            "removed": sorted(prior.keys() - current.keys()),
            "added": sorted(current.keys() - prior.keys()),
        }
        encoded = json.dumps(delta, ensure_ascii=False, separators=(",", ":"))
        if row["history_9622_mention_delta"] != encoded:
            history_delta_rows_changed += 1
        row["history_9622_mention_delta"] = encoded

    stage_after = Counter(row["current_review_status"]
                          for row in target_rows.values())
    status_after = Counter(row["current_review_status"] for row in roster)
    if stage_after != Counter({"reviewed_current_pass": 184,
                               "reviewed_current_pending": 116}):
        raise SystemExit(f"Unexpected stage-final status totals: {stage_after}")
    if status_after != Counter({"reviewed_current_pass": 8658,
                                "reviewed_current_pending": 6847}):
        raise SystemExit(f"Unexpected full-roster status totals: {status_after}")
    batch_totals = {}
    for lo, hi, batch_id, _ in batch_specs:
        counts = Counter(row["current_review_status"] for row in roster
                         if lo <= int(row["current_order"]) <= hi)
        expected = {
            1301: Counter({"reviewed_current_pass": 86,
                           "reviewed_current_pending": 14}),
            1401: Counter({"reviewed_current_pass": 79,
                           "reviewed_current_pending": 21}),
            1501: Counter({"reviewed_current_pass": 19,
                           "reviewed_current_pending": 81}),
        }[lo]
        if counts != expected:
            raise SystemExit(f"Unexpected {batch_id} status totals: {counts}")
        batch_totals[batch_id] = [counts["reviewed_current_pass"],
                                  counts["reviewed_current_pending"]]

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
            json.dumps(statement_by_id[sid], ensure_ascii=False) + ending
        )

    ledger_hash = sha256(LEDGER_PATH.read_bytes())
    relations_hash = sha256(RELATIONS_PATH.read_bytes())
    result = {
        "stage": STAGE_ID,
        "order_range": "1301-1600",
        "current_pass_reused": 163,
        "pending_version_checked": 137,
        "pending_resolved_to_pass": len(pass_notes),
        "pending_retained": stage_after["reviewed_current_pending"],
        "stage_after_pass_pending": [stage_after["reviewed_current_pass"],
                                     stage_after["reviewed_current_pending"]],
        "full_roster_after_pass_pending": [status_after["reviewed_current_pass"],
                                           status_after["reviewed_current_pending"]],
        "batch_pass_pending": batch_totals,
        "changed_statement_ids": sorted(changed_statement_ids),
        "new_mentions": len(new_mentions),
        "changed_mention_segments": sorted(changed_segments),
        "history_mention_delta_rows_changed": history_delta_rows_changed,
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
    print("applied_stage_1301_1600_without_changing_H9622_or_relations")


if __name__ == "__main__":
    main()
