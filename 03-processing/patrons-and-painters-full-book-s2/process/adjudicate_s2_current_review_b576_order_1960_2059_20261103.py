#!/usr/bin/env python3
"""Reconcile and adjudicate the B576 S2 window (current orders 1960-2059)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process"
RESULTS = ROOT / "03-processing/patrons-and-painters-full-book-s2/results"

STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ROSTER_PATH = PROCESS / "s2-current-review-roster.csv"
HISTORY_PATH = PROCESS / "s2-history-9622-review-events.csv"
SEGMENTS_PATH = TABLES / "segments.jsonl"
MENTIONS_PATH = TABLES / "mentions.csv"
CANDIDATES_PATH = TABLES / "entity-candidates.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
RELATIONS_PATH = TABLES / "relations.csv"
INDEX_PATH = ROOT / "02-sources/03-Index/03-2-Index-CSV/M.csv"
SOURCE_PATH = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_iv.md"
PDF_PATH = ROOT / "02-sources/01-book/CHP-2.pdf"
UNIT_PATH = ROOT / "04-knowledge/units/persons/carlo-maderno.md"
STAGES_PATH = PROCESS / "stages.md"
KNOWLEDGE_PATH = PROCESS / "knowledge.md"
RESULT_STAGES_PATH = RESULTS / "stages.md"
CURRENT_RESULT_PATH = ROOT / "04-knowledge/results/patrons-and-painters-full-book-s2.md"

BASE_HEAD = "5c16ab337d9476adf8e2f85ee7675d0c566708c9"
PDF_SHA256 = "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e"
SOURCE_SHA256 = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
HISTORY_SHA256 = "75ab12df478a816035929353565b0301d55959c6bb13d9b511af072c4c931c89"
BATCH_ID = "S2-B576-CH2-1960-2059"
STAGE_ID = "2026-11-03-s2-current-review-b576-order-1960-2059"
KNOWLEDGE_ANCHOR = "s3-targeted-cand-1479-maderno-20261103"
KNOWLEDGE_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    + KNOWLEDGE_ANCHOR
)
EVIDENCE_REF = f"stages.md#{STAGE_ID}"
SAME_KU = "units/persons/carlo-maderno"
WINDOW_START, WINDOW_END = 1960, 2059

PROMOTED = {
    "st-chp2-seciv-l45-52-taddeo-age-and-election-context":
        "补入Taddeo与Urban VIII映射；年龄限于Urban VIII当选教宗时。",
    "st-chp2-seciv-l45-52-taddeo-dynastic-role":
        "Barberini记作预期王朝、Europe记作比较范围，不当作已实现亲缘关系。",
    "st-chp2-seciv-l45-52-taddeo-lieutenant-general":
        "补入Taddeo与papal armies映射，保留约略任命时间。",
    "st-chp2-seciv-l45-52-taddeo-marriage":
        "补入Taddeo、未具名Colonna女儿及Colonna家族映射，不推测女方姓名。",
    "st-chp2-seciv-l45-52-taddeo-palestrina-purchase":
        "补入Taddeo与Principality of Palestrina映射，保留两年后的相对时间。",
    "st-chp2-seciv-l45-52-taddeo-prefect-title":
        "补入Taddeo、Prefect of Rome职位及Rome映射，保留1631年。",
    "st-chp2-seciv-l45-52-taddeo-succeeds-father-command":
        "补入Taddeo、未具名父亲及papal armies映射，不推定身份和继任日期。",
    "st-chp2-seciv-l45-52-della-rovere-prior-prefecture":
        "补入Della Rovere、职位及Urbino映射，保留家族范围。",
    "st-chp2-seciv-l45-52-taddeo-income-ranking":
        "将Italy记为比较范围，不作关系对象。",
    "st-chp2-seciv-l45-52-urban-viii-intended-assertion-of-rights":
        "补入Urban VIII与Taddeo映射，仅记录Urban VIII的意图。",
    "st-chp2-seciv-l45-52-francesco-transfer-sforza-palace-in-1626":
        "补入Francesco、Taddeo、Sforza palace三方映射，明确palace是转让资产。",
    "st-chp2-seciv-l45-52-barberini-new-palace-plan":
        "补入Barberini、新建palace与既有Sforza palace映射；计划与既成事实分开。",
    "st-chp2-seciv-l45-52-bernini-restored-s-bibiana":
        "补入Bernini与S. Bibiana映射；沿用原页校读only restored。",
    "st-chp2-seciv-l45-52-taddeo-approached-maderno":
        "补入Taddeo、Carlo Maderno、Rome与the Pope映射；类型纠正后S3 aln-1814复用既有Maderno KU。",
    "st-chp2-seciv-l54-63-barberini-palace-largest-private-palace":
        "Rome改作比较范围，不投射palace-to-city关系。",
    "st-chp2-seciv-l54-63-barberini-supremacy-symbolized":
        "保留Haskell的政治象征解释，relation_candidate改为false。",
    "st-chp2-seciv-l54-63-facade-precedents-around-rome":
        "Rome改作地理比较范围；保留façade/villa比较及almost only限定，relation_candidate改为false。",
    "st-chp2-seciv-l54-63-new-era-periodization":
        "确认是修辞性断代句，mention数组为空，不造event端点。",
}

RETAINED = {
    "st-chp2-seciv-l45-52-precedence-claims-resisted":
        "待证：提出及抵抗precedence claims的主体未明；移除无据Urban VIII施事者和Taddeo/使馆端点。",
    "st-chp2-seciv-l45-52-sforza-family-sale-at-valmontone":
        "待证：seller=Sforza family、buyer=Francesco、地点=Valmontone已拆清；property本身未被识别为独立资产端点。",
    "st-chp2-seciv-l45-52-maderno-or-collaborator-design-fragment":
        "待证：原文保留Maderno或更可能的未具名collaborator/adviser两种归属，设计关系主体未唯一确定。",
    "st-chp2-seciv-l45-52-taddeo-surrounding-land-purchases":
        "待证：原文未识别具体surrounding-land地块；移除Barberini palace这一错误购买对象。",
    "st-chp2-seciv-l54-63-barberini-palace-departure-from-tradition":
        "待证：延续p.47的设计归属不确定；cand-1479已纠正类型并对齐，但不据此选定设计者。",
}

MENTION_MAPS = {
    "st-chp2-seciv-l45-52-taddeo-age-and-election-context": ["cand-0239", "cand-0209"],
    "st-chp2-seciv-l45-52-taddeo-dynastic-role": ["cand-0239", "cand-0198", "cand-3462"],
    "st-chp2-seciv-l45-52-taddeo-lieutenant-general": ["cand-0239", "cand-4644"],
    "st-chp2-seciv-l45-52-taddeo-marriage": ["cand-0239", "cand-4639", "cand-4638"],
    "st-chp2-seciv-l45-52-taddeo-palestrina-purchase": ["cand-0239", "cand-4215"],
    "st-chp2-seciv-l45-52-taddeo-prefect-title": ["cand-0239", "cand-4645", "cand-4490"],
    "st-chp2-seciv-l45-52-taddeo-succeeds-father-command": ["cand-0239", "cand-4640", "cand-4644"],
    "st-chp2-seciv-l45-52-della-rovere-prior-prefecture": ["cand-4646", "cand-4645", "cand-4648"],
    "st-chp2-seciv-l45-52-taddeo-income-ranking": ["cand-0239", "cand-3461"],
    "st-chp2-seciv-l45-52-precedence-claims-resisted": ["cand-4647"],
    "st-chp2-seciv-l45-52-urban-viii-intended-assertion-of-rights": ["cand-0209", "cand-0239"],
    "st-chp2-seciv-l45-52-francesco-transfer-sforza-palace-in-1626":
        ["cand-3035", "cand-0239", "cand-4620"],
    "st-chp2-seciv-l45-52-sforza-family-sale-at-valmontone":
        ["cand-4637", "cand-3035", "cand-3431"],
    "st-chp2-seciv-l45-52-barberini-new-palace-plan":
        ["cand-0198", "cand-0240", "cand-4620"],
    "st-chp2-seciv-l45-52-bernini-restored-s-bibiana": ["cand-0296", "cand-4441"],
    "st-chp2-seciv-l45-52-maderno-or-collaborator-design-fragment":
        ["cand-4649", "cand-0240", "cand-1479"],
    "st-chp2-seciv-l45-52-taddeo-approached-maderno":
        ["cand-0239", "cand-1479", "cand-4490", "cand-0209"],
    "st-chp2-seciv-l45-52-taddeo-surrounding-land-purchases": ["cand-0239", "cand-0240"],
    "st-chp2-seciv-l54-63-barberini-palace-departure-from-tradition": ["cand-0240", "cand-1479"],
    "st-chp2-seciv-l54-63-barberini-palace-largest-private-palace": ["cand-0240", "cand-4490"],
    "st-chp2-seciv-l54-63-barberini-supremacy-symbolized": ["cand-0240", "cand-0198"],
    "st-chp2-seciv-l54-63-facade-precedents-around-rome": ["cand-0240", "cand-4490"],
    "st-chp2-seciv-l54-63-new-era-periodization": [],
}

ORDER_FOR = {sid: order for order, sid in {
    2026: "st-chp2-seciv-l45-52-taddeo-age-and-election-context",
    2033: "st-chp2-seciv-l45-52-taddeo-dynastic-role",
    2034: "st-chp2-seciv-l45-52-taddeo-lieutenant-general",
    2035: "st-chp2-seciv-l45-52-taddeo-marriage",
    2037: "st-chp2-seciv-l45-52-taddeo-palestrina-purchase",
    2038: "st-chp2-seciv-l45-52-taddeo-prefect-title",
    2039: "st-chp2-seciv-l45-52-taddeo-succeeds-father-command",
    2040: "st-chp2-seciv-l45-52-della-rovere-prior-prefecture",
    2041: "st-chp2-seciv-l45-52-taddeo-income-ranking",
    2042: "st-chp2-seciv-l45-52-precedence-claims-resisted",
    2046: "st-chp2-seciv-l45-52-urban-viii-intended-assertion-of-rights",
    2047: "st-chp2-seciv-l45-52-francesco-transfer-sforza-palace-in-1626",
    2048: "st-chp2-seciv-l45-52-sforza-family-sale-at-valmontone",
    2049: "st-chp2-seciv-l45-52-barberini-new-palace-plan",
    2050: "st-chp2-seciv-l45-52-bernini-restored-s-bibiana",
    2051: "st-chp2-seciv-l45-52-maderno-or-collaborator-design-fragment",
    2052: "st-chp2-seciv-l45-52-taddeo-approached-maderno",
    2053: "st-chp2-seciv-l45-52-taddeo-surrounding-land-purchases",
    2055: "st-chp2-seciv-l54-63-barberini-palace-departure-from-tradition",
    2056: "st-chp2-seciv-l54-63-barberini-palace-largest-private-palace",
    2057: "st-chp2-seciv-l54-63-barberini-supremacy-symbolized",
    2058: "st-chp2-seciv-l54-63-facade-precedents-around-rome",
    2059: "st-chp2-seciv-l54-63-new-era-periodization",
}.items()}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_hash(value: object) -> str:
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":")).encode("utf-8"))


def read_jsonl(path: Path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    return ([json.loads(line) for line in text.splitlines() if line.strip()], raw,
            "\r\n" if "\r\n" in text else "\n", raw.startswith(b"\xef\xbb\xbf"))


def read_csv(path: Path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader), list(reader.fieldnames or []), raw, (
        "\r\n" if "\r\n" in text else "\n"), raw.startswith(b"\xef\xbb\xbf")


def read_text(path: Path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    return text, ("\r\n" if "\r\n" in text else "\n"), raw.startswith(b"\xef\xbb\xbf"), raw


def csv_bytes(rows, fields, eol, bom):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator=eol, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + out.getvalue().encode("utf-8")


def text_bytes(text, eol, bom):
    normalized = text.replace("\r\n", "\n")
    return (b"\xef\xbb\xbf" if bom else b"") + normalized.replace("\n", eol).encode("utf-8")


def jsonl_bytes(raw, updated):
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    found = set()
    for i, line in enumerate(lines):
        if line.strip():
            row = json.loads(line)
            if row.get("statement_id") in updated:
                lines[i] = json.dumps(updated[row["statement_id"]], ensure_ascii=False)
                found.add(row["statement_id"])
    require(found == set(updated), f"JSONL replacement mismatch: {found ^ set(updated)}")
    return (b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b"") + (
        (eol.join(lines) + eol).encode("utf-8")
    )


def atomic_write(path: Path, data: bytes) -> None:
    fd, temp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    require(head == BASE_HEAD, f"Unexpected baseline HEAD: {head}")
    require(sha(PDF_PATH.read_bytes()) == PDF_SHA256, "CHP-2.pdf hash changed")
    require(sha(SOURCE_PATH.read_bytes()) == SOURCE_SHA256, "Chapter 2 section hash changed")
    history_raw = HISTORY_PATH.read_bytes()
    require(sha(history_raw) == HISTORY_SHA256, "Immutable H9622 ledger hash changed")

    statements, statements_raw, _, _ = read_jsonl(STATEMENTS_PATH)
    roster, roster_fields, _, roster_eol, roster_bom = read_csv(ROSTER_PATH)
    mentions, _, _, _, _ = read_csv(MENTIONS_PATH)
    segments, _, _, _ = read_jsonl(SEGMENTS_PATH)
    candidates, candidate_fields, _, candidate_eol, candidate_bom = read_csv(CANDIDATES_PATH)
    alignments, alignment_fields, _, alignment_eol, alignment_bom = read_csv(ALIGNMENT_PATH)
    relations, _, relations_raw, _, _ = read_csv(RELATIONS_PATH)

    require(len(statements) == len(roster) == 15518, "Current statement/roster count changed")
    require(len(mentions) == 27357, "Current mention count changed")
    require(len(history_raw.decode("utf-8-sig").splitlines()) - 1 == 9622, "History row count changed")
    statement_by_id = {r["statement_id"]: r for r in statements}
    roster_by_id = {r["statement_id"]: r for r in roster}
    segment_by_id = {r["segment_id"]: r for r in segments}
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    alignment_by_candidate = {r["candidate_id"]: r for r in alignments}
    mentions_by_segment = defaultdict(list)
    mention_by_id = {}
    for mention in mentions:
        mentions_by_segment[mention["segment_id"]].append(mention)
        mention_by_id[mention["mention_id"]] = mention

    selected = sorted(
        (r for r in roster if WINDOW_START <= int(r["current_order"]) <= WINDOW_END),
        key=lambda r: int(r["current_order"]),
    )
    require(len(selected) == 100 and [int(r["current_order"]) for r in selected]
            == list(range(WINDOW_START, WINDOW_END + 1)), "B576 range is not continuous 100 IDs")
    before = Counter(r["current_review_status"] for r in selected)
    require(before == Counter({"reviewed_current_pass": 77, "reviewed_current_pending": 23}),
            f"Unexpected B576 current status: {dict(before)}")
    pending_ids = {r["statement_id"] for r in selected
                   if r["current_review_status"] == "reviewed_current_pending"}
    require(pending_ids == set(PROMOTED) | set(RETAINED), "Pending IDs changed")
    require(set(MENTION_MAPS) == pending_ids and set(ORDER_FOR) == pending_ids,
            "B576 per-ID mappings are incomplete")

    adjacent = [r for r in roster if 1760 <= int(r["current_order"]) <= 1959]
    require(len(adjacent) == 200 and all(r["current_review_status"] == "reviewed_current_pass"
                                         for r in adjacent), "Adjacent PASS windows changed")

    def verify_fingerprints(rows, label):
        for row in rows:
            sid = row["statement_id"]
            statement = statement_by_id[sid]
            segment = segment_by_id[statement["segment_id"]]
            seg_mentions = sorted(mentions_by_segment[statement["segment_id"]],
                                  key=lambda m: m["mention_id"])
            require(canonical_hash(statement) == row["current_statement_sha256"],
                    f"{label}: current statement hash mismatch: {sid}")
            require(segment["sha256"] == row["segment_sha256"]
                    and segment["asset_sha256"] == row["source_asset_sha256"],
                    f"{label}: segment/source fingerprint mismatch: {sid}")
            require(str(len(seg_mentions)) == row["current_segment_mention_count"]
                    and canonical_hash(seg_mentions) == row["current_segment_mentions_sha256"],
                    f"{label}: mention fingerprint mismatch: {sid}")

    verify_fingerprints(selected, "B576")
    verify_fingerprints(adjacent, "adjacent reuse")
    require(all(r["source_file"] == "02-sources/02-Markdown/02_CHP-2_sec_iv.md" for r in selected),
            "B576 source path changed")
    pre_history = Counter(r["history_9622_current_statement_match"] for r in selected
                          if int(r.get("history_9622_event_count") or 0) > 0)
    require(sum(int(r.get("history_9622_event_count") or 0) for r in selected) == 95
            and sum(r["history_9622_source_match"] == "true" for r in selected) == 95
            and pre_history == Counter({"exact": 42, "changed": 53}),
            f"Unexpected B576 H9622 reconciliation: {dict(pre_history)}")

    source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
    for sid, candidate_ids in MENTION_MAPS.items():
        statement = statement_by_id[sid]
        segment = segment_by_id[statement["segment_id"]]
        segment_text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
        seg_mentions = mentions_by_segment[statement["segment_id"]]
        available = {m["candidate_id"] for m in seg_mentions}
        for cid in candidate_ids:
            require(cid in available, f"{sid}: no source span for {cid}")
        for mention in seg_mentions:
            require(segment_text[int(mention["start_char"]):int(mention["end_char"])]
                    == mention["surface_form"], f"Bad mention span {mention['mention_id']}")

    # S1/S3 targeted correction: index subentry locates the person, it is not a work identity.
    c1479 = candidate_by_id["cand-1479"]
    require(c1479["index_entry_id"] == "M.csv#16" and c1479["canonical_name"] == "Maderno, Carlo"
            and c1479["suggested_type"] == "work"
            and c1479["sub_entry"] == "plans for Barberini palace", "cand-1479 record changed")
    index_rows = list(csv.DictReader(INDEX_PATH.open(encoding="utf-8-sig", newline="")))
    main_rows = [r for r in index_rows if r["Main Entry"] == "Maderno, Carlo" and not r["Sub-entry"]]
    sub_rows = [r for r in index_rows if r["Main Entry"] == "Maderno, Carlo"
                and r["Sub-entry"] == "plans for Barberini palace"]
    require(len(main_rows) == len(sub_rows) == 1 and sub_rows[0]["Page Numbers"] == "47, 48",
            "M.csv#14/#16 anchor changed")
    for cid in ("cand-1477", "cand-4873"):
        row = alignment_by_candidate[cid]
        require(row["decision"] == "new" and row["ku_id"] == SAME_KU,
                f"Existing Maderno identity group changed: {cid}")
    old_aln = alignment_by_candidate["cand-1479"]
    require(old_aln["alignment_id"] == "aln-1814" and old_aln["decision"] == "undecided"
            and not old_aln["ku_id"], "cand-1479 alignment changed")
    for mid, expected in {
        "m-chp2-seciv-l45-52-0062": ("cand-1479", "Carlo Maderno"),
        "m-chp2-seciv-l45-52-0067": ("cand-1479", "Maderno"),
        "m-chp2-seciv-l54-63-0016": ("cand-1479", "Maderno"),
        "m-chp2-seciv-l54-63-0018": ("cand-1479", "his predecessor"),
    }.items():
        m = mention_by_id.get(mid)
        require(m is not None and (m["candidate_id"], m["surface_form"]) == expected,
                f"cand-1479 mention changed: {mid}")

    selected_ids = {r["statement_id"] for r in selected}
    linked_relations = [r for r in relations if any(sid in r.get("source_span", "") for sid in selected_ids)]
    require({r["relation_id"] for r in linked_relations} == {"rel-2491", "rel-2492", "rel-2524"}
            and all(r["status"] == "formal" for r in linked_relations),
            "B576 formal-relation footprint changed")
    rel_2524 = next(r for r in linked_relations if r["relation_id"] == "rel-2524")
    require(rel_2524["predicate"] == "held_office"
            and "st-chp2-seciv-l45-52-taddeo-prefect-title" in rel_2524["source_span"],
            "rel-2524 evidence mismatch")

    # Prepare 22 statement edits; p.48 design attribution remains pending and its existing local map is preserved.
    updated_ids = set(MENTION_MAPS) - {
        "st-chp2-seciv-l54-63-barberini-palace-departure-from-tradition"
    }
    require(len(updated_ids) == 22, "Expected 22 changed statement rows")
    for sid in updated_ids:
        q = dict(statement_by_id[sid].get("qualifiers") or {})
        q["mentioned_candidate_ids"] = list(MENTION_MAPS[sid])
        statement_by_id[sid]["qualifiers"] = q

    def statement(sid):
        return statement_by_id[sid]

    st = statement("st-chp2-seciv-l45-52-taddeo-dynastic-role")
    st["object_candidate_id"] = None
    q = dict(st["qualifiers"])
    q["expected_dynasty_candidate_id"] = "cand-0198"
    q["comparison_scope_candidate_id"] = "cand-3462"
    q["relation_candidate"] = False
    q["relation_candidate_note"] = "Haskell characterizes an expected role, not an accomplished kinship relation."
    st["qualifiers"] = q

    st = statement("st-chp2-seciv-l45-52-taddeo-income-ranking")
    st["object_candidate_id"] = None
    st["qualifiers"]["comparison_scope_candidate_id"] = "cand-3461"

    st = statement("st-chp2-seciv-l45-52-precedence-claims-resisted")
    st["subject_candidate_id"] = st["object_candidate_id"] = None
    q = dict(st["qualifiers"])
    q.pop("asserting_agent_candidate_id", None)
    q["unresolved_actor_roles"] = ["party pressing the claims", "party resisting the claims"]
    q["qualification"] = (
        "Haskell does not identify who pressed or resisted the claims. The adjacent Urban VIII intention is not "
        "treated as naming these actors; foreign embassies are only attributed resentment of perceived humiliation."
    )
    st["qualifiers"] = q

    st = statement("st-chp2-seciv-l45-52-francesco-transfer-sforza-palace-in-1626")
    q = dict(st["qualifiers"])
    q["asset_candidate_id"] = q.pop("place_candidate_id")
    q["qualification"] = (
        "The Sforza palace is the transferred asset. This restates the transfer at L37 and supplies 1626; the "
        "1625 purchase at L36 is separate. No formal edge is created here."
    )
    st["qualifiers"] = q

    st = statement("st-chp2-seciv-l45-52-sforza-family-sale-at-valmontone")
    st["object_candidate_id"] = "cand-3035"
    q = dict(st["qualifiers"])
    q["purchaser_candidate_id"] = "cand-3035"
    q["location_candidate_id"] = "cand-3431"
    q["asset_description"] = "Sforza family property at Valmontone; no distinct asset identity is supplied"
    q["qualification"] = (
        "Seller, purchaser Francesco, and place Valmontone are distinct roles. The property is not identified as "
        "the Quirinal palace or another registered asset; keep the missing asset endpoint pending."
    )
    st["qualifiers"] = q

    st = statement("st-chp2-seciv-l45-52-maderno-or-collaborator-design-fragment")
    st["qualifiers"]["qualification"] = (
        "The source preserves Maderno or, more likely, an unidentified collaborator/adviser as alternatives. "
        "Keep the designer relation pending and preserve the p.48 continuation."
    )

    st = statement("st-chp2-seciv-l45-52-taddeo-approached-maderno")
    st["qualifiers"]["qualification"] = (
        "cand-1479 is now typed person and aln-1814 maps it to the existing Carlo Maderno KU. The claim reports "
        "Taddeo approaching him; Rome's leading-architect description and prior service to the Pope remain Haskell's "
        "context. No S6 formal relation is created."
    )

    st = statement("st-chp2-seciv-l45-52-taddeo-surrounding-land-purchases")
    st["object_candidate_id"] = None
    q = dict(st["qualifiers"])
    q["project_context_candidate_id"] = "cand-0240"
    q["asset_description"] = "surrounding land; individual parcels are not identified"
    q["qualification"] = (
        "The palace is project context, not the acquired object. Haskell reports continued land purchases but does "
        "not identify the parcels; keep the acquisition relation pending."
    )
    st["qualifiers"] = q

    st = statement("st-chp2-seciv-l45-52-taddeo-prefect-title")
    # The evidence and endpoints used by formal rel-2524 remain unchanged.
    require(st["subject_candidate_id"] == "cand-0239"
            and st["object_candidate_id"] == "cand-4645"
            and st["predicate"] == "civic_title_assigned_reported",
            "rel-2524 source statement changed")

    st = statement("st-chp2-seciv-l54-63-barberini-palace-largest-private-palace")
    st["object_candidate_id"] = None
    st["qualifiers"]["comparison_scope_candidate_id"] = "cand-4490"

    st = statement("st-chp2-seciv-l54-63-barberini-supremacy-symbolized")
    q = dict(st["qualifiers"])
    q["relation_candidate"] = False
    q["relation_candidate_note"] = "Haskell's political symbolism is retained as a source claim, not a formal edge."
    st["qualifiers"] = q

    st = statement("st-chp2-seciv-l54-63-facade-precedents-around-rome")
    st["object_candidate_id"] = None
    q = dict(st["qualifiers"])
    q["geographic_scope_candidate_id"] = "cand-4490"
    q["relation_candidate"] = False
    q["relation_candidate_note"] = "Villa precedents around Rome are comparison scope, not a palace-to-city relation."
    st["qualifiers"] = q

    st_2055 = statement("st-chp2-seciv-l54-63-barberini-palace-departure-from-tradition")
    require(st_2055["qualifiers"].get("mentioned_candidate_ids") == ["cand-0240", "cand-1479"],
            "p.48 continuation mapping changed")

    candidate_after = [dict(r) for r in candidates]
    cand_after = {r["candidate_id"]: r for r in candidate_after}["cand-1479"]
    cand_after["suggested_type"] = "person"
    cand_after["detail"] = (
        "B576 targeted S1 correction: M.csv#16 subentry 'plans for Barberini palace' is a locator for the person "
        "Maderno, Carlo, not a work identity. Haskell calls Carlo Maderno the leading architect in Rome on p.47 "
        "and states on p.48 that Maderno died in 1629 and Bernini replaced him. The palace remains cand-0240."
    )
    cand_after["candidate_source_ref"] = (
        "chp-2:02_CHP-2_sec_iv:l45-52#L52;chp-2:02_CHP-2_sec_iv:l54-63#L56"
    )

    alignment_after = [dict(r) for r in alignments]
    aln_after = {r["candidate_id"]: r for r in alignment_after}["cand-1479"]
    aln_after["ku_id"] = SAME_KU
    aln_after["decision"] = "same"
    aln_after["process_ref"] = KNOWLEDGE_REF
    aln_after["resolution_note"] = (
        "source_ref=entity-candidates.csv#cand-1479;index_entry=M.csv#16;index_main=M.csv#14;"
        "index_subentry=plans for Barberini palace;index_pages=47, 48;type=person;"
        "body_mentions=m-chp2-seciv-l45-52-0062,m-chp2-seciv-l45-52-0067,"
        "m-chp2-seciv-l54-63-0016,m-chp2-seciv-l54-63-0018;"
        "group=new-person:carlo-maderno-530c4fdfa7. The subentry locates Maderno's palace-plan context; "
        "p.47 names Carlo Maderno as Rome's leading architect and p.48 identifies the person through his 1629 death "
        "and replacement by Bernini. M.csv#14 has the same full headword; candidates cand-1477 and cand-4873 are "
        "already mapped to units/persons/carlo-maderno. Same reuses that person KU. The palace and its plan remain "
        "distinct. No external identity marker was used."
    )

    # Update the existing person card with the new book-internal identity evidence.
    unit_text, unit_eol, unit_bom, _ = read_text(UNIT_PATH)
    tick = chr(96)
    old_cn = "本卡对应索引词头“Carlo Maderno”及候选cand-1477、cand-4873。"
    new_cn = "本卡对应索引词头“Carlo Maderno”及候选cand-1477、cand-1479、cand-4873。"
    old_en = "This card represents the index entry “Carlo Maderno” and candidates cand-1477 and cand-4873."
    new_en = "This card represents the index entry “Carlo Maderno” and candidates cand-1477, cand-1479, and cand-4873."
    old_ident = f"- S3人物组：{tick}cand-1477{tick}, {tick}cand-4873{tick}；"
    new_ident = f"- S3人物组：{tick}cand-1477{tick}, {tick}cand-1479{tick}, {tick}cand-4873{tick}；"
    old_group_note = "本批未采用外部权威标识。cand-1477与cand-4873按同一全名合并为一个跨章人物KU；未采用外部身份标识。"
    old_process_link = "与[本批过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-crosschapter-person-endpoints-mead-maderno-zanetti-20261017)"
    new_process_link = (
        "、[初始跨章对齐记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
        "#s4-crosschapter-person-endpoints-mead-maderno-zanetti-20261017)与[定向修正记录](../../../03-processing/"
        "patrons-and-painters-full-book-s2/process/knowledge.md#s3-targeted-cand-1479-maderno-20261103)"
    )
    new_group_note = "三个候选均归入同一跨章人物KU；未采用外部身份标识。"
    require(unit_text.count(old_cn) == unit_text.count(old_en) == unit_text.count(old_ident) == 1,
            "Carlo Maderno card identity text changed")
    require(unit_text.count(old_group_note) == unit_text.count(old_process_link) == 1,
            "Carlo Maderno card group note changed")
    unit_text = (unit_text.replace(old_cn, new_cn).replace(old_en, new_en)
                 .replace(old_ident, new_ident).replace(old_group_note, new_group_note)
                 .replace(old_process_link, new_process_link))
    cn_old = (
        "第2章将Maderno置于圣彼得大教堂增建中殿方案的讨论中；第3章称Peretti-Montalto将他带入教堂工程，"
        "并称Borromini曾在Maderno与Bernini手下承担较小任务。Postscript提及Hibbard关于Maderno家族宫殿起源的专著。"
    )
    cn_new = (
        "第2章将Maderno置于圣彼得大教堂增建中殿方案的讨论中，并在p.47称他为罗马主要建筑师、记Taddeo曾接洽他；"
        "p.48记其于1629年去世并由Bernini接替。第3章称Peretti-Montalto将他带入教堂工程，并称Borromini曾在Maderno"
        "与Bernini手下承担较小任务。Postscript提及Hibbard关于Maderno家族宫殿起源的专著。"
    )
    en_old = (
        "Chapter 2 names Maderno in its discussion of the proposed nave addition to St Peter’s. Chapter 3 says "
        "Peretti-Montalto brought him into a church project and that Borromini had earlier worked on comparatively "
        "minor tasks under Maderno and Bernini. The Postscript refers to Hibbard’s monograph on Maderno and the "
        "origins of the family palace."
    )
    en_new = (
        "Chapter 2 names Maderno in its discussion of the proposed nave addition to St Peter’s and, on p. 47, "
        "calls him Rome’s leading architect and says Taddeo approached him; p. 48 states that Maderno died in 1629 "
        "and Bernini replaced him. Chapter 3 says Peretti-Montalto brought him into a church project and that "
        "Borromini had earlier worked on comparatively minor tasks under Maderno and Bernini. The Postscript refers "
        "to Hibbard’s monograph on Maderno and the origins of the family palace."
    )
    require(unit_text.count(cn_old) == unit_text.count(en_old) == 1, "Carlo Maderno description changed")
    unit_text = unit_text.replace(cn_old, cn_new).replace(en_old, en_new)
    source_block = """- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)'
  location: 第2章，印刷页47–48，Markdown L52、L56
  sentence_summary: Haskell称Carlo Maderno为罗马主要建筑师，并记Taddeo曾接洽他；第48页记Maderno于1629年去世后由Bernini接替。
  original_quotes:
  - source_span: Markdown line 52
    text: Carlo Maderno, the leading architect in Rome
  - source_span: Markdown line 56
    text: Maderno died in 1629, and was at once replaced by Bernini
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/02_CHP-2_sec_iv.md
    source_span: Markdown line 52, printed p. 47; line 56, printed p. 48
