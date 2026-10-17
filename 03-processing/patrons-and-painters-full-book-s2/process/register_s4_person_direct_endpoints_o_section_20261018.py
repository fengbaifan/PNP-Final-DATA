from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import register_s4_person_direct_endpoints_h_section_20261018 as template  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ENRICHMENT = TABLES / "enrichment.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-18"
ANCHOR = "s4-person-direct-endpoints-o-section-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"


def src(location: str, summary: str, quote: str, file: str, span: str) -> dict:
    return {"location": location, "summary": summary, "quote": quote, "file": file, "span": span}


TARGETS = [{'primary': 'cand-1767',
  'members': ['cand-1767'],
  'expected_name': 'Oderisi, Roberto',
  'expected_pages': '107',
  'group': 'new-person:oderisi-roberto-9cef78b777',
  'ku': 'units/persons/roberto-oderisi',
  'card': '04-knowledge/units/persons/roberto-oderisi.md',
  'name_zh': '罗伯托·奥德里西',
  'name_en': 'Roberto Oderisi',
  'name_rows': [['索引名', 'Oderisi, Roberto', 'S1（索引O.csv#1）'], ['正文姓名形式', 'Roberto Oderisi', 'S2（第4章第II节；印刷页107）']],
  'sources': [{'location': '第4章第II节；印刷页107',
               'summary': 'Haskell称那不勒斯十四世纪若干湿壁画被归于Roberto Oderisi。',
               'quote': 'some frescoes ascribed to Roberto Oderisi in fourteenth-century Naples.',
               'file': '02-sources/02-Markdown/04_CHP-4_sec_ii.md',
               'span': 'lines 101-103; print p.107'}],
  'zh': '登记索引O.csv#1的Roberto Oderisi（中文显示名为本项目工作音译）。第4章p.107仅称那不勒斯十四世纪若干湿壁画被归于Oderisi；保留Haskell的审慎措辞，不提升为确定创作事实。',
  'en': 'Registers Roberto Oderisi under index O.csv#1; the Chinese display name is a working transliteration. Chapter '
        '4, p.107, says only that some fourteenth-century Neapolitan frescoes are ascribed to Oderisi. Haskell’s '
        'qualified attribution is retained.',
  'context_zh': '作品端点cand-11648因缺少提及级锚点仍未决。',
  'context_en': 'Work endpoint cand-11648 remains undecided for lack of a mention-level anchor.',
  'relations': ['st-chp4-sec-ii-l101-107-oderisi-frescoes-ascribed'],
  'endpoints': {'st-chp4-sec-ii-l101-107-oderisi-frescoes-ascribed': 'ascribed_to'}},
 {'primary': 'cand-1769',
  'members': ['cand-1769'],
  'expected_name': 'Odescalchi, Livio',
  'expected_pages': '98',
  'group': 'new-person:livio-odescalchi-2f323704d5',
  'ku': 'units/persons/livio-odescalchi',
  'card': '04-knowledge/units/persons/livio-odescalchi.md',
  'name_zh': '利维奥·奥德斯卡尔基',
  'name_en': 'Livio Odescalchi',
  'name_rows': [['索引名', 'Odescalchi, Livio', 'S1（索引O.csv#3）'], ['正文姓名形式', 'Don Livio Odescalchi', 'S2（第4章第I节；印刷页98）']],
  'sources': [{'location': '第4章第I节；印刷页98',
               'summary': 'Haskell称Bracciano城堡及地产被售予Don Livio Odescalchi。',
               'quote': 'his nephew sold the castle and estates of Bracciano to the papal nephew of the day, Don Livio '
                        'Odescalchi.',
               'file': '02-sources/02-Markdown/04_CHP-4_sec_i.md',
               'span': 'lines 35-40; print p.98'}],
  'zh': '登记索引O.csv#3的Livio Odescalchi（中文显示名为本项目工作音译）。第4章p.98记述Bracciano城堡及地产被售予Don Livio Odescalchi，但未给准确交易日期。匿名的“his '
        'nephew”是独立未决人物端点，不推定身份。',
  'en': 'Registers Livio Odescalchi under index O.csv#3; the Chinese display name is a working transliteration. '
        'Chapter 4, p.98, reports the sale of Bracciano Castle and estates to Don Livio Odescalchi but gives no exact '
        'date. The anonymous “his nephew” remains an unidentified person endpoint.',
  'context_zh': '卖方端点cand-5577为未指名且未识别的侄子；本书未给出交易准确日期。',
  'context_en': 'Seller endpoint cand-5577 is an unnamed, unidentified nephew; the book gives no exact sale date.',
  'relations': ['st-chp4-sec-i-l35-40-sale-to-livio'],
  'endpoints': {'st-chp4-sec-i-l35-40-sale-to-livio': 'sold_bracciano_castle_and_estates_to_livio_odescalchi'}},
 {'primary': 'cand-1779',
  'members': ['cand-1779'],
  'expected_name': 'Olivieri, Pietro Paolo',
  'expected_pages': '71',
  'group': 'new-person:olivieri-paolo-pietro-b164336a9d',
  'ku': 'units/persons/pietro-paolo-olivieri',
  'card': '04-knowledge/units/persons/pietro-paolo-olivieri.md',
  'name_zh': '彼得罗·保罗·奥利维耶里',
  'name_en': 'Pietro Paolo Olivieri',
  'name_rows': [['索引名', 'Olivieri, Pietro Paolo', 'S1（索引O.csv#13）'],
                ['正文姓名形式', 'Pietro Paolo Olivieri', 'S2（第3章第II节；印刷页71）']],
  'sources': [{'location': '第3章第II节；印刷页71',
               'summary': 'Haskell称Olivieri与Giacomo della Porta先后对Theatines所提议的建筑师拥有完整决定权。',
               'quote': 'Giacomo della Porta and then Pietro Paolo Olivieri, should have complete authority over the '
                        'man whom the Theatines themselves had proposed for the commission.',
               'file': '02-sources/02-Markdown/03_CHP-3_sec_ii.md',
               'span': 'lines 62-72; print p.71'}],
  'zh': '登记索引O.csv#13的Pietro Paolo Olivieri（中文显示名为本项目工作音译）。第3章p.71称他与Giacomo della '
        'Porta先后获得对Theatines所提议建筑师的完整决定权；该建筑师未被具名，不补其身份。',
  'en': 'Registers Pietro Paolo Olivieri under index O.csv#13; the Chinese display name is a working transliteration. '
        'Chapter 3, p.71, says he and Giacomo della Porta successively had complete authority over the architect '
        'proposed by the Theatines. That architect is unnamed.',
  'context_zh': '对象cand-5063是未具名的Theatines提议人，身份仍未决。',
  'context_en': 'Object cand-5063 is the unnamed person proposed by the Theatines; identity remains undecided.',
  'relations': ['st-chp3-secii-l62-72-olivieri-authority-over-proposed-person'],
  'endpoints': {'st-chp3-secii-l62-72-olivieri-authority-over-proposed-person': 'had_complete_authority_over_theatines_proposed_commissionee'}},
 {'primary': 'cand-1781',
  'members': ['cand-1781'],
  'expected_name': 'Oppenord, Gilles-Marie',
  'expected_pages': '285',
  'group': 'new-person:gilles-marie-oppenord-5d38abd47a',
  'ku': 'units/persons/gilles-marie-oppenord',
  'card': '04-knowledge/units/persons/gilles-marie-oppenord.md',
  'name_zh': '吉尔-马里·奥本诺尔',
  'name_en': 'Gilles-Marie Oppenord',
  'name_rows': [['索引名', 'Oppenord, Gilles-Marie', 'S1（索引O.csv#15）'], ['正文姓名形式', 'Oppenord', 'S2（第10章导论；印刷页285）']],
  'sources': [{'location': '第10章导论；印刷页285',
               'summary': 'Haskell称Carriera抵达巴黎后结识多位艺术家和鉴赏家，并列出Oppenord。',
               'quote': 'Coypel, Vleughels, Oppenord, de Troy, Mariette.',
               'file': '02-sources/02-Markdown/10_CHP-10_intro.md',
               'span': 'lines 178-188; print p.285'}],
  'zh': '按索引O.csv#15的全名Gilles-Marie '
        'Oppenord与第10章p.285的姓氏形式Oppenord登记同一书内人物组（中文显示名为工作音译）。正文将其列入Carriera结识的艺术家和鉴赏家名单，但未叙述具体会面。',
  'en': 'Groups the full indexed name Gilles-Marie Oppenord from O.csv#15 with the surname form in chapter 10, p.285, '
        'as one source-local person. The passage lists him among artists and connoisseurs Carriera met but gives no '
        'encounter details.',
  'context_zh': '正文将Oppenord列入Carriera结识的艺术家和鉴赏家名单，但没有具体会面细节或日期。',
  'context_en': 'The passage lists Oppenord among Carriera’s acquaintances but gives no specific encounter details or '
                'date.',
  'relations': ['st-chp10-p285-carriera-met-oppenord'],
  'endpoints': {'st-chp10-p285-carriera-met-oppenord': 'met'}},
 {'primary': 'cand-1788',
  'members': ['cand-1788'],
  'expected_name': 'Orsini, Alessandro',
  'expected_pages': '99',
  'group': 'new-person:alessandro-orsini-908fd3aa90',
  'ku': 'units/persons/alessandro-orsini',
  'card': '04-knowledge/units/persons/alessandro-orsini.md',
  'name_zh': '亚历山德罗·奥尔西尼',
  'name_en': 'Alessandro Orsini',
  'name_rows': [['索引名', 'Orsini, Alessandro', 'S1（索引O.csv#22）'], ['正文姓名形式', 'Alessandro Orsini', 'S2（第4章第II节；印刷页99）']],
  'sources': [{'location': '第4章第II节；印刷页99',
               'summary': 'Haskell称Alessandro Orsini是Cassiano早年在罗马的密友之一，并称其为Paolo Giordano的兄弟。',
               'quote': 'Among his close friends during these early years in Rome were Alessandro Orsini, brother of '
                        'Paolo Giordano',
               'file': '02-sources/02-Markdown/04_CHP-4_sec_ii.md',
               'span': 'lines 10-13; print p.99'}],
  'zh': '登记索引O.csv#22的Alessandro Orsini（中文显示名为本项目工作音译）。第4章p.99称他为Cassiano早年在罗马的密友之一，并称其为Paolo Giordano的兄弟；正文未说明Paolo '
        'Giordano的具体世代，不匹配到某一既有Orsini人物。',
  'en': 'Registers Alessandro Orsini under index O.csv#22; the Chinese display name is a working transliteration. '
        'Chapter 4, p.99, calls him one of Cassiano’s early Roman close friends and a brother of Paolo Giordano. Since '
        'the generation is unspecified, no existing Orsini person is assumed.',
  'context_zh': 'Cassiano端点cand-2036映射到Cassiano dal Pozzo。Paolo端点cand-5645具体世代不详，尚未匹配既有人物。',
  'context_en': 'Cassiano endpoint cand-2036 maps to Cassiano dal Pozzo. The generation of Paolo endpoint cand-5645 is '
                'unspecified, so it is not matched to an existing person.',
  'relations': ['st-chp4-sec-ii-l10-13-alessandro-brother-of-paolo',
                'st-chp4-sec-ii-l10-13-cassiano-close-friend-alessandro'],
  'endpoints': {'st-chp4-sec-ii-l10-13-alessandro-brother-of-paolo': 'brother_of_reported',
                'st-chp4-sec-ii-l10-13-cassiano-close-friend-alessandro': 'close_friendship_reported'}},
 {'primary': 'cand-1793',
  'members': ['cand-1793'],
  'expected_name': 'Ottley, William Young',
  'expected_pages': '377n',
  'group': 'new-person:ottley-william-young-211293a343',
  'ku': 'units/persons/william-young-ottley',
  'card': '04-knowledge/units/persons/william-young-ottley.md',
  'name_zh': '威廉·扬·奥特利',
  'name_en': 'William Young Ottley',
  'name_rows': [['索引名', 'Ottley, William Young', 'S1（索引O.csv#28）'],
                ['正文姓名形式', 'William Young Ottley', 'S2（第16章导论；印刷页377注3）']],
  'sources': [{'location': '第16章导论；印刷页377注3',
               'summary': 'Haskell注3称微型画由William Young Ottley描述，并引Christies 1825年5月26日目录。',
               'quote': 'The miniatures are described by William Young Ottley.',
               'file': '02-sources/02-Markdown/16_CHP-16_intro.md',
               'span': 'lines 69-89; print p.377 n.3'}],
  'zh': '登记索引O.csv#28的William Young '
        'Ottley（中文显示名为本项目工作音译）。第16章p.377注3称这些微型画由Ottley描述，并列出1825年5月26日的Christies目录；仅登记Haskell转述，未独立核阅目录。',
  'en': 'Registers William Young Ottley under index O.csv#28; the Chinese display name is a working transliteration. '
        'Chapter 16, p.377 n.3, says Ottley described the miniatures and cites the Christies catalogue of 26 May 1825. '
        'The catalogue was not independently consulted.',
  'context_zh': '作品端点cand-10651仍是未决微型画组；Haskell所引Christies目录未独立核阅。',
  'context_en': 'Work endpoint cand-10651 remains an undecided group of miniatures; the Christies catalogue cited by '
                'Haskell was not independently consulted.',
  'relations': ['st-chp16-p377-note3-miniatures-described-by-ottley'],
  'endpoints': {'st-chp16-p377-note3-miniatures-described-by-ottley': 'described_by_william_young_ottley'}}]

