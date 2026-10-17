from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
UNITS = ROOT / "04-knowledge" / "units"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

def src(chapter, location, file, span, quote, summary, page=None):
    return dict(chapter=chapter, location=location, file=file, span=span,
                quote=quote, summary=summary, page=page)

FAMILY = [
    dict(group="sg3-family-buonaccorsi-family", candidates=["cand-7729"],
         slug="buonaccorsi-family", name_zh="布奥纳科尔西家族", name_en="Buonaccorsi family",
         description_zh="哈斯克尔称 Raimondo Buonaccorsi 出生于一个古老且重要、在半岛各地有广泛支系的家族；又称家族成员多次分散其藏画，且没有清单留存。本卡只登记书中明确称作 Buonaccorsi 的家族集体，不宣称完整谱系、成员名录或对全部财产的归属。",
         description_en="Haskell says Raimondo Buonaccorsi was born into an old and important family with branches across the peninsula. He also says pictures were repeatedly split among family members and no inventory survived. This card registers only the collective family named Buonaccorsi in the book; it does not claim a complete genealogy, membership list, or ownership of all property.",
         context_zh="第8章 p.223 以家族背景介绍 Raimondo；p.225 讨论其藏画散入家族成员手中及清单缺失。原文关于 Corrado Giaquinto 为家族工作的说法带有 reported 转述限定。",
         context_en="Chapter 8 (p. 223) places Raimondo in the family context; p. 225 discusses pictures dispersed among family members and the absence of an inventory. Haskell qualifies the report that Corrado Giaquinto worked for the family as reported rather than established here.",
         boundary_zh="成员身份、家族分支及完整谱系未由本批补定；不把 Raimondo、家族成员、画家和藏画之间的关系登记为正式边。",
         boundary_en="This batch does not determine individual membership, branches, or a complete genealogy. It creates no formal edges among Raimondo, family members, artists, and pictures.",
         sources=[
             src("8","第8章，印刷页223；OCR L147","08_CHP-8_sec_ii.md","147","This provincial nobleman was born in 1669 of an old and important family with extensive ramifications throughout the peninsula and a particularly close relationship with the Church","哈斯克尔称 Raimondo 出生于一个古老且重要、在半岛各地有广泛支系并与教会关系密切的家族。","223"),
             src("8","第8章，印刷页225；OCR L175","08_CHP-8_sec_ii.md","175","the pictures were repeatedly split up among members of the family and no inventory has survived","哈斯克尔称藏画曾多次分散至家族成员手中，且没有清单留存。","225"),
         ]),
    dict(group="sg3-family-barbaro-family", candidates=["cand-8169"],
         slug="barbaro-family", name_zh="巴尔巴罗家族", name_en="Barbaro family",
         description_zh="第9章图版41a图注将 Santa Maria del Giglio 立面上的肖像称为 Barbaro 家族肖像。本卡仅登记图注明确指称的家族集体。",
         description_en="The Chapter 9 caption for Plate 41a describes the portraits on the façade of Santa Maria del Giglio as portraits of the Barbaro family. This card registers only the family collective explicitly named in the caption.",
         context_zh="来源为图版图注；本书该处没有列出肖像人物、家族支系或委托者。",
         context_en="The evidence is a plate caption; the passage does not identify the sitters, family branch, or commissioner.",
         boundary_zh="不据图注推定家族成员、肖像身份、建筑所有权或委托关系。",
         boundary_en="The caption does not establish family members, portrait identities, ownership of the building, or a commission.",
         sources=[src("9","第9章图版41a图注；OCR L1","09_CHP-9_intro_plates_visual-transcription.md","1","a. Façade of S. Maria del Giglio with portraits of Barbaro family","图版41a图注称 Santa Maria del Giglio 立面上有 Barbaro 家族肖像。")]),
    dict(group="sg3-family-bon-family-venice", candidates=["cand-8301"],
         slug="bon-family-venice", name_zh="邦家族（威尼斯）", name_en="Bon family of Venice",
         description_zh="第9章记载，Aurelio Rezzonico 于1751年从 Bon 家族购入威尼斯一座重要宫邸。该名称作为原文中的家族卖方身份登记；成员、支系和交易边界不在本批扩写。",
         description_en="Chapter 9 says that in 1751 Aurelio Rezzonico bought a major Venetian palace from the Bon family. The card registers the family as named in the source as the seller; it does not expand the membership, branch, or transaction boundaries.",
         context_zh="第9章 p.254；原文称宫邸购自 Bon 家族，没有给出卖方成员姓名。",
         context_en="Chapter 9 (p. 254); the source names the Bon family as seller but does not name an individual seller.",
         boundary_zh="不把家族名称等同于某一位 Bon 家族成员；正式所有权转移关系留待 S6 按端点和证据审查。",
         boundary_en="Do not equate the family name with an individual Bon family member. Formal ownership-transfer relations remain for S6 endpoint and evidence review.",
         sources=[src("9","第9章，印刷页254；OCR L139","09_CHP-9_intro.md","139","Venice from the Bon family.","哈斯克尔称 Aurelio Rezzonico 从 Bon 家族购得威尼斯宫邸。","254")]),
    dict(group="sg3-family-sandi-family", candidates=["cand-8356"],
         slug="sandi-family", name_zh="桑迪家族", name_en="Sandi family",
         description_zh="第9章称 Sandi 家族于1685年受封，并属较早聘用 Tiepolo 的家族之一；其家族在宫邸委托了一幅表现雄辩力量的天花装饰。原文跨 p.255–256，家族身份按 S3 身份组登记。",
         description_en="Chapter 9 says the Sandi were ennobled in 1685 and were among the early families to employ Tiepolo; they commissioned a palace ceiling representing the Powers of Eloquence. The passage crosses pp. 255–256, and the family is registered at the S3 identity-group level.",
         context_zh="p.255 的句子从 The Sandi 起始并跨页续接；p.256 给出受封年份、聘用 Tiepolo 和宫邸天花委托语境。",
         context_en="The sentence begins with The Sandi on p. 255 and continues across the page break; p. 256 gives the ennoblement date, employment of Tiepolo, and palace-ceiling commission context.",
         boundary_zh="本卡不补写具体成员、完整谱系或其他委托；关系候选留待 S6。",
         boundary_en="This card adds no individual members, complete genealogy, or other commissions; relation candidates remain for S6.",
         sources=[
             src("9","第9章，印刷页255；OCR L154","09_CHP-9_intro.md","154","Sometimes the subject could be more allusive. The Sandi,- who had been","p.255 以家族称谓 The Sandi 开启跨页句子。","255"),
             src("9","第9章，印刷页256；OCR L158","09_CHP-9_intro.md","158","ennobled only in 1685,1 were among the first to employ Tiepolo, and as their fortunes were closely linked to the extremely lucrative profession of the law, they commissioned a ceiling in their palace which was to illustrate the Powers of Eloquence, as expressed in four stories from antiquity.","p.256 续述 Sandi 于1685年受封、较早聘用 Tiepolo，并在其宫邸委托表现雄辩力量的天花装饰。","256"),
         ]),
    dict(group="sg3-family-bourbon-dynasty", candidates=["cand-9572"],
         slug="bourbon-dynasty", name_zh="波旁王朝", name_en="Bourbon dynasty",
         description_zh="第10章将 Bourbons 列为 Schulenburg 在 Palazzo Loredan 居所墙上所见王朝肖像群之一。本卡保留该集体称谓，不辨认具体肖像或个人。",
         description_en="Chapter 10 lists the Bourbons among the dynastic portrait groups on the walls of Schulenburg’s residence in the Palazzo Loredan. This card preserves the collective designation without identifying particular portraits or individuals.",
         context_zh="第10章 p.311 的文字把这一称谓置于 Schulenburg 与欧洲各王室交往的叙述中。",
         context_en="Chapter 10 (p. 311) uses this designation in its account of Schulenburg’s contacts with European royal houses.",
         boundary_zh="不据集体称谓识别具体肖像、坐像人物或支系；不登记来访或通信关系。",
         boundary_en="The collective label does not identify particular portraits, sitters, or branches; no visit or correspondence relation is registered.",
         sources=[src("10","第10章，印刷页311；OCR L14","10_CHP-10_sec_ii.md","14","whose portraits—Bourbons and Hapsburgs, Farneses and Hohenzollerns— lined the walls of the Palazzo Loredan in which he lived","哈斯克尔列出 Palazzo Loredan 墙上的王朝肖像群，其中包括 Bourbons。","311")]),
    dict(group="sg3-family-hapsburg-dynasty", candidates=["cand-9573"],
         slug="hapsburg-dynasty", name_zh="哈布斯堡王朝", name_en="Hapsburg dynasty",
         description_zh="第10章将 Hapsburgs 列为 Schulenburg 在 Palazzo Loredan 居所墙上的王朝肖像群之一。英文规范名沿用本书拼写 Hapsburg；本卡不辨认具体肖像或个人。",
         description_en="Chapter 10 lists the Hapsburgs among the dynastic portrait groups on the walls of Schulenburg’s residence in the Palazzo Loredan. The English name retains the book’s spelling, Hapsburg; this card identifies no particular portrait or person.",
         context_zh="第10章 p.311 的文字把该称谓置于 Schulenburg 与欧洲各王室交往的叙述中。",
         context_en="Chapter 10 (p. 311) uses this designation in its account of Schulenburg’s contacts with European royal houses.",
         boundary_zh="不据集体称谓识别具体肖像、坐像人物或支系；不登记来访或通信关系。",
         boundary_en="The collective label does not identify particular portraits, sitters, or branches; no visit or correspondence relation is registered.",
         sources=[src("10","第10章，印刷页311；OCR L14","10_CHP-10_sec_ii.md","14","whose portraits—Bourbons and Hapsburgs, Farneses and Hohenzollerns— lined the walls of the Palazzo Loredan in which he lived","哈斯克尔列出 Palazzo Loredan 墙上的王朝肖像群，其中包括 Hapsburgs。","311")]),
    dict(group="sg3-family-hohenzollern-dynasty", candidates=["cand-9574"],
         slug="hohenzollern-dynasty", name_zh="霍亨索伦王朝", name_en="Hohenzollern dynasty",
         description_zh="第10章将 Hohenzollerns 列为 Schulenburg 在 Palazzo Loredan 居所墙上的王朝肖像群之一。本卡保留来源的集体称谓，不辨认具体肖像或个人。",
         description_en="Chapter 10 lists the Hohenzollerns among the dynastic portrait groups on the walls of Schulenburg’s residence in the Palazzo Loredan. This card preserves the source’s collective designation without identifying particular portraits or individuals.",
         context_zh="第10章 p.311 的文字把该称谓置于 Schulenburg 与欧洲各王室交往的叙述中。",
         context_en="Chapter 10 (p. 311) uses this designation in its account of Schulenburg’s contacts with European royal houses.",
         boundary_zh="不据集体称谓识别具体肖像、坐像人物或支系；不登记来访或通信关系。",
         boundary_en="The collective label does not identify particular portraits, sitters, or branches; no visit or correspondence relation is registered.",
         sources=[src("10","第10章，印刷页311；OCR L14","10_CHP-10_sec_ii.md","14","whose portraits—Bourbons and Hapsburgs, Farneses and Hohenzollerns— lined the walls of the Palazzo Loredan in which he lived","哈斯克尔列出 Palazzo Loredan 墙上的王朝肖像群，其中包括 Hohenzollerns。","311")]),
    dict(group="sg3-family-guardi-brothers", candidates=["cand-9999"],
         slug="guardi-brothers", name_zh="瓜尔迪兄弟", name_en="Guardi brothers",
         description_zh="第13章称 Guardi brothers 仿用了 Piazzetta 为《耶路撒冷解放》所作的插图，并绘成一系列大型装饰画布。本卡只登记原文的兄弟集体称谓；原文没有分别指明各人的画布归属。",
         description_en="Chapter 13 says the Guardi brothers plagiarised Piazzetta’s illustrations for the Gerusalemme Liberata in a series of large decorative canvases. This card registers only the source’s collective sibling designation; it does not assign individual canvases to either brother.",
         context_zh="第13章 p.336；来源在相邻上下文中谈到 Francesco Guardi，但这句只以 Guardi brothers 集体指称。",
         context_en="Chapter 13 (p. 336); Francesco Guardi is mentioned in adjacent context, but this sentence uses only the collective term Guardi brothers.",
         boundary_zh="不在本卡建立完整成员表或作品归属；候选涉及的创作关系需在 S6 按具体端点和证据审查。",
         boundary_en="This card creates no complete member list or work attribution. The candidate creation relation must be reviewed in S6 against specific endpoints and evidence.",
         sources=[src("13","第13章，印刷页336；OCR L43–44","13_CHP-13_intro.md","43–44","Meanwhile in Venice the Guardi brothers plagiarised his illustrations for the\nGerusalemme Liberata in a series of large decorative canvases depicting scenes from the poem.","哈斯克尔将相关大型装饰画布的创作归于 Guardi brothers 集体称谓，但没有逐人说明归属。","336")]),
]