"""
    require(unit_text.count("created: '2026-10-17'") == 1, "Card date marker changed")
    unit_text = unit_text.replace("created: '2026-10-17'", source_block + "created: '2026-10-17'", 1)
    unit_text = unit_text.replace("updated: '2026-10-17'", "updated: '2026-11-03'")

    roster_after = [dict(r) for r in roster]
    roster_after_by_id = {r["statement_id"]: r for r in roster_after}
    old_refs = {r["statement_id"]: r.get("review_evidence_ref", "") for r in selected}
    for row in selected:
        sid = row["statement_id"]
        new = roster_after_by_id[sid]
        new["review_batch_id"] = BATCH_ID
        new["review_evidence_ref"] = EVIDENCE_REF
        if sid in PROMOTED:
            new["current_review_status"] = "reviewed_current_pass"
            new["review_outcome"] = "current_semantic_pass_after_source_mapping_or_role_repair"
            detail = PROMOTED[sid]
        elif sid in RETAINED:
            new["current_review_status"] = "reviewed_current_pending"
            new["review_outcome"] = "current_pending_retained_for_unresolved_endpoint_or_attribution"
            detail = RETAINED[sid]
        else:
            require(row["current_review_status"] == "reviewed_current_pass", f"Unclassified row {sid}")
            new["current_review_status"] = "reviewed_current_pass"
            new["review_outcome"] = "reused_current_pass_after_B576_fingerprint_check"
            detail = "Existing current PASS reused after exact statement/source/segment/mention fingerprints."
        new["follow_up_note"] = (
            f"B576: {detail} Prior current evidence: {old_refs[sid]}.\n"
            + new.get("follow_up_note", "").strip()
        ).strip()

    for sid in updated_ids:
        row = roster_after_by_id[sid]
        current_hash = canonical_hash(statement_by_id[sid])
        row["current_statement_sha256"] = current_hash
        if int(row.get("history_9622_event_count") or 0) > 0:
            row["history_9622_current_statement_match"] = (
                "exact" if row["history_9622_latest_statement_sha256"] == current_hash else "changed"
            )
            row["prior_review_match"] = (
                "exact_object_and_source_segment"
                if row["history_9622_current_statement_match"] == "exact"
                and row["history_9622_source_match"] == "true"
                else "historical_object_or_source_differs"
            )

    # Type/identity correction affects order 2061, but its S2 status stays pending for the next window.
    next_id = "st-chp2-seciv-l54-63-bernini-succeeds-maderno-with-borromini"
    next_row = roster_after_by_id[next_id]
    require(int(next_row["current_order"]) == 2061
            and next_row["current_review_status"] == "reviewed_current_pending",
            "Expected order 2061 to remain pending")
    next_row["follow_up_note"] = (
        "B576 upstream effect: cand-1479 type is person and aln-1814 now maps same to "
        "units/persons/carlo-maderno. This statement remains pending until its own current S2 review in 2060–2159; "
        "the identity decision does not transfer a PASS status. "
        + next_row.get("follow_up_note", "").strip()
    ).strip()

    after = Counter(r["current_review_status"] for r in roster_after)
    window_after = Counter(roster_after_by_id[r["statement_id"]]["current_review_status"] for r in selected)
    require(window_after == Counter({"reviewed_current_pass": 95, "reviewed_current_pending": 5}),
            f"Unexpected B576 result: {dict(window_after)}")
    require(after["reviewed_current_pass"] == 8812 and after["reviewed_current_pending"] == 6706,
            f"Unexpected global status: {dict(after)}")
    history_after = Counter(r["history_9622_current_statement_match"] for r in roster_after
                            if int(r.get("history_9622_event_count") or 0) > 0)
    require(sum(history_after.values()) == 9537, "Current H9622 ID denominator changed")
    require(sha(RELATIONS_PATH.read_bytes()) == sha(relations_raw), "relations.csv changed in dry-run")
    next_window = [r for r in roster_after if 2060 <= int(r["current_order"]) <= 2159]
    require(len(next_window) == 100, "Next 100-ID window is unavailable")
    next_counts = Counter(r["current_review_status"] for r in next_window)

    # Build batch process records and current summary.
    process_record = f"""

