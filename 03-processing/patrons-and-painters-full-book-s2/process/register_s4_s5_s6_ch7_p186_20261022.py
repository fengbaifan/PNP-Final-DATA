from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
RELATIONS = TABLES / "relations.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
SOURCE_FILE = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
SOURCE_ID = "haskell-1980-rev-ed"
DATE = "2026-10-22"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s4-s5-s6-ch7-p186-direct-endpoints-20261022"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


ITEMS = [
    {
        "candidate_id": "cand-6863", "group": "sg3-place-cand-6863",
        "ku_id": "units/places/mazarin-small-gallery-described-by-brienne",
        "card_path": "04-knowledge/units/places/mazarin-small-gallery-described-by-brienne.md",
        "type": "place", "title": "马萨然住所的小画廊（Small Gallery in Mazarin’s Apartments）",
        "name_en": "Small Gallery in Mazarin’s Apartments",
        "location": "第7章；印刷页186；Markdown L216；PDF物理页24。",
        "summary": "Brienne的回忆称Mazarin住所的新公寓内有一处小画廊，并描述其中的Scipio题材羊毛挂毯。原书未给画廊专名；本卡与第7章较早提到的上层画廊保持区分。",
        "quotes": [("L216; print p.186; PDF physical p.24", "la petite galerie que étoit tapissée de Scipion tout de laine")],
        "description_zh": "本卡记录Brienne回忆中Mazarin住所新公寓内的一处小画廊。她的叙述称画廊悬有Scipio题材的羊毛挂毯；原书没有给出画廊专名。该空间不与第7章较早记载的上层画廊合并。",
        "description_en": "This card records the small gallery in the new apartments of Mazarin’s residence described in Brienne’s memoir. The account says that a wool tapestry depicting Scipio hung there; the book gives no proper name for the gallery. This space is kept separate from the upper gallery described earlier in Chapter 7.",
        "fields": [
            ("地点性质", "Mazarin住所新公寓内的小画廊；原书未给专名。", "S1；第7章 p.186 L216。"),
            ("空间内容", "Brienne称Scipio题材的羊毛挂毯悬于此处。", "S1；第7章 p.186 L216。"),
        ],
    },
    {
        "candidate_id": "cand-6864", "group": "workgrp-c6af6e78538186",
        "ku_id": "units/works/scipio-tapestry-brienne-account",
        "card_path": "04-knowledge/units/works/scipio-tapestry-brienne-account.md",
        "type": "work", "title": "描绘西庇阿的羊毛挂毯（Wool Tapestry Depicting Scipio）",
        "name_en": "Wool Tapestry Depicting Scipio",
        "location": "第7章；印刷页186；Markdown L216；PDF物理页24。",
        "summary": "Brienne回忆中提到的一件Scipio题材挂毯；引文称其为羊毛制，并归述其曾属Saint-André元帅、设计取自Jules Romain。版本与归属均保留来源层级。",
        "quotes": [("L216; print p.186; PDF physical p.24", "tapisserie de Scipion tout de laine qui avoit été au maréchal de SaintAndré, la plus belle tapisserie du Cardinal, sur les desseins de Jules Romain")],
        "description_zh": "本卡记录Brienne回忆中Mazarin住所小画廊的Scipio题材羊毛挂毯。引文称其曾属Saint-André元帅，并把设计归于Jules Romain；这些均是来源记载，不构成对具体存世版本或创作者身份的独立核验。Brienne还称它是Cardinal最美的挂毯，这是原文评价而非核定排名。",
        "description_en": "This card records the wool tapestry depicting Scipio that appears in Brienne’s account of the small gallery in Mazarin’s residence. The quotation says that it had belonged to the Marshal of Saint-André and attributes its designs to Jules Romain; neither statement independently identifies a surviving version or verifies the maker. Brienne also calls it the Cardinal’s finest tapestry, a reported evaluation rather than an established ranking.",
        "fields": [
            ("作品类型", "挂毯。", "S1；第7章 p.186 L216。"),
            ("材质", "羊毛；据Brienne法文“tout de laine”。", "S1；第7章 p.186 L216。"),
            ("题材", "Scipio。", "S1；第7章 p.186 L216。"),
            ("前任持有人（来源记载）", "Brienne称挂毯曾属Saint-André元帅；其完整身份仍待证。", "S1；第7章 p.186 L216。"),
            ("设计归属（来源记载）", "Brienne称设计取自Jules Romain；不等于独立作者核验。", "S1；第7章 p.186 L216。"),
            ("原文评价", "Brienne称其为Cardinal最美的挂毯；保留为来源评价。", "S1；第7章 p.186 L216。"),
        ],
    },
    {
        "candidate_id": "cand-6872", "group": "sg3-place-cand-6872",
        "ku_id": "units/places/seine-river",
        "card_path": "04-knowledge/units/places/seine-river.md",
        "type": "place", "title": "塞纳河（River Seine）", "name_en": "River Seine",
        "location": "第7章；印刷页186；Markdown L219；PDF物理页24。",
        "summary": "Haskell提到一支Theatine修会分支定居在塞纳河岸；该处未给出具体建筑或河岸地址。",
        "quotes": [("L219; print p.186; PDF physical p.24", "which settled on the banks of the Seine")],
        "description_zh": "本卡登记第7章所称的塞纳河。该段仅把河岸作为一支Theatine修会分支定居的位置参照，没有给出具体修院、河岸地址或该修会整体的所在地。",
        "description_en": "This card records the River Seine named in Chapter 7. The passage uses its banks to locate the settlement of one branch of the Theatine order; it gives no specific house, riverbank address, or location for the order as a whole.",
        "fields": [("地理要素", "河流；Haskell以其河岸描述一支Theatine修会分支的定居位置。", "S1；第7章 p.186 L219。")],
    },
    {
        "candidate_id": "cand-6875", "group": "sg3-place-cand-6875",
        "ku_id": "units/places/st-anne-la-royale-paris",
        "card_path": "04-knowledge/units/places/st-anne-la-royale-paris.md",
        "type": "place", "title": "圣安娜—皇家教堂（Church of St Anne-la-Royale）",
        "name_en": "Church of St Anne-la-Royale",
        "location": "第7章；印刷页186；Markdown L219–220；PDF物理页24。",
        "summary": "Haskell称Mazarin遗嘱留给Theatines一笔用于重建该教堂的款项，并指示将其心脏葬于教堂；随后记Guarini开始工程及工程中断、完成情况。",
        "quotes": [("L219; print p.186; PDF physical p.24", "the church of St Anne-la-Royale"), ("L219; print p.186; PDF physical p.24", "directed that his heart be buried in it")],
        "description_zh": "本卡登记Haskell称作St Anne-la-Royale的教堂建筑地点。第7章记载Mazarin遗嘱中的重建款项用途及心脏安葬指示，并称Guarini开始教堂工程；后续中断和约五十年后完成的施事者没有指明。遗嘱指示不等于本段独立证明心脏实际安葬。",
        "description_en": "This card records the church building named by Haskell as St Anne-la-Royale. Chapter 7 describes a rebuilding purpose for money left in Mazarin’s will, a direction concerning the burial of his heart, and Guarini’s beginning of work on the church. The agents responsible for the later interruption and completion are not named. The direction in the will is not independent proof here that the heart was actually buried there.",
        "fields": [
            ("地点性质", "教堂建筑。", "S1；第7章 p.186 L219。"),
            ("遗嘱所载用途", "Haskell称Mazarin留给Theatines一大笔款项，用于重建该教堂；金额未载。", "S1；第7章 p.186 L219。"),
            ("遗嘱中的安葬指示", "Haskell称Mazarin指示将其心脏葬于教堂；本段未独立证明实际安葬。", "S1；第7章 p.186 L219。"),
        ],
    },
    {
        "candidate_id": "cand-6869", "group": "workgrp-f1a5bdf2ca7057",
        "ku_id": "units/works/titian-venus-brienne-last-visit",
        "card_path": "04-knowledge/units/works/titian-venus-brienne-last-visit.md",
        "type": "work", "title": "提香的维纳斯画作（Titian’s Venus）", "name_en": "Titian’s Venus",
        "location": "第7章；印刷页186；Markdown L218；PDF物理页24。",
        "summary": "Brienne引述Mazarin在告别时提到一幅称作Titian之Venus的画作；作品版本和确切题名未明。",
        "quotes": [("L218; print p.186; PDF physical p.24", "cette Vénus du Titien")],
        "description_zh": "本卡登记Brienne回忆中Mazarin告别时提到的“Titian的Venus”。引述将作品归于Titian，但没有指出版本、确切题名或收藏编号；不与前页所述Venus del Pardo合并。",
        "description_en": "This card records the “Venus of Titian” mentioned in Brienne’s account of Mazarin’s farewell. The quoted wording attributes the painting to Titian but gives no version, exact title, or collection number. It is not merged with the Venus del Pardo mentioned on the preceding page.",
        "fields": [
            ("作品类型", "画作；引文称其为一幅Venus。", "S1；第7章 p.186 L218。"),
            ("来源题名与归属", "Brienne引述Mazarin称“Vénus du Titien”；版本及确切题名未明。", "S1；第7章 p.186 L218。"),
        ],
    },
    {
        "candidate_id": "cand-6877", "group": "workgrp-92dafc93fed2cf",
        "ku_id": "units/works/st-anne-la-royale-architectural-plan",
        "card_path": "04-knowledge/units/works/st-anne-la-royale-architectural-plan.md",
        "type": "work", "title": "圣安娜—皇家教堂建筑方案（Architectural Plan for St Anne-la-Royale）",
        "name_en": "Architectural Plan for St Anne-la-Royale",
        "location": "第7章；印刷页186；Markdown L219–220；PDF物理页24。",
        "summary": "Haskell称该教堂方案不迁就当时法国实践，并称其为Grand Siècle时期巴黎孤立的意大利巴洛克建筑实例。",
        "quotes": [("L219–220; print p.186; PDF physical p.24", "the plan made no concession whatsoever to current French practice and remained as a wholly isolated-example of Italian Baroque architecture in the Paris of the Grand Siècle")],
        "description_zh": "本卡登记Haskell所述St Anne-la-Royale建筑方案，与教堂建筑本身及其弯曲立面分开。Haskell称方案没有迁就当时法国实践，并把它描述为Grand Siècle时期巴黎孤立的意大利巴洛克建筑实例；这是作者的历史评价，不外推为普遍共识。",
        "description_en": "This card records the architectural plan for St Anne-la-Royale as described by Haskell, separate from the church building and its curving façade. Haskell says the plan made no concession to current French practice and describes it as a wholly isolated example of Italian Baroque architecture in Paris during the Grand Siècle. This is the author’s historical assessment, not a general consensus claim.",
        "fields": [
            ("作品类型", "建筑方案；与教堂建筑及立面构件分开登记。", "S1；第7章 p.186 L219–220。"),
            ("关联工程", "St Anne-la-Royale教堂工程。", "S1；第7章 p.186 L219。"),
            ("Haskell对法国实践的比较", "作者称该方案完全没有迁就当时法国建筑实践。", "S1；第7章 p.186 L219–220。"),
            ("Haskell对风格位置的判断", "作者称其为Grand Siècle时期巴黎孤立的意大利巴洛克建筑实例。", "S1；第7章 p.186 L220。"),
        ],
    },
    {
        "candidate_id": "cand-6878", "group": "workgrp-5866e1a4ddc411",
        "ku_id": "units/works/st-anne-la-royale-curving-facade",
        "card_path": "04-knowledge/units/works/st-anne-la-royale-curving-facade.md",
        "type": "work", "title": "圣安娜—皇家教堂的弯曲立面（Curving Façade of St Anne-la-Royale）",
        "name_en": "Curving Façade of St Anne-la-Royale",
        "location": "第7章；印刷页186；Markdown L219；PDF物理页24。",
        "summary": "Haskell描述教堂立面为弯曲形态，并称其取法于Borromini的S. Carlo alle Quattro Fontane。",
        "quotes": [("L219; print p.186; PDF physical p.24", "With its curving façade, derived from Borromini’s S. Carlo aile Quattro Fontane")],
        "description_zh": "本卡仅指St Anne-la-Royale的弯曲立面这一建筑构件，不与整座教堂或方案合并。Haskell称该立面取法于Borromini的S. Carlo alle Quattro Fontane；现有关系域值域约束不能把作品直接连到place类型建筑，因此关系保留为待证，不用错误类型替代。",
        "description_en": "This card represents only the curving façade of St Anne-la-Royale, distinct from the church building and its plan. Haskell says it derives from Borromini’s S. Carlo alle Quattro Fontane. The current relation domain and range do not permit a work-to-place edge for that building, so the relation remains pending rather than being represented with an inaccurate type.",
        "fields": [
            ("作品构件", "St Anne-la-Royale教堂的弯曲立面。", "S1；第7章 p.186 L219。"),
            ("来源所述形式与取法", "Haskell称立面呈弯曲形态，并取法于S. Carlo alle Quattro Fontane。", "S1；第7章 p.186 L219。"),
        ],
    },
    {
        "candidate_id": "cand-6880", "group": "sg3-term-cand-6880",
        "ku_id": "units/terms/current-french-architectural-practice-haskell-comparison",
        "card_path": "04-knowledge/units/terms/current-french-architectural-practice-haskell-comparison.md",
        "type": "term", "title": "当时法国建筑实践（Current French Architectural Practice）",
        "name_en": "Current French Architectural Practice",
        "location": "第7章；印刷页186；Markdown L219–220；PDF物理页24。",
        "summary": "Haskell以当时法国建筑实践作为与St Anne方案比较的参照；该段未定义其完整内容或代表者。",
        "quotes": [("L219–220; print p.186; PDF physical p.24", "the plan made no concession whatsoever to current French practice")],
        "description_zh": "本卡记录Haskell在比较St Anne方案时使用的“当时法国建筑实践”这一语境性概念。原文只说明方案没有迁就该实践，没有定义其全部内容，也没有将判断推广到所有法国建筑师或建筑。",
        "description_en": "This card records the contextual concept of “current French practice” used by Haskell in comparing the St Anne plan. The passage says only that the plan made no concession to that practice; it does not define the practice in full or generalize the judgment to all French architects or buildings.",
        "fields": [("来源实例", "作为St Anne建筑方案的比较参照；本段没有给出完整定义。", "S1；第7章 p.186 L219–220。")],
    },
    {
        "candidate_id": "cand-6881", "group": "sg3-term-cand-6881",
        "ku_id": "units/terms/italian-baroque-architecture-paris-haskell",
        "card_path": "04-knowledge/units/terms/italian-baroque-architecture-paris-haskell.md",
        "type": "term", "title": "巴黎的意大利巴洛克建筑（Italian Baroque Architecture in Paris）",
        "name_en": "Italian Baroque Architecture in Paris",
        "location": "第7章；印刷页186；Markdown L220；PDF物理页24。",
        "summary": "Haskell把St Anne方案称作Grand Siècle时期巴黎孤立的意大利巴洛克建筑实例；此处只记录该句的概念用法。",
        "quotes": [("L220; print p.186; PDF physical p.24", "a wholly isolated-example of Italian Baroque architecture in the Paris of the Grand Siècle")],
        "description_zh": "本卡记录Haskell在第7章对St Anne方案使用的“巴黎的意大利巴洛克建筑”范畴。作者称该方案在Grand Siècle时期的巴黎是孤立实例；本卡不把这句话扩展为一般风格定义，也不把印本连字符isolated-example误判为OCR错误。",
        "description_en": "This card records Haskell’s use of the category “Italian Baroque architecture in Paris” for the St Anne plan in Chapter 7. He calls it an isolated example in Paris during the Grand Siècle. The card does not expand this sentence into a general style definition, and preserves the printed hyphen in “isolated-example” rather than treating it as an OCR error.",
        "fields": [("来源实例", "Haskell称St Anne方案为Grand Siècle时期巴黎孤立的意大利巴洛克建筑实例。", "S1；第7章 p.186 L220。")],
    },
    {
        "candidate_id": "cand-6886", "group": "sg3-event-cand-6886",
        "ku_id": "units/events/louis-xiv-takes-power-haskell-reference",
        "card_path": "04-knowledge/units/events/louis-xiv-takes-power-haskell-reference.md",
        "type": "event", "title": "路易十四掌权（Louis XIV Takes Power）", "name_en": "Louis XIV Takes Power",
        "location": "第7章；印刷页186；Markdown L221–222；PDF物理页24。",
        "summary": "Haskell在Fouquet被捕的叙述中称Louis XIV接掌权力；该段没有给出年份或更具体的制度描述。",
        "quotes": [("L221–222; print p.186; PDF physical p.24", "who was arrested as soon as Louis XIV took over power")],
        "description_zh": "本卡仅记录Haskell在叙述Fouquet被捕时提到的Louis XIV掌权事件。来源以“Fouquet在Louis XIV接掌权力时随即被捕”建立时间语境；本段没有给出具体年份、法律程序或权力转移的制度细节。",
        "description_en": "This card records only the event of Louis XIV taking power as referenced in Haskell’s account of Fouquet’s arrest. The source places Fouquet’s arrest as occurring as soon as Louis XIV took over power; this passage gives no year, legal process, or institutional detail about the transfer.",
        "fields": [("事件性质", "Louis XIV接掌权力；此处作为Fouquet被捕的时间语境。", "S1；第7章 p.186 L221–222。")],
    },
]


