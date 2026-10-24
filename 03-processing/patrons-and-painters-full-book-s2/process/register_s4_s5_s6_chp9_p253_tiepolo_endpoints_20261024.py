from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TABLES = ROOT / "04-knowledge" / "tables"
TASK = "s4-s5-s6-chp9-p253-tiepolo-endpoints-20261024"
ANCHOR = TASK
PROCESS_REF = f"03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR}"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_FILE = "02-sources/02-Markdown/09_CHP-9_intro.md"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)
DATE = "2026-10-24"
TICK = chr(96)


def source(location: str, span: str, summary: str, quotes: list[str]) -> dict:
    return {
        "citation": BOOK,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote} for quote in quotes],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": SOURCE_FILE,
            "source_span": span,
        },
    }


P253_BODY_125 = (
    "to paint frescoes in the Cathedral and his new Archiepiscopal Palace. "
    "After rather a melodramatic start on the ceiling of the staircase, the artist gradually changed his style "
    "when he came to paint scenes from the life of Abraham in the gallery"
)
P253_TRIBUNAL = "and The Justice of\nSolomon in the hall of the tribunal"
P253_NOTE1 = (
    "In 1759 Tiepolo and his son Gian Domenico were recalled to Udine by a new patriarch, "
    "Daniele Dolfin, nephew of Dionisio, to decorate the Cappella della Purità near the Cathedral."
)
P253_NOTE4 = "In 1775 provincial nobles turned down the chance to acquire Venetian patrician status"
P253_NOTE2_ITALIAN = (
    "Ho udito dite dal Signor Tiepolo stesso, che molti giovani, anche fra suoi allievi"
)
P253_PATRONS_EN = (
    "He himself deliberately aimed at a special class of patron. He used to say that "
    "‘painters must try and succeed in large-scale works capable of pleasing the rich and the nobility"
)


def card_spec(
    cid: str,
    group: str,
    ku: str,
    kind: str,
    zh: str,
    en: str,
    description_zh: str,
    description_en: str,
    identity_zh: str,
    identity_en: str,
    location: str,
    span: str,
    summary: str,
    quotes: list[str],
    section: str,
    fields: list[tuple[str, str, str]],
    statements: list[str],
    subtype: str = "",
    extra_sources: list[dict] | None = None,
) -> dict:
    sources = [source(location, span, summary, quotes)]
    if extra_sources:
        sources.extend(extra_sources)
    return {
        "cid": cid,
        "group": group,
        "ku": ku,
        "type": kind,
        "zh": zh,
        "en": en,
        "title": f"{zh}（{en}）",
        "sub_type": subtype,
        "description_zh": description_zh,
        "description_en": description_en,
        "identity_zh": identity_zh,
        "identity_en": identity_en,
        "sources": sources,
        "section": section,
        "fields": fields,
        "statements": statements,
        "card_path": f"04-knowledge/units/{kind}s/{ku.rsplit('/', 1)[1]}.md",
    }


