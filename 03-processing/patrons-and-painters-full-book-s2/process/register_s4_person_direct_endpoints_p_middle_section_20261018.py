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
ANCHOR = "s4-person-direct-endpoints-p-middle-section-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"


def src(location: str, summary: str, quote: str, file: str, span: str) -> dict:
    return {"location": location, "summary": summary, "quote": quote, "file": file, "span": span}


TARGETS = [{'primary': 'cand-1925',
  'members': ['cand-1925'],
  'expected_name': 'Picart, Bernard',
  'expected_pages': '370',
  'group': 'new-person:bernard-picart-ecea5d104f',
  'ku': 'units/persons/bernard-picart',
  'card': '04-knowledge/units/persons/bernard-picart.md',
  'name_zh': '贝尔纳·皮卡尔',
  'name_en': 'Bernard Picart',
  'name_rows': [['索引名', 'Picart, Bernard', 'S1（索引P.csv#126）'], ['正文姓氏形式', 'Picart', 'S2（第15章第II节p.370）']],
  'sources': [{'location': '第15章第II节；印刷页370',
               'summary': 'Haskell称Querini书房有Picart所作的东方风俗版画。',
               'quote': 'engravings by Picart of oriental customs',
               'file': '02-sources/02-Markdown/15_CHP-15_sec_ii.md',
               'span': 'line 62; print p.370'}],
  'zh': '登记索引P.csv#126的Bernard '
        'Picart及第15章p.370的姓氏形式Picart（中文显示名为工作音译）。Haskell将Picart版画描述为Querini书房墙面的东方风俗版画；个别版画标题与版本未列明。',
  'en': 'Registers Bernard Picart under index P.csv#126 and the surname form in chapter 15, p.370; the Chinese display '
        'name is a working transliteration. Haskell describes Picart’s engravings as depictions of oriental customs '
        'lining Querini’s study; individual print titles and editions are not specified.',
  'context_zh': '作品端点cand-10546仍是身份与粒度未决的版画集合，不据文字建立具体版画组。',
  'context_en': 'Work endpoint cand-10546 remains an undecided group of engravings; no specific print group is '
                'inferred from the wording.',
  'relations': ['st-chp15-p370-picart-engravings-created-by-picart'],
  'endpoints': {'st-chp15-p370-picart-engravings-created-by-picart': 'created_by'}},
 {'primary': 'cand-1929',
  'members': ['cand-1929'],
  'expected_name': 'Pignatelli, Antonio (Pope Innocent XII)',
  'expected_pages': '221, 222',
  'group': 'new-person:antonio-pignatelli-innocent-xii-96ebb8305a',
  'ku': 'units/persons/antonio-pignatelli-innocent-xii',
  'card': '04-knowledge/units/persons/antonio-pignatelli-innocent-xii.md',
  'name_zh': '安东尼奥·皮尼亚泰利（教宗英诺森十二世）',
  'name_en': 'Antonio Pignatelli (Pope Innocent XII)',
  'name_rows': [['索引名', 'Pignatelli, Antonio (Pope Innocent XII)', 'S1（索引P.csv#130）'],
                ['正文教宗称谓', 'Pope Innocent XII', 'S2（第8章第II节p.221）'],
                ['正文简称', 'Innocent XII', 'S2（第8章第II节p.222）']],
  'sources': [{'location': '第8章第II节；印刷页221',
               'summary': 'Haskell称Cardinal Tommaso Ruffo于1692年由Pope Innocent XII任命为Ravenna副使节。',
               'quote': 'in 1692 was made Vice-Legate in Ravenna by Pope Innocent XII.',
               'file': '02-sources/02-Markdown/08_CHP-8_sec_ii.md',
               'span': 'lines 116-117; print p.221'},
              {'location': '第8章第II节；印刷页222',
               'summary': 'Haskell称Ruffo的阶梯装饰中有一枚纪念Innocent XII的教宗浮雕章，并称其为Ruffo的 patron。',
               'quote': 'culminating in Innocent XII, Russo’s own patron.',
               'file': '02-sources/02-Markdown/08_CHP-8_sec_ii.md',
               'span': 'lines 126-128; print p.222'}],
  'zh': '将索引P.csv#130的Antonio Pignatelli（Pope Innocent XII）与第8章p.221、222的Innocent '
        'XII称谓登记为同一书内人物组；中文显示名为工作音译。书内两处称谓与同一索引条目互相对应；不据此补充教宗任期、生平或外部标识。',
  'en': 'Groups Antonio Pignatelli (Pope Innocent XII) in index P.csv#130 with the Innocent XII forms on pp.221–222 as '
        'one source-local person; the Chinese display name is a working transliteration. The book’s two forms align '
        'with the same index entry; no reign, biography, or external identifier is added.',
  'context_zh': '两条关系候选的另一端cand-2304映射到Tommaso Ruffo人物KU；本组与既有Innocent XIII人物卡分立。',
  'context_en': 'The other endpoint cand-2304 of both relation candidates maps to Tommaso Ruffo’s person KU. This '
                'group remains distinct from the existing Innocent XIII person card.',
  'relations': ['st-chp8-p221-innocent-xii-appoints-vice-legate', 'st-chp8-p222-innocent-xii-patron-of-ruffo'],
  'endpoints': {'st-chp8-p221-innocent-xii-appoints-vice-legate': 'appointed_vice_legate_in_ravenna',
                'st-chp8-p222-innocent-xii-patron-of-ruffo': 'served_as_patron_of'},
  's3_note': 'S3 group basis (2026-10-18): the index itself combines Antonio Pignatelli with Pope Innocent XII and '
             'locates the two Innocent XII narrative forms on pp.221–222. No Innocent XII KU exists; the existing '
             'Innocent XIII KU is a different indexed person.'},
 {'primary': 'cand-1930',
  'members': ['cand-1930'],
  'expected_name': 'Pilati, Carlo Antonio',
  'expected_pages': '318, 336',
  'group': 'new-person:antonio-carlo-pilati-e89a18d7a3',
  'ku': 'units/persons/carlo-antonio-pilati',
  'card': '04-knowledge/units/persons/carlo-antonio-pilati.md',
  'name_zh': '卡洛·安东尼奥·皮拉蒂',
  'name_en': 'Carlo Antonio Pilati',
  'name_rows': [['索引名', 'Pilati, Carlo Antonio', 'S1（索引P.csv#131）'],
                ['正文姓名形式（第10章p.318）', 'Carlo Antonio Pilati', 'S2（第10章第II节p.318）'],
                ['正文姓名形式（第13章p.336）', 'Carlo Antonio Pilati', 'S2（第13章导论p.336）']],
  'sources': [{'location': '第10章第II节；印刷页318',
               'summary': 'Haskell将Carlo Antonio Pilati列入被逐出威尼斯领土的非正统思想者。',
               'quote': 'Pietro Giannone, Carlo Antonio Pilati, Giuseppe Baretti and other unorthodox thinkers were '
                        'rapidly expelled from her territory.',
               'file': '02-sources/02-Markdown/10_CHP-10_sec_ii.md',
               'span': 'lines 139-140; print p.318'},
              {'location': '第13章导论；印刷页336',
               'summary': 'Haskell称Carlo Antonio Pilati是Pasquali非从众朋友之一。',
               'quote': 'the friend of non-conforming spirits, such as Angelo Querini, Carlo Antonio Pilati and '
                        'Francesco Albergati-Capacelli.',
               'file': '02-sources/02-Markdown/13_CHP-13_intro.md',
               'span': 'lines 49-50; print p.336'}],
  'zh': '将索引P.csv#131及第10章p.318、第13章p.336的Carlo Antonio '
        'Pilati登记为同一书内人物组，两个正文锚点使用相同全名。Haskell分别记述其被逐出威尼斯领土，以及将其列入Pasquali所说的非从众朋友之中。',
  'en': 'Registers Carlo Antonio Pilati under index P.csv#131 and the matching full-name forms in chapters 10 and 13 '
        'as one source-local identity group. Haskell separately reports his expulsion from Venetian territory and '
        'lists him among Pasquali’s non-conforming friends.',
  'context_zh': '逐出事件的政治实体端点cand-8838映射既有威尼斯共和国机构KU；朋友候选的另一端cand-1844映射Giambattista Pasquali人物KU。',
  'context_en': 'The political-entity endpoint cand-8838 of the expulsion candidate maps to the existing Republic of '
                'Venice institution KU. The other endpoint cand-1844 of the friendship candidate maps to Giambattista '
                'Pasquali’s person KU.',
  'relations': ['st-chp10-p318-pilati-expelled-from-venetian-territory', 'st-chp13-p336-pasquali-friend-of-pilati'],
  'endpoints': {'st-chp10-p318-pilati-expelled-from-venetian-territory': 'expelled_from_territory',
                'st-chp13-p336-pasquali-friend-of-pilati': 'friend_of_nonconforming_spirit'}},
 {'primary': 'cand-1931',
  'members': ['cand-1931'],
  'expected_name': 'Pinacci, Giuseppe',
  'expected_pages': '191, 233n',
  'group': 'new-person:giuseppe-pinacci-5cb62bbf30',
  'ku': 'units/persons/giuseppe-pinacci',
  'card': '04-knowledge/units/persons/giuseppe-pinacci.md',
  'name_zh': '朱塞佩·皮纳奇',
  'name_en': 'Giuseppe Pinacci',
  'name_rows': [['索引名', 'Pinacci, Giuseppe', 'S1（索引P.csv#132）'],
                ['正文姓名形式', 'Giuseppe Pinacci', 'S2（第7章第I节p.191）'],
                ['正文同名形式（索引所指p.233n）', 'Giuseppe Pinacci', 'S1索引定位及第8章第II节p.233注8']],
  'sources': [{'location': '第7章第I节；印刷页191',
               'summary': 'Haskell称Giuseppe Pinacci是Del Carpio藏画的受托管理者，并称他为熟练修复者。',
               'quote': 'putting in charge of them an obscure Sienese painter, Giuseppe Pinacci, who proved to be an '
                        'expert restorer.',
               'file': '02-sources/02-Markdown/07_CHP-7_sec_i.md',
               'span': 'lines 274-275; print p.191'},
              {'location': '第8章第II节注释；印刷页233注8',
               'summary': 'Haskell列举Giuseppe Pinacci等佛罗伦萨画家，并指向Abate Orazio Martini。',
               'quote': 'for Francesco Botti, Giuseppe Pinacci, Romolo Panfi, Cristofano Monari, etc., see Abate '
                        'Orazio Martini.',
               'file': '02-sources/02-Markdown/08_CHP-8_sec_ii.md',
               'span': 'line 420; print p.233 n.8'}],
  'zh': '将索引P.csv#132的Giuseppe Pinacci与第7章p.191及索引所指第8章p.233注8中相同姓名按书内人物组登记；中文显示名为工作音译。p.191称他为Sienese '
        'painter和熟练修复者；p.233注8仅列其姓名并指向Abate Orazio Martini，不据此增加作品、任职或修复事实。',
  'en': 'Groups the indexed Giuseppe Pinacci in P.csv#132 with the same name on chapter 7, p.191, and in the indexed '
        'chapter 8, p.233 n.8; the Chinese display name is a working transliteration. Chapter 7 calls him a Sienese '
        'painter and skilled restorer. The p.233 note only lists his name and points to Abate Orazio Martini; no work, '
        'office, or restoration fact is added from it.',
  'context_zh': '修复职责候选的对象cand-6965仍未分类且未决；本批不据此把收藏集合登记为某一类型。第8章注8的人名未单独进入本候选的S2 mention列表，不据该处创建新关系断言。',
  'context_en': 'Object cand-6965 of the collection-responsibility candidate remains untyped and undecided; this batch '
                'does not assign it a KU type. The p.233 n.8 name does not create a separate S2 mention or relation '
                'assertion here.',
  'relations': ['st-chp7-p191-i22'],
  'endpoints': {'st-chp7-p191-i22': 'in_charge_of'},
  's3_note': 'S3 cross-chapter grouping (2026-10-18): index P.csv#132 locates the same full name at p.191 and p.233 '
             'n.; the later note repeats the name but supplies only a reference to Abate Orazio Martini. No second '
             'relation or external match is inferred.'},
 {'primary': 'cand-1937',
  'members': ['cand-1937'],
  'expected_name': 'Piranesi, Francesco',
  'expected_pages': '366',
  'group': 'new-person:francesco-piranesi-42d51ce564',
  'ku': 'units/persons/francesco-piranesi',
  'card': '04-knowledge/units/persons/francesco-piranesi.md',
  'name_zh': '弗朗切斯科·皮拉内西',
  'name_en': 'Francesco Piranesi',
  'name_rows': [['索引名', 'Piranesi, Francesco', 'S1（索引P.csv#138）'],
                ['正文姓名形式', 'Francesco Piranesi', 'S2（第15章第II节p.366）']],
  'sources': [{'location': '第15章第II节；印刷页366',
               'summary': 'Haskell称Francesco Piranesi于1786年为Subleyras画稿制作版画。',
               'quote': 'Then Francesco Piranesi engraved Subleyras’s drawing',
               'file': '02-sources/02-Markdown/15_CHP-15_sec_ii.md',
               'span': 'line 22; print p.366'}],
  'zh': '登记索引P.csv#138的Francesco Piranesi及第15章p.366正文全名；中文显示名为工作音译。书中称他于1786年为Subleyras的一幅画稿制作版画。该人不同于既有Giovanni '
        'Battista Piranesi人物KU，不因姓氏相同而合并。',
  'en': 'Registers Francesco Piranesi under index P.csv#138 and the full name in chapter 15, p.366; the Chinese '
        'display name is a working transliteration. The book says he engraved a drawing by Subleyras in 1786. He '
        'remains distinct from the existing Giovanni Battista Piranesi KU; the shared surname does not merge them.',
  'context_zh': '版画端点cand-10495已有独立work new组但尚未登记；正文将画稿与版画区分。既有[Giovanni Battista '
                'Piranesi](giovanni-battista-piranesi.md)卡明确为另一人。',
  'context_en': 'Engraving endpoint cand-10495 is a separate new work group not yet registered; the passage '
                'distinguishes the drawing from the engraving. The existing [Giovanni Battista '
                'Piranesi](giovanni-battista-piranesi.md) card identifies a different person.',
  'relations': ['st-chp15-p366-piranesi-engraves-subleyras-drawing'],
  'endpoints': {'st-chp15-p366-piranesi-engraves-subleyras-drawing': 'piranesi_engraved_subleyras_drawing'},
  's3_note': 'S3 distinction (2026-10-18): Francesco Piranesi is retained as a new source-local identity group '
             'distinct from existing Giovanni Battista Piranesi; the source gives a full personal name and a separate '
             'index entry.'},
 {'primary': 'cand-1969',
  'members': ['cand-1969'],
  'expected_name': 'Pöllnitz, Baron de',
  'expected_pages': '283',
  'group': 'new-person:baron-de-pollnitz-745cce1347',
  'ku': 'units/persons/baron-de-pollnitz',
  'card': '04-knowledge/units/persons/baron-de-pollnitz.md',
  'name_zh': '波尔尼茨男爵',
  'name_en': 'Baron de Pöllnitz',
  'name_rows': [['索引名', 'Pöllnitz, Baron de', 'S1（索引P.csv#170）'],
                ['正文称谓', 'the Baron de Pöllnitz', 'S2（第10章导论p.283）'],
                ['注释姓名形式', 'Pöllnitz', 'S1索引定位及第10章导论p.283注1']],
  'sources': [{'location': '第10章导论；印刷页283',
               'summary': 'Haskell称Baron de Pöllnitz在Johann Wilhelm死后约十六年经过Palatinate，并描述其成就。',
               'quote': 'the Baron de Pöllnitz passed through the Palatinate and described the achievements of this',
               'file': '02-sources/02-Markdown/10_CHP-10_intro.md',
               'span': 'line 156; print p.283'},
              {'location': '第10章导论注释；印刷页283注1',
               'summary': '脚注以Pöllnitz和卷页定位所引材料。',
               'quote': 'Pöllnitz, III, p. 274.',
               'file': '02-sources/02-Markdown/10_CHP-10_intro.md',
               'span': 'line 523; print p.283 n.1'}],
  'zh': '按索引P.csv#170登记书中称为Baron de Pöllnitz的人物组（中文显示名为工作音译）。正文没有给出名字；注1仅列Pöllnitz书目卷页。本卡保留书内称谓，不匹配到某一外部个人。',
  'en': 'Registers the person called Baron de Pöllnitz in index P.csv#170; the Chinese display name is a working '
        'transliteration. The passage supplies no given name, and note 1 gives only a Pöllnitz volume/page reference. '
        'The card preserves the source designation without matching an external individual.',
  'context_zh': '关系候选另一端cand-1325映射Johann Wilhelm, Elector Palatinate人物KU；描述仍为Pöllnitz对Elector的转述评价。',
  'context_en': 'The other endpoint cand-1325 maps to Johann Wilhelm, Elector Palatinate’s person KU; the statement '
                'remains Pöllnitz’s reported description of the Elector.',
  'relations': ['st-chp10-p283-pollnitz-praise'],
  'endpoints': {'st-chp10-p283-pollnitz-praise': 'pollnitz_described_wilhelms_achievements_and_praised_his_rule'},
  's3_note': 'S3 correction (2026-10-18): withdraw the prior statement that the source gives a full personal name. '
             'Index and text provide a title-and-surname designation only; the new group is source-local, with no '
             'given name or external individual match.'},
 {'primary': 'cand-1973',
  'members': ['cand-1973'],
  'expected_name': 'Poore, Edward',
  'expected_pages': '374',
  'group': 'new-person:edward-poore-f2d0623bd5',
  'ku': 'units/persons/edward-poore',
  'card': '04-knowledge/units/persons/edward-poore.md',
  'name_zh': '爱德华·普尔',
  'name_en': 'Edward Poore',
  'name_rows': [['索引名', 'Poore, Edward', 'S1（索引P.csv#175）'],
                ['正文称谓', 'Mr Poore', 'S2（第16章导论p.374）'],
                ['注释姓名形式', 'an Edward Poore', 'S2（第16章导论p.374注3）']],
  'sources': [{'location': '第16章导论；印刷页374',
               'summary': 'Haskell称画商G. A. Armanni写信讥讽一位英国访客Mr Poore。',
               'quote': 'wrote derisively of an English visitor Mr Poore:',
               'file': '02-sources/02-Markdown/16_CHP-16_intro.md',
               'span': 'line 21; print p.374'},
              {'location': '第16章导论注释；印刷页374注3',
               'summary': '注3说Mr Poore出现在1789年书信中，并称1805年拍卖出售了属于an Edward Poore的版画与素描。',
               'quote': 'Mr Poore is discussed in a letter of 7 July 1789. In two auctions—4 and 19 April 1805 '
                        '(Richardson)—prints and drawings belonging to an Edward Poore were sold, but there is no '
                        'reference to any Tiepolo among them.',
               'file': '02-sources/02-Markdown/16_CHP-16_intro.md',
               'span': 'line 74; print p.374 n.3'}],
  'zh': '按索引P.csv#175将第16章p.374的Mr Poore与注3所列Edward Poore保留为书内source-local人物组。正文称他为英国访客；注3称该人见于1789年书信，并另报1805年拍卖中有“an '
        'Edward Poore”的版画与素描售出。脚注没有明确证明拍卖藏家与来访者为同一外部个人，目录亦未独立核阅。',
  'en': 'Following index P.csv#175, the chapter 16, p.374 form Mr Poore and Edward Poore in note 3 are retained as one '
        'source-local person group. The narrative calls him an English visitor; note 3 says he appears in a 1789 '
        'letter and separately reports prints and drawings belonging to “an Edward Poore” sold in 1805. The note does '
        'not independently establish that the auction owner and visitor were the same external individual, and the '
        'catalogues were not consulted.',
  'context_zh': '候选另一端cand-0119（G. A. Armanni）仍待证；书信档案端点cand-10615与拍卖事件端点cand-10616各有独立new组、均未登记。本批不将信件与拍卖合并为同一记录。',
  'context_en': 'Other endpoint cand-0119 (G. A. Armanni) remains undecided. Letter archive endpoint cand-10615 and '
                'auction event endpoint cand-10616 are separate new groups, both unregistered; this batch does not '
                'merge the letter and auction into one record.',
  'relations': ['st-chp16-p374-armanni-introduces-poore',
                'st-chp16-p374-note3-poore-letter-locator',
                'st-chp16-p374-note3-poore-auction-sales'],
  'endpoints': {'st-chp16-p374-armanni-introduces-poore': 'armanni_wrote_derisively_of_english_visitor_mr_poore',
                'st-chp16-p374-note3-poore-letter-locator': 'note_says_poore_discussed_in_letter_dated_7_july_1789',
                'st-chp16-p374-note3-poore-auction-sales': 'note_reports_poore_print_and_drawing_sales_without_tiepolo'}},
 {'primary': 'cand-1976',
  'members': ['cand-1976'],
  'expected_name': 'Porta, Giacomo della',
  'expected_pages': '71, 91',
  'group': 'new-person:della-giacomo-porta-b53d418aa4',
  'ku': 'units/persons/giacomo-della-porta',
  'card': '04-knowledge/units/persons/giacomo-della-porta.md',
  'name_zh': '贾科莫·德拉·波尔塔',
  'name_en': 'Giacomo della Porta',
  'name_rows': [['索引名', 'Porta, Giacomo della', 'S1（索引P.csv#178）'],
                ['正文姓名形式', 'Giacomo della Porta', 'S2（第3章第II节p.71）'],
                ['正文简称', 'della Porta', 'S2（第3章第IV节p.91）']],
  'sources': [{'location': '第3章第II节；印刷页71',
               'summary': 'Haskell称Giacomo della Porta先于Pietro Paolo Olivieri，对Theatines提议的建筑师拥有完整决定权。',
               'quote': 'Giacomo della Porta and then Pietro Paolo Olivieri, should have complete authority over the '
                        'man whom the Theatines themselves had proposed for the commission.',
               'file': '02-sources/02-Markdown/03_CHP-3_sec_ii.md',
               'span': 'line 69; print p.71'},
              {'location': '第3章第IV节；印刷页91',
               'summary': 'Haskell称Giacomo della Porta设计的Ignatius礼拜堂祭坛从未完成。',
               'quote': 'the altar had been designed but never completed by Giacomo della Porta',
               'file': '02-sources/02-Markdown/03_CHP-3_sec_iv.md',
               'span': 'line 156; print p.91'}],
  'zh': '将索引P.csv#178的Giacomo della '
        'Porta与第3章p.71、91正文姓名形式按同一书内人物组登记。Haskell称他先于Olivieri获得对Theatines所提议建筑师的决定权，并称他设计的Ignatius礼拜堂祭坛最终未完成。两处陈述与具体关系留待S6。',
  'en': 'Groups Giacomo della Porta under index P.csv#178 with the matching name forms on chapter 3, pp.71 and 91. '
        'Haskell says he preceded Olivieri in authority over the Theatines’ proposed architect and that his designed '
        'altar for the Ignatius chapel was never completed. Both statements remain relation candidates for S6.',
  'context_zh': '对象cand-5063仍是未具名的Theatines提议人；祭坛作品端点cand-11624是独立new work组、尚未登记。候选另端包含已登记的Pietro Paolo Olivieri人物。',
  'context_en': 'Object cand-5063 remains the unnamed person proposed by the Theatines; altar endpoint cand-11624 is a '
                'separate new work group not yet registered. The other candidate subject includes the registered '
                'person Pietro Paolo Olivieri.',
  'relations': ['st-chp3-secii-l62-72-gesualdo-appointed-own-architects',
                'st-chp3-seciv-l152-163-della-porta-designed-uncompleted-altar'],
  'endpoints': {'st-chp3-secii-l62-72-gesualdo-appointed-own-architects': 'had_complete_authority_over_theatines_proposed_commissionee',
                'st-chp3-seciv-l152-163-della-porta-designed-uncompleted-altar': 'designed_altar_for_left_transept_chapel'}}]
