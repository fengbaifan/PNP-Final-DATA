from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import shutil
from pathlib import Path

import yaml


ROOT = Path.cwd()
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
DATE = "2026-10-16"

GROUP = "archive-group-gallacini-trattato-1767"
MEMBERS = ("cand-1110", "cand-9257")
OLD_GROUPS = {
    "cand-1110": "archive-group-db9bd962571d",
    "cand-9257": "archive-group-8924556dfa3f",
}
SEPARATE_CANDIDATE = "cand-9258"
SEPARATE_GROUP = "archive-group-13318baef7cf"
KU_ID = "units/archives/trattato-sopra-gli-errori-degli-architetti-1767"
CARD_REL = "04-knowledge/units/archives/trattato-sopra-gli-errori-degli-architetti-1767.md"
BACKUP_SUFFIX = ".bak-s3s4-gallacini-trattato-1767-20261016"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

BODY_FILE = "10_CHP-10_intro.md"
INDEX_FILE = "22_CHP-22Index_intro.md"
BODY_QUOTE = (
    "Palladio, and in 1767 he published one of the manuscripts in his collection by the "
    "seventeenth-century theorist TeoFilo Gallacini. The title was indicative: Trattato "
    "sopragli errori degli architetti, and within a very short time the book was brought "
    "up to date by"
)
INDEX_QUOTE = "Trattato sopragli errori degli architetti, 309"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), has_bom


