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
import register_s4_person_endpoints_assereto_barelli_baretti_bartoli_basadonna_bassi_20261017 as helper  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s4-person-direct-endpoints-caprara-carlisle-cavazza-caylus-cesi-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
S3_ANCHOR = "s3-correct-cesi-candidate-detail-20261017"
S3_DETAIL_PREFIX = "S3 cross-chapter review 2026-10-17 resolves this Monsignor Angelo Cesi as a distinct person"
DBI_URL = "https://www.treccani.it/enciclopedia/angelo-cesi_res-9e027433-87ea-11dc-8e9d-0016357eee51_(Dizionario-Biografico)/"
DBI_SOURCE = "Treccani, Dizionario Biografico degli Italiani"
BT = chr(96)

helper.DATE = DATE
helper.ANCHOR = ANCHOR
helper.PROCESS_REF = PROCESS_REF

TARGETS = [
    {
        "candidate": "cand-0538",
        "members": ["cand-0538"],
        "group": "new-person:caprara-marshal-bff39a6eb9",
        "ku": "units/persons/marshal-caprara",
        "card": "04-knowledge/units/persons/marshal-caprara.md",
        "name_zh": "卡普拉拉元帅",
        "name_en": "Marshal Caprara",
        "name_field": "索引名",
        "index_entries": [{"entry": "C.csv#62", "file": "C.csv", "name": "Caprara, Marshal", "page": "201"}],
        "source_fragments": ["Thus Marshal Caprara commissioned many paintings in", "'Bologna1"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
                "source_span": "line 43; print p.201",
                "location": "第7章第V节 p.201；OCR L43",
                "summary": "Haskell称Marshal Caprara委托了许多博洛尼亚绘画；未列举作品、日期或委托对象，句末注号保留为原文标记。",
                "quote": "Thus Marshal Caprara commissioned many paintings in 'Bologna1",
            }
        ],
        "description_zh": "本卡登记索引主项“Caprara, Marshal”所指人物。第7章第V节 p.201称Marshal Caprara委托了许多博洛尼亚绘画，但未列举具体作品、日期或委托对象；索引及此处称谓均未提供given name。中文名为工作音译。",
        "description_en": "This card records the person indexed as “Caprara, Marshal.” Chapter 7, section V, p.201, says Marshal Caprara commissioned many paintings in Bologna, without naming individual works, dates, or recipients. Neither the index nor this passage supplies a given name. The Chinese rendering is a working transliteration.",
        "relation_ids": ["st-chp7-p201-v-caprara-commissions-bologna-paintings"],
        "relation_context_zh": "Haskell报告Caprara在博洛尼亚的多项绘画委托，但没有给出作品清单或具体对象；该S2候选留待S6。",
        "relation_context_en": "Haskell reports multiple painting commissions by Caprara in Bologna but gives no work list or specific recipient; this S2 candidate remains for S6.",
        "statement_endpoints": [
            ("st-chp7-p201-v-caprara-commissions-bologna-paintings", "cand-0538", "cand-7310", "commissioned_paintings_in", "commissioned many paintings")
        ],
        "alignment_notes": {"cand-0538": "索引与第7章p.201均使用Marshal Caprara；given name及外部身份未在本次登记中补造或声称核验。"},
    },
    {
        "candidate": "cand-0559",
        "members": ["cand-0559"],
        "group": "new-person:carlisle-of-b2c281b2ce",
        "ku": "units/persons/earl-of-carlisle",
        "card": "04-knowledge/units/persons/earl-of-carlisle.md",
        "name_zh": "卡莱尔伯爵",
        "name_en": "Earl of Carlisle",
        "name_field": "索引名",
        "index_entries": [{"entry": "C.csv#83", "file": "C.csv", "name": "Carlisle, Earl of", "page": "279, 305"}],
        "source_fragments": ["for Lord Carlisle, a young man", "He, too, extensively employed the two Venetian artists", "Earl of Carlisle."],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "line 44; print p.279",
                "location": "第10章导论 p.279；OCR L44",
                "summary": "Haskell称Vanbrugh在Yorkshire为年轻的Lord Carlisle营建乡间住宅，并接着说“他”也大量雇用了两位从Castle Howard转往Narford Hall的威尼斯艺术家；S2将两位艺术家分别映射至Marco Ricci与Pellegrini，但原句没有分别说明各自工作内容。",
                "quote": "for Lord Carlisle, a young man who had already embarked on a career to be more noted for its dazzling social prestige than for any real political achievement. He, too, extensively employed the two Venetian artists who from Castle Howard then moved to Narford Hall in",
            },
            {
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "line 433; print p.305",
                "location": "第10章导论 p.305；OCR L433",
                "summary": "同章 p.305 的索引对应正文称谓为“Earl of Carlisle”；与p.279的“Lord Carlisle”及C.csv#83构成书内名称锚点。",
                "quote": "Earl of Carlisle.",
            },
        ],
        "description_zh": "本卡登记索引主项“Carlisle, Earl of”。第10章 p.279称其为年轻的Lord Carlisle，并说他也大量雇用了两位从Castle Howard转往Narford Hall的威尼斯艺术家；S2将艺术家端点映射到Marco Ricci和Pellegrini，但原句没有分别说明两人的具体工作。p.305出现“Earl of Carlisle”称谓。索引和正文均未在此提供个人名字。",
        "description_en": "This card records the person indexed as “Carlisle, Earl of.” Chapter 10, p.279, calls him the young Lord Carlisle and says he too extensively employed two Venetian artists who moved from Castle Howard to Narford Hall; S2 maps those artist endpoints to Marco Ricci and Pellegrini, while the sentence does not specify each artist’s individual work. Page 305 uses “Earl of Carlisle.” The index and these passages do not supply his personal name.",
        "relation_ids": ["st-chp10-p279-carlisle-employs-marco-ricci", "st-chp10-p279-carlisle-employs-pellegrini"],
        "relation_context_zh": "两条S2候选共享“two Venetian artists”这一集体表述；端点分别映射至Marco Ricci与Pellegrini，但不据此拆定个人合同或工作范围，均留待S6。",
        "relation_context_en": "Both S2 candidates share the collective wording “two Venetian artists”; their endpoints map to Marco Ricci and Pellegrini, but no individual contract or scope of work is inferred. Both remain for S6.",
        "statement_endpoints": [
            ("st-chp10-p279-carlisle-employs-marco-ricci", "cand-0559", "cand-2149", "lord_carlisle_extensively_employed_marco_ricci", "He, too, extensively employed the two Venetian artists"),
            ("st-chp10-p279-carlisle-employs-pellegrini", "cand-0559", "cand-1870", "lord_carlisle_extensively_employed_pellegrini", "He, too, extensively employed the two Venetian artists"),
        ],
        "alignment_notes": {"cand-0559": "C.csv#83将p.279、305列为同一索引主项；书内使用Lord Carlisle与Earl of Carlisle，未提供given name。"},
    },
    {
        "candidate": "cand-0614",
        "members": ["cand-0614"],
        "group": "new-person:cavazza-conte-ebbfa1d543",
        "ku": "units/persons/conte-cavazza",
        "card": "04-knowledge/units/persons/conte-cavazza.md",
        "name_zh": "卡瓦扎伯爵",
        "name_en": "Count Cavazza",
        "name_field": "索引名",
        "index_entries": [{"entry": "C.csv#138", "file": "C.csv", "name": "Cavazza, Conte", "page": "269"}],
        "source_fragments": ["the façade, which cost 74,000 ducats, was paid for by a Conte", "Cavazza, who had been admitted to the patriciate in 1653"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
                "source_span": "lines 22-23; print p.269",
                "location": "第9章第II节 p.269；OCR L22-23",
                "summary": "Haskell称价值74,000达克特的教堂立面由Conte Cavazza支付，并报告Cavazza于1653年获准进入威尼斯贵族阶层；注3所据原始记录未在本次身份登记中独立查阅。",
                "quote": "the façade, which cost 74,000 ducats, was paid for by a Conte\nCavazza, who had been admitted to the patriciate in 1653.",
            }
        ],
        "description_zh": "本卡登记索引名“Cavazza, Conte”所指人物。第9章 p.269称一座花费74,000达克特的教堂立面由Conte Cavazza支付，并称Cavazza于1653年获准进入威尼斯贵族阶层；相关注释所引记录未独立查阅。原书和索引未给出given name。中文名为工作音译。",
        "description_en": "This card records the person indexed as “Cavazza, Conte.” Chapter 9, p.269, says a church façade costing 74,000 ducats was paid for by a Conte Cavazza and reports his admission to the Venetian patriciate in 1653; the record cited in the note was not independently consulted. The book and index give no personal name. The Chinese rendering is a working transliteration.",
        "relation_ids": ["st-chp9-p269-cavazza-admission-patriciate", "st-chp9-p269-cavazza-paid-facade"],
        "relation_context_zh": "1653年入贵族阶层及支付立面费用均按Haskell原书陈述保存；注释所引记录未核，两个S2候选留待S6。",
        "relation_context_en": "The reported 1653 patriciate admission and façade payment remain statements in Haskell; the cited record was not checked, and both S2 candidates remain for S6.",
        "statement_endpoints": [
            ("st-chp9-p269-cavazza-admission-patriciate", "cand-8694", "cand-0614", "conte_cavazza_admitted_to_venetian_patriciate_in_1653", "Cavazza, who had been admitted to the patriciate in 1653"),
            ("st-chp9-p269-cavazza-paid-facade", "cand-0614", "cand-0738", "conte_cavazza_paid_74000_ducats_for_scalzi_church_facade", "the façade, which cost 74,000 ducats, was paid for by a Conte"),
        ],
        "alignment_notes": {"cand-0614": "索引与第9章p.269给出Conte Cavazza这一头衔加姓氏称谓；未补造given name或外部生平。"},
    },
    {
        "candidate": "cand-0615",
        "members": ["cand-0615"],
        "group": "new-person:caylus-comte-de-0164c373cd",
        "ku": "units/persons/comte-de-caylus",
        "card": "04-knowledge/units/persons/comte-de-caylus.md",
        "name_zh": "卡亚吕伯爵",
        "name_en": "Comte de Caylus",
        "name_field": "索引名",
        "index_entries": [{"entry": "C.csv#139", "file": "C.csv", "name": "Caylus, Comte de", "page": "319, 360"}],
        "source_fragments": ["among the many friendships he made was one with the Comte de Caylus"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "source_span": "line 147; print p.319",
                "location": "第10章第II节 p.319；OCR L147",
                "summary": "Haskell称Conti在第二次巴黎停留期间建立的多项友谊之一是与Comte de Caylus的友谊；未给出更具体的交往细节。",
                "quote": "among the many friendships he made was one with the Comte de Caylus.",
            }
        ],
        "description_zh": "本卡登记索引主项“Caylus, Comte de”所指人物。第10章第II节 p.319称Conti在第二次巴黎停留期间建立的友谊之一是与Comte de Caylus的友谊；未给出个人名字或更多交往细节。索引还列p.360。中文名为工作音译。",
        "description_en": "This card records the person indexed as “Caylus, Comte de.” Chapter 10, section II, p.319, says one of the friendships Conti formed during his second stay in Paris was with the Comte de Caylus; it gives no personal name or further details of their contact. The index also lists p.360. The Chinese rendering is a working transliteration.",
        "relation_ids": ["st-chp10-p319-conti-friendship-with-caylus"],
        "relation_context_zh": "交友情形来自Haskell对Conti第二次巴黎停留的叙述；未补入额外交往细节，该S2候选留待S6。",
        "relation_context_en": "The friendship is reported by Haskell in the account of Conti’s second stay in Paris; no additional detail is inferred, and the S2 candidate remains for S6.",
        "statement_endpoints": [
            ("st-chp10-p319-conti-friendship-with-caylus", "cand-0826", "cand-0615", "formed-friendship-with-comte-de-caylus", "friendships he made was one with the Comte de Caylus")
        ],
        "alignment_notes": {"cand-0615": "C.csv#139列出p.319、360；第10章p.319正文使用Comte de Caylus。"},
    },
    {
        "candidate": "cand-0639",
        "members": ["cand-0639", "cand-10945"],
        "group": "new-person:angelo-cesi-d4e25faff9",
        "ku": "units/persons/angelo-cesi-bishop-of-todi",
        "card": "04-knowledge/units/persons/angelo-cesi-bishop-of-todi.md",
        "name_zh": "安杰洛·切西（托迪主教）",
        "name_en": "Angelo Cesi, Bishop of Todi",
        "name_field": "索引名",
        "index_entries": [{"entry": "C.csv#163", "file": "C.csv", "name": "Cesi, Bishop Angelo", "page": "69, 70, 400"}],
        "source_fragments": [
            "his brother Angelo",
            "Cesi, Bishop of Todi, continued the family patronage",
            "decoration had been promised by Cardinal Angelo Cesi",
            "In 1606 Cardinal Cesi died",
            "his brother,",
            "Monsignor Angelo Cesi, was a much less accommodating patron",
        ],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "source_span": "lines 42-44; print p.69",
                "location": "第3章第II节 p.69；OCR L42-44",
                "summary": "Haskell称Cardinal Pier Donato Cesi的兄弟Angelo Cesi为托迪主教，并说他延续了家族对Chiesa Nuova的赞助。",
                "quote": "some years after his death in 1586, his brother Angelo Cesi, Bishop of Todi, continued the family patronage.",
            },
            {
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "source_span": "line 58; print p.70",
                "location": "第3章第II节 p.70；OCR L58",
                "summary": "同章称高坛装饰曾由“Cardinal Angelo Cesi”承诺，并报告Cardinal Cesi于1606年去世；Treccani DBI记载Angelo的枢机推荐于1586年未成功，故保留书内头衔冲突。",
                "quote": "The High Altar had been originally dedicated to the Nativity; its decoration had been promised by Cardinal Angelo Cesi. In about 1605, however, two extremely important events occurred.2 A majority of the Oratorians, after much debating, decided to move to the High Altar a ‘miraculous’ image of the Madonna and Child, preserved from the original church, and the money set aside for its decoration was found to have been absorbed in the unexpected expenses of the façade. In 1606 Cardinal Cesi died.",
            },
            {
                "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "source_span": "lines 52-53; print p.400",
                "location": "第2版后记 p.400；OCR L52-53",
                "summary": "后记称Cardinal Cesi的兄弟Monsignor Angelo Cesi是较不宽容的赞助人；结合第3章p.69的同名兄弟与Treccani身份记录，S3将该候选并入Angelo Cesi, Bishop of Todi组。",
                "quote": "the Cardinal’s intervention and that his brother,\nMonsignor Angelo Cesi, was a much less accommodating patron.",
            },
        ],
        "description_zh": "本卡登记索引“Cesi, Bishop Angelo”及第3章p.69所称Angelo Cesi, Bishop of Todi。第2版后记p.400的“Monsignor Angelo Cesi”按S3跨章裁决归入同一人物。第3章p.70称其为“Cardinal Angelo Cesi”，该头衔与Treccani DBI所记1586年枢机推荐未成功相冲突，保留为来源问题，不把该称谓登记为已证头衔。中文名为工作音译。",
        "description_en": "This card records the person indexed as “Cesi, Bishop Angelo” and called Angelo Cesi, Bishop of Todi, on p.69. The “Monsignor Angelo Cesi” in the second-edition postscript, p.400, is grouped with him under the S3 cross-chapter decision. Chapter 3, p.70, calls him “Cardinal Angelo Cesi”; that title conflicts with the Treccani DBI account of an unsuccessful cardinal nomination in 1586 and is retained as a source issue, not registered as an established title. The Chinese rendering is a working transliteration.",
        "relation_ids": ["st-chp3-secii-l40-52-angelo-continues-family-patronage", "st-chp3-secii-l54-60-cesi-promised-high-altar-decoration"],
        "relation_context_zh": "第3章分别记录Angelo Cesi延续家族对Chiesa Nuova的赞助，以及高坛装饰曾由“Cardinal Angelo Cesi”承诺；后者的头衔冲突保留，两个S2候选留待S6。后记p.400的兄弟身份仅用作S3身份锚点，不在本批建立正式边。",
        "relation_context_en": "Chapter 3 records Angelo Cesi’s continuation of family patronage at the Chiesa Nuova and a high-altar decoration promise attributed to “Cardinal Angelo Cesi”; the title conflict is retained, and both S2 candidates remain for S6. The sibling wording on p.400 serves as an S3 identity anchor only; this batch creates no formal edge.",
        "statement_endpoints": [
            ("st-chp3-secii-l40-52-angelo-continues-family-patronage", "cand-0639", "cand-0710", "continued_family_patronage_of", "Cesi, Bishop of Todi, continued the family patronage"),
            ("st-chp3-secii-l54-60-cesi-promised-high-altar-decoration", "cand-0639", "cand-5033", "promised_decoration_of_high_altar", "decoration had been promised by Cardinal Angelo Cesi"),
        ],
        "alignment_notes": {
            "cand-0639": "S3合并组据Treccani DBI与第3章p.69、第2版后记p.400身份锚点登记；p.70的Cardinal头衔冲突保留。",
            "cand-10945": "后记p.400名称按S3同一身份组映射；不把Monsignor称谓自动视作枢机头衔。",
        },
    },
]


