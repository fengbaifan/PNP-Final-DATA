from __future__ import annotations

import argparse
import csv
import hashlib
import io
import shutil
from collections import Counter
from pathlib import Path


ROOT = Path.cwd()
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
PROCESS_REF = "S3-full-book-2026-10-16"
GROUP = "archive-group-daumale-inventaire-1653-1861"
BACKUP_SUFFIX = ".bak-s3-daumale-cross-chapter-20261016"
OLD_6807_NAME = "D'Aumale, cited publication; title and edition unspecified"
FULL_TITLE_NAME = "Duc d’Aumale, Inventaire de tous les meubles du Cardinal Mazarin (London, 1861)"


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


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not (ROOT / "04-knowledge" / "accepted.yml").exists():
        raise SystemExit("Run this script from the project root.")

    alignment_headers, alignment, alignment_bom = read_csv(ALIGNMENT)
    candidate_headers, candidate_rows, candidate_bom = read_csv(CANDIDATES)
    primary = [row for row in alignment if not row["external_source"]]
    external = [row for row in alignment if row["external_source"]]
    primary_by_id = {row["candidate_id"]: row for row in primary}
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    if len(primary) != 12404 or len(alignment) != 12622 or len(external) != 218:
        raise SystemExit("Unexpected alignment shape; inspect the current S3 baseline.")
    expected_decisions = Counter({"same": 1768, "new": 5017, "undecided": 5512, "excluded": 99, "conflict": 8})
    if Counter(row["decision"] for row in primary) != expected_decisions:
        raise SystemExit("Unexpected S3 decisions; inspect the current baseline.")
    if not {"cand-6807", "cand-11231"}.issubset(primary_by_id) or not {"cand-6807", "cand-11231"}.issubset(candidate_by_id):
        raise SystemExit("One of the D’Aumale candidates is missing.")
    if primary_by_id["cand-6807"]["decision"] != "new" or primary_by_id["cand-11231"]["decision"] != "new":
        raise SystemExit("D’Aumale candidates no longer have new decisions.")
    if "group=archive-group-daumale-inventaire-1653-1861" not in primary_by_id["cand-6807"]["resolution_note"]:
        raise SystemExit("cand-6807 is not in the expected D’Aumale group.")
    if "group=archive-group-1d71af235d8f" not in primary_by_id["cand-11231"]["resolution_note"]:
        raise SystemExit("cand-11231 no longer has its expected prior group.")
    if candidate_by_id["cand-6807"]["canonical_name"] != FULL_TITLE_NAME or candidate_by_id["cand-11231"]["canonical_name"] != FULL_TITLE_NAME:
        raise SystemExit("The expected natural-key collision changed; inspect before regrouping.")
    if not any(row["external_id"] == "https://catalogue.bnf.fr/ark:/12148/cb30039849q" and row["candidate_id"] == "cand-6807" for row in external):
        raise SystemExit("The BnF record for the printed D’Aumale edition is missing.")

    updated_alignment = [dict(row) for row in alignment]
    updated_by_id = {row["candidate_id"]: row for row in updated_alignment if not row["external_source"]}
    old_6807_note = updated_by_id["cand-6807"]["resolution_note"]
    old_11231_note = updated_by_id["cand-11231"]["resolution_note"]
    updated_by_id["cand-6807"]["resolution_note"] = (
        "source_refs=citation_candidate=chp-7:07_CHP-7_sec_i:l160-168#L168; bibliography_candidate=chp-21:21_CHP-21Bibliography:l47-85#L82; "
        "statements=st-chp7-p183-n2-cite-daumale,st-chp7-p184-n2-cite-daumale,st-chp21-bib-l47-85-entry-27; "
        f"identity_peers=cand-11231; group={GROUP}; external_identity=BnF Catalogue général FRBNF30039849, https://catalogue.bnf.fr/ark:/12148/cb30039849q; "
        "The p.7 chapter citations and ch.21 bibliography candidate identify the same Duc d’Aumale 1861 publication. Retain both source candidates in one group; the BnF record confirms the title, author, publication data and relationship to the 1653 Condé original. This is the printed edition, distinct from the underlying inventory manuscript cand-6814 and the 1661 inventory cand-7091. "
        f"prior_resolution_note={old_6807_note}"
    )
    updated_by_id["cand-11231"].update(
        process_ref=PROCESS_REF,
        resolution_note=(
            "source_ref=candidate_ref=chp-21:21_CHP-21Bibliography:l47-85#L82; mention=m-chp21-bib-l47-85-027; "
            "statement=st-chp21-bib-l47-85-entry-27; identity_peers=cand-6807; "
            f"group={GROUP}; external_identity=BnF Catalogue général FRBNF30039849, https://catalogue.bnf.fr/ark:/12148/cb30039849q; "
            "The full bibliography entry identifies the same 1861 D’Aumale edition cited in ch.7 notes 2 and 3. Keep this bibliography candidate as a member of the existing archive identity group rather than creating a duplicate KU. The BnF catalog supports the publication identity only. "
            f"prior_resolution_note={old_11231_note}"
        ),
    )

    updated_candidates = [dict(row) for row in candidate_rows]
    updated_candidate_by_id = {row["candidate_id"]: row for row in updated_candidates}
    updated_candidate_by_id["cand-6807"]["canonical_name"] = OLD_6807_NAME

    result_text = RESULT.read_text(encoding="utf-8-sig")
    replacements = [
        ("new=5,017（4,834个身份组）", "new=5,017（4,833个身份组）"),
        ("尚待登记4,553组、4,665条映射。", "尚待登记4,552组、4,665条映射。"),
        ("| new | 5,017 | 按 4,834 个当前身份组进入 S4；每组登记一个 KU |", "| new | 5,017 | 按 4,833 个当前身份组进入 S4；每组登记一个 KU |"),
        ("| archive | 79→61 | 1,258／1,218 | 29／1,189；1,223 | 0 | 18 | 745 |", "| archive | 79→61 | 1,258／1,217 | 29／1,188；1,223 | 0 | 18 | 745 |"),
        ("| **合计** | **1,768→1,026** | **5,017／4,834** | **281／4,553；4,665** | **8** | **99** | **5,512** |", "| **合计** | **1,768→1,026** | **5,017／4,833** | **281／4,552；4,665** | **8** | **99** | **5,512** |"),
    ]
    for old, new in replacements:
        if result_text.count(old) != 1:
            raise SystemExit(f"Expected one result occurrence of {old!r}, found {result_text.count(old)}")
        result_text = result_text.replace(old, new, 1)
    old_result_paragraph = "`cand-6807` 从 `undecided` 改为 `new`，身份组 `archive-group-daumale-inventaire-1653-1861`，表示 Duc d’Aumale 于1861年刊行的 *Inventaire de tous les meubles du Cardinal Mazarin*；`cand-6814` 与索引候选 `cand-1597` 同组 `archive-group-mazarin-inventory-1653`，表示正文所称1653年清单原件。"
    new_result_paragraph = "`cand-6807`（第7章两条注释引用）由 `undecided` 改为 `new`，与第21章书目候选 `cand-11231`（原属独立 new 组）合入 `archive-group-daumale-inventaire-1653-1861`，表示 Duc d’Aumale 于1861年刊行的 *Inventaire de tous les meubles du Cardinal Mazarin*；`cand-6814` 与索引候选 `cand-1597` 同组 `archive-group-mazarin-inventory-1653`，表示正文所称1653年清单原件。"
    if result_text.count(old_result_paragraph) != 1:
        raise SystemExit("Could not locate the current D’Aumale result paragraph for cross-chapter update.")
    result_text = result_text.replace(old_result_paragraph, new_result_paragraph, 1)
    result_text = result_text.replace(
        "BnF FRBNF30039849 确认1861年版及其所据 Condé 原件。",
        "第21章书目候选 `cand-11231` 与第7章注释候选指向相同刊本，并据此合组；BnF FRBNF30039849 确认1861年版及其所据 Condé 原件。",
        1,
    )

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge_text += (
        "\n\n### S3 archive：d’Aumale 1861年清单刊本跨章候选归组（2026-10-16）\n\n"
        "- 复核发现在第21章书目登记中已有 `cand-11231`，与第7章脚注出版物候选 `cand-6807` 都指向同一 d’Aumale 1861 年刊本。两者现同属 `archive-group-daumale-inventaire-1653-1861`，不重复登记第二个 KU；其来源锚点分别保留为第21章书目行和第7章注释定位。BnF FRBNF30039849 同时支持这两个候选的书目身份。\n"
        "- 为遵守 `entity-candidates.csv` 非索引候选 `canonical_name + suggested_type` 自然键唯一约束，`cand-6807` 恢复原候选名“D'Aumale, cited publication; title and edition unspecified”；完整规范书名、书目字段和映射已写入其 detail 与 alignment 裁决。`cand-11231` 保留完整题名，二者的同一身份组在 alignment 中明确记录。\n"
        "- 组数复核：三组更动的净效应为 Brienne 卷 I/III 两组并为一组（−1）、1653 清单与索引 locator 新增一组（+1）、d’Aumale 1861 刊本并入既有 cand-11231 组（0），故总 new 身份组由4,833保持4,833；new 候选增加4，S4 待登记映射增加4。"
    )

    updates = {
        ALIGNMENT: encode_csv(alignment_headers, updated_alignment, alignment_bom),
        CANDIDATES: encode_csv(candidate_headers, updated_candidates, candidate_bom),
        RESULT: ("\ufeff" + result_text).encode("utf-8"),
        KNOWLEDGE: ("\ufeff" + knowledge_text).encode("utf-8"),
    }
    print("PREVIEW" if not args.apply else "APPLY")
    for path, content in updates.items():
        print(f"  {path.relative_to(ROOT)}: {sha256(path.read_bytes())} -> {sha256(content)}")
    print("  D’Aumale cross-chapter group: cand-6807 + cand-11231 ->", GROUP)
    print("  primary S3 decisions unchanged; new groups=4,833; pending S4 groups=4,552; mappings=4,665")
    if not args.apply:
        print("Dry-run only; pass --apply to write the changes.")
        return

    for path in updates:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"Recovery copy already exists: {backup}")
        shutil.copy2(path, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3-daumale-cross-chapter-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied the cross-chapter group and retained recovery copies.")


if __name__ == "__main__":
    main()
