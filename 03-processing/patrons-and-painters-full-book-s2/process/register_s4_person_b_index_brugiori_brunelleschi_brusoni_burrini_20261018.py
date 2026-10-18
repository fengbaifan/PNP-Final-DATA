from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402


registrar.ANCHOR = "s4-b-index-brugiori-brunelleschi-brusoni-burrini-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-b-index-brugiori-brunelleschi-brusoni-burrini-20261018"
)
registrar.BATCH_TITLE = "Brugiori、Brunelleschi、Brusoni与Burrini四组人物"
registrar.BATCH_PROCESS_NOTE = (
    "四个S3 new人物组登记为4张KU卡、4条new候选映射和8条source_backed姓名字段；"
    "Filippo Brunelleschi、Girolamo Brusoni与Giovanni Antonio Burrini分别有Treccani DBI身份记录，"
    "外部记录只支持身份，不扩展为卡内生平事实。Domenico Brugiori按本书全名及画家称名登记为source-local人物；"
    "Cain and Abel作品候选cand-0457与人物cand-0456分开。Brusoni索引子项cand-0462的same裁决及Canal跨章分组见后续S3复核。"
    "四条直接相关S2关系候选留待S6；无正式关系或backlog写入。"
)
registrar.BATCH_RESULT_NOTE = (
    "；Brunelleschi、Brusoni、Burrini的Treccani DBI身份记录列于alignment.csv；"
    "Brugiori仅据书内全名登记，作品cand-0457保持独立work候选。"
    "相关S2关系候选仍留待S6，不新增正式关系。"
)

book_source = registrar.book_source


def index_subentry_source(entry: str, title: str, page: str) -> dict:
    index_file = entry.split("#", 1)[0]
    source_file = f"02-sources/03-Index/03-2-Index-CSV/{index_file}"
    return {
        "citation": f"Francis Haskell, *Patrons and Painters*, index, {index_file}.",
        "location": f"书后索引，{entry}；子目指向印刷页{page}",
        "sentence_summary": f"索引在人名主项下列出作品子目“{title}”，并指向印刷页{page}。",
        "original_quotes": [{"source_span": entry, "text": title}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": source_file,
            "source_span": entry,
        },
    }


