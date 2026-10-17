from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
UNITS = ROOT / "04-knowledge" / "units"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
MENTION_PATH = TABLES / "mentions.csv"
STATEMENT_PATH = TABLES / "book-statements.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
KIND_DIRS = {"archive": "archives", "institution": "institutions", "person": "persons", "place": "places", "term": "terms", "work": "works"}
DATE = "2026-10-16"


def src(chapter, page, file, lines, quote, summary, location_note=""):
    return card_writer.source(chapter, page, file, lines, quote, summary, location_note)


BATCHES = {
    "person": [
        {
            "group": "new-person:bouchard-jacques-jean-19fda1229d",
            "members": ["cand-0419"],
            "slug": "jean-jacques-bouchard",
            "name_zh": "让-雅克·布沙尔",
            "name_en": "Jean-Jacques Bouchard",
            "description_zh": "本书称 Jean-Jacques Bouchard 为法国 libertin，并记他出席巴贝里尼宫歌剧演出；第4章将他列入 Cassiano dal Pozzo 的法国友人圈。这里仅按本书指称登记人物，不补入出生、死亡或其他传记事实。",
            "description_en": "Haskell identifies Jean-Jacques Bouchard as a French libertin present at an opera performance in the Barberini palace and later includes him among Cassiano dal Pozzo’s French friends. This unit records the person as named in the book and adds no unsupported dates or biography.",
            "context_zh": "第2章 p.56 记 Bouchard 在宫中歌剧演出现场；第4章 pp.107–108 讨论他与 Cassiano 的交往，并区分其较为克制的“official”谈话语境与私人文稿。",
            "context_en": "Chapter 2 p. 56 places Bouchard at an opera performance in the palace. Chapter 4 pp. 107–108 discusses his association with Cassiano and distinguishes the restrained “official” conversation from the private papers described in the account.",
            "boundary_zh": "“French libertin”是本书的称述；卡片不据此补写具体信仰、私生活细节或完整生平。",
            "boundary_en": "“French libertin” is Haskell’s description. The card does not infer particular beliefs, private conduct, or a complete biography from that label.",
            "type_notes_zh": "索引主项 B.csv#266 给出全名 Jean-Jacques Bouchard；S2 将第2、4、7章的相同全名与简称提及映射到此候选。",
            "type_notes_en": "The B.csv#266 index entry supplies the full name Jean-Jacques Bouchard. S2 maps the full-name and surname references in Chapters 2, 4, and 7 to this candidate.",
            "sources": [
                src("2", "56", "02_CHP-2_sec_iv.md", "148", "Jean-Jacques Bouchard, the French ’libertin’", "第2章称 Bouchard 为法国 libertin，并将其置于巴贝里尼宫歌剧演出现场。"),
                src("4", "107", "04_CHP-4_sec_ii.md", "106", "the French ‘libertins’, Jean-Jacques Bouchard, Gabriel Naudé and many others could readily testify.", "第4章将 Bouchard 与 Naudé 等置于法国 libertins 语境，并以其著述讨论 Cassiano 的友人圈。"),
                src("4", "108", "04_CHP-4_sec_ii.md", "110", "the ‘official’ Bouchard ‘whose conversation was so restrained’", "第4章转述 Dupuy 只认识较克制的“official” Bouchard；这是转述语境，不等同于对其全部言行的判定。"),
            ],
        },
        {
            "group": "new-person:carlevarijs-luca-3987dbd340",
            "members": ["cand-0554", "cand-0558"],
            "slug": "luca-carlevarijs",
            "name_zh": "卢卡·卡莱瓦里斯",
            "name_en": "Luca Carlevarijs",
            "description_zh": "本书以 Luca Carlevarijs／Carlevarijs 指称威尼斯画家，并记其绘制城市景观及为来访使节记录入城场景。索引中的 regatta 子目与正文中的 Luca Carlevarijs 属同一人物；相关具体作品分别登记为作品，不并入人物卡。",
            "description_en": "Haskell refers to the Venetian painter as Luca Carlevarijs or Carlevarijs, describing his city views and his work recording visiting ambassadors’ entries into Venice. The regatta index subentry and the prose reference to Luca Carlevarijs identify the same person; the individual works remain separate units.",
            "context_zh": "第8章 p.227–228 引述 Marchesini 对 Carlevarijs 景观画的评价；第10章 pp.276–277 记其受托记录 Lord Manchester 入城并绘制 Frederick IV 庆典赛舟；第13章 p.332 将其《Le Fabriche e Vedute di Venetia》（1703）列为面向旅行者的图书插图出版物。",
            "context_en": "Chapter 8 pp. 227–228 quotes Marchesini on Carlevarijs’s views. Chapter 10 pp. 276–277 records the Lord Manchester entry commission and the regatta painting for Frederick IV. Chapter 13 p. 332 names his Le Fabriche e Vedute di Venetia (1703) as an illustrated publication designed for travellers.",
            "boundary_zh": "人物身份组仅含 cand-0554 与 cand-0558；Manchester、Colloredo 入城画、Frederick IV 赛舟及《Le Fabriche》均为不同对象。",
            "boundary_en": "The person group contains cand-0554 and cand-0558 only. The Manchester and Colloredo entry paintings, the regatta, and Le Fabriche are distinct objects.",
            "type_notes_zh": "名称：索引 C.csv#78 主项为 Carlevarijs, Luca，C.csv#82 的“Regatta in honour of Frederick IV of Denmark”是人物主项下的作品子目。",
            "type_notes_en": "Name: the C.csv#78 main entry is Carlevarijs, Luca. C.csv#82, “Regatta in honour of Frederick IV of Denmark,” is a work subentry under this person, not another person.",
            "sources": [
                src("8", "227", "08_CHP-8_sec_ii.md", "203", "Conti was trying to get two further views by Carlevarijs to add to the three that he already owned", "第8章称 Conti 希望再购两幅 Carlevarijs 景观画，以补全已有三幅。"),
                src("10", "276", "10_CHP-10_intro.md", "10–12", "In 1707 the Ambassador himself, Lord.\nManchester, returned to Venice on a second official visit and commissioned Luca\nCarlevarijs to record his entry.", "第10章称 Lord Manchester 于1707年委托 Carlevarijs 记录其入城；来源 OCR 的断行保留。"),
                src("10", "277", "10_CHP-10_intro.md", "18", "while Luca Carlevarijs painted for him the regatta that had been offered in his honour", "第10章称 Carlevarijs 为 Frederick IV 绘制向其致敬的赛舟场景。"),
                src("13", "332", "13_CHP-13_intro.md", "12", "books like Carlevarijs’Le Fabriche e Vedute di Venetia (1703)", "第13章将 Carlevarijs 的1703年图书列为当时面向旅行者的书籍插图出版物之一。", "该行 OCR 的书名前空格缺失；引文按来源字面保留。"),
            ],
        },
        {
            "group": "new-person:baptiste-colbert-jean-ffec9f31bd",
            "members": ["cand-0800"],
            "slug": "jean-baptiste-colbert",
            "name_zh": "让-巴蒂斯特·柯尔贝尔",
            "name_en": "Jean-Baptiste Colbert",
            "description_zh": "本书围绕路易十四时期的卢浮宫建设与意大利艺术交流讨论 Colbert；C.csv#330 索引主项提供全名 Jean-Baptiste Colbert。此卡只收录书中提及的同一人物，不扩写完整官职履历。",
            "description_en": "Haskell discusses Colbert in the context of Louis XIV’s Louvre projects and exchanges with Italian artists. The C.csv#330 index entry supplies the full name Jean-Baptiste Colbert. This unit records that source-defined person without adding a complete office biography.",
            "context_zh": "第6章 p.153 记 Colbert 与国王致 Bernini 的信件；第7章 pp.186–189 讨论他与 Louis XIV 的卢浮宫规划、对建筑师 Le Vau 的态度及其行政考量；后记 p.403 再将他列入画作传递经手人。",
            "context_en": "Chapter 6 p. 153 mentions letters from Colbert and the King to Bernini. Chapter 7 pp. 186–189 discusses his Louvre planning with Louis XIV, his view of Le Vau, and administrative concerns. The postscript p. 403 names him in the transmission of a painting.",
            "boundary_zh": "后记 p.403 的“through Colbert”表示作品经由 Colbert 转交，不据此称他为创作者、委托人或最终收藏者。",
            "boundary_en": "The postscript’s phrase “through Colbert” describes an intermediary role in the painting’s transmission; it does not make him its creator, commissioner, or final owner.",
            "type_notes_zh": "索引全名与正文多处姓氏形式、Louis XIV／Mazarin 的同一政治语境相符；书内依据仅支持人物对齐。",
            "type_notes_en": "The indexed full name corresponds to the surname references in the shared Louis XIV and Mazarin context; the book evidence supports identity alignment only.",
            "sources": [
                src("6", "153", "06_CHP-6_sec_i.md", "84", "The letters from Colbert and from the King himself were exceedingly flattering.", "第6章称重建卢浮宫期间 Colbert 与国王致 Bernini 的信件措辞十分恭维。"),
                src("7", "186", "07_CHP-7_sec_i.md", "222", "Colbert, who replaced him, had been employed by Mazarin", "第7章将 Colbert 置于 Mazarin 与 Louis XIV 的政治交接语境。"),
                src("7", "187", "07_CHP-7_sec_i.md", "227", "Soon after the onset of his rule Louis and Colbert began to consider proposals for building the eastern’front of the royal palace.", "第7章称 Louis 与 Colbert 讨论王宫东立面的方案。"),
                src("7", "188", "07_CHP-7_sec_i.md", "233", "He too was anxious for grandeur, but as a practical administrator he was just as concerned with expense", "第7章描述 Colbert 对宫殿宏大方案与支出、房间安排的并重考量。"),
                src("20", "403", "20_CHP-20Postscript.md", "111–112", "through Colbert and the Abate Luigi Strozzi", "后记把 Colbert 列为 Franceschini 画作传递链中的经手人之一。"),
            ],
        },
        {
            "group": "new-person:denmark-frederick-iv-of-65aed0cc97",
            "members": ["cand-1078"],
            "slug": "frederick-iv-of-denmark",
            "name_zh": "丹麦的腓特烈四世",
            "name_en": "Frederick IV of Denmark",
            "description_zh": "哈斯克尔称 Frederick IV of Denmark 于1709年到访威尼斯，并记其委托 Rosalba Carriera 创作十二幅粉彩肖像；同段提到 Carlevarijs 为其庆典赛舟作画。此卡只指该人物，不把肖像或赛舟作品并入人物。",
            "description_en": "Haskell says Frederick IV of Denmark visited Venice in 1709 and commissioned twelve pastel portraits from Rosalba Carriera. The same passage mentions Carlevarijs’s regatta painting for the celebration in his honour. This unit represents the person only; the portraits and regatta remain separate works.",
            "context_zh": "第10章 p.277 将到访置于其与瑞典战争期间的假期语境，并分别叙述粉彩肖像委托和庆典赛舟。",
            "context_en": "Chapter 10 p. 277 places the visit during his war with Sweden and separately describes the pastel commission and the ceremonial regatta.",
            "boundary_zh": "人物身份依据原书全名与丹麦称谓；卡片不补写统治年表、外交关系或未由本书支持的生平。",
            "boundary_en": "The identity follows the full name and Danish designation used in the book; this card adds no reign chronology, diplomatic history, or unsupported biography.",
            "type_notes_zh": "索引 F.csv#93 与第10章 p.277 的全名提及一致；此组只含 cand-1078。",
            "type_notes_en": "F.csv#93 matches the full-name reference in Chapter 10 p. 277; this identity group contains cand-1078 only.",
            "sources": [
                src("10", "277", "10_CHP-10_intro.md", "18", "In 1709 Frederick IV of Denmark took time off from his war with Sweden for a holiday in Venice", "第10章给出 Frederick IV of Denmark 全名，并称其于1709年在与瑞典战争期间到威尼斯度假。"),
                src("10", "277 n. 5", "10_CHP-10_intro.md", "499", "the Regatta in honour of Frederick IV of Denmark (1709)", "第10章注5以 Frederick IV of Denmark 名义标识1709年赛舟画题名。"),
            ],
        },
    ],
    "institution": [
        {
            "group": "sg3-institution-accademiadipitturaescultura",
            "members": ["cand-0005"],
            "slug": "academy-of-painting-and-sculpture-venice",
            "name_zh": "威尼斯绘画与雕塑学院",
            "name_en": "Venetian Academy of Painting and Sculpture",
            "description_zh": "哈斯克尔称威尼斯方面早在1724年计划设立绘画与雕塑学院，以吸引经威尼斯领土前往佛罗伦萨、博洛尼亚和罗马的外国旅行者；他将该学院的实际成立时间记为1756年。书中进一步讨论学院的科目等级、奖项活动及其社会语境。",
            "description_en": "Haskell says a plan was made in 1724 to found an Academy of Painting and Sculpture in Venice to attract foreign travellers passing through Venetian territory toward Florence, Bologna, and Rome; he dates the Academy’s establishment to 1756. The book also discusses its hierarchy of subjects, prize-giving sessions, and social context.",
            "context_zh": "第10章 p.329 称 Senate 希望该安排带来商业收益，并记述历史画在科目等级中居首、风景画等被置于较低位置。p.330 记 Andrea Memmo 曾询问威尼斯学院的徽记、名称与守护圣人；第15章称 Pittoni 为 Accademia 主席。后记附录6刊出 Memmo 的相关笔记，并保留 OCR 原文形式。",
            "context_en": "Chapter 10 p. 329 says the Senate hoped the arrangement would yield commercial benefit and describes history painting as dominant in the Academy’s subject hierarchy, with view painting ranked lower. Page 330 records Andrea Memmo’s questions about the Venetian Academy’s device, name, and patron saint; Chapter 15 calls Pittoni president of the Accademia. Appendix 6 reproduces related notes by Memmo, preserving the source OCR form.",
            "boundary_zh": "此卡对应原书所称威尼斯绘画与雕塑学院／Venetian Academy；不与同段作为比较对象的帕尔马学院、巴黎学院或其他城市的学院合并。Memmo 对徽记、名称与守护圣人的问题是其笔记内容，不表示学院已实施相应改革。",
            "boundary_en": "This card represents the Venetian Academy of Painting and Sculpture named in the book. It is distinct from the Parma, Paris, and other city academies mentioned for comparison. Memmo’s questions about the emblem, name, and patron saint are recorded as notes, not as evidence that reforms were implemented.",
            "type_notes_zh": "原语索引形式：Accademia di Pittura e Scultura；书中英文称 Academy of Painting and Sculpture、Venetian Academy。Haskell 所述的1724年计划与1756年成立属于同一机构叙述。",
            "type_notes_en": "Indexed Italian form: Accademia di Pittura e Scultura; Haskell also calls it the Academy of Painting and Sculpture and the Venetian Academy. The 1724 plan and 1756 establishment are presented as phases in the same institutional history.",
            "sources": [
                src("10", "329", "10_CHP-10_sec_ii.md", "255", "As early as 1724 it had been planned to found an Academy of Painting and Sculpture", "第10章记载威尼斯方面不迟于1724年已有创设绘画与雕塑学院的计划。"),
                src("10", "329", "10_CHP-10_sec_ii.md", "255", "When in 1756 the Academy was finally established", "第10章将学院实际成立时间记为1756年。"),
                src("10", "330", "10_CHP-10_sec_ii.md", "261", "the device and the name of the Venetian Academy", "第10章将 Memmo 的问题明确指向 Venetian Academy。"),
                src("15", "361", "15_CHP-15_sec_i.md", "5", "Pittoni, though president of the Accademia", "第15章称 Pittoni 曾任 Accademia 主席；索引将该用例列入本学院主项。"),
                src("19", "394", "19_CHP-19Appendix.md", "183", "l’Impresa della nostra Accademia", "后记附录6转录 Memmo 对“我方学院”徽记及名称的笔记；结合其章节回指和第10章锚点，作为同一威尼斯学院语境。"),
            ],
        }
    ],
    "archive": [
        {
            "group": "archive-group-bf88b7762ce2",
            "members": ["cand-0555"],
            "slug": "carlevarijs-le-fabriche-1703",
            "name_zh": "《威尼斯建筑与景观图》（1703）",
            "name_en": "Le Fabriche e Vedute di Venetia (1703)",
            "description_zh": "第13章以 Carlevarijs’ Le Fabriche e Vedute di Venetia (1703) 为例，称其为面向旅行者的图书插图出版物。此档案卡指该书目对象，不把其中每幅图版拆成已核实作品，也不判断 Carlevarijs 在设计、制版、印刷或出版中的具体角色。",
            "description_en": "Chapter 13 cites Carlevarijs’ Le Fabriche e Vedute di Venetia (1703) as an illustrated book designed for travellers. This archive unit represents the publication as cited; it does not inventory individual plates or assign Carlevarijs a specific design, engraving, printing, or publishing role.",
            "context_zh": "第13章 p.332 将该书与 Domenico Lovisa 于1720年出版的另一部威尼斯图像书并列，讨论18世纪前期艺术家参与书籍插图的现象。",
            "context_en": "Chapter 13 p. 332 places the book alongside Domenico Lovisa’s 1720 Venetian publication in a discussion of artists’ work in book illustration during the early eighteenth century.",
            "boundary_zh": "标题与年份按原书；Haskell 的所有格写法不区分绘图、雕版、印刷或出版责任，本卡不据此建立创作者关系。",
            "boundary_en": "The title and year follow the book. Haskell’s possessive wording does not distinguish drawing, engraving, printing, or publishing responsibility, so this card does not assert a creator relation.",
            "type_notes_zh": "对象类型：archive（具体出版物）；原书称其为 books，并与面向旅行者的图像出版物相连。",
            "type_notes_en": "Object type: archive (a specific publication); Haskell calls it a book and associates it with illustrated publications for travellers.",
            "sources": [
                src("13", "332", "13_CHP-13_intro.md", "12", "books like Carlevarijs’Le Fabriche e Vedute di Venetia (1703)", "第13章以该书名和1703年出版年份为例讨论图书插图。", "源行 OCR 缺少 Carlevarijs’ 与 Le 之间的空格，按原样引用。"),
                src("13", "332", "13_CHP-13_intro.md", "12", "Both of these publications were designed for travellers", "第13章称列举的两种出版物均面向旅行者。"),
            ],
        }
    ],
    "work": [
        {
            "group": "sg3-work-carlevarijs-colloredo-entry-1726",
            "members": ["cand-0556"],
            "slug": "carlevarijs-colloredo-entry-1726",
            "name_zh": "《科洛雷多伯爵入城图》（1726）",
            "name_en": "Entry of the Count of Colloredo (1726)",
            "description_zh": "哈斯克尔注5称 Carlevarijs 绘制《科洛雷多伯爵入城图》，并将人物称为帝国大使、作品定年1726年；注释报告该画当时位于 Dresden。作品身份以这条书内描述为限。",
            "description_en": "Haskell’s note 5 says Carlevarijs painted the Entry of the Count of Colloredo, identifies the Count as an Imperial ambassador, and dates the work to 1726; the note reports the picture in Dresden at the time of its cited source. The work identity is limited to this source-defined description.",
            "context_zh": "第10章 p.277 注5将该作与 Lord Manchester 入城图、Frederick IV 庆典赛舟并列；三者是不同作品。",
            "context_en": "Chapter 10 p. 277 n. 5 lists this work alongside the Lord Manchester entry and the Frederick IV regatta; these are distinct works.",
            "boundary_zh": "原书没有给出 Count of Colloredo 的名字，也未明说委托关系；Dresden 是书内当时地点报告，不表示现今馆藏。",
            "boundary_en": "The book gives no first name for the Count and does not state a commission. Dresden is a source-era location report, not a current holding claim.",
            "type_notes_zh": "题名按 C.csv#80 索引子目及注5描述；创作者为原书所称 Carlevarijs；年份1726。",
            "type_notes_en": "The title follows C.csv#80 and note 5; Carlevarijs is the painter named by the source; the stated year is 1726.",
            "sources": [
                src("10", "277 n. 5", "10_CHP-10_intro.md", "499", "Carlevarijs painted the Entry of the Count of Colloredo, the Imperial ambassador (1726)", "第10章注5给出作品、画家、人物称谓和1726年。"),
                src("10", "277 n. 5", "10_CHP-10_intro.md", "499", "this picture is now in Dresden", "同一注释称该画当时位于 Dresden；所引 Mauroner 未在本批独立查阅，不据此核定现藏。"),
            ],
        },
        {
            "group": "sg3-work-carlevarijs-manchester-entry-1707",
            "members": ["cand-0557", "cand-8839"],
            "slug": "carlevarijs-manchester-entry-1707",
            "name_zh": "《曼彻斯特勋爵入城图》（1707）",
            "name_en": "Lord Manchester’s Entry into Venice (1707)",
            "description_zh": "第10章正文称 Lord Manchester 于1707年第二次正式访问威尼斯时委托 Luca Carlevarijs 记录其入城；注5以《Lord Manchester’s Entry into Venice (1707)》指称该画。此卡登记书内可识别的作品，不据旧馆藏报告确认现存版本。",
            "description_en": "Chapter 10 says Lord Manchester commissioned Luca Carlevarijs to record his entry into Venice during a second official visit in 1707; note 5 names the painting Lord Manchester’s Entry into Venice (1707). This card records the work identifiable in the book and does not use the older holding report to verify a surviving version.",
            "context_zh": "p.276 正文提供访问与委托语境；p.277 注5补出作品题名和年份。注2称“当时”位于 Birmingham City Art Gallery，但所引 Nisser 未在本批独立查阅。",
            "context_en": "The p. 276 narrative supplies the visit and commission context; p. 277 n. 5 supplies the title and year. Note 2 reports the picture at Birmingham City Art Gallery at the time of its cited source, but Nisser was not independently consulted in this batch.",
            "boundary_zh": "cand-0557（索引子目）与 cand-8839（正文候选）指同一作品；Lord Manchester 的个人身份仍待证。旧地点报告不等于当前馆藏验证。",
            "boundary_en": "Index candidate cand-0557 and prose candidate cand-8839 refer to the same work. Lord Manchester’s personal identity remains unresolved; the older location report is not current-holding verification.",
            "type_notes_zh": "作品题名按第10章 p.277 注5；委托叙述来自 p.276 正文，仍是待 S6 裁决的关系候选。",
            "type_notes_en": "The work title follows Chapter 10 p. 277 n. 5; the commission account is in the p. 276 narrative and remains a relation candidate for S6 review.",
            "sources": [
                src("10", "276", "10_CHP-10_intro.md", "10–12", "In 1707 the Ambassador himself, Lord.\nManchester, returned to Venice on a second official visit and commissioned Luca\nCarlevarijs to record his entry.", "第10章记 Lord Manchester 1707年访问威尼斯并委托 Carlevarijs 记录其入城；OCR 断行照录。"),
                src("10", "277 n. 5", "10_CHP-10_intro.md", "499", "Lord Manchester’s Entry into Venice (1707)", "第10章注5为该作品给出明确题名与年份。"),
                src("10", "276 n. 2", "10_CHP-10_intro.md", "493", "The picture is now in the Birmingham City Art Gallery", "注2报告该画在 Nisser 1937 所记时间的位置；本批未独立查阅该书或核定当前馆藏。"),
            ],
        },
        {
            "group": "sg3-work-carlevarijs-regatta-frederick-iv-1709",
            "members": ["cand-8845"],
            "slug": "carlevarijs-regatta-frederick-iv-1709",
            "name_zh": "《为丹麦腓特烈四世举行的赛舟图》（1709）",
            "name_en": "Regatta in honour of Frederick IV of Denmark (1709)",
            "description_zh": "第10章称 Luca Carlevarijs 为 Frederick IV 绘制向其致敬的赛舟场景；注5以《Regatta in honour of Frederick IV of Denmark (1709)》指称该画。作品卡仅表达书内可识别的作品身份。",
            "description_en": "Chapter 10 says Luca Carlevarijs painted a regatta for Frederick IV, offered in his honour; note 5 names the painting Regatta in honour of Frederick IV of Denmark (1709). This card records only the work identity established in the book.",
            "context_zh": "正文将作画置于 Frederick IV 1709年访威尼斯的庆典语境中。注2报告作品当时位于“the Fredericksborg, Copenhagen”，并引 Mauroner 1945；本批未独立查阅所引文献。",
            "context_en": "The narrative places the painting in the context of Frederick IV’s 1709 visit to Venice. Note 2 reports the picture at “the Fredericksborg, Copenhagen,” citing Mauroner 1945; that reference was not independently consulted in this batch.",
            "boundary_zh": "不把注释中的 Fredericksborg 拼写扩定为特定城堡或博物馆，也不将书内旧地点写成现今馆藏。",
            "boundary_en": "The note’s spelling “Fredericksborg” is not expanded into a specific castle or museum, and the source-era location is not presented as a current holding.",
            "type_notes_zh": "作品题名、创作者和1709年均由第10章正文与注5支持；正式创作、致敬及地点关系待 S6 按证据逐项审查。",
            "type_notes_en": "The p. 277 narrative and note 5 support the work title, painter, and year 1709; creation, honour, and location relations remain for item-level S6 review.",
            "sources": [
                src("10", "277", "10_CHP-10_intro.md", "18", "while Luca Carlevarijs painted for him the regatta that had been offered in his honour", "第10章称 Carlevarijs 为 Frederick IV 绘制向其致敬的赛舟画。"),
                src("10", "277 n. 5", "10_CHP-10_intro.md", "499", "the Regatta in honour of Frederick IV of Denmark (1709)", "第10章注5提供作品题名与1709年。"),
                src("10", "277 n. 2", "10_CHP-10_intro.md", "496", "The picture is now in the Fredericksborg, Copenhagen", "注2报告其在 Mauroner 1945 所记时间的位置；所引书未在本批独立查阅，地点身份及当前馆藏不核定。"),
            ],
        },
    ],
    "place": [
        {
            "group": "sg3-place-cand-0947",
            "members": ["cand-0947"],
            "slug": "dresden",
            "name_zh": "德累斯顿",
            "name_en": "Dresden",
            "description_zh": "本书以 Dresden 指称同一城市地点，并将其置于萨克森选侯及波兰国王宫廷、城市建筑与艺术收藏的历史语境中。此卡登记城市本身，不与 Dresden 宫廷、画廊或具体建筑混为一体。",
            "description_en": "Haskell uses Dresden for the same city in accounts of the Saxon electoral and Polish royal court, urban architecture, and art collecting. This unit represents the city itself and keeps it distinct from the Dresden court, gallery, and individual buildings.",
            "context_zh": "第10章 p.277 注5报告 Colloredo 入城画位于 Dresden；p.294 叙述 Augustus II 的宫廷与城市建设；全书其他章节继续以 Dresden 指涉城市及相关目的地。",
            "context_en": "Chapter 10 p. 277 n. 5 reports the Colloredo entry picture in Dresden. Page 294 discusses Augustus II’s court and the city’s development; other chapters use Dresden for the city and destinations associated with it.",
            "boundary_zh": "“Dresden”在不同陈述中也可作为宫廷或馆藏地点的语境称呼；本卡不将具体宫廷机构、画廊或建筑并入城市实体。",
            "boundary_en": "“Dresden” also appears as contextual shorthand for the court or collection location in particular statements; the city unit does not absorb the court institution, gallery, or buildings.",
            "type_notes_zh": "类型为 place；书内地点名称按原文形式 Dresden 保留。",
            "type_notes_en": "Type: place; the source spelling Dresden is retained.",
            "sources": [
                src("10", "277 n. 5", "10_CHP-10_intro.md", "499", "this picture is now in Dresden", "第10章注5以 Dresden 报告一件 Carlevarijs 入城画的书内地点。", "所引 Mauroner 1945 未在本批独立查阅。"),
                src("10", "294", "10_CHP-10_intro.md", "293", "had made his court the most brilliant in Europe, and his munificent architectural policy was transforming Dresden into a city of dazzling beauty", "第10章将 Augustus II 的宫廷与 Dresden 城市建设分别表述。"),
            ],
        },
        {
            "group": "sg3-place-cand-0086",
            "members": ["cand-0086"],
            "slug": "alticchiero-querini-villa-estate",
            "name_zh": "阿尔蒂基耶罗奎里尼庄园",
            "name_en": "Querini’s Villa Estate at Alticchiero",
            "description_zh": "哈斯克尔称 Angelo Querini 将余生大部分时间用于建造和装饰其位于 Alticchiero、距 Padua 一两英里的乡间住宅；他说明该住宅在写作时早已被夷平。此地点卡按原书的 villa／country house 与其园林所构成的庄园语境登记，不认定其现存建筑或遗址。",
            "description_en": "Haskell says Angelo Querini devoted most of his remaining life to building and decorating his country house at Alticchiero, a mile or two from Padua; the author reports that it had long since been razed by the time of his account. This place unit follows the villa/country-house and garden-estate context in the book and does not assert a surviving building or ruin.",
            "context_zh": "第15章 pp.369–370 主要依据 Giustiniana Wynne-Rosenberg 的记述介绍 Alticchiero：住宅以简朴、实用为特点，园林则由规整布局、植物、纪念性构件及雕塑组成。Haskell 将住宅与园林都置于 Querini 的哲学和审美表达中。",
            "context_en": "Chapter 15 pp. 369–370 describes Alticchiero chiefly through Giustiniana Wynne-Rosenberg’s account: the house was presented as simple and convenient, while the garden combined formal outlines, plants, monuments, and sculpture. Haskell treats both the house and garden as expressions of Querini’s philosophical and aesthetic interests.",
            "boundary_zh": "卡片指向 Alticchiero 乡间别墅庄园，不把其中的 Houdon 胸像、城市图、版画、神庙、祭坛、雕塑或具体园林构件并入地点本体；住宅早已被毁是 Haskell 的来源时态报告。",
            "boundary_en": "The unit represents the Alticchiero country-house estate. Houdon busts, city plans, prints, temples, altars, sculptures, and specific garden features remain separate objects; the report that the house had been razed is retained as Haskell’s source-era statement.",
            "type_notes_zh": "类型：place。原书以 Alticchiero 指该乡间住宅地点，并在同段区分 villa 与 gardens；此卡采用庄园级范围，未另行登记单件建筑或花园构件。",
            "type_notes_en": "Type: place. Haskell uses Alticchiero for the country-house site and distinguishes the villa from its gardens in the narrative; this card uses the estate-level scope and does not register individual structures or garden features.",
            "sources": [
                src("15", "369", "15_CHP-15_sec_ii.md", "53", "Most of his life was thereafter devoted to building and decorating his remarkable country house at Alticchiero, a mile or two from Padua.", "第15章给出 Querini 的乡间住宅名称、建造活动及距 Padua 的约略距离。"),
                src("15", "369", "15_CHP-15_sec_ii.md", "55", "It is from her rapturous account that we know most of Alticchiero, which has long since been razed to the ground.", "Haskell 称其对 Alticchiero 的主要描述来自 Wynne-Rosenberg，并报告住宅在写作前早已被夷平。"),
                src("15", "369", "15_CHP-15_sec_ii.md", "57", "the arrangement is as simple and convenient as possible", "Wynne-Rosenberg 经 Haskell 引述的住宅描述强调简朴与便利；不据此推断具体建筑风格。"),
                src("15", "369", "15_CHP-15_sec_ii.md", "57", "the influence of both men is felt throughout the villa and gardens", "引文将 Voltaire 与 Rousseau 的影响置于 villa 与 gardens 的语境中。"),
                src("15", "370", "15_CHP-15_sec_ii.md", "63", "The garden was even more important than the house as an expression of Querini’s taste.", "第15章明确区分 garden 与 house，并说明园林对于 Querini 审美表达的重要性。"),
            ],
        },
    ],
    "term": [
        {
            "group": "sg3-term-cand-6267",
            "members": ["cand-6267"],
            "slug": "decline-of-roman-patronage",
            "name_zh": "罗马艺术赞助的衰退",
            "name_en": "The Decline of Roman Patronage",
            "description_zh": "第6章以“The Decline of Roman Patronage”为章题，并称罗马艺术整体遭遇具有持久影响的打击；正文将经济、政治、瘟疫、饥荒、死亡及审美变化等列为因素，也记述 Innocent X 时期仍有“what patronage there was”。此卡记录作者的章节框架和书内用法，不把“衰退”处理为经独立验证、量化或意味着赞助完全停止的历史结论。",
            "description_en": "Chapter 6 is headed “The Decline of Roman Patronage” and says that the arts in Rome suffered a blow with lasting consequences. The narrative lists economic, political, plague, famine, death, and fashion-related factors, while also referring to “what patronage there was” under Innocent X. This unit records the author’s chapter framing and source usage; it does not treat “decline” as an independently verified, quantified, or total cessation of patronage.",
            "context_zh": "p.146 标题给出“衰退”框架；同页叙述称多种因素共同造成艺术变化。p.147 提到卡斯特罗战争及后续财政和政治背景，并称教宗本人仍安排当时尚存的赞助。",
            "context_en": "The p. 146 heading supplies the decline framing, and the same page attributes change in the arts to multiple factors. Page 147 discusses the War of Castro and later financial and political circumstances, while saying the Pope directed the patronage that remained.",
            "boundary_zh": "该术语组只记录本书的章节命名与论述语境；不将其改写为连续、均质或可量化的历史趋势，也不推断罗马艺术赞助已完全中断。",
            "boundary_en": "This term unit records the book’s chapter title and narrative context. It does not convert them into a continuous, uniform, or quantified historical trend, or infer that artistic patronage in Rome ceased altogether.",
            "type_notes_zh": "类型：term。原文词形为“The Decline of Roman Patronage”；中文题名为语义对应的工作译名。此处表达作者的分析框架，不是另立一个特定年份的事件。",
            "type_notes_en": "Type: term. The source wording is “The Decline of Roman Patronage”; the Chinese title is a working translation. It expresses the author’s analytical framing, not a discrete event dated to a particular year.",
            "sources": [
                src("6", "146", "06_CHP-6_intro.md", "5", "THE DECLINE OF ROMAN PATRONAGE", "第6章印刷标题将本章主题表述为罗马赞助的衰退。"),
                src("6", "146", "06_CHP-6_sec_i.md", "3", "The arts as a whole received a blow which had the most lasting consequences.", "正文称罗马艺术整体遭受了持久影响的打击；其原因在后文由多因素展开。"),
                src("6", "146", "06_CHP-6_sec_i.md", "3", "Many factors were involved, great and small:", "正文明确称变化涉及大小不同的多项因素。"),
                src("6", "146", "06_CHP-6_sec_i.md", "4", "The decline had already begun some three years earher", "正文将衰退起点回溯至卡斯特罗战争爆发前三年左右；OCR 拼写按源文件保留。"),
                src("6", "147", "06_CHP-6_sec_i.md", "13–24", "Thus it was the Pope himself who directed what patronage there was.", "第6章仍称 Innocent X 本人安排当时尚存的艺术赞助；该表述限制了“衰退”不能被理解为赞助全无。"),
            ],
        }
    ],
}


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line]


