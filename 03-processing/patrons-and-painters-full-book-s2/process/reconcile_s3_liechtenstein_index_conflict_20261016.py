from __future__ import annotations

import argparse
import csv
import difflib
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ALIGNMENT = ROOT / "04-knowledge/tables/alignment.csv"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
RESULT = ROOT / "04-knowledge/results/patrons-and-painters-full-book-s2.md"
BACKUP_SUFFIX = ".bak-s3-liechtenstein-index-conflict-20261016"

NEW_NOTE = (
    "source_ref=entity-candidates.csv#cand-1405;index_entry=L.csv#62;"
    "original_group_label=new-person:liechtenstein-of-wenzel-d8f638b83e;"
    "s2_mentions=m-chp7-p169-i-035,m-chp7-p169-i-039,m-chp7-p194-b060,"
    "m-chp7-p195-b001,m-s2-chp7-surface-7b3a3c0d5cdef50f;"
    "prior_decision=new (2026-10-15; prior note incorrectly stated that the body gives a full personal name);"
    "conflict=the p.169 Crespi invitation and pp.194-195 Franceschini correspondence are mapped by the index to Prince Wenzel, "
    "but the p.195 body dates the latter letter to 1691 and names no forename; official Liechtenstein Collections identifies "
    "Joseph Wenzel I as 1696-1772 (https://www.liechtensteincollections.at/en/princes/prince-joseph-wenzel-i-von-liechtenstein), "
    "so he cannot be the 1691 correspondent. The official collection's 6 Dec 1692 letter FA 67.2 identifies its sender as "
    "Johann Adam Andreas I and recipient as Marcantonio Franceschini "
    "(https://www.liechtensteincollections.at/en/collections-online/prince-johann-adam-andreas-i-von-liechtenstein-to-marcantonio-franceschini-he-sends-once-again-the-precise-measurements-for-the-paintings-he-has-o); "
    "Treccani states that the Liechtenstein prince Adamo Giovanni's relationship with Franceschini began in 1691 "
    "(https://www.treccani.it/enciclopedia/marcantonio-franceschini_(Dizionario-Biografico)/). These support Johann Adam Andreas I "
    "as the likely referent of the 1691 passage, not Wenzel; the p.169 invitation is temporally compatible with Johann Adam's palace activity "
    "but remains a separate title-only referent for review. "
    "The index row also has a page-range discrepancy: Markdown index lists 169, 194-5, 341, 345 while L.csv lists 169, 194, 195, 234n, 345. "
    "Do not register a new Wenzel KU or map this mixed index candidate wholesale to an existing KU. Keep conflict pending candidate/mention disaggregation; "
    "review p.169 and pp.194-195 against existing KU units/persons/giovanni-adamo-piola, and keep title-only p.343 / p.341-note candidates "
    "cand-10094 and cand-10202 separate and undecided. The 16 linked S2 relation candidates remain pending S6."
)

PROCESS_ENTRY = """
### S3 冲突复核：Liechtenstein Prince Wenzel 索引组的年代错配（2026-10-16）

- cand-1405 原决定为 `new`，原组标签 `new-person:liechtenstein-of-wenzel-d8f638b83e` 保留。复核发现前次 resolution_note 所称“source anchor gives a full personal name”不实：第7章 p.169 L8 只称 “the Prince of Liechtenstein”；第7章 p.194 L35 及 p.195 L39 也只用头衔，p.195 明确将所引书信定为1691年。原书索引 Markdown 将 Wenzel 关联至 pp.169、194–195、341、345；S1 `L.csv#62` 则将同一条目列为 pp.169、194、195、234n、345，页码范围本身存在不一致。
- 外部身份核对：Liechtenstein Princely Collections 的 Joseph Wenzel I 人物页给出生卒1696–1772，故其不可能是1691年书信作者；官方馆藏记录 FA 67.2 为 Johann Adam Andreas I 于1692-12-06 致 Marcantonio Franceschini 的信；Treccani《意大利人传记辞典》称 Prince Adamo Giovanni 与 Franceschini 的关系始于1691年。合并的姓名变体、年代与书信对象都指向既有 `units/persons/giovanni-adamo-piola`，但索引条目还覆盖较晚页码，故不能把整个 cand-1405 组简单改映为 Johann Adam，也不能按索引直接建立 Wenzel 新卡。
- 将 cand-1405 从 `new` 改为 `conflict`，清楚保留冲突两侧与 S3 后续去向：拆分并复核 p.169、pp.194–195 的正文指代是否可映射到既有 Johann Adam KU；索引所称 Wenzel 的较晚页码须另与源文候选核对。第13章只称 Prince 的木刻赠送 cand-10094 与 Zanetti 往来信件候选 cand-10202 继续各自 `undecided`，不因同一姓氏／头衔合并。16条关联 S2 关系候选仍待身份端点拆分及后续 S6；没有建立新 KU 或正式关系。
- 本次核验来源与访问日期：Liechtenstein Princely Collections，Joseph Wenzel I 人物页，https://www.liechtensteincollections.at/en/princes/prince-joseph-wenzel-i-von-liechtenstein；馆藏信件 FA 67.2，https://www.liechtensteincollections.at/en/collections-online/prince-johann-adam-andreas-i-von-liechtenstein-to-marcantonio-franceschini-he-sends-once-again-the-precise-measurements-for-the-paintings-he-has-o；Treccani，Marcantonio Franceschini，https://www.treccani.it/enciclopedia/marcantonio-franceschini_(Dizionario-Biografico)/；均访问于2026-10-16。

S3 same=1,764/1,025; new=5,005/4,833; conflict=8; undecided=5,528. S4 registered=276/346; pending=4,557/4,659.
"""


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def dump_csv(headers: list[str], rows: list[dict[str, str]]) -> str:
    from io import StringIO

    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one occurrence, found {count}: {old[:100]!r}")
    return text.replace(old, new, 1)


