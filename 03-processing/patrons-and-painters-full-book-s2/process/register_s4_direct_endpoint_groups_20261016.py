from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
STATEMENT_PATH = TABLES / "book-statements.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-16"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
KIND_DIRS = {"work": "works", "event": "events", "place": "places"}


def source(chapter, page, file, lines, quote, summary, note=""):
    return {"chapter": chapter, "page": page, "file": file, "lines": lines,
            "quote": quote, "summary": summary, "note": note}


BATCHES = {
    "work": [
        {
            "group": "workgrp-99b6f34360e16f",
            "members": ["cand-5789"],
            "slug": "poussin-seven-sacraments-series",
            "name_zh": "普桑《七件圣事》绘画组",
            "name_en": "Nicolas Poussin’s Seven Sacraments Series",
            "description_zh": "本书将 Nicolas Poussin 为 Cassiano dal Pozzo 创作的《七件圣事》称为一组绘画，并称他于17世纪30年代后半开始绘制。本卡登记系列层级，不指某一幅单作或未经逐件核定的完整作品清单。",
            "description_en": "Haskell identifies the Seven Sacraments as a series of paintings made by Nicolas Poussin for Cassiano dal Pozzo and says Poussin began painting it in the second half of the 1630s. This unit records the series as a whole, not an individual painting or an independently verified complete item list.",
            "facts_zh": "- 作品类型：绘画组／系列。\n- 创作者：Nicolas Poussin（原书称 Poussin）。\n- 开始绘制：17世纪30年代后半；原文未在此给出确切首作日期。\n- 委托语境：Haskell 将其置于 Poussin 为 Cassiano 工作的语境，并将 Cassiano 的委托与系列构想作为作者判断；正式人物—作品关系仍留待 S6。",
            "facts_en": "- Work type: a series of paintings.\n- Creator: Nicolas Poussin (named as Poussin in the cited passage).\n- Begun: the second half of the 1630s; the passage gives no exact date for the first painting.\n- Commission context: Haskell places the series within Poussin’s work for Cassiano and presents Cassiano’s commission and role in the series as the author’s interpretation; the formal person–work relation remains for S6.",
            "boundary_zh": "系列身份不等于单幅作品、版本或现存实物；此卡不据“七件”补出逐件清单、现藏地点或完整存世状态。后记所引1664年报告只说 Cassiano 曾考虑将该系列赠给一位未具名友人，不表示赠与实际发生。",
            "boundary_en": "The series identity is distinct from any individual painting, version, or surviving object. The card does not infer an itemized list, present location, or complete survival status from the title. The postscript’s report that Cassiano once considered giving the series to an unnamed friend does not establish a completed gift.",
            "sources": [
                source("4", "106", "04_CHP-4_sec_ii.md", "99", "the series of the Seven Sacraments which he began to paint in the second half of the 1630s", "第4章将《七件圣事》称为 Poussin 为 Cassiano 创作中最引人注目的一组作品，并给出开始绘制的大致时间。"),
                source("4", "107", "04_CHP-4_sec_ii.md", "102–104", "in Italy the Sacraments had only once been painted as a series", "第4章讨论该系列在意大利绘画史中的系列形式及其图像学。"),
                source("4", "109", "04_CHP-4_sec_ii.md", "128", "This, no doubt, was what led Cassiano to commission the Sacraments.", "Haskell将 Cassiano 对早期教会的兴趣与委托系列相连；这是作者解释。"),
                source("4", "110", "04_CHP-4_sec_ii.md", "132", "he was enormously proud of the Sacraments and refused permission to have them copied", "第4章称 Poussin 为该系列自豪并拒绝复制许可。"),
                source("20", "401", "20_CHP-20Postscript.md", "83–84", "actually thought of giving away the ‘Seven Sacraments’ to an un-named friend", "后记转述一份1664年报告，称 Cassiano 曾考虑将系列赠予未具名友人；不据此登记已完成的所有权转移。"),
            ],
            "process_note": "`cand-5789` 的 group=workgrp-99b6f34360e16f 仅含这一系列候选。第4章 p.106 将其称为 Poussin 为 Cassiano 创作的一组《七件圣事》并称开始绘制于17世纪30年代后半；pp.107、109–110论及系列形式、作者对 Cassiano 委托缘由的解释及 Poussin 对作品的态度；第20章后记 p.401 的1664年报告仅支持“曾考虑赠与”，不证明实际转移。manifest 中无同题 work KU。",
            "result_note": "`cand-5789` 映射至[普桑《七件圣事》绘画组](../units/works/poussin-seven-sacraments-series.md)。该 KU 以系列为对象，限定原书对开始绘制时间及 Cassiano 委托语境的叙述，不扩写逐件清单、版本或存世状态；1664年报告只记录曾考虑赠与。人物—作品关系候选留待 S6。",
        }
    ],
    "event": [
        {
            "group": "sg3-event-cand-9792",
            "members": ["cand-9792"],
            "slug": "giorgio-pisani-1780-election-and-entry",
            "name_zh": "乔治·皮萨尼1780年当选与入城仪式",
            "name_en": "Giorgio Pisani’s 1780 Election and Solemn Entry as Procuratore di San Marco",
            "description_zh": "本卡记录 Haskell 围绕 Giorgio Pisani 于1780年当选 Procuratore di San Marco 及相关公开入城、游行仪式的叙述。原书分别叙述当选和入城过程；不推定二者发生在同一天。",
            "description_en": "This unit records Haskell’s account of Giorgio Pisani’s 1780 election as Procuratore di San Marco and the associated public entry and procession. The book narrates the election and entry separately; this card does not assume that they occurred on the same day.",
            "facts_zh": "- 事件性质：当选及相关公开入城仪式；本卡标题为描述性工作题名。\n- 时间：当选发生于1780年；原书对图像／版画在入城仪式中展出的判断为“有充分理由相信”其发生在1780年，未给出具体日期。\n- 地点：威尼斯；原书以城市宫殿沿线及入城游行为语境。\n- 参与者：Giorgio Pisani（当选者）；Gozzi 写有颂词。\n- 经过：当局为新任 Procuratore 的游行路线悬挂画作是原书所述习惯；相关具体图像是否专为 Pisani 此次入城而委托，Haskell 明确提出反证并限制判断。",
            "facts_en": "- Event type: election and associated public entry; the card title is descriptive.\n- Date: the election took place in 1780. Haskell says there is good reason to believe that pictures or prints were displayed at the entry in 1780, without giving an exact day.\n- Place: Venice, in the context of palaces along the procession route and the public entry.\n- Participant: Giorgio Pisani, the elected Procuratore; Gozzi wrote a tribute.\n- Course: Haskell describes pictures hung along the route as a custom for a newly elected Procuratore. He also qualifies whether the specific images were commissioned for Pisani’s entry and does not establish that they were.",
            "boundary_zh": "当选与公开入城作为同一叙述组登记，但原书没有说二者同日。游行当晚的宫邸庆祝会另为事件候选 cand-9812，不并入本卡；不将所有沿线画作写成此次专门委托。",
            "boundary_en": "The election and public entry are registered as one source-defined narrative group, while the book does not say they occurred on the same day. The palace celebration on the evening of the procession is a separate event candidate, cand-9812, and is not merged here. The card does not treat all route pictures as commissions made specifically for this entry.",
            "sources": [
                source("10", "326", "10_CHP-10_sec_ii.md", "211–213", "In 1780, after complicated intrigues, he was suddenly elected", "第10章记 Pisani 于1780年当选 Procuratore di San Marco，任命引发热烈反响，并有颂词与纪念刊物。"),
                source("10", "326–327", "10_CHP-10_sec_ii.md", "216–217", "It was the custom when a new Procurator was elected to have the palaces along which the procession would have to pass hung with pictures", "第10章说明新任 Procurator 入城游行路线上的装饰惯例，并记相关图像沿路线展示。"),
                source("10", "327", "10_CHP-10_sec_ii.md", "237", "good reason to believe that the pictures or the prints were exhibited in 1780", "第10章注3以限定语支持图像／版画于1780年入城时展出的可能，并明确反对将它们全说成专为此次入城而委托。"),
            ],
            "process_note": "`cand-9792` 独立新组。第10章 p.326 记 Pisani 于1780年当选，p.326–327 讨论新任 Procuratore 入城路线与图像，p.327 注3仅以“有充分理由相信”判断图像／版画曾于1780年展出，并指出若干图像早于其当选，不应概括成专为此次入城委托。当选与入城保留原书叙述关联但不声称同日；游行当晚宫邸庆祝会由独立候选 `cand-9812` 表示。",
            "result_note": "`cand-9792` 映射至[乔治·皮萨尼1780年当选与入城仪式](../units/events/giorgio-pisani-1780-election-and-entry.md)。卡片分列1780年当选与相关入城游行，保留不确定的具体日期及 Haskell 对图像展示、委托关系的限定；游行当晚宫邸庆祝会另由 `cand-9812` 登记。关系候选留待 S6。",
        },
        {
            "group": "sg3-event-cand-9812",
            "members": ["cand-9812"],
            "slug": "giorgio-pisani-1780-palace-entry-celebration",
            "name_zh": "乔治·皮萨尼入城游行当晚的宫邸庆祝会",
            "name_en": "Palace Celebration on the Evening of Giorgio Pisani’s Entry Procession",
            "description_zh": "本卡记录 Haskell 所述 Pisani 入城游行当晚在宫邸举行的大型庆祝会。书中将其作为游行当晚的另一场事件叙述，且叙事时间顺序不能单独证明庆祝会导致其后审讯行动。",
            "description_en": "This unit records the large palace celebration that Haskell places on the evening of Pisani’s entry procession. The book narrates it as a distinct event that evening; the narrative sequence alone does not establish that the celebration caused the later inquisitorial action.",
            "facts_zh": "- 事件性质：入城游行当晚的宫邸庆祝会；中文题名为描述性工作题名。\n- 时间：与 Pisani 1780年入城叙述相连；原书未给具体日期。\n- 地点：宫邸；原书段落未在此句中重述具体宫名。\n- 参与者：来宾及暗中活动的侦察者；原书称主接待室中有一幅被解读为政治寓意的画作，菜单印有法文诗句。",
            "facts_en": "- Event type: a palace celebration on the evening of the entry procession; the title is descriptive.\n- Date: linked to Haskell’s account of Pisani’s 1780 entry; no exact date is supplied.\n- Place: the palace; the passage does not restate the palace’s proper name here.\n- Participants: guests and spies. Haskell reports a picture in the main reception room that was read as politically charged and French lines printed on the menus.",
            "boundary_zh": "本事件与 Pisani 当选及公开入城仪式候选 cand-9792 分开：它发生在游行当晚。四天后审讯机构采取行动、随后 Pisani 被捕是原书接续叙述的后续事态；本卡不将叙述顺序提升为因果结论。",
            "boundary_en": "This event is separate from candidate cand-9792, Pisani’s election and public entry: it is the celebration held on the evening of the procession. Haskell next narrates inquisitorial action four days later and Pisani’s arrest; this card does not turn narrative sequence into a causal conclusion.",
            "sources": [
                source("10", "327", "10_CHP-10_sec_ii.md", "229–230", "But the real trouble came on the evening of the procession when a huge celebration was held in the palace.", "第10章称游行当晚宫邸举行大型庆祝会，侦察者在宾客间活动并关注主接待室的画作。"),
                source("10", "327", "10_CHP-10_sec_ii.md", "230–233", "The atmosphere was fraught with suspicion", "第10章记述对画作、菜单法文诗句及当时氛围的描述。"),
                source("10", "327", "10_CHP-10_sec_ii.md", "234–235", "Four days later the Inquisitors moved into action.", "原书称四天后 Inquisitors 开始行动，随后记 Pisani 被捕；此为叙述上的后续，不据此断定庆祝会是原因。"),
            ],
            "process_note": "`cand-9812` 保持为区别于 `cand-9792` 当选／公开入城仪式的独立事件组。第10章 p.327 称大型庆祝会于游行当晚在宫邸举行，记有来宾、侦察者、主接待室画作及菜单诗句；随后记四天后 Inquisitors 行动及 Pisani 被捕。本卡保留来源叙述，不从时间先后推因果。",
            "result_note": "`cand-9812` 映射至[乔治·皮萨尼入城游行当晚的宫邸庆祝会](../units/events/giorgio-pisani-1780-palace-entry-celebration.md)，与 `cand-9792` 的当选／入城仪式分开。卡片保留 Haskell 对现场情况的叙述及四天后行动的时间限定，不推定庆祝会导致逮捕；关系候选留待 S6。",
        },
    ],
    "place": [
        {
            "group": "sg3-place-cand-5317",
            "members": ["cand-5317"],
            "slug": "france",
            "name_zh": "法国",
            "name_en": "France",
            "description_zh": "本书中 France 作为国家地点，出现在 Bernini 访问耶稣会教堂、威尼斯艺术家赴法及意大利艺术在法国传播等语境。本卡汇集原书对法国这一地点的跨章指称，不把历史国家称谓规范成现代政权或固定边界。",
            "description_en": "In Haskell’s account, France is a country-place in passages about Bernini’s visits to Jesuit churches, Venetian artists travelling there, and the circulation of Italian art. This unit groups the book’s cross-chapter references to France without normalizing the historical name to a modern polity or fixed boundary.",
            "facts_zh": "- 地点性质：原书所称国家／地理区域 France。\\n- 空间范围：仅按原书语境记录；未据本卡确定不同时期的边界、政权或行政层级。\\n- 本书相关语境：第3章记 Bernini 在法国访问耶稣会教堂；第10章讨论威尼斯艺术家赴法及意大利艺术在法国的影响；第20章后记讨论 Mazarin 在法国推动意大利巴洛克艺术。",
            "facts_en": "- Place type: the country or geographic region called France in the book.\\n- Spatial scope: recorded only as used in the source; this card does not define period-specific borders, governments, or administrative levels.\\n- Book contexts: Chapter 3 places Bernini’s visits to Jesuit churches in France; Chapter 10 discusses Venetian artists travelling there and Italian art’s impact in France; the postscript discusses Mazarin’s promotion of Italian Baroque art in France.",
            "boundary_zh": "同一地点候选涵盖多个时代与叙述语境；不据此断定所有条目指向同一历史政权、边界或单一行政体。法国圣路易堂等位于法国的具体建筑保持独立地点身份；国籍、法语使用者或 French visitors 的称谓不自动映射为地点关系。",
            "boundary_en": "The candidate spans several periods and narrative contexts; it does not establish one continuous historical polity, boundary, or administrative entity for every reference. Specific buildings in France, such as San Luigi dei Francesi, retain separate place identities; nationality, French-speaking people, and the label “French visitors” do not automatically become place relations.",
            "sources": [
                source("3", "86", "03_CHP-3_sec_iv.md", "97", "In France he often visited Jesuit churches", "第3章将 Bernini 访问耶稣会教堂的地点明确写为 France。"),
                source("10", "284", "10_CHP-10_intro.md", "173–174", "This visit, marked the peak of Venetian influence abroad and the last time that contemporary Italian art was to make a serious impact on France.", "第10章将 Pellegrini、Carriera 与 Zanetti 的赴法访问置于威尼斯影响及意大利艺术传播语境。"),
                source("20", "402", "20_CHP-20Postscript.md", "106–107", "the most enterprising patron and collector of Italian art in France was in fact the Italian Cardinal Mazarin", "后记讨论 Mazarin 在法国推动意大利巴洛克艺术；这里只记录其国家地点语境。"),
            ],
            "process_note": "cand-5317 为跨章地点候选，包含48条书内提及及15条直接断言端点；其 S3 new 组为 sg3-place-cand-5317。第3章 p.86 明确将 Bernini 访问耶稣会教堂置于 France；第10章 p.284 与第20章后记 p.402 又分别以法国作为艺术传播和政治文化语境。当前 manifest 无代表法国国家地点的 KU；法国圣路易堂是具体建筑，不是同一对象。",
            "result_note": "cand-5317 映射至法国地点 KU。卡片记录本书中跨章的 France 指称，限定不据此统一不同时期的政权与边界，也不把法籍人物或法语称谓自动转换为地点关系；关系候选留待 S6。",
        }
    ],
}