def get_group(row):
    match = re.search(r"group=([^;| ]+)", row.get("resolution_note", ""))
    return match.group(1) if match else None


def relation_stats(member_ids, statements):
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in member_ids or row.get("object_candidate_id") in member_ids
    ]
    return len(direct), sum(bool(row.get("qualifiers", {}).get("relation_candidate")) for row in direct)


def update_result_counts(result, candidates, alignments, manifest, mentions, statements):
    stats = sync.summarize_by_type(candidates, alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result = sync.update_result(result, stats, totals, len(manifest))
    external_count = sum(bool(row.get("external_source")) for row in alignments)
    replacements = [
        (r"^\| \[全书对齐\].*$", f"| [全书对齐](../tables/alignment.csv) | {sync.fmt(len(alignments))} 条：{sync.fmt(totals['total'])} 条候选决定记录及 {sync.fmt(external_count)} 条外部身份记录；候选决定数见下表 |"),
        (r"^\| \[提及账本\].*$", f"| [提及账本](../tables/mentions.csv) | {sync.fmt(len(mentions))} mentions |"),
        (r"^\| \[原书断言及关系候选\].*$", f"| [原书断言及关系候选](../tables/book-statements.jsonl) | {sync.fmt(len(statements))} statements；relation_candidate true {sync.fmt(sum(bool(x.get('qualifiers', {}).get('relation_candidate')) for x in statements))}、false {sync.fmt(sum(x.get('qualifiers', {}).get('relation_candidate') is False for x in statements))}、unset {sync.fmt(sum('relation_candidate' not in x.get('qualifiers', {}) for x in statements))} |"),
    ]
    for pattern, value in replacements:
        result, count = re.subn(pattern, value, result, count=1, flags=re.M)
        assert count == 1, pattern
    status = (
        f"**当前状态：全书 S2 语义处理已完成，尚未独立语义验收；S3 候选决定账本已按收口标准核对，"
        f"{sync.fmt(totals['total'])} 个候选均有唯一决定、说明与过程引用。{sync.fmt(totals['undecided'])} 项明确保留为待证，"
        f"其身份问题尚未解决；S4 KU 登记处理中。** "
        f"{sync.fmt(totals['total'])} 个候选决定行中，same={sync.fmt(totals['same_candidates'])}（指向{sync.fmt(totals['same_kus'])}个既有 KU）、"
        f"new={sync.fmt(totals['new_candidates'])}（{sync.fmt(totals['new_groups'])}个身份组）、conflict={sync.fmt(totals['conflict'])}、"
        f"excluded={sync.fmt(totals['excluded'])}、undecided={sync.fmt(totals['undecided'])}。"
        f"S4 已登记{sync.fmt(totals['registered_groups'])}组、映射{sync.fmt(totals['registered_members'])}条成员候选；"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组、{sync.fmt(totals['pending_members'])}条映射。"
    )
    result, count = re.subn(r"^\*\*当前状态：.*?S3 已将", status + "S3 已将", result, count=1, flags=re.M)
    assert count == 1
    return result, stats, totals


def main():
    parser = argparse.ArgumentParser(description="Register direct S2 endpoint identity groups in S4, one type per run.")
    parser.add_argument("--type", choices=sorted(BATCHES), required=True)
    parser.add_argument("--group", help="Run one identity group from the selected type batch.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    kind = args.type
    batch = BATCHES[kind]
    if args.group:
        batch = [record for record in batch if record["group"] == args.group]
        assert batch, f"no {kind} record for group={args.group}"

    candidate_fields, candidates = sync.read_csv(CANDIDATE_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id)
    mention_rows = sync.read_csv(MENTION_PATH)[1]
    mention_candidates = {row.get("candidate_id") for row in mention_rows}
    statements = read_jsonl(STATEMENT_PATH)
    manifest_ids = {row["ku_id"] for row in manifest}
    manifest_paths = {row["card_path"] for row in manifest}
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    groups = defaultdict(list)
    registered = defaultdict(list)
    for row in decisions.values():
        if row.get("decision") == "new":
            group = get_group(row)
            assert group, row["candidate_id"]
            groups[group].append(row)
            if row.get("ku_id"):
                registered[group].append(row)

    expected_existing = (len(manifest), sum(bool(row.get("ku_id")) for row in decisions.values()))
    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest = list(manifest)
    cards = []
    direct_total = 0
    relation_total = 0
    for record in batch:
        members = set(record["members"])
        group = record["group"]
        group_rows = groups.get(group, [])
        assert {row["candidate_id"] for row in group_rows} == members, (group, [row["candidate_id"] for row in group_rows])
        assert not registered.get(group), f"group already partly or fully registered: {group}"
        for cid in members:
            candidate = candidate_by_id[cid]
            decision = planned_by_id[cid]
            assert candidate.get("suggested_type") == kind, (cid, candidate.get("suggested_type"), kind)
            assert decision.get("decision") == "new" and not decision.get("ku_id"), cid
            assert get_group(decision) == group
        if not (members & mention_candidates) and not any(
            row.get("subject_candidate_id") in members or row.get("object_candidate_id") in members
            for row in statements
        ):
            raise AssertionError(f"group lacks direct S2 mention or endpoint: {group}")

        slug = record["slug"]
        ku_id = f"units/{KIND_DIRS[kind]}/{slug}"
        rel_path = f"04-knowledge/units/{KIND_DIRS[kind]}/{slug}.md"
        card_path = ROOT / rel_path
        assert not card_path.exists(), card_path
        assert ku_id not in manifest_ids and rel_path not in manifest_paths and rel_path not in accepted
        for item in record["sources"]:
            source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
            assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (cid, item["file"], item["quote"])

        for cid in members:
            planned_by_id[cid]["ku_id"] = ku_id
            planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {group} to {ku_id}."
        planned_manifest.append({
            "ku_id": ku_id,
            "type": kind,
            "canonical_name": record["name_zh"],
            "name_en": record["name_en"],
            "source_task": TASK,
            "card_path": rel_path,
        })
        card_text = card_writer.make_card(record, kind).replace("2026-10-15", DATE)
        cards.append((card_path, rel_path, ku_id, card_text, record))
        direct_n, relation_n = relation_stats(members, statements)
        direct_total += direct_n
        relation_total += relation_n

    planned_stats = sync.summarize_by_type(candidates, planned_alignment)
    planned_totals = {key: sum(row[key] for row in planned_stats.values()) for key in next(iter(planned_stats.values()))}
    assert (len(planned_manifest), sum(bool(row.get("ku_id")) for row in planned_by_id.values())) == (
        expected_existing[0] + len(batch), expected_existing[1] + sum(len(record["members"]) for record in batch)
    )
    for group, rows in groups.items():
        mapped = [row.get("ku_id", "") for row in rows]
        if any(mapped):
            assert all(mapped) and len(set(mapped)) == 1, group
    result_text, _, _ = update_result_counts(
        RESULT_PATH.read_text(encoding="utf-8-sig"), candidates, planned_alignment,
        planned_manifest, mention_rows, statements,
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    batch_lines = [
        f"- `{','.join(record['members'])}` → `{record['group']}` → `{card[2]}`; {dn} direct S2 statements, {rn} relation candidates pending S6."
        for record, card in zip(batch, cards)
        for dn, rn in [relation_stats(set(record["members"]), statements)]
    ]
    label = {"person": "人物", "archive": "文献", "work": "作品", "place": "地点", "term": "术语", "institution": "机构"}[kind]
    summary = (
        f"\n\n### S4 {kind}：Carlevarijs 跨章端点批次（{DATE}）\n\n"
        + "\n".join(batch_lines)
        + f"\n\n本批按类型登记 {label}，每个身份组一张 KU，同组候选映射到同一 `ku_id`。卡片按原书书内证据提供双语名称、等值描述和逐条来源引文。"
        "本批仅登记对象身份及其来源记载，不把 S2 关系候选写成正式关系；待 S6 按端点、方向、语境和证据逐条审查。未开展 S5 补足或外部事实核验。"
        f"\n\nS4 当前已登记{sync.fmt(planned_totals['registered_groups'])}组/{sync.fmt(planned_totals['registered_members'])}条成员映射，尚待登记{sync.fmt(planned_totals['pending_groups'])}组/{sync.fmt(planned_totals['pending_members'])}条。\n"
    )
    result_append = (
        f"\n\n### S4 {kind}：Carlevarijs 跨章端点批次（{DATE}）\n\n"
        + "\n".join(batch_lines)
        + f"\n\n新增{len(batch)}张 {label} KU，成员候选{sum(len(x['members']) for x in batch)}条；本批直接 S2 断言共{direct_total}条，其中{relation_total}条为关系候选，均留待 S6。"
        "本批未新增正式关系或 S5 补足，也未作外部事实核验。"
        f"\n\nS4 当前已登记{sync.fmt(planned_totals['registered_groups'])}组/{sync.fmt(planned_totals['registered_members'])}条候选映射，待登记{sync.fmt(planned_totals['pending_groups'])}组/{sync.fmt(planned_totals['pending_members'])}条。\n"
    )
    result_text += result_append
    process_text += summary

    if args.dry_run:
        print(f"S4 {kind} batch dry-run passed")
        for record, (_, rel_path, ku_id, _, _) in zip(batch, cards):
            print(f"  {','.join(record['members'])} -> {record['group']} -> {ku_id} ({rel_path})")
        print(f"  manifest={len(manifest)} -> {len(planned_manifest)}; groups={planned_totals['registered_groups']}/{planned_totals['pending_groups']}; mappings={planned_totals['registered_members']}/{planned_totals['pending_members']}")
        print(f"  direct S2 statements={direct_total}; relation candidates remain pending={relation_total}; no formal relations added")
        return 0

    for path, _, _, card_text, _ in cards:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    accepted_lines = accepted.splitlines()
    new_paths = sorted(card[1] for card in cards)
    for rel_path in new_paths:
        assert rel_path not in accepted_lines
        insert_at = next(
            (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > rel_path),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {rel_path}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"S4 {kind} batch applied: {len(batch)} groups, {sum(len(x['members']) for x in batch)} candidate mappings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
