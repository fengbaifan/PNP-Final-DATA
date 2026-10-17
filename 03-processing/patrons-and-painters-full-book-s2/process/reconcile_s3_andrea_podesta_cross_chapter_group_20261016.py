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
INDEX = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "P.csv"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
PROCESS_REF = "S3-full-book-2026-10-16"
GROUP = "new-person:andrea-podesta-070b483a9a"
BACKUP_SUFFIX = ".bak-s3-andrea-podesta-cross-chapter-20261016"
GETTY_URL = "https://www.getty.edu/vow/ULANFullDisplay?find=&nation=&role=&subjectid=500021868"
LOUVRE_URL = "https://arts-graphiques.louvre.fr/detail/artistes/0/2039-PODESTA-Giovanni-Andrea"


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
    _, candidates, _ = read_csv(CANDIDATES)
    _, mentions, _ = read_csv(MENTIONS)
    primary = [row for row in alignment if not row["external_source"]]
    external = [row for row in alignment if row["external_source"]]
    primary_by_id = {row["candidate_id"]: row for row in primary}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if len(primary) != 12404 or Counter(row["decision"] for row in primary) != Counter(
        {"same": 1774, "new": 5023, "conflict": 8, "excluded": 100, "undecided": 5499}
    ):
        raise SystemExit("Unexpected S3 baseline; inspect current candidate decisions before applying.")
    if len(alignment) != 12623 or len(external) != 219:
        raise SystemExit("Unexpected alignment row count; inspect the current baseline.")

    for cid in ("cand-5558", "cand-1964"):
        if cid not in primary_by_id or cid not in candidate_by_id:
            raise SystemExit(f"Missing candidate or alignment row for {cid}.")
        if candidate_by_id[cid]["suggested_type"] != "person":
            raise SystemExit(f"{cid} is no longer a person candidate.")
        if primary_by_id[cid]["ku_id"]:
            raise SystemExit(f"{cid} already maps to a KU; inspect before changing its S3 decision.")
    if primary_by_id["cand-5558"]["decision"] != "new" or GROUP not in primary_by_id["cand-5558"]["resolution_note"]:
        raise SystemExit("cand-5558 no longer anchors the expected new-person group.")
    if primary_by_id["cand-1964"]["decision"] != "undecided":
        raise SystemExit("cand-1964 is no longer the expected undecided index candidate.")
    if candidate_by_id["cand-1964"]["index_entry_id"] != "P.csv#165" or candidate_by_id["cand-1964"]["index_page_range"] != "97, 105, 184n":
        raise SystemExit("cand-1964 index locator changed; inspect the candidate before grouping.")
    if not any("m-chp4-sec-i-0216" == row["mention_id"] and row["candidate_id"] == "cand-5558" for row in mentions):
        raise SystemExit("The Chapter 4 p.97 body mention is missing or no longer maps to cand-5558.")
    if not any("m-chp4-sec-ii-l80-89-podesta-first-name" == row["mention_id"] and row["candidate_id"] == "cand-5558" for row in mentions):
        raise SystemExit("The Chapter 4 p.105 body name anchor is missing or no longer maps to cand-5558.")
    statement_lines = STATEMENTS.read_text(encoding="utf-8-sig").splitlines()
    statement = next((json.loads(line) for line in statement_lines if '"statement_id": "st-chp7-p184-n3-podesta-inventory"' in line), None)
    if not statement or statement.get("subject_candidate_id") != "cand-5558" or statement.get("object_candidate_id") != "cand-7091":
        raise SystemExit("The Chapter 7 note 3 source-local identity statement changed; inspect before proceeding.")
    index_text = INDEX.read_text(encoding="utf-8-sig")
    if '"Podestà, Andrea",,,,"97, 105, 184n"' not in index_text:
        raise SystemExit("The P.csv index locator no longer matches cand-1964.")

    existing_external_ids = {row["external_id"] for row in external}
    if GETTY_URL in existing_external_ids or LOUVRE_URL in existing_external_ids:
        raise SystemExit("A Getty or Louvre identity row already exists; inspect before adding another.")
    numeric_ids = [int(row["alignment_id"].removeprefix("aln-")) for row in alignment if row["alignment_id"].startswith("aln-") and row["alignment_id"][4:].isdigit()]
    next_id = max(numeric_ids) + 1

    updated_alignment = [dict(row) for row in alignment]
    updated_primary = {row["candidate_id"]: row for row in updated_alignment if not row["external_source"]}
    previous_5558 = updated_primary["cand-5558"]["resolution_note"]
    previous_1964 = updated_primary["cand-1964"]["resolution_note"]
    source_anchor = (
        "Chapter 4 p.97 body m-chp4-sec-i-0216 (Andrea Podesta) and p.105 body mentions "
        "m-chp4-sec-ii-l80-89-podesta-first-name / m-chp4-sec-ii-l80-89-podesta-surname (Andrea Podesta); "
        "Chapter 7 p.184 n.3 statement st-chp7-p184-n3-podesta-inventory gives the expanded form Giovanni Andrea Podesta."
    )
    identity_basis = (
        "Getty ULAN 500021868 prefers Podesta, Giovanni Andrea and lists Podestà, Andrea as an alternate name; "
        "the Louvre graphic-arts authority record for PODESTA Giovanni Andrea also lists Podesta Andrea as a synonym. "
        "The index locator P.csv#165 pages 97, 105, 184n matches the explicit Chapter 4 anchors and Chapter 7 full-name context. "
        "The identity decision does not verify Haskell's reported role in compiling the 1661 inventory; de Cosnac item 1240 was not independently consulted."
    )
    updated_primary["cand-5558"].update(
        process_ref=PROCESS_REF,
        resolution_note=(
            f"source_ref=candidate=cand-5558;candidate_source_ref={candidate_by_id['cand-5558']['candidate_source_ref']}; "
            f"identity_peers=cand-1964;group={GROUP};external_identity=Getty ULAN 500021868, Louvre artist authority; "
            f"source_anchors={source_anchor} {identity_basis} prior_resolution_note={previous_5558}"
        ),
    )
    updated_primary["cand-1964"].update(
        decision="new",
        process_ref=PROCESS_REF,
        resolution_note=(
            "source_ref=candidate=cand-1964;index_entry=P.csv#165;index_pages=97, 105, 184n; "
            "identity_peers=cand-5558; "
            f"group={GROUP};external_identity=Getty ULAN 500021868, Louvre artist authority; "
            f"source_anchors={source_anchor} {identity_basis} "
            f"prior_resolution_note={previous_1964}"
        ),
    )
    external_rows = [
        {
            "alignment_id": f"aln-{next_id}",
            "candidate_id": "cand-5558",
            "ku_id": "",
            "external_source": "Getty ULAN",
            "external_id": GETTY_URL,
            "decision": "new",
            "accessed_date": "2026-10-16",
            "process_ref": PROCESS_REF,
            "legacy_ku_id": "",
            "resolution_note": "Identity only: Getty ULAN 500021868 prefers Podesta, Giovanni Andrea and lists Podestà, Andrea as an alternate name; the record also identifies him as Genoese and as painter, printmaker/engraver, and etcher. This supports the name and identity match only; it does not verify the reported 1661 inventory role or all source claims.",
        },
        {
            "alignment_id": f"aln-{next_id + 1}",
            "candidate_id": "cand-5558",
            "ku_id": "",
            "external_source": "Louvre, Département des Arts graphiques",
            "external_id": LOUVRE_URL,
            "decision": "new",
            "accessed_date": "2026-10-16",
            "process_ref": PROCESS_REF,
            "legacy_ku_id": "",
            "resolution_note": "Identity only: the Louvre authority record PODESTA Giovanni Andrea lists Podesta Andrea as a synonym and identifies the artist as painter and engraver, with date range 1608–vers 1654/1674. This supports the name and identity match only; it does not verify the reported 1661 inventory role or all source claims.",
        },
    ]
    updated_alignment.extend(external_rows)

    result_text = RESULT.read_text(encoding="utf-8-sig")
    replacements = [
        ("new=5,023（4,840个身份组）、conflict=8、excluded=100、undecided=5,499。S4 已登记305组、映射398条成员候选；尚待登记4,535组、4,625条映射。", "new=5,024（4,840个身份组）、conflict=8、excluded=100、undecided=5,498。S4 已登记305组、映射398条成员候选；尚待登记4,535组、4,626条映射。"),
        ("| person | 1,004→387 | 1,177／1,084 | 89／995；1,040 | 3 | 7 | 1,273 |", "| person | 1,004→387 | 1,178／1,084 | 89／995；1,041 | 3 | 7 | 1,272 |"),
        ("| **合计** | **1,774→1,026** | **5,023／4,840** | **305／4,535；4,625** | **8** | **100** | **5,499** |", "| **合计** | **1,774→1,026** | **5,024／4,840** | **305／4,535；4,626** | **8** | **100** | **5,498** |"),
    ]
    for old, new in replacements:
        if result_text.count(old) != 1:
            raise SystemExit(f"Expected one result occurrence of {old!r}; found {result_text.count(old)}.")
        result_text = result_text.replace(old, new, 1)
    section = (
        "### S3 person：Podestà 跨章身份归组（2026-10-16）\n\n"
        "- `cand-5558`（第4章p.97、p.105正文人物锚点）与 `cand-1964`（P.csv#165，索引页码97、105、184n）同属 `new-person:andrea-podesta-070b483a9a`。第7章p.184注3给出全名 Giovanni Andrea Podesta；Getty ULAN 500021868 将 `Podestà, Andrea` 列为别名，卢浮宫艺术家权威记录列出 `Podesta Andrea` 同义名。`cand-1964` 原 `undecided` 的缺少正文身份锚点问题据此解决，候选保留自身索引定位并加入现有new组。\n"
        "- 本裁决只确认人物身份，不确认Haskell转述的1661年清单编制者身份；de Cosnac item 1240未独立查阅。S3新增1条new候选、未增加new身份组、undecided减少1；S4该person组仍待登记，两条候选共映射至一个KU。相关关系不在本轮写入 `relations.csv`。\n"
    )
    marker = "## 未解决项与交接限制"
    if result_text.count(marker) != 1:
        raise SystemExit("Could not locate the current result insertion point.")
    result_text = result_text.replace(marker, section + "\n" + marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge_text += (
        "\n\n### S3 person：Podestà 跨章身份归组（2026-10-16）\n\n"
        "- `cand-5558`（第4章p.97正文Andrea Podesta及p.105跨行Andrea / Podesta）与 `cand-1964`（P.csv#165，索引页码97、105、184n）归入同一身份组 `new-person:andrea-podesta-070b483a9a`。第7章p.184注3的 `st-chp7-p184-n3-podesta-inventory` 使用完整形式Giovanni Andrea Podesta，并映射到 `cand-5558` 与1661年清单候选 `cand-7091`。\n"
        "- Getty ULAN 500021868 的规范名为Podesta, Giovanni Andrea，别名含Podestà, Andrea；卢浮宫艺术家权威记录的规范名为PODESTA Giovanni Andrea，同义名含Podesta Andrea。索引候选原裁决 `undecided` 的理由为缺少映射S2正文提及；本次依据索引页码与第4章显名正文锚点、跨章全名表述和两条机构权威身份记录改为 `new`，指向既有new组。原未决理由保留在alignment `prior_resolution_note`。\n"
        "- 此身份裁决不验证Haskell关于Podesta参与编制1661年清单的转述；de Cosnac item 1240与底层清单未独立查阅。该人物组尚未登记为KU；其与清单的可能关系留待关系阶段审查，不新增正式边。候选决定new增加1而new组数不变；未决减少1，S4待登记候选映射增加1。"
    )

    updates = {
        ALIGNMENT: encode_csv(alignment_headers, updated_alignment, alignment_bom),
        RESULT: ("\ufeff" + result_text).encode("utf-8"),
        KNOWLEDGE: ("\ufeff" + knowledge_text).encode("utf-8"),
    }
    print("PREVIEW" if not args.apply else "APPLY")
    for path, content in updates.items():
        print(f"  {path.relative_to(ROOT)}: {sha256(path.read_bytes())} -> {sha256(content)}")
    print(f"  S3 cand-1964: undecided -> new; group={GROUP} with cand-5558")
    print(f"  external identity rows: aln-{next_id} Getty ULAN; aln-{next_id + 1} Louvre")
    print("  primary decisions: new 5,023 -> 5,024; undecided 5,499 -> 5,498; new groups unchanged at 4,840")
    print("  pending S4 mappings: 4,625 -> 4,626")
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
        temporary = path.with_name(path.name + ".tmp-s3-andrea-podesta-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied the cross-chapter identity group and retained recovery copies.")


if __name__ == "__main__":
    main()
