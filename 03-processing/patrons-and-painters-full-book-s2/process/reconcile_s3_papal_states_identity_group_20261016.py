#!/usr/bin/env python3
"""Align the Papal States index candidates into one institution identity group."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path.cwd()
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
KNOWLEDGE = PROCESS / "knowledge.md"

GROUP = "sg3-institution-cand-1831"
PROCESS_REF = "S3-full-book-2026-10-16"
TRECCANI_URL = "https://www.treccani.it/enciclopedia/stato-pontificio/"
EXPECTED_STATEMENTS = {
    "st-chp2-sec-ii-l10-18-papal-states-wealth-at-accession",
    "st-chp2-sec-ii-l10-18-urban-professed-wealth-policy",
    "st-chp2-sec-ii-l10-18-urban-role-absolute-monarch",
    "st-chp2-sec-ii-l10-18-venetian-income-estimate",
    "st-chp2-sec-ii-l3-8-sovereignty",
    "st-chp2-secii-l42-50-cost_reported",
    "st-chp6-p146-castro-papal-territory",
    "st-chp6-p149-italian-economic-collapse",
    "st-chp6-p162-v1-05",
    "st-chp8-p203-bologna-second-capital",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), had_bom


def encode_csv(headers: list[str], rows: list[dict[str, str]], had_bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=headers, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    text = stream.getvalue()
    return ("\ufeff" + text if had_bom else text).encode("utf-8")


def get_group(note: str) -> str | None:
    match = re.search(r"\bgroup=([^;\s]+)", note)
    return match.group(1) if match else None


def summarize(candidates: dict[str, dict[str, str]], alignment: list[dict[str, str]]) -> dict[str, object]:
    primary = [row for row in alignment if not row["external_source"]]
    decisions = Counter(row["decision"] for row in primary)
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in primary:
        if row["decision"] == "new":
            group = get_group(row["resolution_note"])
            if group:
                groups[group].append(row)
    registered = sum(all(row["ku_id"] for row in values) for values in groups.values())
    pending = sum(not any(row["ku_id"] for row in values) for values in groups.values())
    pending_candidates = sum(not row["ku_id"] for values in groups.values() for row in values)
    by_type: dict[str, dict[str, int]] = {}
    for kind in ["archive", "event", "family", "institution", "person", "place", "procedure", "term", "work", "unclassified"]:
        candidate_ids = {
            candidate_id
            for candidate_id, candidate in candidates.items()
            if (candidate["suggested_type"] or "unclassified") == kind
        }
        subset = [row for row in primary if row["candidate_id"] in candidate_ids]
        new_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in subset:
            if row["decision"] == "new":
                group = get_group(row["resolution_note"])
                if group:
                    new_groups[group].append(row)
        by_type[kind] = {
            "same": sum(row["decision"] == "same" for row in subset),
            "same_kus": len({row["ku_id"] for row in subset if row["decision"] == "same" and row["ku_id"]}),
            "new_candidates": sum(row["decision"] == "new" for row in subset),
            "new_groups": len(new_groups),
            "registered_groups": sum(all(row["ku_id"] for row in values) for values in new_groups.values()),
            "pending_groups": sum(not any(row["ku_id"] for row in values) for values in new_groups.values()),
            "pending_candidates": sum(not row["ku_id"] for values in new_groups.values() for row in values),
            "conflict": sum(row["decision"] == "conflict" for row in subset),
            "excluded": sum(row["decision"] == "excluded" for row in subset),
            "undecided": sum(row["decision"] == "undecided" for row in subset),
        }
    return {
        "primary_rows": len(primary),
        "external_rows": sum(bool(row["external_source"]) for row in alignment),
        "decisions": decisions,
        "new_groups": len(groups),
        "registered_groups": registered,
        "pending_groups": pending,
        "pending_candidates": pending_candidates,
        "by_type": by_type,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed changes")
    args = parser.parse_args()
    if not (ROOT / "04-knowledge" / "accepted.yml").exists():
        raise SystemExit("Run this script from the project root.")

    alignment_headers, alignment, alignment_bom = read_csv(ALIGNMENT)
    candidate_headers, candidates_list, candidate_bom = read_csv(CANDIDATES)
    candidates = {row["candidate_id"]: row for row in candidates_list}
    if len(candidates) != len(candidates_list):
        raise SystemExit("Duplicate candidate IDs in entity-candidates.csv.")

    primary_rows = [row for row in alignment if not row["external_source"]]
    primary_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in primary_rows:
        primary_by_id[row["candidate_id"]].append(row)
    if len(primary_rows) != 12404 or len(alignment) != 12616:
        raise SystemExit(f"Unexpected alignment shape: primary={len(primary_rows)}, all={len(alignment)}")
    if any(len(primary_by_id[candidate_id]) != 1 for candidate_id in ("cand-1831", "cand-1832", "cand-1833")):
        raise SystemExit("Expected exactly one primary S3 row for each Papal States candidate.")
    if any(row["candidate_id"] == "cand-1831" and row["external_source"] == "Treccani Enciclopedia" for row in alignment):
        raise SystemExit("Treccani identity row already exists; inspect before retrying.")
    if any(candidate_id not in candidates for candidate_id in ("cand-1831", "cand-1832", "cand-1833")):
        raise SystemExit("A Papal States candidate is missing from entity-candidates.csv.")
    if candidates["cand-1831"]["suggested_type"] != "institution":
        raise SystemExit("cand-1831 is no longer the institution anchor.")
    for candidate_id in ("cand-1832", "cand-1833"):
        if candidates[candidate_id]["suggested_type"] != "term":
            raise SystemExit(f"Unexpected prior type for {candidate_id}.")
    expected_decisions = {"cand-1831": "new", "cand-1832": "undecided", "cand-1833": "new"}
    for candidate_id, expected in expected_decisions.items():
        if primary_by_id[candidate_id][0]["decision"] != expected:
            raise SystemExit(f"Unexpected prior S3 decision for {candidate_id}.")

    manifest_path = TABLES / "ku-manifest.csv"
    _, manifest, _ = read_csv(manifest_path)
    if any(row["type"] == "institution" and row["canonical_name"].strip().casefold() in {"papal states", "stato pontificio", "state of the church"} for row in manifest):
        raise SystemExit("A same-type Papal States KU now exists; this is no longer a new identity group.")

    with STATEMENTS.open("r", encoding="utf-8-sig") as stream:
        statement_rows = [json.loads(line) for line in stream if line.strip()]
    direct = [row for row in statement_rows if row.get("subject_candidate_id") == "cand-1831" or row.get("object_candidate_id") == "cand-1831"]
    direct_ids = {row["statement_id"] for row in direct}
    if direct_ids != EXPECTED_STATEMENTS or len(direct) != 10:
        raise SystemExit(f"Unexpected direct S2 statement set for cand-1831: {sorted(direct_ids)}")
    relation_count = sum(bool(row.get("qualifiers", {}).get("relation_candidate")) for row in direct)
    if relation_count != 8:
        raise SystemExit(f"Unexpected relation-candidate count: {relation_count}")

    with MENTIONS.open("r", encoding="utf-8-sig", newline="") as stream:
        mention_rows = list(csv.DictReader(stream))
    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    if mention_by_id.get("m-chp2-seciv-l114-125-0026", {}).get("candidate_id") != "cand-1833":
        raise SystemExit("cand-1833 source anchor changed; inspect before retrying.")
    for mention_id in ("m-chp6-p149-045", "m-chp6-p162-v-008"):
        if mention_by_id.get(mention_id, {}).get("candidate_id") != "cand-1831":
            raise SystemExit(f"Expected direct Papal States anchor {mention_id} not found.")

    alignment_copy = [dict(row) for row in alignment]
    candidate_copy = [dict(row) for row in candidates_list]
    by_id = {row["candidate_id"]: row for row in alignment_copy if not row["external_source"]}
    prior_notes = {candidate_id: by_id[candidate_id]["resolution_note"] for candidate_id in expected_decisions}

    by_id["cand-1831"].update(
        process_ref=PROCESS_REF,
        resolution_note=(
            f"group={GROUP}; members=cand-1831,cand-1832,cand-1833; "
            "source_ref=chp-2:02_CHP-2_sec_ii:l10-18#m-chp2-secii-l10-18-0008; "
            "cross_chapter_s2_statements=10 (ch.2 pp.31-35; ch.5; ch.6 pp.146,149,162; ch.8 pp.203,224); "
            "Identity: the explicit Papal States, States of the Church, and contextual state/territory references denote one political-territorial entity. "
            "Taxonomy: institution, separate from Rome as a city and from the Holy See candidate cand-4424. "
            "Treccani identifies Stato della Chiesa, governed by the pope as temporal sovereign until 1870; this supports identity/type only. "
            "No same-type institution KU exists; one new group is pending S4. "
            f"prior_resolution_note={prior_notes['cand-1831']}"
        ),
    )
    by_id["cand-1832"].update(
        decision="new",
        process_ref=PROCESS_REF,
        resolution_note=(
            f"group={GROUP}; source_ref=P.csv#31; index_pages=149,150,152,161,162; sub_entry=increasing poverty; "
            "S3 type correction: term -> institution. This is an index locator/subentry for the Papal States polity, not a separate term KU. "
            "Index locators p.149 and p.162 correspond to S2 mentions m-chp6-p149-045 and m-chp6-p162-v-008, both explicitly mapped to the Papal States political entity cand-1831. "
            "All three Papal States candidates therefore share one new institution group for S4; uncited index locators are not treated as independently verified claims. "
            f"prior_resolution_note={prior_notes['cand-1832']}"
        ),
    )
    by_id["cand-1833"].update(
        process_ref=PROCESS_REF,
        resolution_note=(
            f"group={GROUP}; source_ref=P.csv#32; index_page=32; sub_entry=wealth of in 1623; "
            "S2 source mention m-chp2-seciv-l114-125-0026 explicitly identifies the Papal States as a political entity, distinct from the Papacy. "
            "S3 type correction: term -> institution. The index subentry is a locator for the polity and its reported wealth, not a separate term KU. "
            "The direct ch.2 p.32 statements about the Papal States' wealth/income also map to cand-1831; assign all three index candidates to one new institution group for S4. "
            f"prior_resolution_note={prior_notes['cand-1833']}"
        ),
    )

    for candidate in candidate_copy:
        if candidate["candidate_id"] in {"cand-1832", "cand-1833"}:
            candidate["suggested_type"] = "institution"

    numeric_ids = [int(row["alignment_id"].split("-")[-1]) for row in alignment_copy if row["alignment_id"].startswith("aln-") and row["alignment_id"].split("-")[-1].isdigit()]
    next_alignment_id = f"aln-{max(numeric_ids) + 1:04d}"
    if any(row["alignment_id"] == next_alignment_id for row in alignment_copy):
        raise SystemExit(f"Alignment ID already exists: {next_alignment_id}")
    alignment_copy.append(
        {
            "alignment_id": next_alignment_id,
            "candidate_id": "cand-1831",
            "ku_id": "",
            "external_source": "Treccani Enciclopedia",
            "external_id": TRECCANI_URL,
            "decision": "new",
            "accessed_date": "2026-10-16",
            "process_ref": PROCESS_REF,
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity only: Treccani entry 'Pontificio, Stato' identifies the Stato della Chiesa as a temporal political entity governed by the pope until 1870. "
                "Supports the institution type and the Papal States / States of the Church identity; does not establish all book claims, relations, or an identity with the Holy See."
            ),
        }
    )

    before = summarize(candidates, alignment)
    after_candidates = {row["candidate_id"]: row for row in candidate_copy}
    after = summarize(after_candidates, alignment_copy)
    if before["decisions"] != Counter({"same": 1766, "new": 5004, "conflict": 8, "excluded": 99, "undecided": 5527}):
        raise SystemExit(f"Unexpected S3 baseline: {before['decisions']}")
    if after["decisions"] != Counter({"same": 1766, "new": 5005, "conflict": 8, "excluded": 99, "undecided": 5526}):
        raise SystemExit(f"Unexpected S3 result: {after['decisions']}")
    if after["new_groups"] != 4830 or after["registered_groups"] != 281 or after["pending_groups"] != 4549 or after["pending_candidates"] != 4653:
        raise SystemExit(f"Unexpected S4 group routing after merge: {after}")

    result_text = RESULT.read_text(encoding="utf-8-sig")
    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    if "### S3 institution：Papal States 跨章身份组裁决（2026-10-16）" in result_text or "### S3 institution：Papal States 跨章身份组裁决（2026-10-16）" in knowledge_text:
        raise SystemExit("Papal States process entry already exists; inspect before retrying.")

    replacements = [
        ("new=5,004（4,831个身份组）", "new=5,005（4,830个身份组）"),
        ("尚待登记4,550组、4,652条映射", "尚待登记4,549组、4,653条映射"),
        ("12,616 条：12,404 条候选决定记录及 212 条外部身份记录", "12,617 条：12,404 条候选决定记录及 213 条外部身份记录"),
        ("212条外部身份记录单独保留", "213条外部身份记录单独保留"),
        ("| institution | 176→140 | 198／196 | 4／192；193 | 0 | 0 | 121 |", "| institution | 176→140 | 200／196 | 4／192；195 | 0 | 0 | 121 |"),
        ("| term | 40→34 | 944／931 | 4／927；937 | 0 | 1 | 657 |", "| term | 40→34 | 943／930 | 4／926；936 | 0 | 1 | 656 |"),
        ("| **合计** | **1,766→1,025** | **5,004／4,831** | **281／4,550；4,652** | **8** | **99** | **5,527** |", "| **合计** | **1,766→1,025** | **5,005／4,830** | **281／4,549；4,653** | **8** | **99** | **5,526** |"),
    ]
    for old, new in replacements:
        if result_text.count(old) != 1:
            raise SystemExit(f"Expected one result occurrence for {old!r}, found {result_text.count(old)}")
        result_text = result_text.replace(old, new, 1)
    result_section = (
        "### S3 institution：Papal States 跨章身份组裁决（2026-10-16）\n\n"
        "- cand-1831、cand-1832、cand-1833 → `sg3-institution-cand-1831`，合为一个 new institution 身份组，待 S4 登记。cand-1832、cand-1833 原标 term，按索引子目和对应 S2 提及改正为 institution；两者是 Papal States 政体的索引定位，不另建概念 KU。\n"
        "- Treccani《Pontificio, Stato》确认 Stato della Chiesa 是教宗作为世俗主权者统治的政治实体（至1870年）；本条只支持对象身份与类型。Rome 城市和 Holy See 候选 cand-4424 保持分立。没有同类型既有 institution KU。10条直接 S2 陈述中8条关系候选留待 S6；未创建 KU、卡片或正式关系。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)。\n\n"
    )
    marker = "### S4 按类型登记进度"
    if result_text.count(marker) != 1:
        raise SystemExit("Could not find unique S4 type-progress insertion point.")
    result_text = result_text.replace(marker, result_section + marker, 1)

    knowledge_section = (
        "\n\n### S3 institution：Papal States 跨章身份组裁决（2026-10-16）\n\n"
        "- cand-1831（P.csv#30）、cand-1832（P.csv#31，sub-entry `increasing poverty`）、cand-1833（P.csv#32，sub-entry `wealth of in 1623`）统一进入 `sg3-institution-cand-1831`，均为同一项 new institution 候选组，待 S4 登记；没有拆成概念或重复实体 KU。cand-1832、cand-1833 的 `suggested_type` 从 `term` 改为 `institution`，历史类型与原裁决理由保存在相应 alignment 行的 `prior_resolution_note`。\n"
        "- 跨章身份依据：第2章 pp.31–35 讨论 Papal States 的政治权力与收入；第5章涉及其领土/职务语境；第6章 pp.146、149、162 明确称 papal territory、Papal States、States of the Church；第8章 pp.203、224 再以该政治疆域定位 Bologna、Macerata 与 Raimondo。10条直接 S2 statement 中8条为关系候选，继续留待 S6；身份归组不裁定其内容或正式关系。\n"
        "- cand-1832 的索引页码 p.149、p.162 与 S2 mentions `m-chp6-p149-045`、`m-chp6-p162-v-008` 指向同一政体；其余 locator 仅作为索引定位，不据此验证全部相关断言。cand-1833 的 mention `m-chp2-seciv-l114-125-0026` 明确将 Papal States 作为政治实体并区别于 Papacy；p.32 的财富/收入叙述也映射到 cand-1831。\n"
        "- 外部身份核对：Treccani《Pontificio, Stato》，https://www.treccani.it/enciclopedia/stato-pontificio/，访问于2026-10-16；条目称 Stato della Chiesa 由教宗作为世俗主权者统治至1870年。该记录只支持历史政体身份及 institution 类型，不支持本书全部具体断言。manifest 中未发现同类型 Papal States KU。Rome 作为城市与 Holy See 候选 cand-4424 均分开保留；本轮不建立二者关系。\n"
        "- 本次向 alignment 追加 Treccani 外部身份记录 aln-12617；无 KU/card/manifest/relations 写入。写回后 S3 为 same=1,766、new=5,005/4,830组、conflict=8、excluded=99、undecided=5,526；S4 已登记281组/352条成员映射，待登记4,549组/4,653条。"
    )
    knowledge_text += knowledge_section
    updates = {
        ALIGNMENT: encode_csv(alignment_headers, alignment_copy, alignment_bom),
        CANDIDATES: encode_csv(candidate_headers, candidate_copy, candidate_bom),
        RESULT: ("\ufeff" + result_text).encode("utf-8"),
        KNOWLEDGE: ("\ufeff" + knowledge_text).encode("utf-8"),
    }
    print("PREVIEW" if not args.apply else "APPLY")
    for path, content in updates.items():
        print(f"  {path.relative_to(ROOT)}: {sha256(path.read_bytes())} -> {sha256(content)}")
    print("  candidate decisions:", dict(before["decisions"]), "->", dict(after["decisions"]))
    print("  new groups / S4 pending groups / pending candidates:", before["new_groups"], before["pending_groups"], before["pending_candidates"], "->", after["new_groups"], after["pending_groups"], after["pending_candidates"])
    print("  external identity records:", before["external_rows"], "->", after["external_rows"])
    for candidate_id in ("cand-1831", "cand-1832", "cand-1833"):
        print(" ", candidate_id, after_candidates[candidate_id]["suggested_type"], by_id[candidate_id]["decision"], get_group(by_id[candidate_id]["resolution_note"]))
    if not args.apply:
        print("Dry-run only; pass --apply to write the changes.")
        return

    for path in updates:
        backup = path.with_name(path.name + ".bak-s3-papal-states-20261016")
        if backup.exists():
            raise SystemExit(f"Recovery copy already exists: {backup}")
        shutil.copy2(path, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3-papal-states-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied targeted S3 updates and retained recovery copies.")


if __name__ == "__main__":
    main()