<a id="{STAGE_ID}"></a>
### 2026-11-03 S2 当前版逐ID语义复核阶段 B576（当前顺序1960–2059）

**窗口与复用。** 连续100条：77条已有PASS经当前statement、来源资产、S0 segment与mention-set指纹核平后复用；23条pending回到第2章印刷p.47–48原文、既有扫描核读和B005 finding，其中18条转PASS、5条保留pending。相邻窗口1760–1859与1860–1959共200条已有PASS也经指纹核平后复用，不重复阅读或另造批次。

**原文与版本。** 权威CHP-2.pdf SHA-256={PDF_SHA256}；当前sec_iv Markdown SHA-256={SOURCE_SHA256}。对应segment为chp-2:02_CHP-2_sec_iv:l45-52及l54-63。窗口100/100 statement、来源资产、segment与mention集合指纹通过；mention表已有候选跨度逐条回切segment并匹配surface form，没有新增mention行。

**逐条通过与映射。** 下表给出18条pending转PASS的当前ID和claim-specific mention候选；roster逐行保留原证据入口和判断变化：

| 序位 | statement ID | 本次裁决与映射 |
|---:|---|---|
| 2026 | st-chp2-seciv-l45-52-taddeo-age-and-election-context | PASS；cand-0239、cand-0209。 |
| 2033 | st-chp2-seciv-l45-52-taddeo-dynastic-role | PASS；cand-0239、cand-0198、cand-3462；王朝是预期角色，Europe为比较范围，不是实际亲缘边。 |
| 2034 | st-chp2-seciv-l45-52-taddeo-lieutenant-general | PASS；cand-0239、cand-4644；保留约略时间。 |
| 2035 | st-chp2-seciv-l45-52-taddeo-marriage | PASS；cand-0239、cand-4639、cand-4638；女方未具名。 |
| 2037 | st-chp2-seciv-l45-52-taddeo-palestrina-purchase | PASS；cand-0239、cand-4215；保留“两年后”限定。 |
| 2038 | st-chp2-seciv-l45-52-taddeo-prefect-title | PASS；cand-0239、cand-4645、cand-4490；1631职位statement的formal证据不变。 |
| 2039 | st-chp2-seciv-l45-52-taddeo-succeeds-father-command | PASS；cand-0239、cand-4640、cand-4644；父亲和日期不推定。 |
| 2040 | st-chp2-seciv-l45-52-della-rovere-prior-prefecture | PASS；cand-4646、cand-4645、cand-4648；保留家族范围。 |
| 2041 | st-chp2-seciv-l45-52-taddeo-income-ranking | PASS；cand-0239、cand-3461；Italy为比较范围。 |
| 2046 | st-chp2-seciv-l45-52-urban-viii-intended-assertion-of-rights | PASS；cand-0209、cand-0239；只记录Urban VIII意图。 |
| 2047 | st-chp2-seciv-l45-52-francesco-transfer-sforza-palace-in-1626 | PASS；cand-3035、cand-0239、cand-4620；Sforza palace明确为转让资产，不建formal edge。 |
| 2049 | st-chp2-seciv-l45-52-barberini-new-palace-plan | PASS；cand-0198、cand-0240、cand-4620；新建计划与既有宫殿分开。 |
| 2050 | st-chp2-seciv-l45-52-bernini-restored-s-bibiana | PASS；cand-0296、cand-4441；沿用p.47扫描校读only restored。 |
| 2052 | st-chp2-seciv-l45-52-taddeo-approached-maderno | PASS；cand-0239、cand-1479、cand-4490、cand-0209；S1/S3定向修正后person端点清楚。 |
| 2056 | st-chp2-seciv-l54-63-barberini-palace-largest-private-palace | PASS；cand-0240、cand-4490；Rome为比较范围。 |
| 2057 | st-chp2-seciv-l54-63-barberini-supremacy-symbolized | PASS；cand-0240、cand-0198；Haskell政治解释保留为非formal claim。 |
| 2058 | st-chp2-seciv-l54-63-facade-precedents-around-rome | PASS；cand-0240、cand-4490；保留façade/villa比较和almost only限定。 |
| 2059 | st-chp2-seciv-l54-63-new-era-periodization | PASS；mention数组为空；不造event端点。 |

