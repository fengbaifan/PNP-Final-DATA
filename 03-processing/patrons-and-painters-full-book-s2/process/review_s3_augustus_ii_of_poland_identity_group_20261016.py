from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import shutil
from collections import Counter
from io import StringIO
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
KNOWLEDGE = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-16"

MEMBERS = ("cand-0146", "cand-0147")
GROUP = "new-person:augustus-ii-of-poland-e7b26d3f40"
SON_KU = "units/persons/augustus-iii-of-poland"
GND_ID = "118505084"
GND_URL = f"https://www.deutsche-biographie.de/gnd{GND_ID}.html"
SAXON_BIO_URL = "https://saebi.isgv.de/biografie/Friedrich_August_I._von_Sachsen_(1670-1733)"
BACKUP_SUFFIX = ".bak-s3-augustus-ii-identity-20261016"


def decision_row(rows, candidate_id: str):
    matches = [
        row for row in rows
        if row.get("candidate_id") == candidate_id and not row.get("external_source")
    ]
    assert len(matches) == 1, (candidate_id, len(matches))
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review the Augustus II person group and distinguish it from the accepted Augustus III KU."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as stream:
        candidate_fields = list(csv.DictReader(stream).fieldnames or [])
        stream.seek(0)
        candidates = list(csv.DictReader(stream))
    with ALIGNMENT.open(encoding="utf-8-sig", newline="") as stream:
        alignment_fields = list(csv.DictReader(stream).fieldnames or [])
        stream.seek(0)
        alignments = list(csv.DictReader(stream))
    with MANIFEST.open(encoding="utf-8-sig", newline="") as stream:
        manifest = list(csv.DictReader(stream))

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    target_rows = {cid: decision_row(alignments, cid) for cid in MEMBERS}
    assert len(candidate_fields) > 0
    assert len([row for row in alignments if row.get("candidate_id") == MEMBERS[0] and row.get("external_source")]) == 0
    assert len([row for row in alignments if row.get("candidate_id") == MEMBERS[1] and row.get("external_source")]) == 0
    for cid, row in target_rows.items():
        candidate = candidate_by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert candidate["canonical_name"] == "Augustus II of Poland (Frederick Augustus I, Elector of Saxony)"
        assert row["decision"] == "new" and not row["ku_id"]
        assert sync.get_group(row["resolution_note"]) == GROUP
    assert candidate_by_id[MEMBERS[0]]["index_entry_id"] == "A.csv#147"
    assert candidate_by_id[MEMBERS[1]]["index_entry_id"] == "A.csv#148"
    assert candidate_by_id[MEMBERS[0]]["index_page_range"] == "266, 278, 294"
    assert candidate_by_id[MEMBERS[1]]["sub_entry"] == "patronage of Venetian artists"
    assert candidate_by_id[MEMBERS[1]]["index_page_range"] == "294"

    member_rows = [
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row["decision"] == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert set(member_rows) == set(MEMBERS), member_rows

    with (ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "A.csv").open(
        encoding="cp1252", newline=""
    ) as stream:
        index_rows = list(csv.DictReader(stream))
    for cid, entry, subentry in ((MEMBERS[0], 147, ""), (MEMBERS[1], 148, "patronage of Venetian artists")):
        source_row = index_rows[entry]
        assert source_row["Main Entry"] == candidate_by_id[cid]["canonical_name"]
        assert source_row["Sub-entry"] == subentry

    source10 = (ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    for quote in (
        "Frederick Augustus I, Elector of Saxony, and since 1697 King of Poland as Augustus II",
        "his son Augustus III, who succeeded to the throne in 1733",
        "Augustus the Strong",
    ):
        assert quote in source10, quote

    statements = [
        json.loads(line)
        for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct_statements = [
        row for row in statements
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    relation_candidates = [
        row for row in direct_statements
        if row.get("qualifiers", {}).get("relation_candidate") is True
    ]
    assert len(direct_statements) == 10 and len(relation_candidates) == 9

    son_manifest = next(row for row in manifest if row.get("ku_id") == SON_KU)
    assert son_manifest["type"] == "person"
    son_card = (ROOT / son_manifest["card_path"]).read_text(encoding="utf-8-sig")
    assert "Augustus III of Poland" in son_card and "Augustus II of Poland" in son_card
    assert not any(
        row.get("type") == "person"
        and ("Augustus II of Poland" in row.get("name_en", "") or "Friedrich August I" in row.get("name_en", ""))
        for row in manifest
    ), "an Augustus II person KU already exists"

    planned = [dict(row) for row in alignments]
    planned_by_id = {cid: decision_row(planned, cid) for cid in MEMBERS}
    planned_by_id[MEMBERS[0]]["process_ref"] = "S3-full-book-2026-10-16"
    planned_by_id[MEMBERS[0]]["resolution_note"] += (
        " S3 identity review (2026-10-16): ch.10 p.294 explicitly identifies Frederick Augustus I, Elector of Saxony, "
        "as King of Poland Augustus II ‘the Strong’; ch.10 p.278 uses the same byname in the Diziani context. "
        "Deutsche Biographie/GND 118505084 confirms Friedrich August I, 1670–1733, as Elector of Saxony and King of Poland "
        "(August II), with the variants Friedrich August I von Sachsen and August der Starke. Sächsische Biografie independently "
        "uses Friedrich August I (August II, der Starke) and records the same Saxon and Polish offices and dates. The index main "
        "entry and its patentage subentry cand-0147 therefore remain one new person identity group; no existing person KU for this "
        "individual is present. The accepted Augustus III KU is a distinct person: the book calls him Augustus II’s son and says "
        "he succeeded in 1733; Deutsche Biographie likewise identifies Friedrich August II / Augustus III as the previous ruler’s son. "
        "Do not merge the father’s group with the son’s KU. The original new-group proposal remains current; S4 registration is pending."
    )
    planned_by_id[MEMBERS[1]]["process_ref"] = "S3-full-book-2026-10-16"
    planned_by_id[MEMBERS[1]]["resolution_note"] += (
        " S3 identity review (2026-10-16): A.csv#148 is the ‘patronage of Venetian artists’ subentry under the same full-name "
        "entry as cand-0146. Its p.294 source context identifies Augustus II and his Venetian-art patronage; retain it in the "
        f"same source-local person group {GROUP}. See cand-0146's authority and father/son identity comparison. This subentry is "
        "not a separate person and does not refer to the accepted Augustus III KU."
    )

    max_id = max(
        (int(match.group(1)) for row in planned if (match := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))),
        default=0,
    )
    external_rows = [
        {
            "alignment_id": f"aln-{max_id + 1:04d}",
            "candidate_id": MEMBERS[0],
            "ku_id": "",
            "external_source": "GND (Deutsche Biographie)",
            "external_id": GND_ID,
            "decision": "new",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity only: GND 118505084 is headed Friedrich August I; Deutsche Biographie records 1670–1733, "
                "the Saxon elector and Polish king roles, and variants including August II (as King of Poland), "
                "Friedrich August I von Sachsen, and August der Starke."
            ),
        },
        {
            "alignment_id": f"aln-{max_id + 2:04d}",
            "candidate_id": MEMBERS[0],
            "ku_id": "",
            "external_source": "Sächsische Biografie (ISGV)",
            "external_id": SAXON_BIO_URL,
            "decision": "new",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity only: Winfried Müller's regional biography uses Friedrich August I (August II, der Starke), "
                "dates him 1670–1733, and identifies him as Elector of Saxony and King of Poland."
            ),
        },
    ]
    planned.extend(external_rows)

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidates)
    assert totals["new_candidates"] == sum(row["decision"] == "new" for row in [decision_row(planned, cid) for cid in candidate_by_id])
    current_external_count = sum(bool(row.get("external_source")) for row in alignments)
    external_count = sum(bool(row.get("external_source")) for row in planned)
    assert external_count == current_external_count + len(external_rows)

    result_text = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    result_text, count_updates = re.subn(
        r"\d+(?=条外部身份记录单独保留)", str(external_count), result_text, count=1
    )
    assert count_updates == 1
    result_marker = "### S4 按类型登记进度"
    assert result_text.count(result_marker) == 1
    result_note = (
        "本轮复核 `cand-0146`（Augustus II of Poland / Frederick Augustus I of Saxony）与其索引子项 `cand-0147`："
        f"二者保持 {GROUP} 的独立 new 身份组，外部身份由 GND 118505084 与 Sächsische Biografie 支持；"
        "已有 Augustus III 人物卡对应其子，原书与权威记录均明确父子及继位边界，故不映射到该卡。KU 尚未登记；10条直接 S2 陈述中的9条关系候选留待 S6。\n\n"
    )
    assert "本轮复核 `cand-0146`" not in result_text
    result_text = result_text.replace(result_marker, result_note + result_marker, 1)

    process_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    heading = f"### S3 person：Augustus II of Poland 身份组复核（{DATE}）"
    assert heading not in process_text
    process_note = (
        f"\n\n{heading}\n\n"
        f"- `cand-0146`（A.csv#147，pp.266、278、294）与 `cand-0147`（A.csv#148，patronage of Venetian artists，p.294）"
        f"继续组成 `{GROUP}`，决定保持 `new`，暂不写 `ku_id`，待 S4 登记。第10章 p.294 明称 Frederick Augustus I 为萨克森选帝侯、"
        "自1697年起为波兰国王 Augustus II ‘the Strong’；p.278 也用 Augustus the Strong 记其宫廷任用 Diziani。Deutsche Biographie 的"
        "GND 118505084 以 Friedrich August I 为标题，记1670–1733、萨克森选帝侯与波兰国王 Augustus II 身份，并列 August der Starke 等异名；"
        "Sächsische Biografie 亦以 Friedrich August I (August II, der Starke) 记其头衔与生卒年。索引子项 `cand-0147` 与同一索引主项和 p.294 语境对应，"
        "因此是同组的索引切分，不另立人物。全书尚无指向该人的同一 person KU。\n"
        f"- 边界核验：既有人物 KU `{SON_KU}` 是 Augustus III / Frederick Augustus II。原书 p.294 明称 Augustus III 为 Augustus II 之子、"
        "并记其1733年继位；Deutsche Biographie 另有其子 Friedrich August II 的单独身份记录。父子头衔相邻但身份不同，Augustus II 组不并入 Augustus III 卡。"
        "本轮补入两个身份记录（GND 118505084、Sächsische Biografie）；未登记 KU、未新建关系，也未把外部生平事实注入知识卡。\n\n"
        f"涉及该组的{len(direct_statements)}条直接 S2 陈述中{len(relation_candidates)}条为关系候选，均留待 S6；组成员继续待 S4 登记。当前 S4 已登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条成员映射，尚待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条。\n"
    )
    process_text += process_note

    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=alignment_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(planned)
    updated = {
        ALIGNMENT: buffer.getvalue(),
        RESULT: result_text,
        KNOWLEDGE: process_text,
    }
    for path in updated:
        assert not path.with_name(path.name + BACKUP_SUFFIX).exists(), path

    before_decisions = [decision_row(alignments, cid) for cid in candidate_by_id]
    after_decisions = [decision_row(planned, cid) for cid in candidate_by_id]
    assert Counter(row["decision"] for row in before_decisions) == Counter(row["decision"] for row in after_decisions)
    assert len([row for row in after_decisions if sync.get_group(row["resolution_note"]) == GROUP]) == 2

    if args.dry_run:
        for path, content in updated.items():
            current = path.read_text(encoding="utf-8-sig")
            diff = difflib.unified_diff(
                current.splitlines(keepends=True), content.splitlines(keepends=True),
                fromfile=str(path.relative_to(ROOT)), tofile=str(path.relative_to(ROOT)) + " (updated)", n=2,
            )
            print("".join(diff), end="")
        print(
            f"dry-run passed: group={GROUP} members={','.join(MEMBERS)} remains new/pending S4; "
            f"distinct_from={SON_KU}; direct_statements={len(direct_statements)} relation_candidates_pending={len(relation_candidates)}; "
            f"external_records={current_external_count}->{external_count}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']} "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)} unchanged"
        )
        return 0

    backups = []
    for path in updated:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        shutil.copy2(path, backup)
        backups.append((path, backup))
    try:
        for path, content in updated.items():
            path.write_text(content, encoding="utf-8-sig", newline="\n")
    except Exception:
        for path, backup in backups:
            shutil.copy2(backup, path)
        raise
    print(
        f"applied: {GROUP} remains new/pending S4; members={','.join(MEMBERS)}; distinct_from={SON_KU}; "
        f"direct_statements={len(direct_statements)} relation_candidates_pending={len(relation_candidates)}; "
        f"external_records={external_count}; registered={totals['registered_groups']}/{totals['registered_members']} "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)} unchanged; "
        f"recovery_backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
