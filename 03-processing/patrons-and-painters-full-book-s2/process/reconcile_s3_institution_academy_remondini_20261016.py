#!/usr/bin/env python3
"""Review an academy sub-entry and the Remondini cross-chapter institution group."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from collections import Counter
from pathlib import Path


ROOT = Path.cwd()
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
MANIFEST = TABLES / "ku-manifest.csv"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
PROCESS_REF = "S3-full-book-2026-10-16"
ACADEMY_KU = "units/institutions/academy-of-painting-and-sculpture-venice"
REMONDINI_KU = "units/institutions/remondini-firm"


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed changes")
    args = parser.parse_args()
    if not (ROOT / "04-knowledge" / "accepted.yml").exists():
        raise SystemExit("Run this script from the project root.")

    alignment_headers, alignment, alignment_bom = read_csv(ALIGNMENT)
    candidate_headers, candidate_rows, candidate_bom = read_csv(CANDIDATES)
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    primary = [row for row in alignment if not row["external_source"]]
    primary_by_id = {row["candidate_id"]: row for row in primary}
    if len(primary) != 12404 or len(alignment) != 12617 or sum(bool(row["external_source"]) for row in alignment) != 213:
        raise SystemExit("Unexpected alignment shape; inspect current S3 baseline.")
    if Counter(row["decision"] for row in primary) != Counter({"same": 1766, "new": 5005, "undecided": 5526, "excluded": 99, "conflict": 8}):
        raise SystemExit("Unexpected S3 decisions; inspect before retrying.")
    if primary_by_id["cand-0006"]["decision"] != "undecided" or primary_by_id["cand-0006"]["ku_id"]:
        raise SystemExit("cand-0006 no longer has its expected undecided S3 row.")
    for cid in ("cand-2122", "cand-2123"):
        row = primary_by_id[cid]
        if row["decision"] != "new" or row["ku_id"] != REMONDINI_KU or "group=sg3-institution-remondini" not in row["resolution_note"]:
            raise SystemExit(f"Unexpected prior Remondini routing for {cid}.")
    if candidates["cand-0006"]["suggested_type"] != "institution":
        raise SystemExit("cand-0006 no longer has institution type.")

    _, manifest, _ = read_csv(MANIFEST)
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    if manifest_by_id.get(ACADEMY_KU, {}).get("type") != "institution":
        raise SystemExit("The existing Venetian Academy institution KU is unavailable.")
    if manifest_by_id.get(REMONDINI_KU, {}).get("type") != "institution":
        raise SystemExit("The existing Remondini institution KU is unavailable.")

    with MENTIONS.open("r", encoding="utf-8-sig", newline="") as stream:
        mention_rows = {row["mention_id"]: row for row in csv.DictReader(stream)}
    expected_mentions = {
        "m-s2-ch10-p331-0021": "cand-0005",
        "m-s2-ch13-p340-036": "cand-2123",
        "m-chp19-p392-025": "cand-2122",
    }
    for mention_id, candidate_id in expected_mentions.items():
        if mention_rows.get(mention_id, {}).get("candidate_id") != candidate_id:
            raise SystemExit(f"Expected source anchor {mention_id} changed.")
    with STATEMENTS.open("r", encoding="utf-8-sig") as stream:
        statement_rows = [json.loads(line) for line in stream if line.strip()]
    academy_statement = next((row for row in statement_rows if row["statement_id"] == "st-chp10-p331-academy-borrowed-pictures"), None)
    if not academy_statement or academy_statement.get("subject_candidate_id") != "cand-0005":
        raise SystemExit("The p.331 Academy statement anchor changed.")
    remondini_statement = next((row for row in statement_rows if row["statement_id"] == "st-chp13-p340-remondini-established-at-bassano"), None)
    if not remondini_statement or remondini_statement.get("subject_candidate_id") != "cand-2123":
        raise SystemExit("The p.340 Remondini firm statement anchor changed.")

    alignment_copy = [dict(row) for row in alignment]
    by_id = {row["candidate_id"]: row for row in alignment_copy if not row["external_source"]}
    prior_notes = {cid: by_id[cid]["resolution_note"] for cid in ("cand-0006", "cand-2122", "cand-2123")}
    by_id["cand-0006"].update(
        decision="same",
        ku_id=ACADEMY_KU,
        process_ref=PROCESS_REF,
        resolution_note=(
            "group=sg3-institution-accademiadipitturaescultura; source_ref=A.csv#5 p.331; sub_entry=art exhibitions; "
            "S2 anchor: the p.331 account says the Academy's members were asked to exhibit annually and that the Academy borrowed pictures to complete the required number; that statement is mapped to cand-0005. "
            "The index sub-entry is a locator for exhibitions associated with the same Venetian Academy already established in ch.10 p.329 and registered as this KU; it is not a separate academy or the event itself. "
            f"Same -> {ACADEMY_KU}. prior_resolution_note={prior_notes['cand-0006']}"
        ),
    )
    by_id["cand-2122"].update(
        process_ref=PROCESS_REF,
        resolution_note=(
            "group=sg3-institution-remondini; source_refs=Q-R.csv#49 p.392; chp-19:19_CHP-19Appendix:l126-138#m-chp19-p392-025; "
            "chp-15:15_CHP-15_sec_ii:l90-113#m-chp15-p367-memmo-0055; "
            "Haskell identifies Giovanni Volpato's 22 April 1766 letter as addressed to the publisher Remondini; ch.15 bibliography also names Bassano [Remondini] as publisher in 1787. "
            "This matches the named Remondini firm in cand-2123's ch.13 p.340 account (established at Bassano, Venice branch, print/publishing activity), not an identified family member. "
            f"Retain one new institution group already registered at {REMONDINI_KU}; no new KU, external identity claim, or formal relation is added. "
            f"prior_resolution_note={prior_notes['cand-2122']}"
        ),
    )
    by_id["cand-2123"].update(
        process_ref=PROCESS_REF,
        resolution_note=(
            "group=sg3-institution-remondini; source_refs=Q-R.csv#50 p.340; chp-13:13_CHP-13_intro:l79-88#m-s2-ch13-p340-036; "
            "Haskell explicitly calls this the firm of Remondini, established at Bassano with a Venice branch, and describes its publishing and print-selling activities; the index sub-entry specifies prints associated with named artists. "
            "The ch.19 p.392 mention cand-2122 calls the same-named Remondini the publisher in a 1766 letter, consistent with the established firm and its period of activity. "
            f"Retain one new institution group already registered at {REMONDINI_KU}; do not expand it to the Remondini family or individual members. "
            f"prior_resolution_note={prior_notes['cand-2123']}"
        ),
    )

    result_text = RESULT.read_text(encoding="utf-8-sig")
    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    old_summary = "same=1,766（指向1,025个既有 KU）、new=5,005（4,830个身份组）、conflict=8、excluded=99、undecided=5,527。"
    new_summary = "same=1,767（指向1,026个既有 KU）、new=5,005（4,830个身份组）、conflict=8、excluded=99、undecided=5,525。"
    if result_text.count(old_summary) != 1:
        raise SystemExit("Could not find the current result summary line.")
    result_text = result_text.replace(old_summary, new_summary, 1)
    old_institution = "| institution | 176→140 | 200／196 | 4／192；195 | 0 | 0 | 121 |"
    new_institution = "| institution | 177→141 | 200／196 | 4／192；195 | 0 | 0 | 119 |"
    if result_text.count(old_institution) != 1:
        raise SystemExit("Could not find the current institution stats row.")
    result_text = result_text.replace(old_institution, new_institution, 1)
    old_total = "| **合计** | **1,766→1,025** | **5,005／4,830** | **281／4,549；4,653** | **8** | **99** | **5,526** |"
    new_total = "| **合计** | **1,767→1,026** | **5,005／4,830** | **281／4,549；4,653** | **8** | **99** | **5,525** |"
    if result_text.count(old_total) != 1:
        raise SystemExit("Could not find the current total S3/S4 type-progress row.")
    result_text = result_text.replace(old_total, new_total, 1)
    marker = "### S4 按类型登记进度"
    if result_text.count(marker) != 1:
        raise SystemExit("Could not find the S4 type-progress insertion point.")
    result_section = (
        "### S3 institution：威尼斯绘画与雕塑学院及 Remondini 跨章复核（2026-10-16）\n\n"
        "- cand-0006（A.csv#5，p.331，sub-entry `art exhibitions`）判为 same → [威尼斯绘画与雕塑学院](../units/institutions/academy-of-painting-and-sculpture-venice)。p.331 的 S2 叙述将学院成员与年度展览、借画补足展品数量相连，并已映射至 cand-0005；它是既有学院索引子目，不是第二所学院或展览事件。\n"
        "- cand-2122（Q-R.csv#49，p.392）与 cand-2123（Q-R.csv#50，p.340）保留 `sg3-institution-remondini` 同一 new institution 组，已共同映射至[Remondini 印刷商行](../units/institutions/remondini-firm)。第13章称其为 Bassano 商行、在 Venice 有分支并从事出版/印刷；第19章称 1766 年 Volpato 致出版者 Remondini 的信。此组表示商行，不推及家族或具名成员。没有新增外部身份行、KU 或正式关系。\n\n"
    )
    result_text = result_text.replace(marker, result_section + marker, 1)

    knowledge_text += (
        "\n\n### S3 institution：威尼斯绘画与雕塑学院及 Remondini 跨章身份复核（2026-10-16）\n\n"
        "- cand-0006（A.csv#5，p.331，`art exhibitions`）由 `undecided` 改为 `same`，映射至 `units/institutions/academy-of-painting-and-sculpture-venice`。索引子目挂在 Accademia di Pittura e Scultura 下；第10章 p.329 记该威尼斯学院于1756年成立，第10章 p.331 记其成员按年展示作品、学院借画补足数量，并将该 mention/statement 映射到 cand-0005。子目指学院参与的展览语境，不是另一家学院或独立展览事件。原 undecided 理由留在 alignment 行 `prior_resolution_note`。\n"
        "- cand-2122（Q-R.csv#49，p.392）与 cand-2123（Q-R.csv#50，p.340）继续同属 `sg3-institution-remondini`，共同映射至 `units/institutions/remondini-firm`。第13章 p.340 将 Remondini 明确称为设于 Bassano、在 Venice 有分支的出版/印刷商行；同章记其出版图书、主要发行单张版画并雇用艺术家制作复制图像。第19章 p.392 记 Giovanni Volpato 1766年4月22日致出版者 Remondini 的信；第15章 p.367 注2另列 `Bassano [Remondini], 1787`。名称、出版职能、地点和时间语境支持同一商行候选。不是 Remondini 家族或未具名成员的身份裁决。原书所述关系和机构活动不由 S3 验证；相关 S2 关系候选仍待 S6。\n"
        "- 本次不新增外部身份记录、KU、卡片、manifest 或正式关系。写回后 S3 为 same=1,767/1,026个KU、new=5,005/4,830组、conflict=8、excluded=99、undecided=5,525；S4 已登记281组/352条成员映射，待登记4,549组/4,653条。"
    )

    updates = {
        ALIGNMENT: encode_csv(alignment_headers, alignment_copy, alignment_bom),
        RESULT: ("\ufeff" + result_text).encode("utf-8"),
        KNOWLEDGE: ("\ufeff" + knowledge_text).encode("utf-8"),
    }
    print("PREVIEW" if not args.apply else "APPLY")
    for path, content in updates.items():
        print(f"  {path.relative_to(ROOT)}: {sha256(path.read_bytes())} -> {sha256(content)}")
    print("  candidate decisions:", dict(Counter(row["decision"] for row in primary)), "->", dict(Counter(row["decision"] for row in alignment_copy if not row["external_source"])))
    for cid in ("cand-0006", "cand-2122", "cand-2123"):
        print(" ", cid, by_id[cid]["decision"], by_id[cid]["ku_id"], by_id[cid]["process_ref"])
    if not args.apply:
        print("Dry-run only; pass --apply to write the changes.")
        return

    for path in updates:
        backup = path.with_name(path.name + ".bak-s3-institution-academy-remondini-20261016")
        if backup.exists():
            raise SystemExit(f"Recovery copy already exists: {backup}")
        shutil.copy2(path, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3-institution-academy-remondini-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied targeted institution identity updates and retained recovery copies.")


if __name__ == "__main__":
    main()
