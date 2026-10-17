from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MENTIONS_PATH = TABLES / "mentions.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
RELATIONS_PATH = TABLES / "relations.csv"

CID = "cand-2209"
PERSON_CID = "cand-2208"
GROUP = "sg3-event-cand-2209"
KU = "units/events/romanelli-appointment-principe-accademia-di-san-luca-1638"
CARD = f"04-knowledge/{KU}.md"
NAME_ZH = "乔万尼·弗朗切斯科·罗马内利获任圣路加学院 Principe（1638）"
NAME_EN = "Giovanni Francesco Romanelli’s 1638 Appointment as Principe of the Accademia di S. Luca"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_iv.md"
EVENT_MENTION = "m-chp2-seciv-l106-112-0051"
APPOINTMENT_STATEMENT = "st-chp2-seciv-l106-112-romanelli-academy-prince-1638"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def make_card() -> str:
    source = {
        "citation": BOOK_CITATION,
        "location": "第二章；印刷页53；OCR L112",
        "sentence_summary": (
            "Haskell says that in 1638 Giovan Francesco Romanelli was made Principe of the Accademia di S. Luca "
            "on the orders of Cardinal [Francesco] Barberini. The passage gives no term dates or further appointment procedure."
        ),
        "original_quotes": [
            {
                "source_span": "line 112",
                "text": "In 1638 he was made Principe of the Accademia di S. Luca ‘on the orders of Cardinal [Francesco] Barberini’",
            }
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": SOURCE_FILE,
            "source_span": "line 112; print p.53",
        },
    }
    front_matter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "event",
        "evidence_status": "source_backed",
        "sources": [source],
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    body = """## 内容

### 描述

**中文：** 哈斯克尔称，1638年乔万尼·弗朗切斯科·罗马内利奉红衣主教弗朗切斯科·巴贝里尼之命，获任 Accademia di S. Luca 的 Principe。本卡记录这一次任命；保留原文职衔，不推定现代职务对应、正式任命程序或任期。引文没有说明任命地点。

**English:** Haskell states that in 1638 Giovanni Francesco Romanelli was made Principe of the Accademia di S. Luca on the orders of Cardinal Francesco Barberini. This card records that appointment; it retains the source's office title and does not infer a modern equivalent, a formal appointment procedure, or a term of office. The cited passage does not specify where the appointment took place.

### 基本信息

- **事件性质：** 人物获任 Accademia di S. Luca 的 Principe；这是本书所记的一次具体任命。
- **时间：** 1638年。原文未提供任期起止日期。
- **地点：** 引文未说明。
- **证据范围：** 哈斯克尔第2章 p.53，L112；关于任命的直接书内陈述。

### 参与者与相关机构

- **受任者：** [乔万尼·弗朗切斯科·罗马内利](../persons/romanelli.md)。原文称其获任 Principe。
- **下令者：** [弗朗切斯科·巴贝里尼](../persons/francesco-barberini.md)。原文称任命“on the orders of” Cardinal [Francesco] Barberini。
- **职衔所属机构：** [圣路加学院（Accademia di S. Luca）](../institutions/accademia-di-san-luca.md)。
- **关系审查：** S2 将人物—机构任职陈述保留为关系候选，待 S6 裁决；本卡登记不等于正式关系边，未改动 `relations.csv`。

## 关系与证据

### 来源

- [Francis Haskell, *Patrons and Painters*](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md)，第2章，印刷页53，L112。原文：“In 1638 he was made Principe of the Accademia di S. Luca ‘on the orders of Cardinal [Francesco] Barberini’”。

## 过程

- S3 将索引子目 `Romanelli, Giovan Francesco — appointment to Accademia di S. Luca` 作为事件组，未与同名人物候选合并。
- S2 的人物提及和人物断言已归到既有人物 KU；任命短语单独映射为本事件候选。
- 目前只记录本书叙述；未独立核读其脚注所引研究，亦未据此补定任期、地点或任命手续。
"""
    return "---\n" + yaml.safe_dump(front_matter, allow_unicode=True, sort_keys=False, width=110) + "---\n\n" + body