PROCEDURE = [
    dict(group="sg3-procedure-customs-duty-pictures", candidates=["cand-0897"],
         slug="customs-duty-on-pictures", name_zh="画作关税与海关处置", name_en="Customs duties and handling of pictures",
         description_zh="第8章称宗教题材画作适用的海关税低于世俗题材；第16章在艺术品跨境运输语境下称海关手续棘手、必要时须设法规避。本卡只记录索引将两处归入的画作关税／海关事项，不推定税率、法域或固定操作步骤。",
         description_en="Chapter 8 says sacred pictures paid lower customs duty than profane ones. In the context of transporting art across borders, Chapter 16 says customs were troublesome and had to be evaded if possible. This card records only the picture-duty and customs topic grouped by the index; it infers no rate, jurisdiction, or fixed procedure.",
         context_zh="索引 C.csv#431 指向 pp.228、374；前者是 Crespi 改题时对税差的说明，后者是 Joseph Smith 经手艺术品运输的语境。两处都不提供完整税则或手续清单。",
         context_en="Index entry C.csv#431 points to pp. 228 and 374. The first explains a title change by Crespi in relation to a duty difference; the second concerns Joseph Smith’s art transport. Neither supplies a complete tariff or list of customs steps.",
         boundary_zh="不要把个案税差推广成适用于所有时期和地区的规则；海关手续的规避描述也不构成法律程序说明。",
         boundary_en="Do not generalise the case-specific duty difference to all periods or jurisdictions. The account of evading customs does not establish a legal procedure.",
         sources=[
             src("8","第8章，印刷页228；OCR L211","08_CHP-8_sec_ii.md","211","he changed the title to The Finding of Moses, as sacred pictures paid lower customs duty than profane ones!","哈斯克尔称 Crespi 改变画名，因为宗教题材画作的关税低于世俗题材。","228"),
             src("16","第16章，印刷页374；OCR L18","16_CHP-16_intro.md","18","The process could be difficult. Collections likely to be dispersed had to be examined in absolute secrecy; transport was enormously expensive; the customs were troublesome and had to be evaded if possible.","哈斯克尔在跨境艺术品运输语境中称海关手续棘手、必要时须设法规避。","374"),
         ]),
    dict(group="sg3-procedure-manfrin-painter-competitions", candidates=["cand-1514"],
         slug="manfrin-painter-competitions", name_zh="吉罗拉莫·曼弗林举办的画家竞赛", name_en="Painter competitions organized by Girolamo Manfrin",
         description_zh="第17章称 Girolamo Manfrin 会组织画家围绕他自行构想的色情题材竞赛作画。此卡登记书中概述的赞助做法，不补写竞赛规则、获胜者或作品实际完成情况。",
         description_en="Chapter 17 says Girolamo Manfrin would organize competitions among painters to produce pictures on erotic themes of his own devising. This card records the patronage practice as described in the book; it adds no rules, winners, or claims about completion of the proposed pictures.",
         context_zh="第17章 p.381；索引 M.csv#51 将 competitions for painters 列在 Manfrin 条目之下。原文使用 would，未指认某一次竞赛。",
         context_en="Chapter 17 (p. 381); index entry M.csv#51 places competitions for painters under Manfrin. The source uses would and does not identify a single competition.",
         boundary_zh="本对象是做法，不是 Girolamo Manfrin 人物 KU，也不把索引人物主项本身映射成程序；不推定题材画作的作者或存世情况。",
         boundary_en="This is a practice, not the person KU for Girolamo Manfrin; the index’s person heading is not itself mapped as a procedure. The authorship or survival of the proposed pictures is not inferred.",
         sources=[src("17","第17章，印刷页381；OCR L24","17_CHP-17_sec_i.md","24","He would organise competitions among the painters to produce pictures on erotic themes which he himself devised—Joseph and Potiphars Wife, Bathsheba bathing, Lot and his Daughters, Susanna and the Elders.","哈斯克尔称 Manfrin 会组织画家围绕其自行构想的色情题材竞赛作画，并列举题材。","381")]),
    dict(group="sg3-procedure-ferdinand-art-exhibition-guidance", candidates=["cand-1610"],
         slug="ferdinand-art-exhibition-guidance", name_zh="费迪南德借助展览引导佛罗伦萨绘画", name_en="Grand Prince Ferdinand’s use of exhibitions to guide Florentine painting",
         description_zh="第8章称费迪南德借助艺术展览引导当时佛罗伦萨绘画方向，并在 Corpus Domini 游行期间展出其认可艺术家的作品；他还曾计划展出 Cassana 的肖像以影响本地画家。1706年较大型展览是另一个 event 身份组，本卡不与该事件合并。",
         description_en="Chapter 8 says Ferdinand used art exhibitions to guide the direction of painting in Florence, showing works by artists he approved during Corpus Domini processions; he also planned to exhibit a portrait by Cassana to influence local painters. The larger exhibition of 1706 is a separate event identity group and is not merged into this procedure.",
         context_zh="第8章 p.240；哈斯克尔把展览描述为费迪南德引导绘画方向的工具，并区分较随意的节庆展示与1706年更大规模的展览。",
         context_en="Chapter 8 (p. 240); Haskell describes exhibitions as an instrument Ferdinand used to guide painting and distinguishes casual festival displays from the larger exhibition of 1706.",
         boundary_zh="只登记展览作为引导绘画的做法；不将一次具体展览、展览中的作品或参与者关系并入程序卡，相关正式关系留待 S6。",
         boundary_en="Register only the practice of using exhibitions to guide painting. A particular exhibition, its works, and participant relations remain distinct and await S6 review.",
         sources=[
             src("8","第8章，印刷页240；OCR L355–356","08_CHP-8_sec_ii.md","355–356","He was also anxious to guide the whole direction taken by painters in the Florence of his day. For this purpose he took advantage of the still rudimentary instrumentof the art exhibition and used it in an entirely new way. Pictures had been exhibited in Florence, as in many other Italian cities, on the occasion of the Corpus Domini processions, and Ferdinand regularly showed works painted for him by those artists of whom he approved","哈斯克尔称费迪南德利用展览引导佛罗伦萨绘画，并定期在 Corpus Domini 游行期间展出其认可艺术家的作品。","240"),
             src("8","第8章，印刷页240；OCR L357","08_CHP-8_sec_ii.md","357","he intended to exhibit so that it would be seen ‘by our own artists here who paint so timidly’","费迪南德计划展出 Cassana 的肖像，希望本地画家看到。","240"),
         ]),
    dict(group="sg3-procedure-florentine-flour-revenue-concession-1676", candidates=["cand-7498","cand-12414"],
         slug="florentine-flour-revenue-concession-1676", name_zh="1676年佛罗伦萨面粉收入专营权授予", name_en="Florentine flour-revenue concession of 1676",
         description_zh="第8章称 Andrea del Rosso 获授有利可图的面粉专营权，并与 Lorenzo 共享；脚注将其记为佛罗伦萨城市及领地面粉收入的 Appalto Generale，自1676年6月1日起九年。本卡将正文与脚注所述授予事项登记为一个程序身份组，相关法令档案仍是独立对象。",
         description_en="Chapter 8 says Andrea del Rosso received a lucrative flour monopoly and shared it with Lorenzo. A footnote identifies it as the Appalto Generale of flour revenues for the City and Domain of Florence for nine years from 1 June 1676. This card registers the concession described in the text and note as one procedure identity group; the decree archive remains a separate object.",
         context_zh="第8章 p.211 正文交代 Andrea 与 Lorenzo 共享专营权；注2提供正式称谓、适用范围、期限和法令副本的档案定位。",
         context_en="Chapter 8 (p. 211) says Andrea and Lorenzo shared the monopoly; note 2 gives the formal designation, scope, term, and archival location of a copy of the decree.",
         boundary_zh="不把本程序等同于授予法令或法令副本；不推定执行细节或其他承包方。参与人物和档案端点关系留待 S6。",
         boundary_en="The procedure is distinct from the granting decree and its archival copy. No operating details or additional contractors are inferred. Relations to the named people and archive endpoint remain for S6.",
         sources=[
             src("8","第8章，印刷页211；OCR L85","08_CHP-8_sec_i.md","85","Andrea, the eldest of the brothers, who was born in 1640, was at the age of 36 awarded the lucrative flour monopoly which he shared with the slightly younger Lorenzo.","哈斯克尔称 Andrea del Rosso 获授面粉专营权，并与稍年轻的 Lorenzo 共享。","211"),
             src("8","第8章，印刷页211；注2；OCR L147","08_CHP-8_sec_i.md","147","A copy of the decree conferring the Appalto Generale della rendita della Farine della Città, e Dominio di Firenze for nine years as from I June 1676 is preserved in the Archivio di Stato—Miscellanea Medicea 533, Uffizio delle Farine","注2将授予内容称为佛罗伦萨城市及领地面粉收入的 Appalto Generale，并称期限自1676年6月1日起九年；法令副本存于佛罗伦萨国家档案馆。","211"),
         ]),
    dict(group="sg3-procedure-paintings-for-engraved-reproduction", candidates=["cand-9982"],
         slug="paintings-for-engraved-reproduction", name_zh="为雕版复制而作的当代绘画", name_en="Contemporary paintings produced for reproduction by engravers",
         description_zh="第13章将领先的当代画家有时制作、主要供雕版师复制的绘画列为出版赞助的第二种路径，并与复制既有名作、绘制书籍插图底稿和艺术家自行制版分别区分。",
         description_en="Chapter 13 identifies pictures sometimes produced by leading contemporary painters primarily for reproduction by an engraver as a second route of publishing patronage, distinct from reproducing established masterpieces, preparing drawings for book illustrations, and artists making their own engravings.",
         context_zh="第13章 p.333；原文明确列出四种相近但不相同的出版与图像生产路径。",
         context_en="Chapter 13 (p. 333); the source explicitly distinguishes four related but non-identical routes of publishing and image production.",
         boundary_zh="本卡记录一般生产路径，不指认任何具体绘画、画家、委托或雕版成品；相关实体关系不在此登记。",
         boundary_en="This card records a general production route and identifies no particular picture, painter, commission, or engraving. Entity relations are not registered here.",
         sources=[src("13","第13章，印刷页333；OCR L16","13_CHP-13_intro.md","16","Secondly, leading contemporary painters sometimes produced pictures whose primary purpose was to be reproduced by some engraver.","哈斯克尔将当代画家制作、主要供雕版师复制的绘画列作第二种出版赞助路径。","333")]),
    dict(group="sg3-procedure-pieta-plan-selection", candidates=["cand-11471"],
         slug="pieta-plan-selection", name_zh="威尼斯慈善院理事会的绘画方案遴选", name_en="Plan selection by the governors of the Pietà",
         description_zh="第9章称，Pietà 理事会似乎采用过一种做法：向最受看重且构想合适的画家征求方案，再择优选择。哈斯克尔以 A similar practice seems 限定其判断；本卡保留这种推测语气，不把它扩展为已证实、固定或普遍适用的制度。",
         description_en="Chapter 9 says that a similar practice seems to have been followed at the Pietà: the governors were to seek plans from highly regarded painters with suitable ideas and choose the best. Haskell’s phrase A similar practice seems qualifies the claim; this card does not turn it into a verified, fixed, or universal rule.",
         context_zh="第9章 p.274；该段把 Pietà 的方案遴选与此前 Scuola del Carmine 的方案竞赛作类比，而不是说两者规则完全相同。",
         context_en="Chapter 9 (p. 274); the passage compares plan selection at the Pietà with an earlier scheme competition at the Scuola del Carmine but does not say their rules were identical.",
         boundary_zh="候选登记为程序身份；参与者、具体方案和实际执行结果按原文限定，正式关系留待 S6。",
         boundary_en="The candidate is registered as a procedure identity. Participants, specific plans, and actual implementation remain bounded by the source; formal relations await S6.",
         sources=[src("9","第9章，印刷页274；OCR L72","09_CHP-9_sec_ii.md","72","A similar practice seems to have been followed in the Pietà, where the governors were required ‘to seek plans from the most highly thought of painters with suitable ideas and choose the best’.","哈斯克尔称 Pietà 理事会似乎要求向声望较高且构想合适的画家征求方案并择优。","274")]),
]

