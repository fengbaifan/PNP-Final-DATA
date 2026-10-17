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
MENTIONS = TABLES / "mentions.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
TARGET = "units/persons/mazarin"
GROUP = "sg3-ku-units-persons-mazarin"
PROCESS_REF = "S3-full-book-2026-10-16"
BACKUP_SUFFIX = ".bak-s3-mazarin-index-person-20261016"
IDS = ["cand-1588", "cand-1589", "cand-1590", "cand-1591", "cand-1592", "cand-1593"]


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
    import hashlib

    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not ACCEPTED.exists():
        raise SystemExit("Run this script from the project root.")

    alignment_headers, alignment, alignment_bom = read_csv(ALIGNMENT)
    _, candidates, _ = read_csv(CANDIDATES)
    primary = [row for row in alignment if not row["external_source"]]
    external = [row for row in alignment if row["external_source"]]
    primary_by_id = {row["candidate_id"]: row for row in primary}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if len(primary) != 12404 or len(alignment) != 12622 or len(external) != 218:
        raise SystemExit("Unexpected alignment shape; inspect the current S3 baseline.")
    expected = Counter({"same": 1768, "new": 5017, "undecided": 5512, "excluded": 99, "conflict": 8})
    if Counter(row["decision"] for row in primary) != expected:
        raise SystemExit("Unexpected S3 decisions; inspect the current baseline.")
    for cid in IDS:
        candidate = candidate_by_id.get(cid)
        decision = primary_by_id.get(cid)
        if not candidate or not decision:
            raise SystemExit(f"Missing candidate or alignment row for {cid}.")
        if candidate["canonical_name"] != "Mazarin, Cardinal" or candidate["suggested_type"] != "person":
            raise SystemExit(f"{cid} no longer identifies the expected Mazarin person index candidate.")
        if decision["decision"] != "undecided" or decision["ku_id"]:
            raise SystemExit(f"{cid} is no longer the expected undecided candidate.")

    _, manifest, _ = read_csv(MANIFEST)
    accepted_text = ACCEPTED.read_text(encoding="utf-8-sig")
    card_path = ROOT / "04-knowledge" / "units" / "persons" / "mazarin.md"
    if not card_path.exists() or "04-knowledge/units/persons/mazarin.md" not in accepted_text:
        raise SystemExit("The expected accepted Mazarin person card is missing.")
    manifest_entry = next((row for row in manifest if row["ku_id"] == TARGET), None)
    if not manifest_entry or manifest_entry.get("type") != "person":
        raise SystemExit("The expected Mazarin person KU is not in the manifest.")

    with MENTIONS.open("r", encoding="utf-8-sig", newline="") as stream:
        mentions = list(csv.DictReader(stream))
    mazarin_mentions = [row for row in mentions if row["candidate_id"] == "cand-1588"]
    if len(mazarin_mentions) < 20 or not any("Cardinal Mazarin" in row["surface_form"] for row in mazarin_mentions):
        raise SystemExit("cand-1588 no longer has the expected repeated full-form source anchors.")

    updated_alignment = [dict(row) for row in alignment]
    updated_by_id = {row["candidate_id"]: row for row in updated_alignment if not row["external_source"]}
    old_notes = {cid: updated_by_id[cid]["resolution_note"] for cid in IDS}
    subentries = {
        "cand-1588": "M.csv#127 main heading, pages 139, 155, 175–187, 402",
        "cand-1589": "M.csv#128, subentry ‘and Poussin’, pages 180–181",
        "cand-1590": "M.csv#129, subentry ‘and Poussin’, page 181",
        "cand-1591": "M.csv#130, subentry ‘and Romanelli’, pages 181–182",
        "cand-1592": "M.csv#131, subentry ‘and Sacchetti family’, page 180",
        "cand-1593": "M.csv#132, subentry ‘association with Barberini and Bentivoglio families’, page 180",
    }
    for cid in IDS:
        updated_by_id[cid].update(
            decision="same",
            ku_id=TARGET,
            process_ref=PROCESS_REF,
            resolution_note=(
                f"source_ref=index_candidate={cid};index_locator={subentries[cid]}; "
                "identity_peers=cand-1588,cand-1589,cand-1590,cand-1591,cand-1592,cand-1593; "
                f"group={GROUP}; target={TARGET}; existing_card=04-knowledge/units/persons/mazarin.md; "
                "The index parent heading identifies Cardinal Mazarin, and the subentry changes only the topical locator. The accepted person card records Jules Mazarin, his title as cardinal, full name, and the source-supported gallery context; repeated Chapter 7 mentions include the explicit form ‘Cardinal Mazarin’. Reuse the existing person identity for all six index rows. The Poussin, Romanelli, Sacchetti, Barberini, and Bentivoglio subentries are index context only and do not establish formal relations. "
                f"prior_resolution_note={old_notes[cid]}"
            ),
        )

    result_text = RESULT.read_text(encoding="utf-8-sig")
    replacements = [
        ("same=1,768（指向1,026个既有 KU）", "same=1,774（指向1,026个既有 KU）"),
        ("undecided=5,512。S4 已登记281组、映射352条成员候选；尚待登记4,552组、4,665条映射。", "undecided=5,506。S4 已登记281组、映射352条成员候选；尚待登记4,552组、4,665条映射。"),
        ("| same | 1,768 | 指向 1,026 个既有 KU |", "| same | 1,774 | 指向 1,026 个既有 KU |"),
        ("| undecided | 5,512 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |", "| undecided | 5,506 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |"),
        ("| person | 998→387 | 1,176／1,083 | 88／995；1,040 | 3 | 7 | 1,280 |", "| person | 1,004→387 | 1,176／1,083 | 88／995；1,040 | 3 | 7 | 1,274 |"),
        ("| **合计** | **1,768→1,026** | **5,017／4,833** | **281／4,552；4,665** | **8** | **99** | **5,512** |", "| **合计** | **1,774→1,026** | **5,017／4,833** | **281／4,552；4,665** | **8** | **99** | **5,506** |"),
    ]
    for old, new in replacements:
        if result_text.count(old) != 1:
            raise SystemExit(f"Expected one result occurrence of {old!r}, found {result_text.count(old)}")
        result_text = result_text.replace(old, new, 1)
    section = (
        "### S3 person：Mazarin 索引主项与子目复用（2026-10-16）\n\n"
        "- `cand-1588`（M.csv#127）及索引子目 `cand-1589`–`cand-1593`（M.csv#128–132）均由 `undecided` 改为 `same` → [Jules Mazarin 人物卡](../units/persons/mazarin.md)。主项及其页码 locator 中的“and Poussin”“and Romanelli”“and Sacchetti family”“association with Barberini and Bentivoglio families”仍指向同一索引父项人物；既有卡以图版标题、全名、生卒与头衔识别该人，正文反复使用 Cardinal Mazarin 明称。\n"
        "- 子目仅保留为主题/页码定位，不由此新增 Poussin、Romanelli、Sacchetti、Barberini 或 Bentivoglio 关系边。六条候选共享 `sg3-ku-units-persons-mazarin` 复用组；不新增外部身份行、KU、卡片或关系。"
    )
    marker = "### S4 按类型登记进度"
    if result_text.count(marker) != 1:
        raise SystemExit("Could not find the S4 type-progress insertion point.")
    result_text = result_text.replace(marker, section + "\n\n" + marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge_text += (
        "\n\n### S3 person：Mazarin 索引主项与子目复用（2026-10-16）\n\n"
        "- `cand-1588`（M.csv#127，Mazarin, Cardinal）及 `cand-1589`–`cand-1593`（M.csv#128–132：and Poussin 两条、and Romanelli、and Sacchetti family、association with Barberini and Bentivoglio families）由 `undecided` 改为 `same`，全部映射至 `units/persons/mazarin`，共用 `sg3-ku-units-persons-mazarin`。主索引项与五个关系/主题子目都以 `Mazarin, Cardinal` 为父项，未产生另一个人物身份。\n"
        "- 复用证据：接受卡 `04-knowledge/units/persons/mazarin.md` 已依图版标题、S2 全名/头衔及生卒等证据记录 Jules Mazarin；第7章 p.180–186 正文及其他索引页范围出现明确 `Cardinal Mazarin` 名称。主项跨多章的索引页码可由候选 `cand-1588` 的 mentions 回链；子项标题与父项共同保存索引定位。\n"
        "- 原 alignment note 将主候选搁置于单名不足，但现有接收卡与原书全名/头衔锚点已解决实体身份。保留其余关联人物的独立 KU；索引并列只作语境定位，不裁决师承、交往、赞助或其他关系。本批没有新增 KU、卡片、外部记录或正式关系。"
    )

    updates = {
        ALIGNMENT: encode_csv(alignment_headers, updated_alignment, alignment_bom),
        RESULT: ("\ufeff" + result_text).encode("utf-8"),
        KNOWLEDGE: ("\ufeff" + knowledge_text).encode("utf-8"),
    }
    new_primary = [row for row in updated_alignment if not row["external_source"]]
    print("PREVIEW" if not args.apply else "APPLY")
    for path, content in updates.items():
        print(f"  {path.relative_to(ROOT)}: {sha256(path.read_bytes())} -> {sha256(content)}")
    print("  primary S3 decisions:", dict(Counter(row["decision"] for row in primary)), "->", dict(Counter(row["decision"] for row in new_primary)))
    print("  same mappings: six index candidates ->", TARGET, "; new S4 groups/mappings unchanged")
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
        temporary = path.with_name(path.name + ".tmp-s3-mazarin-index-person-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied the person reuse decision and retained recovery copies.")


if __name__ == "__main__":
    main()