**S1/S3定向修正。** 独立逐页复核指出cand-1479将Carlo Maderno错标为work。本批核回M.csv#16：主项“Maderno, Carlo”，子项“plans for Barberini palace”是索引定位，页码47–48；p.47原文称Carlo Maderno为“the leading architect in Rome”，p.48称其1629年去世后由Bernini接替。故entity-candidates.csv只将suggested_type从work改为person，并写入原页source ref。M.csv#14主项同为“Maderno, Carlo”，cand-1477和cand-4873已归入new-person:carlo-maderno-530c4fdfa7并登记至units/persons/carlo-maderno；因此aln-1814从undecided改为same，复用该KU，不合并palace或方案，也未使用外部标识。人物卡补入p.47–48身份依据和cand-1479入口。2061号Bernini接替Maderno statement仍pending，留待下一窗口独立复核。

**保留pending的五项。** 2042提出/抵抗precedence claims的主体不明；移除无据Urban VIII asserting-agent及错误关系端点。2048已拆清Sforza family卖方、Francesco买方、Valmontone地点，但property未被识别为独立资产端点。2051保留Maderno与更可能的未具名collaborator/adviser两种归属。2053未识别所购surrounding-land地块，已移除错误的palace购买对象。2055是同一跨页设计归属不确定；类型修正不替原文选定设计者。以上关系端点缺口继续pending，不补造S6 formal edge。