def encode_csv(fields: list[str], rows: list[dict[str, str]], has_bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    text = stream.getvalue()
    return ("\ufeff" + text if has_bom else text).encode("utf-8")


def encode_text(path: Path, text: str) -> bytes:
    has_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    return ("\ufeff" + text if has_bom else text).encode("utf-8")


def group_of(note: str) -> str:
    match = re.search(r"group=([^;|\s]+)", note)
    return match.group(1) if match else ""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one occurrence of {old!r}, found {count}")
    return text.replace(old, new, 1)


def collapse(text: str) -> str:
    return " ".join(text.split())


def make_card() -> str:
    title_zh = "《建筑师错误论》1767年刊本"
    title_en = "Trattato sopra gli errori degli architetti (1767 publication)"
    body_path = f"../../../02-sources/02-Markdown/{BODY_FILE}"
    index_path = f"../../../02-sources/02-Markdown/{INDEX_FILE}"
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": (
                "第10章；印刷页309；Markdown行473；S2记录页图读法为“sopra gli”；"
                "原书与所述手稿未独立查阅"
            ),
            "sentence_summary": (
                "Haskell称Smith于1767年刊行其收藏的一份Teofilo Gallacini手稿，题为 "
                "Trattato sopra gli errori degli architetti；并称该书很快由Antonio Visentini更新。"
            ),
            "original_quotes": [{"source_span": "lines 473-474", "text": BODY_QUOTE}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{BODY_FILE}",
                "source_span": "lines 473-474; print p. 309; PDF physical p. 38",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书末索引；Markdown行1407-1408；该索引子目指向印刷页309",
            "sentence_summary": (
                "索引在Gallacini, Teofilo名下列出Trattato sopragli errori degli architetti，"
                "并指向p.309；此子目与第10章p.309正文书名对应。"
            ),
            "original_quotes": [{"source_span": "line 1408", "text": INDEX_QUOTE}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{INDEX_FILE}",
                "source_span": "lines 1407-1408; index locator p. 309",
            },
        },
    ]
    frontmatter = {
        "title": f"{title_zh}（{title_en}）",
        "name_en": title_en,
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    header = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** 本卡登记哈斯克尔第10章所述的1767年刊本，题名为 *Trattato sopra gli errori degli architetti*。哈斯克尔称该书依据Smith收藏的一份Teofilo Gallacini手稿刊行；第10章正文与书末索引的同题子目均指向印刷页309。S2依据该页图将正文OCR的连写“sopragli”读作“sopra gli”，索引转录保留连写形式。这里的手稿是刊本来源说明，原文没有给出可独立识别的手稿馆藏号或存世本，本卡只登记1767年刊本。原刊未独立查阅。{f'[第10章 p.309]({body_path})（L473–474）'} {f'[书末索引]({index_path})（L1407–1408）'}

**English:** This card records the 1767 publication described in Haskell’s Chapter 10 under the title *Trattato sopra gli errori degli architetti*. Haskell says Smith published it from a manuscript in his collection by Teofilo Gallacini; the Chapter 10 passage and the book index entry both point to printed p. 309. S2 read the page image as “sopra gli,” while the index transcription retains the joined OCR form “sopragli.” The manuscript is described as the publication’s source; Haskell gives no separately identifiable manuscript holding or surviving copy, so this card covers only the 1767 publication. The printed work was not independently consulted. {f'[Chapter 10, p. 309]({body_path}) (L473–474)'} {f'[book index]({index_path}) (L1407–1408)'}

### 文献身份

| 字段 | 内容 | 证据 |
|---|---|---|
| 原题名 | *Trattato sopra gli errori degli architetti*；索引OCR连写为“sopragli”，S2页图读法分开为“sopra gli” | [第10章 p.309]({body_path})（L473）；[书末索引]({index_path})（L1408） |
| 作者 | Haskell称其为17世纪理论家Teofilo Gallacini的手稿；此卡只记录书内作者归属 | [第10章 p.309]({body_path})（L473） |
| 刊行年份 | 1767；出版地、印刷者、版本项及馆藏号未载 | [第10章 p.309]({body_path})（L473） |

### 身份边界

S3组 `{GROUP}` 合并索引候选 `cand-1110` 与正文候选 `cand-9257`：索引子目完整书名并指向正文所在的p.309，正文给出同一书名及1767年刊行叙述。`cand-9258` 所记Visentini对该书的更新保持独立身份组；Haskell未给出其精确版本或刊行细节。本卡不把未单独定位的手稿另建为archive，也不把更新版并入1767年刊本。

## 关系与证据

当前没有登记正式关系。作者、刊行与更新相关的S2关系候选留待S6逐条审查；本卡只登记书目身份，来源字段不等于正式关系。
"""
    return f"---\n{header}---\n\n{body}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reconcile Gallacini's index/body identity group and register the 1767 publication in S4."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not (ROOT / "04-knowledge" / "accepted.yml").exists():
        raise SystemExit("Run this script from the project root.")
    alignment_fields, alignment_rows, alignment_bom = read_csv(ALIGNMENT)
    manifest_fields, manifest_rows, manifest_bom = read_csv(MANIFEST)
    _, candidates, _ = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignments = {
        row["candidate_id"]: row
        for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
    }
    if not set(MEMBERS + (SEPARATE_CANDIDATE,)) <= set(candidate_by_id):
        raise SystemExit("A required S3 candidate is missing.")
    for cid in MEMBERS:
        row = alignments[cid]
        if candidate_by_id[cid].get("suggested_type") != "archive":
            raise SystemExit(f"Unexpected type for {cid}.")
        if row.get("decision") != "new" or row.get("ku_id"):
            raise SystemExit(f"{cid} is no longer an unmapped new archive candidate.")
        if group_of(row.get("resolution_note", "")) != OLD_GROUPS[cid]:
            raise SystemExit(f"Unexpected original group for {cid}.")
    separate = alignments[SEPARATE_CANDIDATE]
    if separate.get("decision") != "new" or separate.get("ku_id") or group_of(separate.get("resolution_note", "")) != SEPARATE_GROUP:
        raise SystemExit("The Visentini update candidate changed; review the identity boundary before proceeding.")
    if len(manifest_rows) != 1315 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
        raise SystemExit("Unexpected KU manifest baseline or target already registered.")
    card_path = ROOT / CARD_REL
    if card_path.exists():
        raise SystemExit(f"S4 card already exists: {CARD_REL}")

    body = collapse((ROOT / "02-sources" / "02-Markdown" / BODY_FILE).read_text(encoding="utf-8-sig"))
    index = collapse((ROOT / "02-sources" / "02-Markdown" / INDEX_FILE).read_text(encoding="utf-8-sig"))
    if BODY_QUOTE not in body:
        raise SystemExit("Chapter 10 source quote mismatch.")
    if INDEX_QUOTE not in index:
        raise SystemExit("Index source quote mismatch.")

    planned_alignment = [dict(row) for row in alignment_rows]
    planned_by_id = {
        row["candidate_id"]: row
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    identity_note = (
        "S3 cross-anchor comparison: the index subentry names the same Trattato title and points to p.309, "
        "where the body identifies the 1767 publication; the manuscript is provenance, not a separately "
        "identified archive object. Keep distinct from cand-9258, Haskell's Visentini-updated version."
    )
    for cid in MEMBERS:
        row = planned_by_id[cid]
        old_note = row.get("resolution_note", "")
        old_note = re.sub(r"group=[^;|\s]+", f"group={GROUP}", old_note, count=1)
        row["resolution_note"] = f"{old_note.rstrip()} {identity_note}"
        row["ku_id"] = KU_ID
        row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest_rows)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": "《建筑师错误论》1767年刊本",
        "name_en": "Trattato sopra gli errori degli architetti (1767 publication)",
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    planned_manifest.sort(key=lambda row: row["ku_id"])

    accepted_text = ACCEPTED.read_text(encoding="utf-8-sig")
    accepted_lines = accepted_text.splitlines()
    if any(line.strip() == f"- {CARD_REL}" for line in accepted_lines):
        raise SystemExit("Accepted path already exists.")
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    result_text = RESULT.read_text(encoding="utf-8-sig")
    result_text = replace_once(result_text, "new=5,021（4,840个身份组）", "new=5,021（4,839个身份组）")
    result_text = replace_once(result_text,
        "S4 已登记296组、映射381条成员候选；尚待登记4,544组、4,640条映射。",
        "S4 已登记297组、映射383条成员候选；尚待登记4,542组、4,638条映射。")
    result_text = replace_once(result_text, "1,315 KU；新组登记与待登记分类型统计见下表",
                               "1,316 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(result_text,
        "| [既有字段表](../tables/enrichment.jsonl) | 10,220条，其中1,571条 unverified |",
        "| [既有字段表](../tables/enrichment.jsonl) | 10,295条，其中1,573条 unverified |")
    result_text = replace_once(result_text,
        "| new | 5,021 | 按 4,840 个当前身份组进入 S4；每组登记一个 KU |",
        "| new | 5,021 | 按 4,839 个当前身份组进入 S4；每组登记一个 KU |")
    result_text = replace_once(result_text,
        "| archive | 79→61 | 1,258／1,221 | 36／1,185；1,206 | 0 | 18 | 745 |",
        "| archive | 79→61 | 1,258／1,220 | 37／1,183；1,204 | 0 | 18 | 745 |")
    result_text = replace_once(result_text,
        "| **合计** | **1,774→1,026** | **5,021／4,840** | **281／4,559；4,669** | **8** | **100** | **5,501** |",
        "| **合计** | **1,774→1,026** | **5,021／4,839** | **297／4,542；4,638** | **8** | **100** | **5,501** |")
    detail = (
        "### S3 分组校正与 S4 archive 登记：Gallacini《Trattato》1767年刊本（2026-10-16）\n\n"
        "- `cand-1110` 的索引子目（G.csv#17，索引转录L1407–1408）完整列出 *Trattato sopragli errori degli architetti* 并指向p.309；`cand-9257` 的第10章正文候选记录同页所述1767年刊本。原先两个 `new` 组据同题名和同页指向合并为 `archive-group-gallacini-trattato-1767`，二者映射到 `units/archives/trattato-sopra-gli-errori-degli-architetti-1767`。S2依据页图把正文标题读作“sopra gli”；索引OCR连写保留为来源差异。\n"
        "- 对象范围限于1767年刊本；书内所称手稿只作为刊本来源，不另建未获馆藏号或存世定位的手稿对象。`cand-9258` 所述Visentini更新版保持独立组，精确版本信息仍未载。原刊未独立查阅；作者、刊行与更新关系留待S6，本次未新增正式关系。\n"
        "- 新增1张archive卡、1条manifest映射、2条候选KU映射和1条accepted路径。S3 new候选数不变，身份组由4,840减至4,839；S4累计登记297组/383条映射，待登记4,542组/4,638条映射；archive为37组已登记、1,183组/1,204条成员待登记；KU总数1,316。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", detail + "## 未解决项与交接限制")

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    if "### S3 分组校正与 S4 archive 登记：Gallacini《Trattato》1767年刊本" in process_text:
        raise SystemExit("Gallacini S3/S4 process record already exists.")
    process_text += (
        "\n\n### S3 分组校正与 S4 archive 登记：Gallacini《Trattato》1767年刊本（2026-10-16）\n\n"
        "- 对比 `cand-1110`（G.csv#17；索引子目“Trattato sopragli errori degli architetti, 309”）与 `cand-9257`（第10章p.309正文候选）。索引子目指向正文所在页，正文按S2页图读法记载Smith于1767年刊行Gallacini手稿并给出同一题名；这是同一书目身份的索引／正文双锚点。将两行从原组 `archive-group-db9bd962571d`、`archive-group-8924556dfa3f` 统一到 `archive-group-gallacini-trattato-1767`，保留 `decision=new`。原稿作为出版来源，不作为未识别的独立手稿KU。\n"
        "- `cand-9258` 的Visentini更新版保留 `archive-group-13318baef7cf`，不与1767年刊本合并；来源未给出更新版精确题名、出版项。\n"
        "- S4新增 `units/archives/trattato-sopra-gli-errori-degli-architetti-1767`，记录原题、书内作者归属及1767刊行叙述，并分别保留正文与索引证据。未独立查阅原刊；不新增正式关系。\n"
        "- 新增1张archive卡、manifest 1条、alignment 2条KU映射、accepted 1条路径。S3 new身份组净减1，候选决议数不变；S4累计297组/383条映射，待登记4,542组/4,638条映射；archive为37组已登记、1,183组/1,204条成员待登记；KU总数1,316。字段表经 `build_field_facts.py` 预检及apply写回。\n"
    )

    card_text = make_card()
    frontmatter = yaml.safe_load(card_text.split("---\n", 2)[1])
    if frontmatter.get("type") != "archive" or len(frontmatter.get("sources", [])) != 2:
        raise SystemExit("Generated card frontmatter failed validation.")

    updates = {
        ALIGNMENT: encode_csv(alignment_fields, planned_alignment, alignment_bom),
        MANIFEST: encode_csv(manifest_fields, planned_manifest, manifest_bom),
        ACCEPTED: encode_text(ACCEPTED, planned_accepted),
        PROCESS: encode_text(PROCESS, process_text),
        RESULT: encode_text(RESULT, result_text),
        card_path: card_text.encode("utf-8-sig"),
    }
    print("DRY-RUN" if args.dry_run else "APPLY")
    for path, content in updates.items():
        old_hash = digest(path.read_bytes()) if path.exists() else "absent"
        print(f"  {path.relative_to(ROOT)}: {old_hash} -> {digest(content)}")
    print(f"  S3 group merge: {OLD_GROUPS[MEMBERS[0]]} + {OLD_GROUPS[MEMBERS[1]]} -> {GROUP}")
    print("  S4 group=1; candidates=2; card title=Trattato sopra gli errori degli architetti (1767 publication)")
    print("  S3 new groups=4,840 -> 4,839; candidate decisions unchanged")
    print("  S4=296/381 -> 297/383; pending=4,542/4,638; KU=1,316")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, PROCESS, RESULT]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A Gallacini S3/S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3s4-gallacini-trattato-1767-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied Gallacini S3 identity-group correction and S4 registration.")


if __name__ == "__main__":
    main()