NEW_STATEMENTS = [
    {
        "statement_id": "st-chp7-p186-i21", "segment_id": "chp-7:07_CHP-7_sec_i:l215-222",
        "subject_candidate_id": "cand-6864", "object_candidate_id": "cand-6866",
        "predicate": "brienne_reports_tapestry_formerly_belonged_to_marshal_of_saint_andre",
        "qualifiers": {
            "source_line_start": 216, "source_line_end": 216, "printed_page": 186, "pdf_physical_page": 24,
            "claim": "Brienne称这件Scipio挂毯曾属Saint-André元帅。",
            "speaker": "Brienne as quoted by Haskell", "text_layer": "quoted memoir",
            "qualification": "元帅的完整身份未由此处确定；保留为Brienne的前任持有人记载。",
            "mentioned_candidate_ids": ["cand-6864", "cand-6866", "cand-0452"],
            "relation_candidate": True,
            "relation_candidate_note": "Source-reported former ownership; the named marshal remains identity-unresolved.",
            "open_endpoint_reason": "cand-6866 identifies only a marshal title and surname; no stable person KU is currently mapped.",
            "ocr_corrections": [{"source_line": 216, "source_form": "SaintAndré", "print_form": "Saint-André"}],
        },
        "original_quote": "qui avoit été au maréchal de SaintAndré", "origin": "book", "source_file": SOURCE_FILE,
    },
    {
        "statement_id": "st-chp7-p186-i22", "segment_id": "chp-7:07_CHP-7_sec_i:l215-222",
        "subject_candidate_id": "cand-6864", "object_candidate_id": None,
        "predicate": "brienne_describes_tapestry_as_cardinals_finest",
        "qualifiers": {
            "source_line_start": 216, "source_line_end": 216, "printed_page": 186, "pdf_physical_page": 24,
            "claim": "Brienne称这件挂毯是Cardinal最美的挂毯。",
            "speaker": "Brienne as quoted by Haskell", "text_layer": "quoted memoir",
            "qualification": "保留为来源中的审美评价，不转写为经核验的排名。",
            "mentioned_candidate_ids": ["cand-6864", "cand-1588", "cand-0452"],
            "relation_candidate": False,
        },
        "original_quote": "la plus belle tapisserie du Cardinal", "origin": "book", "source_file": SOURCE_FILE,
    },
    {
        "statement_id": "st-chp7-p186-i23", "segment_id": "chp-7:07_CHP-7_sec_i:l215-222",
        "subject_candidate_id": "cand-6869", "object_candidate_id": "cand-2630",
        "predicate": "brienne_quotes_mazarin_identifying_venus_as_titian",
        "qualifiers": {
            "source_line_start": 218, "source_line_end": 218, "printed_page": 186, "pdf_physical_page": 24,
            "claim": "Brienne引述Mazarin在告别时提到一幅Titian的Venus。",
            "speaker": "Mazarin as quoted by Brienne", "text_layer": "quoted speech",
            "qualification": "引文归属于Titian；具体版本和确切题名未明，不与p.185的Venus del Pardo合并。",
            "mentioned_candidate_ids": ["cand-1588", "cand-6869", "cand-2630", "cand-0452"],
            "relation_candidate": True,
            "relation_candidate_note": "The quoted wording expressly identifies the painting as Titian's Venus; preserve the unidentified version in the relation scope.",
        },
        "original_quote": "cette Vénus du Titien", "origin": "book", "source_file": SOURCE_FILE,
    },
    {
        "statement_id": "st-chp7-p186-i24", "segment_id": "chp-7:07_CHP-7_sec_i:l215-222",
        "subject_candidate_id": "cand-6871", "object_candidate_id": "cand-6870",
        "predicate": "brienne_quotes_mazarin_identifying_deluge_as_antoine_carrache",
        "qualifiers": {
            "source_line_start": 218, "source_line_end": 218, "printed_page": 186, "pdf_physical_page": 24,
            "claim": "Brienne引述Mazarin提到Antoine Carrache的Deluge，并称其无与伦比。",
            "speaker": "Mazarin as quoted by Brienne", "text_layer": "quoted speech",
            "qualification": "保留原文Carrache拼写；人物身份与画作版本均未解决。",
            "mentioned_candidate_ids": ["cand-1588", "cand-6871", "cand-6870", "cand-0452"],
            "relation_candidate": True,
            "relation_candidate_note": "The source reports an attribution to Antoine Carrache, but neither the artist candidate nor painting version is resolved.",
            "open_endpoint_reason": "The candidate artist's identity and the cited painting version remain unresolved in S3.",
        },
        "original_quote": "cet incomparable Déluge d’Antoine Carrache", "origin": "book", "source_file": SOURCE_FILE,
    },
    {
        "statement_id": "st-chp7-p186-i25", "segment_id": "chp-7:07_CHP-7_sec_i:l215-222",
        "subject_candidate_id": "cand-2564", "object_candidate_id": "cand-6872",
        "predicate": "one_theatine_branch_settled_on_the_banks_of_the_seine",
        "qualifiers": {
            "source_line_start": 219, "source_line_end": 219, "printed_page": 186, "pdf_physical_page": 24,
            "claim": "Haskell称此前赴巴黎的一支Theatine修会分支后来定居在塞纳河岸。",
            "speaker": "Haskell", "text_layer": "authorial narrative",
            "qualification": "关系限定为一支分支，不表示整个Theatine修会位于河岸；原文未给具体修院或地址。",
            "mentioned_candidate_ids": ["cand-2564", "cand-6872"],
            "relation_candidate": True,
            "relation_candidate_note": "The source explicitly locates one branch on the banks of the Seine; retain branch scope.",
            "open_endpoint_reason": "The source identifies an unnamed branch, while cand-2564 maps the Theatine order as a whole; no distinct branch endpoint is established.",
        },
        "original_quote": "which settled on the banks of the Seine", "origin": "book", "source_file": SOURCE_FILE,
    },
    {
        "statement_id": "st-chp7-p186-i26", "segment_id": "chp-7:07_CHP-7_sec_i:l215-222",
        "subject_candidate_id": "cand-6875", "object_candidate_id": None,
        "predicate": "church_work_interrupted_in_1669",
        "qualifiers": {
            "source_line_start": 219, "source_line_end": 219, "printed_page": 186, "pdf_physical_page": 24,
            "claim": "Haskell称该教堂工程于1669年中断；原文未指明中断者。",
            "speaker": "Haskell", "text_layer": "authorial narrative",
            "qualification": "不推定中断者或具体施工活动。", "mentioned_candidate_ids": ["cand-6875"],
            "relation_candidate": False,
        },
        "original_quote": "work on the church which was interrupted in 1669", "origin": "book", "source_file": SOURCE_FILE,
    },
    {
        "statement_id": "st-chp7-p186-i27", "segment_id": "chp-7:07_CHP-7_sec_i:l215-222",
        "subject_candidate_id": "cand-6875", "object_candidate_id": None,
        "predicate": "church_completed_some_fifty_years_later",
        "qualifiers": {
            "source_line_start": 219, "source_line_end": 219, "printed_page": 186, "pdf_physical_page": 24,
            "claim": "Haskell称教堂工程约五十年后才完成；完成者未具名。",
            "speaker": "Haskell", "text_layer": "authorial narrative",
            "qualification": "保留原文some所表示的约数，不换算为确定年份。", "mentioned_candidate_ids": ["cand-6875"],
            "relation_candidate": False,
        },
        "original_quote": "only completed some fifty years later", "origin": "book", "source_file": SOURCE_FILE,
    },
    {
        "statement_id": "st-chp7-p186-i28", "segment_id": "chp-7:07_CHP-7_sec_i:l215-222",
        "subject_candidate_id": "cand-6876", "object_candidate_id": None,
        "predicate": "guarino_guarini_arrived_in_1662",
        "qualifiers": {
            "source_line_start": 219, "source_line_end": 219, "printed_page": 186, "pdf_physical_page": 24,
            "claim": "Haskell称Guarino Guarini于1662年抵达。",
            "speaker": "Haskell", "text_layer": "authorial narrative",
            "qualification": "此条只记录抵达时间；受召请关系和工程语境另行记录。", "mentioned_candidate_ids": ["cand-6876"],
            "relation_candidate": False,
        },
        "original_quote": "who arrived in 1662", "origin": "book", "source_file": SOURCE_FILE,
    },
]