BATCHES["work"].append({
    "group": "workgrp-adab2fea7b8577",
    "members": ["cand-6917"],
    "slug": "bernini-equestrian-statue-louis-xiv-marcus-curtius",
    "name_zh": "贝尔尼尼《路易十四骑马像》（后改称马库斯·库尔提乌斯）",
    "name_en": "Bernini’s Equestrian Statue of Louis XIV, later altered as Marcus Curtius",
    "description_zh": "本书称 Louis XIV 在 Bernini 的路易十四胸像完成后订制其骑马像。作品于 Bernini 返回罗马四年后开工，1684年抵达巴黎，后置于凡尔赛园林偏远角落；Louis XIV 曾要求砸毁，随后改变主意，Girardon 作必要改造，形象被称为 Marcus Curtius。本卡记录同一雕像的委托、迁置与改造叙述。",
    "description_en": "Haskell says Louis XIV ordered an equestrian statue after Bernini completed the king’s bust. Work began four years after Bernini’s return to Rome; the statue reached Paris in 1684 and was later placed in a remote corner of the Versailles grounds. Louis first wanted it broken up, then relented; Girardon made alterations and the figure was called Marcus Curtius. This unit records the book’s account of one statue’s commission, relocation, and alteration.",
    "facts_zh": "- 作品类型：骑马像。\\n- 创作者：Gian Lorenzo Bernini；委托者：Louis XIV。\\n- 开工：Bernini 返回罗马四年后；本段没有直接给出开工的公历年份。\\n- 抵达巴黎：1684年，晚于 Bernini 去世。\\n- 后续安置：Louis XIV 改变砸毁雕像的决定后，将其置于凡尔赛园林最偏远处。\\n- 改造与称名：Girardon 作必要改造，之后形象被称为 Marcus Curtius。\\n- 后续报价：Haskell 转述有人传言 Del Carpio 曾愿以30,000 scudi 求购，且该报价未获接受；不记录为实际所有权转移。",
    "facts_en": "- Work type: equestrian statue.\\n- Creator: Gian Lorenzo Bernini; commissioner: Louis XIV.\\n- Begun: four years after Bernini’s return to Rome; the passage does not directly supply a calendar year for the start of work.\\n- Arrival in Paris: 1684, after Bernini’s death.\\n- Later placement: after Louis XIV relented from his wish to break it up, the statue was banished to a remote corner of the Versailles grounds.\\n- Alteration and later name: Girardon made necessary alterations, after which the figure was called Marcus Curtius.\\n- Later offer: Haskell reports a rumor that Del Carpio offered 30,000 scudi for the statue and says the offer was not accepted; this is not recorded as a transfer of ownership.",
    "boundary_zh": "此候选与既有《路易十四肖像》（Bernini, Louis XIV）是不同作品：后者为胸像，本卡为骑马像。书中把后来的改造与 Marcus Curtius 称名接在同一雕像叙述中，故暂按同一作品的变化史登记；不据此扩写改造前后完整实物状态或外部现存位置。",
    "boundary_en": "This candidate is distinct from the existing Portrait of Louis XIV by Bernini, which is a bust; this unit is the equestrian statue. Haskell narrates the later alteration and the name Marcus Curtius as the history of this statue, so they are recorded here as changes to one work. The card does not add an external account of the object’s present state or location.",
    "sources": [
        source("7", "188", "07_CHP-7_sec_i.md", "237–238", "Louis was sufficiently impressed to order an equestrian statue.", "第7章称 Louis XIV 对 Bernini 的胸像印象深刻，随后订制一座骑马像。"),
        source("7", "188", "07_CHP-7_sec_i.md", "238", "Bernini began work on this four years after his return to Rome, but it did not reach Paris until 1684, some time after his death.", "第7章给出相对开工时间及1684年抵达巴黎、晚于 Bernini 去世的时间信息。"),
        source("7", "188", "07_CHP-7_sec_i.md", "240", "Soon Girardon made the necessary alterations and the figure was called Marcus Curtius.", "第7章称 Louis XIV 放弃砸毁计划并将作品置于凡尔赛园林，随后由 Girardon 改造并称为 Marcus Curtius。"),
        source("7", "191", "07_CHP-7_sec_i.md", "270–272", "he was offering 30,000 scudi for the ill-fated equestrian statue of Louis XIV", "第7章记 Del Carpio 有意出价，但该报价未被接受，不构成所有权转移。"),
    ],
    "process_note": "cand-6917 为一个 new work 组，当前无同一骑马像的既有 work KU。现有 units/works/bernini-louis-xiv 是图版27b所记胸像，不与该骑马像合并。第7章 pp.188–189 记录 Louis XIV 委托、相对开工时间、1684年抵达巴黎、凡尔赛安置及 Girardon 改造；p.191 记 Del Carpio 的求购传言及未获接受。作品变化状态严格按 Haskell 叙述，不补外部实物信息。",
    "result_note": "cand-6917 登记为 Bernini《路易十四骑马像》作品 KU；卡片将其与既有路易十四胸像分开，并记录1684年抵达、凡尔赛安置、Girardon 改造及 Marcus Curtius 后称，保留报价未被接受的限定。",
})