**相关关系和历史裁决。** aln-1814由undecided转same；其余alignment及S6裁决未改。relations.csv中3条本窗口formal关系rel-2491、rel-2492、rel-2524保持端点、predicate、scope、evidence与状态不变；rel-2524仍由2038号Prefect of Rome statement支持，relations.csv逐字节未变。H9622账本保持9,622行、SHA-256={HISTORY_SHA256}；本窗口95个历史事件的source version均95/95匹配，批前hash为42 exact/53 changed。原始review hash、历史裁决与事件账本不回写，只刷新roster当前hash匹配。

| 阶段量 | 数量 | 结果 |
|---|---:|---|
| 连续当前statement | 100（1960–2059） | 100/100指纹核平 |
| 既有当前PASS复用 | 77 | 不重读 |
| pending转当前PASS | 18 | 补映/定向修正后通过 |
| 保留pending | 5 | 缺失行为主体、作品或地块端点 |
| statement字段修订 | {len(updated_ids)} | 未新增statement或mention |
| 相邻窗口PASS复用 | 200（1760–1959） | 已有证据与指纹一致 |

**批后状态。** 全书{len(statements):,}条statement、{len(mentions):,}条mention；PASS {after['reviewed_current_pass']:,}、pending {after['reviewed_current_pending']:,}。下一连续窗口为2060–2159；该窗口PASS {next_counts['reviewed_current_pass']}、pending {next_counts['reviewed_current_pending']}，其中2061仍pending。本阶段不等同全书S2独立语义接收。

