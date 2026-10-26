#!/usr/bin/env python3
"""Apply the evidence-bounded Chapter 2 emblem and endpoint batch.

Default mode is a read-only preflight. Use --apply only after reviewing it.
The write path snapshots every tracked target under the batch recovery folder
and rolls back the applied file set if any replacement fails.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from datetime import date
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
UNITS = ROOT / "04-knowledge" / "units"
PROCESS_DIR = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
PROCESS_REF = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp2-emblems-endpoints-20261026"
PROCESS_SLUG = "s3-s4-s5-s6-chp2-emblems-endpoints-20261026"
TODAY = "2026-10-26"
HASKELL_ID = "haskell-1980-rev-ed"
HASKELL_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)."
TRECCANI_URL = "https://www.treccani.it/enciclopedia/senigallia_%28Enciclopedia-Italiana%29/"
TRECCANI_CITATION = f"Ettore Ricci, Pasquale Rotondi, and Giuseppe Castellani, ‘Senigallia,’ *Enciclopedia Italiana* (1936). {TRECCANI_URL} Accessed {TODAY}."
TRECCANI_ID = "src-" + hashlib.sha256(TRECCANI_URL.encode("utf-8")).hexdigest()[:16]
SOURCE_FILES = {
    "sec-ii": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
    "sec-iv": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
}


def book_source(page: str, pdf_page: str, lines: str, summary: str, quote: str, file_key: str) -> dict:
    source_file = SOURCE_FILES[file_key]
    span = f"lines {lines}; print p. {page}; PDF physical p. {pdf_page}"
    return {
        "citation": HASKELL_CITATION,
        "location": f"第2章，印刷页{page}；PDF物理页{pdf_page}；OCR L{lines}",
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": source_file, "source_span": span},
    }


def treccani_source() -> dict:
    span = "entry heading and opening identification, lines 21–28"
    return {
        "citation": TRECCANI_CITATION,
        "location": "Enciclopedia Italiana, entry ‘SENIGALLIA’, heading and opening identification",
        "sentence_summary": "条目将 Senigallia 与 Sinigaglia 并列为同一地名，并说明其为城市；仅用于名称和身份对应。",
        "original_quotes": [{"source_span": span, "text": "SENIGALLIA (o Sinigaglia)"}],
        "evidence_ref": {"doc_id": TRECCANI_URL, "source_file": TRECCANI_URL, "source_span": span},
    }


CARDS = [
    {
        "candidate": "cand-4394", "ku_id": "units/works/baldacchino-twisted-columns", "type": "work",
        "zh": "圣彼得大殿华盖螺旋柱", "en": "Twisted Columns of the Baldacchino at St Peter’s Basilica",
        "description_zh": "本卡记录伯尔尼尼圣彼得大殿青铜华盖的巨型螺旋柱这一建筑构件组。哈斯克尔分别叙述其柱式传统和宗教图像语境；所称源自所罗门圣殿属于书中记载的传统，不在此确认为实际历史源流。",
        "description_en": "This unit records the group of giant twisted columns in Bernini’s bronze baldacchino at St Peter’s Basilica. Haskell discusses the column form’s tradition and religious context; the claimed derivation from Solomon’s Temple remains a reported tradition, not an independently established origin.",
        "sources": [book_source("35", "16", "44–45", "哈斯克尔称华盖最醒目的特征是巨型螺旋柱，并记载该柱式被认为源自耶路撒冷的所罗门圣殿。", "the most immediately striking feature of the baldacchino is the use of giant twisted columns", "sec-ii"), book_source("35", "16", "45", "作者以 ‘supposed to derive’ 表述螺旋柱与所罗门圣殿的传统关联。", "the twisted column was supposed to derive from Solomon’s Temple in Jerusalem", "sec-ii")],
        "sections": {
            "名称": [("描述性名称", "圣彼得大殿华盖螺旋柱／Twisted Columns of the Baldacchino at St Peter’s Basilica；项目描述性名称，非原题", "S1；第2章印刷页35 L44")],
            "基本信息": [("作品类型", "建筑构件组：华盖的巨型螺旋柱", "S1；第2章印刷页35 L44"), ("历史关联", "哈斯克尔称这一柱式被认为源自耶路撒冷的所罗门圣殿；保留其传统说法限定", "S1；第2章印刷页35 L45")],
            "本章相关内容": [("来源语境", "与圣彼得大殿华盖及古代大殿屏风中的螺旋柱传统相关；不与未具名、称在圣彼得大殿保存的单根柱合并", "S1；第2章印刷页35 L44–45")],
        },
        "prose": "本卡范围限于圣彼得大殿华盖上的螺旋柱构件。",
    },
    {
        "candidate": "cand-4395", "ku_id": "units/places/solomons-temple", "type": "place",
        "zh": "所罗门圣殿", "en": "Solomon’s Temple",
        "description_zh": "古代耶路撒冷圣殿地点。此卡只记录哈斯克尔在螺旋柱传统叙述中提到的地点名称和来源说法，不据此核实建筑沿革或柱式的实际来源。",
        "description_en": "The ancient temple site in Jerusalem. This unit records the place named in Haskell’s account of the twisted-column tradition; it does not verify the temple’s history or the actual origin of the column form.",
        "sources": [book_source("35", "16", "45", "哈斯克尔称螺旋柱被认为源自耶路撒冷的所罗门圣殿。", "Solomon’s Temple in Jerusalem", "sec-ii")],
        "sections": {
            "名称": [("原文名称", "Solomon’s Temple", "S1；第2章印刷页35 L45")],
            "基本信息": [("地点性质", "圣殿地点；哈斯克尔称其位于 Jerusalem", "S1；第2章印刷页35 L45"), ("来源所述关联", "螺旋柱被说成源自该圣殿；原文使用 ‘supposed to derive’", "S1；第2章印刷页35 L45")],
        },
        "prose": "来源记述是一项被报告的传统，不表示对建筑遗址、年代或技术传播的独立核验。",
    },
    {
        "candidate": "cand-4398", "ku_id": "units/terms/barberini-bee-emblem", "type": "term",
        "zh": "巴贝里尼蜜蜂纹章", "en": "Barberini Bee Emblem",
        "description_zh": "哈斯克尔所述巴贝里尼家族蜜蜂标识这一跨作品纹章概念。此 KU 统一记录符号身份；华盖、萨基饰带和科尔托纳天顶中的图像出现仍是不同的作品语境，不等同于同一件实物。",
        "description_en": "The Barberini family’s bee emblem as a cross-work symbolic concept in Haskell’s account. This KU records the shared emblem identity; its appearances on the baldacchino, Sacchi’s friezes, and Cortona’s ceiling remain distinct work contexts, not one physical object.",
        "sources": [book_source("35", "16", "47", "哈斯克尔描述华盖柱上的巴贝里尼蜜蜂。", "The Barberini bees crawl up the columns", "sec-ii"), book_source("51", "36", "92", "作者将蜜蜂列为巴贝里尼家族标识，并说它们见于萨基壁画周围的饰带。", "one of the three special insignia of the Barberini family", "sec-iv"), book_source("52", "37", "99", "科尔托纳天顶中的蜜蜂与月桂被哈斯克尔称为壁画的重要主题。", "the Bees and the Laurel ... are made the essential themes of the fresco", "sec-iv")],
        "sections": {
            "名称": [("纹章名称", "Barberini bees／巴贝里尼蜜蜂", "S1；第2章印刷页35 L47、页51 L92")],
            "基本信息": [("定义", "哈斯克尔列举的巴贝里尼家族纹章之一；本 KU 指符号概念，不指向任一单独雕刻或画面", "S1；第2章印刷页51 L92"), ("来源实例", "圣彼得大殿华盖：蜜蜂攀上柱身并悬于檐口青铜流苏", "S1；第2章印刷页35 L47"), ("来源实例", "萨基《神圣智慧》主壁画周围的彩绘及灰泥饰带", "S1；第2章印刷页51 L92"), ("来源实例", "科尔托纳巴贝里尼宫天顶：蜜蜂与月桂被称为壁画的重要主题", "S1；第2章印刷页52 L99")],
        },
        "prose": "各处纹章出现不代表其物质载体、制作时间或作者相同。",
    },
    {
        "candidate": "cand-4399", "ku_id": "units/terms/barberini-sun-emblem", "type": "term",
        "zh": "巴贝里尼太阳纹章", "en": "Barberini Sun Emblem",
        "description_zh": "哈斯克尔所述巴贝里尼太阳纹章这一跨作品符号概念。在萨基壁画中，作者还将太阳解释为智慧的惯用象征；这些象征用途不使太阳、智慧人格化形象或各作品中的太阳图像成为同一对象。",
        "description_en": "The Barberini sun emblem as a cross-work symbolic concept in Haskell’s account. For Sacchi’s fresco, the author also describes the sun as a conventional emblem of Wisdom; these symbolic uses do not equate the sun with personified Wisdom or with any individual depiction.",
        "sources": [book_source("35", "16", "47", "华盖柱头上方的太阳被称为巴贝里尼太阳。", "the Barberini sun blazes above the rich capitals", "sec-ii"), book_source("51", "36", "92", "哈斯克尔称太阳兼具智慧象征和巴贝里尼家族标识的双重意义。", "a conventional emblem for Wisdom ... one of the three special insignia of the Barberini family", "sec-iv")],
        "sections": {
            "名称": [("纹章名称", "Barberini sun／巴贝里尼太阳", "S1；第2章印刷页35 L47、页51 L92")],
            "基本信息": [("定义", "巴贝里尼家族太阳纹章；萨基壁画语境另将其作为智慧象征，依来源保留双重用途", "S1；第2章印刷页51 L92"), ("来源实例", "圣彼得大殿华盖柱头上方的太阳图像", "S1；第2章印刷页35 L47"), ("来源实例", "萨基《神圣智慧》中从中央女性形象胸前发出的太阳；此处记录来源所述图像关系", "S1；第2章印刷页51 L92")],
        },
        "prose": "本条记录跨作品沿用的巴贝里尼太阳纹章；各作品中的图像仍是不同描绘。",
    },
    {
        "candidate": "cand-4400", "ku_id": "units/terms/barberini-laurel-emblem", "type": "term",
        "zh": "巴贝里尼月桂纹章", "en": "Barberini Laurel Emblem",
        "description_zh": "哈斯克尔所述巴贝里尼月桂纹章这一跨作品符号概念。第2章先将华盖柱叶辨认为月桂、称其为另一项家族纹章，后又称其在科尔托纳天顶中成为重要主题。各处图像出现仍属不同作品语境。",
        "description_en": "The Barberini laurel emblem as a cross-work symbolic concept in Haskell’s account. Chapter 2 identifies the baldacchino’s column leaves as laurel and another family emblem, then describes it as an important theme in Cortona’s ceiling. The depictions remain distinct work contexts.",
        "sources": [book_source("35", "16", "47", "哈斯克尔将柱叶辨认为月桂，并称之为另一项巴贝里尼纹章。", "the leaves on the columns are those of the laurel—another Barberini emblem", "sec-ii"), book_source("51", "36", "92", "月桂与蜜蜂一起见于萨基主壁画周围的饰带。", "the bees and the laurel—feature prominently in the friezes", "sec-iv"), book_source("52", "37", "99", "科尔托纳天顶中的月桂被称为壁画的重要主题。", "the Bees and the Laurel ... are made the essential themes of the fresco", "sec-iv")],
        "sections": {
            "名称": [("纹章名称", "Barberini laurel／巴贝里尼月桂", "S1；第2章印刷页35 L47、页51 L92")],
            "基本信息": [("定义", "哈斯克尔认定为巴贝里尼家族纹章之一的月桂符号；不与传统葡萄藤混同", "S1；第2章印刷页35 L47"), ("来源实例", "圣彼得大殿华盖柱上的月桂叶，与传统葡萄藤区分", "S1；第2章印刷页35 L47"), ("来源实例", "萨基主壁画周围饰带中的月桂纹章", "S1；第2章印刷页51 L92"), ("来源实例", "科尔托纳巴贝里尼宫天顶壁画中的月桂主题", "S1；第2章印刷页52 L99")],
        },
        "prose": "本条记录跨作品沿用的巴贝里尼月桂纹章；各作品中的图像仍是不同描绘。",
    },
    {
        "candidate": "cand-4692", "ku_id": "units/works/sacchi-divine-wisdom-friezes", "type": "work",
        "zh": "萨基《神圣智慧》周围的彩绘及灰泥饰带", "en": "Painted and Stucco Friezes around Sacchi’s Divine Wisdom",
        "description_zh": "哈斯克尔所述围绕萨基《神圣智慧》主壁画的彩绘及灰泥装饰饰带。来源称蜜蜂和月桂纹章在其中突出出现；未据此推定饰带的独立作者、创作年代或与主壁画相同的作品边界。",
        "description_en": "The painted and stucco decorative friezes that Haskell describes around the main fresco of Sacchi’s Divine Wisdom. The source says the bee and laurel emblems feature prominently there; it does not establish a separate maker, date, or the friezes’ exact boundary relative to the main fresco.",
        "sources": [book_source("51", "36", "92", "哈斯克尔称蜜蜂和月桂纹章突出见于围绕主壁画的彩绘及灰泥饰带。", "the bees and the laurel ... feature prominently in the friezes of paint and stucco which surround the main fresco", "sec-iv")],
        "sections": {
            "名称": [("描述性题名", "萨基《神圣智慧》周围的彩绘及灰泥饰带／Painted and Stucco Friezes around Sacchi’s Divine Wisdom；项目描述性题名", "S1；第2章印刷页51 L92")],
            "基本信息": [("作品类型", "围绕主壁画的装饰饰带", "S1；第2章印刷页51 L92"), ("媒材", "彩绘与灰泥", "S1；第2章印刷页51 L92"), ("来源实例", "巴贝里尼蜜蜂与月桂纹章突出出现于饰带", "S1；第2章印刷页51 L92")],
        },
        "prose": "哈斯克尔将饰带描述为围绕《神圣智慧》主壁画的彩绘及灰泥装饰。",
    },
    {
        "candidate": "cand-4681", "ku_id": "units/terms/love-personified-sacchi-divine-wisdom", "type": "term",
        "zh": "萨基《神圣智慧》中的爱之人格化形象", "en": "Love Personified in Sacchi’s Divine Wisdom",
        "description_zh": "萨基《神圣智慧》壁画中的爱之人格化形象，按哈斯克尔描述参与寓意行动；作为图像学概念记录，不视为历史人物。",
        "description_en": "The personified figure of Love in Sacchi’s Divine Wisdom, described by Haskell as taking part in the allegorical action. This is recorded as an iconographic concept, not a historical person.",
        "sources": [book_source("51", "36", "92", "哈斯克尔称智慧命令爱与恐惧控制兽性激情欲望与愤怒；原文不配对各角色。", "is shown ordering Love and Fear to control the bestial passions of Lust and Wrath", "sec-iv")],
        "sections": {
            "名称": [("原文概念名称", "Love，萨基《神圣智慧》中的人格化形象", "S1；第2章印刷页51 L92")],
            "基本信息": [("图像学角色", "与 Fear 一同受命控制 Lust 和 Wrath；来源未说明一对一配对", "S1；第2章印刷页51 L92"), ("对象边界", "寓意形象／概念，不作为历史人物", "S1；第2章印刷页51 L92")],
        },
        "prose": "哈斯克尔将 Love 与 Fear 描写为共同控制 Lust 与 Wrath；没有作一对一配对。",
    },
    {
        "candidate": "cand-4702", "ku_id": "units/places/senigallia-sinigaglia", "type": "place",
        "zh": "西尼加利亚", "en": "Senigallia (Sinigaglia)",
        "description_zh": "哈斯克尔以旧式拼写 Sinigaglia 称呼亚得里亚海沿岸的一处港口。Treccani《意大利百科全书》将 Senigallia 与 Sinigaglia 并列为同一地名。本卡采用书中拼写并记录规范对应；外部来源只支持名称与地点身份，不核实布拉乔利尼滞留事件。",
        "description_en": "Haskell uses the spelling Sinigaglia for a port on the Adriatic coast. The Treccani Enciclopedia Italiana lists Senigallia and Sinigaglia as the same place name. This unit preserves the book’s form and records the normalized identity; the external source supports the name and place identity only, not Bracciolini’s reported stay.",
        "sources": [book_source("52", "37", "99", "哈斯克尔称布拉乔利尼被困在 Sinigaglia 这一亚得里亚海小港。", "Bishop of Sinigaglia. Stranded in this little port on the Adriatic coast", "sec-iv"), treccani_source()],
        "sections": {
            "名称": [("书中名称", "Sinigaglia", "S1；第2章印刷页52 L99"), ("规范对应名称", "Senigallia；Treccani 条目将 Senigallia 与 Sinigaglia 并列", "S3；Treccani《Enciclopedia Italiana》条目标题与开篇，访问于2026-10-26")],
            "基本信息": [("地点性质", "城市／港口；哈斯克尔称其为亚得里亚海沿岸小港", "S1；第2章印刷页52 L99"), ("身份核对范围", "Treccani 确认 Senigallia／Sinigaglia 名称对应；不核实哈斯克尔叙述的具体事件", "S3；Treccani《Enciclopedia Italiana》条目标题与开篇")],
            "相关活动": [("来源所述活动", "Francesco Bracciolini 在 Sinigaglia 滞留期间写下抱怨信；确切日期、地点边界与收信人未明", "S1；第2章印刷页52 L99")],
        },
        "prose": "原书拼写保留为来源名称；Treccani 的名称对应只解决地点身份，不为本书叙述补充事实。",
        "external_link": f"[Treccani《Senigallia》，Enciclopedia Italiana (1936)]({TRECCANI_URL}) — 条目写作 ‘Senigallia (o Sinigaglia)’；仅用于名称与地点身份对应。",
    },
    {
        "candidate": "cand-4704", "ku_id": "units/terms/divine-providence-personified-barberini-ceiling", "type": "term",
        "zh": "巴贝里尼宫天顶中的神意人格化形象", "en": "Divine Providence Personified in the Barberini Ceiling",
        "description_zh": "哈斯克尔所述科尔托纳巴贝里尼宫天顶中央的神意人格化形象。该概念限于此处图像角色，不与一般神学意义的神意或天顶作品本身合并。",
        "description_en": "The personified figure of Divine Providence at the centre of Cortona’s Barberini Palace ceiling in Haskell’s account. This unit is limited to the iconographic role and remains distinct from general theological uses of Providence and from the ceiling work itself.",
        "sources": [book_source("52", "37", "99–100", "哈斯克尔描述神意位于天顶中央并指挥美德与不朽等拟人形象。", "In the centre of the ceiling Divine Providence", "sec-iv")],
        "sections": {
            "名称": [("原文概念名称", "Divine Providence personified in Cortona’s Barberini ceiling", "S1；第2章印刷页52 L99–100")],
            "基本信息": [("图像学角色", "天顶中央的人格化形象；统御 Present、Future、Time 与 Fates，并命令 Immortality 为美德加冕", "S1；第2章印刷页52 L99–100"), ("对象边界", "特定作品中的寓意形象；不等同于一般神学概念或作品本身", "S1；第2章印刷页52 L99–100")],
        },
        "prose": "上述角色、动作和称谓均按哈斯克尔的图像描述记录。",
    },
    {
        "candidate": "cand-4720", "ku_id": "units/terms/abundance-personified-barberini-ceiling", "type": "term",
        "zh": "巴贝里尼宫天顶中的丰饶人格化形象", "en": "Abundance Personified in the Barberini Ceiling",
        "description_zh": "哈斯克尔所述科尔托纳巴贝里尼宫天顶中的丰饶人格化形象。书中转述解释者将其联系到年轻枢机安东尼奥，并提到其后方的粮仓；此为来源所载图像解释，不与该历史人物等同。",
        "description_en": "The personified figure of Abundance in Cortona’s Barberini Palace ceiling as described by Haskell. The book reports interpreters linking the figure to the younger Cardinal Antonio and mentioning granaries behind it; this is an attributed iconographic interpretation, not an identity between the allegory and the historical person.",
        "sources": [book_source("52", "37", "100", "哈斯克尔转述解释者将丰饶形象联系到年轻枢机安东尼奥及其修建的粮仓。", "Abundance stood for young Cardinal Antonio and behind him could be seen the granaries he built", "sec-iv")],
        "sections": {
            "名称": [("原文概念名称", "Abundance personified in Cortona’s Barberini ceiling", "S1；第2章印刷页52 L100")],
            "基本信息": [("图像学角色", "天顶副主题之一；来源称解释者将其联系到年轻枢机安东尼奥", "S1；第2章印刷页52 L100"), ("解释范围", "粮仓与人物对应是书中转述的解释，不等同于该历史人物", "S1；第2章印刷页52 L100")],
        },
        "prose": "书中将 Abundance 联系到年轻枢机安东尼奥，保留为解释者所述的图像解读。",
    },
    {
        "candidate": "cand-4724", "ku_id": "units/terms/tumbling-giants-barberini-ceiling", "type": "term",
        "zh": "巴贝里尼宫天顶中的翻滚巨人群像", "en": "Tumbling Giants in the Barberini Ceiling",
        "description_zh": "哈斯克尔在科尔托纳巴贝里尼宫天顶描写的翻滚巨人群像。作者称其营造正在发生冲突的印象，并将观者卷入教皇对抗邪恶力量的寓意阐释；该群像是作品中的图像主题，不作为历史人物群体。",
        "description_en": "The group of tumbling giants described by Haskell in Cortona’s Barberini Palace ceiling. The author says they convey an impression of conflict and interprets the visitor as drawn into the Pope’s war against evil; the group is an iconographic subject, not a historical collective.",
        "sources": [book_source("52", "37", "101–102", "哈斯克尔称翻滚巨人群像营造正在发生的冲突感。", "writhing masses of raw, red, tumbling giants -- convey the impression of some tremendous conflict", "sec-iv"), book_source("53", "38", "107", "跨页续句称观者也被卷入教皇对抗邪恶力量的寓意。", "head so that he too is inextricably involved in the Pope’s strenuous war against the forces of evil", "sec-iv")],
        "sections": {
            "名称": [("描述性名称", "Tumbling Giants in Cortona’s Barberini ceiling／科尔托纳巴贝里尼宫天顶中的翻滚巨人群像", "S1；第2章印刷页52 L101–102、页53 L107；项目描述性名称")],
            "基本信息": [("图像学对象", "天顶中的一组翻滚巨人；作为作品描绘的群像主题记录", "S1；第2章印刷页52 L101–102"), ("来源解释", "作者称其营造冲突印象，并将观者描述为卷入教皇对抗邪恶的寓意", "S1；第2章印刷页52 L101–102、页53 L107")],
        },
        "prose": "本卡只记录哈斯克尔描写的翻滚巨人群像，不推断各形象的个体身份。",
    },
]


SAME_MERGES = {
    "cand-4675": {"alignment_id": "aln-4858", "root": "cand-4399", "ku_id": "units/terms/barberini-sun-emblem", "detail": "此候选记录萨基《神圣智慧》中的太阳图像；其巴贝里尼太阳纹章身份与 cand-4399 相同，具体画面出现仍只属于萨基作品语境。"},
    "cand-4676": {"alignment_id": "aln-4859", "root": "cand-4398", "ku_id": "units/terms/barberini-bee-emblem", "detail": "此候选记录萨基壁画周围饰带中的蜜蜂图像；其巴贝里尼蜜蜂纹章身份与 cand-4398 相同，具体饰带出现仍保留独立语境。"},
    "cand-4677": {"alignment_id": "aln-4860", "root": "cand-4400", "ku_id": "units/terms/barberini-laurel-emblem", "detail": "此候选记录萨基壁画周围饰带中的月桂图像；其巴贝里尼月桂纹章身份与 cand-4400 相同，具体饰带出现仍保留独立语境。"},
    "cand-4721": {"alignment_id": "aln-4904", "root": "cand-4398", "ku_id": "units/terms/barberini-bee-emblem", "detail": "此候选记录科尔托纳天顶中的蜜蜂主题；其巴贝里尼蜜蜂纹章身份与 cand-4398 相同，天顶中的图像出现仍保留独立语境。"},
    "cand-4722": {"alignment_id": "aln-4905", "root": "cand-4400", "ku_id": "units/terms/barberini-laurel-emblem", "detail": "此候选记录科尔托纳天顶中的月桂主题；其巴贝里尼月桂纹章身份与 cand-4400 相同，天顶中的图像出现仍保留独立语境。"},
}


RELATION_CANDIDATES = [
    {"subject": "units/works/andrea-sacchi-allegory-of-divine-wisdom", "object": "units/terms/barberini-sun-emblem", "predicate": "has_subject", "role": "智慧人格化形象胸前发出的太阳纹章", "scope": "Haskell将该太阳称为 Wisdom 的惯用象征及 Barberini 家族标识；仅记录萨基作品中的图像描述。", "span": "line 92; print p. 51; PDF physical p. 36", "file": SOURCE_FILES["sec-iv"], "statement": "st-chp2-seciv-l91-94-wisdom-figure-emits-sun"},
    {"subject": "units/works/sacchi-divine-wisdom-friezes", "object": "units/terms/barberini-bee-emblem", "predicate": "has_subject", "role": "作为装饰图像出现的巴贝里尼蜜蜂", "scope": "Haskell称蜜蜂突出见于围绕主壁画的饰带；不据此推断饰带作者或制作时间。", "span": "line 92; print p. 51; PDF physical p. 36", "file": SOURCE_FILES["sec-iv"], "statement": "st-chp2-seciv-l91-94-bees-feature-in-surrounding-friezes"},
    {"subject": "units/works/sacchi-divine-wisdom-friezes", "object": "units/terms/barberini-laurel-emblem", "predicate": "has_subject", "role": "作为装饰图像出现的巴贝里尼月桂", "scope": "Haskell称月桂突出见于围绕主壁画的饰带；不据此推断饰带作者或制作时间。", "span": "line 92; print p. 51; PDF physical p. 36", "file": SOURCE_FILES["sec-iv"], "statement": "st-chp2-seciv-l91-94-laurel-features-in-surrounding-friezes"},
    {"subject": "units/works/pietro-da-cortona-glorification-of-the-reign-of-urban-viii", "object": "units/terms/barberini-bee-emblem", "predicate": "has_subject", "role": "哈斯克尔称为天顶壁画重要主题的蜜蜂纹章", "scope": "来源将 Bees 与 Laurel 称为该壁画的重要主题；保留其相较 Sacchi 处理的来源限定。", "span": "line 99; print p. 52; PDF physical p. 37", "file": SOURCE_FILES["sec-iv"], "statement": "st-chp2-seciv-l96-104-bee-emblem-ceiling-theme"},
    {"subject": "units/works/pietro-da-cortona-glorification-of-the-reign-of-urban-viii", "object": "units/terms/barberini-laurel-emblem", "predicate": "has_subject", "role": "哈斯克尔称为天顶壁画重要主题的月桂纹章", "scope": "来源将 Bees 与 Laurel 称为该壁画的重要主题；保留其相较 Sacchi 处理的来源限定。", "span": "line 99; print p. 52; PDF physical p. 37", "file": SOURCE_FILES["sec-iv"], "statement": "st-chp2-seciv-l96-104-laurel-emblem-ceiling-theme"},
    {"subject": "units/works/pietro-da-cortona-glorification-of-the-reign-of-urban-viii", "object": "units/terms/divine-providence-personified-barberini-ceiling", "predicate": "has_subject", "role": "天顶中央的神意人格化形象", "scope": "只记录 Haskell 对天顶构图及拟人化角色的描述，不推广至一般神学概念。", "span": "line 99; print p. 52; PDF physical p. 37", "file": SOURCE_FILES["sec-iv"], "statement": "st-chp2-seciv-l96-104-central-providence-composition"},
    {"subject": "units/works/pietro-da-cortona-glorification-of-the-reign-of-urban-viii", "object": "units/terms/tumbling-giants-barberini-ceiling", "predicate": "has_subject", "role": "传达冲突印象的翻滚巨人群像", "scope": "保留 Haskell 对冲突印象与观者参与的阐释；第2章印刷页53 L107 为跨页续句。", "span": "lines 101–102 and 107; print pp. 52–53; PDF physical pp. 37–38", "file": SOURCE_FILES["sec-iv"], "statement": "st-chp2-seciv-l96-104-giants-conflict-continuation"},
    {"subject": "units/persons/francesco-bracciolini", "object": "units/places/senigallia-sinigaglia", "predicate": "located_at", "time": "", "role": "来源报告的暂时滞留地点", "scope": "Haskell称 Bracciolini 被困于该亚得里亚海港口；确切日期、地点边界和滞留原因未明。", "span": "line 99; print p. 52; PDF physical p. 37", "file": SOURCE_FILES["sec-iv"], "statement": "st-chp2-seciv-l96-104-bracciolini-stranded-sinigaglia"},
    {"subject": "units/places/bologna", "object": "units/institutions/papal-states", "predicate": "part_of", "time": "", "role": "哈斯克尔称作教皇国的第二首都", "scope": "仅记录第8章的历史性表述；来源未说明正式宪制地位或精确时期，不延伸至现代行政关系。", "span": "line 8; print p. 203; PDF physical p. 1", "file": "02-sources/02-Markdown/08_CHP-8_sec_i.md", "statement": "st-chp8-p203-bologna-second-capital"},
]


def table_for(section: str, rows: list[tuple[str, str, str]]) -> str:
    parts = [f"### {section}", "", "| 字段 | 值 | 证据 |", "|---|---|---|"]
    for field, value, evidence in rows:
        parts.append(f"| {field} | {value} | {evidence} |")
    return "\n".join(parts)


def render_card(spec: dict) -> tuple[Path, bytes]:
    source_task = "patrons-and-painters-full-book-s2"
    frontmatter = {
        "title": f"{spec['zh']}（{spec['en']}）",
        "name_en": spec["en"],
        "type": spec["type"],
        "evidence_status": "source_backed",
        "sources": spec["sources"],
        "created": TODAY,
        "updated": TODAY,
        "process_ref": PROCESS_REF,
    }
    yaml_text = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True, width=110).rstrip()
    body = ["## 内容", "", "### 描述", f"**中文：** {spec['description_zh']}", f"**English:** {spec['description_en']}", ""]
    for section, rows in spec["sections"].items():
        body.extend([table_for(section, rows), ""])
    body.extend(["### 本章相关内容", spec["prose"], "", "## 关系与证据", ""])
    if spec.get("external_link"):
        body.extend(["### 身份与外部链接", spec["external_link"], ""])
    body.extend(["### 关系记录", ""])
    text = "---\n" + yaml_text + "\n---\n\n" + "\n".join(body).rstrip() + "\n"
    return UNITS / (spec["ku_id"].removeprefix("units/") + ".md"), text.encode("utf-8")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool, str]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    header = list(rows[0].keys()) if rows else next(csv.reader(io.StringIO(text)))
    return header, rows, bom, newline


def patch_csv_bytes(path: Path, key_field: str, updates: dict[str, dict[str, str]], appends: list[dict[str, str]] | None = None) -> bytes:
    header, current, bom, newline = read_csv(path)
    by_key = {row[key_field]: row for row in current}
    for key, values in updates.items():
        if key not in by_key:
            raise ValueError(f"{path.name}: missing {key_field}={key}")
        by_key[key].update(values)
    appends = appends or []
    keys = [row[key_field] for row in appends]
    if len(keys) != len(set(keys)) or set(keys) & set(by_key):
        raise ValueError(f"{path.name}: duplicate appended {key_field}")
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    rewritten = []
    key_index = header.index(key_field)
    for raw_line in text.splitlines(keepends=True):
        ending = "\r\n" if raw_line.endswith("\r\n") else "\n" if raw_line.endswith("\n") else ""
        line = raw_line[:-len(ending)] if ending else raw_line
        parsed = next(csv.reader([line]))
        key = parsed[key_index] if key_index < len(parsed) else ""
        if key not in updates:
            rewritten.append(raw_line)
        else:
            stream = io.StringIO(newline="")
            writer = csv.DictWriter(stream, fieldnames=header, extrasaction="ignore", lineterminator=ending or newline)
            writer.writerow(by_key[key])
            rewritten.append(stream.getvalue())
    if appends:
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=header, extrasaction="ignore", lineterminator=newline)
        writer.writerows(appends)
        if rewritten and not rewritten[-1].endswith(("\n", "\r")):
            rewritten.append(newline)
        rewritten.append(stream.getvalue())
    return (b"\xef\xbb\xbf" if bom else b"") + "".join(rewritten).encode("utf-8")


def with_snapshot(changes: dict[Path, bytes], apply_changes: bool) -> None:
    changed = {path: content for path, content in changes.items() if not path.exists() or path.read_bytes() != content}
    print(json.dumps({"mode": "apply" if apply_changes else "preflight", "files": len(changed), "paths": [p.relative_to(ROOT).as_posix() for p in changed]}, ensure_ascii=False, indent=2))
    if not apply_changes or not changed:
        return
    recovery = ROOT / "06-runtime" / "recovery" / PROCESS_SLUG
    recovery.mkdir(parents=True, exist_ok=False)
    originals = {path: path.read_bytes() if path.exists() else None for path in changed}
    for index, (path, raw) in enumerate(originals.items(), start=1):
        if raw is not None:
            backup = recovery / f"{index:02d}-{path.name}.before"
            backup.write_bytes(raw)
    applied = []
    try:
        for path, raw in changed.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            applied.append(path)
    except Exception:
        for path in reversed(applied):
            old = originals[path]
            if old is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(old)
        raise
    print(f"Applied {len(applied)} files. Recovery snapshot: {recovery.relative_to(ROOT).as_posix()}")


def build_changes() -> tuple[dict[Path, bytes], dict]:
    changes: dict[Path, bytes] = {}
    card_paths = {}
    for spec in CARDS:
        path, raw = render_card(spec)
        if path.exists():
            raise ValueError(f"target card already exists: {path.relative_to(ROOT)}")
        card_paths[spec["candidate"]] = path.relative_to(ROOT).as_posix()
        changes[path] = raw

    alignment_path = TABLES / "alignment.csv"
    _, alignments, _, _ = read_csv(alignment_path)
    by_alignment = {row["alignment_id"]: row for row in alignments}
    alignment_updates = {}
    for spec in CARDS:
        candidate = spec["candidate"]
        row = next((r for r in alignments if r["candidate_id"] == candidate and r.get("ku_id") == ""), None)
        if row is None or row["decision"] != "new":
            raise ValueError(f"expected one unmapped new alignment row for {candidate}")
        note = row["resolution_note"] + f"；S4登记于 {spec['ku_id']}；批次记录见 {PROCESS_REF}。"
        updates = {"ku_id": spec["ku_id"], "process_ref": PROCESS_SLUG, "resolution_note": note}
        if candidate == "cand-4702":
            updates.update({"external_source": "Treccani, Enciclopedia Italiana", "external_id": TRECCANI_URL, "accessed_date": TODAY})
            updates["resolution_note"] = note + " S3 identity note: Treccani Enciclopedia Italiana (1936), heading ‘Senigallia (o Sinigaglia)’, supports the same named place; no same-type place KU exists. This identifies the spelling only and does not validate Haskell’s event narrative."
        alignment_updates[row["alignment_id"]] = updates
    for candidate, spec in SAME_MERGES.items():
        row = by_alignment.get(spec["alignment_id"])
        if row is None or row["candidate_id"] != candidate or row["decision"] != "new" or row["ku_id"]:
            raise ValueError(f"expected unmapped new alignment {spec['alignment_id']} for {candidate}")
        prior = row["resolution_note"]
        note = (f"prior_decision=new; prior_group=sg3-term-{candidate}; prior_resolution_note={prior}; "
                f"S3 reassessment: same emblem concept as {spec['root']}; members are distinct depiction occurrences, not one physical object. "
                f"Haskell ch.2 pp.35, 51–52 names the Barberini sun/bees/laurel consistently across the baldacchino, Sacchi’s friezes, and Cortona’s ceiling. "
                f"S3 same -> {spec['ku_id']}; see {PROCESS_REF}.")
        alignment_updates[spec["alignment_id"]] = {"decision": "same", "ku_id": spec["ku_id"], "process_ref": PROCESS_SLUG, "resolution_note": note}
    changes[alignment_path] = patch_csv_bytes(alignment_path, "alignment_id", alignment_updates)

    candidate_path = TABLES / "entity-candidates.csv"
    detail_updates = {
        "cand-4675": {"detail": SAME_MERGES["cand-4675"]["detail"]},
        "cand-4676": {"detail": SAME_MERGES["cand-4676"]["detail"]},
        "cand-4677": {"detail": SAME_MERGES["cand-4677"]["detail"]},
        "cand-4721": {"detail": SAME_MERGES["cand-4721"]["detail"]},
        "cand-4722": {"detail": SAME_MERGES["cand-4722"]["detail"]},
        "cand-4702": {"detail": "Haskell calls this the Adriatic port where Bracciolini was stranded and prints Sinigaglia; Treccani Enciclopedia Italiana (1936) identifies Senigallia as ‘Sinigaglia’ as well. Record one historical place identity under the book spelling, with Senigallia as the normalized name; the external source supports name identity only, not the reported episode."},
    }
    candidate_rows = read_csv(candidate_path)[1]
    found = {r["candidate_id"] for r in candidate_rows}
    if set(detail_updates) - found:
        raise ValueError(f"missing candidate rows: {sorted(set(detail_updates)-found)}")
    changes[candidate_path] = patch_csv_bytes(candidate_path, "candidate_id", detail_updates)

    manifest_path = TABLES / "ku-manifest.csv"
    manifest_header, manifest, _, _ = read_csv(manifest_path)
    existing_kus = {r["ku_id"] for r in manifest}
    if existing_kus & {spec["ku_id"] for spec in CARDS}:
        raise ValueError("a planned KU already exists in ku-manifest.csv")
    manifest_rows = [{"ku_id": s["ku_id"], "type": s["type"], "canonical_name": s["zh"], "name_en": s["en"], "source_task": "patrons-and-painters-full-book-s2", "card_path": card_paths[s["candidate"]]} for s in CARDS]
    changes[manifest_path] = patch_csv_bytes(manifest_path, "ku_id", {}, manifest_rows)

    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    accepted_raw = accepted_path.read_bytes()
    accepted_text = accepted_raw.decode("utf-8-sig")
    bom = accepted_raw.startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if "\r\n" in accepted_text else "\n"
    lines = accepted_text.splitlines(keepends=True)
    accepted_entries = {f"- {path}" for path in card_paths.values()}
    if any(line.rstrip("\r\n") in accepted_entries for line in lines):
        raise ValueError("one or more planned card paths already occur in accepted.yml")
    claims_index = next((i for i, line in enumerate(lines) if line.rstrip("\r\n") == "claims:"), None)
    if claims_index is None:
        raise ValueError("accepted.yml has no claims section")
    lines[claims_index:claims_index] = [f"- {path}{newline}" for path in card_paths.values()]
    changes[accepted_path] = (b"\xef\xbb\xbf" if bom else b"") + "".join(lines).encode("utf-8")

    relations_path = TABLES / "relations.csv"
    relation_header, old_relations, _, _ = read_csv(relations_path)
    last_number = max(int(r["relation_id"].removeprefix("rel-")) for r in old_relations)
    existing_natural = {(r["subject_ku_id"], r["object_ku_id"], r["predicate"], r.get("time", "")) for r in old_relations}
    relation_rows = []
    for offset, spec in enumerate(RELATION_CANDIDATES, start=1):
        key = (spec["subject"], spec["object"], spec["predicate"], spec.get("time", ""))
        if key in existing_natural:
            raise ValueError(f"duplicate formal relation natural key: {key}")
        existing_natural.add(key)
        relation_rows.append({
            "relation_id": f"rel-{last_number + offset}", "subject_ku_id": spec["subject"], "object_ku_id": spec["object"],
            "predicate": spec["predicate"], "time": spec.get("time", ""), "role": spec["role"], "scope": spec["scope"],
            "origin": "book", "status": "formal", "source_id": HASKELL_ID, "source_span": spec["span"], "source_file": spec["file"],
            "note": f"S2 statement: {spec['statement']}. Haskell, chapter 2 or 8 as located in source_span; source-scoped relation only.",
        })
    known_kus = existing_kus | {s["ku_id"] for s in CARDS}
    for row in relation_rows:
        if row["subject_ku_id"] not in known_kus or row["object_ku_id"] not in known_kus:
            raise ValueError(f"planned relation has missing KU endpoint: {row['relation_id']}")
    # Relations are adjudicated here but written to relations.csv as a separately
    # reviewed semantic edit; this batch helper only prepares S3/S4 card mappings.
    return changes, {"new_cards": len(CARDS), "same_merges": len(SAME_MERGES), "formal_relations_planned": len(relation_rows), "candidate_details_updated": len(detail_updates)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply after reviewing the default preflight")
    args = parser.parse_args()
    changes, stats = build_changes()
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    with_snapshot(changes, args.apply)


if __name__ == "__main__":
    main()