registrar.TARGETS = [
    {
        "candidate": "cand-0456",
        "group": "new-person:brugiori-domenico-add9db10dc",
        "ku": "units/persons/domenico-brugiori",
        "card": "04-knowledge/units/persons/domenico-brugiori.md",
        "candidate_name": "Brugiori, Domenico",
        "name_zh": "多梅尼科·布鲁乔里",
        "name_en": "Domenico Brugiori",
        "index_entry": "B.csv#303",
        "index_name": "Brugiori, Domenico",
        "index_page": "",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "book_sources": [
            index_subentry_source("B.csv#304", "Cain and Abel", "227"),
            book_source(
                "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "第8章第II节，印刷页227，行202",
                "line 202; print p. 227",
                "a Cain and Abel by the local artist Domenico Brugiori",
                "Haskell将Domenico Brugiori称为本地画家，并在购买叙述中将其与Cain and Abel作品相连。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Brugiori, Domenico", "S1，B.csv#303"),
            ("正文全名", "Domenico Brugiori", "S3，第8章第II节，p.227，L202"),
        ],
        "relation_ids": ["st-chp8-p227-conti-bought-brugiori-cain-abel"],
        "description_zh": (
            "本卡登记书后索引主项“Brugiori, Domenico”及第8章第227页正文全名Domenico Brugiori。"
            "Haskell称其为本地画家；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Domenico Brugiori, indexed as “Brugiori, Domenico” and named in full in Chapter 8, page 227. "
            "Haskell calls him a local artist. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "第8章p.227将Cain and Abel作为独立作品候选cand-0457，并在同句称Domenico Brugiori为画家。"
            "人物与作品分开；购买statement及其作者表述保留为S2关系候选，留待S6，不由本次登记生成正式边。"
        ),
        "context_en": (
            "Chapter 8, page 227, represents Cain and Abel as a separate work candidate, cand-0457, and names Domenico Brugiori as its painter. "
            "The person and work remain distinct; the purchase statement and its authorship wording remain an S2 relation candidate for S6, "
            "and this registration creates no formal edge."
        ),
    },
    {
        "candidate": "cand-0459",
        "group": "new-person:brunelleschi-filippo-62fe3e2653",
        "ku": "units/persons/filippo-brunelleschi",
        "card": "04-knowledge/units/persons/filippo-brunelleschi.md",
        "candidate_name": "Brunelleschi, Filippo",
        "name_zh": "菲利波·布鲁内莱斯基",
        "name_en": "Filippo Brunelleschi",
        "index_entry": "B.csv#306",
        "index_name": "Brunelleschi, Filippo",
        "index_page": "103",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
        "book_source": book_source(
            "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
            "第4章第II节，印刷页103，行50–51",
            "lines 50–51; print p. 103",
            "Brunelleschi, Buonarotti,\nBramante, Serlio, Palladio, Vignola",
            "Haskell转引Cassiano，将Brunelleschi列入一组建筑复兴者；相关集合表述保留为引文语境。",
        ),
        "name_rows": [
            ("索引姓名", "Brunelleschi, Filippo", "S1，B.csv#306"),
            ("正文称名", "Brunelleschi", "S2，第4章第II节，p.103，L50–51"),
        ],
        "relation_ids": ["st-chp4-sec-ii-l46-51-restorers-took-proportions-from-roman-buildings"],
        "external_identities": [
            {
                "source": "Treccani DBI",
                "id": "https://www.treccani.it/enciclopedia/filippo-brunelleschi_(Dizionario-Biografico)/",
                "resolution_note": (
                    "Identity only: Treccani DBI, “BRUNELLESCHI, Filippo” (1972), identifies the person under the same full name "
                    "as index B.csv#306 and the Chapter 4 surname form. Used to confirm the person identity; it does not verify the "
                    "historical architectural claim attributed to Cassiano. Accessed 2026-10-18."
                ),
            }
        ],
        "s3_identity_note": (
            "索引B.csv#306的“Brunelleschi, Filippo”与第4章p.103 Cassiano引文中的姓氏称名相合；"
            "Treccani DBI“BRUNELLESCHI, Filippo”（https://www.treccani.it/enciclopedia/filippo-brunelleschi_(Dizionario-Biografico)/；"
            "访问2026-10-18）以同一全名收录建筑师Filippo Brunelleschi。当前KU中未发现同一人物，故保留new；"
            "外部记录仅支持身份，不验证引文中的建筑史判断。"
        ),
        "identity_section": (
            "### 身份与外部链接\n\n"
            "- Treccani，《意大利人传记辞典》："
            "[Filippo Brunelleschi](https://www.treccani.it/enciclopedia/filippo-brunelleschi_(Dizionario-Biografico)/)。"
            "用于核对全名与人物身份，不用于验证Cassiano引文中的建筑史判断。"
        ),
        "description_zh": (
            "本卡将索引全名“Brunelleschi, Filippo”及正文姓氏“Brunelleschi”记录为Filippo Brunelleschi；"
            "Treccani DBI支持该身份对应。中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index form “Brunelleschi, Filippo” and the text form “Brunelleschi” as Filippo Brunelleschi; "
            "the Treccani DBI entry supports the identity match. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell转引Cassiano，将Brunelleschi列在一组被称为建筑复兴者的人物中。该表述保留引文与群体层级；"
            "不据此为Brunelleschi补充未由本书锚点支持的个人生平或建筑事实。"
        ),
        "context_en": (
            "Haskell quotes Cassiano listing Brunelleschi among figures described as restorers of architecture. "
            "The quotation and group-level scope are retained; no biography or architectural fact beyond the book anchor is added."
        ),
    },
    {
        "candidate": "cand-0461",
        "group": "new-person:brusoni-girolamo-86f3dc6e32",
        "ku": "units/persons/girolamo-brusoni",
        "card": "04-knowledge/units/persons/girolamo-brusoni.md",
        "candidate_name": "Brusoni, Girolamo",
        "name_zh": "吉罗拉莫·布鲁索尼",
        "name_en": "Girolamo Brusoni",
        "index_entry": "B.csv#308",
        "index_name": "Brusoni, Girolamo",
        "index_page": "149n",
        "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
        "book_sources": [
            index_subentry_source("B.csv#309", "Allori d'Eurota", "149n"),
            book_source(
                "02-sources/02-Markdown/06_CHP-6_sec_i.md",
                "第6章第I节脚注，印刷页149，注6",
                "line 128; print p. 149, note 6",
                "the poems edited by Girolamo Brusoni under the title Allori d'Eurota in 1662.",
                "Haskell脚注称一部1662年诗集Allori d'Eurota由Girolamo Brusoni编辑；诗集作为archive对象与人物分别处理。",
            ),
        ],
        "name_rows": [
            ("索引主项及子项姓名", "Brusoni, Girolamo", "S1，B.csv#308–309"),
            ("正文全名", "Girolamo Brusoni", "S3，第6章第I节脚注，p.149注6，L128"),
        ],
        "relation_ids": ["st-chp6-notes-l128-p149-n6"],
        "external_identities": [
            {
                "source": "Treccani DBI",
                "id": "https://www.treccani.it/enciclopedia/girolamo-brusoni_(Dizionario-Biografico)/",
                "resolution_note": (
                    "Identity only: Treccani DBI, “BRUSONI, Girolamo” (Gaspare De Caro, 1972), identifies a person under the exact "
                    "full name in the index and Chapter 6 note. This supports the person identity only, not the cited book's editorial "
                    "details or the relation candidate. Accessed 2026-10-18."
                ),
            }
        ],
        "s3_identity_note": (
            "B.csv#308–309使用同一主项“Brusoni, Girolamo”，第309行仅增加Allori d'Eurota作品子目；"
            "第6章p.149注6正文以全名Girolamo Brusoni称编辑者。Treccani DBI“BRUSONI, Girolamo”"
            "（Gaspare De Caro，1972；https://www.treccani.it/enciclopedia/girolamo-brusoni_(Dizionario-Biografico)/；"
            "访问2026-10-18）支持人物全名身份。该身份核对不验证Haskell对诗集的编辑归属或脚注内容。"
        ),
        "identity_section": (
            "### 身份与外部链接\n\n"
            "- Treccani，《意大利人传记辞典》："
            "[Girolamo Brusoni](https://www.treccani.it/enciclopedia/girolamo-brusoni_(Dizionario-Biografico)/)。"
            "用于核对人物全名身份；诗集归属仍按Haskell注释记录，未由此升级为外部验证事实。"
        ),
        "description_zh": (
            "本卡登记索引主项“Brusoni, Girolamo”、同一主项下的Allori d'Eurota子目及第6章第149页注6的全名称谓。"
            "Treccani DBI支持Girolamo Brusoni的人物身份；中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the index entry “Brusoni, Girolamo,” its Allori d'Eurota subentry, and the full name in Chapter 6, page 149 note 6. "
            "The Treccani DBI entry supports Girolamo Brusoni's person identity. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell脚注称1662年诗集Allori d'Eurota由Girolamo Brusoni编辑；archive候选与人物保持分开，"
            "脚注关系候选st-chp6-notes-l128-p149-n6留待S6，不建立正式关系。"
        ),
        "context_en": (
            "Haskell's note says the 1662 poetry collection Allori d'Eurota was edited by Girolamo Brusoni. "
            "The archive candidate remains separate from the person; statement st-chp6-notes-l128-p149-n6 remains for S6, with no formal edge created."
        ),
    },
    {
        "candidate": "cand-0473",
        "group": "new-person:antonio-burrini-giovanni-e58a37c469",
        "ku": "units/persons/giovanni-antonio-burrini",
        "card": "04-knowledge/units/persons/giovanni-antonio-burrini.md",
        "candidate_name": "Burrini, Giovanni Antonio",
        "name_zh": "乔瓦尼·安东尼奥·布里尼",
        "name_en": "Giovanni Antonio Burrini",
        "index_entry": "B.csv#321",
        "index_name": "Burrini, Giovanni Antonio",
        "index_page": "204",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "book_source": book_source(
            "02-sources/02-Markdown/08_CHP-8_sec_i.md",
            "第8章第I节，印刷页204，行15",
            "line 15; print p. 204",
            "above all Burrini and the young Crespi.",
            "Haskell在描述Giovanni Ricci欣赏的当代艺术家时列出Burrini与年轻的Crespi。",
        ),
        "name_rows": [
            ("索引姓名", "Burrini, Giovanni Antonio", "S1，B.csv#321"),
            ("正文姓氏", "Burrini", "S2，第8章第I节，p.204，L15"),
        ],
        "relation_ids": ["st-chp8-p204-ricci-admired-contemporary-artists"],
        "external_identities": [
            {
                "source": "Treccani DBI",
                "id": "https://www.treccani.it/enciclopedia/giovanni-antonio-burrini_(Dizionario-Biografico)/",
                "resolution_note": (
                    "Identity only: Treccani DBI, “BURRINI, Giovanni Antonio” (Dwight C. Miller, 1972), uses the exact indexed full name "
                    "and identifies a painter, matching the name and artist context in the book. It does not verify Ricci's appraisal or any relation. "
                    "Accessed 2026-10-18."
                ),
            }
        ],
        "s3_identity_note": (
            "索引B.csv#321的全名“Burrini, Giovanni Antonio”与第8章p.204艺术家名单中的Burrini相合；"
            "Treccani DBI“BURRINI, Giovanni Antonio”（Dwight C. Miller，1972；"
            "https://www.treccani.it/enciclopedia/giovanni-antonio-burrini_(Dizionario-Biografico)/；访问2026-10-18）"
            "以同一全名收录画家。当前KU中未发现同一人物，故保留new；外部记录只支持身份，不验证Ricci的评价或关系。"
        ),
        "identity_section": (
            "### 身份与外部链接\n\n"
            "- Treccani，《意大利人传记辞典》："
            "[Giovanni Antonio Burrini](https://www.treccani.it/enciclopedia/giovanni-antonio-burrini_(Dizionario-Biografico)/)。"
            "用于核对人物全名身份，不验证Haskell关于Giovanni Ricci的评价或关系。"
        ),
        "description_zh": (
            "本卡登记索引全名“Burrini, Giovanni Antonio”及第8章第204页姓氏称名“Burrini”；"
            "Treccani DBI支持人物全名身份。中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the indexed full name “Burrini, Giovanni Antonio” and the Chapter 8, page 204 surname form “Burrini”; "
            "the Treccani DBI entry supports the full-name identity. The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Haskell在描写Giovanni Ricci欣赏的当代艺术家时列出Burrini和年轻的Crespi。"
            "该表述保留原书评价与多人语境；S2关系候选st-chp8-p204-ricci-admired-contemporary-artists留待S6。"
        ),
        "context_en": (
            "Haskell names Burrini and the young Crespi among the contemporary artists Giovanni Ricci appreciated. "
            "The book's appraisal and group context are retained; S2 candidate st-chp8-p204-ricci-admired-contemporary-artists remains for S6."
        ),
    },
]


if __name__ == "__main__":
    raise SystemExit(registrar.main())