S2_UPDATES = {
    "st-chp7-p186-i01": {
        "predicate": "brienne_places_scipio_tapestry_in_mazarins_small_gallery",
        "object_candidate_id": "cand-6863",
        "original_quote": "petite galerie que étoit tapissée de Scipion tout de laine",
        "claim": "Brienne称Scipio题材羊毛挂毯悬于Mazarin住所的小画廊。",
        "qualification": "保留Brienne回忆及Haskell转述层；挂毯具体版本未定。前任持有人与设计归属另行拆分记录。",
        "mentioned_candidate_ids": ["cand-6864", "cand-6863", "cand-1588", "cand-0452"],
        "relation_candidate": True,
        "relation_candidate_note": "Brienne's account locates the tapestry in the small gallery; this is distinct from previous ownership and design attribution.",
        "open_endpoint_reason": "The tapestry's physical version remains unidentified.",
    },
    "st-chp7-p186-i02": {
        "claim": "Brienne将挂毯设计归于Jules Romain（索引候选Giulio Romano）。",
        "qualification": "这是来源中的设计归属，不等于独立作者或具体版本核验；不以created_by替代设计归属。",
    },
    "st-chp7-p186-i04": {
        "object_candidate_id": "cand-6868",
        "predicate": "brienne_quotes_mazarin_naming_cortege_painting",
        "original_quote": "ce beau tableau du Cortège",
        "claim": "Brienne称Mazarin在最后一次看画时提到一幅名为Cortège的画作。",
        "qualification": "Cortège的具体作品身份和版本未明；此处只保留来源中的具名作品，不与另外两幅画合并。",
        "mentioned_candidate_ids": ["cand-1588", "cand-6868", "cand-0452"],
        "relation_candidate_note": "This is a temporary speech act in Brienne's quoted account; S6 does not treat it as a continuing work relationship.",
        "open_endpoint_reason": "The painting called Cortège has no resolved version or identity mapping.",
    },
    "st-chp7-p186-i06": {
        "object_candidate_id": "cand-2564",
        "predicate": "mazarin_summoned_a_branch_of_theatines_to_paris_in_1644",
        "original_quote": "In 1644 he had summoned to Paris a branch of the Theatine order",
        "claim": "Haskell称Mazarin于1644年召请Theatine修会的一支分支赴巴黎。",
        "qualification": "按原文保留a branch；不推断为整个修会，也不据此确定某一修院或法律实体。",
        "mentioned_candidate_ids": ["cand-1588", "cand-2564", "cand-4653"],
        "relation_candidate_note": "The source reports a summons involving one branch; no controlled predicate exactly represents this action.",
        "open_endpoint_reason": "The branch is not separately identified from the Theatine order in the source.",
    },
    "st-chp7-p186-i07": {
        "subject_candidate_id": "cand-1588", "object_candidate_id": "cand-2564",
        "predicate": "mazarin_left_theatines_a_sum_for_st_anne_rebuilding",
        "claim": "Haskell称Mazarin在遗嘱中给Theatines留下一大笔款项，用于重建St Anne-la-Royale教堂。",
        "qualification": "行动主体按原文为Mazarin，受领者为Theatines；重建教堂是款项用途而非已发生的重建结果。金额未给出。",
        "mentioned_candidate_ids": ["cand-1588", "cand-2564", "cand-6873", "cand-6875"],
        "relation_candidate_note": "The bequest and its purpose are explicit, but no controlled predicate exactly represents the transfer of a sum in a will.",
        "open_endpoint_reason": None,
    },
    "st-chp7-p186-i09": {
        "predicate": "theatines_summoned_member_guarini_for_st_anne_project",
        "original_quote": "For this purpose the Theatines summoned a member of their own order, Guarino Guarini",
        "claim": "Haskell称Theatines为此召来本会成员Guarino Guarini，目的为St Anne-la-Royale教堂工程。",
        "qualification": "member of their own order指Guarini与Theatines的成员关系；此句记录召请和工程目的，不等于建造委托已被独立验证。抵达年份另行记录。",
        "mentioned_candidate_ids": ["cand-2564", "cand-6876", "cand-6875"],
        "relation_candidate_note": "The summons is source-explicit, but the controlled vocabulary has no exact summons predicate for this relation.",
    },
    "st-chp7-p186-i10": {
        "predicate": "guarini_began_work_on_st_anne_church",
        "original_quote": "There he began work on the church",
        "claim": "Haskell称Guarini开始了该教堂工程。",
        "qualification": "there承接St Anne-la-Royale；中断和完成情况已拆为独立statement，施事者仍未具名。",
        "mentioned_candidate_ids": ["cand-6876", "cand-6875"],
        "relation_candidate_note": "The source says Guarini began work but does not state a commission or entrustment; no controlled predicate exactly represents this action.",
    },
    "st-chp7-p186-i11": {
        "predicate": "st_anne_curving_facade_derived_from_borrominis_s_carlo",
        "qualification": "Haskell将立面取法归于Borromini的S. Carlo alle Quattro Fontane；本句是来源判断，不是独立作者或设计核验。印本页图将S0中的aile校读为alle。",
        "ocr_corrections": [{"source_line": 219, "source_form": "aile", "print_form": "alle"}],
    },
    "st-chp7-p186-i13": {
        "qualification": "这是Haskell对该方案与当时法国建筑实践的比较；不推广为全体法国建筑师的立场。",
        "relation_candidate_note": "The comparison is explicit, but the controlled vocabulary has no precise predicate for making no concession to a practice.",
    },
    "st-chp7-p186-i14": {
        "claim": "Haskell称该方案仍是Grand Siècle时期巴黎孤立的意大利巴洛克建筑实例。",
        "qualification": "保留remained所示的持续状态及Haskell的作者判断。印本页图确认isolated-example带连字符；该连字符不是OCR错误。",
        "ocr_corrections": [],
    },
    "st-chp7-p186-i15": {
        "object_candidate_id": None,
        "mentioned_candidate_ids": ["cand-6877", "cand-6875"],
        "relation_candidate_note": "The plan's possible deterrent effect is Haskell's qualified interpretation; no specific later experiment is identified.",
        "open_endpoint_reason": "The future experiments are unnamed and do not correspond to cand-6883, which denotes the reported reaction.",
    },
    "st-chp7-p186-i16": {
        "object_candidate_id": None,
        "relation_candidate": False,
        "relation_candidate_note": "This is Haskell's source-bound interpretive statement about a reaction, without an identified agent or relational object.",
        "open_endpoint_reason": None,
    },
    "st-chp7-p186-n1-cite-wittkower": {
        "claim": "Haskell的注1引用Wittkower（1958）第269页。",
        "qualification": "与第21章书目中的Art and Architecture in Italy 1600 to 1750相匹配；被引第269页未独立查阅。",
        "relation_candidate_note": "This is an explicit bibliographic citation; it records the citation only and does not claim that the cited page was read.",
    },
    "st-chp7-p186-q01": {
        "subject_candidate_id": None, "object_candidate_id": None,
        "predicate": "brienne_quote_continues_from_p185_and_closes_on_p186",
        "relation_candidate": False,
        "relation_candidate_note": "Textual continuation and closure remain recorded in continuation metadata; they do not form a Brienne-to-Mazarin relationship.",
        "open_endpoint_reason": None,
    },
}