ITEMS = [
    card_spec(
        "cand-8278", "sg3-place-cand-8278",
        "units/places/staircase-in-archiepiscopal-palace-udine", "place",
        "乌迪内总主教宫中的楼梯空间",
        "Staircase in the new Archiepiscopal Palace at Udine",
        "本卡登记哈斯克尔所述、蒂埃波罗在乌迪内新总主教宫楼梯天花板上开始壁画工作的内部空间。原书只称楼梯天花板，不说明该楼梯的建筑细节、确切空间范围或现存状态。",
        "This card records the interior space where Haskell says Tiepolo made a melodramatic start on the ceiling of the staircase in the new Archiepiscopal Palace at Udine. The account gives no architectural detail, exact spatial boundary, or present condition for the staircase.",
        "本组只对应来源所述宫殿楼梯空间；不把未具名的楼梯壁画与 Abraham 场景或《所罗门的审判》合并。",
        "This group represents only the staircase space described in the source; the untitled staircase fresco is kept separate from the Abraham scenes and The Justice of Solomon.",
        "第9章，印刷页253，来源转录 L125。",
        "line 125; print p. 253",
        "Haskell先提到新总主教宫中的壁画工作，继而称蒂埃波罗在楼梯天花板上开始创作。",
        [P253_BODY_125],
        "来源所述空间",
        [("空间位置", "新总主教宫的楼梯天花板；来源未提供更具体的建筑描述或现存状态。", "S1")],
        ["st-chp9-p253-udine-fresco-sites-and-works", "st-chp9-p253-staircase-fresco-location"],
        "interior architectural space; source-local location",
    ),
    card_spec(
        "cand-8279", "sg3-place-cand-8279",
        "units/places/gallery-in-archiepiscopal-palace-udine", "place",
        "乌迪内总主教宫的画廊",
        "Gallery in the new Archiepiscopal Palace at Udine",
        "本卡登记哈斯克尔所述乌迪内新总主教宫中的画廊。书中把蒂埃波罗绘制的 Abraham 场景置于该画廊；场景的单件身份、数量与完整边界仍未确定。",
        "This card records the gallery in the new Archiepiscopal Palace at Udine as described by Haskell. He places Tiepolo’s Abraham scenes there; the individual works, their number, and the group’s complete boundary remain unidentified.",
        "本组是来源局部的室内空间，不代表已识别某一现存画廊或特定建筑遗存。",
        "This is a source-local interior-space group, not an identification of a surviving gallery or a specific architectural fabric.",
        "第9章，印刷页253，来源转录 L125。",
        "line 125; print p. 253",
        "Haskell把 Abraham 场景的绘制位置说成新总主教宫的画廊。",
        [P253_BODY_125],
        "来源所述空间",
        [("空间位置", "新总主教宫的画廊；Haskell称 Abraham 场景在此绘制，但作品组身份仍待证。", "S1")],
        ["st-chp9-p253-abraham-scenes-location"],
        "interior architectural space; source-local location",
    ),
    card_spec(
        "cand-8280", "sg3-place-cand-8280",
        "units/places/tribunal-hall-archiepiscopal-palace-udine", "place",
        "乌迪内总主教宫审判厅",
        "Tribunal hall in the new Archiepiscopal Palace at Udine",
        "本卡登记哈斯克尔所述新总主教宫的审判厅。哈斯克尔将《所罗门的审判》置于此处；这记录的是原书所述位置，不说明该空间或作品的现存状态。",
        "This card records the tribunal hall in the new Archiepiscopal Palace as described by Haskell. He places The Justice of Solomon there; this is the location stated in the book and does not establish the present condition of either space or work.",
        "本组只对应来源所称的审判厅；不与新总主教宫整体或其他宫殿空间合并。",
        "This group represents only the tribunal hall named by the source; it remains distinct from the palace as a whole and from its other interior spaces.",
        "第9章，印刷页253，来源转录 L125–126。",
        "lines 125–126; print p. 253",
        "Haskell将《所罗门的审判》放在总主教宫的 tribunal hall。",
        [P253_BODY_125, P253_TRIBUNAL],
        "来源所述空间",
        [("空间位置", "新总主教宫的审判厅；Haskell将《所罗门的审判》置于此处。", "S1")],
        ["st-chp9-p253-justice-solomon-location"],
        "interior architectural space; source-local location",
    ),
    card_spec(
        "cand-8283", "workgrp-d5a413438b3817",
        "units/works/the-justice-of-solomon-tiepolo-udine", "work",
        "所罗门的审判",
        "The Justice of Solomon",
        "本卡登记哈斯克尔第9章 p.253 所述蒂埃波罗作品《所罗门的审判》。索引子目另作“Judgment of Solomon”，按当前 S3 跨来源身份组归为同一作品候选组。原书描述其位于乌迪内总主教宫审判厅；未据此确认现存版本或外部目录身份。",
        "This card records The Justice of Solomon, a Tiepolo work described in Haskell’s Chapter 9, p.253. The index subentry reads “Judgment of Solomon”; the current S3 cross-source group treats these as the same work candidate. Haskell places it in the tribunal hall of the Archiepiscopal Palace at Udine; no surviving version or external catalogue identity is asserted.",
        "S3 身份组 workgrp-d5a413438b3817 同时映射正文候选 cand-8283 与索引候选 cand-2595。题名及索引异文按来源并列；不推定作品现存、尺寸、媒介材料或当前收藏。",
        "S3 identity group workgrp-d5a413438b3817 maps both body candidate cand-8283 and index candidate cand-2595. The title and index variant are preserved as source forms; survival, dimensions, material medium, and present collection are not inferred.",
        "第9章，印刷页253，来源转录 L125–126。",
        "lines 125–126; print p. 253",
        "Haskell在蒂埃波罗的宫殿壁画叙述中列出《所罗门的审判》，并将其置于审判厅。",
        [P253_BODY_125, P253_TRIBUNAL],
        "题名与书内描述",
        [
            ("来源题名", "The Justice of Solomon（按正文照录）；索引子目作 Judgment of Solomon。", "S1"),
            ("作品语境", "哈斯克尔在总主教宫壁画叙述中讨论该作；不据此补写具体材质、尺寸或现存版本。", "S1"),
        ],
        ["st-chp9-p253-justice-solomon-work", "st-chp9-p253-justice-solomon-location"],
        "work; source-local title",
    ),
    card_spec(
        "cand-8285", "sg3-place-cand-8285",
        "units/places/cappella-della-purita-udine", "place",
        "乌迪内 Purità 礼拜堂",
        "Cappella della Purità near Udine Cathedral",
        "本卡登记哈斯克尔注1所称、靠近乌迪内主教座堂的 Cappella della Purità。注释称 1759 年 Daniele Dolfin 召回蒂埃波罗及其子 Gian Domenico 前往乌迪内装饰该堂；召回和装饰目的不证明装饰实际完成。",
        "This card records the Cappella della Purità near Udine Cathedral as named in Haskell’s note 1. The note says that in 1759 Daniele Dolfin recalled Tiepolo and his son Gian Domenico to Udine to decorate the chapel; the recall and stated purpose do not establish that the decoration was completed.",
        "地点身份限于哈斯克尔注释所指礼拜堂；不推定其现存建筑身份、历史沿革或装饰现状。",
        "The place identity is limited to the chapel named in Haskell’s note; no surviving architectural identity, building history, or present decoration is inferred.",
        "第9章，印刷页253，注1，来源转录 L360。",
        "line 360; print p. 253 n. 1",
        "Haskell注1称该礼拜堂位于主教座堂附近，并记述 1759 年召回两位画家以装饰该堂。",
        [P253_NOTE1],
        "来源所述地点",
        [
            ("来源所列名称", "Cappella della Purità。", "S1"),
            ("位置与装饰语境", "注释称其在主教座堂附近；1759 年召回画家以装饰该堂，但未说明是否完成。", "S1"),
        ],
        [
            "st-chp9-p253-note1-later-recall-and-chapel",
            "st-chp9-p253-note1-recalled-gian-domenico-1759",
            "st-chp9-p253-note1-tiepolo-recalled-to-decorate-chapel",
            "st-chp9-p253-note1-gian-domenico-recalled-to-decorate-chapel",
        ],
        "chapel; named place in Haskell’s note",
    ),
    card_spec(
        "cand-8293", "sg3-term-cand-8293",
        "units/terms/provincial-nobles-declined-patrician-status-1775", "term",
        "据称于1775年拒绝威尼斯贵族身份的外省贵族",
        "Provincial nobles said to have declined Venetian patrician status in 1775",
        "本卡记录哈斯克尔注4所述 1775 年拒绝获取威尼斯 patrician 身份机会的外省贵族集合称谓。注释未列出个人姓名、人数或集合边界；这里保留为来源局部群体术语，不构成人物名录。",
        "This card records the source-local collective term for provincial nobles whom Haskell’s note 4 says declined the opportunity to acquire Venetian patrician status in 1775. The note supplies no individual names, count, or membership boundary; this is not a roster of persons.",
        "该术语仅限注释所称的外省贵族集合，不与已具威尼斯贵族身份的家族或个人合并。",
        "This term is limited to the provincial-noble group named in the note and is not merged with families or persons already holding Venetian patrician status.",
        "第9章，印刷页253，注4，来源转录 L363。",
        "line 363; print p. 253 n. 4",
        "Haskell称外省贵族在 1775 年拒绝取得威尼斯 patrician 身份的机会。",
        [P253_NOTE4],
        "来源中的群体用法",
        [("来源群体描述", "Haskell注4所称 1775 年拒绝获取威尼斯贵族身份机会的外省贵族；个人与人数未说明。", "S1")],
        ["st-chp9-p253-note4-provincial-nobles-berengo"],
        "collective social category; source-local term",
    ),
    card_spec(
        "cand-8294", "sg3-term-cand-8294",
        "units/terms/venetian-patrician-status", "term",
        "威尼斯贵族身份",
        "Venetian patrician status",
        "本卡记录哈斯克尔注4提到的威尼斯 patrician 身份，作为外省贵族可能取得的一种身份地位。来源说相关群体在 1775 年拒绝这一机会；本卡不据此补写授予程序、法律规则或群体成员。",
        "This card records Venetian patrician status as a standing that provincial nobles could acquire, as mentioned in Haskell’s note 4. The source says that the group declined the opportunity in 1775; this card adds no admission procedure, legal rule, or membership list.",
        "本组是身份地位术语，不等同于威尼斯共和国、贵族家族或取得该身份的个人。",
        "This group is a status term, distinct from the Venetian Republic, patrician families, and individuals who acquired the status.",
        "第9章，印刷页253，注4，来源转录 L363。",
        "line 363; print p. 253 n. 4",
        "Haskell将 Venetian patrician status 描述为外省贵族在 1775 年曾有机会取得的身份。",
        [P253_NOTE4],
        "来源中的地位术语",
        [("来源所述地位", "外省贵族被称可取得的 Venetian patrician 身份；Haskell称他们于 1775 年拒绝该机会。", "S1")],
        ["st-chp9-p253-note4-provincial-nobles-berengo"],
        "social status; source-local term",
    ),
    card_spec(
        "cand-8297", "sg3-term-cand-8297",
        "units/terms/young-artists-in-tiepolo-reported-advice", "term",
        "蒂埃波罗报道中受劝诫的青年画家",
        "Young artists addressed in Tiepolo’s reported advice",
        "本卡记录哈斯克尔注2转引的意大利报纸报道中所称青年画家。报道称其中一些是蒂埃波罗的学生，但没有列出姓名或人数；言论经报纸及哈斯克尔转述，未在此独立核验。",
        "This card records the young artists mentioned in the Italian newspaper report reproduced in Haskell’s note 2. The report says some were Tiepolo’s pupils but gives no names or count; the statement is mediated through the newspaper and Haskell and is not independently verified here.",
        "本组为来源局部的青年画家集合称谓，不转写为具名人物或固定学生名册。",
        "This group is a source-local collective term for young artists, not a set of named persons or a fixed pupil roster.",
        "第9章，印刷页253，注2，来源转录 L361。",
        "line 361; print p. 253 n. 2",
        "意大利语引文报告许多青年人仍应继续学习，其中包括蒂埃波罗的一些学生。",
        [P253_NOTE2_ITALIAN],
        "转述中的群体用法",
        [("报告对象", "意大利报纸转引的蒂埃波罗言论涉及许多青年画家，其中一些被称为其学生；姓名和人数未载。", "S1")],
        ["st-chp9-p253-note2-italian-advice-to-young-artists"],
        "collective audience; source-local term",
    ),
    card_spec(
        "cand-8299", "sg3-term-cand-8299",
        "units/terms/wealthy-and-noble-patrons-in-tiepolo-advice", "term",
        "蒂埃波罗报道中富有且高贵的赞助人",
        "Wealthy and noble patrons in Tiepolo’s reported advice",
        "本卡记录哈斯克尔正文及注2所呈现的富有者与贵族作为画家大型作品的预期受众。正文将话语归于蒂埃波罗，注2说明其来自 1762 年意大利报纸报道；这不证明所有此类人士实际委托了作品。",
        "This card records the wealthy and noble audience for large-scale works in Haskell’s body text and note 2. The body attributes the advice to Tiepolo, while note 2 locates it in a 1762 Italian newspaper report; this does not establish that all such people commissioned works.",
        "本组是来源话语中的社会受众类别，不与威尼斯贵族术语、具名赞助人或实际委托者合并。",
        "This group is a social audience category in the reported statement, distinct from the Venetian aristocracy term, named patrons, and actual commissioners.",
        "第9章，印刷页253，正文 L130 及注2 L361。",
        "lines 130, 361; print p. 253",
        "正文与注2把大型作品的理想受众描述为富有者和贵族；注释标明意大利报纸转引背景。",
        [P253_PATRONS_EN, P253_NOTE2_ITALIAN],
        "转述中的社会受众",
        [("来源受众描述", "大型作品应取悦富有者与贵族的说法；据哈斯克尔正文及注2所记报纸引语。", "S1")],
        ["st-chp9-p253-tiepolo-aimed-at-rich-noble-patrons", "st-chp9-p253-note2-italian-advice-to-young-artists"],
        "collective social audience; source-local term",
    ),
]

