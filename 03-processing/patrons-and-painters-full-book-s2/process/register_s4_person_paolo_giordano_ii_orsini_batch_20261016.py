from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
UNITS = ROOT / "04-knowledge" / "units"
KIND = "person"
GROUP = "new-person:bracciano-giordona-ii-of-orsini-paolo-502da19f7d"
MEMBERS = ("cand-0428", "cand-0434")

RECORD = {
    "candidate": "cand-0428",
    "group": GROUP,
    "slug": "paolo-giordano-ii-orsini",
    "name_zh": "保罗·乔尔达诺二世·奥尔西尼",
    "name_en": "Paolo Giordano II Orsini",
    "description_zh": "第4章明确称其为 Paolo Giordano II Orsini、布拉恰诺公爵，并叙述其音乐、戏剧兴趣及艺术交往。第19章附录列出与其委托 Bernini、Tacca 有关的文件；第20章后记提到一尊以他为主人公的青铜胸像，同时记录对 Bernini 归属的异议。本卡据书内全名和跨章指代登记身份；委托、作品及作者归属仍按 Haskell 的报告范围保留，不视为外部核实。",
    "description_en": "Chapter 4 names him Paolo Giordano II Orsini, Duke of Bracciano, and recounts his interests in music and theatre and his artistic associations. Appendix 2 presents documents relating to commissions from him to Bernini and Tacca. The Chapter 20 postscript mentions a small bronze bust identified as him while also reporting objections to its attribution to Bernini. This card registers the identity from the book's full name and cross-chapter references; commissions, works, and attribution remain within Haskell's report and are not treated as externally verified.",
    "context_zh": "第4章 p.95 以全名识别其为布拉恰诺公爵；第19章附录2 p.387 标题称收录其与 Bernini、Tacca 委托有关的文件；第20章 p.401 再次以 Paolo Giordano II Orsini 全名讨论青铜半身像及其作者归属争议。",
    "context_en": "Chapter 4 (p. 95) identifies him by full name as Duke of Bracciano. The title of Appendix 2 (p. 387) describes documents relating to his commissions to Bernini and Tacca. The Chapter 20 postscript (p. 401) again names Paolo Giordano II Orsini when discussing a bronze bust and the dispute over its attribution.",
    "boundary_zh": "本卡仅指 Paolo Giordano II Orsini。已有 `paolo-giordano-orsini` 卡记录 Paolo Giordano I，世代不同，不并合；`duke-bracciano-mulier` 卡所指公爵仍未具名，不能承载本人的已知全名。第19章附录标题的 Paolo Giordano Orsini 与第4、20章具名者按书内引证和同名语境归为同一人。青铜半身像对 Bernini 的归属在后记中被质疑；本卡不将其写为 Bernini 确作。S2 的创作、委托、作品与人物交往断言仍待 S6 审查，本卡不新增正式关系或外部生平。",
    "boundary_en": "This card refers only to Paolo Giordano II Orsini. The existing `paolo-giordano-orsini` card records Paolo Giordano I, a different generation, and is not merged. The `duke-bracciano-mulier` card refers to an unnamed duke and cannot carry this known full name. The Paolo Giordano Orsini named in the Chapter 19 appendix is matched to the person identified in Chapters 4 and 20 by the book's cross-references and context. The postscript questions the attribution of the bronze bust to Bernini; this card does not state that Bernini made it. S2 claims about commissions, works, and personal associations remain for S6 review. No formal relations or external biography are added.",
    "sources": [
        card_writer.source(
            "4", "95", "04_CHP-4_sec_i.md", "12–13",
            "Paolo\nGiordano II Orsini, Duke of Bracciano,",
            "第4章明确给出 Paolo Giordano II Orsini 全名及布拉恰诺公爵身份。",
        ),
        card_writer.source(
            "19", "387", "19_CHP-19Appendix.md", "33–35",
            "APPENDIX 2\nDocuments relating to commissions from Paolo Giordano Orsini, duke of Bracciano, to\nBernini and Tacca in thè Fondo Orsini, Biblioteca Vallicelliana, Rome.",
            "第19章附录2标题将 Paolo Giordano Orsini、布拉恰诺公爵与 Bernini、Tacca 委托文件相连，并指回第4章。",
        ),
        card_writer.source(
            "20", "401", "20_CHP-20Postscript.md", "85–86",
            "a small bronze bust of Paolo\nGiordano II Orsini, Duke of Bracciano",
            "第20章后记提到一尊以 Paolo Giordano II Orsini 为对象的青铜半身像。",
        ),
        card_writer.source(
            "20", "401", "20_CHP-20Postscript.md", "88",
            "I understand, however, that there are convincing documentary reasons for believing that the attribution to Bernini of this attractive bust has to.be rejected.",
            "第20章后记记录了对该半身像归于 Bernini 的异议。",
        ),
    ],
    "type_notes_zh": "规范名采用第4章及第20章的全名 Paolo Giordano II Orsini；第19章附录标题省略罗马数字，但明确回指第4章相关委托。中文名为便于识别的音译。",
    "type_notes_en": "The normalized name follows the full form Paolo Giordano II Orsini in Chapters 4 and 20. The Chapter 19 appendix title omits the numeral but explicitly points back to the relevant commissions in Chapter 4. The Chinese form is a transliteration for display.",
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note):
    match = re.search(r"group=([^;| ]+)", note)
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser(description="Register Paolo Giordano II Orsini as one S4 person KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_path = TABLES / "ku-manifest.csv"
    alignment_path = TABLES / "alignment.csv"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    manifest_fields, manifest = read_csv(manifest_path)
    alignment_fields, alignments = read_csv(alignment_path)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")
    assert len(manifest) == 1125, f"unexpected manifest count: {len(manifest)}"

    current = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    new_rows = [row for row in current if row["decision"] == "new"]
    new_groups = defaultdict(list)
    registered = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group
        new_groups[group].append(row)
        if row.get("ku_id"):
            registered[group].append(row)
    assert (len(current), len(new_rows), len(new_groups)) == (12403, 5006, 4829)
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (106, 112)
    for group, rows in registered_groups.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(new_groups[group]) and len({row["ku_id"] for row in mapped}) == 1, group

    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate["suggested_type"] == KIND
        assert candidate["canonical_name"] == "Bracciano, Paolo Giordona II Orsini, Duke of"
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert get_group(alignment["resolution_note"]) == GROUP
    assert {row["candidate_id"] for row in new_groups[GROUP]} == set(MEMBERS)

    rel_path = f"04-knowledge/units/persons/{RECORD['slug']}.md"
    ku_id = f"units/persons/{RECORD['slug']}"
    card_path = UNITS / "persons" / f"{RECORD['slug']}.md"
    assert not card_path.exists() and rel_path not in accepted_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    assert not any(
        row["type"] == "person" and row.get("name_en", "").casefold() == RECORD["name_en"].casefold()
        for row in manifest
    ), "an exact same-name person KU already exists"
    paolo_i = (UNITS / "persons" / "paolo-giordano-orsini.md").read_text(encoding="utf-8-sig")
    mulier_duke = (UNITS / "persons" / "duke-bracciano-mulier.md").read_text(encoding="utf-8-sig")
    assert "Paolo Giordano I Orsini" in paolo_i
    assert "Ferdinando Orsini" in mulier_duke and "Flavio Orsini" in mulier_duke

    endpoint_statement_count = 0
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as f:
        for line in f:
            statement = json.loads(line)
            endpoints = {
                item for item in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
                if item
            }
            endpoint_statement_count += bool(endpoints & set(MEMBERS))
    assert endpoint_statement_count == 73, f"unexpected statement endpoint count: {endpoint_statement_count}"

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_manifest = list(manifest)
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = ku_id
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {ku_id}."
    planned_manifest.append({
        "ku_id": ku_id,
        "type": KIND,
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": rel_path,
    })
    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if not row.get("external_source") and row["decision"] == "new":
            planned_groups[get_group(row["resolution_note"])].append(row)
    planned_registered = {group: rows for group, rows in planned_groups.items() if any(row.get("ku_id") for row in rows)}
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (107, 114)
    assert len(planned_manifest) == 1126

    if args.dry_run:
        print(
            "dry-run passed: person_groups=1 candidate_members=2 "
            f"statement_endpoints={endpoint_statement_count} registered_groups_after=107 "
            "mapped_candidates_after=114 manifest_after=1126; Paolo I and unnamed Mulier patron remain separate"
        )
        return 0

    card_text = card_writer.make_card(RECORD, KIND)
    card_text, date_count = re.subn(r"^(created|updated): '2026-10-15'$", r"\1: '2026-10-16'", card_text, flags=re.MULTILINE)
    assert date_count == 2, f"expected two card dates, found {date_count}"
    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(manifest_path, manifest_fields, planned_manifest)
    write_csv(alignment_path, alignment_fields, planned_alignment)
    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > rel_path),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {rel_path}")
    accepted_path.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    print(f"applied: person_groups=1 candidate_members=2 statement_endpoints={endpoint_statement_count} manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