def extract_card_fields(cards: dict[str, str]) -> tuple[list[dict], dict, list[str], int]:
    from scripts import build_field_facts
    from scripts.build_field_facts import extract_records

    with tempfile.TemporaryDirectory(prefix="pnp-s4-five-person-groups-") as temp_root:
        temp_base = Path(temp_root)
        rows = []
        for t in TARGETS:
            temp_card = temp_base / t["card"]
            temp_card.parent.mkdir(parents=True, exist_ok=True)
            temp_card.write_text(cards[t["card"]], encoding="utf-8")
            rows.append({"ku_id": t["ku"], "card_path": t["card"]})
        previous_base = build_field_facts.BASE
        build_field_facts.BASE = temp_base
        try:
            return extract_records(rows)
        finally:
            build_field_facts.BASE = previous_base


def make_card(t: dict) -> str:
    card = helper.make_card(t)
    if t["candidate"] == "cand-0639":
        index_row = "| 索引名 | Cesi, Bishop Angelo | S1（索引 C.csv#163） |"
        alias_row = "| 别名 | Monsignor Angelo Cesi | S4（第2版后记 p.400） |"
        assert card.count(index_row) == 1
        card = card.replace(index_row, index_row + "\n" + alias_row, 1)
        dbi_markdown_url = DBI_URL.replace("(", "%28").replace(")", "%29")
        identity_section = (
            "### 身份与外部链接\n\n"
            f"- [Treccani DBI, “CESI, Angelo”]({dbi_markdown_url})：记载Angelo Cesi为托迪主教、1606年去世，"
            "1586年枢机推荐未成功。该记录用于身份比较及第3章p.69／后记p.400兄弟身份锚点；"
            "Haskell p.70的“Cardinal Angelo”保留为头衔冲突，不据此确认枢机身份。"
        )
        marker = "## 关系与证据\n\n### 关系记录"
        assert card.count(marker) == 1
        card = card.replace(marker, "## 关系与证据\n\n" + identity_section + "\n\n### 关系记录", 1)
    return card


