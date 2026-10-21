from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
import register_s4_s5_s6_archive_citations_20261020 as archive_batch
import scripts.build_field_facts as field_facts

TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATE_TABLE = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
RELATIONS = TABLES / "relations.csv"
ENRICHMENT = TABLES / "enrichment.jsonl"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
AGENTS = ROOT / "AGENTS.md"

DATE = "2026-10-22"
ANCHOR = "s3-s4-s5-s6-diario-romano-cross-chapter-citations-20261022"
GROUP = "archive-group-1bfc6126228c"
KU_ID = "units/archives/gigli-diario-romano-ricciotti-1958"
CARD_PATH = f"04-knowledge/{KU_ID}.md"
SOURCE_ID = "haskell-1980-rev-ed"
SUBJECT = "units/archives/patrons-and-painters"
CANDIDATES = ("cand-6076", "cand-6269", "cand-6360")
STATEMENTS = (
    "st-chp5-note-p131-n4-citation",
    "st-chp5-notes-l129-gigli-citation",
    "st-chp6-p146-note4-gigli",
    "st-chp6-notes-l131-p150-n2",
    "st-chp5-p131-gigli-diary",
)
BIB = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
CH5I = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
CH5III = "02-sources/02-Markdown/05_CHP-5_sec_iii.md"
CH6INTRO = "02-sources/02-Markdown/06_CHP-6_intro.md"
CH6I = "02-sources/02-Markdown/06_CHP-6_sec_i.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BT = chr(96)

SOURCES = [
    {
        "location": "第21章书目，印刷页423，Markdown L523。",
        "summary": "Haskell书目将Diario Romano列在Gigli, Giacinto名下，注明a cura di Giuseppe Ricciotti、Roma、1958；本卡只记录该书目著录。",
        "source_file": BIB,
        "span": "L523; printed p. 423",
        "quotes": ["Gigli, Giacinto: Diario Romano—a cura di Giuseppe Ricciotti, Roma 1958."],
        "link": "[第21章 p.423 书目](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L523)",
    },
    {
        "location": "第5章，印刷页131注4，Markdown L147。",
        "summary": "注4以Gigli passim回指该书；只记录Haskell的书内引注，未查阅被引版本。",
        "source_file": CH5I,
        "span": "L147; printed p. 131 n. 4",
        "quotes": ["4 Gigli passim."],
        "link": "[第5章 p.131 注4](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md#L147)",
    },
    {
        "location": "第5章，印刷页133注1，Markdown L129。",
        "summary": "注1以Gigli passim为引文，并特别列出pp.77、162、290、324–325；不表示这些页已独立核读。",
        "source_file": CH5III,
        "span": "L129; printed p. 133 n. 1",
        "quotes": ["1 Gigli passim, especially pp. 77, 162, 290, 324-5."],
        "link": "[第5章 p.133 注1](../../../02-sources/02-Markdown/05_CHP-5_sec_iii.md#L129)",
    },
    {
        "location": "第6章，印刷页146注4，Markdown L11。",
        "summary": "注4为罗马战争影响定位Gigli pp.203–240；被引书页未独立核读。",
        "source_file": CH6INTRO,
        "span": "L11; printed p. 146 n. 4",
        "quotes": ["4 For the effects of the war in Rome see Gigli, pp. 203-40."],
        "link": "[第6章 p.146 注4](../../../02-sources/02-Markdown/06_CHP-6_intro.md#L11)",
    },
    {
        "location": "第6章，印刷页150注2，Markdown L131。",
        "summary": "注2引Gigli p.233；该页码落在同章注4所引pp.203–240范围内。",
        "source_file": CH6I,
        "span": "L131; printed p. 150 n. 2",
        "quotes": ["2 Gigli, p. 233."],
        "link": "[第6章 p.150 注2](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md#L131)",
    },
]

CITATIONS = [
    {
        "statement": STATEMENTS[0], "file": CH5I, "span": "L147; printed p. 131 n. 4",
        "role": "第5章 p.131 注4的书内引注",
        "scope": "Haskell注4以Gigli passim指向该出版物；只记录书内引注，不表示被引版本或内容已查阅。",
    },
    {
        "statement": STATEMENTS[1], "file": CH5III, "span": "L129; printed p. 133 n. 1",
        "role": "第5章 p.133 注1的书内引注",
        "scope": "Haskell注1列Gigli passim及pp.77、162、290、324–325；只记录书内引注，不表示这些页已查阅。",
    },
    {
        "statement": STATEMENTS[2], "file": CH6INTRO, "span": "L11; printed p. 146 n. 4",
        "role": "第6章 p.146 注4的书内引注",
        "scope": "Haskell注4为战争对罗马的影响引Gigli pp.203–240；formal cites只记录该引注，不验证被引内容。",
    },
    {
        "statement": STATEMENTS[3], "file": CH6I, "span": "L131; printed p. 150 n. 2",
        "role": "第6章 p.150 注2的书内引注",
        "scope": "Haskell注2引Gigli p.233；该定位在p.146 n.4所引pp.203–240内，只记录书内引注。",
    },
]