CORRECTIONS = []
POLLNITZ_OLD_1 = "source anchor gives a full personal name."
POLLNITZ_OLD_2 = "Grouped with cand-1969 by identical normalized full-name/explicit-alias anchor (baron de pollnitz), not surname-only similarity."
POLLNITZ_NEW_1 = "source anchor identifies a person by the title-and-surname designation Baron de Pöllnitz; no given name is supplied."
POLLNITZ_NEW_2 = "Grouped with cand-1969 by the same indexed and in-text title-and-surname designation; no external person match is asserted."


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
    parser = argparse.ArgumentParser(description="Register eight new middle P-section person groups.")
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
        if target["primary"] == "cand-1969":
            assert target["s3_note"] in row.get("resolution_note", "") or (POLLNITZ_OLD_1 in row.get("resolution_note", "") and POLLNITZ_OLD_2 in row.get("resolution_note", ""))
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
            if target["primary"] == "cand-1969":
                if target["s3_note"] not in row["resolution_note"]:
                    assert POLLNITZ_OLD_1 in row["resolution_note"] and POLLNITZ_OLD_2 in row["resolution_note"]
                    row["resolution_note"] = row["resolution_note"].replace(POLLNITZ_OLD_1, POLLNITZ_NEW_1).replace(POLLNITZ_OLD_2, POLLNITZ_NEW_2)
                    row["resolution_note"] += " " + target["s3_note"]
            elif target["s3_note"] not in row["resolution_note"]:
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
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3复核与S4人物直接端点登记：P索引中段组（{DATE}）\n\n"
    process_text += "- S3依据修正：cand-1969原对齐说明称来源提供full personal name，现撤回。索引与正文仅称Baron de Pöllnitz，保留为source-local人物组，不补给名或外部匹配；原错误措辞保留于Git历史。\n"
    for target in TARGETS:
        process_text += f"- {target['primary']}（{target['group']}）→ [{target['name_zh']}（{target['name_en']}）](../../../04-knowledge/{target['ku']}.md)。索引{target['entry']}（页码{target['pages']}）与对应书内页段支持source-local人物登记；直接S2关系候选{', '.join(target['relations'])}留待S6逐条裁决，不登记正式关系。\n"
    process_text += (
        f"本批S4登记{batch_size}个S3 new人物组、{batch_size}条候选映射和{name_fields}条source_backed名称字段；"
        f"{sum(len(target['relations']) for target in TARGETS)}条直接S2关系候选留待S6。"
        "Antonio Pignatelli与Innocent XII按同一索引及第8章正文形式分组，与Innocent XIII分立；Pilati按第10、13章相同全名归组；Pinacci的p.233注仅记录姓名与书目指引，不新增关系；Francesco Piranesi与Giovanni Battista Piranesi保持分立。"
        "Poore组保留Haskell索引和脚注的书内关联，不据未核的拍卖目录断言访客与拍卖藏家为同一外部个人。未决的画作组、藏画集合、书信、拍卖事件、提议建筑师及未完成祭坛对象均保持原状态。"
        "本批未新增外部身份行、正式关系、来源登记或S2断言。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S3复核与S4人物直接端点登记：P索引中段组（{DATE}）\n\n"
        f"登记Bernard Picart、Antonio Pignatelli（Pope Innocent XII）、Carlo Antonio Pilati、Giuseppe Pinacci、Francesco Piranesi、Baron de Pöllnitz、Edward Poore与Giacomo della Porta八个人物组；"
        f"本批{batch_size}条new候选映射、{name_fields}条source_backed名称字段及{sum(len(target['relations']) for target in TARGETS)}条直接S2关系候选。"
        f"关系均留待S6，未新增正式边；Pöllnitz只保留书内头衔与姓氏，Poore外部身份与拍卖归属未核。KU={len(planned_manifest)}；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-p-middle-section-persons-") as td:
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