CARD_BY_CANDIDATE = {item["cid"]: item for item in ITEMS}
CARD_BY_CANDIDATE["cand-2595"] = CARD_BY_CANDIDATE["cand-8283"]
MAPPED_CANDIDATES = [
    "cand-8278", "cand-8279", "cand-8280", "cand-8283", "cand-2595",
    "cand-8285", "cand-8293", "cand-8294", "cand-8297", "cand-8299",
]

PENDING_DECISIONS = [
    ("st-chp9-p253-aristocracy-work-and-fragmentation", "人物→term 的“为贵族工作”没有精确受控谓词；patronized_by 的值域不接受该 term，不能改写为委托或赞助。"),
    ("st-chp9-p253-barbaro-dolfin-roman-epics", "罗马史诗组候选 cand-8241 的作品身份与范围仍为 S3 undecided；待作品边界解决后再判断。"),
    ("st-chp9-p253-commission-to-palace-and-cathedral", "summoned 没有精确受控关系类型；句子同时涉及主教座堂和 S3 未决的宫殿对象，不改写成 commissioned_by。"),
    ("st-chp9-p253-dionisio-saw-tiepolo-masterpieces", "候选 cand-12377 的作品组身份与成员范围仍为 S3 undecided，且“看见”没有精确受控谓词。"),
    ("st-chp9-p253-note4-provincial-nobles-berengo", "群体拒绝取得身份地位的语义有据，但当前受控词表无准确的拒绝取得关系；不把未具名贵族拆成个人。"),
    ("st-chp9-p253-two-dolfin-members-imprisoned-or-exiled", "两名家族成员均未具名；“入狱或流亡”没有当前适用的受控关系类型，不能伪装为受机构任职或成员关系。"),
    ("st-chp9-p253-udine-fresco-sites-and-works", "楼梯壁画候选 cand-8281 缺少 mention-level 锚定且身份仍为 S3 undecided；不补造单件作品。"),
    ("st-chp9-p253-staircase-fresco-location", "地点已登记，但作品端点 cand-8281 仍为 S3 undecided；端点未解析前不建立正式位置边。"),
    ("st-chp9-p253-abraham-scenes-work", "Abraham 场景为未枚举的作品集合，cand-8282 的身份粒度与边界仍为 S3 undecided。"),
    ("st-chp9-p253-abraham-scenes-location", "gallery 地点已登记，但作品集合 cand-8282 的身份边界仍未确定；位置边保持待证。"),
    ("st-chp9-p253-tiepolo-summoned-outside-venice", "原文未给召集者或目的地；不从相邻 Udine 叙述推断缺失端点。"),
    ("st-chp9-p253-roman-epics-commemorate-daniele-dolfin", "史诗作品组 cand-8241 尚未定界，且原文的 Daniele Dolfin 与 Daniele III 的身份对应仍待证。"),
    ("st-chp9-p253-tiepolo-aimed-at-rich-noble-patrons", "受众为 term 集合，人物到社会类别没有精确的受控谓词；intended_for 仅接受 work→institution/place。"),
    ("st-chp9-p253-note2-italian-advice-to-young-artists", "advised 的值域为 person；此处接收对象是未具名青年画家 term 集合，且引语经意大利报纸转述。"),
    ("st-chp9-p253-note1-later-recall-and-chapel", "原复合断言拆分后，保留丹尼埃莱召回吉安巴蒂斯塔·蒂埃波罗的独立主张；summoned/recalled 无精确受控谓词。"),
    ("st-chp9-p253-note1-recalled-gian-domenico-1759", "丹尼埃莱召回吉安·多梅尼科的独立主张有注释支持，但 recalled 没有精确受控谓词。"),
    ("st-chp9-p253-note1-tiepolo-recalled-to-decorate-chapel", "注释只报告以装饰礼拜堂为目的的召回，不证明装饰实际完成；人物→地点也无精确适用谓词。"),
    ("st-chp9-p253-note1-gian-domenico-recalled-to-decorate-chapel", "注释只报告以装饰礼拜堂为目的的召回，不证明装饰实际完成；人物→地点也无精确适用谓词。"),
]

