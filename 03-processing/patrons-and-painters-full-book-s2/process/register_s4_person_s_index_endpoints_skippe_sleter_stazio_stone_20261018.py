from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_s_index_endpoints_schut_segala_serlio_skala_20261018 as registrar  # noqa: E402

registrar.ANCHOR = "s4-skippe-sleter-stazio-stone-person-endpoints-20261018"
registrar.PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    "s4-skippe-sleter-stazio-stone-person-endpoints-20261018"
)
registrar.BATCH_TITLE = "Skippe、Sleter、Stazio、Stone四组直接端点登记"
registrar.BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选身份组，登记4张KU卡、4条候选映射和9条source_backed姓名字段。"
    "Sleter在p.286–287的句子跨页续接；Stazio遗嘱明确未说明合唱席画作的委托者；"
    "Nicholas Stone的陈述是Haskell转引的嵌套引文。本批不新增外部来源、正式关系或backlog项目。"
)
registrar.BATCH_RESULT_NOTE = (
    "。六条S2关系候选继续待S6；Sleter跨p.286–287续接、Stazio遗嘱未具名画作委托者、"
    "Stone陈述的转引层级均保留。"
)
registrar.TARGETS = [
    {
        "candidate": "cand-2437",
        "group": "new-person:john-skippe-c41d071db2",
        "ku": "units/persons/john-skippe",
        "card": "04-knowledge/units/persons/john-skippe.md",
        "name_zh": "约翰·斯基普",
        "name_en": "John Skippe",
        "index_entry": "S.csv#126",
        "index_name": "Skippe, John",
        "index_page": "375n",
        "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/16_CHP-16_intro.md",
            "第16章脚注3，印刷页375",
            "line 78; print p. 375 n. 3",
            "Among those in touch with Sasso were A. Hume—see Lorenzetti, 1914, who publishes three letters of 1790-2; John Skippe (1778-9) and Hamilton, Marquis of Douglas (1800-2)—see letters in the Epistolario Moschini, Biblioteca Correr, Venice.",
            "Haskell脚注将John Skippe（1778–79）列为与Sasso有联系者之一，并指向威尼斯Correr图书馆的Epistolario Moschini书信；原信未在本轮查阅。",
        ),
        "name_rows": [
            ("索引姓名", "Skippe, John", "S1，S.csv#126"),
            ("脚注姓名", "John Skippe", "S2，第16章，p.375 n.3，L78"),
        ],
        "relation_ids": ["st-chp16-p375-skippe-in-touch-with-sasso"],
        "description_zh": (
            "本卡登记书后索引作“Skippe, John”、第16章脚注具名的John Skippe。"
            "Haskell将他列为1778–79年与Sasso有联系者之一，并指向威尼斯Correr图书馆的Epistolario Moschini书信。"
            "相关书信未在本轮独立查阅；本卡记录限于Haskell脚注。中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records John Skippe, indexed as “Skippe, John” and named in a Chapter 16 footnote. "
            "Haskell lists him among those in touch with Sasso in 1778–79 and points to letters in the Epistolario Moschini at the Biblioteca Correr in Venice. "
            "The letters were not independently consulted; this card is limited to Haskell's note. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "唯一关系候选是Haskell脚注所述Skippe与Sasso的联系及其书信目录指引；原信未读，候选待S6。"
        ),
        "context_en": (
            "The relation candidate is Haskell's footnote report of Skippe being in touch with Sasso and its pointer to correspondence. "
            "The letters were not read; the candidate remains for S6."
        ),
    },
    {
        "candidate": "cand-2439",
        "group": "new-person:francesco-sleter-5d38f9ab80",
        "ku": "units/persons/francesco-sleter",
        "card": "04-knowledge/units/persons/francesco-sleter.md",
        "name_zh": "弗朗切斯科·斯莱特",
        "name_en": "Francesco Sleter",
        "index_entry": "S.csv#128",
        "index_name": "Sleter, Francesco",
        "index_page": "281, 287",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "book_sources": [
            registrar.book_source(
                "02-sources/02-Markdown/10_CHP-10_intro.md",
                "第10章，印刷页281，行131–132",
                "lines 131–132; print p. 281",
                "above all, he employed this artist together with the Bolognese stuccatore Bagutti and a mysterious figure called\nFrancesco Sleter to decorate the chapel.",
                "Haskell称Brydges雇用Sleter、Bellucci和灰泥工Bagutti装饰礼拜堂，并将Sleter称为一位身份未明的人物。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/10_CHP-10_intro.md",
                "第10章，印刷页286，行204",
                "line 204; print p. 286",
                "Styles had intended to entrust Thornhill with the decoration, but the two men quarrelled and to spite the artist Styles gave the job to",
                "Haskell称Styles原拟将Moor Park装饰工作交给Thornhill，争执后改派他人；句子在页末跨至下一印刷页。",
            ),
            registrar.book_source(
                "02-sources/02-Markdown/10_CHP-10_intro.md",
                "第10章，印刷页287，行207",
                "line 207; print p. 287",
                "Amigoni and Francesco Sleter instead.",
                "跨页续句说明Styles最终把Moor Park装饰工作交给Amigoni和Francesco Sleter。",
            ),
        ],
        "name_rows": [
            ("索引姓名", "Sleter, Francesco", "S1，S.csv#128"),
            ("正文姓名", "Francesco Sleter", "S2，第10章，p.281，L132"),
            ("跨页续句姓名", "Francesco Sleter", "S4，第10章，p.287，L207"),
        ],
        "relation_ids": [
            "st-chp10-p281-bellucci-chandos-chapel-team",
            "st-chp10-p286-moor-park-decoration-open",
        ],
        "description_zh": (
            "本卡登记书后索引作“Sleter, Francesco”、第10章具名的Francesco Sleter。"
            "Haskell称Brydges雇用他与Bellucci、Bagutti装饰一处礼拜堂，并称他当时是身份未明的人物；"
            "另述Styles与Thornhill争执后，将Moor Park装饰工作交给Amigoni和Sleter。后一句从p.286续至p.287。"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Francesco Sleter, indexed as “Sleter, Francesco” and named in Chapter 10. "
            "Haskell says Brydges employed him with Bellucci and Bagutti to decorate a chapel, calling him a mysterious figure at the time; "
            "elsewhere, after Styles quarrelled with Thornhill, Styles gave the Moor Park decoration to Amigoni and Sleter. "
            "The latter sentence continues from p. 286 onto p. 287. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "两条候选分别涉及礼拜堂装饰雇用和Moor Park工作改派；后一陈述跨页，按原文续句保留，不将其拆成不同身份。"
        ),
        "context_en": (
            "The two candidates concern the chapel decoration employment and the reassignment of the Moor Park work. "
            "The latter statement crosses a page break and is retained as one continuation, not split into separate identities."
        ),
    },
    {
        "candidate": "cand-2508",
        "group": "new-person:andrea-stazio-a3e55b8f8f",
        "ku": "units/persons/andrea-stazio",
        "card": "04-knowledge/units/persons/andrea-stazio.md",
        "name_zh": "安德烈亚·斯塔齐奥",
        "name_en": "Andrea Stazio",
        "index_entry": "S.csv#197",
        "index_name": "Stazio, Andrea",
        "index_page": "269n",
        "source_file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
            "第9章脚注1，印刷页269",
            "line 91; print p. 269 n. 1",
            "while a bourgeois, Andrea Stazio, left nearly 200 ducats for further building and decoration. Some of this was spent on pictures in the choir painted by a remarkable group of artists that included Piazzetta, Sebastiano Ricci and Tiepolo. Unfortunately, Stazio’s will in the Archivio di Stato (Sezione Notarile, Atti Giovanni Zon 1283:27) gives us no information about who actually commissioned these pictures.",
            "Haskell称Andrea Stazio遗留近200达克特用于S. Stae后续营建和装饰；部分款项用于合唱席画作，但遗嘱没有说明这些画作的委托者。",
        ),
        "name_rows": [
            ("索引姓名", "Stazio, Andrea", "S1，S.csv#197"),
            ("脚注姓名", "Andrea Stazio", "S2，第9章，p.269 n.1，L91"),
        ],
        "relation_ids": [
            "st-chp9-p269-n01-stae-choir-pictures",
            "st-chp9-p269-n01-stazio-bequest",
        ],
        "description_zh": (
            "本卡登记书后索引作“Stazio, Andrea”、第9章脚注具名的Andrea Stazio。"
            "Haskell称他遗留近200达克特用于S. Stae的后续营建与装饰，部分款项用于合唱席画作；"
            "同一脚注明确说遗嘱没有说明是谁委托这些画作，故不将Stazio写作画作委托人。"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Andrea Stazio, indexed as “Stazio, Andrea” and named in a Chapter 9 footnote. "
            "Haskell says he left nearly 200 ducats for further building and decoration at S. Stae, part of which was spent on choir pictures. "
            "The same note explicitly says the will does not identify who commissioned those pictures, so this card does not name Stazio as their commissioner. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "两条候选区分Stazio遗赠款项与合唱席画作支出；委托者未明，关系候选保留此缺口并待S6。"
        ),
        "context_en": (
            "The two candidates distinguish Stazio's bequest from spending on the choir pictures. "
            "The commissioner is unidentified; the candidates retain that gap for S6."
        ),
    },
    {
        "candidate": "cand-2511",
        "group": "new-person:nicholas-stone-02907ebe1f",
        "ku": "units/persons/nicholas-stone",
        "card": "04-knowledge/units/persons/nicholas-stone.md",
        "name_zh": "尼古拉斯·斯通",
        "name_en": "Nicholas Stone",
        "index_entry": "S.csv#200",
        "index_name": "Stone, Nicholas",
        "index_page": "37",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
        "book_source": registrar.book_source(
            "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
            "第2章第2节，印刷页37，行66–67",
            "lines 66–67; print p. 37",
            "We hear from the English sculptor Nicholas Stone that when the artist was carving the bust of Thomas Baker (the man entrusted with conveying to Bernini\nVan Dyck’s triple portrait of Charles I) ‘. . . it fell out that his patrone the Pope came to here of itt who sent Cardinal Barberine to forbid him . . . for the Pope would have no other picture sent into England from this hand but his Maity’.3",
            "Haskell将一段关于Bernini、Thomas Baker和教皇干预的嵌套引文归于英国雕塑家Nicholas Stone；Stone的原始记述未在本轮独立查阅。",
        ),
        "name_rows": [
            ("索引姓名", "Stone, Nicholas", "S1，S.csv#200"),
            ("正文姓名", "Nicholas Stone", "S2，第2章，p.37，L66"),
        ],
        "relation_ids": ["st-chp2-secii-l62-69-nicholas-stone-baker-bust-account"],
        "description_zh": (
            "本卡登记书后索引作“Stone, Nicholas”、第2章称为英国雕塑家的Nicholas Stone。"
            "Haskell将一段关于Bernini雕刻Thomas Baker胸像及教皇干预的嵌套引文归于Stone；"
            "Stone的原始记述未在本轮独立查阅，卡片保留Haskell的转引层级。中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Nicholas Stone, indexed as “Stone, Nicholas” and described in Chapter 2 as an English sculptor. "
            "Haskell attributes to Stone a nested account concerning Bernini carving Thomas Baker's bust and the Pope's intervention. "
            "Stone's original account was not independently consulted; the card preserves Haskell's reporting layer. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "关系候选是Haskell转引Stone关于Bernini为Thomas Baker制作胸像及教皇派人阻止的记述；不将引文直接当作已核读原件。"
        ),
        "context_en": (
            "The relation candidate is Haskell's report of Stone's account of Bernini making Thomas Baker's bust and the Pope sending an order to stop him. "
            "The nested quotation is not treated as an independently read original."
        ),
    },
]


if __name__ == "__main__":
    raise SystemExit(registrar.main())
