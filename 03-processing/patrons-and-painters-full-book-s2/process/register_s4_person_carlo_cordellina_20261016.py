from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import shutil
import sys
from io import StringIO
from pathlib import Path

import yaml

PROCESS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

GROUP = "new-person:carlo-cordellina-80fe525d81"
CANDIDATE_ID = "cand-0842"
ALIGNMENT_ID = "aln-1177"
KU_ID = "units/persons/carlo-cordellina"
CARD_REL = "04-knowledge/units/persons/carlo-cordellina.md"
CARD_PATH = ROOT / CARD_REL
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-carlo-cordellina-20261016"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv_text(fieldnames, rows) -> str:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    if any(line.strip() == f"- {CARD_REL}" for line in lines):
        raise ValueError("Accepted path already exists.")
    insert_at = next(
        (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "全书索引 C.csv#372；列第9章p.256及第二版后记p.405",
            "sentence_summary": "索引主项为Cordellina, Carlo，两个页码锚点均由正文全名对应。",
            "original_quotes": [{"source_span": "C.csv#372", "text": "Cordellina, Carlo"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/C.csv",
                "source_span": "C.csv#372",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第9章 p.256；OCR L158–161",
            "sentence_summary": "Haskell称Cordellina为当时重要的法律倡辩者，并叙述其住所与Tiepolo装饰活动；本卡不据此裁定两所住宅的具体建筑身份。",
            "original_quotes": [
                {
                    "source_span": "lines 158–160; print p. 256",
                    "text": "Carlo Cordellina, the leading advocate of the day. He was a man, we are told,4 who did not\nEke useless luxury, such as loading his wife with precious stones, but who beHeved in splendid living. And so he built himself two houses, one in his native Vicenza and one in the country at Montecchio.",
                },
                {
                    "source_span": "lines 160–161; print p. 256",
                    "text": "To decorate the latter he summoned Tiepolo, who was much irritated by the extensive entertainment for which Cordellina was renowned,5 but who frescoed The Continence of Scipio and the Family of Darius before Alexander the Great on the walls—clear allusions to the magnanimity of his patron—and the Triumph of the Arts on the ceiling.",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "source_span": "lines 158–161; print p. 256",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第二版后记 p.405；OCR L143–144",
            "sentence_summary": "Haskell报告Puppi关于Cordellina赞助的新材料，并称他于1770年、73岁时开始建造Vicenza宫殿，十八年后卒于该处；Puppi文章未独立查阅。",
            "original_quotes": [
                {
                    "source_span": "lines 143–144; print p. 405",
                    "text": "Puppi has also given us new information about the patronage of Carlo Cordellina (another employer of Tiepolo), and especially about the palace in\nVicenza which he began to have built in 1770 at the age of 73 and where he died eighteen years later.",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "source_span": "lines 143–144; print p. 405",
            },
        },
    ]
    frontmatter = {
        "title": "卡洛·科尔代利纳（Carlo Cordellina）",
        "name_en": "Carlo Cordellina",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    idx = "[全书索引 C.csv#372](../../../02-sources/03-Index/03-2-Index-CSV/C.csv)"
    ch9 = "[第9章 p.256](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L158–161）"
    postscript = "[第二版后记 p.405](../../../02-sources/02-Markdown/20_CHP-20Postscript.md)（L143–144）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应索引中的 Carlo Cordellina。第9章称其为当时的重要法律倡辩者；第二版后记再次以全名介绍其艺术赞助语境和Vicenza宫殿。中文展示名为项目工作音译。{idx} {ch9} {postscript}

**English:** This unit corresponds to Carlo Cordellina in the index. Chapter 9 describes him as a leading legal advocate of his day; the second-edition postscript again names him in its account of artistic patronage and a palace in Vicenza. The Chinese display name is a project working transliteration. {idx} {ch9} {postscript}

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Carlo Cordellina | S2，第9章 p.256 |
| 索引形式 | Cordellina, Carlo | S1，C.csv#372 |
| 身份 | 法律倡辩者（advocate） | S2，第9章 p.256 |

### 本书相关语境

第9章叙述Cordellina在Vicenza与Montecchio的住宅、Tiepolo受邀装饰乡间住宅及其作品；后记称其在1770年开始建造Vicenza宫殿并于十八年后卒于该处。第9章所述Vicenza住宅与后记所述宫殿是否同一建筑，S2候选`cand-8375`仍未裁定；Haskell引述的Puppi文章和Tiepolo书信未独立查阅。关系端点及具体建筑身份不由本人物卡合并。{ch9} {postscript}

Chapter 9 describes Cordellina’s residences in Vicenza and Montecchio, Tiepolo’s invitation to decorate the country residence, and the resulting works. The postscript says he began building a palace in Vicenza in 1770 and died there eighteen years later. Whether the Vicenza house in Chapter 9 and the palace in the postscript are the same building remains unresolved in candidate `cand-8375`; Puppi’s article and Tiepolo’s cited letter were not independently consulted. This person card does not merge the relationship endpoints or resolve the building’s identity. {ch9} {postscript}

## 关系与证据

### 身份与外部链接

本卡仅登记书内身份依据；当前没有外部身份链接。

This unit records identity evidence from the book; no external identity link is currently recorded.

### 关系记录

当前没有正式关系记录。书内直接关系候选保留在断言账本中，尚未转为正式关系。

No formal relations are recorded. Direct relation candidates from the book remain in the statement ledger and have not been converted into formal relations.
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Carlo Cordellina identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment = read_csv(ALIGNMENT)
    manifest_fields, manifest = read_csv(MANIFEST)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row.get("candidate_id") == CANDIDATE_ID)
    assert candidate.get("suggested_type") == "person"
    group_rows = [
        row for row in alignment
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and f"group={GROUP}" in row.get("resolution_note", "")
    ]
    assert len(group_rows) == 1 and group_rows[0].get("candidate_id") == CANDIDATE_ID
    primary = group_rows[0]
    assert primary.get("alignment_id") == ALIGNMENT_ID and not primary.get("ku_id")
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not any(
        row.get("type") == "person" and row.get("name_en", "").casefold() == "carlo cordellina"
        for row in manifest
    )
    assert not CARD_PATH.exists()
    assert not any(line.strip() == f"- {CARD_REL}" for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines())

    index_bytes = (ROOT / "02-sources/03-Index/03-2-Index-CSV/C.csv").read_bytes()
    ch9 = (ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md").read_text(encoding="utf-8-sig")
    postscript = (ROOT / "02-sources/02-Markdown/20_CHP-20Postscript.md").read_text(encoding="utf-8-sig")
    assert b"Cordellina, Carlo" in index_bytes
    assert "Carlo\nCordellina, the leading advocate of the day" in ch9
    assert "he built himself two houses" in ch9 and "To decorate the latter he summoned Tiepolo" in ch9
    assert "palace in\nVicenza which he began to have built in 1770" in postscript

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct_statements = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE_ID or row.get("object_candidate_id") == CANDIDATE_ID
    ]
    relation_candidates = [
        row for row in direct_statements
        if row.get("qualifiers", {}).get("relation_candidate")
    ]
    non_relation_statements = [row for row in direct_statements if not row.get("qualifiers", {}).get("relation_candidate")]
    assert len(direct_statements) == 8 and len(relation_candidates) == 7 and len(non_relation_statements) == 1

    planned_alignment = [dict(row) for row in alignment]
    mapped = next(row for row in planned_alignment if row.get("alignment_id") == ALIGNMENT_ID)
    mapped["ku_id"] = KU_ID
    mapped["resolution_note"] += f" S4 registration ({DATE}): mapped this new-person group to {KU_ID}."
    planned_manifest = [dict(row) for row in manifest] + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "卡洛·科尔代利纳",
        "name_en": "Carlo Cordellina",
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    planned_manifest.sort(key=lambda row: row["ku_id"])
    accepted_text = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))
    card_text = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card_text, re.DOTALL)
    assert frontmatter_match
    card_frontmatter = yaml.safe_load(frontmatter_match.group(1))
    assert card_frontmatter["type"] == "person" and len(card_frontmatter["sources"]) == 3

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_insert = (
        f"### S4 person：Carlo Cordellina 跨章人物组登记（{DATE}）\n\n"
        f"- `cand-0842`（C.csv#372，pp.256、405）保持S3组 `{GROUP}`，现映射至 `{KU_ID}`。索引全名与第9章、第20章后记同名锚点对应；既有manifest无同名人物KU。新卡只登记书内法律倡辩者身份，不补外部生平。\n"
        f"- 8条直接S2陈述中7条为关系候选，1条为非关系性格描述。Vicenza住宅与后记所称宫殿的同一性候选`cand-8375`保持未决；Tiepolo委托、作品及其他端点关系留待S6。本轮不修改`relations.csv`。\n"
        f"- `build_field_facts.py` 预检无警告并apply新增3条source-backed字段记录、来源数不变；unverified数量保持1,578。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。\n\n"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, result_insert + marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = f"### S4 person：Carlo Cordellina 跨章人物组登记（{DATE}）"
    assert process_heading not in process_text
    process_text += (
        f"\n\n{process_heading}\n\n"
        f"- `cand-0842`（C.csv#372）保持S3组 `{GROUP}`，登记为 `{KU_ID}`。索引列p.256和p.405，第9章与第二版后记均以Carlo Cordellina全名锚定；无既有人物KU命中，未访问外部身份源。\n"
        "- 卡片仅登记姓名、索引形式和第9章明确称为leading advocate的法律身份。第9章两处住所、Tiepolo装饰和作品叙述，以及后记记载的1770年Vicenza宫殿开建和其后去世信息均保留来源归属。Haskell引用的Puppi文章、Tiepolo信件未独立查阅。\n"
        "- S2为Vicenza房屋及p.405宫殿保留的对象候选`cand-8375`仍未裁定两处是否同一建筑；本轮不合并端点或创建关系。8条直接S2 statements中7条为relation_candidate、1条为非关系生活方式描述；7条关系候选待S6。\n"
        f"- `build_field_facts.py` 预检无警告并apply新增3条source-backed字段记录，来源数不变、unverified保持1,578。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；manifest={len(planned_manifest)}。\n"
    )

    outputs = {
        ALIGNMENT: write_csv_text(alignment_fields, planned_alignment),
        MANIFEST: write_csv_text(manifest_fields, planned_manifest),
        ACCEPTED: accepted_text,
        CARD_PATH: card_text,
        PROCESS: process_text,
        RESULT: result_text,
    }
    for path in outputs:
        assert not path.with_name(path.name + BACKUP_SUFFIX).exists()

    if args.dry_run:
        for path, updated in outputs.items():
            current = path.read_text(encoding="utf-8-sig") if path.exists() else ""
            diff = difflib.unified_diff(
                current.splitlines(keepends=True), updated.splitlines(keepends=True),
                fromfile=str(path.relative_to(ROOT)), tofile=str(path.relative_to(ROOT)) + " (updated)", n=2,
            )
            print("".join(diff), end="")
        print(
            f"dry-run passed: {CANDIDATE_ID}->{GROUP}->{KU_ID}; registered="
            f"{totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
            f"direct_statements={len(direct_statements)}; relation_candidates={len(relation_candidates)}"
        )
        return 0

    backups = []
    try:
        for path in outputs:
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if path.exists():
                shutil.copy2(path, backup)
            else:
                backup.write_text("NEW FILE: created by S4 Carlo Cordellina registration\n", encoding="utf-8")
            backups.append((path, backup))
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8", newline="\n")
    except Exception:
        for path, backup in backups:
            if backup.read_text(encoding="utf-8-sig").startswith("NEW FILE:"):
                if path.exists():
                    path.unlink()
            else:
                shutil.copy2(backup, path)
        raise

    print(
        f"applied: {CANDIDATE_ID}->{GROUP}->{KU_ID}; registered={totals['registered_groups']}/"
        f"{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}; direct_statements={len(direct_statements)}; "
        f"relation_candidates={len(relation_candidates)}; backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