def main() -> int:
    parser = argparse.ArgumentParser(description="Register five S3 new person groups as S4 KU cards.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    base = helper.base
    alignment_fields, alignments = base.sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = base.sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = base.sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    assert len(candidate_by_id) == len(alignment_by_id) and len(manifest_by_ku) == len(manifest)
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [
        json.loads(line)
        for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    statement_by_id = {row["statement_id"]: row for row in statements}
    before_stats = base.sync.summarize_by_type(candidates, alignments)
    planned_candidates = [dict(row) for row in candidates]
    planned_candidate_by_id = {row["candidate_id"]: row for row in planned_candidates}

    # The S3 identity decision is already correct; this repairs stale explanatory metadata
    # left by the earlier candidate-detail writeback.
    stale_detail = candidate_by_id["cand-10945"].get("detail", "")
    assert stale_detail.startswith(S3_DETAIL_PREFIX), stale_detail
    assert base.sync.get_group(alignment_by_id["cand-10945"].get("resolution_note", "")) == TARGETS[-1]["group"]
    assert base.sync.get_group(alignment_by_id["cand-0639"].get("resolution_note", "")) == TARGETS[-1]["group"]
    planned_candidate_by_id["cand-10945"]["detail"] = (
        "S3跨章复核（2026-10-17）：第3章p.69称Angelo Cesi, Bishop of Todi为Cardinal Pier Donato Cesi的兄弟；"
        "第2版后记p.400称Monsignor Angelo Cesi为同一Cardinal Cesi的兄弟。结合Treccani DBI所载Angelo Cesi为托迪主教，"
        "且1586年枢机推荐未成功，cand-10945与cand-0639是同一人物。第3章p.70的“Cardinal Angelo”作为头衔冲突保留，"
        "不作为已证枢机身份。"
    )

    for t in TARGETS:
        for cid in t["members"]:
            c, a = candidate_by_id[cid], alignment_by_id[cid]
            assert c.get("suggested_type") == "person"
            assert a.get("decision") == "new" and not a.get("ku_id")
            assert base.sync.get_group(a.get("resolution_note", "")) == t["group"]
        group_members = [
            row["candidate_id"]
            for row in alignments
            if row.get("candidate_id")
            and not row.get("external_source")
            and row.get("decision") == "new"
            and base.sync.get_group(row.get("resolution_note", "")) == t["group"]
        ]
        assert set(group_members) == set(t["members"]), (t["group"], group_members)
        for entry in t["index_entries"]:
            row = base.read_index_rows(entry["file"])[int(entry["entry"].split("#")[1])]
            assert row.get("Main Entry") == entry["name"] and row.get("Page Numbers", "") == entry["page"]
        source_texts = {
            file: (ROOT / file).read_text(encoding="utf-8-sig")
            for file in {s["source_file"] for s in t["book_sources"]}
        }
        normalized_all = re.sub(r"\s+", " ", " ".join(source_texts.values()))
        assert all(re.sub(r"\s+", " ", frag) in normalized_all for frag in t["source_fragments"]), t["candidate"]
        for source in t["book_sources"]:
            normalized_source = re.sub(r"\s+", " ", source_texts[source["source_file"]])
            assert re.sub(r"\s+", " ", source["quote"]) in normalized_source, (t["candidate"], source["source_span"])
        direct = {
            row["statement_id"]
            for row in statements
            if (row.get("qualifiers") or {}).get("relation_candidate") is True
            and (row.get("subject_candidate_id") in t["members"] or row.get("object_candidate_id") in t["members"])
        }
        expected_direct = {row[0] for row in t["statement_endpoints"]}
        assert direct == expected_direct, (t["group"], direct, expected_direct)
        for sid, subject, obj, predicate, quote_fragment in t["statement_endpoints"]:
            statement = statement_by_id[sid]
            normalized_quote = re.sub(r"\s+", " ", statement.get("original_quote", ""))
            assert statement.get("subject_candidate_id") == subject and statement.get("object_candidate_id") == obj, sid
            assert statement.get("predicate") == predicate and re.sub(r"\s+", " ", quote_fragment) in normalized_quote, sid
        assert t["ku"] not in manifest_by_ku and t["card"] not in accepted_paths and not (ROOT / t["card"]).exists()
        assert not any(
            row.get("type") == "person" and (row.get("name_en") or "").casefold() == t["name_en"].casefold()
            for row in manifest
        )

    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    map_count = sum(len(t["members"]) for t in TARGETS)
    for t in TARGETS:
        for cid in t["members"]:
            a = next(row for row in planned_alignments if row.get("candidate_id") == cid and not row.get("external_source"))
            a["ku_id"] = t["ku"]
            a["process_ref"] = PROCESS_REF
            group_token = f"group={t['group']}"
            if a["resolution_note"].endswith(group_token):
                a["resolution_note"] += ";"
            note = t.get("alignment_notes", {}).get(cid, "书内身份依据保留来源限定。")
            a["resolution_note"] += f" S4登记（{DATE}）：{t['group']}映射至{t['ku']}；{note}直接关系候选留待S6。"
        planned_manifest.append(
            {
                "ku_id": t["ku"],
                "type": "person",
                "canonical_name": t["name_zh"],
                "name_en": t["name_en"],
                "source_task": TASK,
                "card_path": t["card"],
            }
        )
    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        planned_accepted = base.insert_accepted(planned_accepted, t["card"])
    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    assert len({line[2:] for line in planned_accepted if line.startswith("- 04-knowledge/units/")}) == len(accepted_paths) + len(TARGETS)

    external_rows = [row for row in alignments if row.get("external_source")]
    existing_alignment_ids = {row.get("alignment_id", "") for row in alignments}
    max_alignment_id = max(
        (int(match.group(1)) for value in existing_alignment_ids if (match := re.fullmatch(r"aln-(\d+)", value))),
        default=0,
    )
    external_alignment = {
        "alignment_id": f"aln-{max_alignment_id + 1:05d}",
        "candidate_id": "cand-0639",
        "ku_id": TARGETS[-1]["ku"],
        "external_source": DBI_SOURCE,
        "external_id": DBI_URL,
        "decision": "same",
        "accessed_date": DATE,
        "process_ref": PROCESS_REF,
        "legacy_ku_id": "",
        "resolution_note": (
            "Identity comparison only: Luigi Cajani, “CESI, Angelo,” Dizionario Biografico degli Italiani, vol. 24 (1980), "
            "identifies Angelo Cesi as Bishop of Todi, records that the 1586 cardinal recommendation was unsuccessful, and gives his death in 1606. "
            "Compared with Haskell ch.3 pp.69-70 and second-edition postscript p.400; supports identity reconciliation only, "
            "retains the p.70 cardinal-title conflict, and does not validate the patronage statements."
        ),
    }
    assert external_alignment["alignment_id"] not in existing_alignment_ids
    assert not any(
        row.get("candidate_id") == "cand-0639"
        and row.get("external_source") == DBI_SOURCE
        and row.get("external_id") == DBI_URL
        for row in external_rows
    )
    planned_alignments.append(external_alignment)

    stats = base.sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(row[key] for row in before_stats.values()) for key in next(iter(before_stats.values()))}
    assert stats["person"]["registered_groups"] == before_stats["person"]["registered_groups"] + len(TARGETS)
    assert stats["person"]["registered_members"] == before_stats["person"]["registered_members"] + map_count
    assert totals["registered_groups"] == before_totals["registered_groups"] + len(TARGETS)
    assert totals["registered_members"] == before_totals["registered_members"] + map_count
    assert totals["pending_groups"] == before_totals["pending_groups"] - len(TARGETS)
    assert totals["pending_members"] == before_totals["pending_members"] - map_count
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    cards = {t["card"]: make_card(t) for t in TARGETS}
    for card in cards.values():
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert match and isinstance(base.yaml.safe_load(match.group(1)), dict)

    additions, source_registry, warnings, cards_with_tables = extract_card_fields(cards)
    assert cards_with_tables == len(TARGETS) and len(additions) == 6, (cards_with_tables, len(additions))
    assert all(row.get("source_ids") == ["haskell-1980-rev-ed"] for row in additions)
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
    assert set(source_registry) == {"haskell-1980-rev-ed"}
    assert not warnings, warnings
    additions_by_ku = {}
    for row in additions:
        additions_by_ku.setdefault(row["ku_id"], []).append(row)
    assert additions_by_ku[TARGETS[-1]["ku"]][0]["field"] == "索引名"
    assert {row["field"] for row in additions_by_ku[TARGETS[-1]["ku"]]} == {"索引名", "别名"}
    existing_enrichment = [
        json.loads(line)
        for line in ENRICHMENT_PATH.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    existing_enrichment_text = ENRICHMENT_PATH.read_text(encoding="utf-8-sig")
    natural_keys = {
        (row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id"))
        for row in existing_enrichment
    }
    existing_enrichment_ids = {row.get("enrichment_id", "") for row in existing_enrichment}
    max_enrichment_id = max(
        (int(match.group(1)) for value in existing_enrichment_ids if (match := re.fullmatch(r"enr-(\d+)", value))),
        default=0,
    )
    for offset, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_enrichment_id + offset:05d}"
        key = (row["ku_id"], row["field"], row["value"], row.get("source_id", ""))
        assert key not in natural_keys and row["enrichment_id"] not in existing_enrichment_ids

    process_text = helper.base.process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    if f'<a id="{S3_ANCHOR}"></a>' not in process_text:
        process_text = process_text.rstrip() + (
            f"\n\n<a id=\"{S3_ANCHOR}\"></a>\n\n### S3候选元数据纠正：cand-10945（{DATE}）\n\n"
            "核对entity-candidates.csv时发现cand-10945的detail仍保留旧的“不同人物”说明，"
            "与alignment.csv中已执行的cand-0639/cand-10945同组决定冲突。S3裁决、组号及候选映射本身正确；"
            "前次更正脚本把detail写到了候选字典外层，本次将说明修正到cand-10945行。"
            "现明确两者同为Cardinal Pier Donato Cesi的兄弟Angelo Cesi；Treccani支持托迪主教身份，"
            "第3章p.70的枢机头衔仍保留为来源冲突。组成员和S3决定计数不变。"
        )
    group_lines = []
    for t in TARGETS:
        member_label = "、".join(f"{BT}{cid}{BT}" for cid in t["members"])
        relation_labels = ", ".join(f"{BT}{sid}{BT}" for sid in t["relation_ids"])
        group_lines.append(
            f"- {member_label}（{BT}{t['group']}{BT}）→ [{t['name_zh']}（{t['name_en']}）](../../../{t['card']})；"
            f"S2直接关系候选 {relation_labels} 留待S6。{t['relation_context_zh']}"
        )
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物身份组登记：Caprara、Carlisle、Cavazza、Caylus、Angelo Cesi（{DATE}）\n\n"
        + "\n".join(group_lines)
        + "\n\n本批登记5个S3 new人物身份组、6条候选映射；每组只登记书内支持的名称。"
        "Cesi外部身份比较另记Treccani DBI为aln外部记录，仅支持身份及头衔冲突辨析。"
        "新增6条source_backed姓名字段；不新增formal relations。"
        f"\n\n登记后person类型S4为{base.sync.fmt(stats['person']['registered_groups'])}组/"
        f"{base.sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{base.sync.fmt(stats['person']['pending_groups'])}组/{base.sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{base.sync.fmt(totals['registered_groups'])}组/{base.sync.fmt(totals['registered_members'])}条已登记、"
        f"{base.sync.fmt(totals['pending_groups'])}组/{base.sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )

    result_text = base.sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text, alignment_count = re.subn(
        r"^\| \[全书对齐\]\(\.\./tables/alignment\.csv\) \| [\d,]+ 条：[\d,]+ 条候选决定记录及 [\d,]+ 条外部身份记录；候选决定数见下表 \|$",
        f"| [全书对齐](../tables/alignment.csv) | {len(planned_alignments):,} 条：12,407 条候选决定记录及 {len(external_rows) + 1:,} 条外部身份记录；候选决定数见下表 |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert alignment_count == 1
    result_text, enrichment_count = re.subn(
        r"^\| \[既有字段表\]\(\.\./tables/enrichment\.jsonl\) \| [\d,]+条(.*)\|$",
        lambda m: f"| [既有字段表](../tables/enrichment.jsonl) | {len(existing_enrichment) + len(additions):,}条{m.group(1)}|",
        result_text,
        count=1,
        flags=re.M,
    )
    assert enrichment_count == 1
    result_text += (
        f"\n\n### S4人物身份组登记：五个直接关系端点组（{DATE}）\n\n"
        + "；".join(
            f"{BT}{' / '.join(t['members'])}{BT} → {BT}../units/persons/{t['ku'].split('/')[-1]}.md{BT}"
            for t in TARGETS
        )
        + "。共5组/6条映射；Cesi的p.70头衔冲突保留，Treccani外部记录仅作身份比较。"
        "8条直接S2关系候选留待S6，本批无新增formal relations。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: groups={len(TARGETS)}; candidate_mappings={map_count}; "
            f"Cesi stale detail corrected; external_alignment={external_alignment['alignment_id']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; "
            f"enrichment={len(existing_enrichment)}->{len(existing_enrichment)+len(additions)}; "
            f"alignment_rows={len(alignments)}->{len(planned_alignments)}; formal_relations_added=0; no files changed"
        )
        return 0

    for rel_path, card in cards.items():
        (ROOT / rel_path).write_text(card, encoding="utf-8", newline="\n")
    base.sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    base.sync.write_csv(ENTITY_PATH, candidate_fields, planned_candidates)
    base.sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    with ENRICHMENT_PATH.open("w", encoding="utf-8-sig", newline="\n") as handle:
        handle.write(existing_enrichment_text.rstrip("\r\n") + "\n")
        for row in additions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups={len(TARGETS)}; candidate_mappings={map_count}; "
        f"Cesi detail corrected; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"enrichment_rows={len(additions)}; external_alignment={external_alignment['alignment_id']}; formal_relations_added=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
