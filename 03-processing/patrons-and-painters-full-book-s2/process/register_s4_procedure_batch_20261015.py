from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
UNITS = ROOT / "04-knowledge" / "units"
TASK = "patrons-and-painters-full-book-s2"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-procedure"
GROUPS = [
    {
        "group": "sg3-procedure-zanetti-colour-woodcut",
        "candidates": ["cand-2852", "cand-9734"],
        "slug": "zanetti-chiaroscuro-colour-woodcut-process",
        "zh": "三色或四色明暗木刻工艺",
        "en": "Process for making three- or four-colour chiaroscuro woodcuts",
        "description_zh": "一种用于制作三色或四色明暗木刻的彩色木刻工艺。哈斯克尔称 A. M. Zanetti the Elder 将重新发现该工艺视为其最重要的成就。",
        "description_en": "A colour woodcut process for producing three- or four-colour chiaroscuro prints. Haskell reports that A. M. Zanetti the Elder regarded rediscovering it as his most important achievement.",
        "context_zh": "第十章记述年长的 Zanetti 曾向 Stefano Conti 宣告重新发现彩色木刻工艺；第十三章进一步说明该工艺用于三色或四色明暗木刻。两处记载共同支持同一项工艺身份。",
        "sources": [
            {"chapter": "10", "page": "320", "file": "10_CHP-10_sec_ii.md", "lines": "155–155", "summary": "年长的 Zanetti 致信 Stefano Conti，宣告重新发现彩色木刻工艺。", "quote": "Zanetti wrote to announce his rediscovery of the process for making colour woodcuts"},
            {"chapter": "13", "page": "343", "file": "13_CHP-13_intro.md", "lines": "112–112", "summary": "Zanetti 将重新发现三色或四色明暗木刻工艺视为其最重要的成就。", "quote": "Zanetti himself considered that his most important achievement was his rediscovery of the process for making chiaroscuro woodcuts in three or four different colours."},
        ],
    },
    {
        "group": "sg3-procedure-cand-4133", "candidates": ["cand-4133"], "slug": "haskell-empirical-research-method",
        "zh": "经验实证研究与取材方法", "en": "Empirical method of research and selection",
        "description_zh": "哈斯克尔在第一版序言中说明，他尽量避免概括、坚持经验研究，也不试图逐一描述书中提及的全部绘画。",
        "description_en": "In the first-edition preface, Haskell says he avoids generalisation, aims to be empirical, and does not attempt to describe every painting mentioned in the book.",
        "context_zh": "这是作者对本书研究取径与材料取舍的自述，不构成适用于其他研究者的普遍规则。",
        "sources": [{"chapter": "preface", "page": "viii", "file": "00_03_Preface_1st_Ed.md", "lines": "15–16", "summary": "哈斯克尔称其研究尽量经验化，避免普遍概括，也未追述全部相关绘画。", "quote": "I have also fought shy of generalisations and have tried to be severely empirical"}],
    },
    {
        "group": "sg3-procedure-cand-4476", "candidates": ["cand-4476"], "slug": "copying-raphael-titian-as-training",
        "zh": "摹写拉斐尔与提香的训练方式", "en": "Training through copying Raphael and Titian",
        "description_zh": "哈斯克尔将 Pietro 摹写拉斐尔和提香的学习方式概括为后来艺术家也须经历的类似训练。",
        "description_en": "Haskell generalises from Pietro's copying of Raphael and Titian to a similar training that, he says, every later artist was required to undergo.",
        "context_zh": "这是哈斯克尔对艺术训练传统的概括，保留其作者判断，不作为已逐人核实的教育记录。",
        "sources": [{"chapter": "2", "page": "39", "file": "02_CHP-2_sec_ii.md", "lines": "81–81", "summary": "Pietro 摹写拉斐尔和提香之后，哈斯克尔称此后每位艺术家都须接受类似训练。", "quote": "Thereafter every artist was required to undergo similar training."}],
    },
    {
        "group": "sg3-procedure-cand-6717", "candidates": ["cand-6717"], "slug": "artist-recruitment-pressure-france",
        "zh": "以威胁和贿赂招募艺术家赴法", "en": "Recruitment of artists for France through threats and bribery",
        "description_zh": "哈斯克尔称，法国方面招募意大利艺术家的有限成果，是在从威胁到贿赂的极端压力下取得的。",
        "description_en": "Haskell says the limited success in recruiting Italian artists for France was achieved through extreme pressure ranging from threats to bribery.",
        "context_zh": "该段记述是对一次招募行动的概括；书中没有逐项列出具体威胁或贿赂。",
        "sources": [{"chapter": "7", "page": "176", "file": "07_CHP-7_sec_i.md", "lines": "84–84", "summary": "招募行动仅取得有限成果，哈斯克尔将其归因于从威胁到贿赂的极端压力。", "quote": "Even this limited success had been achieved only by using the most extreme pressure ranging from ugly threats to bribery"}],
    },
    {
        "group": "sg3-procedure-cand-7787", "candidates": ["cand-7787"], "slug": "stefano-conti-picture-commission-requirements",
        "zh": "斯特凡诺·孔蒂的绘画委托与付款要求", "en": "Stefano Conti's picture-commission and payment requirements",
        "description_zh": "哈斯克尔称，孔蒂允许画家选择题材，但要求作品为专为他创作的原作、符合指定尺寸，并附写明题材与日期的书面保证；付款不超过他认为作品应有的价值。",
        "description_en": "Haskell says Conti allowed artists to choose subjects but required original pictures made for him alone, specified dimensions, and written guarantees of subject and date; he would not pay more than he thought a picture was worth.",
        "context_zh": "上述条件是哈斯克尔对孔蒂委托方式的记述；本卡不将该个案推广为其他赞助人的通行规则。",
        "sources": [{"chapter": "8", "page": "226", "file": "08_CHP-8_sec_ii.md", "lines": "184–184", "summary": "哈斯克尔记述孔蒂对作品原创性、尺寸、题材日期保证及付款上限的要求。", "quote": "He was a generous patron, but refused ever to pay more than he thought a picture was worth. He insisted that each work should be an originals painted for him alone and not copied."}],
    },
    {
        "group": "sg3-procedure-cand-7788", "candidates": ["cand-7788"], "slug": "marchesini-written-reports-to-conti",
        "zh": "马尔凯西尼定期向孔蒂书面报告", "en": "Marchesini's regular written reporting to Stefano Conti",
        "description_zh": "哈斯克尔称，马尔凯西尼经常写信向其赞助人孔蒂通报委托进度。",
        "description_en": "Haskell says Marchesini regularly wrote to his patron, Stefano Conti, to report on the progress of commissions.",
        "context_zh": "本书记述的是通信做法，没有据此确认具体书信现存。",
        "sources": [{"chapter": "8", "page": "226", "file": "08_CHP-8_sec_ii.md", "lines": "187–187", "summary": "马尔凯西尼定期写信向孔蒂通报进展，并处理预付款、艺术家建议和作品修改。", "quote": "writing regularly to his patron to keep him informed"}],
    },
    {
        "group": "sg3-procedure-cand-8111", "candidates": ["cand-8111"], "slug": "venetian-patrician-travel-permission",
        "zh": "威尼斯贵族出境许可规定", "en": "Venetian restriction on patricians' travel abroad",
        "description_zh": "哈斯克尔称，威尼斯一项于1709年通过、1783年恢复的法律规定，贵族未经十人委员会特别许可不得出国。",
        "description_en": "Haskell says a Venetian law passed in 1709 and revived in 1783 forbade patricians to travel abroad without special permission from the Council of Ten.",
        "context_zh": "原书未给出该法律的正式题名；年代与限制范围按哈斯克尔的叙述保留。",
        "sources": [{"chapter": "9", "page": "245", "file": "09_CHP-9_intro.md", "lines": "14–15", "summary": "法律于1709年通过并于1783年恢复，限制贵族未经十人委员会许可出国。", "quote": "and a law was passed in 1709, to be revived in\n1783, forbidding patricians to travel abroad without special permission of the Council of Ten."}],
    },
    {
        "group": "sg3-procedure-cand-8113", "candidates": ["cand-8113"], "slug": "venetian-political-unorthodoxy-prosecutions",
        "zh": "威尼斯政治异端的检控", "en": "Prosecutions for political unorthodoxy in Venice",
        "description_zh": "哈斯克尔称，威尼斯对政治异端的检控威胁到社会地位很高的人物。",
        "description_en": "Haskell says prosecutions for political unorthodoxy threatened even highly placed people in Venice.",
        "context_zh": "该段未点名被告或具体案件，因而只登记书中描述的检控做法。",
        "sources": [{"chapter": "9", "page": "245", "file": "09_CHP-9_intro.md", "lines": "13–13", "summary": "哈斯克尔称，政治异端检控的威胁甚至涉及地位很高的人物。", "quote": "censorship was strict, if fitful, and prosecutions for political unorthodoxy threatened even the most highly placed"}],
    },
    {
        "group": "sg3-procedure-cand-8122", "candidates": ["cand-8122"], "slug": "betrothal-of-the-sea-ceremony",
        "zh": "海上婚礼仪式", "en": "Betrothal of the Sea ceremony",
        "description_zh": "威尼斯的海上婚礼仪式是书中所述的周期性公共仪式；哈斯克尔记载游客多觉得它荒谬，一些较有思考的威尼斯人也开始质疑它。",
        "description_en": "The Betrothal of the Sea was a recurring Venetian public ceremony. Haskell reports that tourists often found it ridiculous and that some more thoughtful Venetians were beginning to question it.",
        "context_zh": "此处登记的是重复举行的仪式类型，不代表某一次具体仪式事件。",
        "sources": [{"chapter": "9", "page": "246", "file": "09_CHP-9_intro.md", "lines": "22–22", "summary": "哈斯克尔比较游客对海上婚礼仪式的看法与部分威尼斯人开始出现的疑虑。", "quote": "Indeed it was mainly the tourists who found such ceremonies as The Betrothal of the Sea somewhat ridiculous, though more thoughtful Venetians were also beginning to have doubts."}],
    },
    {
        "group": "sg3-procedure-cand-8135", "candidates": ["cand-8135"], "slug": "purchase-of-venetian-nobility",
        "zh": "购买威尼斯贵族身份的方式", "en": "Purchase of admission into the Venetian nobility",
        "description_zh": "哈斯克尔称，威尼斯政府允许新兴家族通过付费进入贵族阶层。",
        "description_en": "Haskell says the Venetian government allowed newly admitted families to purchase entry into the nobility.",
        "context_zh": "原书没有提供正式程序名称或完整规则；这里只记录其明确陈述的付费准入方式。",
        "sources": [{"chapter": "9", "page": "247", "file": "09_CHP-9_intro.md", "lines": "28–28", "summary": "战争消耗国家资源后，参议院接纳更多新家族，并允许其购买贵族身份。", "quote": "new families, who were allowed to buy themselves into the nobility"}],
    },
    {
        "group": "sg3-procedure-cand-8175", "candidates": ["cand-8175"], "slug": "wealth-based-venetian-nobility-admission",
        "zh": "以财富作为威尼斯贵族准入条件", "en": "Wealth-based admission to the Venetian nobility",
        "description_zh": "哈斯克尔称，威尼斯贵族准入在当时完全取决于财富。",
        "description_en": "Haskell says admission to the Venetian nobility at this time depended purely on wealth.",
        "context_zh": "这是哈斯克尔对准入条件的概括；与个别家族购入身份的案例分开登记。",
        "sources": [{"chapter": "9", "page": "249", "file": "09_CHP-9_intro.md", "lines": "81–81", "summary": "哈斯克尔称，长期战争后贵族准入完全取决于财富。", "quote": "Admission to the nobility now depended purely on wealth."}],
    },
    {
        "group": "sg3-procedure-cand-8365", "candidates": ["cand-8365"], "slug": "inspection-of-decorative-modelli",
        "zh": "威尼斯装饰委托方案的制作与审阅", "en": "Preparation and patron inspection of modelli for Venetian decorative works",
        "description_zh": "哈斯克尔称，十八世纪多数威尼斯艺术家会先制作装饰方案模型供赞助人审阅；他认为方案与完工装饰差异很大的情况很少。",
        "description_en": "Haskell says most eighteenth-century Venetian artists first prepared modelli for a patron's inspection, and that major discrepancies between proposal and completed decoration were rare.",
        "context_zh": "“多数”和“很少”均为哈斯克尔对书中材料的概括，保留其范围限定。",
        "sources": [{"chapter": "9", "page": "255", "file": "09_CHP-9_intro.md", "lines": "155–155", "summary": "多数威尼斯艺术家先向赞助人提交装饰方案模型；哈斯克尔称方案与完工差异很大的案例很少。", "quote": "Most Venetian artists of the eighteenth century first produced modelli of their proposed work for inspection by the patron and there are only a very few cases of great discrepancy between these and the completed decoration."}],
    },
    {
        "group": "sg3-procedure-cand-8370", "candidates": ["cand-8370"], "slug": "artist-initiative-in-subject-choice",
        "zh": "装饰委托中由艺术家主动选择题材", "en": "Artist-initiated subject choice in Venetian decorative commissions",
        "description_zh": "哈斯克尔称，有证据表明至少在一些案例中，装饰委托的题材由艺术家主动提出。",
        "description_en": "Haskell says there is evidence that, in at least some cases, the artist took the initiative in choosing the subject of a decorative commission.",
        "context_zh": "“至少一些案例”是本卡适用范围；不推广为普遍委托惯例。",
        "sources": [{"chapter": "9", "page": "255", "file": "09_CHP-9_intro.md", "lines": "151–151", "summary": "哈斯克尔称，至少部分装饰委托中艺术家主动选择题材。", "quote": "there is evidence that in at least some cases the artist himself took the initiative in choosing the subject"}],
    },
    {
        "group": "sg3-procedure-cand-8409", "candidates": ["cand-8409"], "slug": "noble-banquet-competitions",
        "zh": "贵族竞办奢华宴席的做法", "en": "Noble competitions to provide the most expensive banquets",
        "description_zh": "哈斯克尔转述 Antonio Longo 的回忆录，称威尼斯贵族曾竞相比办最昂贵的宴席。",
        "description_en": "Reporting Antonio Longo's memoirs, Haskell says Venetian nobles used to compete over who could offer the most expensive banquets.",
        "context_zh": "这是经 Haskell 转述的回忆录记载，不标作独立核实的长期惯例。",
        "sources": [{"chapter": "9", "page": "257", "file": "09_CHP-9_intro.md", "lines": "168–168", "summary": "Haskell 据 Longo 回忆录转述贵族竞办最昂贵宴席的做法。", "quote": "nobles used to organise competitions as to who could offer the most expensive banquets"}],
    },
    {
        "group": "sg3-procedure-cand-8518", "candidates": ["cand-8518"], "slug": "pisani-family-drawing-lessons",
        "zh": "为皮萨尼家之子提供绘画课", "en": "Drawing lessons given to the Pisani family's son",
        "description_zh": "哈斯克尔称，皮萨尼家组织的私人学院由 Pietro Longhi 负责，似乎主要为家中儿子提供绘画课，并在其去世后结束。",
        "description_en": "Haskell says the Pisani family's private academy, led by Pietro Longhi, seems to have mainly provided drawing lessons for their son and ended after his death.",
        "context_zh": "“似乎”保留原书限定；本卡记录的是学院的教学活动，不推断更广泛的课程。",
        "sources": [{"chapter": "9", "page": "260", "file": "09_CHP-9_intro.md", "lines": "208–208", "summary": "皮萨尼家私人学院似乎主要为其子提供绘画课，并在其去世后终止。", "quote": "this seems to have done little more than provide their son Almord with drawing lessons and it came to an end with his death"}],
    },
    {
        "group": "sg3-procedure-cand-8989", "candidates": ["cand-8989"], "slug": "grand-tour-english-travel-habit",
        "zh": "英国人的大旅行习惯", "en": "Grand Tour as a habitual English travel practice",
        "description_zh": "哈斯克尔将大旅行成为惯常活动与英国赞助人审美信心变化联系起来，并称他们不喜欢大型历史画，除非作者是早已去世的古代大师。",
        "description_en": "Haskell links the Grand Tour becoming habitual with changing confidence in English taste, and says English patrons disliked large-scale history painting unless it was by a long-dead Old Master.",
        "context_zh": "该段描述的是群体性旅行与审美趋势，不指向某一旅客或具体行程。",
        "sources": [{"chapter": "10", "page": "286", "file": "10_CHP-10_intro.md", "lines": "196–196", "summary": "大旅行成为惯常活动后，哈斯克尔称英国人的趣味变化影响其对大型历史画的接受。", "quote": "as the Grand Tour became habitual and the English grew more sure of their tastes"}],
    },
    {
        "group": "sg3-procedure-cand-9978", "candidates": ["cand-9978"], "slug": "venetian-book-copyright-monopoly",
        "zh": "威尼斯出版业的二十年版权专营制度", "en": "Twenty-year copyright monopolies in Venetian book publishing",
        "description_zh": "哈斯克尔称，威尼斯政府以有利版权法鼓励奢华插图书出口，这些法律授予二十年专营权；他认为长期结果是本地市场图书质量下降，而面向外国读者的豪华版本增加。",
        "description_en": "Haskell says advantageous copyright laws granting twenty-year monopolies encouraged Venetian illustrated-book exports; he argues that local-market book quality later declined while luxury editions for foreign readers increased.",
        "context_zh": "政策效果是作者对书市变化的解释，保留为 Haskell 的论述，不当作独立验证的因果结论。",
        "sources": [{"chapter": "13", "page": "332", "file": "13_CHP-13_intro.md", "lines": "9–11", "summary": "政府以版权法鼓励插图书出口；法律授予二十年专营权，Haskell据此描述本地与出口版本的变化。", "quote": "the government encouraged this policy by enforcing advantageous copyright laws"}],
    },
    {
        "group": "sg3-procedure-cand-9981", "candidates": ["cand-9981"], "slug": "reproducing-venetian-masterpieces-in-prints",
        "zh": "版画再现威尼斯既有名作", "en": "Reproduction of established Venetian masterpieces in prints",
        "description_zh": "Haskell 将绘图者与雕版师、或仅雕版师复制威尼斯既有名作列为版画出版的第一种路径。",
        "description_en": "Haskell identifies reproduction of established Venetian masterpieces by draughtsmen and engravers, or by engravers alone, as one route for print publishing.",
        "context_zh": "Haskell称该做法延续至十八世纪，但与赞助史的直接关联有限。",
        "sources": [{"chapter": "13", "page": "333", "file": "13_CHP-13_intro.md", "lines": "15–16", "summary": "绘图者与雕版师复制威尼斯既有名作是出版版画的一种路径，该做法延续至十八世纪。", "quote": "draughtsmen and engravers, or sometimes merely engravers, might reproduce wellestablished masterpieces of Venetian art"}],
    },
    {
        "group": "sg3-procedure-cand-9983", "candidates": ["cand-9983"], "slug": "artist-drawings-for-engraved-book-illustrations",
        "zh": "为书籍插图绘制版画底稿", "en": "Artist drawings designed for engraving as book illustrations",
        "description_zh": "Haskell 将艺术家先绘制、再供雕版制成书籍插图的底稿列为版画出版路径之一，并称这是更常见的做法。",
        "description_en": "Haskell identifies artists' drawings intended for engraving as book illustrations as one print-publishing route and describes it as the more frequent practice.",
        "context_zh": "“更常见”只适用于 Haskell 在该段列举的四种出版路径。",
        "sources": [{"chapter": "13", "page": "333", "file": "13_CHP-13_intro.md", "lines": "16–16", "summary": "艺术家绘制供雕版制成书籍插图的底稿，被 Haskell 列为更常见的出版路径。", "quote": "Thirdly, and far more frequently, artists produced drawings designed to be engraved as bookillustrations."}],
    },
    {
        "group": "sg3-procedure-cand-9984", "candidates": ["cand-9984"], "slug": "artists-own-engraving",
        "zh": "艺术家自制版画", "en": "Artists producing their own engravings",
        "description_zh": "Haskell 将艺术家自行制作雕版列为书籍与版画生产的第四种路径。",
        "description_en": "Haskell identifies artists producing their own engravings as the fourth route in his account of print production.",
        "context_zh": "这里记录的是 Haskell 的出版路径分类，不表示具体艺术家或版画作品已经逐项登记。",
        "sources": [{"chapter": "13", "page": "333", "file": "13_CHP-13_intro.md", "lines": "16–16", "summary": "Haskell将艺术家自行制作雕版列为第四种出版路径。", "quote": "And fourthly a number of artists produced their own engravings."}],
    },
    {
        "group": "sg3-procedure-cand-10049", "candidates": ["cand-10049"], "slug": "remondini-low-priced-facsimiles",
        "zh": "伦多尼印制低价仿本", "en": "Remondini's low-priced facsimiles of other publications",
        "description_zh": "Haskell称，伦多尼印刷所曾以大幅低价制作其他出版物的仿本；“少有顾忌”是作者对其做法的评价。",
        "description_en": "Haskell says the Remondini firm produced facsimiles of other publications at much reduced prices; his description of the firm as having few scruples is an attributed evaluation.",
        "context_zh": "本卡区分可核对的低价仿印记载与 Haskell 的评价措辞。",
        "sources": [{"chapter": "13", "page": "340", "file": "13_CHP-13_intro.md", "lines": "85–85", "summary": "伦多尼以低价仿印其他出版物；Haskell同时使用带评价色彩的措辞。", "quote": "producing facsimiles of other publications at much reduced prices"}],
    },
    {
        "group": "sg3-procedure-cand-10775", "candidates": ["cand-10775"], "slug": "powder-preparation-for-clean-casting",
        "zh": "用于洁净铸造的粉末制备记载", "en": "Reported powder preparation for clean casting",
        "description_zh": "一封书中转录的信称，用于洁净铸造的粉末由一种 OCR 读作“dalco”、印本疑似为“talco”的材料充分焙烧后细筛制成；材料读法仍有疑问。",
        "description_en": "A letter quoted in the book reports that powder for clean casting was made by thoroughly burning and finely sifting a material read by OCR as “dalco” and possibly printed as “talco”; the material reading remains uncertain.",
        "context_zh": "原文是意大利语书信转录；卡片保留 OCR 异读，不把材料名称裁定为滑石。",
        "sources": [{"chapter": "19", "page": "387", "file": "19_CHP-19Appendix.md", "lines": "40–40", "summary": "书信报告粉末制法，并称材料 OCR 读作 dalco、印本可能为 talco，须烧制并细筛。", "quote": "la Polvere si fa di dalco beniss:o abbrucciato, e poi questo, e setacciato finissimam:te."}],
    },
    {
        "group": "sg3-procedure-cand-10785", "candidates": ["cand-10785"], "slug": "bronze-head-casting-preparation",
        "zh": "青铜头像铸造准备过程", "en": "Bronze-head casting preparation described in the Orsini letters",
        "description_zh": "一封书中转录的信讨论为受信人铸造青铜头像的准备与费用，并提及石膏和蜡制空腔试模。",
        "description_en": "A letter quoted in the book discusses the preparation and cost of casting a bronze head for its recipient, including plaster and wax trials for the hollow mould.",
        "context_zh": "卡片只记录 p.388 这封信明确写出的准备过程；不据此补出完整铸造步骤或后续修整事实。",
        "sources": [{"chapter": "19", "page": "388", "file": "19_CHP-19Appendix.md", "lines": "50–50", "summary": "信中提议给铸工费用，以覆盖青铜头像空腔试模所需石膏和蜡的成本。", "quote": "dare fino à 25 scudi à m.r Bastiano Sebastiani che deve fare il getto di Bronzo della testa di V.E."}],
    },
]


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def frontmatter(row: dict) -> str:
    sources = []
    for source in row["sources"]:
        if source["chapter"] == "preface":
            citation = f"Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), Preface to the First Edition, p. {source['page']}."
            location = f"章前：第一版序言，印刷页{source['page']}；OCR L{source['lines']}"
        else:
            citation = f"Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. {source['chapter']}, p. {source['page']}."
            location = f"第{source['chapter']}章，印刷页{source['page']}；OCR L{source['lines']}"
        sources.append({
            "citation": citation,
            "location": location,
            "sentence_summary": source["summary"],
            "original_quotes": [{"source_span": f"lines {source['lines']}", "text": source["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{source['file']}",
                "source_span": f"lines {source['lines']}; print p. {source['page']}",
            },
        })
    data = {
        "title": f"{row['zh']}（{row['en']}）",
        "name_en": row["en"],
        "type": "procedure",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-15",
        "updated": "2026-10-15",
        "process_ref": PROCESS_REF,
    }
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000).rstrip()


def card(row: dict) -> tuple[str, str]:
    path = f"04-knowledge/units/procedures/{row['slug']}.md"
    body = (
        f"---\n{frontmatter(row)}\n---\n\n"
        "## 内容\n\n### 描述\n\n"
        f"**中文：** {row['description_zh']}\n\n"
        f"**English:** {row['description_en']}\n\n"
        f"### 本章相关内容\n\n{row['context_zh']}\n"
    )
    return path, body


def make_plan() -> tuple[list[dict], list[dict], list[dict], list[str], list[str]]:
    errors: list[str] = []
    manifest, manifest_fields = read_csv(TABLES / "ku-manifest.csv")
    alignments, alignment_fields = read_csv(TABLES / "alignment.csv")
    candidates, _ = read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    alignment_map: dict[str, list[dict]] = {}
    for row in alignments:
        if row["candidate_id"] and not row["external_source"]:
            alignment_map.setdefault(row["candidate_id"], []).append(row)
    catalog_path = ROOT / "04-knowledge" / "accepted.yml"
    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8-sig"))
    accepted = set(catalog["units"])
    existing_ids = {row["ku_id"] for row in manifest}
    existing_paths = {row["card_path"] for row in manifest}
    plans: list[dict] = []
    new_rows: list[dict] = []
    updates: list[dict] = []
    additions: list[str] = []
    seen_groups: set[str] = set()
    seen_candidates: set[str] = set()
    for item in GROUPS:
        group = item["group"]
        if group in seen_groups:
            errors.append(f"duplicate group: {group}")
        seen_groups.add(group)
        ku_id = f"units/procedures/{item['slug']}"
        path, content = card(item)
        if ku_id in existing_ids or path in existing_paths or path in accepted:
            errors.append(f"KU/path already registered: {ku_id} {path}")
        if (ROOT / path).exists():
            errors.append(f"card file already exists: {path}")
        group_candidates = []
        for candidate_id in item["candidates"]:
            if candidate_id in seen_candidates:
                errors.append(f"candidate appears in more than one batch group: {candidate_id}")
            seen_candidates.add(candidate_id)
            candidate = candidate_map.get(candidate_id)
            rows = alignment_map.get(candidate_id, [])
            if not candidate or candidate.get("suggested_type") != "procedure":
                errors.append(f"not a procedure candidate: {candidate_id}")
            if len(rows) != 1 or rows[0]["decision"] != "new" or rows[0]["ku_id"]:
                errors.append(f"candidate decision is not an unregistered new row: {candidate_id}")
            elif f"group={group}" not in rows[0]["resolution_note"]:
                errors.append(f"S3 group mismatch for {candidate_id}: expected {group}")
            else:
                group_candidates.append(rows[0])
        if len(group_candidates) != len(item["candidates"]):
            errors.append(f"incomplete group membership: {group}")
        for source in item["sources"]:
            source_path = ROOT / "02-sources" / "02-Markdown" / source["file"]
            if not source_path.is_file():
                errors.append(f"missing source file: {source['file']}")
                continue
            source_text = source_path.read_text(encoding="utf-8-sig")
            if normalized(source["quote"]) not in normalized(source_text):
                errors.append(f"quote does not match source: {group} {source['file']} p.{source['page']}")
        for row in group_candidates:
            row["ku_id"] = ku_id
            updates.append(row)
        new_rows.append({"ku_id": ku_id, "type": "procedure", "canonical_name": item["zh"], "name_en": item["en"], "source_task": TASK, "card_path": path})
        additions.append(path)
        plans.append({"group": group, "candidates": item["candidates"], "ku_id": ku_id, "card_path": path, "title": f"{item['zh']}（{item['en']}）", "source_pages": [s["page"] for s in item["sources"]]})
    if len(GROUPS) != 23:
        errors.append(f"expected 23 reviewed procedure groups, found {len(GROUPS)}")
    if len(seen_candidates) != 24:
        errors.append(f"expected 24 candidate mappings, found {len(seen_candidates)}")
    if accepted & set(additions):
        errors.append("one or more planned card paths already appear in accepted.yml")
    return plans, new_rows, updates, additions, errors


def atomic_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    temp = path.with_suffix(path.suffix + ".s4tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def apply() -> None:
    plans, new_rows, updates, additions, errors = make_plan()
    if errors:
        raise SystemExit("preflight failed:\n" + "\n".join(errors))
    manifest, manifest_fields = read_csv(TABLES / "ku-manifest.csv")
    alignments, alignment_fields = read_csv(TABLES / "alignment.csv")
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")
    marker = "claims:\n"
    if accepted_text.count(marker) != 1:
        raise SystemExit("cannot find the unique claims section in accepted.yml")
    for item in GROUPS:
        path, content = card(item)
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")
    by_candidate = {row["candidate_id"]: row for row in updates}
    for row in alignments:
        if row["candidate_id"] in by_candidate and not row["external_source"]:
            row["ku_id"] = by_candidate[row["candidate_id"]]["ku_id"]
    atomic_csv(TABLES / "alignment.csv", alignments, alignment_fields)
    atomic_csv(TABLES / "ku-manifest.csv", manifest + new_rows, manifest_fields)
    accepted_text = accepted_text.replace(marker, "".join(f"- {path}\n" for path in additions) + marker, 1)
    accepted_path.write_text(accepted_text, encoding="utf-8-sig", newline="")
    print(f"registered groups={len(plans)} candidate_mappings={len(updates)} new_KUs={len(new_rows)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.apply:
        parser.error("choose exactly one of --dry-run or --apply")
    plans, _, updates, _, errors = make_plan()
    if errors:
        raise SystemExit("preflight failed:\n" + "\n".join(errors))
    if args.dry_run:
        for item in plans:
            print(f"{item['group']} -> {item['ku_id']} :: {','.join(item['candidates'])} :: p.{','.join(item['source_pages'])}")
        print(f"dry-run passed: groups={len(plans)} candidate_mappings={len(updates)}; no files written")
    else:
        apply()


if __name__ == "__main__":
    main()