BATCHES["work"].append({
    "group": "workgrp-08f1a6d27a1b75",
    "members": ["cand-9007"],
    "slug": "mcswiny-allegorical-tomb-paintings-british-worthies",
    "name_zh": "麦克斯温尼英国名人寓意墓葬绘画组",
    "name_en": "McSwiny’s Allegorical Tomb Paintings for England’s Recent Great Men",
    "description_zh": "Haskell 记 Owen McSwiny 代表 Lord March（后为 Duke of Richmond）提出委托意大利画家绘制一组寓意墓葬画，以纪念英国近代显要人物。原书称1722年前已有十五幅开工；之后既评述该组画未能实现原定纪念目的，也记录其收藏和版画出版情况。本卡指绘画系列，不指实际墓葬；具体单幅作品、收藏清单及1741年版画书均保持各自边界。",
    "description_en": "Haskell reports that Owen McSwiny, acting for Lord March (later the Duke of Richmond), proposed commissioning Italian painters to make a series of allegorical tomb pictures commemorating England’s recent great men. The book says fifteen pictures had been started by 1722; it later judges that the paintings failed their declared commemorative aim and recounts their acquisition and engraved publication. This unit is the painting series, not physical tombs; individual pictures, uncertain ownership lists, and the 1741 book remain distinct.",
    "facts_zh": "- 作品类型：以寓意墓葬为题材的一组绘画；原书交替称其为 tombs、monuments、pictures 和 paintings。\n- 提议者与委托语境：Haskell 称 McSwiny 代表 Lord March（后为 Duke of Richmond）提出由意大利画家绘制该系列；正式委托关系候选留待 S6。\n- 预定纪念对象：英国君主、指挥官及其他显要人物。Haskell 判断项目开始时几乎可以确定没有确定名单；具体人物和单幅作品另行登记。\n- 形式与分工：画幅拟采用统一竖式及半圆形顶部；McSwiny 要求每幅由人物、风景、建筑与装饰分工绘制。\n- 实施情况：原书称截至1722年已有十五幅开工，不表示十五幅均完成。Haskell 认为这组画未能达到其宣称的纪念英国名人的目标。\n- 收藏与版画：Haskell 称 Richmond 至少购入十幅，William Morice 于1730年买下其余已完成画作；其注释同时指出具体归属清单存在混乱。拟议的五十幅版画卷于1741年出版时仅有十八幅版画，其中九幅为寓意墓画。",
    "facts_en": "- Work type: a series of paintings depicting allegorical tombs; Haskell also calls them monuments, pictures, and paintings.\n- Proposal and commission context: Haskell says McSwiny proposed the series on behalf of Lord March, later the Duke of Richmond, for execution by Italian painters; the formal commission relation remains for S6.\n- Intended subjects: British monarchs, commanders, and other illustrious figures. Haskell infers that no definite list had probably been drawn up at the outset; named subjects and individual pictures are kept distinct.\n- Format and roles: the pictures were intended to share a vertical format with semicircular tops; McSwiny required separate artists for figures, landscape, buildings, and ornaments.\n- Execution: the book reports that fifteen pictures had been started by 1722; this does not mean all fifteen were completed. Haskell judges that the series failed its declared aim of commemorating British Worthies.\n- Ownership and engravings: Haskell says Richmond bought at least ten paintings and William Morice bought the remaining completed pictures in 1730; his note also records confusion over the precise acquisition list. The proposed fifty-plate volume appeared in 1741 with eighteen plates, only nine of them allegorical tombs.",
    "boundary_zh": "本卡登记系列层级，区别于其中任何一幅具名纪念画或版本；“tomb/monument”是绘画所表现的寓意墓葬，不据词义登记实体墓地或纪念建筑。1741年《Tombeaux des Princes》是版画出版物，不并入绘画系列。后记候选 cand-11080 仅称“为 Owen McSwiny 绘制的纪念画”并延续到作品目录，尚未证明与本系列完全对应，故其 S3 对应关系保持 undecided，不纳入本卡映射。",
    "boundary_en": "This unit records the series as a whole and remains distinct from every named commemorative painting and version within it. “Tomb” and “monument” refer to depicted allegorical tombs, not a physical burial site or monument. The 1741 Tombeaux des Princes is a printed publication, not part of the painting series. Postscript candidate cand-11080 refers only to commemorative pictures painted for Owen McSwiny and continues into a catalogue discussion; its correspondence with this series is not established, so its S3 status remains undecided and it is not mapped here.",
    "sources": [
        source("10", "287", "10_CHP-10_intro.md", "213", "he proposed to have painted by the leading Italian artists a series of allegorical tombs to commemorate the great men of England’s recent history", "第10章称 McSwiny 代表 Lord March 提出由意大利画家绘制纪念英国近代显要人物的寓意墓葬画系列。"),
        source("10", "288", "10_CHP-10_intro.md", "220–221", "The pictures were all to be the same size, vertically inclined with semicircular tops like altar paintings", "第10章记画作拟采用统一尺寸、竖式及半圆形顶部。"),
        source("10", "288", "10_CHP-10_intro.md", "225–227", "every picture was to be painted by three artists", "第10章记 McSwiny 对每幅画的分工要求，分别绘制人物、风景、建筑及装饰。"),
        source("10", "289", "10_CHP-10_intro.md", "230", "by 1722 fifteen pictures had already been started", "第10章称截至1722年已有十五幅开工，并说明多数后来由 Richmond 收藏。"),
        source("10", "289", "10_CHP-10_intro.md", "232", "they entirely fail to achieve their declared aim", "Haskell 评价这些作品没有实现其宣称的纪念英国名人目标。"),
        source("10", "289", "10_CHP-10_intro.md", "238", "there is a great deal of confusion about which of these pictures were actually acquired by the Duke of Richmond", "第10章注2指出具体哪些画作由 Richmond 实际购入存在很大混乱。"),
        source("10", "290", "10_CHP-10_intro.md", "246", "the Duke of Richmond bought at least ten of the paintings", "第10章记 Richmond 至少购入十幅，Morice 于1730年买下其余已完成作品。"),
        source("10", "291", "10_CHP-10_intro.md", "259", "There were eighteen instead of fifty plates, and only nine of the allegorical tombs were engraved", "第10章称1741年出版物只有十八幅版画，其中九幅为寓意墓画。"),
    ],
    "process_note": "cand-9007 为一个 new work 组，原书第10章 pp.287–291 连续描述 McSwiny 代表 Lord March 提出的寓意墓葬绘画系列、画面规则、1722年前开工情况、作者对项目成效的评价及后续收藏与版画出版。作品对象为绘画系列，不是实际墓葬。Haskell 注2明确说明 Richmond 购藏的具体清单存在混乱，故保留“至少十幅”及收藏不确定性。第20章后记候选 cand-11080 只指“为 Owen McSwiny 绘制的纪念画”及后续目录，尚无明确措辞证明其与本系列同一；cand-11080 仍保持 undecided，不合并到本 work 组。",
    "result_note": "cand-9007 登记至麦克斯温尼英国名人寓意墓葬绘画组 KU；记录提议、统一画幅与分工、1722年前十五幅开工、Haskell 对项目目标的评价及有保留的收藏和版画信息。作品系列与实体墓葬、单幅画及1741年出版物分开；后记 cand-11080 的身份对应仍待证。",
})

BATCHES["work"].append({
    "group": "workgrp-0323f2bb274493",
    "members": ["cand-5232"],
    "slug": "gaulli-gesu-dome-and-vault-decoration-commission",
    "name_zh": "耶稣堂穹顶与拱顶装饰委托",
    "name_en": "Gaulli’s Dome and Vault Decoration Commission at the Gesù",
    "description_zh": "Haskell 记载 Oliva 于1672年8月与 Gaulli 签订合同，委托其绘制并装饰耶稣堂穹顶、主拱顶及横翼拱顶。原约将穹顶与其余绘饰分列工期，并排除预留给 Borgognone 的后殿拱顶。本卡表示这项整体装饰委托及其约定范围，不指单幅壁画，也不表示所有项目均按期完成。",
    "description_en": "Haskell reports that Oliva and Gaulli signed a contract in August 1672 for the decoration of the Gesù’s dome, main vault, and transept vaults. The contract set separate deadlines for the dome and the remaining work and excluded the tribune vault reserved for Borgognone. This unit records the overall decoration commission and its agreed scope, not an individual fresco or proof that every element was completed on schedule.",
    "facts_zh": "- 对象类型：耶稣堂内部穹顶、主拱顶及横翼拱顶的大型绘饰工程；本卡按原书所述整体委托范围登记。\n- 委托语境与日期：Haskell 称 Oliva 与 Gaulli 于1672年8月签订合同。\n- 合同范围：穹顶及其灯笼、帆拱；含窗龛的主拱顶；以及圣依纳爵和圣方济各·沙勿略礼拜堂上方的横翼拱顶。后殿拱顶预留给 Borgognone，不在此约范围内。\n- 工期：穹顶约定两年内完成，其余绘画、镀金和灰泥工程约定于八年内、即1682年底前完成。Haskell 另记穹顶于1675年4月已就绪，主拱顶在此后四年完成；不将合同期限写成所有部分的实绩日期。\n- 合同条件：Gaulli 自付绘画和镀金费用；若专家认为作品不够完善，他承诺免费修正。顺利完成时约定报酬为14,000 scudi，脚手架等费用另计。\n- 展示评价：Haskell 记受邀专家对私人预展不热衷，而公众赞赏绘画与灰泥组合；这是作者报告的不同反应。",
    "facts_en": "- Object type: an extensive decorative programme for the Gesù’s dome, main vault, and transept vaults; this card records the overall commission as Haskell describes it.\n- Commission context and date: Haskell says Oliva and Gaulli signed a contract in August 1672.\n- Contracted scope: the dome with its lantern and pendentives; the main vault including window recesses; and the transept vaults above the chapels of St Ignatius and St Francis Xavier. The tribune vault was reserved for Borgognone and excluded from this contract.\n- Schedule: the dome was due within two years; the remaining painting, gilding, and stucco work was due within eight years, by the end of 1682. Haskell separately reports that the dome was ready by April 1675 and the main vault four years later; the contractual deadline is not treated as a completion date for every element.\n- Contract terms: Gaulli was to pay the painting and gilding expenses and correct work judged imperfect by experts without charge. If all went well, his fee was 14,000 scudi, with scaffolding and related expenses additional.\n- Reception: Haskell reports that invited experts were not enthusiastic at a private showing, while the public admired the painting and stucco arrangement; these are the author’s reports of differing reactions.",
    "boundary_zh": "本卡登记1672年合同所定义的绘饰工程，不是合同文书本身；合同档案候选 cand-5227 仍为独立 archive 对象，待 S4 登记及后续关系审查。既有[盖乌利耶稣堂拱顶壁画工程](gaulli-gesu-vaults.md)记录第1章所称中殿及横翼拱顶、八年工期的作品范围，未纳入此处另行列出的穹顶及其两年工期，故本次保留两项身份边界，不把较大委托自动当成单一壁画。图版14《耶稣圣名的胜利》是单幅中殿壁画，亦与整体工程分开；后殿拱顶及此前 Courtois 的方案不并入。作品的正式组成或 `part_of` 关系仍待 S6 审查。",
    "boundary_en": "This unit records the decorative work defined by the 1672 contract, not the contract document itself; archive candidate cand-5227 remains a distinct archive object, pending S4 registration and later relation review. The existing [Gaulli’s vault fresco project at the Gesù](gaulli-gesu-vaults.md) records the nave and transept vault work and its eight-year allowance as described in Chapter 1; it does not include the dome and its separately stated two-year deadline listed here. The two work identities are therefore kept distinct, and the larger commission is not treated as one individual fresco. Plate 14, Triumph of the Name of Jesus, is a separate nave fresco; the tribune vault and Courtois’s earlier proposal are also excluded. Any formal component or `part_of` relation between these works remains for S6 review.",
    "sources": [
        source("3", "80", "03_CHP-3_sec_iv.md", "39", "In August 1672 a contract was signed between the two men.", "第3章称 Oliva 与 Gaulli 于1672年8月签订合同。"),
        source("3", "80", "03_CHP-3_sec_iv.md", "42–43", "For Gaulli agreed to paint the entire dome (including the lantern and the pendentives which had already been frescoed by Giovanni de’ Vecchi); the entire vault including the window recesses; and the vaults of the transepts above the chapels of St Ignatius and St Francis Xavier.", "第3章列出穹顶、主拱顶和横翼拱顶的合同范围。"),
        source("3", "80", "03_CHP-3_sec_iv.md", "43", "He was to omit only the vault of the tribune which was being kept for Borgognone.", "原合同排除留给 Borgognone 的后殿拱顶。"),
        source("3", "80", "03_CHP-3_sec_iv.md", "43", "The dome was to be completed within two years, and all the rest of the work—gilding, painting and stucco—within eight years from then, i.e. by the end of 1682.", "第3章分别给出穹顶与其余绘饰的合同工期。"),
        source("3", "80", "03_CHP-3_sec_iv.md", "44–45", "The dome was ready by April 1675,4 and four years later the vault was completed.", "第3章报告穹顶就绪及主拱顶完成的先后时间，不推定整个合同范围完成日期。"),
        source("3", "80", "03_CHP-3_sec_iv.md", "43", "If the work was considered by experts to be other than perfect Gaulli undertook to correct it without charge.", "合同约定专家认为作品不完善时 Gaulli 应免费修正。"),
        source("3", "80", "03_CHP-3_sec_iv.md", "43", "If all went well he was to be paid 14,000 scudi as well as all the expenses of scaffolding and so on.", "第3章记录14,000 scudi 的约定报酬及另计脚手架等费用。"),
        source("3", "80", "03_CHP-3_sec_iv.md", "45", "with the general public it won ‘universal admiration both for the beauty of the painting and for the arrangement of the stucco which makes it still more worthy of applause’", "Haskell 对公众观看耶稣堂绘画与灰泥组合的反应作出报告。"),
    ],
    "process_note": "cand-5232 为独立 new work 组，表示合同定义的绘饰工程，不是合同文书本身；合同档案 cand-5227 另属 archive，尚待 S4。第3章 p.80 明确将绘饰范围界定为1672年8月合同下的整体工程：穹顶及其灯笼、帆拱，主拱顶及窗龛，横翼拱顶；穹顶工期为两年，其余绘画、镀金与灰泥工程为八年，后殿拱顶排除并留给 Borgognone。既有 `units/works/gaulli-gesu-vaults` 记录第1章所称中殿及横翼拱顶与八年工期；其范围未包含本候选另外列出的穹顶及独立两年期限，因此 S3 保留为大范围装饰工程与范围较窄的拱顶绘画工程两个对象，不并为一张单作卡。`cand-11837` 因缺少 S2 mention-level 锚点仍为 undecided，不并入。当前不新增正式关系，10条关系候选留待 S6核对整体工程与其组成作品的端点关系。",
    "result_note": "cand-5232 登记为耶稣堂穹顶与拱顶装饰委托 KU，按1672年合同范围记录穹顶、主拱顶及横翼拱顶、分项工期、约定条件与 Haskell 所述进度。此 KU 表示绘饰工程，不是合同 archive cand-5227；它与现有八年拱顶壁画工程卡按整体工程／范围较窄的拱顶作品分开，单幅《耶稣圣名的胜利》及后殿拱顶方案亦不并入；组成关系留待 S6。",
})