FORMAL_RELATIONS = [
    {"statement_id": "st-chp7-p186-i01", "subject_candidate_id": "cand-6864", "predicate": "located_at", "object_candidate_id": "cand-6863", "time": "", "role": "Brienne-reported gallery location", "scope": "Brienne's account places the wool Scipio tapestry in the small gallery; the physical version is unidentified.", "source_span": "Chapter 7, p.186, L216", "note": "位置关系来自Brienne被Haskell转引的回忆；不表示当前存放地点。"},
    {"statement_id": "st-chp7-p186-i23", "subject_candidate_id": "cand-6869", "predicate": "created_by", "object_candidate_id": "cand-2630", "time": "", "role": "source-reported attribution", "scope": "Brienne's quoted wording calls it a Venus of Titian; the physical version and exact title are not identified, and no independent attribution check is claimed.", "source_span": "Chapter 7, p.186, L218", "note": "关系只表达原书的Titian归属，不与p.185 Venus del Pardo合并。"},
    {"statement_id": "st-chp7-p186-i19", "subject_candidate_id": "cand-1062", "predicate": "employed_by", "object_candidate_id": "cand-1588", "time": "", "role": "employment", "scope": "Haskell says Fouquet had been employed by Mazarin; the employment period is not specified.", "source_span": "Chapter 7, p.186, L221–222", "note": "past-tense雇佣事实按来源限定记录，不补年份。"},
    {"statement_id": "st-chp7-p186-i20", "subject_candidate_id": "cand-0800", "predicate": "employed_by", "object_candidate_id": "cand-1588", "time": "", "role": "employment", "scope": "Haskell says Colbert had been employed by Mazarin; the employment period is not specified.", "source_span": "Chapter 7, p.186, L221–222", "note": "past-tense雇佣事实按来源限定记录，不补年份。"},
    {"statement_id": "st-chp7-p186-n1-cite-wittkower", "subject_candidate_id": "cand-2962", "predicate": "cites", "object_candidate_id": "cand-4557", "time": "", "role": "footnote 1 citation", "scope": "Chapter 7, p.186, footnote 1 cites Wittkower (1958), p.269; the cited page was not independently consulted.", "source_span": "Chapter 7, p.186, footnote 1, L361", "note": "只确认Haskell的书目引用，不确认被引页内容。"},
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    old = path.read_bytes() if path.exists() else b""
    encoding = "utf-8-sig" if old.startswith(b"\xef\xbb\xbf") else "utf-8"
    newline = "\r\n" if b"\r\n" in old else "\n"
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding=encoding, newline="") as handle:
        handle.write(text.replace("\n", newline))
    temp.replace(path)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    old = path.read_bytes()
    encoding = "utf-8-sig" if old.startswith(b"\xef\xbb\xbf") else "utf-8"
    newline = "\r\n" if b"\r\n" in old else "\n"
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding=encoding, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator=newline)
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def make_card(item: dict) -> str:
    frontmatter = {
        "title": item["title"], "name_en": item["name_en"], "type": item["type"],
        "evidence_status": "source_backed",
        "sources": [{
            "citation": BOOK_CITATION, "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": span, "text": quote} for span, quote in item["quotes"]],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": SOURCE_FILE, "source_span": item["location"]},
        }],
        "created": DATE, "updated": DATE, "process_ref": PROCESS_REF,
    }
    yaml_text = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=100)
    rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in item["fields"])
    body = (
        "\n## 内容\n\n### 描述\n\n"
        f"**中文：** {item['description_zh']}\n\n"
        f"**English:** {item['description_en']}\n\n"
        f"### {'事件信息' if item['type'] == 'event' else '来源所载字段'}\n\n"
        "| 字段 | 内容 | 依据 |\n|---|---|---|\n"
        f"{rows}\n\n"
        "## 关系与证据\n\n### 关系记录\n\n"
        "本卡正式关系以 `relations.csv` 为准；待证与否决项及逐条理由见对应 S6 过程记录。"
        "本书来源事实不表示已独立核验被引内容或未说明的作品版本。\n"
    )
    return f"---\n{yaml_text}---\n{body}"


