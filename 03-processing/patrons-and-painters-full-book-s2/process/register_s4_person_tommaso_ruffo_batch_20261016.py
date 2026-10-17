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
GROUP = "new-person:ruffo-tommaso-362bd882fa"

RECORD = {
    "candidate": "cand-2304",
    "group": GROUP,
    "slug": "tommaso-ruffo",
    "name_zh": "托马索·鲁福",
    "name_en": "Tommaso Ruffo",
    "description_zh": "哈斯克尔将枢机托马索·鲁福置于意大利地方赞助语境，记述他1706年获枢机职、曾在拉文纳任特使并前往费拉拉；书中又以他在费拉拉汇集绘画、在多座任职城市委托作品为例。第8章叙述正文的 OCR 多处写作“Russo”，而同章后注所引费拉拉手稿题名写作“Ruffo”；本卡依书内手稿题名与索引规范为 Ruffo，并保留这一拼写差异。以上均为原书记述，本轮没有外部核验。",
    "description_en": "Haskell presents Cardinal Tommaso Ruffo in the context of provincial patronage in Italy. The account says he became cardinal in 1706, served as legate in Ravenna before going to Ferrara, assembled pictures there, and commissioned works in cities where he served. The Chapter 8 narrative OCR reads ‘Russo’ several times, while the Ferrara manuscript title quoted in the note reads ‘Ruffo’; this card uses Ruffo from that title and the index while preserving the spelling discrepancy. These remain the book's reports; no external verification was made in this batch.",
    "context_zh": "第8章 p.221 叙述其枢机身份、拉文纳特使任职及赴费拉拉；接续段落使用 Ruffo 和 Russo 两种拼写，并叙述其绘画收藏及委托。p.224 后注引 Biblioteca Ariostea 手稿题名，称其为 Cardinal Tommaso Ruffo。",
    "context_en": "Chapter 8 (p. 221) recounts his cardinalate, legation in Ravenna, and move to Ferrara; the continuation uses both Ruffo and Russo and describes his picture collection and commissions. A note on p. 224 quotes a Biblioteca Ariostea manuscript title naming him Cardinal Tommaso Ruffo.",
    "boundary_zh": "本卡依据第8章同一连续叙述及后注中的手稿题名识别人物；叙述正文的 Russo 与 Ruffo 异文保留为来源拼写差异，不拆为两个人。姓名使用原书索引及手稿题名支持的 Tommaso Ruffo；中文音译仅作显示。候选 cand-2305、cand-2308 只有索引子目而无映射的 S2 正文提及，仍为 undecided，未在本批并入。S2 中关于职务、作品、收藏、委托和相关人物的断言仍待 S6 逐项审查；本卡不新增正式关系，也不补入外部生平。",
    "boundary_en": "This identification follows the continuous Chapter 8 account and the manuscript title quoted in its note. The narrative spellings Russo and Ruffo are retained as source variants and are not split into two people. The display name Tommaso Ruffo follows the book's index and manuscript title; the Chinese form is transliterated for display. Index-only candidates cand-2305 and cand-2308 have no mapped S2 body mentions and remain undecided; they are not included in this registration. S2 claims about offices, works, collecting, commissions, and other people remain for item-level S6 review. This card adds no formal relations or external biography.",
    "sources": [
        card_writer.source(
            "8", "221", "08_CHP-8_sec_ii.md", "115",
            "One such was Cardinal Tommaso Russo.",
            "第8章以 Cardinal Tommaso Russo 为地方赞助的例子；保留该处 OCR 拼写。",
        ),
        card_writer.source(
            "8", "221", "08_CHP-8_sec_ii.md", "118",
            "He was made Cardinal in 1706, after which he returned to Ravenna as Legate for a short time before going to Ferrara, with which his connection was particularly close.",
            "第8章记述其1706年获枢机职，并在拉文纳任特使后前往费拉拉。",
        ),
        card_writer.source(
            "8", "221", "08_CHP-8_sec_ii.md", "122",
            "Even this brief outline of his career will show that Ruffo had plenty of opportunities for seeking works by most of the leading Italian artists with the notable exception of those in Venice. And the very varied contents of his gallery testify to the width of his tastes as well as to his enthusiasm. It was in Ferrara that he brought the collection together, though we know that he would commission paintings in most of the towns in which he resided.",
            "第8章接续段以 Ruffo 称呼同一人物，称其在费拉拉汇集绘画，并在多座任职城市委托绘画。",
        ),
        card_writer.source(
            "8", "224", "08_CHP-8_sec_ii.md", "382",
            "Sig.r Card.l Tommaso Ruffo",
            "第8章后注引 Biblioteca Ariostea, Collezione Antonelli MS. 610 的费拉拉宫殿与画廊手稿题名，明确写作 Cardinal Tommaso Ruffo。",
        ),
    ],
    "type_notes_zh": "索引主词及第224页所引手稿题名均作 Ruffo；第8章正文 OCR 多处作 Russo。依来源语境将二者保留为同一候选的拼写差异，不将 OCR 形式当作另一人物。",
    "type_notes_en": "The index headword and the manuscript title quoted on p. 224 read Ruffo; the Chapter 8 narrative OCR reads Russo in several places. The variants are retained for this person and are not treated as separate identities.",
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
    parser = argparse.ArgumentParser(description="Register Cardinal Tommaso Ruffo as an S4 person KU")
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
    assert len(manifest) == 1124, f"unexpected manifest count: {len(manifest)}"

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
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (105, 111)
    for group, rows in registered_groups.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(new_groups[group]) and len({row["ku_id"] for row in mapped}) == 1, group

    cid = RECORD["candidate"]
    candidate = candidate_by_id[cid]
    alignment = alignment_by_id[cid]
    assert candidate["suggested_type"] == KIND
    assert candidate["canonical_name"] == "Ruffo, Cardinal Tommaso"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert get_group(alignment["resolution_note"]) == GROUP
    assert [row["candidate_id"] for row in new_groups[GROUP]] == [cid]
    candidate_endpoints = set()
    endpoint_statement_count = 0
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as f:
        for line in f:
            statement = json.loads(line)
            endpoints = {
                item for item in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
                if item
            }
            candidate_endpoints.update(endpoints)
            endpoint_statement_count += cid in endpoints
    assert cid in candidate_endpoints and endpoint_statement_count > 0

    rel_path = f"04-knowledge/units/persons/{RECORD['slug']}.md"
    ku_id = f"units/persons/{RECORD['slug']}"
    card_path = UNITS / "persons" / f"{RECORD['slug']}.md"
    assert not card_path.exists() and rel_path not in accepted_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    assert not any(
        row["type"] == "person" and (row.get("name_en", "").casefold() == RECORD["name_en"].casefold())
        for row in manifest
    ), "an exact same-name person KU already exists"
    for sibling in ("cand-2305", "cand-2308"):
        assert alignment_by_id[sibling]["decision"] == "undecided"
        assert "s2_mentions=none" in alignment_by_id[sibling]["resolution_note"]
    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (cid, item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_manifest = list(manifest)
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
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (106, 112)
    assert len(planned_manifest) == 1125

    if args.dry_run:
        print(
            "dry-run passed: person_groups=1 candidates=1 statement_endpoints="
            f"{endpoint_statement_count} registered_groups_after=106 mapped_candidates_after=112 "
            "manifest_after=1125; index-only Ruffo candidates remain undecided"
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
    print(f"applied: person_groups=1 candidates=1 statement_endpoints={endpoint_statement_count} manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