FIELDS = [
    ("文献类型", "Haskell书目所列图书", "S1；第21章书目，印刷页423，L523"),
    ("原题名", "*Diario Romano*", "S1；第21章书目，印刷页423，L523"),
    ("书目责任者形式", "Gigli, Giacinto（照录书目列名；本批不据此建立作者关系）", "S1；第21章书目，印刷页423，L523"),
    ("编辑责任", "Giuseppe Ricciotti（原书记作a cura di）", "S1；第21章书目，印刷页423，L523"),
    ("出版地", "Roma", "S1；第21章书目，印刷页423，L523"),
    ("出版年", "1958", "S1；第21章书目，印刷页423，L523"),
    ("Haskell书内引注定位", "第5章p.131注4：Gigli passim；被引版本未独立查阅", "S2；第5章印刷页131注4，L147"),
    ("Haskell书内引注定位", "第5章p.133注1：Gigli passim，尤其pp.77、162、290、324–325；被引页未独立查阅", "S2；第5章印刷页133注1，L129"),
    ("Haskell书内引注定位", "第6章p.146注4：Gigli pp.203–240；被引页未独立查阅", "S2；第6章印刷页146注4，L11"),
    ("Haskell书内引注定位", "第6章p.150注2：Gigli p.233，位于同书注4所引范围内；被引页未独立查阅", "S2；第6章印刷页150注2，L131"),
]

SPEC = {
    "candidate": CANDIDATES[0],
    "group": GROUP,
    "ku_id": KU_ID,
    "type": "archive",
    "sub_type": "book",
    "name_zh": "罗马日记，1958年版",
    "name_en": "Diario Romano, 1958 edition",
    "sources": SOURCES,
    "fields": FIELDS,
    "paragraph_zh": (
        "本卡登记Haskell第21章书目所列的Giacinto Gigli《Diario Romano》1958年出版版本，"
        "书目注明由Giuseppe Ricciotti编者。该对象是书目指向的出版物，不等同于日记手稿；"
        "第5、6章四处定位只记录Haskell的书内引注，本批未查阅该出版物或被引页面。"
    ),
    "paragraph_en": (
        "This unit records the 1958 published book Diario Romano listed under Giacinto Gigli in Haskell’s chapter 21 bibliography, "
        "which identifies Giuseppe Ricciotti as editor. The unit is the cited publication, not a diary manuscript. "
        "The four chapter 5 and 6 locators record Haskell’s in-book citations only; neither the volume nor its cited pages was consulted."
    ),
}


def write_text(path: Path, text: str) -> None:
    raw = path.read_bytes() if path.exists() else b""
    newline = "\r\n" if b"\r\n" in raw else "\n"
    encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    with path.open("w", encoding=encoding, newline="") as handle:
        handle.write(text.replace("\n", newline))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    raw = path.read_bytes()
    encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    newline = "\r\n" if b"\r\n" in raw else "\n"
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding=encoding, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator=newline)
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def replace_one(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, lambda _: replacement, text, count=1, flags=re.M)
    assert count == 1, f"could not update {label}"
    return updated


def extract_fields(card: str, manifest_rows: list[dict]) -> list[dict]:
    old_base = field_facts.BASE
    with tempfile.TemporaryDirectory(prefix="pnp-s4-diario-romano-") as temp_name:
        field_facts.BASE = Path(temp_name)
        path = field_facts.BASE / CARD_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(card, encoding="utf-8-sig", newline="\n")
        try:
            rows, _, warnings, count = field_facts.extract_records(
                [row for row in manifest_rows if row["ku_id"] == KU_ID]
            )
        finally:
            field_facts.BASE = old_base
    assert not warnings, warnings
    assert count == 1 and len(rows) == len(FIELDS), (count, len(rows))
    assert all(row["source_ids"] == [SOURCE_ID] for row in rows)
    assert all(row["evidence_status"] == "source_backed" and row["origin"] == "book" for row in rows)
    field_facts.assign_ids(rows, ENRICHMENT)
    return rows