BATCHES = {"family": FAMILY, "procedure": PROCEDURE}
TYPE_DIRS = {"family": "families", "procedure": "procedures"}

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
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None

def make_card(record, kind):
    source_rows = []
    for item in record["sources"]:
        cite_loc = f", ch. {item['chapter']}"
        cite_loc += f", p. {item['page']}" if item["page"] else f", {item['location']}"
        source_rows.append({
            "citation": BOOK_CITATION + cite_loc + ".",
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['span']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": f"lines {item['span']}" + (f"; print p. {item['page']}" if item["page"] else "; plate caption"),
            },
        })
    frontmatter = {
        "title": f"{record['name_zh']}（{record['name_en']}）",
        "name_en": record["name_en"],
        "type": kind,
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** {record['description_zh']}

**English:** {record['description_en']}

### 名称

中文显示名及英文规范名见卡片标题。中文名为便于识别的项目译名或描述性译名；原书用词按来源引文保留。

The bilingual display name appears in the card title. The Chinese name is a project transliteration or descriptive rendering; the source wording is preserved in the quotations.

### 本书语境

{record['context_zh']}

{record['context_en']}

### 身份与范围边界

**中文：** {record['boundary_zh']}

**English:** {record['boundary_en']}

## 关系与证据

本批仅完成 S4 身份组登记，未新增正式关系。可成立的成员、创作、委托、所有权或参与关系仍须在 S6 依据具体端点和对应证据逐项审查。

This batch registers the S4 identity group only and adds no formal relation. Any membership, creation, commission, ownership, or participation relation must be reviewed in S6 against its specific endpoints and evidence.
"""
    return f"---\n{fm}---\n\n{body}"

def progress(alignment_rows):
    new_rows = [r for r in alignment_rows if r.get("candidate_id") and not r.get("external_source") and r["decision"] == "new"]
    groups = defaultdict(list)
    for row in new_rows:
        group = get_group(row.get("resolution_note", ""))
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
    registered = {g: rows for g, rows in groups.items() if any(r.get("ku_id") for r in rows)}
    mapped = sum(bool(r.get("ku_id")) for rows in registered.values() for r in rows)
    return len(registered), mapped, len(groups) - len(registered), len(new_rows) - mapped

def update_progress(process, result, alignment_rows, manifest_rows):
    registered, mapped, pending_groups, pending_members = progress(alignment_rows)
    process_pattern = re.compile(r"已登记\s*[\d,]+\s*组、\s*[\d,]+\s*条成员映射，尚待登记\s*[\d,]+\s*组、\s*[\d,]+\s*条。")
    process, pc = process_pattern.subn(
        f"已登记{registered:,}组、{mapped:,}条成员映射，尚待登记{pending_groups:,}组、{pending_members:,}条。", process, count=1)
    assert pc == 1, "process current S4 totals did not match"
    result_pattern = re.compile(r"S4 已登记\s*[\d,]+\s*组、映射\s*[\d,]+\s*条成员候选；尚待登记\s*[\d,]+\s*组、\s*[\d,]+\s*条映射。")
    result, rc = result_pattern.subn(
        f"S4 已登记{registered:,}组、映射{mapped:,}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。", result, count=1)
    assert rc == 1, "result current S4 totals did not match"
    manifest_pattern = re.compile(r"(\|\s*\[KU 登记\]\(\.\./tables/ku-manifest\.csv\)\s*\|\s*)[\d,]+ KU")
    result, mc = manifest_pattern.subn(lambda m: f"{m.group(1)}{len(manifest_rows):,} KU", result, count=1)
    assert mc == 1, "result manifest total did not match"
    return process, result, registered, mapped, pending_groups, pending_members

def main():
    parser = argparse.ArgumentParser(description="Register traceable family or procedure S3 groups in S4")
    parser.add_argument("--type", choices=sorted(BATCHES), required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    kind, batch = args.type, BATCHES[args.type]
    type_dir = TYPE_DIRS[kind]
    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    alignment_by_id = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    pending_by_group = defaultdict(list)
    for row in alignments:
        if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new" and not row.get("ku_id"):
            pending_by_group[get_group(row.get("resolution_note", ""))].append(row["candidate_id"])
    for rec in batch:
        assert sorted(pending_by_group.get(rec["group"], [])) == sorted(rec["candidates"]), (rec["group"], pending_by_group.get(rec["group"]))
        for cid in rec["candidates"]:
            candidate, alignment = candidate_by_id[cid], alignment_by_id[cid]
            assert candidate["suggested_type"] == kind, (cid, candidate["suggested_type"])
            assert alignment["decision"] == "new" and not alignment.get("ku_id"), (cid, alignment)
            assert get_group(alignment.get("resolution_note", "")) == rec["group"], cid
        rel_path = f"04-knowledge/units/{type_dir}/{rec['slug']}.md"
        ku_id = f"units/{type_dir}/{rec['slug']}"
        assert not (UNITS / type_dir / f"{rec['slug']}.md").exists(), rel_path
        assert rel_path not in accepted_text
        assert not any(r.get("ku_id") == ku_id or r.get("card_path") == rel_path for r in manifest), ku_id
        for item in rec["sources"]:
            source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
            assert source_path.is_file(), source_path
            assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (rec["group"], item["quote"])

    planned_alignment = [dict(r) for r in alignments]
    planned_by_id = {r["candidate_id"]: r for r in planned_alignment if r.get("candidate_id") and not r.get("external_source")}
    planned_manifest = list(manifest)
    new_paths = []
    for rec in batch:
        ku_id = f"units/{type_dir}/{rec['slug']}"
        rel_path = f"04-knowledge/units/{type_dir}/{rec['slug']}.md"
        for cid in rec["candidates"]:
            planned_by_id[cid]["ku_id"] = ku_id
            planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {rec['group']} to {ku_id}."
            if cid == "cand-11471":
                planned_by_id[cid]["resolution_note"] += (
                    " Source locator correction: the quote at L72 follows the [Page 274] marker at L70; "
                    "use print p. 274. This supersedes the p. 273 locator in the earlier S3 process note."
                )
        planned_manifest.append(dict(ku_id=ku_id, type=kind, canonical_name=rec["name_zh"],
                                     name_en=rec["name_en"], source_task=TASK, card_path=rel_path))
        new_paths.append(rel_path)

    mapped_groups = defaultdict(list)
    for row in planned_alignment:
        if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new":
            mapped_groups[get_group(row.get("resolution_note", ""))].append(row)
    for group, rows in mapped_groups.items():
        if any(r.get("ku_id") for r in rows):
            mapped = [r for r in rows if r.get("ku_id")]
            assert len(mapped) == len(rows) and len({r["ku_id"] for r in mapped}) == 1, group

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    updated_process, updated_result, registered, mapped, pending_groups, pending_members = update_progress(
        process_text, result_text, planned_alignment, planned_manifest)
    marker = f"### S4 {kind}：余下明确身份组登记（2026-10-16）"
    assert marker not in process_text and marker not in result_text, "batch note already exists"

    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as f:
        statements = [json.loads(line) for line in f if line.strip()]
    details = []
    for rec in batch:
        ids = set(rec["candidates"])
        direct = [s for s in statements if s.get("subject_candidate_id") in ids or s.get("object_candidate_id") in ids]
        relation = [s for s in direct if (s.get("qualifiers") or {}).get("relation_candidate") is True]
        details.append(f"- {', '.join(rec['candidates'])} → {rec['group']} → units/{type_dir}/{rec['slug']}；直接 S2 断言 {len(direct)} 条、其中关系候选 {len(relation)} 条；本批未将其写成正式边。")
    note = (
        f"\n\n{marker}\n\n" + "\n".join(details)
        + "\n\n逐卡按双语字段和原文引文登记；没有把未列名成员、支系、肖像、税率、程序步骤或作品归属补猜为事实。"
        + "程序类中，1706年佛罗伦萨展览事件与 Ferdinand 的展览引导做法分组；Florentine 面粉收入专营权与授予法令档案分开；"
        + "Pietà 方案遴选保留 Haskell 的 seems 限定。其引文位于 OCR L72，前置页标 L70 为 [Page 274]；本批将旧 S3 过程所记 p.273 更正为印刷页274。"
        + "全部正式关系继续留待 S6，未开展 S5。"
        + f"\n\nS4 当前已登记{registered:,}组/{mapped:,}条成员映射，尚待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    result_note = (
        f"\n\n### {kind}：剩余明确身份组 S4 登记（2026-10-16）\n\n"
        + "；".join(f"{', '.join(rec['candidates'])} → units/{type_dir}/{rec['slug']}" for rec in batch)
        + "。卡片依据所列原书语句保存身份与范围限定；未确定的成员、支系、个别肖像、程序细节和关系继续按原状态保留。"
        + "程序卡中的一次展览事件、相关档案及一般做法保持分开。无外部身份核验、S5 补足或 S6 正式关系新增。"
        + "Pietà 引文按来源页标更正为 p.274（旧过程记录为 p.273）。"
        + f"\n\n全书 S4 当前登记{registered:,}组/{mapped:,}条映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    updated_process += note
    updated_result += result_note

    if args.dry_run:
        print(f"dry-run passed: type={kind} groups={len(batch)} candidates={sum(len(r['candidates']) for r in batch)} "
              f"registered_after={registered} mapped_after={mapped} pending_after={pending_groups}/{pending_members} manifest_after={len(planned_manifest)}")
        return 0

    for rec in batch:
        (UNITS / type_dir / f"{rec['slug']}.md").write_text(make_card(rec, kind), encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted_text.splitlines()
    for rel_path in sorted(new_paths):
        insert_at = next((i for i, line in enumerate(accepted_lines)
                          if line.startswith("- 04-knowledge/units/") and line[2:] > rel_path),
                         next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)))
        accepted_lines.insert(insert_at, f"- {rel_path}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(updated_process, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(updated_result, encoding="utf-8-sig", newline="")
    print(f"applied: type={kind} groups={len(batch)} candidates={sum(len(r['candidates']) for r in batch)} manifest={len(planned_manifest)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
