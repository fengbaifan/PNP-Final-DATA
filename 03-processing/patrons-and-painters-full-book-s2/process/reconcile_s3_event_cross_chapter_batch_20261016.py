from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ALIGNMENT = ROOT / "04-knowledge" / "tables" / "alignment.csv"
CANDIDATES = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
PROCESS_REF = "S3-event-cross-chapter-batch-2026-10-16"
MARKER = "### S3 事件类型补充裁决：跨章候选与既有事件组（2026-10-16）"


# Each source-bounded body candidate is a distinct event or recurring event series.
# cand-1821 is the index sub-entry for the same 1655 burial-cost dispute as cand-6297.
CASES = {
    "cand-10532": {
        "group": "sg3-event-cand-10532",
        "source_ref": "chp-15:15_CHP-15_sec_ii:l49-59#L52",
        "rationale": (
            "Chapter 15, p.369, identifies Querini's 1777 journey to Switzerland and visit to Voltaire; "
            "the following sentence names Girolamo Festari as his companion on that trip. "
            "The group covers this journey only; the source does not specify a complete itinerary."
        ),
    },
    "cand-11601": {
        "group": "sg3-event-cand-11601",
        "source_ref": "chp-3:03_CHP-3_sec_iv:l26-33#L31",
        "rationale": (
            "Chapter 3, p.79, dates Jacques Courtois's death to 1676 and says the Gesu tribune affair "
            "then came to a standstill. This is the death event, distinct from Courtois and the unfinished "
            "decoration project; no completion is inferred."
        ),
    },
    "cand-11625": {
        "group": "sg3-event-cand-11625",
        "source_ref": "chp-3:03_CHP-3_sec_iv:l152-163#L160",
        "rationale": (
            "Chapter 3, p.91, identifies Padre Nickel's proposal to redirect the Peru legacy toward a Gesu chapel; "
            "Haskell says the Spaniards did not welcome the idea and the matter was dropped. This is a discrete "
            "reported proposal episode, not a transfer of funds or executed decoration."
        ),
    },
    "cand-11725": {
        "group": "sg3-event-cand-11725",
        "source_ref": "chp-5:05_CHP-5_sec_i:l51-58#L53",
        "rationale": (
            "Chapter 5, p.125, identifies the 1607 Rome display of Caravaggio's Death of the Virgin, "
            "arranged under pressure from Roman painters through the Duke of Mantua's agent. The event is "
            "identifiable despite the source not naming its exact venue or a formal event title."
        ),
    },
    "cand-11728": {
        "group": "sg3-event-cand-11728",
        "source_ref": "chp-5:05_CHP-5_sec_i:l51-58#L56",
        "rationale": (
            "Chapter 5, p.125, describes the Bergamasque community's recurring Rome exhibitions on 24 August "
            "for St Bartholomew, flourishing by 1650 but with no stated start date. This is an event-series "
            "identity, distinct from the separate S. Bartolomeo all'Isola series."
        ),
    },
    "cand-11736": {
        "group": "sg3-event-cand-11736",
        "source_ref": "chp-5:05_CHP-5_sec_i:l51-58#L57",
        "rationale": (
            "Chapter 5, p.125, separately identifies the less important name-day exhibitions arranged at "
            "S. Bartolomeo all'Isola. The different site and organizing description distinguish this series "
            "from the Bergamasque community's exhibitions."
        ),
    },
    "cand-11879": {
        "group": "sg3-event-cand-11879",
        "source_ref": "chp-2:02_CHP-2_sec_ii:l20-28#L23",
        "rationale": (
            "Chapter 2, p.33, names Henri IV's reconciliation in 1593 as a particular historical event. "
            "The note preserves Haskell's characterization of its effect on the Protestant advance without "
            "treating that causal interpretation as independently verified."
        ),
    },
    "cand-11932": {
        "group": "sg3-event-cand-11932",
        "source_ref": "chp-5:05_CHP-5_sec_iii:l82-93#L93",
        "rationale": (
            "Chapter 5, p.138, identifies Urban VIII's death as the event after which French influence ended "
            "and Spanish patrons moved forward. Chapter 6, p.146, independently anchors the same death after "
            "the March 1644 peace; cand-6260 concerns the subsequent conclave and remains a distinct event."
        ),
    },
    "cand-11942": {
        "group": "sg3-event-cand-11942",
        "source_ref": "chp-5:05_CHP-5_sec_iii:l126-165#L143",
        "rationale": (
            "The note to Chapter 5, p.143, dates the S. Salvatore in Lauro exhibition attended by Raggi's "
            "five Cerquozzi paintings to 1701. It is a distinct occurrence from the recurring December series "
            "cand-6051 and the separately identified 1675 and 1697 occurrences; membership in the recurring "
            "series is not asserted."
        ),
    },
    "cand-11955": {
        "group": "sg3-event-cand-11955",
        "source_ref": "chp-6:06_CHP-6_sec_i:l3-11#L4",
        "rationale": (
            "Chapter 6, p.146, names Giambattista Pamfili's election as Innocent X as the change affecting "
            "French interests and the arts. This election is an event, distinct from the pope as a person and "
            "from the conclave after Urban VIII's death (cand-6260)."
        ),
    },
    "cand-1821": {
        "group": "sg3-event-cand-6297",
        "source_ref": "P.csv#20 sub-entry=dispute over burial of, p.150; chp-6:06_CHP-6_sec_i:l48-57#L56",
        "rationale": (
            "The P.csv#20 sub-entry 'dispute over burial of' points to p.150 and the same Innocent X burial-cost "
            "dispute described by body candidate cand-6297 in Chapter 6, p.150. The parent index heading names "
            "the pope, but the sub-entry denotes the event; join cand-1821 to cand-6297's event group, not to the person KU."
        ),
    },
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def group_of(row):
    first = (row.get("resolution_note") or "").split(";", 1)[0]
    return first[len("group="):].strip() if first.startswith("group=") else ""


def read_text_preserving_bom(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return raw.decode("utf-8-sig"), bom


def write_text_preserving_bom(path: Path, text: str, bom: bool):
    data = text.encode("utf-8")
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write S3 event decisions and current result updates.")
    args = parser.parse_args()

    alignment_fields, alignment_rows = read_csv(ALIGNMENT)
    candidate_fields, candidate_rows = read_csv(CANDIDATES)
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    by_id = {
        row["candidate_id"]: row
        for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(CASES) == 11
    assert set(CASES).issubset(by_id) and set(CASES).issubset(candidates)

    own_groups = {candidate_id: case["group"] for candidate_id, case in CASES.items() if candidate_id != "cand-1821"}
    assert len(set(own_groups.values())) == len(own_groups), "New event groups must remain distinct."
    for candidate_id, case in CASES.items():
        candidate = candidates[candidate_id]
        row = by_id[candidate_id]
        assert candidate["suggested_type"] == "event", (candidate_id, candidate["suggested_type"])
        assert row["decision"] == "undecided", (candidate_id, row["decision"])
        assert not row.get("ku_id")
        assert group_of(row), (candidate_id, row.get("resolution_note"))
        if candidate_id != "cand-1821":
            assert group_of(row) == case["group"], (candidate_id, group_of(row), case["group"])

    grouped_rows = {}
    for row in by_id.values():
        group = group_of(row)
        if group:
            grouped_rows.setdefault(group, set()).add(row["candidate_id"])
    assert grouped_rows.get("sg3-event-cand-6297") == {"cand-6297"}, grouped_rows.get("sg3-event-cand-6297")
    assert by_id["cand-6297"]["decision"] == "new"
    for group in own_groups.values():
        assert grouped_rows.get(group) == {next(cid for cid, g in own_groups.items() if g == group)}

    for candidate_id, case in CASES.items():
        row = by_id[candidate_id]
        prior = row["resolution_note"]
        row["decision"] = "new"
        row["ku_id"] = ""
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"group={case['group']}; source_ref={case['source_ref']}; "
            f"S3 event identity review 2026-10-16: undecided -> new. {case['rationale']} "
            f"Prior S3 rationale retained as history: {prior}"
        )

    expected = {"same": 1708, "new": 5016, "undecided": 5575, "excluded": 98, "conflict": 7}
    counts = {decision: sum(row["decision"] == decision for row in by_id.values()) for decision in expected}
    assert counts == expected, counts
    event_ids = {row["candidate_id"] for row in by_id.values() if candidates[row["candidate_id"]]["suggested_type"] == "event"}
    event_counts = {decision: sum(by_id[cid]["decision"] == decision for cid in event_ids) for decision in ("same", "new", "undecided")}
    assert event_counts == {"same": 7, "new": 230, "undecided": 120}, event_counts

    result_text, result_bom = read_text_preserving_bom(RESULT)
    process_text, process_bom = read_text_preserving_bom(PROCESS)
    assert MARKER not in result_text and MARKER not in process_text, "Batch already recorded."
    old_summary = "12,404 个候选决定行中，same=1,708（指向1,025个既有 KU）、new=5,005（4,834个身份组）、conflict=7、excluded=98、undecided=5,586。"
    new_summary = "12,404 个候选决定行中，same=1,708（指向1,025个既有 KU）、new=5,016（4,844个身份组）、conflict=7、excluded=98、undecided=5,575。"
    assert result_text.count(old_summary) == 1, "Current result summary changed; inspect before applying."
    result_text = result_text.replace(old_summary, new_summary, 1)
    old_pending = "尚待登记4,672组、4,798条映射。"
    new_pending = "尚待登记4,682组、4,809条映射。"
    assert result_text.count(old_pending) == 1, "Current S4 pending count changed; inspect before applying."
    result_text = result_text.replace(old_pending, new_pending, 1)
    old_event = "event 类型当前为 same=7、new=219、undecided=131。"
    new_event = "event 类型当前为 same=7、new=230、undecided=120。"
    assert result_text.count(old_event) == 1, "Current event count changed; inspect before applying."
    result_text = result_text.replace(old_event, new_event, 1)

    process_section = f"""\n\n{MARKER}

复核正文事件候选与相关索引子目后，将10个可由原文识别的独立事件／系列从 `undecided` 裁为 `new`：

| 候选 | S3 身份组 | 决定依据与边界 |
|---|---|---|
| `cand-10532` | `sg3-event-cand-10532` | 第15章 p.369 明确 Querini 于1777年赴瑞士并访问 Voltaire，同行者为 Girolamo Festari；仅确认该次行程，不补写完整路线。 |
| `cand-11601` | `sg3-event-cand-11601` | 第3章 p.79 记 Courtois 于1676年去世及 Gesù 祭坛工程随之停摆；事件与人物、未完成工程分立。 |
| `cand-11625` | `sg3-event-cand-11625` | 第3章 p.91 记 Padre Nickel 提议以秘鲁遗产装饰 Gesù 小堂、此议未获西班牙人欢迎而搁置；不推定资金转移或工程执行。 |
| `cand-11725` | `sg3-event-cand-11725` | 第5章 p.125 可识别为1607年罗马展出《圣母之死》的具体场次；场地和正式活动名称未见于该段，故不补定。 |
| `cand-11728` | `sg3-event-cand-11728` | 第5章 p.125 的罗马 Bergamasque 团体圣巴多罗买节系列，8月24日举办、1650年前已兴盛；起始年份未知。 |
| `cand-11736` | `sg3-event-cand-11736` | 第5章 p.125 另称 S. Bartolomeo all'Isola 举办该圣人命名日展览，地点与组织语境有别，单列系列。 |
| `cand-11879` | `sg3-event-cand-11879` | 第2章 p.33 明确为1593年 Henri IV reconciliation；保留 Haskell 对其作用的叙述，不标作独立核实。 |
| `cand-11932` | `sg3-event-cand-11932` | 第5章 p.138 指 Urban VIII 去世后法国影响结束；第6章 p.146 将其置于1644年3月和平之后。`cand-6260` 是随后召开、身份有别的 conclave。 |
| `cand-11942` | `sg3-event-cand-11942` | 第5章 p.143 注释记1701年 S. Salvatore in Lauro 展览及 Raggi 借展五幅 Cerquozzi 画；与12月常设系列 `cand-6051` 及1675、1697年场次分立，不推定系列归属。 |
| `cand-11955` | `sg3-event-cand-11955` | 第6章 p.146 明确 Giambattista Pamfili 当选 Innocent X；与人物 KU 及 Urban VIII 死后的 conclave (`cand-6260`) 分立。 |

另将索引候选 `cand-1821`（P.csv#20，“dispute over burial of”，p.150）与正文候选 `cand-6297`（Innocent X 葬礼费用争议）并入 `sg3-event-cand-6297`。父级索引标题是人物，但该子目指向事件；没有并入 Innocent X 人物 KU。审查了邻近事件组，包括 S. Salvatore in Lauro 的 recurring series 与已识别的1675、1697年场次、Urban VIII 死亡与其后 conclave、Henri IV reconciliation 与其后刺杀，以及第5章两种不同圣巴多罗买展览系列。

批次脚本 [复核脚本](reconcile_s3_event_cross_chapter_batch_20261016.py) 的 dry-run 核对11条原待证候选、事件类型、索引子目/正文锚点、唯一组与既有 burial-cost 事件组后通过，再 apply。决定后全局 `same=1,708`、`new=5,016`（4,844组）、`undecided=5,575`、`conflict=7`、`excluded=98`；event 为 `same=7`、`new=230`、`undecided=120`。S4 仍待登记4,682组、4,809条候选映射；无新 KU、外部身份记录或正式关系。尚未定位到同一原文场景或无法判明系列/单次场次边界的事件仍留 `undecided`，继续按其对齐行 `source_ref` 回到对应章节复核。
"""

    result_section = f"""\n\n{MARKER}

将10个正文事件／系列候选裁为10个新的事件身份组；另将索引候选 `cand-1821` 并入正文候选 `cand-6297` 的 Innocent X 葬礼费用争议组。主要对象界线包括：Bergamasque 与 S. Bartolomeo all'Isola 两种节庆展览系列分开；1701年 S. Salvatore in Lauro 展览与 recurring series 及已知的1675、1697年场次分开；Urban VIII 之死与其后 conclave 分开；1593年 Henri IV reconciliation 与1610年刺杀分开。所有决定保留原文限定及旧裁决历史，待证的场地、完整行程和系列归属不补定。

本批后全局 S3 为 `same=1,708`、`new=5,016`（4,844组）、`undecided=5,575`、`conflict=7`、`excluded=98`；event 类型为 `same=7`、`new=230`、`undecided=120`。S4 尚待4,682组、4,809条候选映射。过程证据见[处理记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)与[批次复核脚本](../../03-processing/patrons-and-painters-full-book-s2/process/reconcile_s3_event_cross_chapter_batch_20261016.py)，候选决定见[对齐表](../tables/alignment.csv)。
"""

    process_text += process_section
    result_text += result_section

    print("S3 event cross-chapter batch dry-run passed")
    print("new event candidates:", 10)
    print("joined existing event group: cand-1821 -> sg3-event-cand-6297 (cand-6297)")
    print("global decisions:", counts)
    print("event decisions:", event_counts)
    print("result/process append and current counters verified")
    if args.apply:
        write_csv(ALIGNMENT, alignment_fields, alignment_rows)
        write_text_preserving_bom(PROCESS, process_text, process_bom)
        write_text_preserving_bom(RESULT, result_text, result_bom)
        print("applied alignment decisions and updated process/current result records")
    else:
        print("dry-run only; pass --apply to write")


if __name__ == "__main__":
    main()