def update_artifact_row(result: str, label: str, replacement: str) -> str:
    return replace_one(result, rf"^\| \[{re.escape(label)}\].*$", replacement, f"result artifact row {label}")


def summarize_s3_s4(candidate_rows: list[dict], alignment_rows: list[dict], manifest_rows: list[dict]):
    by_candidate = {row["candidate_id"]: row for row in candidate_rows}
    decisions: dict[str, dict] = {}
    for row in alignment_rows:
        candidate_id = row.get("candidate_id", "")
        if not candidate_id or row.get("external_source") or candidate_id not in by_candidate:
            continue
        assert candidate_id not in decisions, f"duplicate non-external decision: {candidate_id}"
        decisions[candidate_id] = row
    manifest_ids = {row["ku_id"] for row in manifest_rows}
    buckets: dict[str, list[dict]] = {kind: [] for kind in sync.TYPE_ORDER}
    for candidate_id, candidate in by_candidate.items():
        raw_type = candidate.get("suggested_type", "")
        kind = sync.TYPE_LABELS.get(raw_type, raw_type) or "未分类"
        if kind not in buckets:
            kind = "未分类"
        if candidate_id in decisions:
            buckets[kind].append(decisions[candidate_id])
    stats = {}
    for kind, rows in buckets.items():
        same_rows = [row for row in rows if row.get("decision") == "same"]
        same_targets = {row.get("ku_id", "") for row in same_rows}
        assert all(same_targets), f"same rows without target in {kind}"
        groups: dict[str, list[dict]] = {}
        for row in rows:
            if row.get("decision") == "new":
                group = sync.get_group(row.get("resolution_note", ""))
                assert group, f"new row without group: {row.get('candidate_id')}"
                groups.setdefault(group, []).append(row)
        registered_groups = registered_members = pending_groups = pending_members = 0
        for group, members in groups.items():
            mapped = [row.get("ku_id", "") for row in members]
            if all(mapped):
                assert len(set(mapped)) == 1 and mapped[0] in manifest_ids, group
                registered_groups += 1
                registered_members += len(members)
            else:
                assert not any(mapped), f"partially registered group: {group}"
                pending_groups += 1
                pending_members += len(members)
        stats[kind] = {
            "same_candidates": len(same_rows),
            "same_kus": len(same_targets),
            "new_candidates": sum(len(members) for members in groups.values()),
            "new_groups": len(groups),
            "registered_groups": registered_groups,
            "registered_members": registered_members,
            "pending_groups": pending_groups,
            "pending_members": pending_members,
            "conflict": sum(row.get("decision") == "conflict" for row in rows),
            "excluded": sum(row.get("decision") == "excluded" for row in rows),
            "undecided": sum(row.get("decision") == "undecided" for row in rows),
            "total": len(rows),
        }
    return stats, decisions


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Reconcile, register and adjudicate the Diario Romano cross-chapter endpoint.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--preview", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    archive_batch.DATE = DATE
    archive_batch.ANCHOR = ANCHOR
    archive_batch.BOOK_CITATION = BOOK_CITATION
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    candidate_fields, candidates = sync.read_csv(CANDIDATE_TABLE)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    relation_fields, relations = sync.read_csv(RELATIONS)
    _, sources = sync.read_csv(TABLES / "sources.csv")
    statements = sync.load_statements()
    by_candidate = {row["candidate_id"]: row for row in candidates}
    decision_by_candidate = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    by_statement = {row["statement_id"]: row for row in statements}
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    accepted_text = ACCEPTED.read_text(encoding="utf-8-sig")
    agents_text = AGENTS.read_text(encoding="utf-8-sig")

    assert ANCHOR not in process_text and ANCHOR not in result_text
    assert SOURCE_ID in {row["source_id"] for row in sources}
    assert all(candidate_id in by_candidate for candidate_id in CANDIDATES)
    assert all(statement_id in by_statement for statement_id in STATEMENTS)
    assert CARD_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)
    assert decision_by_candidate[CANDIDATES[0]]["decision"] == "new"
    assert sync.get_group(decision_by_candidate[CANDIDATES[0]]["resolution_note"]) == GROUP
    assert decision_by_candidate[CANDIDATES[1]]["decision"] == "undecided"
    assert decision_by_candidate[CANDIDATES[2]]["decision"] == "undecided"
    assert all(by_candidate[c]["suggested_type"] == "archive" for c in CANDIDATES)
    members_before = [
        row["candidate_id"] for row in alignments
        if row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert members_before == [CANDIDATES[0]], members_before

    targets = {
        row["statement_id"] for row in statements
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and (row.get("subject_candidate_id") in CANDIDATES or row.get("object_candidate_id") in CANDIDATES)
    }
    assert targets == set(STATEMENTS), targets
    for citation in CITATIONS:
        statement = by_statement[citation["statement"]]
        assert statement["subject_candidate_id"] == "cand-2962"
        assert statement["object_candidate_id"] in CANDIDATES and statement["predicate"] == "cites"
        assert not any(citation["statement"] in row.get("note", "") for row in relations)
    keeper = by_statement[STATEMENTS[-1]]
    assert keeper["subject_candidate_id"] == "cand-1168" and keeper["object_candidate_id"] == CANDIDATES[0]
    assert keeper["predicate"] == "kept_diary_recording_religious_festivals_and_miraculous_occurrences"
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    assert manifest_by_id["units/archives/patrons-and-painters"]["type"] == "archive"
    assert manifest_by_id["units/persons/giacinto-gigli"]["type"] == "person"
    domain_range = yaml.safe_load((ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8-sig"))["domain_range"]
    assert "archive" in domain_range["cites"]["domain"] and "archive" in domain_range["cites"]["range"]
    assert not any(key in domain_range for key in ("kept_by", "keeper_of"))
    source_cache = {}
    for source in SOURCES:
        source_cache.setdefault(source["source_file"], (ROOT / source["source_file"]).read_text(encoding="utf-8-sig"))
        normalized = " ".join(source_cache[source["source_file"]].split())
        assert " ".join(source["quotes"][0].split()) in normalized, source["source_file"]

    planned_alignment = [dict(row) for row in alignments]
    for candidate_id in CANDIDATES[1:]:
        row = next(row for row in planned_alignment if row.get("candidate_id") == candidate_id and not row.get("external_source"))
        previous = row["resolution_note"]
        row["decision"] = "new"
        row["ku_id"] = ""
        row["resolution_note"] = (
            f"{previous} | Earlier undecided note retained. Bibliography reconciliation {DATE}: "
            "chapter 21 p.423 identifies Diario Romano, edited by Giuseppe Ricciotti, Rome 1958; "
            "cand-6360 p.233 falls within cand-6269 pp.203-240. Both pointers identify the same published volume; "
            f"group={GROUP}."
        )
    primary = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATES[0] and not row.get("external_source"))
    primary["resolution_note"] += (
        f" Cross-chapter reconciliation {DATE}: bibliography p.423 identifies the cited 1958 edited volume; "
        "cand-6269 and cand-6360 are page locators in the same volume."
    )
    group_members = [
        row["candidate_id"] for row in planned_alignment
        if row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert set(group_members) == set(CANDIDATES) and len(group_members) == 3, group_members
    for candidate_id in CANDIDATES:
        next(row for row in planned_alignment if row.get("candidate_id") == candidate_id and not row.get("external_source"))["ku_id"] = KU_ID

    planned_candidates = [dict(row) for row in candidates]
    details = {
        CANDIDATES[0]: "Haskell says Gigli kept a detailed diary; the chapter 21 bibliography identifies the cited published volume as Diario Romano, edited by Giuseppe Ricciotti, Rome 1958. Cross-chapter candidates cand-6269 and cand-6360 are locators in the same volume. The publication was not independently consulted.",
        CANDIDATES[1]: "Haskell cites Gigli pp.203-240 for effects of the war in Rome. Chapter 21 bibliography identifies the volume as Diario Romano, edited by Giuseppe Ricciotti, Rome 1958; this is the same publication as cand-6076 and cand-6360. The cited pages and publication were not independently consulted.",
        CANDIDATES[2]: "Haskell cites Gigli p.233; this page falls within pp.203-240 cited in chapter 6 note 4. Chapter 21 bibliography identifies the same publication as Diario Romano, edited by Giuseppe Ricciotti, Rome 1958. The page and publication were not independently consulted.",
    }
    for candidate_id, detail in details.items():
        next(row for row in planned_candidates if row["candidate_id"] == candidate_id)["detail"] = detail

    card = archive_batch.make_archive_card(SPEC)
    boundary = (
        f"本 KU 对应 S3 身份组 {BT}{GROUP}{BT}，登记为独立 archive 对象。"
        "身份范围限于Haskell第21章书目列出的Diario Romano 1958年出版版本；不表示已查阅该卷、其引用页面或日记手稿。"
    )
    card = replace_one(card, r"^本 KU 对应 S3 身份组.*$", boundary, "archive card identity boundary")
    identity_line = (
        f"- **S3身份组：** {BT}{GROUP}{BT}；候选 "
        + "、".join(f"{BT}{candidate}{BT}" for candidate in CANDIDATES)
        + f" 均映射至本 KU。完整身份依据及逐条 S6 裁决见[本批过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )
    card = replace_one(card, r"^- \*\*S3身份组：\*\*.*$", identity_line, "archive card identity group")
    if (ROOT / CARD_PATH).exists():
        existing_card = (ROOT / CARD_PATH).read_text(encoding="utf-8-sig")
        assert existing_card == card, "partially created card differs from the reviewed batch"
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID, "type": "archive", "canonical_name": f"《{SPEC['name_zh']}》",
        "name_en": SPEC["name_en"], "source_task": TASK, "card_path": CARD_PATH,
    }]
    planned_accepted = archive_batch.insert_accepted_paths(accepted_text, [CARD_PATH])
    old_fields = [json.loads(line) for line in ENRICHMENT.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    new_fields = extract_fields(card, planned_manifest)
    assert len(new_fields) == 10
    field_total = len(old_fields) + len(new_fields)
    unverified = sum(row.get("evidence_status") == "unverified" for row in old_fields)

    next_relation_id = max(int(row["relation_id"].split("-")[1]) for row in relations) + 1
    new_relations = []
    for offset, citation in enumerate(CITATIONS):
        new_relations.append({
            "relation_id": f"rel-{next_relation_id + offset:04d}",
            "subject_ku_id": SUBJECT, "object_ku_id": KU_ID, "predicate": "cites",
            "time": "", "role": citation["role"], "scope": citation["scope"],
            "origin": "book", "status": "formal", "source_id": SOURCE_ID,
            "source_span": citation["span"], "source_file": citation["file"],
            "note": f"S2 statement: {citation['statement']}. This edge records Haskell's in-book citation only; the cited volume and contents were not consulted.",
        })
    natural_keys = {
        (r["subject_ku_id"], r["predicate"], r["object_ku_id"], r["time"], r["role"], r["scope"])
        for r in relations
    }
    for row in new_relations:
        key = (row["subject_ku_id"], row["predicate"], row["object_ku_id"], row["time"], row["role"], row["scope"])
        assert key not in natural_keys, key
        natural_keys.add(key)
    planned_relations = relations + new_relations

    type_stats, effective_decisions = summarize_s3_s4(planned_candidates, planned_alignment, planned_manifest)
    totals = {key: sum(values[key] for values in type_stats.values()) for key in next(iter(type_stats.values()))}
    coverage_count = len(effective_decisions)
    missing_decisions = len(planned_candidates) - coverage_count
    assert coverage_count == 12_388 and missing_decisions == 20
    s3_count = Counter(row["decision"] for row in effective_decisions.values())
    same_kus = {row["ku_id"] for row in effective_decisions.values() if row.get("decision") == "same"}
    direct_groups, direct_candidates, direct_members, _ = archive_batch.summarize_relation_endpoint_queue(
        planned_candidates, planned_alignment, planned_manifest, statements
    )
    pending_groups = totals["pending_groups"]
    pending_members = totals["pending_members"]
    non_direct_groups = pending_groups - direct_groups
    non_direct_members = pending_members - direct_members
    relation_status = Counter(row["status"] for row in planned_relations)
    missing_source = sum(not row.get("source_id") for row in planned_relations)
    candidate_count = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements)
    assert candidate_count == 10_417
    match = re.search(r"([\d,]+)/([\d,]+)条S2关系候选（([\d,]+) formal、([\d,]+) pending、([\d,]+) rejected）", result_text)
    assert match, "current S6 summary missing"
    old_s6 = [int(value.replace(",", "")) for value in match.groups()]
    assert old_s6[0] == sum(old_s6[2:]) and old_s6[1] == candidate_count
    s6 = (old_s6[0] + 5, old_s6[1], old_s6[2] + 4, old_s6[3] + 1, old_s6[4])

    batch_result = (
        f"### S3/S4/S5/S6 archive：Diario Romano 跨章引注端点（{DATE}）\n\n"
        "第21章印刷页423书目将Diario Romano列在Gigli, Giacinto名下，注明Giuseppe Ricciotti编、Roma、1958。"
        "据此把cand-6269（第6章p.146注4的pp.203–240）与cand-6360（第6章p.150注2的p.233）由undecided改为同一现有new身份组"
        f" {GROUP}，并与cand-6076合并；p.233位于pp.203–240范围内。只确定被引出版物身份，不表示已查阅该版本或页面。"
        "本批重算全书统计时只计非external_source主裁决行；20项只有外部对齐记录的候选仍不计作S3决定。按现有group标记重算，new组为4,789，修正此前当前快照多计1组；本次未更改其他S3候选。\n\n"
        f"S4将该archive组登记为 {KU_ID}，映射三条候选；S5新增{len(new_fields)}条书目与引注支持字段。"
        f"S6对四条明确引注逐条裁为formal cites（{new_relations[0]['relation_id']}–{new_relations[-1]['relation_id']}）；"
        "对Gigli“kept a detailed diary”候选裁为pending：原文支持保留行为，但当前受控关系类型没有准确的keeper谓词，不能改写为authored_by。\n\n"
        f"批后S3裁决行仍为12,388/12,408；new {totals['new_candidates']:,}项／{totals['new_groups']:,}组，undecided {totals['undecided']:,}项。"
        f"S4已登记{totals['registered_groups']:,}/{totals['new_groups']:,}组、{totals['registered_members']:,}/{totals['new_candidates']:,}条映射；"
        f"S5字段{field_total:,}条；S6逐项裁决{s6[0]:,}/{s6[1]:,}条，关系表{len(planned_relations):,}条。"
        f"逐项依据见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。\n"
    )
    marker = f"更新日期：{DATE}。\n"
    assert marker in result_text
    result_text = result_text.replace(marker, marker + "\n" + batch_result + "\n", 1)
    result_text = replace_one(
        result_text, r"^- \*\*S3：\*\*.*$",
        f"- **S3：** 候选共12,408项，其中12,388项有S3裁决行；另20项缺裁决行（person 16、archive 2、institution 2）。"
        f"现有same={s3_count['same']:,}（指向{len(same_kus):,}个既有KU）、new={s3_count['new']:,}（{totals['new_groups']:,}组）、"
        f"conflict={s3_count['conflict']:,}、excluded={s3_count['excluded']:,}、undecided={s3_count['undecided']:,}；缺行不计入任何决定类别。",
        "result S3 overview",
    )
    result_text = replace_one(
        result_text, r"^- \*\*S3未决类型：\*\*.*$",
        "- **S3未决类型：** undecided 5,240条，包括 work 1,625、person 1,078、archive 692、term 656、place 312、institution 120、event 115、family 18、procedure 2，以及类型未定622；另有9项冲突（work 5、person 4）。",
        "result S3 type counts",
    )
    result_text = replace_one(
        result_text, r"^- \*\*S4：\*\*.*$",
        f"- **S4：** 已登记{totals['registered_groups']:,}/{totals['new_groups']:,}组、{totals['registered_members']:,}/{totals['new_candidates']:,}条候选映射；"
        f"待登记{pending_groups:,}组／{pending_members:,}条映射，直接端点{direct_groups:,}组／{direct_members:,}条组成员映射。",
        "result S4 overview",
    )
    result_text = replace_one(
        result_text, r"^- \*\*S5：\*\*.*$",
        f"- **S5：** 字段表{field_total:,}条，其中{unverified:,}条为 unverified；未核字段按证据逐项处理。",
        "result S5 overview",
    )
    result_text = replace_one(
        result_text, r"^- \*\*S6：\*\*.*$",
        f"- **S6：** 关系表{len(planned_relations):,}条（{relation_status['formal']:,} formal、{relation_status['pending']:,} pending）；"
        f"过程记录累计逐条裁决{s6[0]:,}/{s6[1]:,}条S2关系候选（{s6[2]:,} formal、{s6[3]:,} pending、{s6[4]:,} rejected），"
        f"其余{s6[1]-s6[0]:,}条待逐项裁决。",
        "result S6 overview",
    )
    result_text = update_artifact_row(result_text, "KU 登记", f"| [KU 登记](../tables/ku-manifest.csv) | {len(planned_manifest):,} KU；新组登记与待登记分类型统计见下表 |")
    result_text = update_artifact_row(result_text, "字段表", f"| [字段表](../tables/enrichment.jsonl) | {field_total:,}条，其中{unverified:,}条 unverified |")
    result_text = update_artifact_row(
        result_text, "关系表",
        f"| [关系表](../tables/relations.csv) | {len(planned_relations):,}条：{relation_status['formal']:,} formal、{relation_status['pending']:,} pending；"
        f"{missing_source}条缺结构化 source_id；S2另有{candidate_count:,}条relation_candidate=true的statement，二者不是同一计数口径 |",
    )
    matrix_marker = "| 类型 | same（候选→KU） | new（候选／组） | S4 新组（已登记／待登记；待登候选） | conflict | excluded | undecided |"
    start = result_text.index(matrix_marker)
    end = result_text.index("\n\n", start)
    type_table, _ = sync.build_type_table(type_stats)
    result_text = result_text[:start] + type_table + result_text[end:]

    snapshot = next(line for line in agents_text.splitlines() if line.startswith("项目版本为"))
    replacements = (
        ("new=5,015", f"new={s3_count['new']:,}"),
        ("undecided=5,242", f"undecided={s3_count['undecided']:,}"),
        ("archive 694", "archive 692"),
        ("1,387/4,790组、1,592/5,015条候选映射", f"{totals['registered_groups']:,}/{totals['new_groups']:,}组、{totals['registered_members']:,}/{totals['new_candidates']:,}条候选映射"),
        ("3,403组／3,423条映射", f"{pending_groups:,}组／{pending_members:,}条映射"),
        ("1,657组／1,672条组成员映射", f"{direct_groups:,}组／{direct_members:,}条组成员映射"),
        ("1,746组／1,751条", f"{non_direct_groups:,}组／{non_direct_members:,}条"),
        ("12,014条、其中1,634条unverified", f"{field_total:,}条、其中{unverified:,}条unverified"),
        ("1,385条（1,382 formal、3 pending）", f"{len(planned_relations):,}条（{relation_status['formal']:,} formal、{relation_status['pending']:,} pending）"),
        ("243/10,417条S2关系候选（164 formal、65 pending、14 rejected）；其余10,174条", f"{s6[0]:,}/{s6[1]:,}条S2关系候选（{s6[2]:,} formal、{s6[3]:,} pending、{s6[4]:,} rejected）；其余{s6[1]-s6[0]:,}条"),
    )
    for old, new in replacements:
        assert old in snapshot, old
        snapshot = snapshot.replace(old, new, 1)
    agents_text = replace_one(agents_text, r"^项目版本为.*$", snapshot, "AGENTS current snapshot")

    process_note = f"""

<a id="{ANCHOR}"></a>

### S3/S4/S5/S6 archive：Diario Romano 跨章引注端点（{DATE}）

**S3跨章身份复核。** 第21章印刷页423、Markdown L523的书目著录为“Gigli, Giacinto: Diario Romano—a cura di Giuseppe Ricciotti, Roma 1958.”。它确认Haskell书目列出的出版物题名、编者形式、地点与年份。cand-6076原已属于new组{GROUP}；据新增书目证据，将第6章cand-6269（p.146 n.4，pp.203–240）与cand-6360（p.150 n.2，p.233）由undecided改为new并并入同组。p.233包含在pp.203–240之内，故二者是同一出版物的页定位，不是两种出版物。旧undecided理由保留于alignment resolution_note；被引版本与页面均未独立查阅。

**当前计数口径校正。** 统计只将alignment.csv中的非external_source主裁决行视为S3决定。20项只有外部对齐记录的候选仍为缺裁决，不计入same/new等类别。按当前唯一身份组标记重算，new组为4,789，修正此前当前快照所列4,790；本次只增加两个候选到既有组，没有处理其他缺行或未决对象。

**S4/S5登记。** 将身份组登记为{KU_ID}，映射cand-6076、cand-6269、cand-6360。卡片只记录Haskell书目和四处书内引注，不等同于日记手稿，不据书目署名新增Gigli作者关系。新增{len(new_fields)}条source_backed字段：书目类型、题名、责任者形式、编者、出版地、出版年及四处引注定位；来源ID {SOURCE_ID}未改写。

**S6逐条裁决。** 四条明确书内引注均裁为formal archive→archive cites；正式边只记录Haskell的引注路径，不确认被引版本内容：

| statement_id | 原书定位与引注 | 决定 | 正式关系 |
|---|---|---|---|
| {CITATIONS[0]['statement']} | 第5章p.131注4，Gigli passim，L147 | formal cites | {new_relations[0]['relation_id']} |
| {CITATIONS[1]['statement']} | 第5章p.133注1，Gigli passim及pp.77、162、290、324–325，L129 | formal cites | {new_relations[1]['relation_id']} |
| {CITATIONS[2]['statement']} | 第6章p.146注4，Gigli pp.203–240，L11 | formal cites | {new_relations[2]['relation_id']} |
| {CITATIONS[3]['statement']} | 第6章p.150注2，Gigli p.233，L131 | formal cites | {new_relations[3]['relation_id']} |
| {STATEMENTS[4]} | 第5章p.131正文称Gigli kept a detailed diary，L123 | pending；无准确keeper谓词，不改写为authored_by | 不写formal边 |

“Gigli kept a detailed diary”作为Haskell原书陈述保留。pending只表示当前关系词表不能准确表达该角色，不否认原书陈述。

批后S3决定行仍为12,388/12,408，另有20项缺行未变；same {s3_count['same']:,}、new {s3_count['new']:,}（{totals['new_groups']:,}组）、conflict {s3_count['conflict']:,}、excluded {s3_count['excluded']:,}、undecided {s3_count['undecided']:,}。S4已登记{totals['registered_groups']:,}/{totals['new_groups']:,}组、{totals['registered_members']:,}/{totals['new_candidates']:,}条映射；待登记{pending_groups:,}组／{pending_members:,}条，其中直接端点{direct_groups:,}组／{direct_members:,}条，非直接{non_direct_groups:,}组／{non_direct_members:,}条。S5字段{field_total:,}条、{unverified:,}条unverified。S6裁决{s6[0]:,}/{s6[1]:,}条（{s6[2]:,} formal、{s6[3]:,} pending、{s6[4]:,} rejected）；关系表{len(planned_relations):,}条，source_id缺失{missing_source}。
"""
    process_text = process_text.rstrip() + process_note

    if args.preview:
        print("REVIEWABLE BATCH PREVIEW")
        print(f"S3: cand-6269 and cand-6360 -> new in existing group {GROUP}; prior reasons retained")
        print(f"S4: +1 archive group, +3 candidate mappings -> {KU_ID}")
        print(f"S5: +{len(new_fields)} source_backed fields; total={field_total:,}; unverified={unverified:,}")
        print(f"S6: +4 formal cites and 1 pending keeper relation; total={s6[0]:,}/{s6[1]:,}")
        print(f"relations.csv: {len(planned_relations):,} rows ({relation_status['formal']} formal, {relation_status['pending']} pending)")
        print("\nALIGNMENT")
        for candidate in CANDIDATES:
            row = next(row for row in planned_alignment if row.get("candidate_id") == candidate and not row.get("external_source"))
            print(f"{candidate}: {row['decision']} | {sync.get_group(row.get('resolution_note', ''))} | {row.get('ku_id', '')}")
        print("\nNEW CARD")
        print(card)
        print("\nPROCESS DECISIONS")
        print(process_note)
        return 0

    if args.dry_run:
        print("dry-run passed: bibliography and four citation quotations verified")
        print(f"S3: two triggered candidates added to existing group {GROUP}; the 20 unrelated missing rows are unchanged")
        print(f"S4: 1 archive group / 3 mappings; accepted path and duplicate checks pass")
        print(f"S5: {len(new_fields)} source_backed fields; enrichment {len(old_fields):,}->{field_total:,}; unverified unchanged={unverified:,}")
        print(f"S6: 4 formal cites and 1 pending keeper relation; relation IDs {new_relations[0]['relation_id']}–{new_relations[-1]['relation_id']}")
        print(f"direct endpoint queue after batch: {direct_groups} groups/{direct_candidates} candidates/{direct_members} mappings")
        print(f"relation table: {len(planned_relations):,} rows; missing source_id={missing_source}")
        print("planned writes: card, accepted.yml, alignment/candidate/manifest tables, relations/enrichment tables, process/result/AGENTS")
        return 0

    write_text(ROOT / CARD_PATH, card)
    write_csv(ALIGNMENT, alignment_fields, planned_alignment)
    write_csv(CANDIDATE_TABLE, candidate_fields, planned_candidates)
    write_csv(MANIFEST, manifest_fields, planned_manifest)
    write_csv(RELATIONS, relation_fields, planned_relations)
    write_text(ACCEPTED, planned_accepted)
    with ENRICHMENT.open("a", encoding="utf-8", newline="\n") as handle:
        for row in new_fields:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    write_text(PROCESS, process_text)
    write_text(RESULT, result_text.rstrip() + "\n")
    write_text(AGENTS, agents_text)
    print(f"applied: {KU_ID}; 1 S4 group / 3 mappings; {len(new_fields)} S5 fields")
    print(f"S6: 4 formal cites ({new_relations[0]['relation_id']}–{new_relations[-1]['relation_id']}) and 1 documented pending decision")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