FORMAL_RELATIONS = [
    {
        "statement_id": "st-chp9-p253-justice-solomon-work",
        "subject_ku_id": "units/persons/giambattista-tiepolo",
        "object_ku_id": "units/works/the-justice-of-solomon-tiepolo-udine",
        "predicate": "creator_of",
        "time": "",
        "role": "Haskell 所述创作者",
        "scope": "来源将 The Justice of Solomon 置于 Tiepolo 在乌迪内新总主教宫绘制的作品中；仅记录该书的创作者归属，不断言现存版本或外部目录身份。",
        "span": "Chapter 9, printed p.253, lines 125–126; S2 statement st-chp9-p253-justice-solomon-work",
        "note": "Formal S6 decision: the book’s continuation identifies Tiepolo as the artist who painted The Justice of Solomon; no external attribution is added.",
    },
    {
        "statement_id": "st-chp9-p253-justice-solomon-location",
        "subject_ku_id": "units/works/the-justice-of-solomon-tiepolo-udine",
        "object_ku_id": "units/places/tribunal-hall-archiepiscopal-palace-udine",
        "predicate": "located_at",
        "time": "",
        "role": "来源所述室内位置",
        "scope": "仅记录 Haskell 在印刷页253所述该作品位于总主教宫审判厅；不表示现今位置、存世状态或已完成馆方身份核验。",
        "span": "Chapter 9, printed p.253, lines 125–126; S2 statement st-chp9-p253-justice-solomon-location",
        "note": "Formal S6 decision: the source explicitly places The Justice of Solomon in the hall of the tribunal.",
    },
]

NEW_S2_IDS = [
    "st-chp9-p253-note1-recalled-gian-domenico-1759",
    "st-chp9-p253-note1-tiepolo-recalled-to-decorate-chapel",
    "st-chp9-p253-note1-gian-domenico-recalled-to-decorate-chapel",
]
NOTE1_ID = "st-chp9-p253-note1-later-recall-and-chapel"
ALL_PAGE_RELATION_IDS = [
    "st-chp9-p253-aristocracy-work-and-fragmentation",
    "st-chp9-p253-barbaro-dolfin-roman-epics",
    "st-chp9-p253-commission-to-palace-and-cathedral",
    "st-chp9-p253-dionisio-saw-tiepolo-masterpieces",
    NOTE1_ID,
    "st-chp9-p253-note4-provincial-nobles-berengo",
    "st-chp9-p253-two-dolfin-members-imprisoned-or-exiled",
    "st-chp9-p253-udine-fresco-sites-and-works",
    "st-chp9-p253-staircase-fresco-location",
    "st-chp9-p253-abraham-scenes-work",
    "st-chp9-p253-abraham-scenes-location",
    "st-chp9-p253-justice-solomon-work",
    "st-chp9-p253-justice-solomon-location",
    "st-chp9-p253-tiepolo-summoned-outside-venice",
    "st-chp9-p253-roman-epics-commemorate-daniele-dolfin",
    "st-chp9-p253-tiepolo-aimed-at-rich-noble-patrons",
    "st-chp9-p253-note2-italian-advice-to-young-artists",
]


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str], bytes]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or []), raw


def csv_bytes(path: Path, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    out = io.StringIO(newline="")
    with path.open("rb") as handle:
        has_bom = handle.read(3) == b"\xef\xbb\xbf"
    writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if has_bom else b"") + out.getvalue().encode("utf-8")


def jsonl_bytes(path: Path, rows: list[dict]) -> bytes:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    existing_lines = raw.decode("utf-8-sig").splitlines()
    desired = {row["statement_id"]: row for row in rows}
    seen: set[str] = set()
    output_lines = []
    for line in existing_lines:
        if not line.strip():
            continue
        original = json.loads(line)
        statement_id = original["statement_id"]
        updated = desired.get(statement_id)
        if updated is None:
            output_lines.append(line)
            continue
        seen.add(statement_id)
        if updated == original:
            output_lines.append(line)
        else:
            compact = '\":\"' in line
            separators = (",", ":") if compact else None
            output_lines.append(json.dumps(updated, ensure_ascii=False, separators=separators))
    for row in rows:
        if row["statement_id"] not in seen:
            output_lines.append(json.dumps(row, ensure_ascii=False))
    body = "\n".join(output_lines) + "\n"
    return (b"\xef\xbb\xbf" if has_bom else b"") + body.encode("utf-8")


