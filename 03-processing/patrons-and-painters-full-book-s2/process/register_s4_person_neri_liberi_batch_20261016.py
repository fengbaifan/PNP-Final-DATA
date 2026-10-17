from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
KIND = "person"
BATCHES = {
    "new-person:neri-philip-42b3421786": {
        "candidate": "cand-1898",
        "ku_id": "units/persons/philip-neri",
        "rel_path": "04-knowledge/units/persons/philip-neri.md",
        "record": {
            "name_zh": "圣菲利普·内里",
            "name_en": "Philip Neri",
            "description_zh": (
                "第3章称 Philip Neri 为奥拉托利会（Oratorians）的创立者，记他对绘画与音乐有深切感受，并亲自关注其教堂的装饰。书中还记述他与 Chiesa Nuova（S. Maria della Vallicella）的建设、礼仪空间及 Federico Barocci 祭坛画的关联；早期传记的神意故事和观看画作时的反应均保留为书中转述。"
            ),
            "description_en": (
                "Chapter 3 identifies Philip Neri as the founder of the Oratorians, describes his deep responsiveness to painting and music, and says that he took a personal interest in decorating his church. The book also connects him with the building of Chiesa Nuova (S. Maria della Vallicella), its devotional setting, and Federico Barocci's altarpiece; stories attributed to early biographers and reports of his response to the painting remain attributed accounts."
            ),
            "context_zh": (
                "P.csv#99“Philip Neri, St”列出第2章 p.24、第3章 pp.64、68–69、77。第3章以全名称其为奥拉托利会创立者，并叙述他对视觉艺术、音乐和教堂装饰的兴趣；书中称 S. Maria della Vallicella 于1575年交由他负责，后扩建为 Chiesa Nuova。作者说明早期传记关于拆除旧堂、依赖神意募款的故事并不完全准确；Barocci 画前的入神场景则以“据称”转述。第2章 p.24 的预言及第3章关于其与教团、作品和建筑的联系属于 S2 断言端点，关系裁决留待 S6。"
            ),
            "context_en": (
                "P.csv#99, “Philip Neri, St,” points to Chapter 2 p. 24 and Chapter 3 pp. 64, 68–69, and 77. Chapter 3 names him as the founder of the Oratorians and describes his interest in visual art, music, and church decoration; the book says S. Maria della Vallicella was assigned to him in 1575 and later enlarged as Chiesa Nuova. Haskell says the early-biographer story about demolishing the old church and relying on providence for funds is not wholly accurate. The episode before Barocci's painting is introduced as a report. The Chapter 2 prophecy and Chapter 3 statements about his links with the congregation, works, and building remain S2 assertions for S6 review."
            ),
            "boundary_zh": (
                "本卡对应唯一候选 cand-1898，属于 S3 跨章组 `new-person:neri-philip-42b3421786`。名称据索引和正文的 Philip Neri、St Philip Neri；中文显示名为工作音译。早期传记故事、作者评价和转述的宗教体验不提升为独立核实事实。17条直接 S2 断言端点中16条标记为关系候选，全部留待 S6；本批不新增正式关系、works／archives KU、外部身份记录或 S5 补足。"
            ),
            "boundary_en": (
                "This card represents the sole candidate cand-1898 in the cross-chapter S3 group `new-person:neri-philip-42b3421786`. The displayed name follows the index and the forms Philip Neri and St Philip Neri in the book; the Chinese name is a working transliteration. Early-biographer stories, authorial evaluations, and reported religious experiences are not elevated to independently verified facts. Sixteen of 17 direct S2 statement endpoints are relation candidates and remain for S6. This batch adds no formal relations, work or archive KUs, external identity record, or S5 enrichment."
            ),
            "type_notes_zh": (
                "索引称“Philip Neri, St”，正文作 Philip Neri、St Philip Neri；圣徒称号按书内用法保留，姓名中文为工作音译。"
            ),
            "type_notes_en": (
                "The index form is “Philip Neri, St”; the prose uses Philip Neri and St Philip Neri. The saintly title is retained as used in the book."
            ),
            "sources": [
                card_writer.source(
                    "3", "64", "03_CHP-3_sec_i.md", "18",
                    "the founder of the Oratorians Philip Neri",
                    "第3章称 Philip Neri 为奥拉托利会创立者。",
                ),
                card_writer.source(
                    "3", "68", "03_CHP-3_sec_ii.md", "37",
                    "St Philip Neri, on the other hand, was a man of the profoundest aesthetic sensibility who responded passionately to painting and music. He naturally attracted to himself many of the most cultivated spirits of the time and he personally took an enthusiastic interest in the decoration of his church.",
                    "第3章描述 Philip Neri 对绘画、音乐和教堂装饰的兴趣，并称他吸引了当时许多有教养的人。",
                ),
                card_writer.source(
                    "3", "68", "03_CHP-3_sec_ii.md", "38",
                    "S. Maria deUa Vallicclla was assigned to him in 1575 by Pope Gregory XIII. It lay in the very heart of fashionable and cultivated Rome. It was, however, immediately felt to be too small and was pulled down to be replaced by a larger budding of the same name, often caUed the Chiesa Nuova.",
                    "第3章记 S. Maria della Vallicella 于1575年交由 Philip Neri，并称后拆建为较大的同名教堂（Chiesa Nuova）；保留 OCR 拼写于原文引句。",
                ),
                card_writer.source(
                    "3", "68–69", "03_CHP-3_sec_ii.md", "38",
                    "St PhiEp himself worked in close co-operation with the architect Matteo da Castello whom the Oratorians chose",
                    "第3章称 Philip 本人与奥拉托利会选择的建筑师 Matteo da Castello 密切合作。",
                ),
                card_writer.source(
                    "3", "69", "03_CHP-3_sec_ii.md", "49",
                    "We hear that ‘he would sit on a small chair in front of it and all unconsciously be rapt into a sweet ecstasy’. Then the down-to-earth side of his character would reassert itself: irritated by the women who came to gaze at him, he would have them angrily sent away and would do all in his power to conceal the effects of the picture on him.",
                    "第3章以转述方式记 Philip Neri 观看 Barocci 画作时的反应，并写到他后来驱离围观女性；此处按 Haskell 的叙述层级保存。",
                ),
                card_writer.source(
                    "2", "24", "02_CHP-2_sec_i.md", "4",
                    "St Philip Neri prophesied that he would one day be a cardinal.",
                    "第2章记 Philip Neri 对 Maffeo Barberini 的预言；该关系断言留待 S6。",
                ),
            ],
        },
    },
    "new-person:liberi-pietro-19e17efc6a": {
        "candidate": "cand-1401",
        "ku_id": "units/persons/pietro-liberi",
        "rel_path": "04-knowledge/units/persons/pietro-liberi.md",
        "record": {
            "name_zh": "皮耶特罗·利贝里",
            "name_en": "Pietro Liberi",
            "description_zh": (
                "第7章称 Pietro Liberi 为当时威尼斯最成功的画家之一，记他于1658年应利奥波德·威廉大公之邀赴维也纳一年并获授 Count Palatine。第8章记他于1660年承接贝加莫 Santa Maria Maggiore 的绘画委托，作品《洪水》经返修后安置，另一画稿遭拒后合同取消。对其艺术质量及委托失败原因的说法保留为 Haskell 的评价和推断。"
            ),
            "description_en": (
                "Chapter 7 calls Pietro Liberi one of the most successful Venetian painters of his day and says that he went to Vienna for a year in 1658 at the invitation of Archduke Leopold Wilhelm, receiving the title Count Palatine in return. Chapter 8 records his 1660 commission for Santa Maria Maggiore in Bergamo: The Flood was repainted and installed, while the contract was cancelled after a sketch for a second picture was rejected. Haskell's assessment of the painter and his inference about the commission's failure remain attributed judgements."
            ),
            "context_zh": (
                "L.csv#58“Liberi, Pietro”列出第7章 pp.193、197，第8章 p.217 及第19章 p.393。第7章 p.193 给出全名及赴维也纳的叙述；p.197 的 Liberis 与其对应。第8章记威尼斯的画家委托、合同和《洪水》返修，Haskell 对其艺术质量和裸体画引起当地反感的解释属于作者评价/推测。第19章附录所述1789年匿名拍卖中部分画作据称来自 Joseph Smith 收藏，且相关归属不确定；不据此确立作品所有权。"
            ),
            "context_en": (
                "L.csv#58, “Liberi, Pietro,” points to Chapter 7 pp. 193 and 197, Chapter 8 p. 217, and Chapter 19 p. 393. Chapter 7 p. 193 supplies the full name and the Vienna account; the p. 197 form Liberis refers to him. Chapter 8 records the Venetian painter's commission, contract, and repainting of The Flood. Haskell's assessment of his artistic quality and proposed explanation involving local reaction to nudes remain authorial evaluation and inference. The Chapter 19 appendix says that some pictures in an anonymous 1789 sale were reportedly from Joseph Smith's collection and treats attribution cautiously; it does not establish ownership."
            ),
            "boundary_zh": (
                "本卡对应唯一候选 cand-1401，属于 S3 跨章组 `new-person:liberi-pietro-19e17efc6a`。索引与正文全名锚点确认 Pietro Liberi；p.197 的 Liberis 按上下文作为书内变体。拍卖目录的作品来源、作者对性格和艺术质量的描述及当地审美原因均不转写为无条件事实。17条直接 S2 断言端点中11条为关系候选，全部留待 S6；本批不新增正式关系、work／archive KU、外部身份记录或 S5 补足。"
            ),
            "boundary_en": (
                "This card represents the sole candidate cand-1401 in the cross-chapter S3 group `new-person:liberi-pietro-19e17efc6a`. The index and full-name passages identify Pietro Liberi; Liberis at p. 197 is treated as a contextual form referring to him. The sale catalogue's provenance statements and Haskell's character, quality, and local-taste assessments are not converted into unqualified facts. Eleven of 17 direct S2 statement endpoints are relation candidates and remain for S6. This batch adds no formal relations, work or archive KUs, external identity record, or S5 enrichment."
            ),
            "type_notes_zh": (
                "索引规范名为 Liberi, Pietro；正文偶见 Liberis。该词形按其在第7章 p.197 的语境记为同一人物的形式，不另立身份。"
            ),
            "type_notes_en": (
                "The index form is Liberi, Pietro; the prose also has Liberis. In its Chapter 7 p. 197 context this is treated as a form referring to the same person, not a separate identity."
            ),
            "sources": [
                card_writer.source(
                    "7", "193", "07_CHP-7_sec_iv.md", "8–9",
                    "He also persuaded the most successful Venetian painter of the day, Pietro Liberi, to come to Vienna in 1658 and stay there for a year during which he painted a large number of pictures and was -made Count\nPalatine in return.2",
                    "第7章给出 Pietro Liberi 全名，称其于1658年赴维也纳一年，并在此期间绘制多幅作品、获授 Count Palatine。",
                ),
                card_writer.source(
                    "7", "197", "07_CHP-7_sec_iv.md", "73",
                    "In Venice he bought Liberis;",
                    "第7章以 Liberis 记 Lord Exeter 在威尼斯购买其作品；具体作品未在此句具名。",
                ),
                card_writer.source(
                    "8", "217", "08_CHP-8_sec_ii.md", "71",
                    "In 1660 a contract was signed with Pietro Liberi, at that time the best known artist in the city and already a man with a European reputation. Liberi agreed to paint the entire sixteen pictures for 3 800 ducats and was paid the first 500 as an advance guarantee.",
                    "第8章记1660年与 Pietro Liberi 签订十六幅画的合同，载总价与预付款，并描述其当时声望。",
                ),
                card_writer.source(
                    "8", "217", "08_CHP-8_sec_ii.md", "72",
                    "It was a year before Liberi arrived in Bergamo, and after he had repainted the picture as demanded, it was placed above the South door, where it still is. He then returned to Venice to carry on with the commission. This time he was more cautious and instead of completing the second picture, The Last Judgement,he sent a sketch. This too was a total failure. The committee found it ‘deficient in every respect’, and thereafter the contract with Liberi was cancelled.",
                    "第8章记《洪水》返修并安置于南门上方；《最后的审判》仅交画稿且遭委员会拒绝，合同随后取消。",
                ),
                card_writer.source(
                    "8", "217", "08_CHP-8_sec_ii.md", "73–74",
                    "In fact it seems most probable that Pietro Liberi, who was notorious for the extreme indecency of his highly erotic nudes, had upset Bergamasque susceptibilities, unused as they were to the more sophisticated tastes of Venice.",
                    "第8章将委托失败的可能原因归于当地对其裸体画的不适；Haskell 明确以最可能解释提出，卡片保留为作者推测。",
                ),
                card_writer.source(
                    "19", "393", "19_CHP-19Appendix.md", "150–151",
                    "These include a self portrait by Sebastiano Ricci, landscapes by Marco Ricci and Zuccarelli, and a number of pictures by Giulio\nCarpioni, Mastelletta, Pietro Liberi, Strozzi, Fetti and Lazzarini.",
                    "第19章附录列举1789年匿名拍卖中据称来自 Smith 收藏的画作；清单归属并非确定认定。",
                ),
            ],
        },
    },
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def group_of(note):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected one exact occurrence, found {count}"
    return text.replace(old, new, 1)


def replace_after_once(text, marker, old, new, label):
    start = text.index(marker) + len(marker)
    return text[:start] + replace_once(text[start:], old, new, label)


def updated_process(text):
    text = replace_once(
        text,
        "截至 Donna Olimpia Maidalchini 批次，4,818 个当前 `new` 身份组中完成149组，余4,669组；4,988条成员候选中映射189条，余4,799条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记43组、76条候选，待登记1,042组、1,102条候选。",
        "截至 Philip Neri 与 Pietro Liberi 批次，4,818 个当前 `new` 身份组中完成151组，余4,667组；4,988条成员候选中映射191条，余4,797条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记45组、78条候选，待登记1,040组、1,100条候选。",
        "process current S4 counts",
    )
    text = replace_once(
        text,
        "Giovanni Vianello、Bonomo Algarotti、Donna Olimpia Maidalchini 已登记为人物 KU。",
        "Giovanni Vianello、Bonomo Algarotti、Donna Olimpia Maidalchini、Philip Neri、Pietro Liberi 已登记为人物 KU。",
        "process registered person names",
    )
    text = replace_once(
        text,
        "Donna Olimpia Maidalchini 的17条（其中13条为关系候选）及其他已登记对象的 S2 关系候选仍待 S6",
        "Donna Olimpia Maidalchini 的17条（其中13条为关系候选）、Philip Neri 的16条关系候选与 Pietro Liberi 的11条关系候选及其他已登记对象的 S2 关系候选仍待 S6",
        "process pending relation candidates",
    )
    batch = """### person：Philip Neri 与 Pietro Liberi 跨章身份组登记（2026-10-16）

- `cand-1898`（P.csv#99）属于 `new-person:neri-philip-42b3421786`，登记为 `units/persons/philip-neri`；`cand-1401`（L.csv#58）属于 `new-person:liberi-pietro-19e17efc6a`，登记为 `units/persons/pietro-liberi`。两组各一名候选，当前 manifest 和 accepted.yml 均无对应 KU；卡片分别保留 St Philip Neri/Philip Neri 与 Pietro Liberi/Liberis 的书内写法。
- Philip Neri 卡据第3章对奥拉托利会创立者、视觉艺术兴趣及 Chiesa Nuova 建设的记述；早期传记故事和 Barocci 画前的宗教体验保留原有转述限定。Pietro Liberi 卡据第7章赴维也纳叙述、第8章贝加莫委托及第19章拍卖清单；作品来源、评价及委托失败原因均按 Haskell 的叙述、推测和不确定归属登记。
- Philip Neri 有17条直接 S2 断言端点（16条关系候选）；Pietro Liberi 有17条端点（11条关系候选），均留待 S6。本批未新增正式关系、work/archive KU、外部身份记录或 S5 补足。批次脚本 [register_s4_person_neri_liberi_batch_20261016.py](register_s4_person_neri_liberi_batch_20261016.py) dry-run 核对两组成员、11处精确引文、端点/关系候选数、既有 KU 和登记外键后通过，再 apply 完成两张卡、manifest、accepted.yml 与候选映射。manifest 从1,168增至1,170；累计登记151组、191条候选映射，余4,667组、4,797条。

"""
    return replace_once(text, "### 登记进度与后续\n\n", batch + "### 登记进度与后续\n\n", "process S4 batch insertion")


def updated_result(text):
    text = replace_once(text, "目前完成149组、映射189条成员候选，余4,669组、4,799条映射。", "目前完成151组、映射191条成员候选，余4,667组、4,797条映射。", "result top S4 counts")
    text = replace_once(text, "Bonomo Algarotti、Donna Olimpia Maidalchini 四十一个补充 person 组", "Bonomo Algarotti、Donna Olimpia Maidalchini、Philip Neri、Pietro Liberi 四十三个补充 person 组", "result top person names")
    text = replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,168 KU；含本轮新增43个 person 组（", "| [KU 登记](../tables/ku-manifest.csv) | 1,170 KU；含本轮新增45个 person 组（", "result manifest count")
    text = replace_once(text, "Giovanni Vianello、Bonomo Algarotti、Donna Olimpia Maidalchini、2个 Valmarana 组", "Giovanni Vianello、Bonomo Algarotti、Donna Olimpia Maidalchini、Philip Neri、Pietro Liberi、2个 Valmarana 组", "result manifest names")
    text = replace_once(text, "当前已登记43个 person 组（", "当前已登记45个 person 组（", "result current person count")
    text = replace_after_once(
        text,
        "当前已登记45个 person 组（",
        "Bonomo Algarotti、Donna Olimpia Maidalchini、",
        "Bonomo Algarotti、Donna Olimpia Maidalchini、Philip Neri、Pietro Liberi、",
        "result current person names",
    )
    text = replace_once(
        text,
        "当前尚余4,669个 `new` 身份组、4,799条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记43组、76条候选，待登记1,042组、1,102条候选。",
        "当前尚余4,667个 `new` 身份组、4,797条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记45组、78条候选，待登记1,040组、1,100条候选。",
        "result current S4 type counts",
    )
    batch = """### person：Philip Neri 与 Pietro Liberi 跨章身份组登记（2026-10-16）

`cand-1898`（P.csv#99）与 `cand-1401`（L.csv#58）分别映射至 [Philip Neri 人物卡](../../04-knowledge/units/persons/philip-neri.md)和 [Pietro Liberi 人物卡](../../04-knowledge/units/persons/pietro-liberi.md)。现有 accepted KU 中无对应人物。Philip Neri 的17条直接端点中16条为关系候选；Pietro Liberi 的17条端点中11条为关系候选，均留待 S6。本批不新增正式关系、work/archive KU、外部身份核验或 S5 补足；来源限定、干跑记录和映射依据见[S4批次脚本](../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_neri_liberi_batch_20261016.py)。manifest 从1,168增至1,170；累计登记151组、191条候选映射，余4,667组、4,797条。

"""
    return replace_once(
        text,
        "### person：Donna Olimpia Maidalchini 跨章身份组登记（2026-10-16）\n\n",
        batch + "### person：Donna Olimpia Maidalchini 跨章身份组登记（2026-10-16）\n\n",
        "result S4 batch insertion",
    )


def main():
    parser = argparse.ArgumentParser(description="Register Philip Neri and Pietro Liberi person identity groups")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    current = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    alignment_by_id = {row["candidate_id"]: row for row in current}
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")

    assert len(manifest) == 1168, f"unexpected manifest count: {len(manifest)}"
    counts = Counter(row["decision"] for row in current)
    assert counts == Counter({"same": 1698, "new": 4988, "undecided": 5614, "excluded": 97, "conflict": 7}), counts
    groups = defaultdict(list)
    for row in current:
        if row["decision"] == "new":
            group = group_of(row["resolution_note"])
            assert group
            groups[group].append(row)
    registered = defaultdict(list)
    for row in current:
        if row["decision"] == "new" and row.get("ku_id"):
            registered[group_of(row["resolution_note"])].append(row)
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(groups), sum(map(len, groups.values()))) == (4818, 4988)
    assert (len(registered_groups), sum(len(value) for value in registered_groups.values())) == (149, 189)

    endpoint_counts = {}
    for group, spec in BATCHES.items():
        candidate_id = spec["candidate"]
        assert {row["candidate_id"] for row in groups[group]} == {candidate_id}
        assert not any(row.get("ku_id") for row in groups[group])
        assert alignment_by_id[candidate_id]["decision"] == "new"
        assert candidate_by_id[candidate_id]["suggested_type"] == KIND
        assert not (ROOT / spec["rel_path"]).exists()
        assert spec["rel_path"] not in accepted_text
        assert not any(row["ku_id"] == spec["ku_id"] or row["card_path"] == spec["rel_path"] for row in manifest)
        endpoint_ids, relation_ids = set(), set()
        with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
            for line in stream:
                statement = json.loads(line)
                if candidate_id in {statement.get("subject_candidate_id"), statement.get("object_candidate_id")}:
                    endpoint_ids.add(statement["statement_id"])
                    if statement.get("qualifiers", {}).get("relation_candidate") is True:
                        relation_ids.add(statement["statement_id"])
        expected = (17, 16) if candidate_id == "cand-1898" else (17, 11)
        assert (len(endpoint_ids), len(relation_ids)) == expected, (candidate_id, len(endpoint_ids), len(relation_ids))
        endpoint_counts[candidate_id] = (len(endpoint_ids), len(relation_ids))
        for item in spec["record"]["sources"]:
            source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
            assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (candidate_id, item["file"], item["quote"])
    assert candidate_by_id["cand-1898"]["canonical_name"] == "Philip Neri, St"
    assert candidate_by_id["cand-1401"]["canonical_name"] == "Liberi, Pietro"
    assert not any(
        row["type"] == KIND and any(name in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for name in ("philip neri", "pietro liberi"))
        for row in manifest
    )

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest = list(manifest)
    for group, spec in BATCHES.items():
        candidate_id = spec["candidate"]
        planned_by_id[candidate_id]["ku_id"] = spec["ku_id"]
        planned_by_id[candidate_id]["resolution_note"] += f" S4 registration: mapped {group} to {spec['ku_id']}."
        record = spec["record"]
        planned_manifest.append({"ku_id": spec["ku_id"], "type": KIND, "canonical_name": record["name_zh"], "name_en": record["name_en"], "source_task": TASK, "card_path": spec["rel_path"]})

    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new":
            planned_groups[group_of(row["resolution_note"])].append(row)
    planned_registered = {group: rows for group, rows in planned_groups.items() if any(row.get("ku_id") for row in rows)}
    for group, rows in planned_registered.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
    assert (len(planned_registered), sum(len(value) for value in planned_registered.values())) == (151, 191)
    assert (len(planned_groups) - len(planned_registered), sum(len(value) - sum(bool(row.get("ku_id")) for row in value) for value in planned_groups.values())) == (4667, 4797)

    planned_process = updated_process(process_text)
    planned_result = updated_result(result_text)
    card_texts = {}
    for spec in BATCHES.values():
        card_text = card_writer.make_card(spec["record"], KIND)
        card_text, dates = re.subn(r"^(created|updated): '2026-10-15'$", r"\1: '2026-10-16'", card_text, flags=re.MULTILINE)
        assert dates == 2
        card_texts[spec["rel_path"]] = card_text

    if args.dry_run:
        print(
            "dry-run passed: person_groups=2 candidate_members=2 "
            f"Philip_Neri_endpoints={endpoint_counts['cand-1898'][0]} relation_candidates={endpoint_counts['cand-1898'][1]} "
            f"Pietro_Liberi_endpoints={endpoint_counts['cand-1401'][0]} relation_candidates={endpoint_counts['cand-1401'][1]} "
            "source_quotes=11 registered_groups_after=151 mapped_candidates_after=191 "
            "pending_groups=4667 pending_candidates=4797 manifest_after=1170; no formal relations added"
        )
        return 0

    for rel_path, content in card_texts.items():
        (ROOT / rel_path).write_text(content, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted_text.splitlines()
    for rel_path in sorted(spec["rel_path"] for spec in BATCHES.values()):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > rel_path),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {rel_path}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(planned_process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(planned_result, encoding="utf-8-sig", newline="\n")
    print(f"applied: person_groups=2 candidates=2 endpoints=34 relation_candidates=27 manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