BATCHES["work"].append({
    "group": "workgrp-05ac00daf8fe99",
    "members": ["cand-5065"],
    "slug": "lanfranco-dome-fresco-s-andrea-della-valle",
    "name_zh": "兰弗兰科圣安德烈堂穹顶壁画",
    "name_en": "Lanfranco’s Dome Fresco at S. Andrea della Valle",
    "description_zh": "Haskell 将圣安德烈堂 S. Andrea della Valle 的穹顶壁画归于 Giovanni Lanfranco，并称其于1627年完成。书中描述灯笼中的基督为光源，光线逐渐充满穹顶表面，周围有诸圣、先知、使徒与天使班列。本卡是作品，不是穹顶建筑空间；图名为描述性工作译名。",
    "description_en": "Haskell attributes the dome fresco at S. Andrea della Valle to Giovanni Lanfranco and says it was completed in 1627. He describes Christ in the lantern as the source of light filling the dome surface, surrounded by choirs of saints, prophets, apostles, and cherubs. This unit is the fresco, not the architectural dome; its title is descriptive rather than a formal work title.",
    "facts_zh": "- 作品类型：圣安德烈堂穹顶的壁画装饰；不等同于穹顶这一建筑空间。\n- 作者归属：Haskell 称为 Lanfranco 的穹顶壁画；本卡按原书表述记录，未作外部归属核验。\n- 完成时间：Haskell 记为1627年；该日期随作者引注记载，不据此补出更精确的完工日。\n- 可能开工时间：第3章称画中的圣安德鲁·阿韦利诺于1624年列福，“壁画可能在那时开始”；保留作者的可能性表述。\n- 构图描述：灯笼中基督为光源，光线向外扩展并充满画面；周围诸圣、殉道者、先知、使徒及 cherubs 合唱赞颂。圣母注视光线，并指向两侧的圣安德鲁、圣加耶塔诺、圣彼得及圣安德鲁·阿韦利诺。人物及集体形象分别作为图像端点处理。\n- 比较与影响：Haskell 称该穹顶是帕尔马 Correggio 穹顶之后一百余年间同类穹顶的首例，并称其影响后来的艺术家约一百年；这些是作者的历史评价，不是独立验证的影响范围。第6章另泛称 Lanfranco 在 S. Andrea 的早期壁画已被视为经典，本卡不把这一复数表述缩限为只指本穹顶。",
    "facts_en": "- Work type: a fresco decorating the dome of S. Andrea della Valle; it is not the architectural dome itself.\n- Attribution: Haskell identifies the dome fresco as Lanfranco’s; this card records the book’s attribution without external authorship verification.\n- Completion: Haskell dates it to 1627; no more precise completion date is inferred.\n- Possible start: Chapter 3 says the fresco was “probably begun” when St Andrew Avellino was beatified in 1624; the qualification is retained.\n- Composition: Christ in the lantern is described as the source of light spreading across the surface, surrounded by choirs of saints, martyrs, prophets, apostles, and cherubs. The Virgin gazes toward the light and gestures to St Andrew, S. Gaetano, St Peter, and St Andrew Avellino. The depicted figures and group remain distinct iconographic endpoints.\n- Comparison and influence: Haskell calls it the first dome of its kind since Correggio’s at Parma more than a century earlier and says it served as a model to artists for the next hundred years. These are the author’s historical assessments, not independently verified measures of influence. Chapter 6 separately refers broadly to Lanfranco’s earlier frescoes at S. Andrea as having come to be regarded as classics; this plural statement is not narrowed to this dome alone.",
    "boundary_zh": "本卡指穹顶内的绘画作品，不指 S. Andrea della Valle 教堂或穹顶建筑空间；与 Domenichino 的后殿／tribune 装饰及其横翼帆拱四福音作者组分开。候选 cand-1360 只是索引中的“dome of S. Andrea della Valle”子项，没有 S2 正文锚点，继续保持 undecided，不据此映射本卡。诸圣群 cand-5071、基督 cand-4141及具名圣徒仍是独立图像端点；关系候选待 S6。",
    "boundary_en": "This unit is the painting inside the dome, not the church or architectural dome space. It is distinct from Domenichino’s tribune decoration and his Evangelists in the pendentives. Index candidate cand-1360, “dome of S. Andrea della Valle,” has no S2 body anchor and remains undecided; it is not mapped here. The choir group cand-5071, Christ cand-4141, and the named saints remain distinct iconographic endpoints; relation candidates are for S6.",
    "sources": [
        source("3", "72", "03_CHP-3_sec_ii.md", "79", "Lanfranco’s dome, which was completed in 1627", "第3章称 Lanfranco 的穹顶壁画于1627年完成；第3条脚注为该日期提供作者引注。"),
        source("3", "72", "03_CHP-3_sec_ii.md", "79", "Light is the centre, radiating out from Christ, its source in the lantern, and gradually filling the whole surface", "第3章描述灯笼中基督所发出的光线及其在穹顶画面中的扩展。"),
        source("3", "72", "03_CHP-3_sec_ii.md", "79", "around which the choirs of saints, martyrs, prophets, apostles and cherubs hymn their praises", "第3章记穹顶画面中环绕光线的圣徒与天使班列。"),
        source("3", "72", "03_CHP-3_sec_ii.md", "79", "the Theatine beatified in 1624 when the fresco was probably begun", "第3章仅以 probably 将1624年列福与壁画可能开工时间相连。"),
        source("3", "78", "03_CHP-3_sec_iv.md", "18", "Lanfranco of a generation earlier had come to be looked upon as classics", "第3章后文泛称 Lanfranco 在 S. Andrea 的早期壁画已被视为经典；保留其复数及整体评价范围。"),
    ],
    "process_note": "cand-5065 为一个 new work 组，现有 manifest 无 Lanfranco 在 S. Andrea della Valle 的穹顶壁画 KU。第3章 p.72 称其于1627年完成、描写灯笼中基督为光源及周围图像，并以 probably 将圣安德鲁·阿韦利诺1624年列福与可能开工时间相连；p.78 的“壁画已成经典”是对 Lanfranco 在该堂作品的复数评价，本卡保留范围，不缩写为只评价穹顶。建筑地点、Domenichino 的相邻装饰和绘画中的人物／群体不并入作品身份。索引子项 cand-1360 无 S2 锚点，仍 undecided；cand-12318 的未具名艺术家群体也不并入作品。14条直接 S2 断言中9条关系候选留待 S6，本次不登记正式关系。",
    "result_note": "cand-5065 登记为 Lanfranco 圣安德烈堂穹顶壁画作品 KU。卡片记录 Haskell 所载1627年完成、可能于1624年开工、构图描述及作者对其比较和影响的判断；区分建筑穹顶、Domenichino 的装饰、人物图像端点及无 S2 锚点的索引候选 cand-1360。9条关系候选留待 S6。",
})