**针对性验证。** [B576预检与写入脚本](adjudicate_s2_current_review_b576_order_1960_2059_20261103.py)的基线及来源指纹核验通过。`audit_tables.py --strict-stage --summary`返回15,518条statement、27,357条mention、`errors=[]`、`s2_missing=[]`、`alignments_unlinked=0`；`audit_relation_consistency.py --dry-run`五类关系阻断均为0，另报告1,320个零关系KU与2个超连接KU诊断项。Carlo Maderno卡片按单卡预检并渲染1张，写后字节核验通过，再次预览无差异；未投影关系行。`git diff --check`通过。结构审计中的S4 2,522项登记待办及全书S2仍待独立语义接收，均保持原状态。
""".strip()

    knowledge_text, knowledge_eol, knowledge_bom, _ = read_text(KNOWLEDGE_PATH)
    require(KNOWLEDGE_ANCHOR not in knowledge_text, "S3 correction note already exists")
    knowledge_record = f"""

<a id="{KNOWLEDGE_ANCHOR}"></a>
### S1/S3定向修正：cand-1479 Carlo Maderno（2026-11-03）

M.csv#16主项为“Maderno, Carlo”，子项“plans for Barberini palace”及页码47–48是索引定位，不是work身份。第2章p.47称Carlo Maderno为罗马主要建筑师，并记Taddeo接洽他；p.48记Maderno于1629年去世后由Bernini接替。独立原页复核也指出原suggested_type=work错误。此次将cand-1479类型更正为person；Barberini palace仍为独立候选cand-0240。

