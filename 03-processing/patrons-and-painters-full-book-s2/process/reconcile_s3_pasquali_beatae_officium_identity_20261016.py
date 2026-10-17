#!/usr/bin/env python3
"""Resolve the Pasquali Beatae Mariae Virginis Officium archive candidate."""

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
GROUP = "archive-group-pasquali-officium-1740"
SBN_ID = "PUVE008510"
SBN_URL = "https://opac.bibliotecauniversitaria.pi.it/bid/PUVE008510"
EXPECTED_STATEMENTS = {
    "st-chp13-p337-officium-commissioned-and-financed-by-caime",
    "st-chp13-p337-officium-distinct-from-pasquali-general-output",
    "st-chp13-p337-officium-plates-religious-intimacy",
    "st-chp13-p337-pasquali-employed-piazzetta-for-officium",
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
    if Counter(row["decision"] for row in primary) != Counter({"same": 1767, "new": 5005, "undecided": 5525, "excluded": 99, "conflict": 8}):
        raise SystemExit("Unexpected S3 decisions; inspect before retrying.")
    candidate = candidates.get("cand-1849")
    decision = primary_by_id.get("cand-1849")
    if not candidate or candidate["suggested_type"] != "archive" or candidate["index_entry_id"] != "P.csv#49" or candidate["sub_entry"] != "Beatae Mariae Virginis Officium":
        raise SystemExit("cand-1849 index identity has changed.")
    if not decision or decision["decision"] != "undecided" or decision["ku_id"]:
        raise SystemExit("cand-1849 is no longer the expected undecided candidate.")
    if any(row["candidate_id"] == "cand-1849" and row["external_source"] == "OPAC SBN (Biblioteca Universitaria di Pisa)" for row in alignment):
        raise SystemExit("SBN identity row already exists; inspect before retrying.")
    if any(f"group={GROUP}" in row["resolution_note"] for row in primary):
        raise SystemExit("The proposed Pasquali archive group ID is already in use.")

    _, manifest, _ = read_csv(MANIFEST)
    if any(
        row["type"] == "archive"
        and "beatae maria" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    ):
        raise SystemExit("A same-title archive KU now exists; compare it before deciding new.")

    with MENTIONS.open("r", encoding="utf-8-sig", newline="") as stream:
        mention_rows = {row["mention_id"]: row for row in csv.DictReader(stream)}
    for mention_id in ("m-s2-ch13-p337-032", "m-s2-ch13-p337-033"):
        if mention_rows.get(mention_id, {}).get("candidate_id") != "cand-1849":
            raise SystemExit(f"The source mention {mention_id} changed.")
    with STATEMENTS.open("r", encoding="utf-8-sig") as stream:
        statements = [json.loads(line) for line in stream if line.strip()]
    direct = [row for row in statements if row.get("subject_candidate_id") == "cand-1849" or row.get("object_candidate_id") == "cand-1849"]
    direct_ids = {row["statement_id"] for row in direct}
    if direct_ids != EXPECTED_STATEMENTS or len(direct) != 4:
        raise SystemExit(f"Unexpected S2 statement set for cand-1849: {sorted(direct_ids)}")
    relation_count = sum(bool(row.get("qualifiers", {}).get("relation_candidate")) for row in direct)
    if relation_count != 3:
        raise SystemExit(f"Unexpected S2 relation-candidate count: {relation_count}")

    alignment_copy = [dict(row) for row in alignment]
    by_id = {row["candidate_id"]: row for row in alignment_copy if not row["external_source"]}
    prior_note = by_id["cand-1849"]["resolution_note"]
    by_id["cand-1849"].update(
        decision="new",
        process_ref=PROCESS_REF,
        resolution_note=(
            f"group={GROUP}; source_ref=P.csv#49 p.337; index_subentry=Beatae Mariae Virginis Officium; "
            "S2 source mentions=m-s2-ch13-p337-032,m-s2-ch13-p337-033; statements=st-chp13-p337-officium-commissioned-and-financed-by-caime,st-chp13-p337-officium-distinct-from-pasquali-general-output,st-chp13-p337-officium-plates-religious-intimacy,st-chp13-p337-pasquali-employed-piazzetta-for-officium. "
            "Haskell identifies a specific illustrated book published in 1740. OPAC SBN PUVE008510 records the same title as a monograph, Venetiis: Apud Jo. Baptistam Pasquali, 1740; bibliographic identity matches the source candidate. "
            "One new archive group, pending S4; distinct from cand-1848 Dactylografa Smithiana, cand-1851 Goldoni edition, and cand-12144's unnamed aggregate of Pasquali publications. The catalog does not verify the source's commission, financing, or evaluation claims. "
            f"prior_resolution_note={prior_note}"
        ),
    )

    numeric_ids = [int(row["alignment_id"].split("-")[-1]) for row in alignment if row["alignment_id"].startswith("aln-") and row["alignment_id"].split("-")[-1].isdigit()]
    new_alignment_id = f"aln-{max(numeric_ids) + 1:04d}"
    if any(row["alignment_id"] == new_alignment_id for row in alignment):
        raise SystemExit(f"Alignment ID already exists: {new_alignment_id}")
    alignment_copy.append(
        {
            "alignment_id": new_alignment_id,
            "candidate_id": "cand-1849",
            "ku_id": "",
            "external_source": "OPAC SBN (Biblioteca Universitaria di Pisa)",
            "external_id": SBN_ID,
            "decision": "new",
            "accessed_date": "2026-10-16",
            "process_ref": PROCESS_REF,
            "legacy_ku_id": "",
            "resolution_note": (
                f"Identity only: {SBN_URL} (record {SBN_ID}) describes the titled work as a printed monograph and gives Venetiis, Apud Jo. Baptistam Pasquali, 1740. "
                "This confirms the bibliographic identity and edition anchor; it does not verify Haskell's claims about commissioning, financing, artistic reception, or relations."
            ),
        }
    )

    result_text = RESULT.read_text(encoding="utf-8-sig")
    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    replacements = [
        ("new=5,005（4,830个身份组）", "new=5,006（4,831个身份组）"),
        ("undecided=5,525。S4 已登记281组、映射352条成员候选；尚待登记4,549组、4,653条映射。", "undecided=5,524。S4 已登记281组、映射352条成员候选；尚待登记4,550组、4,654条映射。"),
        ("12,617 条：12,404 条候选决定记录及 213 条外部身份记录", "12,618 条：12,404 条候选决定记录及 214 条外部身份记录"),
        ("213条外部身份记录单独保留", "214条外部身份记录单独保留"),
        ("| new | 5,005 | 按 4,830 个当前身份组进入 S4；每组登记一个 KU |", "| new | 5,006 | 按 4,831 个当前身份组进入 S4；每组登记一个 KU |"),
        ("| undecided | 5,525 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |", "| undecided | 5,524 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |"),
        ("| archive | 78→61 | 1,246／1,214 | 29／1,185；1,211 | 0 | 18 | 758 |", "| archive | 78→61 | 1,247／1,215 | 29／1,186；1,212 | 0 | 18 | 757 |"),
        ("| **合计** | **1,767→1,026** | **5,005／4,830** | **281／4,549；4,653** | **8** | **99** | **5,525** |", "| **合计** | **1,767→1,026** | **5,006／4,831** | **281／4,550；4,654** | **8** | **99** | **5,524** |"),
    ]
    for old, new in replacements:
        if result_text.count(old) != 1:
            raise SystemExit(f"Expected one result occurrence for {old!r}, found {result_text.count(old)}")
        result_text = result_text.replace(old, new, 1)
    result_section = (
        "### S3 archive：Pasquali《Beatae Mariae Virginis Officium》身份裁决（2026-10-16）\n\n"
        "- cand-1849（P.csv#49，p.337）从 `undecided` 改为 new，进入 `archive-group-pasquali-officium-1740`，待 S4 登记。Haskell 直接给出题名与1740年出版信息；OPAC SBN PUVE008510 将同题名著录为单行本，出版地 Venetiis、出版者 Jo. Baptistam Pasquali、年份1740。\n"
        "- 本组仅表示该书的书目身份。与 cand-1848《Dactylografa Smithiana》、cand-1851 Goldoni 十七卷版、cand-12144 未具名的 Pasquali 一般出版物群区分；未将 Morazzoni 注释引用当成该书本身。3条直接关系候选留待 S6；本轮不验证委托、资助或艺术评价，不创建 KU、卡片或正式关系。"
    )
    marker = "### S4 按类型登记进度"
    if result_text.count(marker) != 1:
        raise SystemExit("Could not find the S4 type-progress insertion point.")
    result_text = result_text.replace(marker, result_section + "\n\n" + marker, 1)

    knowledge_text += (
        "\n\n### S3 archive：Pasquali《Beatae Mariae Virginis Officium》身份裁决（2026-10-16）\n\n"
        "- cand-1849（P.csv#49，sub-entry `Beatae Mariae Virginis Officium`，p.337）由 `undecided` 改为 `new`，identity group 为 `archive-group-pasquali-officium-1740`，KU 尚待 S4。第13章 p.337 称 Pasquali 于1740年出版该插图宗教小书，并明确将它与其一般出版物区分；四条直接 S2 statements 记录其插图、出版、委托/资助及作者评价，后续关系判断仍由 S6 分别处理。\n"
        "- 身份记录：OPAC SBN（Biblioteca Universitaria di Pisa），记录 PUVE008510，https://opac.bibliotecauniversitaria.pi.it/bid/PUVE008510，访问于2026-10-16。目录将题名 `Beatae Mariae Virginis officium` 著录为 printed monograph，出版项 Venetiis : Apud Jo. Baptistam Pasquali, 1740。它与原书索引题名、年份和出版者吻合；仅支持文献身份和版本定位，不证明委托、资助、作品质量或书内关系。\n"
        "- 边界：与 cand-1848 `Dactylografa Smithiana`（另一出版物）、cand-1851 Goldoni 十七卷版及 cand-12144 未具名的 Pasquali 一般出版物集合分别处理；脚注引文 cand-10175 指向 Morazzoni p.116，并非 Officium 本身。3条关系候选留待 S6。本次只向 alignment 追加外部身份记录，不新建 KU/card/manifest/relations。\n"
        "- 写回后 S3 为 same=1,767/1,026个KU、new=5,006/4,831组、conflict=8、excluded=99、undecided=5,524；S4 已登记281组/352条成员映射，待登记4,550组/4,654条。"
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
    print("  archive group:", "cand-1849 ->", GROUP, "-> S4 pending")
    print("  external records:", sum(bool(row["external_source"]) for row in alignment), "->", sum(bool(row["external_source"]) for row in alignment_copy), "new alignment ID:", new_alignment_id)
    if not args.apply:
        print("Dry-run only; pass --apply to write the changes.")
        return

    for path in updates:
        backup = path.with_name(path.name + ".bak-s3-pasquali-officium-20261016")
        if backup.exists():
            raise SystemExit(f"Recovery copy already exists: {backup}")
        shutil.copy2(path, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3-pasquali-officium-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied the archive identity decision and retained recovery copies.")


if __name__ == "__main__":
    main()