BATCHES["work"].append({
    "group": "workgrp-40fe5d001d7c1f",
    "members": ["cand-9251"],
    "slug": "smith-palladian-overdoor-series",
    "name_zh": "史密斯帕拉第奥式门上画系列",
    "name_en": "Joseph Smith’s Palladian Overdoor Series",
    "description_zh": "Haskell 将 Joseph Smith 为宣扬帕拉第奥及其建筑原则而策划的门上画委托描述为连续系列：Canaletto 于1744年绘制十三幅门上画，离开威尼斯后 Smith 又请 Visentini 延续系列建筑画，并由 Zuccarelli 添加装饰风景。本卡登记系列与委托计划，不把不同阶段画作合成一幅作品，也不推定系列总件数。",
    "description_en": "Haskell describes Joseph Smith’s overdoor commission, intended to glorify Palladio and his architectural principles, as a continuing series: Canaletto painted thirteen door pieces in 1744, and after he left Venice Smith had Visentini continue the architectural views, with Zuccarelli adding decorative landscapes. This unit records the series and commission, not a single painting or an inferred total number of works.",
    "facts_zh": "- 对象类型：为门上装饰设计的一组建筑画，包含1744年及1746年后的委托阶段。\n- 委托语境：第20章后记称其为 Smith 精心设计的委托，旨在彰显帕拉第奥及其建筑原则；这是 Haskell 对系列意图的概括。\n- 1744年阶段：Canaletto 绘制十三幅以帕拉第奥主要建筑为题的门上画；Haskell 同时指出并非所有画中建筑都出自帕拉第奥。\n- 后续阶段：Canaletto 离开后，Smith 转请 Visentini 延续系列。Haskell 描述十一幅后续建筑画取材于英国乡间别墅：五幅涉及 Inigo Jones，两幅分别涉及 Burlington 与 Colen Campbell，另有 Roger Morris 和 Vanbrugh 各一幅。\n- 分工及形式：Zuccarelli 为 Visentini 的建筑画添加威尼斯式装饰风景；原书称其参与较次要。后续画作主要依据 Colen Campbell《Vitruvius Britannicus》的版画，建筑细节大多准确，部分画面组合彼此分离的建筑。",
    "facts_en": "- Object type: a series of architectural pictures designed as overdoors, with commission phases described in 1744 and after 1746.\n- Commission context: the postscript calls it a carefully devised commission by Smith to glorify Palladio and his architectural principles; this is Haskell’s characterization of its purpose.\n- 1744 phase: Canaletto painted thirteen door pieces depicting Palladio’s principal buildings. Haskell notes that not all buildings represented were by Palladio.\n- Later phase: after Canaletto’s departure, Smith turned to Visentini to continue the series. Haskell describes eleven later architectural pictures based on English country houses: five portray works by Inigo Jones; two each by Burlington and Colen Campbell; and one each by Roger Morris and Vanbrugh.\n- Division and style: Zuccarelli added decorative Venetian landscapes to Visentini’s architectural views; Haskell calls his role minor. The later pictures were based primarily on engravings from Colen Campbell’s Vitruvius Britannicus, their architectural details were mostly accurate, and some combined geographically separate buildings.",
    "boundary_zh": "本卡登记系列层级。1744年 Canaletto 的十三幅门上画与1746年后 Visentini、Zuccarelli 参与的十一幅后续建筑画是不同阶段和贡献，不合成单幅作品；现有 S2 证据不支持逐件目录、全部存世情况或系列总件数。后记称 William Barcham 分析过此委托，但该研究未在本轮独立查阅，不据其增补内容。索引候选 cand-2785、cand-2883 仍待证其艺术家子项是否代表可独立识别作品；cand-2453 的“委托”事件索引项因缺少对应 S2 身份锚点保持 undecided，均不强行并入本卡。",
    "boundary_en": "This card records the series level. Canaletto’s thirteen 1744 door pieces and the eleven later architectural pictures involving Visentini and Zuccarelli are distinct phases and contributions, not one individual work; the available S2 evidence does not support a complete item list, survival account, or total series count. The postscript says William Barcham analyzed the commission, but that study was not independently consulted here and no details are added from it. Index candidates cand-2785 and cand-2883 remain pending as to whether the artists’ subentries denote separately identifiable works; commissioning-event candidate cand-2453 also remains undecided because it lacks a corresponding S2 identity anchor. They are not forced into this card.",
    "sources": [
        source("10", "308", "10_CHP-10_intro.md", "456–458", "13 Door Pieces", "第10章记 Canaletto 于1744年绘制十三幅门上画，并限定并非所有画中建筑均为帕拉第奥作品。"),
        source("10", "308", "10_CHP-10_intro.md", "464–466", "After Canaletto’s departure in 1746 Smith turned to two other artists to continue the series of overdoors illustrating Palladian architecture.", "第10章记 Canaletto 离开后 Smith 请两位艺术家继续帕拉第奥式门上画系列。"),
        source("10", "308", "10_CHP-10_intro.md", "466–468", "adding attractive decorative landscapes", "第10章说明 Zuccarelli 为 Visentini 的建筑画添加装饰风景，且参与较次要。"),
        source("10", "309", "10_CHP-10_intro.md", "470–472", "Five of the eleven pictures portray works by Inigo Jones", "第10章列出十一幅后续画作所表现的建筑师及比例；紧接着说明其版画来源。"),
        source("20", "407", "20_CHP-20Postscript.md", "168", "evidently carefully devised commission for a series of fantasising overdoors depicting sixteenth-century buildings and monuments has been analysed by William Barcham", "后记将系列概括为 Smith 宣扬帕拉第奥建筑原则的精心设计委托，并提到 Barcham 的分析；该研究未在本轮独立查阅。"),
    ],
    "process_note": "cand-9251 是跨第10章 pp.308–309 与第20章后记 p.407 的 new work 组，group=workgrp-40fe5d001d7c1f。第10章先记 Canaletto 于1744年绘制十三幅门上画，后记 Canaletto 离开后由 Visentini 延续同一系列，并由 Zuccarelli 为建筑画增加装饰风景；第10章另列后续十一幅画的建筑师来源。系列 KU 保存总体委托身份与分阶段贡献，但不把十三幅及十一幅并成一个件数或单作。第20章提及的 Barcham 文章没有独立阅读；文献候选 cand-11099 仍属独立 archive 对象，不把引用当作已核研究证据。相邻索引候选 cand-2785、cand-2883 缺少已裁决的独立作品身份，cand-2453 缺少可连接的 S2 委托事件身份，均保留原 undecided 决定和待证去向。11条直接 S2 断言中8条关系候选留待 S6，本次不登记正式关系。",
    "result_note": "cand-9251 登记至史密斯帕拉第奥式门上画系列 KU。跨章记录 1744 年 Canaletto 的十三幅门上画与1746年后 Visentini、Zuccarelli 延续系列的不同阶段，以及 Haskell 对委托意图的概括；不生成逐件清单或系列总数。cand-2785、cand-2883、cand-2453 与 Barcham 文献对象 cand-11099 均按各自 S3 身份边界处理，不并入本卡。",
})

BATCHES["work"].append({
    "group": "workgrp-e4dc131e4ac24c",
    "members": ["cand-6307"],
    "slug": "bernini-colonnade-st-peters-square",
    "name_zh": "贝尼尼圣彼得广场柱廊",
    "name_en": "Bernini’s Colonnade at St Peter’s Square",
    "description_zh": "Haskell 称 Bernini 在圣彼得大教堂外建造了大型柱廊，并描述其向外环抱广场。原书还转述了威尼斯使节对柱廊费用的观察、Niccolò Sagredo 于1661年关于工程约完成一半且预计三年后完成的估计，以及 Giacomo Querini 对柱廊的政治性批评。本卡记录建筑作品及这些带来源限定的叙述，不推定准确施工年月或实际竣工状态。",
    "description_en": "Haskell says Bernini built a great colonnade outside St Peter’s that stretches out to embrace the square. He also reports Venetian ambassadors’ observations on its expense, Niccolò Sagredo’s 1661 estimate that the work was about half finished with three years to go, and Giacomo Querini’s political criticism of the porticos. This unit records the architectural work and these attributed accounts without inferring exact construction dates or completion status.",
    "facts_zh": "- 对象类型：围绕圣彼得广场展开的柱廊建筑作品；本卡不把广场或圣彼得大教堂合并为作品组成部分。\n- 作者归属与位置：Haskell 将柱廊归于 Bernini，称其建于教堂外并延伸环抱广场。\n- 工程进度报告：Niccolò Sagredo 转述的1661年估计称工程约完成一半，预计三年后完成；这是当时的估计，不是竣工记录。\n- 费用与政治评价：Haskell 称威尼斯使节注意到 Bernini 柱廊的巨大开支；Giacomo Querini 后来批评圣彼得柱廊和其建筑政策，称三百根柱子按椭圆形布局形成教堂的建筑界域，并预测对 Leonine City、Vatican 及 conclave 会造成影响。后几项均记录为 Querini 的预测和论辩，不当作实际后果。",
    "facts_en": "- Object type: an architectural colonnade extending around St Peter’s Square; the square and St Peter’s Basilica are not merged into the work.\n- Attribution and location: Haskell attributes the colonnade to Bernini and says it was built outside the church, stretching out to embrace the square.\n- Reported progress: an estimate relayed by Niccolò Sagredo in 1661 put the work at about half complete, with three years remaining. This is a contemporary estimate, not a completion record.\n- Expense and political criticism: Haskell says Venetian ambassadors noticed the ruinous expense of Bernini’s portico. Giacomo Querini later criticized the colonnades and papal building policy, describing three hundred columns in an oval arrangement as an architectural precinct for the church and predicting effects on the Leonine City, the Vatican, and conclaves. These are recorded as Querini’s arguments and predictions, not established outcomes.",
    "boundary_zh": "本卡是柱廊建筑作品；圣彼得广场 cand-6308、圣彼得大教堂 cand-5696 及 Vatican、Leonine City 等地点保持独立。Cand-11982“威尼斯使节”是未具名群体，cand-11987 是 Querini 预测中可能举行的教宗选举；二者仍按 S3 undecided 待身份审查，不因本卡关系语境而升级。关于费用、列柱数量、工程进度和政治后果均保留原文的发言者与限定。",
    "boundary_en": "This unit is the architectural colonnade. St Peter’s Square candidate cand-6308, St Peter’s Basilica candidate cand-5696, and places such as the Vatican and Leonine City remain distinct. Candidate cand-11982, the unnamed Venetian ambassadors, and cand-11987, a hypothetical papal conclave in Querini’s prediction, remain S3 undecided for identity review; their appearance in this account does not resolve them. Reports about expense, column count, progress, and political consequences retain their original speakers and qualifications.",
    "sources": [
        source("6", "151", "06_CHP-6_sec_i.md", "66", "built the huge colonnade which stretches out to embrace the square", "第6章将教堂外环抱广场的大型柱廊归于 Bernini。"),
        source("6", "152", "06_CHP-6_sec_i.md", "71", "It is estimated that the work is about half way through and that in three years it will be complete.", "Niccolò Sagredo 转述1661年对工程进度的估计；不是完成记录。"),
        source("6", "152", "06_CHP-6_sec_i.md", "72–73", "The three hundred columns, arranged according to an oval plan, merely serve as an architectural precinct for the marvellous church of the Prince of the Apostles.", "Giacomo Querini 将柱廊描述为教堂的建筑界域；此处作为其引语保存。"),
    ],
    "process_note": "cand-6307 为 workgrp-e4dc131e4ac24c 的单候选 new 组，正文锚点跨第6章 pp.151–153。Haskell 明确称 Bernini 在圣彼得大教堂外建造环抱广场的柱廊；第152页转述 Sagredo 于1661年的半途及三年工期估计，并引 Querini 对三百柱、椭圆布局和建筑政策的批评。卡片保留发言者，未把估计变为实际竣工事实，未把 Querini 的预测写成后果。广场 cand-6308、大教堂 cand-5696、Vatican 与 Leonine City 保持地点端点边界。11条候选关联中8条关系候选留待 S6；cand-11982 与 cand-11987 仍为 undecided，不借关系语境强行裁决。",
    "result_note": "cand-6307 登记为贝尼尼圣彼得广场柱廊 KU。卡片记录 Haskell 对作品归属和位置的叙述、Sagredo 于1661年的工程进度估计及 Querini 的政治批评，并保留其发言者和不确定性。广场、教堂及预测涉及地点与事件保持独立；8条关系候选留待 S6，cand-11982 和 cand-11987 仍待 S3 身份审查。",
})