cand-1479与cand-1477、cand-4873的索引规范名相同。cand-1477、cand-4873已组成new-person:carlo-maderno-530c4fdfa7并登记至units/persons/carlo-maderno。故aln-1814裁为same并复用该KU；此为书内全名、页码和人物角色的比较，不声称外部身份验证。人物卡已补入p.47–48来源证据和cand-1479入口。设计归属与关系候选不因身份same而自动formal；2051、2055及2061仍按各自pending状态处理。
""".strip()
    knowledge_text = knowledge_text.rstrip() + "\n\n" + knowledge_record + "\n"

    stages_text, stages_eol, stages_bom, _ = read_text(STAGES_PATH)
    result_text, result_eol, result_bom, _ = read_text(RESULT_STAGES_PATH)
    require(STAGE_ID not in stages_text and STAGE_ID not in result_text, "B576 already recorded")
    stages_text = stages_text.rstrip() + "\n\n" + process_record + "\n"
    exact_after, changed_after = history_after["exact"], history_after["changed"]
    result_index = (
        f"\n\n### 2026-11-03 S2 current semantic review stage B576 (1960–2059)\n\n"
        f"Reviewed 100 continuous current statements: reused 77 current PASS, promoted 18 pending to PASS, retained 5 pending. "
        f"Updated {len(updated_ids)} statements, adding no statement or mention. Two adjacent pre-existing PASS windows "
        f"(200 statements) were reused after fingerprint checks. Corrected cand-1479 to person and aln-1814 to same with "
        f"the existing Carlo Maderno KU. Full-book totals: {len(statements)} statements, {len(mentions)} mentions, "
        f"{after['reviewed_current_pass']} PASS, {after['reviewed_current_pending']} pending. "
        f"Formal relations and immutable H9622 outcomes were preserved. See [B576 process record](../process/stages.md#{STAGE_ID}) "
        f"and [targeted S3 record](../process/knowledge.md#{KNOWLEDGE_ANCHOR}).\n"
    )
    result_text = result_text.rstrip() + result_index

    current_text, current_eol, current_bom, _ = read_text(CURRENT_RESULT_PATH)
    lines = current_text.splitlines()
    status_idx = next((i for i, line in enumerate(lines)
                       if line.startswith("**后续顺序（逐阶段执行）：**")), None)
    require(status_idx is not None, "Current S2 status line missing")
    pass_pct = 100 * after["reviewed_current_pass"] / len(statements)
    pending_pct = 100 * after["reviewed_current_pending"] / len(statements)
    lines[status_idx] = (
        f"**后续顺序（逐阶段执行）：** **S1 → S2 → S3 → S4 → S5 → S6 → S7。** "
        f"S1索引、图版、书目及候选来源映射复核已完成；B576定向纠正cand-1479类型work→person，aln-1814裁为same并复用"
        f"units/persons/carlo-maderno。S2当前版本为{len(statements):,}条statement、{len(mentions):,}条mention；"
        f"逐ID清单{len(roster_after):,}/{len(roster_after):,}均有当前决定：PASS {after['reviewed_current_pass']:,}"
        f"（{pass_pct:.2f}%）、pending {after['reviewed_current_pending']:,}（{pending_pct:.2f}%），尚未全书独立语义接收。"
        f"H9622历史事件账本9,622行保持不变；当前roster映射9,620条事件至9,537个ID（含83条重复审读，另2个旧ID各有撤销/拆分去向），"
        f"当前ID级statement hash为{exact_after:,} exact、{changed_after:,} changed。B576连续复核当前顺序1960–2059共100条："
        f"77条PASS复用、18条pending转PASS、5条保留pending；此前相邻窗口1760–1959的200条PASS经指纹核平后复用。"
        f"下一连续窗口2060–2159；全书S2仍有{after['reviewed_current_pending']:,}条pending。S3–S6逐类收口，S7待前序阶段收口后开展。"
    )
    current_text = "\n".join(lines) + "\n"

    plan = {
        "batch": BATCH_ID, "window": [WINDOW_START, WINDOW_END],
        "promoted": sorted(PROMOTED), "retained": sorted(RETAINED),
        "changed_statements": sorted(updated_ids),
        "candidate": ["cand-1479", "work", "person"],
        "alignment": ["aln-1814", "undecided", "same", SAME_KU],
        "global_status": dict(after), "history_hashes": dict(history_after),
        "relations": ["rel-2491", "rel-2492", "rel-2524"], "history_ledger_sha256": HISTORY_SHA256,
    }
    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "plan_sha256": canonical_hash(plan),
        "window": [WINDOW_START, WINDOW_END],
        "before_window": dict(before), "after_window": dict(window_after),
        "after_global": dict(after), "h9622_window_before": dict(pre_history),
        "h9622_global_after": dict(history_after), "window_events": 95, "source_matches": 95,
        "adjacent_pass_reused": len(adjacent), "next_window": dict(next_counts),
        "relations_checked": ["rel-2491", "rel-2492", "rel-2524"],
        "candidate_type": "cand-1479 work -> person",
        "alignment": "aln-1814 undecided -> same units/persons/carlo-maderno",
        "changed_statement_count": len(updated_ids), "new_mentions": 0,
        "history_ledger_sha256": HISTORY_SHA256,
    }, ensure_ascii=False, sort_keys=True))
    if not args.apply:
        return

    writes = [
        (STATEMENTS_PATH, jsonl_bytes(statements_raw, {sid: statement_by_id[sid] for sid in updated_ids})),
        (ROSTER_PATH, csv_bytes(roster_after, roster_fields, roster_eol, roster_bom)),
        (CANDIDATES_PATH, csv_bytes(candidate_after, candidate_fields, candidate_eol, candidate_bom)),
        (ALIGNMENT_PATH, csv_bytes(alignment_after, alignment_fields, alignment_eol, alignment_bom)),
        (UNIT_PATH, text_bytes(unit_text, unit_eol, unit_bom)),
        (STAGES_PATH, text_bytes(stages_text, stages_eol, stages_bom)),
        (KNOWLEDGE_PATH, text_bytes(knowledge_text, knowledge_eol, knowledge_bom)),
        (RESULT_STAGES_PATH, text_bytes(result_text, result_eol, result_bom)),
        (CURRENT_RESULT_PATH, text_bytes(current_text, current_eol, current_bom)),
    ]
    for path, data in writes:
        atomic_write(path, data)
    print(f"applied={BATCH_ID}")


if __name__ == "__main__":
    main()
