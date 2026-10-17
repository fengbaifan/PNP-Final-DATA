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
ANCHOR = "s4-person-direct-endpoints-p-early-section-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"


def src(location: str, summary: str, quote: str, file: str, span: str) -> dict:
    return {"location": location, "summary": summary, "quote": quote, "file": file, "span": span}


TARGETS = [{'primary': 'cand-1813',
  'members': ['cand-1813'],
  'expected_name': "Paltronieri, Pietro ('il Mirandolese')",
  'expected_pages': '289n',
  'group': 'new-person:il-mirandolese-paltronieri-pietro-0e77ff1415',
  'ku': 'units/persons/pietro-paltronieri',
  'card': '04-knowledge/units/persons/pietro-paltronieri.md',
  'name_zh': '彼得罗·帕尔特罗涅里',
  'name_en': 'Pietro Paltronieri (il Mirandolese)',
  'name_rows': [['索引名', "Paltronieri, Pietro ('il Mirandolese')", 'S1（索引P.csv#12）'],
                ['正文姓氏形式', 'Paltronieri', 'S2（第10章p.289注1）']],
  'sources': [{'location': '第10章导论；印刷页289注1',
               'summary': 'Haskell称Paltronieri为Bolognese画家，并转述Anthony Blunt指出拍卖目录中的Petoni异写。',
               'quote': 'Paltronieri was a Bolognese painter.',
               'file': '02-sources/02-Markdown/10_CHP-10_intro.md',
               'span': 'line 234; print p.289 n.1'},
              {'location': '第10章导论注表转录；印刷页289注1',
               'summary': '表格将Paltronieri列于Lord Dorset纪念碑项目的艺术家栏。',
               'quote': '| Paltronieri; Cimaroli; Pittoni | Lord Dorset | Rome, private collection |',
               'file': '02-sources/02-Markdown/10_CHP-10_intro_notes_p289_visual-transcription.md',
               'span': 'table row 6; print p.289 n.1'}],
  'zh': '按索引P.csv#12所列Pietro Paltronieri及别称il '
        'Mirandolese，与第10章p.289注1的姓氏形式Paltronieri登记为书内同一人物组（中文显示名为工作音译）。Haskell称其为Bolognese画家，并记述Anthony '
        'Blunt曾指出拍卖目录中出现Petoni这一异写；本卡不把该转述扩展为独立身份核验。',
  'en': 'Groups the indexed Pietro Paltronieri (il Mirandolese) in P.csv#12 with the surname form in chapter 10, p.289 '
        'n.1, as one source-local person. Haskell calls him a Bolognese painter and reports Anthony Blunt’s '
        'observation of the sale-catalogue form Petoni; this is not treated as independent identity verification.',
  'context_zh': '表格端点cand-9392是Lord Dorset纪念碑项目的未决作品组；表格只列艺术家与题目，未界定Paltronieri的创作、执行或委托角色。',
  'context_en': 'Table endpoint cand-9392 is an undecided work group for the Lord Dorset monument project. The table '
                'lists artists and subject but does not define Paltronieri’s creative, execution, or commission role.',
  'relations': ['st-chp10-p289-note1-paltronieri-bolognese', 'st-chp10-p289-note1-row06-artist1'],
  'endpoints': {'st-chp10-p289-note1-paltronieri-bolognese': 'described_as_bolognese_painter',
                'st-chp10-p289-note1-row06-artist1': 'artist_listed_as_concerned_in_enterprise_for_monument_subject'},
  's3_note': 'S3 group qualification (2026-10-18): index full name and epithet anchor the person; chapter text uses '
             'surname Paltronieri. The book reports a sale-catalogue spelling Petoni through Anthony Blunt but does '
             'not independently verify that variant.'},
 {'primary': 'cand-1825',
  'members': ['cand-1825'],
  'expected_name': 'Panciatichi, Senator Francesco',
  'expected_pages': '212n',
  'group': 'new-person:francesco-panciatichi-senator-bf360bf677',
  'ku': 'units/persons/francesco-panciatichi',
  'card': '04-knowledge/units/persons/francesco-panciatichi.md',
  'name_zh': '弗朗切斯科·潘恰蒂基',
  'name_en': 'Senator Francesco Panciatichi',
  'name_rows': [['索引名', 'Panciatichi, Senator Francesco', 'S1（索引P.csv#24）'],
                ['正文姓名形式', 'Senator Francesco Panciatichi', 'S2（第8章第I节p.212注5）']],
  'sources': [{'location': '第8章第I节；印刷页212注5',
               'summary': 'Haskell称Francesco Panciatichi自1682年任Primo Segretario，并称他是Nicola del Rosso的岳父。',
               'quote': 'Senator Francesco Panciatichi, who from 1682 held the important post of Primo Segretario, was '
                        'the father-in-law of Nicola del Rosso, the fourth brother.',
               'file': '02-sources/02-Markdown/08_CHP-8_sec_i.md',
               'span': 'line 153; print p.212 n.5'}],
  'zh': '按索引P.csv#24及第8章p.212注5登记Senator Francesco Panciatichi（中文显示名为工作音译）。Haskell称他自1682年起任Primo '
        'Segretario，并称他是Nicola del Rosso的岳父；书内引述和关系仍按原文归属记录。',
  'en': 'Registers Senator Francesco Panciatichi under index P.csv#24 and chapter 8, p.212 n.5; the Chinese display '
        'name is a working transliteration. Haskell says he held the Primo Segretario office from 1682 and was Nicola '
        'del Rosso’s father-in-law; the account remains attributed to the book.',
  'context_zh': '亲属候选另一端cand-7611映射到Nicola del Rosso人物KU；职务端点cand-12349仍是未登记的新组。两条关系均留待S6。',
  'context_en': 'The other endpoint cand-7611 of the kinship candidate maps to Nicola del Rosso’s person KU. Office '
                'endpoint cand-12349 remains an unregistered new group. Both relations remain for S6.',
  'relations': ['st-chp8-p212-n5-panciatichi-nicola-kinship', 'st-chp8-p212-n5-panciatichi-office'],
  'endpoints': {'st-chp8-p212-n5-panciatichi-nicola-kinship': 'panciatichi_was_father_in_law_of_nicola_del_rosso',
                'st-chp8-p212-n5-panciatichi-office': 'panciatichi_held_primo_segretario_from_1682'}},
 {'primary': 'cand-1841',
  'members': ['cand-1841'],
  'expected_name': 'Parodi, Domenico',
  'expected_pages': '200, 201',
  'group': 'new-person:antonio-domenico-parodi-domenico-parodi-741540edee',
  'ku': 'units/persons/domenico-antonio-parodi',
  'card': '04-knowledge/units/persons/domenico-antonio-parodi.md',
  'name_zh': '多梅尼科·安东尼奥·帕罗迪',
  'name_en': 'Domenico Antonio Parodi',
  'name_rows': [['索引名', 'Parodi, Domenico', 'S1（索引P.csv#41）'],
                ['正文姓名形式', 'Domenico Parodi', 'S2（第7章第V节p.200）'],
                ['正文全名形式', 'Domenico Antonio Parodi', 'S2（第7章第V节p.201）']],
  'sources': [{'location': '第7章第V节；印刷页200',
               'summary': 'Haskell称Admiral Pekemburgh委托雕塑家Domenico Parodi制作胸像，之后试图带他赴英但未成功。',
               'quote': 'ordered his bust from the sculptor Domenico Parodi whom he then tried in vain to take back '
                        'with him to England',
               'file': '02-sources/02-Markdown/07_CHP-7_sec_v.md',
               'span': 'line 11; print p.200'},
              {'location': '第7章第V节；印刷页201',
               'summary': 'Haskell称Domenico Antonio Parodi与Lorenzo Mattielli为Prince Eugene的厅堂和花园制作雕像。',
               'quote': 'Lorenzo Mattielli and Domenico Antonio Parodi made statues for the hall and gardens',
               'file': '02-sources/02-Markdown/07_CHP-7_sec_v.md',
               'span': 'line 50; print p.201'}],
  'zh': '将索引P.csv#41的Domenico Parodi与第7章p.201的全名Domenico Antonio '
        'Parodi按同一书内人物组登记；两处相邻叙述和索引页码相合，中文显示名为工作音译。p.200记述他为Admiral Pekemburgh制作胸像，p.201称他与Mattielli为Prince '
        'Eugene制作雕像；具体作品和未完成的带艺术家赴英尝试保持各自原文范围。',
  'en': 'Groups indexed Domenico Parodi in P.csv#41 with the fuller form Domenico Antonio Parodi on p.201 as one '
        'source-local person; the adjacent account and index pages align. Chapter 7 reports a bust commission from '
        'Admiral Pekemburgh and statues for Prince Eugene, while preserving the source’s limits on the works and the '
        'unsuccessful attempt to take him to England.',
  'context_zh': 'Pekemburgh端点cand-7285身份未决；雕像作品端点cand-7312未识别为具体作品。',
  'context_en': 'Endpoint cand-7285, Admiral Pekemburgh, remains unidentified; statue endpoint cand-7312 is not '
                'identified as a specific work.',
  'relations': ['st-chp7-p200-v-parodi-trip-to-england-failed',
                'st-chp7-p201-v-parodi-made-statues-for-hall-and-gardens'],
  'endpoints': {'st-chp7-p200-v-parodi-trip-to-england-failed': 'attempted_to_take_artist_to_england_unsuccessfully',
                'st-chp7-p201-v-parodi-made-statues-for-hall-and-gardens': 'made_statues_for_hall_and_gardens'}},
 {'primary': 'cand-1843',
  'members': ['cand-1843'],
  'expected_name': 'Pasinelli, Lorenzo',
  'expected_pages': '197',
  'group': 'new-person:lorenzo-pasinelli-901ba3712c',
  'ku': 'units/persons/lorenzo-pasinelli',
  'card': '04-knowledge/units/persons/lorenzo-pasinelli.md',
  'name_zh': '洛伦佐·帕西内利',
  'name_en': 'Lorenzo Pasinelli',
  'name_rows': [['索引名', 'Pasinelli, Lorenzo', 'S1（索引P.csv#43）'], ['正文姓名形式', 'Lorenzo Pasinelli', 'S2（第7章第IV节p.197）']],
  'sources': [{'location': '第7章第IV节；印刷页197',
               'summary': 'Haskell在Lord Exeter的收藏与委托叙述中，将Lorenzo Pasinelli列在Bologna项下。',
               'quote': 'In Venice he bought Liberis; in Bologna, Lorenzo Pasinelli;',
               'file': '02-sources/02-Markdown/07_CHP-7_sec_iv.md',
               'span': 'lines 73-74; print p.197'}],
  'zh': '登记索引P.csv#43的Lorenzo Pasinelli及第7章p.197正文姓名。该段在Lord '
        'Exeter于不同城市的绘画收藏叙述中，将Pasinelli列于Bologna；原文为省略式列表，本卡不把它改写成明确购买行为。',
  'en': 'Registers Lorenzo Pasinelli under index P.csv#43 and the name in chapter 7, p.197. The passage lists him '
        'under Bologna in an account of Lord Exeter’s collecting across cities; its elliptical wording is not '
        'converted into an explicit purchase claim.',
  'context_zh': '地点端点cand-0984映射到Lord Exeter人物KU；列表关系的具体动作仍须按S6复核。',
  'context_en': 'Place endpoint cand-0984 maps to Lord Exeter’s person KU; the precise action expressed by the list '
                'remains for S6 review.',
  'relations': ['st-chp7-p197-exeter-collected-pasinelli-bologna'],
  'endpoints': {'st-chp7-p197-exeter-collected-pasinelli-bologna': 'collector_artist_association_in_city'}},
 {'primary': 'cand-1853',
  'members': ['cand-1853'],
  'expected_name': 'Pasquetti, Leonardo',
  'expected_pages': '346',
  'group': 'new-person:hunchback-leonardo-pasquetti-leonardo-pasq-52e202de52',
  'ku': 'units/persons/leonardo-pasquetti',
  'card': '04-knowledge/units/persons/leonardo-pasquetti.md',
  'name_zh': '莱奥纳多·帕斯奎蒂',
  'name_en': 'Leonardo Pasquetti',
  'name_rows': [['索引名', 'Pasquetti, Leonardo', 'S1（索引P.csv#53）'],
                ['正文姓名与称谓', 'the hunchback Leonardo Pasquetti', 'S2（第13章导论p.346）']],
  'sources': [{'location': '第13章导论；印刷页346',
               'summary': 'Haskell称Toni会在Merceria摊位向驼背的Leonardo Pasquetti购买版画。',
               'quote': 'buy prints from the hunchback Leonardo Pasquetti',
               'file': '02-sources/02-Markdown/13_CHP-13_intro.md',
               'span': 'line 176; print p.346'}],
  'zh': '登记索引P.csv#53的Leonardo '
        'Pasquetti及第13章p.346的全名和称谓；中文显示名为工作音译。Haskell以习惯性叙述称Toni会去Merceria摊位向他买版画，没有给出单次交易、版画标题或具体数量。',
  'en': 'Registers Leonardo Pasquetti from index P.csv#53 with the full name and designation in chapter 13, p.346; the '
        'Chinese display name is a working transliteration. Haskell uses habitual wording for Toni’s visits to buy '
        'prints at a Merceria stall and gives no individual transaction, print title, or count.',
  'context_zh': '买方端点cand-2640映射到Pietro Antonio Toni人物KU；Merceria具体摊位仍未定位。',
  'context_en': 'Buyer endpoint cand-2640 maps to Pietro Antonio Toni’s person KU; the specific Merceria stall remains '
                'unidentified.',
  'relations': ['st-chp13-p346-toni-would-buy-prints-from-pasquetti'],
  'endpoints': {'st-chp13-p346-toni-would-buy-prints-from-pasquetti': 'would_buy_prints_from'}},
 {'primary': 'cand-1860',
  'members': ['cand-1860'],
  'expected_name': 'Pedozzi, Padre Jacopo',
  'expected_pages': '270',
  'group': 'new-person:jacopo-pedozzi-ba3154b82f',
  'ku': 'units/persons/jacopo-pedozzi',
  'card': '04-knowledge/units/persons/jacopo-pedozzi.md',
  'name_zh': '雅各布·佩多齐',
  'name_en': 'Padre Jacopo Pedozzi',
  'name_rows': [['索引名', 'Pedozzi, Padre Jacopo', 'S1（索引P.csv#61）'],
                ['正文姓名形式', 'Padre Jacopo Pedozzi', 'S2（第9章第II节p.270）']],
  'sources': [{'location': '第9章第II节；印刷页270',
               'summary': 'Haskell称Padre Jacopo Pedozzi为加尔默罗会秘书长、受威尼斯贵族敬重且为Canaletto早期赞助人之一。',
               'quote': 'Padre Jacopo Pedozzi, Secretary General of the Order and a man ‘very highly thought of, '
                        'especially by the Venetian nobikty’, who was one of the very first patrons of Canaletto.',
               'file': '02-sources/02-Markdown/09_CHP-9_sec_ii.md',
               'span': 'lines 32-34; print p.270'}],
  'zh': '登记索引P.csv#61的Padre Jacopo '
        'Pedozzi和第9章p.270的相同称谓。Haskell称他为加尔默罗会秘书长、受到威尼斯贵族高度敬重，并列为Canaletto最早的赞助人之一；这些均保留为本书叙述。',
  'en': 'Registers Padre Jacopo Pedozzi under index P.csv#61 and chapter 9, p.270. Haskell identifies him as Secretary '
        'General of the Carmelite Order, highly regarded by Venetian nobility, and among Canaletto’s earliest patrons; '
        'these remain the book’s account.',
  'context_zh': '关系候选另一端cand-0498映射到Canaletto人物KU；具体赞助行为与时间未在本段详述。',
  'context_en': 'The other endpoint cand-0498 maps to Canaletto’s person KU; this passage does not detail a specific '
                'act or date of patronage.',
  'relations': ['st-chp9-p270-pedozzi-reputation-and-canaletto-patron'],
  'endpoints': {'st-chp9-p270-pedozzi-reputation-and-canaletto-patron': 'carmelite_secretary_general_pedozzi_held_in_high_regard_by_venetian_nobility_was_among_canalettos_earliest_patrons'}},
 {'primary': 'cand-1899',
  'members': ['cand-1899'],
  'expected_name': 'Pian, Giovanni del',
  'expected_pages': '376',
  'group': 'new-person:del-giovanni-pian-f2cac6631e',
  'ku': 'units/persons/giovanni-del-pian',
  'card': '04-knowledge/units/persons/giovanni-del-pian.md',
  'name_zh': '乔瓦尼·德尔·皮安',
  'name_en': 'Giovanni del Pian',
  'name_rows': [['索引名', 'Pian, Giovanni del', 'S1（索引P.csv#100）'], ['正文姓名形式', 'Giovanni del Pian', 'S2（第16章导论p.376）']],
  'sources': [{'location': '第16章导论；印刷页376',
               'summary': 'Haskell称Toninotto于1785年负责出版Giovanni del Pian为Carpaccio场景所作的九幅大型版画。',
               'quote': 'In 1785 he was responsible for publishing a series of nine large prints by Giovanni del Pian '
                        'of Carpaccio’s famous scenes of the Life of St Ursula.',
               'file': '02-sources/02-Markdown/16_CHP-16_intro.md',
               'span': 'lines 43-44; print p.376'}],
  'zh': '登记索引P.csv#100的Giovanni del Pian及第16章p.376正文姓名。Haskell称Padre Giuseppe '
        'Toninotto于1785年负责出版他为Carpaccio《圣乌尔苏拉生平》场景所作的九幅大型版画；个别版画题名与版本未提供。',
  'en': 'Registers Giovanni del Pian under index P.csv#100 and the name in chapter 16, p.376. Haskell says Padre '
        'Giuseppe Toninotto was responsible in 1785 for publishing nine large prints by him after Carpaccio’s Life of '
        'St Ursula scenes; individual titles and editions are not supplied.',
  'context_zh': '作品端点cand-10636仍是未具个别题名的九幅版画组；出版与作者关系候选留待S6。',
  'context_en': 'Work endpoint cand-10636 remains an untitled group of nine prints; the publication and authorship '
                'relation candidate remains for S6.',
  'relations': ['st-chp16-p376-del-pian-maker-of-print-series'],
  'endpoints': {'st-chp16-p376-del-pian-maker-of-print-series': 'prints_by_giovanni_del_pian'}}]
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
    parser = argparse.ArgumentParser(description="Register seven new early P-section person groups.")
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
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3复核与S4人物直接端点登记：P索引前段组（{DATE}）\n\n"
    for target in TARGETS:
        process_text += f"- {target['primary']}（{target['group']}）→ [{target['name_zh']}（{target['name_en']}）](../../../04-knowledge/{target['ku']}.md)。索引{target['entry']}（页码{target['pages']}）与对应书内页段支持source-local人物登记；直接S2关系候选{', '.join(target['relations'])}留待S6逐条裁决，不登记正式关系。\n"
    process_text += (
        f"本批S4登记{batch_size}个S3 new人物组、{batch_size}条候选映射和{name_fields}条source_backed名称字段；"
        f"{sum(len(target['relations']) for target in TARGETS)}条直接S2关系候选留待S6。"
        "跨页姓名形式按本书索引及对应正文定位归组；Paltronieri的Petoni为Haskell转述的拍卖目录异写，未当作独立核验。"
        "未决的海军将领、纪念碑项目、职务或版画组端点保持原状态；本批未新增外部身份行、正式关系、来源登记或S2断言。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S3复核与S4人物直接端点登记：P索引前段组（{DATE}）\n\n"
        f"登记Pietro Paltronieri、Senator Francesco Panciatichi、Domenico Antonio Parodi、Lorenzo Pasinelli、Leonardo Pasquetti、Padre Jacopo Pedozzi与Giovanni del Pian七个人物组；"
        f"本批{batch_size}条new候选映射、{name_fields}条source_backed名称字段及{sum(len(target['relations']) for target in TARGETS)}条直接S2关系候选。"
        f"关系均留待S6，未新增正式边；中文显示名均为工作音译。KU={len(planned_manifest)}；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-p-early-section-persons-") as td:
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