def main():
    parser = argparse.ArgumentParser(description="Register Romanelli's 1638 Accademia appointment event in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = read_csv(ENTITY_PATH)
    alignment_fields, alignment = read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    mentions_fields, mentions = read_csv(MENTIONS_PATH)
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    candidate = next(row for row in candidates if row["candidate_id"] == CID)
    event_decision = next(row for row in alignment if row.get("candidate_id") == CID and not row.get("external_source"))
    person_decision = next(row for row in alignment if row.get("candidate_id") == PERSON_CID and not row.get("external_source"))
    manifest_by_id = {row["ku_id"]: row for row in manifest}

    assert candidate["suggested_type"] == "event"
    assert candidate["index_entry_id"] == "Q-R.csv#136"
    assert candidate["sub_entry"] == "appointment to Accademia di S. Luca"
    assert event_decision["decision"] == "new" and not event_decision.get("ku_id")
    assert sync.get_group(event_decision.get("resolution_note", "")) == GROUP
    assert person_decision["decision"] == "same" and person_decision["ku_id"] == "units/persons/romanelli"
    assert KU not in manifest_by_id and not (ROOT / CARD).exists()
    assert f"- {CARD}" not in accepted_lines
    assert manifest_by_id["units/persons/romanelli"]["type"] == "person"
    assert manifest_by_id["units/institutions/accademia-di-san-luca"]["type"] == "institution"
    assert not any(
        row["type"] == "event" and row["ku_id"] != KU
        and "romanelli" in (row["canonical_name"] + row["name_en"]).casefold()
        and "1638" in (row["canonical_name"] + row["name_en"])
        for row in manifest
    ), "possible duplicate Romanelli appointment event KU"
    mention = next(row for row in mentions if row["mention_id"] == EVENT_MENTION)
    assert mention["candidate_id"] == CID and mention["surface_form"] == "In 1638 he was made Principe"

    statements = sync.load_statements()
    statement = next(row for row in statements if row["statement_id"] == APPOINTMENT_STATEMENT)
    assert statement["subject_candidate_id"] == PERSON_CID
    assert statement["object_candidate_id"] == "cand-0007"
    assert CID in statement.get("qualifiers", {}).get("mentioned_candidate_ids", [])
    assert statement.get("qualifiers", {}).get("relation_candidate") is True

    source_text = (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig")
    quote = "In 1638 he was made Principe of the Accademia di S. Luca ‘on the orders of Cardinal [Francesco] Barberini’"
    assert quote in source_text
    relations_fields, relations = read_csv(RELATIONS_PATH)
    assert relations_fields and not any(KU in str(row) for row in relations)

    planned_alignment = [dict(row) for row in alignment]
    for row in planned_alignment:
        if row.get("candidate_id") == CID and not row.get("external_source"):
            row["ku_id"] = KU
            row["resolution_note"] += (
                f" S4 registration: mapped {GROUP} to {KU}; card records the 1638 appointment evidence. "
                "Person assertion endpoints remain mapped to units/persons/romanelli."
            )

    planned_manifest = [dict(row) for row in manifest]
    planned_manifest.append({
        "ku_id": KU,
        "type": "event",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD,
    })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_anchor = "<a id=\"s4-romanelli-appointment-event\"></a>"
    process_entry = (
        f"\n\n{process_anchor}\n\n### S4 event：Romanelli 1638 年获任 Accademia di S. Luca Principe（2026-10-17）\n\n"
        f"`{CID}` 沿用 S3 事件组 `{GROUP}`，登记为 `{KU}`。候选来自索引子目“appointment to Accademia di S. Luca”；第2章 p.53 L112 明载 Romanelli 于1638年奉 Cardinal [Francesco] Barberini 之命获任 Principe。"
        "卡片保留原职衔，不补任期、任命地点或正式程序。四条人物提及和九条人物断言已归到同名人物候选 `cand-2208`；事件短语另记为 `cand-2209`。"
        "人物—机构关系仍待 S6；没有新增正式关系。"
        f"\n\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    assert process_anchor not in process_text
    process_text += process_entry
    result_text += (
        "\n\n### S4 event：Romanelli 1638 年获任圣路加学院 Principe\n\n"
        f"`{CID}` 映射至[乔万尼·弗朗切斯科·罗马内利获任圣路加学院 Principe（1638）](../units/events/romanelli-appointment-principe-accademia-di-san-luca-1638.md)。"
        "第2章 p.53 直接记载1638年任命及 Cardinal [Francesco] Barberini 的下令；原文未给任期或地点。相关人物—机构关系仍待 S6。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    planned_accepted = list(accepted_lines)
    planned_accepted.insert(insert_at, f"- {CARD}")

    if args.dry_run:
        print(f"S4 event dry-run passed: group={GROUP}; candidates=1; event mention={EVENT_MENTION}")
        print("source=Haskell, ch.2, p.53, line 112; appointment year=1638; term/location unspecified")
        print("S6 person-institution relation candidates remain pending; formal_relations_added=0")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    (ROOT / CARD).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / CARD).write_text(make_card(), encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups=1; registered={sync.fmt(totals['registered_groups'])}/"
        f"{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/"
        f"{sync.fmt(totals['pending_members'])}; manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