CORRECTIONS = []


def make_batch_card(target: dict) -> str:
    card = template.make_card(target)
    relations = ", ".join(target["relations"])
    if relations:
        zh_display = f"直接S2候选（待S6）：{relations}。"
        en_display = f"Direct S2 relation candidates pending individual review in S6: {relations}."
    else:
        zh_display = "当前未有直接S2关系候选映射到此人物端点。"
        en_display = "S2 does not currently map this person as a direct relation-candidate endpoint."
    zh_context_suffix = f" 直接S2关系候选{relations}仍待S6逐条裁决；本次登记不建立正式边。"
    en_context_suffix = f" Direct S2 relation candidates {relations} remain for individual S6 review; this registration creates no formal edges."
    assert zh_context_suffix in card
    assert en_context_suffix in card
    card = card.replace(zh_context_suffix, "", 1).replace(en_context_suffix, "", 1)
    old = f"**English:** {zh_display}\n"
    new = f"**English:** {en_display}\n"
    assert old in card
    return card.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Register six new O-section person groups.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--refresh-cards", action="store_true")
    args = parser.parse_args()
    template.TARGETS = TARGETS
    template.DATE, template.ANCHOR, template.PROCESS_REF = DATE, ANCHOR, PROCESS_REF
    sync = template.helper.base.sync
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    main_rows = [r for r in alignments if r.get("candidate_id") and not r.get("external_source")]
    main_by_id = {r["candidate_id"]: r for r in main_rows}
    manifest_by_ku = {r["ku_id"]: r for r in manifest}
    accepted_lines = ACCEPTED.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]

    for correction in CORRECTIONS:
        row = main_by_id[correction["candidate"]]
        existing = main_by_id[correction["existing_candidate"]]
        assert row.get("decision") == "new" or (row.get("decision") == "same" and row.get("ku_id") == correction["ku"])
        assert existing.get("decision") == "same" and existing.get("ku_id") == correction["ku"]
        assert correction["ku"] in manifest_by_ku
        assert "- 04-knowledge/units/persons/benedict-nicolson.md" in accepted_lines
        existing_card = ROOT / "04-knowledge/units/persons/benedict-nicolson.md"
        assert existing_card.exists() and "Benedict Nicolson" in existing_card.read_text(encoding="utf-8-sig")
        candidate = candidate_by_id[correction["candidate"]]
        assert candidate.get("canonical_name") == "Nicolson, Benedict" and candidate.get("index_page_range") == "94n"
        source_text = (ROOT / correction["source_file"]).read_text(encoding="utf-8-sig")
        assert re.sub(r"\s+", " ", correction["quote"]) in re.sub(r"\s+", " ", source_text)
        direct = {r["statement_id"]: r for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and (r.get("subject_candidate_id") == correction["candidate"] or r.get("object_candidate_id") == correction["candidate"])}
        assert set(direct) == {correction["statement_id"]}
        assert direct[correction["statement_id"]].get("predicate") == correction["predicate"]
        if row.get("decision") == "same":
            assert correction["note"] in row.get("resolution_note", "")

    for target in TARGETS:
        candidate = candidate_by_id[target["primary"]]
        target["entry"], target["index_name"], target["pages"] = candidate["index_entry_id"], candidate["canonical_name"], candidate["index_page_range"]
        assert candidate.get("suggested_type") == "person"
        assert (candidate.get("canonical_name"), candidate.get("index_page_range")) == (target["expected_name"], target["expected_pages"])
        row = main_by_id[target["primary"]]
        assert row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == target["group"]
        assert not row.get("ku_id") or row.get("ku_id") == target["ku"]
        members = [r["candidate_id"] for r in main_rows if r.get("decision") == "new" and sync.get_group(r.get("resolution_note", "")) == target["group"]]
        assert members == target["members"]
        index_file, _ = target["entry"].split("#", 1)
        index_hits = [r for r in template.helper.base.read_index_rows(index_file) if r.get("Main Entry") == target["index_name"] and r.get("Page Numbers") == target["pages"] and not r.get("Sub-entry")]
        assert len(index_hits) == 1
        direct = {r["statement_id"]: r for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and (r.get("subject_candidate_id") == target["primary"] or r.get("object_candidate_id") == target["primary"])}
        assert set(direct) == set(target["endpoints"]), (target["primary"], sorted(direct), sorted(target["endpoints"]))
        for statement_id, predicate in target["endpoints"].items():
            assert direct[statement_id].get("predicate") == predicate
        for item in target["sources"]:
            source_text = (ROOT / item["file"]).read_text(encoding="utf-8-sig")
            assert re.sub(r"\s+", " ", item["quote"]) in re.sub(r"\s+", " ", source_text), (target["primary"], item["span"])
        path = ROOT / target["card"]
        mapped = row.get("ku_id") == target["ku"]
        assert (target["ku"] in manifest_by_ku) == (target["card"] in accepted_paths) == path.exists() == mapped

    cards = {target["card"]: make_batch_card(target) for target in TARGETS}
    all_registered = (
        all(main_by_id[target["primary"]].get("ku_id") == target["ku"] for target in TARGETS)
        and all(main_by_id[correction["candidate"]].get("decision") == "same" and main_by_id[correction["candidate"]].get("ku_id") == correction["ku"] for correction in CORRECTIONS)
    )
    if all_registered:
        if args.refresh_cards:
            for target in TARGETS:
                template.atomic_write(ROOT / target["card"], template.with_bom(cards[target["card"]]))
            print("refreshed person cards: removed repeated S6 context and restored English relation summaries")
            return 0
        for target in TARGETS:
            assert (ROOT / target["card"]).read_text(encoding="utf-8-sig") == cards[target["card"]]
        print("ALREADY REGISTERED: all person groups and their source-backed name fields are recorded.")
        return 0
    assert not any(main_by_id[target["primary"]].get("ku_id") for target in TARGETS), "partial registration requires explicit reconciliation"

    before = sync.summarize_by_type(candidates, alignments)
    before_totals = {key: sum(row[key] for row in before.values()) for key in next(iter(before.values()))}
    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignments if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest, planned_accepted = list(manifest), list(accepted_lines)
    corrections_to_apply = 0
    for correction in CORRECTIONS:
        row = planned_by_id[correction["candidate"]]
        if row.get("decision") == "new":
            row["decision"], row["ku_id"], row["process_ref"] = "same", correction["ku"], PROCESS_REF
            row["resolution_note"] += " " + correction["note"]
            corrections_to_apply += 1
        else:
            assert row.get("decision") == "same" and row.get("ku_id") == correction["ku"]
    for target in TARGETS:
        row = planned_by_id[target["primary"]]
        row["ku_id"], row["process_ref"] = target["ku"], PROCESS_REF
        if target.get("s3_note"):
            row["resolution_note"] += " " + target["s3_note"]
        row["resolution_note"] += f" S4 registration ({DATE}): group {target['group']} -> {target['ku']}; source-backed person identity registration; direct S2 relation candidates remain for S6."
        planned_manifest.append({"ku_id": target["ku"], "type": "person", "canonical_name": target["name_zh"], "name_en": target["name_en"], "source_task": TASK, "card_path": target["card"]})
        planned_accepted = template.helper.base.insert_accepted(planned_accepted, target["card"])

    planned_manifest.sort(key=lambda row: row["ku_id"])
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    batch_size = len(TARGETS)
    assert totals["registered_groups"] == before_totals["registered_groups"] + batch_size
    assert totals["registered_members"] == before_totals["registered_members"] + batch_size
    assert totals["same_candidates"] == before_totals["same_candidates"] + corrections_to_apply
    assert totals["new_candidates"] == before_totals["new_candidates"] - corrections_to_apply
    assert totals["pending_groups"] == before_totals["pending_groups"] - batch_size - corrections_to_apply
    assert totals["pending_members"] == before_totals["pending_members"] - batch_size - corrections_to_apply
    assert len(planned_manifest) == len(manifest) + batch_size

    additions, card_tables = template.extract_card_fields(cards)
    name_fields = sum(len(target["name_rows"]) for target in TARGETS)
    assert card_tables == batch_size and len(additions) == name_fields and all(row.get("evidence_status") == "source_backed" for row in additions)
    enrichment_text = ENRICHMENT.read_text(encoding="utf-8-sig")
    existing = [json.loads(line) for line in enrichment_text.splitlines() if line.strip()]
    natural_keys = {(row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id", "")) for row in existing}
    existing_ids = {row.get("enrichment_id", "") for row in existing}
    max_id = max((int(match.group(1)) for value in existing_ids if (match := re.fullmatch(r"enr-(\d+)", value))), default=0)
    for i, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id+i:05d}"
        assert (row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id", "")) not in natural_keys
        assert row["enrichment_id"] not in existing_ids
    planned_enrichment = enrichment_text.rstrip("\n") + "\n" + "\n".join(json.dumps(row, ensure_ascii=False) for row in additions) + "\n"

    process_text = template.helper.base.process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3复核与S4人物直接端点登记：O索引组（{DATE}）\n\n"
    for target in TARGETS:
        process_text += f"- {target['primary']}（{target['group']}）→ [{target['name_zh']}（{target['name_en']}）](../../../04-knowledge/{target['ku']}.md)。索引{target['entry']}（页码{target['pages']}）与对应书内页段支持source-local人物登记；直接S2关系候选{', '.join(target['relations'])}留待S6逐条裁决，不登记正式关系。\n"
    process_text += (
        f"本批S4登记{batch_size}个S3 new人物组、{batch_size}条候选映射和{name_fields}条source_backed名称字段；"
        f"{sum(len(target['relations']) for target in TARGETS)}条直接S2关系候选留待S6。"
        "人物身份按索引及本书正文建立，不据姓氏相似补并外部人物；未决的匿名人物、拟议建筑师及作品端点保持原状态。"
        "本批未新增外部身份行、正式关系、来源登记或S2断言。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S3复核与S4人物直接端点登记：O索引组（{DATE}）\n\n"
        f"登记Roberto Oderisi、Livio Odescalchi、Pietro Paolo Olivieri、Gilles-Marie Oppenord、Alessandro Orsini与William Young Ottley六个人物组；"
        f"本批{batch_size}条new候选映射、{name_fields}条source_backed名称字段及{sum(len(target['relations']) for target in TARGETS)}条直接S2关系候选。"
        f"关系均留待S6，未新增正式边；中文显示名均为工作音译。KU={len(planned_manifest)}；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-o-section-persons-") as td:
        temp = Path(td)
        alignment_stage, manifest_stage = temp / "alignment.csv", temp / "ku-manifest.csv"
        sync.write_csv(alignment_stage, alignment_fields, planned_alignments)
        sync.write_csv(manifest_stage, manifest_fields, planned_manifest)
        writes = {
            ALIGNMENT: alignment_stage.read_bytes(), MANIFEST: manifest_stage.read_bytes(),
            ENRICHMENT: template.with_bom(planned_enrichment, ENRICHMENT.read_bytes()),
            ACCEPTED: template.with_bom("\n".join(planned_accepted) + "\n", ACCEPTED.read_bytes()),
            PROCESS: template.with_bom(process_text + "\n", PROCESS.read_bytes()),
            RESULT: template.with_bom(result_text + "\n", RESULT.read_bytes()),
        }
        for target in TARGETS:
            writes[ROOT / target["card"]] = template.with_bom(cards[target["card"]])

    if args.dry_run:
        relation_count = sum(len(target["relations"]) for target in TARGETS) + len(CORRECTIONS)
        print(f"S4 dry-run passed: new_groups={batch_size}; new_candidate_mappings={batch_size}; s3_same_corrections={len(CORRECTIONS)}; name_fields={name_fields}; direct_relation_candidates={relation_count}.")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; KU={len(planned_manifest)}")
        print("formal_relations_added=0; candidate_backlog_changed=0; sources_registry_changed=0; no files changed")
        return 0

    originals = {path: path.read_bytes() if path.exists() else None for path in writes}
    try:
        for path, content in writes.items():
            template.atomic_write(path, content)
    except Exception:
        for path, content in originals.items():
            if content is None:
                if path.exists():
                    path.unlink()
            else:
                template.atomic_write(path, content)
        raise
    print(f"applied: new_groups={batch_size}; new_candidate_mappings={batch_size}; s3_same_corrections={corrections_to_apply}; name_fields={name_fields}; relation_candidates={sum(len(target['relations']) for target in TARGETS) + len(CORRECTIONS)}; KU={len(planned_manifest)}; formal_relations_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