BATCHES["work"].append({
    "group": "workgrp-d2f152b9c3608e",
    "members": ["cand-5022"],
    "slug": "fiammeri-s-vitale-martyrdom-frescoes",
    "name_zh": "圣维塔莱堂早期基督教殉道题材壁画组",
    "name_en": "Early Christian Martyrdom Frescoes at S. Vitale",
    "description_zh": "Haskell 记述圣维塔莱堂以早期基督教殉道者受刑为主题的一组壁画：Jesuit 画家 Giovanni Battista Fiammeri 负责装饰，Claudio Aquaviva 总会长直接监督并参与构思。壁画多以田园景致呈现酷刑场面，唱诗班区域则更直接描绘施刑过程。后记又转述 Thomas Buser 对这些壁画及其可能“古代感”风格来源的讨论。本卡登记绘画组，不指教堂空间或其中任何单幅场景。",
    "description_en": "Haskell describes a group of frescoes at S. Vitale depicting the tortures of early Christian martyrs. The Jesuit painter Giovanni Battista Fiammeri directed the decoration under the immediate control of Superior General Claudio Aquaviva, who took a personal interest and offered suggestions. Most scenes presented torture within pastoral landscapes, while those in the choir showed the mechanisms more directly. The postscript also reports Thomas Buser’s discussion of the frescoes and the possible sources of their “antique” style. This unit is the group of paintings, not the church space or an individual scene.",
    "facts_zh": "- 对象类型：圣维塔莱堂内一组以早期基督教殉道者受刑为主题的壁画；原书未给出确切绘制、完成日期或逐幅清单。\n- 装饰统筹：Haskell 称 Jesuit 画家 Giovanni Battista Fiammeri 负责装饰，Claudio Aquaviva 总会长直接监督，对方案有强烈个人兴趣并提出建议。\n- 题材与呈现：受刑是主要题材；一般画面以牧歌式风景表现酷刑，观看者需结合画面和题铭辨认受难者。唱诗班中的画家被鼓励减少克制，更直接展示施刑方式。\n- 归属限定：Haskell 说这些作品在19世纪曾被归于 Gaspard Poussin；本卡不将此历史误归属当作认可归属。\n- 后记讨论：Haskell 转述 Thomas Buser 对 S. Vitale“牧歌式”酷刑场景的评论，并报告 Buser 推测其风格可能受罗马壁画启发、意在营造古代感；这是被转述的解释，不是本轮独立核验的结论。",
    "facts_en": "- Object type: a group of frescoes at S. Vitale depicting the tortures of early Christian martyrs; Haskell supplies no exact production or completion dates and no itemized list.\n- Direction: Haskell says the Jesuit painter Giovanni Battista Fiammeri directed the decoration under the immediate control of Superior General Claudio Aquaviva, who took a strong personal interest and made suggestions.\n- Subjects and presentation: torture predominates. The scenes often place it in pastoral landscapes, with inscriptions helping identify the victims; in the choir, painters were encouraged to show the mechanisms of torture more directly.\n- Attribution qualification: Haskell says the works were attributed to Gaspard Poussin in the nineteenth century; this historical misattribution is not adopted as the card’s attribution.\n- Postscript discussion: Haskell reports Thomas Buser’s comments on the “pastoral” torture scenes and his suggestion that their style may have been influenced by Roman wall painting to give the victims’ suffering an antique feeling. This is a reported interpretation, not independently verified here.",
    "boundary_zh": "本卡是壁画组，不是圣维塔莱堂建筑、唱诗班空间 cand-5023 或单幅殉道场景；第3章的作品与第20章后记对该组壁画的评论相互指认，但不因此添加逐幅作品。圣斯德望圆厅 Circignani 壁画是原书用于比较的前一组作品，不与本组合并。Thomas Buser 为独立人物端点，后记所转述的论述不等于已查阅其1976年文章。",
    "boundary_en": "This unit is the fresco group, not the church building, the choir space candidate cand-5023, or any individual martyrdom scene. Chapter 3’s account and the postscript’s later comments refer to the same S. Vitale frescoes, but do not supply an itemized list. Circignani’s earlier frescoes at S. Stefano Rotondo are a separate comparison and are not merged here. Thomas Buser remains a distinct person endpoint; Haskell’s report of his interpretation does not mean that his 1976 article was consulted directly.",
    "sources": [
        source("3", "67", "03_CHP-3_sec_ii.md", "25–27", "The decoration was directed by a Jesuit painter Giovanni Battista Fiammeri under the immediate control of the General, Claudio Aquaviva, who took a strong personal interest in the scheme and made suggestions of his own.", "第3章交代壁画装饰的统筹者、Jesuit 总会长监督及其参与程度。"),
        source("3", "67", "03_CHP-3_sec_ii.md", "26–27", "Once again the subjects were almost exclusively concerned with torture", "第3章概括 S. Vitale 壁画以酷刑为主的题材，并说明一般画面呈牧歌式景观。"),
        source("3", "67", "03_CHP-3_sec_ii.md", "27", "Only in the choir were the painters encouraged to throw off their restraint", "第3章说明唱诗班区域的画作更直接展示施刑方式。"),
        source("20", "399", "20_CHP-20Postscript.md", "41–42", "episodes of torture depicted in the church of S. Vitale", "后记再次指认 S. Vitale 壁画，并转述 Buser 对其“牧歌式”酷刑场景和古代感风格来源的解释。"),
    ],
    "process_note": "cand-5022 是跨第3章 p.67 与第20章后记 p.399 的 new work 组，group=workgrp-d2f152b9c3608e。第3章说明 Fiammeri 统筹、Aquaviva 直接监督并参与、壁画以酷刑为主要题材且唱诗班场景更直接；后记的“牧歌式”场景与风格来源讨论回指同一组 S. Vitale 壁画。卡片不混入 S. Stefano Rotondo 的 Circignani 壁画，不把第19世纪的 Gaspard Poussin 归属误说成作者确认。Buser 的判断仍是 Haskell 对其研究的转述。9条直接 S2 断言中8条关系候选留待 S6；圣维塔莱唱诗班 cand-5023 保持独立 place KU。",
    "result_note": "cand-5022 登记至圣维塔莱堂早期基督教殉道题材壁画组 KU，跨章汇合第3章的创作、监督与场景描述及后记对同组壁画的评论。保留未给精确日期、19世纪误归属、Buser 解释为转述等限定；不与唱诗班地点、单幅图像或圣斯德望圆厅壁画合并。8条关系候选留待 S6。",
})

BATCHES["work"].append({
    "group": "workgrp-b9528b8c029410",
    "members": ["cand-5373"],
    "slug": "pozzo-fresco-cycle-tribune-apse-s-ignazio",
    "name_zh": "波佐圣依纳爵堂祭坛区与后殿壁画组",
    "name_en": "Pozzo’s Fresco Cycle in the Tribune and Apse of S. Ignazio",
    "description_zh": "Haskell 称 Andrea Pozzo 在1685年后若干年间于圣依纳爵堂的 tribune 与 apse 绘制壁画，表现耶稣会早期历史中的重要事件，并以基督在 La Storta 向圣依纳爵作出的应许为高潮。本卡记录这组叙事壁画及 Haskell 对其风格的评价，不并入同堂另一项拱顶壁画。",
    "description_en": "Haskell says Andrea Pozzo painted frescoes in the tribune and apse of S. Ignazio some years after 1685. They represented principal events in the Society’s early history and culminated in Christ’s promise to St Ignatius at La Storta. This unit records that narrative cycle and Haskell’s stylistic assessment, separately from another fresco on the church vault.",
    "facts_zh": "- 对象类型：圣依纳爵堂 tribune 与 apse 内的一组叙事壁画；原书将两处空间分别列出，但本卡只登记壁画组。\n- 作者与年代：Haskell 将壁画归于 Andrea Pozzo，称其在1685年后若干年间绘制；未给出确切开工或完工年份。\n- 题材：表现耶稣会早期历史中的若干主要事件，并以基督在 La Storta 向圣依纳爵作出的应许为叙事高潮。\n- 风格评价：Haskell 认为这些作品在题材与处理上均不同于耶稣堂 Gaulli 壁画，某些方面标志着对 Baroque 的反动；这是作者的风格史判断。",
    "facts_en": "- Object type: a narrative fresco group in the tribune and apse of S. Ignazio. Haskell names the two spaces separately; this card records the paintings, not the rooms.\n- Attribution and date: Haskell attributes the frescoes to Andrea Pozzo and dates them to some years after 1685; he gives no exact start or completion year.\n- Subject: the pictures represent principal events in the early history of the Society and culminate in Christ’s promise to St Ignatius at La Storta.\n- Stylistic assessment: Haskell says they differ in subject and treatment from Gaulli’s frescoes in the Gesù and, in some ways, mark a reaction against the Baroque. This is the author’s art-historical judgment.",
    "boundary_zh": "本卡是 tribune 与 apse 中的壁画组，不是这两处建筑空间。既有[圣依纳爵堂拱顶壁画](pozzo-fresco-vault-s-ignazio.md)及其模型[波佐圣依纳爵堂拱顶壁画模型](andrea-pozzo-modello-for-fresco-on-vault-of-s-ignazio.md)属于不同作品及媒介，不并入本组；Gaulli 在耶稣堂的壁画亦为比较对象。La Storta 应许属于画面叙事内容；本卡不把其地点、基督显现或圣依纳爵另行折入作品身份。",
    "boundary_en": "This unit is the fresco group in the tribune and apse, not those architectural spaces. The existing [Fresco on the Vault of S. Ignazio](pozzo-fresco-vault-s-ignazio.md) and [Pozzo’s modello for the vault fresco](andrea-pozzo-modello-for-fresco-on-vault-of-s-ignazio.md) are different works and media and are not included; Gaulli’s Gesù frescoes are a comparison. The La Storta promise is narrative content and does not merge its place, Christ’s apparition, or St Ignatius into the identity of this work.",
    "sources": [
        source("3", "89", "03_CHP-3_sec_iv.md", "138–140", "For some years after 1685 Pozzo painted frescoes in the tribune and the apse", "第3章为该组壁画给出“1685年后若干年”的宽泛时间及两处绘制空间。"),
        source("3", "89–90", "03_CHP-3_sec_iv.md", "138–142", "representing there some of the principal events in the early history of the Society, culminating", "第3章概述壁画题材及叙事高潮。"),
        source("3", "90", "03_CHP-3_sec_iv.md", "142", "they lack both the theological complexity", "第3章比较该组壁画与 Gaulli 耶稣堂壁画在题材和处理上的区别。"),
        source("3", "90", "03_CHP-3_sec_iv.md", "142", "In some ways they mark a reaction against the Baroque", "Haskell 对该组壁画风格史意义的判断。"),
    ],
    "process_note": "cand-5373 为 workgrp-b9528b8c029410 单候选 new 组。第3章 pp.89–90 将 Pozzo 在 S. Ignazio 的工作分为不同项目：早先拱顶画另有 cand-5074，已登记为 `units/works/pozzo-fresco-vault-s-ignazio`；拱顶画的 modèle cand-4002 亦已有独立 KU。cand-5373 指 p.89 所称1685年后若干年间绘于 tribune 与 apse 的叙事壁画组，题材为耶稣会早期事件并以 La Storta 应许为高潮，因此登记新作品身份，不复用拱顶卡。Haskell 对其与 Gaulli 的比较及“反 Baroque”判断按作者意见记录。9条直接 S2 断言中8条关系候选留待 S6；场所和叙事端点不并入。",
    "result_note": "cand-5373 登记为波佐圣依纳爵堂祭坛区与后殿壁画组 KU，记录 Haskell 所载宽泛年代、叙事题材及风格判断。与既有同堂拱顶壁画及其模型分开；tribune 空间、apse 空间和 La Storta 叙事端点不并入作品身份。8条关系候选留待 S6。",
})

