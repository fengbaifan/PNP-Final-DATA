from __future__ import annotations

import argparse
import csv
import difflib
import json
import shutil
import sys
from io import StringIO
from pathlib import Path

PROCESS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
GROUP = "new-person:modena-of-6566b00ada"
CANDIDATE_ID = "cand-1675"
ALIGNMENT_ID = "aln-2010"
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s3-modena-duke-undecided-20261016"


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Reclassify the title-only Duke of Modena candidate as S3 undecided.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment = read_csv(ALIGNMENT)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row.get("candidate_id") == CANDIDATE_ID)
    assert candidate.get("suggested_type") == "person"
    target = next(row for row in alignment if row.get("alignment_id") == ALIGNMENT_ID)
    assert target.get("candidate_id") == CANDIDATE_ID
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert f"group={GROUP}" in target.get("resolution_note", "")

    index_text = (ROOT / "02-sources/03-Index/03-2-Index-CSV/M.csv").read_text(encoding="utf-8-sig")
    ch5 = (ROOT / "02-sources/02-Markdown/05_CHP-5_sec_iv.md").read_text(encoding="utf-8-sig")
    ch7 = (ROOT / "02-sources/02-Markdown/07_CHP-7_sec_i.md").read_text(encoding="utf-8-sig")
    assert '"Modena, Duke of"' in index_text and '"143, 177n"' in index_text
    assert "Duke of Modena who wrote to his agent in Rome" in ch5
    assert "in 1645 Gabriele Balestrieri wrote to the Duke of Modena" in ch7

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE_ID or row.get("object_candidate_id") == CANDIDATE_ID
    ]
    direct_relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate") is True]
    letter_statement = next(row for row in direct if row.get("statement_id") == "st-chp7-p177-n4-letter-addressed-to")
    assert len(direct) == 10 and len(direct_relations) == 9
    assert letter_statement.get("object_candidate_id") == CANDIDATE_ID

    planned_alignment = [dict(row) for row in alignment]
    target_new = next(row for row in planned_alignment if row.get("alignment_id") == ALIGNMENT_ID)
    old_note = target_new["resolution_note"]
    updated_note = old_note.replace(
        f"group={GROUP}", f"former_identity_cluster={GROUP}", 1
    )
    updated_note += (
        f" S3 review ({DATE}): decision revised from new to undecided; the former identity cluster is withdrawn. "
        "Both referenced passages use only the office title 'Duke of Modena'. The p.177 note reports a 1645 letter, "
        "while the request at p.143 is undated in a section spanning Rosa's career; neither source passage gives a personal name. "
        "The index entry locates both passages but cannot by itself establish that the title-only references denote one individual. "
        "The prior rationale incorrectly claimed a full personal-name anchor. Keep unresolved; do not create a KU until dated or "
        "independent identity evidence ties or distinguishes the references."
    )
    target_new["decision"] = "undecided"
    target_new["ku_id"] = ""
    target_new["resolution_note"] = updated_note

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"),
        stats,
        totals,
        len(read_csv(ROOT / "04-knowledge" / "tables" / "ku-manifest.csv")[1]),
    )
    result_section = (
        f"### S3 复核：Modena 公爵候选改列待证（{DATE}）\n\n"
        f"- `cand-1675`（M.csv#217）原列为 `{GROUP}`／`new`，现改为 `undecided`，不登记KU；原组号与理由保留在alignment行中并标明已撤回。\n"
        "- 索引将 p.143 与 p.177 注4列在同一“Duke of Modena”条目下，但这只是定位。p.143正文只称公爵，未给出所述画作请求的日期；p.177注4转述一封1645年书信，也只称公爵。没有全名锚点或已读的原始书信证明两处是同一人。原S3备注声称存在full personal-name anchor，与源文不符，现已更正。\n"
        "- 保留9条关系候选及1条评价性非关系陈述；未将可能的不同公爵合并，也不拆分成缺少姓名依据的新候选。待核查能为p.143请求定年的原始记录或其他直接身份依据后再决定复用、新建或拆分。\n\n"
    )
    marker = "## S3 身份决定与交接\n\n"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, marker + result_section, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    heading = f"### S3 复核：Modena 公爵候选改列待证（{DATE}）"
    assert heading not in process_text
    process_text += (
        f"\n\n{heading}\n\n"
        f"- 复核 `cand-1675`／`aln-2010`。原决定为`new`，组 `{GROUP}`；现改为`undecided`，撤回该身份组，不登记KU。旧对齐理由原样保留在resolution_note并标注为前次裁决。\n"
        "- S1索引 M.csv#217 把p.143与p.177注4列在同一标题“Modena, Duke of”下，但索引仅供定位。S2 p.143写Duke of Modena向罗马代理人索求画作，未给请求日期；S2 p.177注4转述Gabriele Balestrieri于1645年写给Duke of Modena的信，原信与Lumbroso/Venturi记录未在本次独立查阅。两处都没有公爵全名。" 
        "p.143所在论述包含Rosa自1637年至1667年间的多项事件，但此句没有可据以锁定任期的日期。不能仅凭同一标题或索引页码证明是同一公爵；也没有足够证据将此单一索引候选拆成两个已识别人物。\n"
        "- 原resolution_note的“source anchor gives a full personal name”及“full-name/explicit-alias anchor (modena of)”不受原文支持，现明确视为被撤回的旧理由。依verify规则，头衔不足以合并人物；保持`undecided`，直到有可核的年代/身份记录能够连接或区分两处。\n"
        f"- 候选直接关联10条S2 statement，其中9条relation_candidate、1条评价性非关系陈述；保持原分类。更新后S3为same={sync.fmt(totals['same_candidates'])}、new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组、conflict={sync.fmt(totals['conflict'])}、excluded={sync.fmt(totals['excluded'])}、undecided={sync.fmt(totals['undecided'])}。S4 KU清单和关系表均不因本次修订改变。\n"
    )

    outputs = {
        ALIGNMENT: write_csv_text(alignment_fields, planned_alignment),
        PROCESS: process_text,
        RESULT: result_text,
    }
    for path in outputs:
        assert not path.with_name(path.name + BACKUP_SUFFIX).exists()

    if args.dry_run:
        for path, updated in outputs.items():
            current = path.read_text(encoding="utf-8-sig")
            diff = difflib.unified_diff(
                current.splitlines(keepends=True), updated.splitlines(keepends=True),
                fromfile=str(path.relative_to(ROOT)), tofile=str(path.relative_to(ROOT)) + " (updated)", n=2,
            )
            print("".join(diff), end="")
        print(
            f"dry-run passed: {CANDIDATE_ID} {target.get('decision')}->{target_new['decision']}; "
            f"S3 new={totals['new_candidates']}/{totals['new_groups']} groups; "
            f"undecided={totals['undecided']}; S4 pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"direct_statements={len(direct)}; relation_candidates={len(direct_relations)}"
        )
        return 0

    backups = []
    try:
        for path in outputs:
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            shutil.copy2(path, backup)
            backups.append((path, backup))
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8", newline="\n")
    except Exception:
        for path, backup in backups:
            shutil.copy2(backup, path)
        raise

    print(
        f"applied: {CANDIDATE_ID} new->{target_new['decision']}; "
        f"S3 new={totals['new_candidates']}/{totals['new_groups']} groups; "
        f"undecided={totals['undecided']}; S4 pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