def new_statement(statement_id: str, line_start: int, line_end: int, subject: str | None,
                  obj: str | None, predicate: str, claim: str, quote: str,
                  speaker: str, layer: str, qualification: str,
                  mentioned: list[str], is_relation: bool,
                  relation_note: str = "", open_reason: str | None = None,
                  ocr: list[dict] | None = None) -> dict:
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 186, "pdf_physical_page": 24,
        "claim": claim, "speaker": speaker, "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": is_relation,
    }
    if relation_note:
        qualifiers["relation_candidate_note"] = relation_note
    if open_reason:
        qualifiers["open_endpoint_reason"] = open_reason
    if ocr:
        qualifiers["ocr_corrections"] = ocr
    return {
        "statement_id": statement_id,
        "segment_id": "chp-7:07_CHP-7_sec_i:l215-222",
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


def apply_statement_patch() -> tuple[str, int, int]:
    raw = STATEMENTS.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    existing = {}
    parsed = []
    for line in lines:
        if not line.strip():
            parsed.append((line, None))
            continue
        item = json.loads(line)
        existing[item["statement_id"]] = item
        parsed.append((line, item))
    required = set(S2_UPDATES)
    missing = required - set(existing)
    if missing:
        raise ValueError(f"Missing expected S2 rows: {sorted(missing)}")
    duplicate_new = {item["statement_id"] for item in NEW_STATEMENTS} & set(existing)
    if duplicate_new:
        raise ValueError(f"New statement IDs already exist: {sorted(duplicate_new)}")

    updated_lines = []
    updated_count = 0
    for old_line, item in parsed:
        if item is None:
            updated_lines.append(old_line)
            continue
        patch = S2_UPDATES.get(item["statement_id"])
        if patch is None:
            updated_lines.append(old_line)
            continue
        qpatch = {k: v for k, v in patch.items() if k not in {"subject_candidate_id", "object_candidate_id", "predicate", "original_quote", "ocr_corrections"}}
        for key in ("subject_candidate_id", "object_candidate_id", "predicate", "original_quote"):
            if key in patch:
                item[key] = patch[key]
        q = item["qualifiers"]
        q.update(qpatch)
        if "ocr_corrections" in patch:
            if patch["ocr_corrections"]:
                q["ocr_corrections"] = patch["ocr_corrections"]
            else:
                q.pop("ocr_corrections", None)
        if patch.get("open_endpoint_reason") is None:
            q.pop("open_endpoint_reason", None)
        updated_lines.append(json.dumps(item, ensure_ascii=False))
        updated_count += 1

    anchor = "st-chp7-p186-i20"
    insert_at = next((i + 1 for i, (_, item) in enumerate(parsed) if item and item["statement_id"] == anchor), None)
    if insert_at is None:
        raise ValueError(f"Cannot locate insertion anchor {anchor}")
    new_lines = [json.dumps(item, ensure_ascii=False) for item in NEW_STATEMENTS]
    updated_lines[insert_at:insert_at] = new_lines
    output = newline.join(updated_lines) + (newline if text.endswith(("\n", "\r")) else "")
    if bom:
        output = "\ufeff" + output
    return output, updated_count, len(NEW_STATEMENTS)


def main(apply: bool) -> None:
    align_fields, align_rows = read_csv(ALIGNMENT)
    manifest_fields, manifest_rows = read_csv(MANIFEST)
    rel_fields, rel_rows = read_csv(RELATIONS)
    candidate_alignment = {r["candidate_id"]: r for r in align_rows}
    current_manifest = {r["ku_id"] for r in manifest_rows}
    for item in ITEMS:
        row = candidate_alignment.get(item["candidate_id"])
        if row is None or row["decision"] != "new":
            raise ValueError(f"Expected an existing S3 new decision for {item['candidate_id']}")
        if row["ku_id"] not in ("", item["ku_id"]):
            raise ValueError(f"Unexpected existing mapping for {item['candidate_id']}: {row['ku_id']}")
        if item["ku_id"] in current_manifest and row["ku_id"] != item["ku_id"]:
            raise ValueError(f"KU already exists without candidate mapping: {item['ku_id']}")
        path = ROOT / item["card_path"]
        if path.exists():
            raise ValueError(f"Card path already exists: {item['card_path']}")

    statement_output, updated_statements, added_statements = apply_statement_patch()
    patched_statements = {
        item["statement_id"]: item
        for item in (json.loads(line) for line in statement_output.lstrip("\ufeff").splitlines() if line.strip())
    }
    for relation in FORMAL_RELATIONS:
        statement = patched_statements.get(relation["statement_id"])
        if statement is None:
            raise ValueError(f"Formal relation has no S2 statement: {relation['statement_id']}")
        qualifiers = statement.get("qualifiers", {})
        if qualifiers.get("relation_candidate") is not True:
            raise ValueError(f"Formal relation points to a non-relation S2 statement: {relation['statement_id']}")
        if (statement.get("subject_candidate_id"), statement.get("object_candidate_id")) != (
            relation["subject_candidate_id"], relation["object_candidate_id"]
        ):
            raise ValueError(f"Formal relation endpoints differ from S2: {relation['statement_id']}")

    source_lines = (ROOT / SOURCE_FILE).read_text(encoding="utf-8").splitlines()
    footnote_segment = "\n".join(source_lines[292:389])
    cite_surface = "Wittkower"
    publication_surface = "1958, p. 269"
    author_start = footnote_segment.find(cite_surface, footnote_segment.find("1 Wittkower, 1958, p. 269."))
    publication_start = footnote_segment.find(publication_surface, footnote_segment.find("1 Wittkower, 1958, p. 269."))
    if author_start < 0 or publication_start < 0:
        raise ValueError("Could not locate exact p.186 footnote mention spans")
    mention_fields, mention_rows = read_csv(MENTIONS)
    new_mentions = [
        {"mention_id": "m-chp7-p186-n1-wittkower-author", "segment_id": "chp-7:07_CHP-7_sec_i:l293-389", "candidate_id": "cand-2818", "surface_form": cite_surface, "start_char": str(author_start), "end_char": str(author_start + len(cite_surface)), "note": "Author named in Haskell's printed footnote."},
        {"mention_id": "m-chp7-p186-n1-wittkower-publication", "segment_id": "chp-7:07_CHP-7_sec_i:l293-389", "candidate_id": "cand-4557", "surface_form": publication_surface, "start_char": str(publication_start), "end_char": str(publication_start + len(publication_surface)), "note": "Year and locator identify the cited publication in this footnote; its title is not printed here."},
    ]
    mention_ids = {r["mention_id"] for r in mention_rows}
    if any(r["mention_id"] in mention_ids for r in new_mentions):
        raise ValueError("Footnote mention IDs already exist")

    for candidate_id, mention_id in (
        ("cand-2818", "m-chp7-p186-n1-wittkower-author"),
        ("cand-4557", "m-chp7-p186-n1-wittkower-publication"),
    ):
        alignment = candidate_alignment[candidate_id]
        alignment["resolution_note"] = (
            alignment["resolution_note"].rstrip()
            + f" Footnote evidence from this batch is anchored by {mention_id} in the p.186 footnote; the cited page itself was not independently consulted."
        )

    manifest_additions = []
    for item in ITEMS:
        alignment = candidate_alignment[item["candidate_id"]]
        if alignment["ku_id"] == "":
            alignment["ku_id"] = item["ku_id"]
            alignment["process_ref"] = PROCESS_REF
            alignment["resolution_note"] = (alignment["resolution_note"].rstrip() +
                f" S4 registered from the existing S3 new group {item['group']} using the source-local evidence recorded in this batch; no external identity claim is added.")
        manifest_additions.append({
            "ku_id": item["ku_id"], "type": item["type"],
            "canonical_name": item["title"].split("（", 1)[0],
            "name_en": item["name_en"], "source_task": TASK, "card_path": item["card_path"],
        })

    all_align = {r["candidate_id"]: r for r in align_rows}
    for rel in FORMAL_RELATIONS:
        rel["subject_ku_id"] = all_align[rel["subject_candidate_id"]]["ku_id"]
        rel["object_ku_id"] = all_align[rel["object_candidate_id"]]["ku_id"]
        if not rel["subject_ku_id"] or not rel["object_ku_id"]:
            raise ValueError(f"Formal relation endpoint is not mapped: {rel['statement_id']}")
    rel_existing_keys = {(r["subject_ku_id"], r["predicate"], r["object_ku_id"], r["time"], r["role"], r["scope"]) for r in rel_rows}
    for rel in FORMAL_RELATIONS:
        key = (rel["subject_ku_id"], rel["predicate"], rel["object_ku_id"], rel["time"], rel["role"], rel["scope"])
        if key in rel_existing_keys:
            raise ValueError(f"Duplicate natural-key relation for {rel['statement_id']}")
    max_relation_id = max((int(r["relation_id"].split("-")[1]) for r in rel_rows if re.fullmatch(r"rel-\d+", r["relation_id"])), default=0)
    relation_additions = []
    for i, rel in enumerate(FORMAL_RELATIONS, start=1):
        relation_additions.append({
            "relation_id": f"rel-{max_relation_id + i}",
            "subject_ku_id": rel["subject_ku_id"], "object_ku_id": rel["object_ku_id"],
            "predicate": rel["predicate"], "time": rel["time"], "role": rel["role"],
            "scope": rel["scope"], "origin": "book", "status": "formal",
            "source_id": SOURCE_ID, "source_span": rel["source_span"],
            "source_file": SOURCE_FILE, "note": rel["note"],
        })

    accepted_doc = yaml.safe_load(ACCEPTED.read_text(encoding="utf-8-sig")) or {}
    accepted_units = list(accepted_doc.get("units", []))
    for item in ITEMS:
        if item["card_path"] in accepted_units:
            raise ValueError(f"Accepted path already exists: {item['card_path']}")
        accepted_units.append(item["card_path"])
    accepted_doc["units"] = sorted(accepted_units)
    accepted_output = yaml.safe_dump(accepted_doc, allow_unicode=True, sort_keys=False, width=120)

    cards = {item["card_path"]: make_card(item) for item in ITEMS}
    print(f"S2 rows to update: {updated_statements}; new atomic statements: {added_statements}")
    print("New S2 IDs: " + ", ".join(item["statement_id"] for item in NEW_STATEMENTS))
    print("New mention spans: " + ", ".join(f"{r['mention_id']}[{r['start_char']}:{r['end_char']}]" for r in new_mentions))
    print("S4 new groups to register: " + ", ".join(f"{x['candidate_id']}->{x['ku_id']}" for x in ITEMS))
    print(f"S5 source-backed card rows expected: {sum(len(x['fields']) for x in ITEMS)}")
    print("S6 formal relation rows: " + ", ".join(f"{x['statement_id']}={x['predicate']}" for x in FORMAL_RELATIONS))
    print("Other S6 decisions will be recorded as pending/rejected in knowledge.md; no unsupported relation row is created.")
    if not apply:
        print("DRY RUN ONLY; no files written. Pass --apply after reviewing this batch.")
        return

    write_text(STATEMENTS, statement_output)
    write_csv(MENTIONS, mention_fields, mention_rows + new_mentions)
    write_csv(ALIGNMENT, align_fields, align_rows)
    write_csv(MANIFEST, manifest_fields, manifest_rows + manifest_additions)
    write_csv(RELATIONS, rel_fields, rel_rows + relation_additions)
    write_text(ACCEPTED, accepted_output)
    for relative, content in cards.items():
        write_text(ROOT / relative, content)
    print("Applied S2 repairs, S4 mappings/cards, footnote mentions, and supported S6 formal rows.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reviewable Ch.7 p.186 S2/S4/S5/S6 batch")
    parser.add_argument("--apply", action="store_true", help="write the reviewed table/card batch")
    args = parser.parse_args()
    main(args.apply)