BATCHES["work"].append({
    "group": "workgrp-49e44482856548",
    "members": ["cand-4248"],
    "slug": "titian-worship-of-venus",
    "name_zh": "提香《维纳斯崇拜》",
    "name_en": "Titian’s Worship of Venus",
    "description_zh": "Haskell 记载提香《维纳斯崇拜》曾是费拉拉埃斯特家族艺术收藏的一部分，并于1598年前后由 Aldobrandini 枢机带回罗马；1637年又被送往西班牙。第2章叙述其在罗马的接受，第4章记录版画传播及 Padovanino 前往临摹。本卡只登记提香原作，相关临摹、后出版本和其他提香画作另行区分。",
    "description_en": "Haskell reports that Titian’s Worship of Venus belonged to the Este art collection at Ferrara, was brought to Rome by Cardinal Aldobrandini around 1598, and was sent to Spain in 1637. Chapter 2 discusses its reception in Rome; Chapter 4 records the print after it and Padovanino’s journey to copy it. This unit records Titian’s painting alone, distinct from copies, later versions, and other Titian works.",
    "facts_zh": "- 对象类型：提香《维纳斯崇拜》绘画原作；此处采用第4章正确拼写的作品名。第2章相应 OCR 将 Venus 误读为“os”，不沿用该误字。\n- 收藏与转移：Haskell 将其列为16世纪末从埃斯特家族艺术收藏中被带离的作品之一，称 Aldobrandini 枢机将它与另外两幅提香画一并带回罗马。\n- 罗马接受：Haskell 称这些画在罗马一度少有人注意，直到 Maffeo Barberini 成为教宗近四分之一世纪后，才帮助奠定一种全新艺术风格的基础；这是作者对接受史的评价。\n- 后续流转与传播：第4章称该画于1637年送往西班牙；Andrea Podesta 为 Cassiano dal Pozzo 制作并题献一幅取自该画的版画，Alessandro Varotari（Padovanino）前往罗马临摹。\n- 复制史的限定：第2章注释提到 d’Arpino 曾复制相关画作、Albani 可能研究过它们；John Walker 认为 Rubens 不太可能在罗马访问期间复制《维纳斯崇拜》，其斯德哥尔摩版本年代更晚，可能依据另一位艺术家的复制品。保留注释范围与作者转述，不据此补定作品版本链。",
    "facts_en": "- Object type: Titian’s original painting, titled Worship of Venus here following the correctly spelled title in Chapter 4. Chapter 2’s OCR renders Venus as “os”; the OCR error is not adopted.\n- Collection and transfer: Haskell includes it among the Este art treasures removed from Ferrara and says Cardinal Aldobrandini brought it to Rome with two other Titian paintings.\n- Reception in Rome: Haskell says the paintings attracted little attention there until nearly a quarter century later, when Maffeo Barberini became Pope; he judges that they then helped lay the foundations for a wholly new artistic style.\n- Later movement and circulation: Chapter 4 says the painting was sent to Spain in 1637. Andrea Podesta dedicated to Cassiano dal Pozzo a print taken from it, and Alessandro Varotari (Padovanino) travelled to Rome to copy it.\n- Copying qualification: Chapter 2’s note says d’Arpino copied the paintings and Albani must have studied them; John Walker considered it unlikely that Rubens copied the Worship of Venus during his visit to Rome. His Stockholm versions were much later and probably derived from another artist’s copies. The note’s qualifications are retained, and no complete version history is inferred.",
    "boundary_zh": "本卡只指提香原作。与同批带回罗马的《安德里安人》和《巴克斯与阿里阿德涅》分开；d’Arpino 的临摹、Albani 的研究、Rubens 后出的斯德哥尔摩版本及 Podesta 版画均为各自对象，不合并为原作。Haskell 注释中的复数代词不据此断言每条复制史都只对应本画。接受史与版画关系候选留待 S6逐条核验。",
    "boundary_en": "This unit is Titian’s original painting alone. It remains distinct from The Andrians and Bacchus and Ariadne, which were brought to Rome with it; from d’Arpino’s copies and Albani’s study; from Rubens’s later Stockholm versions; and from Podesta’s print. The plural references in Haskell’s note are not used to claim that every copying statement applies exclusively to this painting. Reception and print-related relation candidates remain for S6 review.",
    "sources": [
        source("2", "25", "02_CHP-2_sec_i.md", "50", "brought with him back to Rome were Titian", "第2章将该画与另外两幅提香作品一并列入 Aldobrandini 枢机从费拉拉带回罗马的埃斯特藏画。"),
        source("2", "25", "02_CHP-2_sec_i.md", "50", "these pictures attracted little attention in Rome until Maffeo Barberini himself became Pope", "第2章讨论三幅提香画在罗马的接受及后续艺术史评价。"),
        source("2", "31", "02_CHP-2_sec_i.md", "129", "copied them", "第2章注释转述 d’Arpino、Albani 与 Rubens 相关复制史判断及限定。"),
        source("4", "105", "04_CHP-4_sec_ii.md", "83–84", "when that picture was sent to Spain in 1637", "第4章记录作品于1637年送往西班牙，并接续记载 Podesta 版画和 Padovanino 临摹。"),
    ],
    "process_note": "cand-4248 为 workgrp-49e44482856548 单候选 new 组，跨第2章 pp.25、31 与第4章 p.105。第2章记 Aldobrandini 将提香《维纳斯崇拜》与另外两幅作品从费拉拉带至罗马，并讨论其接受；注释对 d’Arpino、Albani、Rubens 的复制关系使用复数范围和 Walker 的限定。第4章确认正确标题拼写，记该画于1637年送往西班牙及版画和 Padovanino 临摹。原作、其他两画、复制品、后出版本和版画均保持边界；不依据注释推导逐件版本谱系。9条直接 S2 断言中8条关系候选留待 S6。",
    "result_note": "cand-4248 登记为提香《维纳斯崇拜》KU，连接第2章费拉拉—罗马及接受史叙述与第4章1637年送往西班牙、版画传播和 Padovanino 临摹的记载。原作与其他提香作品、临摹、后出版本及版画分开；8条关系候选留待 S6核验。",
})

