from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml

import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
UNITS = ROOT / "04-knowledge" / "units"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
KIND = "person"
GROUP = "new-person:crozat-pierre-793a5b5d2e"
MEMBERS = ("cand-0894", "cand-0895")
KU_ID = "units/persons/pierre-crozat"
REL_PATH = "04-knowledge/units/persons/pierre-crozat.md"
SCRIPT_REL = "03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_pierre_crozat_batch_20261016.py"
S3_SCRIPT_REL = "03-processing/patrons-and-painters-full-book-s2/process/reconcile_s3_crozat_index_subentry_20261016.py"


RECORD = {
    "name_zh": "皮埃尔·克罗扎",
    "name_en": "Pierre Crozat",
    "description_zh": (
        "哈斯克尔称 Pierre Crozat 为富有的银行家和法国新型收藏者之一。第10章记述他观看 Rosalba Carriera 的粉彩作品、"
        "1716年到访威尼斯并与 Antonio Maria Zanetti 建立友谊，以及在巴黎接待 Carriera 等人的经历；正文还提到其 Rue Richelieu 宅邸、"
        "收藏和艺术家聚会。相关经历均保留为本书叙述，宅邸、街址和收藏不并入人物身份。"
    ),
    "description_en": (
        "Haskell describes Pierre Crozat as a wealthy banker and a new kind of French collector. Chapter 10 recounts his viewing of Rosalba Carriera's pastels, "
        "his 1716 visit to Venice and friendship with Antonio Maria Zanetti, and his reception of Carriera and other artists in Paris. The text also describes "
        "his Rue Richelieu mansion, collection, and meetings for artists; the mansion, street location, and collection remain distinct from the person."
    ),
    "context_zh": (
        "C.csv#428 为人物主项；C.csv#429 的 “patronage of Venetian artists” 是同名主项下的索引子目，指向第10章 pp.284–285。第7章 p.200 注3称 de Matteis 曾在巴黎为 Crozat 等人工作，但该注引 Loret，未独立核读所引材料。"
        "第10章 pp.277、284–285 描述 Crozat 的银行家/收藏者身份、1715年观看 Rosalba 粉彩、Rue Richelieu 宅邸、收藏及接待艺术家；第13章 p.341 记他1716年到访威尼斯并与 Zanetti 结为密友。"
        "第14章 p.349 提到 Algarotti 在巴黎与 Crozat 会面，同时明确说该会面仅为间接得知，脚注所引 Zanotti 书信未在本批查阅。"
    ),
    "context_en": (
        "C.csv#428 is the person entry; C.csv#429, “patronage of Venetian artists,” is a subentry under the same name and points to Chapter 10, pp. 284–285. "
        "Chapter 7 p. 200 n. 3 says de Matteis worked for Crozat among other patrons in Paris, but cites Loret, which was not independently consulted here. "
        "Chapter 10 pp. 277 and 284–285 describes Crozat as a banker and collector, records his viewing of Rosalba's pastels in 1715, and discusses his Rue Richelieu "
        "mansion, collection, and hospitality to artists. Chapter 13 p. 341 says he came to Venice in 1716 and formed a close friendship with Zanetti. Chapter 14 p. 349 "
        "mentions Algarotti meeting Crozat in Paris while explicitly qualifying that meeting as known only indirectly; the cited Zanotti letter was not consulted in this batch."
    ),
    "name_zh_note": "中文显示名“皮埃尔·克罗扎”为工作音译；原书全名拼写为 Pierre Crozat，简称 Crozat。",
    "name_en_note": "The Chinese display form is a working transliteration; the book gives the full name as Pierre Crozat and also uses Crozat.",
    "identity_zh": (
        "只指 C.csv#428 与 #429 所指、正文及注释中称作 Pierre Crozat / Crozat 的人物。cand-0894 与 cand-0895 同属该人物组；不把索引子目视为第二个人。"
        "人物与未分类的 Crozat 收藏候选 cand-11494、未识别的巴黎宅邸 cand-8846、Rue Richelieu 街址 cand-8961 及未具名交换画作 cand-8847 分开。"
        "19条 S2 直接断言以该人物为端点，其中14条标记为关系候选；全部留待 S6 逐项裁决。本批未新增正式关系、外部身份记录或 S5 补足。"
    ),
    "identity_en": (
        "This card refers only to the person named Pierre Crozat or Crozat in the prose and notes indexed by C.csv#428 and #429. Candidates cand-0894 and cand-0895 "
        "belong to one person group; the index subentry is not a second person. Keep the person distinct from the untyped collection candidate cand-11494, the unidentified Paris "
        "house cand-8846, the Rue Richelieu street candidate cand-8961, and the unidentified promised painting cand-8847. Nineteen direct S2 statements use this person as an endpoint, "
        "14 marked as relation candidates; all remain for item-by-item S6 review. This batch adds no formal relation, external identity record, or S5 enrichment."
    ),
    "sources": [
        card_writer.source(
            "7", "200 n. 3", "07_CHP-7_sec_v.md", "65",
            "In Paris de Matteis worked for Pierre Crozat among other patrons",
            "第7章注释称 de Matteis 曾在巴黎为 Pierre Crozat 等赞助人工作。",
            "该书内注释转引 Loret, p. 543；本批未独立查阅 Loret。",
        ),
        card_writer.source(
            "10", "277", "10_CHP-10_intro.md", "22",
            "a new type of collector, symbolised by Pierre Crozat, the fabulously rich banker",
            "第10章以 Pierre Crozat 为法国新型收藏者的代表，并称其为富有的银行家。",
        ),
        card_writer.source(
            "10", "277", "10_CHP-10_intro.md", "22",
            "In Rosalba’s pastels which he saw during his visit of 1715 he found exactly what he was looking for",
            "第10章称 Crozat 在1715年一次访问期间观看 Rosalba 的粉彩作品，并认为作品符合其所求。",
        ),
        card_writer.source(
            "10", "284", "10_CHP-10_intro.md", "171",
            "He was at once brought into touch with Pierre Crozat, then aged 51, whose fine mansion in the Rue Richelieu contained a superb collection of paintings and, above all, many thousands of drawings by all the greatest Italian and Flemish masters.",
            "第10章在 Sebastiano Ricci 于1716年赴巴黎的叙述中称其结识 Pierre Crozat，当时 Crozat 51岁；同句描述 Rue Richelieu 宅邸内的绘画及图纸收藏。",
            "年龄仅按原书在该段的说法保留；收藏边界与宅邸分别处理。",
        ),
        card_writer.source(
            "10", "284", "10_CHP-10_intro.md", "174",
            "through the patronage of Crozat",
            "第10章称三位威尼斯艺术家经由 Crozat 的赞助而进入巴黎贵族社交圈。",
        ),
        card_writer.source(
            "10", "285", "10_CHP-10_intro.md", "183–184",
            "She was welcomed by Crozat, who lodged\n' her in his house and organised a series of splendid receptions in her honour",
            "第10章称 Crozat 欢迎 Rosalba Carriera 到巴黎、让她住在自己家中并为她安排一系列接待活动。",
        ),
        card_writer.source(
            "13", "341", "13_CHP-13_intro.md", "92",
            "Crozat came to Venice in 1716, he formed a close friendship with Zanetti",
            "第13章称 Crozat 于1716年到访威尼斯，并与 Zanetti 建立密切友谊。",
        ),
        card_writer.source(
            "14", "349", "14_CHP-14_intro.md", "24",
            "he met Pierre Crozat",
            "第14章称 Algarotti 在巴黎居留期间与 Pierre Crozat 会面。",
            "同段 L33 明确说该会面仅为间接得知；脚注所引 Zanotti 书信未在本批独立查阅。",
        ),
    ],
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


def build_card():
    source_rows = []
    for item in RECORD["sources"]:
        loc_note = item["location_note"]
        source_rows.append({
            "citation": card_writer.BOOK_CITATION,
            "location": f"第{item['chapter']}章，印刷页{item['page']}；OCR L{item['lines']}" + (f"；{loc_note}" if loc_note else ""),
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": f"lines {item['lines']}; print p. {item['page']}" + (f"; {loc_note}" if loc_note else ""),
            },
        })
    frontmatter = {
        "title": f"{RECORD['name_zh']}（{RECORD['name_en']}）",
        "name_en": RECORD["name_en"],
        "type": KIND,
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** {RECORD['description_zh']}

**English:** {RECORD['description_en']}

### 名称

- **全名：** Pierre Crozat（第10章 p.277 L22、p.284 L171；来源2、4）
- **简称：** Crozat（第10章 pp.284–285、第13章 p.341；来源4–7）
- **中文显示名：** 皮埃尔·克罗扎（工作音译；依原书全名，不声称为原语名称）
- **索引子目：** “patronage of Venetian artists”（C.csv#429；对应第10章 pp.284–285）

### 身份

- **职业身份：** banker（银行家；第10章 p.277 L22；来源2）
- **职业身份：** collector（收藏者；第10章 p.277 L22；来源2）
- **书中所述年龄：** 第10章叙述其与 Ricci 接触时称其51岁；不据此推算出生日期（p.284 L171；来源4）

### 职业与生平履历

- **1715年访问期间：** 哈斯克尔称 Crozat 观看了 Rosalba Carriera 的粉彩作品，并认为这些作品正符合他的寻找目标。来源3；地点不由该句单独确定。
- **1716年：** 第13章称他到访威尼斯并与 Antonio Maria Zanetti 建立密切友谊。来源7。
- **巴黎交往：** 第10章把 Crozat 与 Sebastiano Ricci 在巴黎的接触置于 Ricci 1716 年离开伦敦前往巴黎的叙述中，并称 Crozat 当时51岁。来源4。
- **1721年：** 第10章记载 Crozat 促使 Carriera 到巴黎访问；她抵达后受到接待、住在其家中，并参加为她举办的接待活动。来源5–6。
- **Algarotti 的巴黎会面：** 第14章记为会面，但哈斯克尔说明该信息仅为间接得知；其所引 Zanotti 书信未在本批独立查阅。来源8。

### 本书语境

第10章 p.284 将 Crozat 的 Rue Richelieu 宅邸、藏画和大量图纸、每周艺术家与作家聚会及向艺术家开放收藏的叙述并置；这些仍是关于人物所处环境的书内记载，不表示已登记宅邸或收藏的 KU。第7章 p.200 注3补充 de Matteis 曾为 Crozat 工作，但所引 Loret 未在本批独立查阅。

Chapter 10 p. 284 places Crozat's Rue Richelieu mansion, paintings and drawings, weekly meetings of artists and writers, and access to his collection in the same account. These are source-bounded descriptions of his context; they do not register a mansion or collection KU. Chapter 7 p. 200 n. 3 adds that de Matteis worked for Crozat, but the cited Loret source was not independently consulted in this batch.

### 身份边界

中文：C.csv#428 主项与 C.csv#429 子目已在 S3 依据相同人物名称、子目范围及 pp.284–285 正文锚点归为一个人物组。人物与收藏 cand-11494、未识别的巴黎宅邸 cand-8846、Rue Richelieu 街址 cand-8961 及 Watteau 未识别画作 cand-8847 保持区分；这些候选不因同在 Crozat 语境而映射到人物卡。19条直接 S2 断言端点中14条为关系候选，全部待 S6 逐项审查；本批没有登记正式关系、外部身份标识或 S5 补足。

English: S3 groups the C.csv#428 main entry and C.csv#429 subentry as one person based on their shared name, subentry scope, and the text anchors on pp. 284–285. Keep the person distinct from collection cand-11494, unidentified Paris house cand-8846, Rue Richelieu street candidate cand-8961, and unidentified Watteau painting cand-8847; shared Crozat context does not map these candidates to this person card. Fourteen of 19 direct S2 statement endpoints are relation candidates, all retained for item-by-item S6 review. No formal relation, external identity record, or S5 enrichment was added.

## 关系与证据

### 身份与外部链接

本轮未新增外部身份记录；身份组依据书内索引与对应正文锚点登记。

### 关系记录

本卡尚无正式关系记录。S2 中14条关系候选及其他直接端点仍待 S6 审查；本批不把共现或叙述性关系直接写为正式边。
"""
    return f"---\n{fm}---\n\n{body}"


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected one exact occurrence, found {count}"
    return text.replace(old, new, 1)


def updated_process_text(text):
    text = replace_once(
        text,
        "| person | 3,469 | 963 | 1,178 | 2 | 7 | 1,319 |",
        "| person | 3,469 | 963 | 1,179 | 2 | 7 | 1,318 |",
        "S3 person type row",
    )
    status_prefix = "全书候选级 S3 决定闭包已完成：12,404 个候选都有唯一、可追溯的决定；"
    lines = text.splitlines()
    matching = [i for i, line in enumerate(lines) if line.startswith(status_prefix)]
    assert len(matching) == 1, f"S3 completion status line count={len(matching)}"
    i = matching[0]
    lines[i] = lines[i].replace("5,615 个 `undecided`", "5,614 个 `undecided`").replace(
        "4,988 个 `new` 身份候选", "4,989 个 `new` 身份候选"
    )
    assert "5,614 个 `undecided`" in lines[i] and "4,989 个 `new` 身份候选" in lines[i]
    text = "\n".join(lines) + "\n"
    text = replace_once(
        text,
        "**状态：处理中。** 本轮按当前 S3 裁决需登记 4,988 条 `new` 候选，按 `resolution_note` 中的 `group=` 汇总为 4,819 个身份组。",
        "**状态：处理中。** 本轮按当前 S3 裁决需登记 4,989 条 `new` 候选，按 `resolution_note` 中的 `group=` 汇总为 4,819 个身份组。",
        "S4 state",
    )
    s3_section = """### S3 补充裁决：Pierre Crozat 索引子目并入跨章人物组（2026-10-16）

`cand-0895`（C.csv#429，“patronage of Venetian artists”）原为 `undecided`，原因是该索引子目未映射到 S2 正文提及。复核索引父项 C.csv#428、子目页码284–285及第10章 p.284 的 Crozat patronage 断言、p.285 的 Carriera 接待断言后，确认该子目描述同一人物而非第二位赞助者。现将 `cand-0895` 改为 `new`，并与 `cand-0894` 共用 `new-person:crozat-pierre-793a5b5d2e`；原 `undecided` 理由全文保留在对齐行。新身份组数不变；S3 当前为 `new=4,989`、`undecided=5,614`、4,819组。裁决脚本 [reconcile_s3_crozat_index_subentry_20261016.py](reconcile_s3_crozat_index_subentry_20261016.py) dry-run 已核对三条 p.284–285 断言锚点后 apply；未新增 KU 或正式关系。

"""
    text = replace_once(text, "## S4 KU 登记（2026-10-15）\n", s3_section + "## S4 KU 登记（2026-10-15）\n", "S3 Crozat process section")
    progress_old = (
        "截至 Francesco Zuccarelli 批次，4,819 个当前 `new` 身份组中完成142组，余4,677组；4,988条成员候选中映射179条，余4,809条。family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,178条候选，已登记36组、66条候选，待登记1,050组、1,112条候选。procedure 已登记23组、24条候选，work、place 各登记1组/1条和2组/2条候选。"
    )
    progress_new = (
        "截至 Pierre Crozat 批次，4,819 个当前 `new` 身份组中完成143组，余4,676组；4,989条成员候选中映射181条，余4,808条。family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记37组、68条候选，待登记1,049组、1,111条候选。procedure 已登记23组、24条候选，work、place 各登记1组/1条和2组/2条候选。"
    )
    text = replace_once(text, progress_old, progress_new, "process current S4 progress")
    text = replace_once(text, "Giorgio Pisani 的15条、Francesco Zuccarelli 的17条及其他已登记对象", "Giorgio Pisani 的15条、Francesco Zuccarelli 的17条、Pierre Crozat 的14条及其他已登记对象", "process relation follow-up")

    batch_log = """### person：Pierre Crozat 跨章双候选组登记（2026-10-16）

- `cand-0894`（C.csv#428 人物主项）与经 S3 补裁的 `cand-0895`（C.csv#429，“patronage of Venetian artists”子目）同属 `new-person:crozat-pierre-793a5b5d2e`，登记为 `units/persons/pierre-crozat`，两条候选映射到一张人物卡。后者原 S3 `undecided` 的理由仍保存在对齐行历史注释中。
- 卡片依第7章 p.200 注3、第10章 pp.277、284–285、第13章 p.341 和第14章 p.349 的书内证据，记录银行家/收藏者身份、1715年观看 Carriera 粉彩、1716年威尼斯访问与 Zanetti 交往、1721年接待 Carriera 等语境。Loret 与 Zanotti 书信未在本批独立查阅；Crozat 收藏、宅邸、街址及未识别画作继续与人物分开。未补入生卒年、外部身份记录、正式关系或 S5 内容。
- 该组19条直接 S2 断言端点，其中14条标记为关系候选，全部留待 S6 逐项审查。批次脚本 [register_s4_person_pierre_crozat_batch_20261016.py](register_s4_person_pierre_crozat_batch_20261016.py) dry-run 核对 S3 组成员、类型、8处原文锚点、端点/候选数及外键后通过；apply 将两条候选映射至同一卡并登记 manifest/accepted。manifest 从1,161增至1,162；累计登记143组、181条候选映射，余4,676组、4,808条候选。

"""
    text = replace_once(text, "### 登记进度与后续\n", batch_log + "### 登记进度与后续\n", "Crozat S4 process log")
    return text


def updated_result_text(text):
    lines = text.splitlines()
    status = [i for i, line in enumerate(lines) if line.startswith("**当前状态：全书 S2 语义处理已完成")]
    assert len(status) == 1, f"result status line count={len(status)}"
    i = status[0]
    line = lines[i]
    line = line.replace("5,615 个仍为 `undecided`", "5,614 个仍为 `undecided`")
    line = line.replace("4,988条 `new` 候选", "4,989条 `new` 候选")
    line = line.replace("目前完成142组、映射179条成员候选，余4,677组、4,809条映射", "目前完成143组、映射181条成员候选，余4,676组、4,808条映射")
    line = line.replace("Francesco Zuccarelli 三十四个补充 person 组", "Francesco Zuccarelli、Pierre Crozat 三十五个补充 person 组")
    assert "5,614 个仍为 `undecided`" in line and "4,989条 `new` 候选" in line and "143组" in line
    lines[i] = line
    text = "\n".join(lines) + "\n"
    text = replace_once(text, "| new | 4,988 | 按 4,819 个当前身份组进入 S4；每组登记一个 KU |", "| new | 4,989 | 按 4,819 个当前身份组进入 S4；每组登记一个 KU |", "result S3 new count")
    text = replace_once(text, "| undecided | 5,615 | 保留对象、版本、身份、类型或来源方面的未决理由及后续证据需求 |", "| undecided | 5,614 | 保留对象、版本、身份、类型或来源方面的未决理由及后续证据需求 |", "result S3 undecided count")
    s3_note = """\n\n**Pierre Crozat 子目补裁：** `cand-0895`（C.csv#429，“patronage of Venetian artists”）根据其父项与第10章 pp.284–285 正文锚点，现与 `cand-0894` 共组 `new-person:crozat-pierre-793a5b5d2e`；旧待证理由保留。详见[S3裁决脚本](../../03-processing/patrons-and-painters-full-book-s2/process/reconcile_s3_crozat_index_subentry_20261016.py)。\n"""
    text = replace_once(text, "| **合计** | **12,404** | 每个候选一条当前决定记录 |", "| **合计** | **12,404** | 每个候选一条当前决定记录 |" + s3_note, "result Crozat S3 note")
    old = "当前尚余4,677个 `new` 身份组、4,809条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,178条候选，已登记36组、66条候选，待登记1,050组、1,112条候选。"
    new = "当前尚余4,676个 `new` 身份组、4,808条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记37组、68条候选，待登记1,049组、1,111条候选。"
    text = replace_once(text, old, new, "result current S4 counts")
    text = replace_once(text, "(../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_francesco_zuccarelli_batch_20261016.py)", "(../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_francesco_zuccarelli_batch_20261016.py)、[Pierre Crozat 人物卡](../../04-knowledge/units/persons/pierre-crozat.md)与[S4 批次脚本](../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_pierre_crozat_batch_20261016.py)", "result S4 artifacts")
    text = replace_once(text, "5,616 个 `undecided`", "5,614 个 `undecided`", "result current undecided count")
    text = replace_once(text, "Francesco Zuccarelli、2个 Valmarana 组", "Francesco Zuccarelli、Pierre Crozat、2个 Valmarana 组", "result S4 registered groups table")
    text = replace_once(text, "Francesco Zuccarelli、Valmarana 跨章2组", "Francesco Zuccarelli、Pierre Crozat、Valmarana 跨章2组", "result S4 registered person list")
    result_batch_log = """### person：Pierre Crozat 跨章双候选组登记（2026-10-16）

`cand-0894`（C.csv#428 人物主项）与 `cand-0895`（C.csv#429，“patronage of Venetian artists”子目）经 S3 归入同一新人物组，现共同映射至 [Pierre Crozat 人物卡](../../04-knowledge/units/persons/pierre-crozat.md)。第7章 p.200 注3、第10章 pp.277、284–285、第13章 p.341 与第14章 p.349 提供书内证据；保留书信和转引材料未独立查阅的限制。19条直接 S2 断言端点中14条为关系候选，均留待 S6。批次脚本 dry-run 核对组成员、8处原文锚点及映射后通过；本批不新增正式关系、外部身份记录或 S5 补足。\n\n"""
    text = replace_once(text, "## 未解决项与交接限制\n", result_batch_log + "## 未解决项与交接限制\n", "result Crozat S4 section")
    return text


def main():
    parser = argparse.ArgumentParser(description="Register the Pierre Crozat person identity group")
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

    assert len(manifest) == 1161, f"unexpected manifest count: {len(manifest)}"
    counts = Counter(row["decision"] for row in current)
    assert counts == Counter({"same": 1697, "new": 4989, "undecided": 5614, "excluded": 97, "conflict": 7}), counts
    groups = defaultdict(list)
    for row in current:
        if row["decision"] == "new":
            group = group_of(row["resolution_note"])
            assert group, f"new candidate lacks group: {row['candidate_id']}"
            groups[group].append(row)
    registered = defaultdict(list)
    for row in current:
        if row["decision"] == "new" and row.get("ku_id"):
            registered[group_of(row["resolution_note"])].append(row)
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(groups), sum(map(len, groups.values()))) == (4819, 4989)
    assert (len(registered_groups), sum(len(rows) for rows in registered_groups.values())) == (142, 179)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])
    assert all(alignment_by_id[candidate]["decision"] == "new" for candidate in MEMBERS)
    assert candidate_by_id["cand-0894"]["suggested_type"] == candidate_by_id["cand-0895"]["suggested_type"] == KIND
    assert candidate_by_id["cand-0895"]["sub_entry"] == "patronage of Venetian artists"
    assert "Previous S3 decision and rationale retained" in alignment_by_id["cand-0895"]["resolution_note"]

    card_path = ROOT / REL_PATH
    assert not card_path.exists() and REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(
        row["type"] == KIND and "pierre crozat" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )

    endpoint_ids = set()
    relation_ids = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if "cand-0894" in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert len(endpoint_ids) == 19 and len(relation_ids) == 14, (len(endpoint_ids), len(relation_ids))

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    for candidate in MEMBERS:
        planned_by_id[candidate]["ku_id"] = KU_ID
        planned_by_id[candidate]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": KIND,
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": REL_PATH,
    })
    planned_groups = defaultdict(list)
    for row in [row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")]:
        if row["decision"] == "new":
            planned_groups[group_of(row["resolution_note"])].append(row)
    planned_registered = {group: rows for group, rows in planned_groups.items() if any(row.get("ku_id") for row in rows)}
    for group, rows in planned_registered.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
    assert (len(planned_registered), sum(len(rows) for rows in planned_registered.values())) == (143, 181)
    assert (len(planned_groups) - len(planned_registered), sum(map(len, planned_groups.values())) - sum(len(rows) for rows in planned_registered.values())) == (4676, 4808)

    planned_process = updated_process_text(process_text)
    planned_result = updated_result_text(result_text)
    card_text = build_card()

    if args.dry_run:
        print(
            "dry-run passed: Pierre Crozat person_group=1 candidate_members=2 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            f"registered_groups_after={len(planned_registered)} mapped_candidates_after="
            f"{sum(len(rows) for rows in planned_registered.values())} pending_groups=4676 "
            f"pending_candidates=4808 manifest_after={len(planned_manifest)}; docs/cards/accepted references prepared; no formal relations added"
        )
        return 0

    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > REL_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {REL_PATH}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(planned_process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(planned_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: Pierre Crozat registered as {KU_ID}; mapped {len(MEMBERS)} candidates; "
        f"manifest={len(planned_manifest)} registered_groups=143 mapped_candidates=181; no formal relations added"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