def card_bytes(item: dict) -> bytes:
    frontmatter = {
        "title": item["title"],
        "name_en": item["en"],
        "type": item["type"],
        "evidence_status": "source_backed",
        "sources": item["sources"],
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    if item["sub_type"]:
        frontmatter["sub_type"] = item["sub_type"]
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    table_rows = "\n".join(
        f"| {field} | {value} | {evidence} |" for field, value, evidence in item["fields"]
    )
    statement_links = "、".join(f"{TICK}{sid}{TICK}" for sid in item["statements"])
    source_links = "；".join(
        f"[来源{i}](../../../{SOURCE_FILE}#L{re.search(r'line[s]? (\d+)', src['original_quotes'][0]['source_span']).group(1)})"
        for i, src in enumerate(item["sources"], 1)
    )
    body = (
        "## 内容\n\n### 描述\n\n"
        f"**中文：** {item['description_zh']} [{source_links}]\n\n"
        f"**English:** {item['description_en']}\n\n"
        "### 身份边界\n\n"
        f"{item['identity_zh']}\n\n{item['identity_en']}\n\n"
        f"### {item['section']}\n\n"
        "| 字段 | 值 | 证据 |\n|---|---|---|\n"
        f"{table_rows}\n\n"
        "## 关系与证据\n\n"
        "### 关系记录\n\n"
        f"正式关系由 relations.csv 定向渲染；本批其余裁决及理由见[过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR})。\n\n"
        "### S2 关系候选入口\n\n"
        f"{statement_links}\n"
    )
    return ("---\n" + fm + "---\n\n" + body).encode("utf-8-sig")


def make_note1_statement(base: dict, statement_id: str, subject: str, obj: str, claim: str, predicate: str, mentions: list[str]) -> dict:
    row = json.loads(json.dumps(base, ensure_ascii=False))
    row["statement_id"] = statement_id
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = obj
    row["predicate"] = predicate
    q = row["qualifiers"]
    q["claim"] = claim
    q["qualification"] = (
        "Haskell's 1759 note reports the recall for the purpose of decorating the named chapel; "
        "it does not state that the decoration was completed. The recalled person and the chapel "
        "are separated into person-specific S2 claims."
    )
    q["mentioned_candidate_ids"] = mentions
    q["semantic_review"] = (
        "2026-10-24 corrective atomization based on the existing 2026-10-14 page review; "
        "Haskell p.253 n.1 was re-read. This repair is not counted as a new independent-review item."
    )
    q["relation_candidate_note"] = (
        "S6 must assess the recall and intended decoration separately; do not infer completed work "
        "or substitute an inexact controlled predicate."
    )
    return row


def text_bytes(path: Path, value: str) -> bytes:
    with path.open("rb") as handle:
        has_bom = handle.read(3) == b"\xef\xbb\xbf"
    return (b"\xef\xbb\xbf" if has_bom else b"") + value.encode("utf-8")


def update_accepted(text: str) -> str:
    lines = text.splitlines()
    claim_pos = next((i for i, line in enumerate(lines) if line.strip() == "claims:"), None)
    if claim_pos is None:
        raise ValueError("accepted.yml units/claims boundary changed")
    additions = [f"- {item['card_path']}" for item in ITEMS]
    existing = set(lines[:claim_pos])
    if existing.intersection(additions):
        raise ValueError("one or more planned cards already appears in accepted.yml")
    for addition in sorted(additions, key=lambda x: x[2:]):
        claim_pos = next(i for i, line in enumerate(lines) if line.strip() == "claims:")
        insert_at = next(
            (
                i for i, line in enumerate(lines[:claim_pos])
                if line.startswith("- 04-knowledge/units/") and line[2:] > addition[2:]
            ),
            claim_pos,
        )
        lines.insert(insert_at, addition)
    return "\n".join(lines) + "\n"


def replace_once(text: str, before: str, after: str, label: str) -> str:
    if text.count(before) != 1:
        raise ValueError(f"expected exactly one snapshot field for {label}: {text.count(before)}")
    return text.replace(before, after, 1)


def build_outputs(dry_run: bool) -> tuple[dict[Path, bytes], dict[Path, bytes], dict]:
    paths = {
        "candidates": TABLES / "entity-candidates.csv",
        "alignment": TABLES / "alignment.csv",
        "manifest": TABLES / "ku-manifest.csv",
        "relations": TABLES / "relations.csv",
        "statements": TABLES / "book-statements.jsonl",
        "enrichment": TABLES / "enrichment.jsonl",
        "accepted": ROOT / "04-knowledge" / "accepted.yml",
        "process": ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md",
        "stages": ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "results" / "stages.md",
        "result": ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md",
        "agents": ROOT / "AGENTS.md",
        "sources": TABLES / "sources.csv",
    }
    if not all(path.is_file() for path in paths.values()):
        raise FileNotFoundError("required project table or result file is missing")
    candidates, _, _ = read_csv(paths["candidates"])
    alignment, alignment_fields, _ = read_csv(paths["alignment"])
    manifest, manifest_fields, _ = read_csv(paths["manifest"])
    relations, relation_fields, _ = read_csv(paths["relations"])
    with paths["statements"].open(encoding="utf-8-sig") as handle:
        statements = [json.loads(line) for line in handle if line.strip()]
    with paths["enrichment"].open(encoding="utf-8-sig") as handle:
        enrichment = [json.loads(line) for line in handle if line.strip()]
    sources, _, _ = read_csv(paths["sources"])
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    main_alignment: dict[str, dict] = {}
    for row in alignment:
        if row.get("candidate_id") and not row.get("external_source") and not row.get("external_id"):
            if row["candidate_id"] in main_alignment:
                raise ValueError(f"duplicate primary S3 rows for {row['candidate_id']}")
            main_alignment[row["candidate_id"]] = row
    manifest_ids = {row["ku_id"] for row in manifest}
    manifest_paths = {row["card_path"] for row in manifest}
    accepted_text = paths["accepted"].read_text(encoding="utf-8-sig")
    process_text = paths["process"].read_text(encoding="utf-8-sig")
    stages_text = paths["stages"].read_text(encoding="utf-8-sig")
    result_text = paths["result"].read_text(encoding="utf-8-sig")
    agents_text = paths["agents"].read_text(encoding="utf-8-sig")
    if ANCHOR in process_text or f"### {ANCHOR}" in result_text:
        raise ValueError("this batch already appears in current process or result")
    if not any(row.get("source_id") == SOURCE_ID for row in sources):
        raise ValueError(f"source registry lacks {SOURCE_ID}")
    if len(statements) != 15330:
        raise ValueError(f"unexpected S2 statement baseline: {len(statements)}")
    if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in statements) != 10544:
        raise ValueError("unexpected S6 relation-candidate baseline")

    for cid in MAPPED_CANDIDATES:
        if cid not in candidate_by_id or cid not in main_alignment:
            raise ValueError(f"missing candidate or primary S3 row: {cid}")
        item = CARD_BY_CANDIDATE[cid]
        candidate = candidate_by_id[cid]
        decision = main_alignment[cid]
        if candidate.get("suggested_type") != item["type"]:
            raise ValueError(f"candidate type changed for {cid}")
        if decision.get("decision") != "new" or decision.get("ku_id"):
            raise ValueError(f"{cid} is no longer an unmapped S3 new candidate")
        if f"group={item['group']}" not in decision.get("resolution_note", ""):
            raise ValueError(f"existing S3 identity group changed for {cid}")
        if item["ku"] in manifest_ids or item["card_path"] in manifest_paths:
            raise ValueError(f"planned KU already exists: {item['ku']}")
        if (ROOT / item["card_path"]).exists() or item["card_path"] in accepted_text:
            raise ValueError(f"planned card already exists: {item['card_path']}")
    if not (
        main_alignment["cand-2595"]["decision"] == "new"
        and main_alignment["cand-8283"]["decision"] == "new"
        and main_alignment["cand-2595"]["resolution_note"].count("workgrp-d5a413438b3817") == 1
        and main_alignment["cand-8283"]["resolution_note"].count("workgrp-d5a413438b3817") == 1
    ):
        raise ValueError("Justice of Solomon cross-source S3 group changed")
    for item in ITEMS:
        if any(
            row["type"] == item["type"] and row["name_en"].casefold() == item["en"].casefold()
            for row in manifest
        ):
            raise ValueError(f"possible same-type manifest collision for {item['en']}")

    statement_by_id = {row["statement_id"]: row for row in statements}
    if len(statement_by_id) != len(statements):
        raise ValueError("duplicate statement ids detected")
    if NOTE1_ID not in statement_by_id:
        raise ValueError("note 1 composite statement is missing")
    note1 = statement_by_id[NOTE1_ID]
    if (
        note1.get("subject_candidate_id") != "cand-0926"
        or note1.get("object_candidate_id") != "cand-8285"
        or note1.get("qualifiers", {}).get("relation_candidate") is not True
        or note1.get("qualifiers", {}).get("source_line_start") != 360
    ):
        raise ValueError("note 1 statement changed since semantic review")
    if set(NEW_S2_IDS) & set(statement_by_id):
        raise ValueError("one or more planned atomic S2 statement ids already exist")
    for sid in ALL_PAGE_RELATION_IDS:
        row = statement_by_id.get(sid)
        if not row or row.get("qualifiers", {}).get("relation_candidate") is not True:
            raise ValueError(f"expected p.253 relation candidate is missing or reclassified: {sid}")
    if any("st-chp9-p253-" in " ".join(row.values()) for row in relations):
        raise ValueError("p.253 already has a formal or pending row in relations.csv")
    if any(sid in process_text for sid, _ in PENDING_DECISIONS):
        # S3/S4 history can name a statement as a remaining candidate. Only a prior
        # S6 decision table is disallowed; detect such a table row specifically.
        for sid, _ in PENDING_DECISIONS:
            if re.search(rf"(?m)^\|\s*{re.escape(TICK + sid + TICK)}\s*\|", process_text):
                raise ValueError(f"an earlier S6 disposition already exists for {sid}")

    # Atomize the composite footnote claim into four person-specific source claims.
    original_quote = note1["original_quote"]
    mention_ids = ["cand-0926", "cand-2569", "cand-2624", "cand-2666", "cand-8285", "cand-8235", "cand-0929"]
    note1_tiepolo = make_note1_statement(
        note1, NOTE1_ID, "cand-0926", "cand-2569",
        "Haskell says that in 1759 the new patriarch Daniele Dolfin recalled Giambattista Tiepolo to Udine for the purpose of decorating the Cappella della Purità near the Cathedral.",
        "recalled_tiepolo_to_udine_to_decorate_chapel_in_1759",
        ["cand-0926", "cand-2569", "cand-2666", "cand-8285", "cand-8235"],
    )
    note1_son = make_note1_statement(
        note1, NEW_S2_IDS[0], "cand-0926", "cand-2624",
        "Haskell says that in 1759 the new patriarch Daniele Dolfin recalled Gian Domenico Tiepolo to Udine for the purpose of decorating the Cappella della Purità near the Cathedral.",
        "recalled_gian_domenico_to_udine_to_decorate_chapel_in_1759",
        ["cand-0926", "cand-2624", "cand-2666", "cand-8285", "cand-8235"],
    )
    note1_tiepolo_chapel = make_note1_statement(
        note1, NEW_S2_IDS[1], "cand-2569", "cand-8285",
        "Haskell's note identifies the Cappella della Purità as the intended object of the decoration for which Giambattista Tiepolo was recalled in 1759; completion is not stated.",
        "tiepolo_recalled_to_decorate_cappella_della_purita_in_1759",
        ["cand-2569", "cand-8285", "cand-2666"],
    )
    note1_son_chapel = make_note1_statement(
        note1, NEW_S2_IDS[2], "cand-2624", "cand-8285",
        "Haskell's note identifies the Cappella della Purità as the intended object of the decoration for which Gian Domenico Tiepolo was recalled in 1759; completion is not stated.",
        "gian_domenico_recalled_to_decorate_cappella_della_purita_in_1759",
        ["cand-2624", "cand-8285", "cand-2666"],
    )
    note1.update(note1_tiepolo)
    statement_by_id[NOTE1_ID] = note1
    statement_by_id[NEW_S2_IDS[0]] = note1_son
    statement_by_id[NEW_S2_IDS[1]] = note1_tiepolo_chapel
    statement_by_id[NEW_S2_IDS[2]] = note1_son_chapel
    statements = [statement_by_id[row["statement_id"]] for row in statements] + [
        note1_son, note1_tiepolo_chapel, note1_son_chapel
    ]
    # The original is replaced in place; only the three new atomized statements append.
    statements = [
        (note1 if row["statement_id"] == NOTE1_ID else row)
        for row in statements
    ]
    if len({row["statement_id"] for row in statements}) != len(statements):
        raise ValueError("statement atomization produced duplicate ids")
    if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in statements) != 10547:
        raise ValueError("unexpected post-atomization S6 denominator")

    planned_alignment = [dict(row) for row in alignment]
    for row in planned_alignment:
        if row.get("candidate_id") in MAPPED_CANDIDATES and not row.get("external_source") and not row.get("external_id"):
            row["ku_id"] = CARD_BY_CANDIDATE[row["candidate_id"]]["ku"]
            row["process_ref"] = PROCESS_REF
            row["resolution_note"] += (
                f" S4 registration: mapped the existing S3 group {CARD_BY_CANDIDATE[row['candidate_id']]['group']} "
                f"to {CARD_BY_CANDIDATE[row['candidate_id']]['ku']} using Haskell p.253; no external identity is asserted."
            )
    planned_manifest = list(manifest)
    for item in ITEMS:
        planned_manifest.append({
            "ku_id": item["ku"],
            "type": item["type"],
            "canonical_name": item["title"],
            "name_en": item["en"],
            "source_task": TASK,
            "card_path": item["card_path"],
        })

    accepted_after = update_accepted(accepted_text)
    cards = {ROOT / item["card_path"]: card_bytes(item) for item in ITEMS}
    from scripts import build_field_facts as field_facts
    original_base = field_facts.BASE
    try:
        with tempfile.TemporaryDirectory(prefix="pnp-chp9-p253-preview-") as temp_dir:
            temp_root = Path(temp_dir)
            for card_path, content in cards.items():
                dest = temp_root / card_path.relative_to(ROOT)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(content)
            selected_manifest = [row for row in planned_manifest if row["ku_id"] in {item["ku"] for item in ITEMS}]
            field_facts.BASE = temp_root
            fields, source_registry, warnings, cards_with_tables = field_facts.extract_records(selected_manifest)
    finally:
        field_facts.BASE = original_base
    if warnings or cards_with_tables != len(ITEMS) or not fields:
        raise ValueError(f"S5 field extraction failed: cards={cards_with_tables}, warnings={warnings}")
    field_facts.assign_ids(fields, paths["enrichment"])
    if any(row["source_ids"] != [SOURCE_ID] or row["evidence_status"] != "source_backed" for row in fields):
        raise ValueError("one or more planned S5 rows are not source-backed to Haskell")
    old_enrichment_ids = {row.get("enrichment_id") for row in enrichment}
    if old_enrichment_ids & {row["enrichment_id"] for row in fields}:
        raise ValueError("S5 extraction reused an existing enrichment id for a new row")
    if source_registry.keys() != {SOURCE_ID}:
        raise ValueError(f"unexpected S5 source set: {sorted(source_registry)}")

    next_relation = max(int(re.search(r"(\d+)$", row["relation_id"]).group(1)) for row in relations) + 1
    formal_rows = []
    existing_keys = {
        (row["subject_ku_id"], row["predicate"], row["object_ku_id"], row.get("time", ""), row.get("role", ""), row.get("scope", ""))
        for row in relations
    }
    for offset, spec in enumerate(FORMAL_RELATIONS):
        natural_key = (
            spec["subject_ku_id"], spec["predicate"], spec["object_ku_id"],
            spec["time"], spec["role"], spec["scope"],
        )
        if natural_key in existing_keys:
            raise ValueError(f"duplicate formal relation natural key for {spec['statement_id']}")
        formal_rows.append({
            "relation_id": f"rel-{next_relation + offset:04d}",
            "subject_ku_id": spec["subject_ku_id"],
            "object_ku_id": spec["object_ku_id"],
            "predicate": spec["predicate"],
            "time": spec["time"],
            "role": spec["role"],
            "scope": spec["scope"],
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": spec["span"],
            "source_file": SOURCE_FILE,
            "note": spec["note"],
        })
        existing_keys.add(natural_key)
    planned_relations = relations + formal_rows
    used_kus = {row["ku_id"] for row in planned_manifest}
    for row in planned_relations:
        if row["status"] == "formal" and (
            row["subject_ku_id"] not in used_kus or row["object_ku_id"] not in used_kus
        ):
            raise ValueError(f"formal relation has unresolved KU endpoint: {row['relation_id']}")

    pending_by_id = dict(PENDING_DECISIONS)
    if set(pending_by_id) != set(ALL_PAGE_RELATION_IDS) - {r["statement_id"] for r in FORMAL_RELATIONS} | set(NEW_S2_IDS):
        raise ValueError("S6 disposition set does not match the p.253 relation candidates")
    decision_rows = []
    for sid in ALL_PAGE_RELATION_IDS:
        if sid in pending_by_id:
            decision_rows.append((sid, "pending", pending_by_id[sid]))
        elif sid in {r["statement_id"] for r in FORMAL_RELATIONS}:
            predicate = next(r["predicate"] for r in FORMAL_RELATIONS if r["statement_id"] == sid)
            decision_rows.append((sid, "formal", f"正式边 {predicate}，见 {TICK}relations.csv{TICK} 新增关系。"))
    for sid in NEW_S2_IDS:
        decision_rows.append((sid, "pending", pending_by_id[sid]))
    if len(decision_rows) != 20 or sum(row[1] == "formal" for row in decision_rows) != 2:
        raise ValueError("expected 20 S6 decisions (2 formal, 18 pending)")

    s2_note = (
        "\n\n### S2 定向原子化修订：第9章 p.253 注1（2026-10-24）\n\n"
        "依据既有第9章逐页复核指出的复合关系问题，重读 Haskell 第9章印刷页253注1。原 statement "
        f"{TICK}{NOTE1_ID}{TICK} 现保留为丹尼埃莱·多尔芬召回吉安巴蒂斯塔·蒂埃波罗的个体化主张；"
        "另新增三条 statement，分别记录丹尼埃莱召回吉安·多梅尼科、两位画家各自被召回以装饰 "
        "Cappella della Purità 的目的。原注只说 recalled to decorate，不证明装饰完成；S0 OCR 不变，"
        "既有 mention 已足够，不新增 mention。本次净增3条 S2 statement，不计入独立复核分子。"
    )
    process_note = (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        f"### 第9章 p.253 跨章端点登记及 S6 逐项裁决（{DATE}）\n\n"
        "#### S3 身份组与 S4 登记\n\n"
        "本批沿用既有 S3 决定，不重开身份判断。登记9个 S3 new 身份组、10条候选映射；"
        "正文 cand-8283 与索引 cand-2595 沿用 workgrp-d5a413438b3817，共用一张《所罗门的审判》KU。"
        "三个宫殿内部空间、Purità 礼拜堂、该作品及四个来源局部术语各自保持边界；"
        "未登记楼梯壁画 cand-8281、Abraham 场景集合 cand-8282、宫殿 cand-8277 或 "
        "first-masterpieces 组 cand-12377，因其 S3 身份或边界仍待证。\n\n"
        "| S3 candidate | existing identity group | S4 KU | type |\n|---|---|---|---|\n"
        + "\n".join(
            f"| {TICK}{item['cid']}{TICK} | {TICK}{item['group']}{TICK} | {TICK}{item['ku']}{TICK} | {item['type']} |"
            for item in ITEMS
        )
        + f"\n| {TICK}cand-2595{TICK} | {TICK}workgrp-d5a413438b3817{TICK} | {TICK}units/works/the-justice-of-solomon-tiepolo-udine{TICK} | work; index mapping |\n\n"
        "#### S2 修订与 S5 字段\n\n"
        "注1复合关系按人物和礼拜堂端点原子化：丹尼埃莱→吉安巴蒂斯塔、丹尼埃莱→吉安·多梅尼科、"
        "吉安巴蒂斯塔→礼拜堂（以装饰为目的召回）、吉安·多梅尼科→礼拜堂（以装饰为目的召回）。"
        f"statement 净增3，mention 不变；此修订不增加统一独立 S2 复核分子。新增 {len(fields)} 条 "
        "Haskell 原书支持的 S5 字段，均为 source_backed，未添加外部身份或未读引文信息。\n\n"
        "#### S6 逐项裁决\n\n"
        "本页及 p.252–253 跨页连续语境内的20条 S2 关系候选均有当前去向：2 formal、18 pending。"
        f"Formal 边为 {TICK}rel-{next_relation:04d}{TICK} creator_of（Tiepolo→The Justice of Solomon）"
        f"与 {TICK}rel-{next_relation + 1:04d}{TICK} located_at（作品→审判厅）。"
        "pending 不进入正式关系投影；本页没有 rejected 项。逐项理由如下：\n\n"
        "| statement_id | status | decision / evidence boundary |\n|---|---|---|\n"
        + "\n".join(
            f"| {TICK}{sid}{TICK} | {status} | {detail} |"
            for sid, status, detail in decision_rows
        )
        + "\n\n不为没有精确谓词的召回、劝诫、社会受众、拒绝身份地位或惩罚行为扩充关系类型。"
        "未决作品端点和开放目的地均保留各自的 S3/S2 卡点，不用相邻语境推断。"
    )
    process_after = process_text.rstrip() + s2_note + process_note + "\n"

    stages_note = (
        "\n\n### 第9章 p.253 注1定向修订（2026-10-24）\n\n"
        "依据既有逐页复核意见，将原复合 recall/decorate statement 原子化为四条人物或地点关系主张；"
        "净增3条 statement、mention 不变，不计入独立复核分子。原文只报告召回画家以装饰礼拜堂，"
        "不据此断言装饰已完成。过程及 S6 去向见 "
        f"[第9章 p.253 批次](../../patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR})。"
    )
    stages_after = stages_text.rstrip() + stages_note + "\n"

    relation_string = (
        f"**第9章 p.253 Tiepolo 端点批次（{DATE}）：** 沿用9个既有 S3 new 身份组，登记9个 KU、"
        "10条 S4 映射；cand-8283 与索引 cand-2595 共用一张 work 卡。第9章注1一条复合 S2 statement "
        "原子化后净增3条，不增 mention，不计入独立复核分子。新增"
        f"{len(fields)}条 Haskell 来源 S5 字段。p.252–253 同一连续语境内20条 S6 候选逐项裁决为"
        f"2 formal、18 pending，新增 formal {TICK}rel-{next_relation:04d}–rel-{next_relation + 1:04d}{TICK}；"
        "未把未具名楼梯壁画、Abraham 场景组、first-masterpieces 组或未给目的地的召回推成确定对象。"
        f"详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR})。"
    )
    result_marker = "### 本轮进度与后续工作（2026-10-24）"
    if result_text.count(result_marker) != 1:
        raise ValueError("current result progress marker changed")
    result_after = result_text.replace(result_marker, result_marker + "\n\n" + relation_string, 1)

    s2_old = "S2共15,330条statement、26,779条mention，统一独立逐条复核9,617/15,330（62.73%"
    s2_new = "S2共15,333条statement、26,779条mention，统一独立逐条复核9,617/15,333（62.72%"
    agents_after = replace_once(agents_text, s2_old, s2_new, "AGENTS S2")
    agents_after = replace_once(
        agents_after,
        "S4已映射2,021/5,071条new候选，待映射3,050条，其中1,331条触及关系端点。",
        "S4已映射2,031/5,071条new候选，待映射3,040条，其中1,322条触及关系端点。",
        "AGENTS S4",
    )
    agents_after = replace_once(
        agents_after,
        "S5字段13,130条（1,634条unverified）。",
        f"S5字段{13130 + len(fields):,}条（1,634条unverified）。",
        "AGENTS S5",
    )
    agents_after = replace_once(
        agents_after,
        "S6已裁决1,160/10,544条（674 formal、379 pending、107 rejected），尚余9,384条；relations.csv共1,908条（1,890 formal、18 pending）。",
        "S6已裁决1,180/10,547条（676 formal、397 pending、107 rejected），尚余9,367条；relations.csv共1,910条（1,892 formal、18 pending）。",
        "AGENTS S6",
    )

    snapshot_before = (
        "S2现有15,330条statement、26,779条mention；独立逐条复核记录9,617条（按当前分母粗算62.73%）"
    )
    snapshot_after = (
        "S2现有15,333条statement、26,779条mention；独立逐条复核记录9,617条（按当前分母粗算62.72%）"
    )
    result_after = replace_once(result_after, snapshot_before, snapshot_after, "result S2")
    result_after = replace_once(result_after, "S4已映射2,021/5,071", "S4已映射2,031/5,071", "result S4 mapped")
    result_after = replace_once(result_after, "待登记3,050条，其中1,331条触及关系端点", "待登记3,040条，其中1,322条触及关系端点", "result S4 pending")
    result_after = replace_once(
        result_after,
        "S5字段13,130条，1,634条unverified",
        f"S5字段{13130 + len(fields):,}条，1,634条unverified",
        "result S5",
    )
    result_after = replace_once(result_after, "共有10,544条关系候选", "共有10,547条关系候选", "result S6 denominator")
    result_after = replace_once(
        result_after,
        "累计逐项裁决1,160条（674 formal、379 pending、107 rejected），尚有9,384条未裁决",
        "累计逐项裁决1,180条（676 formal、397 pending、107 rejected），尚有9,367条未裁决",
        "result S6 adjudication",
    )
    result_after = replace_once(
        result_after,
        "relations.csv有1,908条（1,890 formal、18 pending）",
        "relations.csv有1,910条（1,892 formal、18 pending）",
        "result relation table",
    )

    # Candidate-free new S3 groups add nine units; ten mappings include the index row.
    current_state = {
        "new_fields": len(fields),
        "new_formal_relations": len(formal_rows),
        "s2_statements": len(statements),
        "s2_relation_candidates": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in statements),
        "s4_new_mappings": len(MAPPED_CANDIDATES),
        "s4_new_groups": len(ITEMS),
        "s4_total_mapped": 2031,
        "s4_total_pending": 3040,
        "s4_relation_endpoints_pending": 1322,
        "s5_total_fields": 13130 + len(fields),
        "s6_page_decisions": len(decision_rows),
        "s6_page_formal": 2,
        "s6_page_pending": 18,
        "s6_total_decided": 1180,
        "s6_total_formal": 676,
        "s6_total_pending": 397,
        "s6_total_rejected": 107,
        "s6_total_undecided": 9367,
        "relation_table_total": len(planned_relations),
        "relation_table_formal": sum(row["status"] == "formal" for row in planned_relations),
        "relation_table_pending": sum(row["status"] == "pending" for row in planned_relations),
        "ku_total": len(planned_manifest),
        "new_relation_ids": [row["relation_id"] for row in formal_rows],
        "new_enrichment_ids": [row["enrichment_id"] for row in fields],
    }

    enr_raw = paths["enrichment"].read_bytes()
    enr_suffix = (b"" if enr_raw.endswith((b"\n", b"\r")) else b"\n")
    enr_after = enr_raw + enr_suffix + b"".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
        for row in fields
    )
    output = {
        paths["alignment"]: csv_bytes(paths["alignment"], alignment_fields, planned_alignment),
        paths["manifest"]: csv_bytes(paths["manifest"], manifest_fields, planned_manifest),
        paths["relations"]: csv_bytes(paths["relations"], relation_fields, planned_relations),
        paths["statements"]: jsonl_bytes(paths["statements"], statements),
        paths["enrichment"]: enr_after,
        paths["accepted"]: text_bytes(paths["accepted"], accepted_after),
        paths["process"]: text_bytes(paths["process"], process_after),
        paths["stages"]: text_bytes(paths["stages"], stages_after),
        paths["result"]: text_bytes(paths["result"], result_after),
        paths["agents"]: text_bytes(paths["agents"], agents_after),
        **cards,
    }
    before = {path: path.read_bytes() for path in output if path.exists()}
    meta = {
        **current_state,
        "touched_files": [path.relative_to(ROOT).as_posix() for path in output],
        "before_sha256": {path.relative_to(ROOT).as_posix(): hashlib.sha256(data).hexdigest() for path, data in before.items()},
        "output_sha256": {path.relative_to(ROOT).as_posix(): hashlib.sha256(data).hexdigest() for path, data in output.items()},
    }
    return output, before, meta


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    output, before, meta = build_outputs(args.dry_run)
    meta["mode"] = "apply" if args.apply else "dry_run"
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    if not args.apply:
        print("dry-run only; no project files written")
        return 0

    recovery = ROOT / "06-runtime" / "recovery" / f"S4-S5-S6-chp9-p253-tiepolo-endpoints-{DATE}"
    if recovery.exists():
        raise FileExistsError(f"recovery directory already exists: {recovery}")
    recovery.mkdir(parents=True)
    manifest = {}
    for path in output:
        rel = path.relative_to(ROOT)
        original = before.get(path)
        if original is None:
            manifest[rel.as_posix()] = None
            continue
        backup = recovery / "original" / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(original)
        manifest[rel.as_posix()] = hashlib.sha256(original).hexdigest()
    (recovery / "backup-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    written: list[Path] = []
    created: list[Path] = []
    try:
        for path, content in output.items():
            if path not in before:
                created.append(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
                handle.write(content)
                temporary = Path(handle.name)
            temporary.replace(path)
            written.append(path)
            if hashlib.sha256(path.read_bytes()).hexdigest() != hashlib.sha256(content).hexdigest():
                raise RuntimeError(f"post-write hash mismatch: {path.relative_to(ROOT)}")
    except Exception:
        for path in reversed(written):
            if path in before:
                path.write_bytes(before[path])
            elif path.exists():
                path.unlink()
        for path in created:
            if path.exists():
                path.unlink()
        raise
    print(f"apply complete: {len(written)} files; recovery copy: {recovery.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