BATCHES["place"].extend([
    {
        "group": "sg3-place-cand-5236",
        "members": ["cand-5236"],
        "slug": "gesu-chapel-st-ignatius",
        "name_zh": "耶稣堂圣依纳爵礼拜堂",
        "name_en": "Chapel of St Ignatius in the Gesù",
        "description_zh": "本书将耶稣堂圣依纳爵礼拜堂列为 Gaulli 拱顶装饰工程覆盖的内部空间之一；后文又叙述画家于1685年完成耶稣堂左横翼、圣依纳爵祭坛上方的绘画。本卡登记礼拜堂空间，不将其与祭坛或绘画合并。",
        "description_en": "Haskell names the Chapel of St Ignatius as one of the internal spaces beneath the transept vaults included in Gaulli’s decoration commission. He later says that in 1685 Gaulli completed work in the Gesù’s left transept above the altar of St Ignatius. This unit records the chapel separately from its altar and paintings.",
        "facts_zh": "- 地点性质：耶稣堂内部礼拜堂。\\n- 所在建筑：罗马 Gesù 教堂；本卡不复写建筑卡的基本信息。\\n- 空间语境：第3章将圣依纳爵与圣方济各·沙勿略礼拜堂列在耶稣堂横翼拱顶之下；后文提及左横翼圣依纳爵祭坛上方的绘画。\\n- 原书没有在此为礼拜堂给出独立的建成年份或完整空间测绘。",
        "facts_en": "- Place type: an internal chapel within the Gesù.\\n- Parent building: the Gesù in Rome; this card does not duplicate the church card’s general description.\\n- Spatial context: Chapter 3 names the chapels of St Ignatius and St Francis Xavier beneath the Gesù’s transept vaults and later mentions painting above the altar of St Ignatius in the left transept.\\n- The cited passages do not provide a separate construction date or complete architectural survey.",
        "boundary_zh": "本卡为礼拜堂建筑空间，不是其祭坛、祭坛画或拱顶绘画；不与耶稣堂建筑本体合并，也不与另一座 S. Ignazio 教堂的圣依纳爵礼拜堂混为一处。",
        "boundary_en": "This unit is the chapel space, not its altar, altarpiece, or vault paintings. It remains distinct from the Gesù church building as a whole and from the chapel of St Ignatius at the separate church of S. Ignazio.",
        "sources": [
            source("3", "80", "03_CHP-3_sec_iv.md", "42–43", "the vaults of the transepts above the chapels of St Ignatius and St Francis Xavier", "Gaulli 的委托范围包括耶稣堂圣依纳爵与圣方济各·沙勿略礼拜堂上方的横翼拱顶。"),
            source("3", "81", "03_CHP-3_sec_iv.md", "49", "Finally in 1685 he completed his work in the church by painting the left transept above the altar of St Ignatius", "第3章称 Gaulli 于1685年完成耶稣堂左横翼圣依纳爵祭坛上方的绘画。"),
        ],
        "process_note": "cand-5236 保持为耶稣堂内圣依纳爵礼拜堂的独立 place 组。第3章 p.80 将其与圣方济各·沙勿略礼拜堂并列于 Gaulli 横翼拱顶工程范围，p.81 后文提到左横翼圣依纳爵祭坛上方的绘画。它与 Gesù 教堂本体、祭坛及绘画分开，也与 S. Ignazio 教堂中的同名空间分开。",
        "result_note": "cand-5236 登记为耶稣堂圣依纳爵礼拜堂地点 KU，记录其为耶稣堂内部空间并与祭坛、绘画和另一座 S. Ignazio 教堂区分。",
    },
    {
        "group": "sg3-place-cand-5300",
        "members": ["cand-5237", "cand-5300"],
        "slug": "gesu-right-transept-chapel-st-francis-xavier",
        "name_zh": "耶稣堂右横翼圣方济各·沙勿略礼拜堂",
        "name_en": "Right-Transept Chapel of St Francis Xavier in the Gesù",
        "description_zh": "本书先在 Gaulli 委托范围中提及耶稣堂圣方济各·沙勿略礼拜堂，后说明右横翼礼拜堂先后奉献于救世主、复活和圣方济各·沙勿略。两处指向同一右横翼礼拜堂；本卡登记建筑空间及其奉献沿革，不混同祭坛画或独立绘画。",
        "description_en": "Haskell first names the Chapel of St Francis Xavier in the Gesù among the spaces beneath Gaulli’s transept vaults, then describes a right-transept chapel successively dedicated to the Saviour, the Resurrection, and St Francis Xavier. The passages identify the same chapel; this unit records the space and its dedication history separately from altarpieces and paintings.",
        "facts_zh": "- 地点性质：耶稣堂右横翼内部礼拜堂。\\n- 奉献沿革：原奉献于救世主，后改奉复活；1623年圣方济各·沙勿略列圣后改奉该圣人。\\n- 早期陈设：第3章称 Baglione 于1602年为此礼拜堂绘制祭坛画，并称礼拜堂内曾置一幅 Van Dyck 绘制的圣人像；作品各自保持独立对象。\\n- 后续 patronage：本书称 Monsignor Negroni 于17世纪60年代后期取得礼拜堂赞助权，并强调他对本礼拜堂装饰的主张。",
        "facts_en": "- Place type: an internal chapel in the right transept of the Gesù.\\n- Dedication history: first dedicated to the Saviour, then to the Resurrection, and after St Francis Xavier’s canonization in 1623 to that saint.\\n- Earlier furnishings: Haskell says Baglione painted an altarpiece for the chapel in 1602 and that a picture of the saint by Van Dyck was placed there; each work remains a separate object.\\n- Later patronage: Haskell says Monsignor Negroni acquired the chapel’s patronage in the late 1660s and asserted authority over its decoration.",
        "boundary_zh": "cand-5237 的 Gaulli 合约段与 cand-5300 的奉献沿革段指同一礼拜堂，合为一张地点 KU。礼拜堂不是耶稣堂本体、祭坛、Baglione 或 Van Dyck 作品；不与 S. Andrea al Quirinale 的圣方济各·沙勿略礼拜堂合并。",
        "boundary_en": "Candidate cand-5237’s Gaulli-commission passage and cand-5300’s dedication history refer to the same chapel and share one place KU. The chapel is distinct from the Gesù building, its altar, and works by Baglione or Van Dyck; it is also distinct from the Chapel of St Francis Xavier at S. Andrea al Quirinale.",
        "sources": [
            source("3", "80", "03_CHP-3_sec_iv.md", "42–43", "the vaults of the transepts above the chapels of St Ignatius and St Francis Xavier", "Gaulli 的工程范围同时点名耶稣堂圣方济各·沙勿略礼拜堂。"),
            source("3", "84", "03_CHP-3_sec_iv.md", "79–80", "The chapel, in the right transept was one of the only ones that long remained exclusively under Jesuit patronage.", "第3章定位右横翼礼拜堂，并接续说明其奉献对象及1602年 Baglione 祭坛画。"),
            source("3", "84", "03_CHP-3_sec_iv.md", "79–80", "On his canonisation in 1623 the chapel was dedicated to St Francis Xavier", "第3章称圣方济各·沙勿略于1623年列圣后，该礼拜堂改奉此圣人。"),
            source("3", "85", "03_CHP-3_sec_iv.md", "87–89", "the chapel of St Francis Xavier was decorated by another artist after giving rise to further difficulties", "第3章将圣方济各·沙勿略礼拜堂与同教堂圣依纳爵礼拜堂的后续装饰分开叙述。"),
        ],
        "process_note": "cand-5237 与 cand-5300 现共组 sg3-place-cand-5300。第3章 p.80 的 Gaulli 合约称横翼拱顶位于 St Ignatius 与 St Francis Xavier 礼拜堂之上；p.84 记右横翼礼拜堂从救世主、复活到1623年改奉圣方济各·沙勿略的连续沿革，表明两候选是同一地点在不同段落中的名称锚点。Baglione 祭坛画与 Van Dyck 圣人像保持为作品端点；S. Andrea al Quirinale 的同名礼拜堂不并入。",
        "result_note": "cand-5237 与 cand-5300 共映射至耶稣堂右横翼圣方济各·沙勿略礼拜堂 KU。卡片保留其奉献沿革及与祭坛、绘画、耶稣堂本体和 S. Andrea al Quirinale 同名礼拜堂的身份边界。",
    },
])


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def group_of(row):
    m = re.search(r"group=([^;| ]+)", row.get("resolution_note", ""))
    return m.group(1) if m else ""


def rel_stats(members, statements):
    direct = [s for s in statements if s.get("subject_candidate_id") in members or s.get("object_candidate_id") in members]
    return len(direct), sum(bool(s.get("qualifiers", {}).get("relation_candidate")) for s in direct)


def card(record, kind):
    source_rows = []
    for item in record["sources"]:
        loc = f"第{item['chapter']}章，印刷页{item['page']}；OCR L{item['lines']}"
        if item.get("note"):
            loc += f"；{item['note']}"
        source_rows.append({
            "citation": BOOK_CITATION,
            "location": loc,
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": f"lines {item['lines']}; print pp. {item['page']}",
            },
        })
    frontmatter = {
        "title": f"{record['name_zh']}（{record['name_en']}）",
        "name_en": record["name_en"],
        "type": kind,
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    kind_label = {"work": "作品信息", "event": "事件信息", "place": "地点信息"}[kind]
    return (
        f"---\n{fm}---\n\n## 内容\n\n### 描述\n\n**中文：** {record['description_zh']}\n\n"
        f"**English:** {record['description_en']}\n\n### 名称\n\n中文显示名及英文显示名见卡片标题；中文名为描述性工作译名，非原书正式题名。\n\n"
        f"The bilingual display names appear in the card title; the Chinese name is a descriptive working title, not a formal title from the book.\n\n"
        f"### {kind_label}\n\n{record['facts_zh']}\n\n{record['facts_en']}\n\n### 身份边界\n\n中文：{record['boundary_zh']}\n\n"
        f"English: {record['boundary_en']}\n\n## 关系与证据\n\n当前没有登记正式关系。S2 中有据的相关关系候选仍待 S6 按端点、方向、语境和证据逐条审查。\n"
    )


def main():
    parser = argparse.ArgumentParser(description="Register supported cross-chapter S4 direct-endpoint identity groups.")
    parser.add_argument("--type", choices=sorted(BATCHES), required=True)
    parser.add_argument("--group", help="Optionally run one identity group from the selected type.")
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
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    alignment_by_id = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    assert len(alignment_by_id) == len(candidate_by_id)
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    statements = read_jsonl(STATEMENT_PATH)
    manifest_ids = {r["ku_id"] for r in manifest}
    manifest_paths = {r["card_path"] for r in manifest}
    groups = defaultdict(list)
    for row in alignment_by_id.values():
        if row.get("decision") == "new":
            group = group_of(row)
            assert group, row["candidate_id"]
            groups[group].append(row)

    planned_alignment = [dict(r) for r in alignments]
    planned_by_id = {r["candidate_id"]: r for r in planned_alignment if r.get("candidate_id") and not r.get("external_source")}
    planned_manifest = list(manifest)
    accepted_lines = accepted.splitlines()
    total_direct = total_relations = 0
    cards = []
    process_details, result_details = [], []
    for record in batch:
        members = set(record["members"])
        assert {r["candidate_id"] for r in groups.get(record["group"], [])} == members, (record["group"], members)
        for cid in members:
            candidate = candidate_by_id[cid]
            row = planned_by_id[cid]
            assert candidate.get("suggested_type") == kind and row.get("decision") == "new" and not row.get("ku_id"), cid
            assert group_of(row) == record["group"]
        slug = record["slug"]
        relative_path = f"04-knowledge/units/{KIND_DIRS[kind]}/{slug}.md"
        ku_id = f"units/{KIND_DIRS[kind]}/{slug}"
        assert not (ROOT / relative_path).exists() and relative_path not in manifest_paths and relative_path not in accepted
        assert ku_id not in manifest_ids
        for r in manifest:
            if r.get("type") == kind:
                title = f"{record['name_zh']}（{record['name_en']}）"
                assert r.get("canonical_name") != record["name_zh"] and r.get("name_en") != record["name_en"] and title not in (r.get("canonical_name", "") + r.get("name_en", ""))
        for item in record["sources"]:
            path = ROOT / "02-sources" / "02-Markdown" / item["file"]
            text = " ".join(path.read_text(encoding="utf-8-sig").split())
            assert " ".join(item["quote"].split()) in text, (item["file"], item["lines"], item["quote"])
        for cid in members:
            planned_by_id[cid]["ku_id"] = ku_id
            planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {record['group']} to {ku_id}."
        planned_manifest.append({"ku_id": ku_id, "type": kind, "canonical_name": record["name_zh"], "name_en": record["name_en"], "source_task": TASK, "card_path": relative_path})
        direct, rel = rel_stats(members, statements)
        total_direct += direct
        total_relations += rel
        cards.append((ROOT / relative_path, relative_path, ku_id, card(record, kind)))
        process_details.append(f"- `{','.join(record['members'])}` → `{record['group']}` → `{ku_id}`；{direct} 条直接 S2 断言，其中 {rel} 条关系候选留待 S6。{record['process_note']}")
        result_details.append(f"- {record['result_note']}")

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    kind_label = "作品" if kind == "work" else "事件"
    process_text += (
        f"\n\n### S4 {kind}：跨章直接端点身份组登记（{DATE}）\n\n"
        + "\n".join(process_details)
        + f"\n\n本批新增{len(batch)}张{kind_label} KU，每个 S3 new 身份组一张；卡片保存双语描述及精确书内引文。"
        "不将关系候选升级为正式关系，也未开展 S5 外部补足。"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    result_text += (
        f"\n\n### S4 {kind}：跨章直接端点身份组登记（{DATE}）\n\n"
        + "\n".join(result_details)
        + f"\n\n新增{len(batch)}张{kind_label} KU、{sum(len(r['members']) for r in batch)}条候选映射；本批直接 S2 断言{total_direct}条，其中{total_relations}条关系候选留待 S6。"
        "未新增正式关系或开展 S5 外部补足。"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    if args.dry_run:
        print(f"S4 {kind} dry-run passed")
        for record, (_, relative_path, ku_id, _) in zip(batch, cards):
            print(f"  {','.join(record['members'])} -> {record['group']} -> {ku_id} ({relative_path})")
        print(f"  source quotations checked={sum(len(r['sources']) for r in batch)}; direct statements={total_direct}; relation candidates pending={total_relations}")
        print(f"  manifest={len(manifest)} -> {len(planned_manifest)}; registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}")
        return 0

    for path, _, _, text in cards:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8-sig", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    new_paths = sorted(item[1] for item in cards)
    for relative_path in new_paths:
        insert_at = next((i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > relative_path), next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)))
        accepted_lines.insert(insert_at, f"- {relative_path}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"S4 {kind} batch applied: {len(batch)} groups, {sum(len(r['members']) for r in batch)} candidate mappings")


if __name__ == "__main__":
    raise SystemExit(main())