def build_changes() -> dict[Path, str]:
    headers, rows = load_csv(ALIGNMENT)
    target = [row for row in rows if row.get("candidate_id") == "cand-1405"]
    if len(target) != 1:
        raise SystemExit(f"Expected one cand-1405 alignment row, found {len(target)}")
    row = target[0]
    if row.get("decision") != "new" or row.get("ku_id"):
        raise SystemExit(f"Unexpected cand-1405 pre-state: decision={row.get('decision')!r}, ku_id={row.get('ku_id')!r}")
    if "new-person:liechtenstein-of-wenzel-d8f638b83e" not in row.get("resolution_note", ""):
        raise SystemExit("Expected prior Wenzel identity group label was not found")
    row["decision"] = "conflict"
    row["ku_id"] = ""
    row["process_ref"] = "S3-full-book-2026-10-16"
    row["external_source"] = ""
    row["external_id"] = ""
    row["accessed_date"] = ""
    row["resolution_note"] = NEW_NOTE

    result = RESULT.read_text(encoding="utf-8-sig")
    result = replace_once(
        result,
        "same=1,764（指向1,025个既有 KU）、new=5,006（4,834个身份组）、conflict=7、excluded=99、undecided=5,528。S4 已登记276组、映射346条成员候选；尚待登记4,558组、4,660条映射。",
        "same=1,764（指向1,025个既有 KU）、new=5,005（4,833个身份组）、conflict=8、excluded=99、undecided=5,528。S4 已登记276组、映射346条成员候选；尚待登记4,557组、4,659条映射。",
    )
    result = replace_once(result, "| new | 5,006 | 按 4,834 个当前身份组进入 S4；每组登记一个 KU |", "| new | 5,005 | 按 4,833 个当前身份组进入 S4；每组登记一个 KU |")
    result = replace_once(result, "| conflict | 7 | 冲突两侧与来源依据保留在对齐行，等待解决证据 |", "| conflict | 8 | 冲突两侧与来源依据保留在对齐行，等待解决证据 |")
    result = replace_once(
        result,
        "| person | 996→387 | 1,178／1,086 | 83／1,003；1,048 | 2 | 7 | 1,281 |",
        "| person | 996→387 | 1,177／1,085 | 83／1,002；1,047 | 3 | 7 | 1,281 |",
    )
    result = replace_once(
        result,
        "| **合计** | **1,764→1,025** | **5,006／4,834** | **276／4,558；4,660** | **7** | **99** | **5,528** |",
        "| **合计** | **1,764→1,025** | **5,005／4,833** | **276／4,557；4,659** | **8** | **99** | **5,528** |",
    )
    marker = "### S4 按类型登记进度"
    conflict_summary = (
        "本轮新增一项身份冲突：`cand-1405` 的 Wenzel 索引标签与第七章 1691 年书信年代不相容；该信的 Prince 较可能是既有人物 Johann Adam Andreas I，但索引跨页组尚待拆分核实。该候选由 `new` 改为 `conflict`，不生成 Wenzel KU；另两条只具头衔的第十三章候选继续独立待证。16条相关关系候选不进入正式关系。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)。\n\n"
    )
    if result.count(marker) != 1:
        raise SystemExit("Could not locate unique S4 progress section")
    result = result.replace(marker, conflict_summary + marker, 1)

    process = PROCESS.read_text(encoding="utf-8-sig")
    if "### S3 冲突复核：Liechtenstein Prince Wenzel 索引组的年代错配（2026-10-16）" in process:
        raise SystemExit("The S3 conflict review is already present")
    process += PROCESS_ENTRY

    return {ALIGNMENT: dump_csv(headers, rows), RESULT: result, PROCESS: process}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write changes after dry-run review")
    args = parser.parse_args()
    changes = build_changes()

    for path, updated in changes.items():
        current = path.read_text(encoding="utf-8-sig")
        diff = difflib.unified_diff(
            current.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile=str(path.relative_to(ROOT)),
            tofile=str(path.relative_to(ROOT)) + " (updated)",
            n=2,
        )
        print("".join(diff), end="")

    if not args.apply:
        print("DRY-RUN only; pass --apply to write.")
        return

    backups: list[tuple[Path, Path]] = []
    for path in changes:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"Backup already exists: {backup}")
        shutil.copy2(path, backup)
        backups.append((path, backup))
    try:
        for path, updated in changes.items():
            path.write_text(updated, encoding="utf-8-sig", newline="")
    except Exception:
        for path, backup in backups:
            shutil.copy2(backup, path)
        raise
    print("APPLIED; recoverable backups:")
    for _, backup in backups:
        print(backup.relative_to(ROOT))


if __name__ == "__main__":
    main()
