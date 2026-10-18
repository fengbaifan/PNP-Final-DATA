from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
ANCHOR = "s3-s4-person-endpoints-varda-della-valle-carlo-emanuele-tamizey-20261019"
PROCESS_REF = f"03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR}"
TRECCANI = "https://www.treccani.it/enciclopedia/carlo-emanuele-iii-di-savoia-re-di-sardegna_%28Dizionario-Biografico%29/"
HASKELL = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)."

PEOPLE = [
    {
        "candidate": "cand-2685", "alignment": "aln-3020", "ku": "units/persons/filippo-della-valle",
        "slug": "filippo-della-valle", "name": "Filippo della Valle", "title": "菲利波·德拉瓦莱（Filippo della Valle）",
        "group": "new-person:della-filippo-valle-b6ab7ea511", "source": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
        "location": "第3章 p.93；OCR line 185", "span": "line 185; printed p. 93",
        "summary": "Haskell称Filippo della Valle与Pietro Bracci制作右侧耳堂礼拜堂的《天使报喜》大理石浅浮雕；该礼拜堂于1749年完成。",
        "quote": "The chapel in the right transept was only completed in 1749 when Filippo della Valle and Pietro Bracci made a marble bas-relief of the Annunciation—see Fabrini.",
        "zh": "本卡记录第3章具名的人物Filippo della Valle。Haskell称他与Pietro Bracci制作了右侧耳堂礼拜堂的《天使报喜》大理石浅浮雕，并称礼拜堂于1749年完成；本卡仅保存原书语境，不据此登记作品现状或正式关系。中文名为项目工作音译。",
        "en": "This card records the person named as Filippo della Valle in Chapter 3. Haskell says he and Pietro Bracci made a marble bas-relief of the Annunciation for the right-transept chapel, which was completed in 1749. This preserves the book's account without asserting the work's present state or registering a formal relation. The Chinese display name is a project working transliteration.",
        "names": "- **索引形式：** Valle, Filippo della（S1，UVWXYZ.csv#21）\n- **正文形式：** Filippo della Valle（S2，第3章 p.93，line 185）",
        "identity": "无同类型既有KU与该全名相合；按原文全名保留为独立source-local人物组。",
        "relation": "`st-chp3-seciv-l179-187-della-valle-made-annunciation-relief`仍是S2关系候选；与[皮埃特罗·布拉奇](../../../04-knowledge/units/persons/pietro-bracci.md)的共同制作表述待S6核对，本次未登记正式边。",
    },
    {
        "candidate": "cand-2700", "alignment": "aln-3035", "ku": "units/persons/salvator-varda",
        "slug": "salvator-varda", "name": "Salvator Varda", "title": "萨尔瓦托·瓦尔达（Salvator Varda）",
        "group": "new-person:salvator-varda-c4461bbddc", "source": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "location": "第9章注释续段；OCR lines 240–249，line 247", "span": "line 247; footnote continuation",
        "summary": "Haskell在叙述Zaccaria Sagredo遗嘱时称，他将一幅Rubens作品和一幅Moroni肖像留给朋友Sig. Salvator Varda。",
        "quote": "He left a Rubens and un Ritrato del Moron’ to a friend. Sig. Salvator Varda.",
        "zh": "本卡记录Haskell在Zaccaria Sagredo遗嘱注释中称为“Sig. Salvator Varda”的书内人物。页图可读姓名为Varda；原书称其为朋友，并报告两件遗赠，但相关身份和遗嘱内容未独立核验。本卡不将其与Salvator Rosa合并，也不据姓名相似断言两者必为不同人。中文名为项目工作音译。",
        "en": "This card records the book-local person named “Sig. Salvator Varda” in Haskell's note on Zaccaria Sagredo's will. The printed page image reads Varda; the book calls him a friend and reports two bequests, but neither the identity nor the will has been independently verified. This card does not merge him with Salvator Rosa or claim from name similarity alone that they are certainly different people. The Chinese display name is a project working transliteration.",
        "names": "- **原书称名：** Sig. Salvator Varda（S2，第9章注释续段，line 247）\n- **索引形式：** Varda, Salvator（S1，UVWXYZ.csv#36）",
        "identity": "保留独立source-local身份组；与Salvator Rosa的对应关系未获证实，不能仅凭名字或威尼斯语境合并。",
        "relation": "`st-chp9-p263264-will-gifts-to-varda`为Haskell转述遗嘱的S2关系候选；端点身份与遗赠内容仍待S6审查，本次未登记正式边。",
    },
    {
        "candidate": "cand-7353", "alignment": "aln-7529", "ku": "units/persons/carlo-emanuele-iii-of-savoy",
        "slug": "carlo-emanuele-iii-of-savoy", "name": "Carlo Emanuele III of Savoy", "title": "萨伏依的卡洛·埃马努埃莱三世（Carlo Emanuele III of Savoy）",
        "group": "new-person:carlo-emanuele-iii-of-savoy-a69e3c8f1b", "source": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
        "location": "第7章 p.201 注2；OCR line 71", "span": "line 71; printed p. 201, note 2",
        "summary": "Haskell称Prince Eugene收藏散佚后，其中大部分由Carlo Emanuele III of Savoy购得；此处是经引文转述的交易报告。",
        "quote": "For the fate of the collection much of which was bought by Carlo Emanuele III of Savoy",
        "zh": "本卡记录第7章注释中的萨伏依国王Carlo Emanuele III。Treccani人物辞典将他识别为Vittorio Amedeo II之子；该身份依据用于区分两位君主。Haskell关于他购得Prince Eugene收藏“大部分”的说法仍是原书经引文转述，未由此处的身份核对独立验证。中文名为项目工作音译。",
        "en": "This card records Carlo Emanuele III of Savoy, named in a Chapter 7 note. Treccani's biographical dictionary identifies him as the son of Vittorio Amedeo II; this identity evidence distinguishes the two rulers. Haskell's report that he bought “much of” Prince Eugene's collection remains a second-hand account and is not independently verified by the identity check. The Chinese display name is a project working transliteration.",
        "names": "- **原书全名：** Carlo Emanuele III of Savoy（S2，第7章 p.201 注2，line 71）\n- **Treccani规范称名：** Carlo Emanuele III di Savoia（Treccani DBI；仅用于身份区分）",
        "identity": f"[Treccani DBI：Carlo Emanuele III di Savoia](<{TRECCANI}>)将其列为Vittorio Amedeo II之子并记其1730年继位；该记录支持人物身份，不支持藏品购藏断言。",
        "relation": "`st-chp7-p201-n2-eugene-collection-acquired`仍为Haskell转述的S2关系候选，保留“much of”限定；购藏事实未独立核实，本次未登记正式边。",
    },
    {
        "candidate": "cand-5833", "alignment": "aln-6014", "ku": "units/persons/tamizey-de-laroque",
        "slug": "tamizey-de-laroque", "name": "Tamizey de Laroque", "title": "塔米泽·德·拉罗克（Tamizey de Laroque）",
        "group": "new-person:de-laroque-tamizey-ce365919cd", "source": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
        "location": "第4章 p.108 注1；OCR line 265", "span": "line 265; printed p. 108",
        "summary": "Haskell称Bouchard的遗嘱由Tamizey de Laroque于1886年刊布。",
        "quote": "Bouchard’s will was published by Tamizey de Laroque in 1886.",
        "zh": "本卡记录第4章注释中写作“Tamizey de Laroque”的人物。第21章书目另列作者形式“P. Tamizey de Larroque”，并列出1886年文章；拼写和引文语境提示可能相关，但本项目尚未核读该文章，也未确认其与注释所指刊布记录完全对应，故保留两种来源形式且不扩写首字母P。中文名为项目工作音译。",
        "en": "This card records the person named “Tamizey de Laroque” in a Chapter 4 note. Chapter 21 separately lists the author form “P. Tamizey de Larroque” for an 1886 article. The spelling and citation context suggest a possible connection, but the article has not been consulted and its exact mapping to the publication mentioned in the note remains unconfirmed; both source forms are retained and the initial P is not expanded. The Chinese display name is a project working transliteration.",
        "names": "- **第4章形式：** Tamizey de Laroque（S2，第4章 p.108 注1，line 265）\n- **书目作者形式：** P. Tamizey de Larroque（S1，第21章书目 p.438；仅作来源形式）",
        "identity": "无已核实的外部身份记录；书目作者形式与第4章称名可能相关，精确身份及文章对应关系仍待核。",
        "relation": "`st-chp4-sec-ii-notes-l265-268-fn265-publication`为Haskell所述遗嘱刊布关系候选；书目中的`Deux testaments inédits`仅是可能匹配，本次未登记正式边。",
    },
]


def q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def card(person: dict[str, str]) -> str:
    source_entries = [
        f"  - citation: {q(HASKELL)}\n    location: {person['location']}\n    sentence_summary: {person['summary']}\n    original_quotes:\n      - source_span: {person['span']}\n        text: {q(person['quote'])}\n    evidence_ref:\n      doc_id: patrons-and-painters\n      source_file: {person['source']}\n      source_span: {person['span']}"
    ]
    if person["candidate"] == "cand-5833":
        source_entries.append(
            f"  - citation: {q(HASKELL)}\n    location: 第21章书目 p.438；OCR line 1145\n    sentence_summary: 书目列出作者形式“P. Tamizey de Larroque”及1886年文章“Deux testaments inédits”。\n    original_quotes:\n      - source_span: line 1145; printed p. 438\n        text: {q('Tamizey de Larroque, P.: ‘Deux testaments inédits’ in Bulletin Critique, 15 Mai 1886.')}\n    evidence_ref:\n      doc_id: patrons-and-painters\n      source_file: 02-sources/02-Markdown/21_CHP-21Bibliography.md\n      source_span: line 1145; printed p. 438"
        )
    return f'''---
title: {q(person['title'])}
name_en: {q(person['name'])}
type: person
evidence_status: source_backed
sources:
{chr(10).join(source_entries)}
created: '2026-10-19'
updated: '2026-10-19'
process_ref: {PROCESS_REF}
---

## 内容

### 描述

**中文：** {person['zh']}

**English:** {person['en']}

### 姓名形式

{person['names']}

## 关系与证据

### 身份入口

- **S3身份组：** `{person['group']}`；候选：`{person['candidate']}`；KU：`{person['ku']}`。
- {person['identity']}

### 关系记录

当前没有正式关系。{person['relation']}
'''


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(headers: list[str], rows: list[dict[str, str]]) -> str:
    import io

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_path = TABLES / "alignment.csv"
    manifest_path = TABLES / "ku-manifest.csv"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    alignment_headers, alignments = read_csv(alignment_path)
    manifest_headers, manifest = read_csv(manifest_path)
    expected_alignment_headers = ["alignment_id", "candidate_id", "ku_id", "external_source", "external_id", "decision", "accessed_date", "process_ref", "legacy_ku_id", "resolution_note"]
    if alignment_headers != expected_alignment_headers:
        raise ValueError("alignment.csv headers changed")
    if manifest_headers != ["ku_id", "type", "canonical_name", "name_en", "source_task", "card_path"]:
        raise ValueError("ku-manifest.csv headers changed")

    candidate_ids = {r["candidate_id"] for r in alignments if r.get("candidate_id")}
    if len(candidate_ids) != 12407:
        raise ValueError(f"expected 12,407 unique candidates, found {len(candidate_ids)}")
    by_alignment_id = {r["alignment_id"]: r for r in alignments}
    manifest_ids = {r["ku_id"] for r in manifest}
    output_cards: dict[Path, str] = {}
    for person in PEOPLE:
        row = by_alignment_id.get(person["alignment"])
        if not row or row.get("candidate_id") != person["candidate"] or row.get("external_source") or row.get("decision") != "new" or row.get("ku_id"):
            raise ValueError(f"unexpected current decision for {person['candidate']}")
        if person["ku"] in manifest_ids:
            raise ValueError(f"KU already exists: {person['ku']}")
        path = ROOT / "04-knowledge" / "units" / "persons" / f"{person['slug']}.md"
        if path.exists():
            raise ValueError(f"card already exists: {path}")
        output_cards[path] = card(person)
    if any(r.get("candidate_id") == "cand-7353" and r.get("external_source") == "Treccani DBI" for r in alignments):
        raise ValueError("Treccani DBI row already exists for cand-7353")

    max_alignment_id = max(int(m.group(1)) for r in alignments if (m := re.fullmatch(r"aln-(\d+)", r.get("alignment_id", ""))))
    external_id = f"aln-{max_alignment_id + 1:04d}"
    for person in PEOPLE:
        row = by_alignment_id[person["alignment"]]
        row["ku_id"] = person["ku"]
        row["process_ref"] = PROCESS_REF
        if person["candidate"] == "cand-7353":
            row["resolution_note"] = (
                f"source_ref=candidate=cand-7353; existing S3 new-person group retained; Treccani DBI {TRECCANI} identifies Carlo Emanuele III as Vittorio Amedeo II's son and supports a distinct person KU; "
                f"the identity source does not verify Haskell's collection-purchase report. S4 registered {person['ku']}; relation candidate remains pending S6."
            )
        else:
            old_s4_status = "; KU assignment remains for S4."
            if old_s4_status not in row["resolution_note"]:
                raise ValueError(f"expected prior S4-pending note missing for {person['candidate']}")
            row["resolution_note"] = row["resolution_note"].replace(old_s4_status, ".", 1).rstrip() + f" S4 registered {person['ku']} under {PROCESS_REF}; relation candidate remains pending S6."
    alignments.append({
        "alignment_id": external_id, "candidate_id": "cand-7353", "ku_id": "", "external_source": "Treccani DBI",
        "external_id": TRECCANI, "decision": "new", "accessed_date": "2026-10-19", "process_ref": PROCESS_REF,
        "legacy_ku_id": "", "resolution_note": "Identity only: Treccani DBI identifies Carlo Emanuele III as the son and successor of Vittorio Amedeo II. Used to distinguish the two rulers; does not independently verify Haskell's report about the collection purchase.",
    })

    for person in PEOPLE:
        manifest.append({
            "ku_id": person["ku"], "type": "person", "canonical_name": person["title"], "name_en": person["name"],
            "source_task": "patrons-and-painters-full-book-s2", "card_path": f"04-knowledge/units/persons/{person['slug']}.md",
        })

    accepted_lines = accepted_path.read_text(encoding="utf-8-sig").splitlines()
    if not accepted_lines or accepted_lines[0] != "units:":
        raise ValueError("accepted.yml format changed")
    section_end = next((i for i, line in enumerate(accepted_lines[1:], 1) if line and not line.startswith("- ")), len(accepted_lines))
    unit_lines = accepted_lines[1:section_end]
    if any(line and not line.startswith("- ") for line in unit_lines):
        raise ValueError("accepted.yml units list format changed")
    accepted = [line[2:] for line in unit_lines if line]
    new_paths = [f"04-knowledge/units/persons/{p['slug']}.md" for p in PEOPLE]
    if set(accepted).intersection(new_paths):
        raise ValueError("one or more cards already appear in accepted.yml")
    accepted_text = "units:\n" + "".join(f"- {p}\n" for p in [*accepted, *new_paths])
    if section_end < len(accepted_lines):
        accepted_text += "\n".join(accepted_lines[section_end:]) + "\n"

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    if f'<a id="{ANCHOR}"></a>' in process_text:
        raise ValueError("process anchor already exists")
    process_note = f'''\n\n<a id="{ANCHOR}"></a>
### S3–S4 person：四个直接关系端点组裁决与登记（2026-10-19）

本批核查四个已有S3 `new` 决定，四组均与现有同类型人物KU区分并完成S4登记。除Carlo Emanuele III新增一条Treccani DBI身份记录外，未新增外部身份配对。身份核验不等于原书关系断言已验证。

| 候选 | S3身份组 | S4去向 | S2关系候选 |
|---|---|---|---|
| `cand-2685` | `new-person:della-filippo-valle-b6ab7ea511` | `units/persons/filippo-della-valle` | `st-chp3-seciv-l179-187-della-valle-made-annunciation-relief` |
| `cand-2700` | `new-person:salvator-varda-c4461bbddc` | `units/persons/salvator-varda` | `st-chp9-p263264-will-gifts-to-varda` |
| `cand-7353` | `new-person:carlo-emanuele-iii-of-savoy-a69e3c8f1b` | `units/persons/carlo-emanuele-iii-of-savoy` | `st-chp7-p201-n2-eugene-collection-acquired` |
| `cand-5833` | `new-person:de-laroque-tamizey-ce365919cd` | `units/persons/tamizey-de-laroque` | `st-chp4-sec-ii-notes-l265-268-fn265-publication` |

- **Filippo della Valle：** 第3章 p.93 line 185明示全名及其与Pietro Bracci共同制作《天使报喜》大理石浅浮雕的原书说法。既有Bracci卡记载相同书内陈述，但不是另一张Filippo KU；未发现同类型既有KU。登记新人物卡，保留statement供S6审查；不独立核验作品或正式关系。
- **Salvator Varda：** 第9章注释续段页图可读作“Sig. Salvator Varda”，所以保留原书读法，不当作OCR误认。现有Salvator Rosa卡不是该拼写的直接身份依据，故不合并；目前也没有证据断言二人必为不同个体。按书内source-local身份登记新KU，遗嘱和友人关系仍待S6。
- **Carlo Emanuele III of Savoy：** Treccani DBI条目将其列为Vittorio Amedeo II之子并记其1730年继位，支持其为独立人物而非父亲别名；身份记录写入alignment外部身份行。Haskell关于其购得Prince Eugene收藏“大部分”的说法仍属原书转述，Treccani身份条目不验证该交易。
- **Tamizey de Laroque：** 第4章 p.108写“Tamizey de Laroque”；第21章 p.438书目列“P. Tamizey de Larroque”及1886年文章。保留拼写异文，不扩写首字母P，不把书目条目与注释所指刊布记录认定为已证同一事件；对应和关系留待S6。

四张卡分别为[Filippo della Valle](../../../04-knowledge/units/persons/filippo-della-valle.md)、[Salvator Varda](../../../04-knowledge/units/persons/salvator-varda.md)、[Carlo Emanuele III](../../../04-knowledge/units/persons/carlo-emanuele-iii-of-savoy.md)和[Tamizey de Laroque](../../../04-knowledge/units/persons/tamizey-de-laroque.md)。本批未新增formal relation或enrichment；四条原书关系候选保留待S6。

本批后S3决定数不变：same=1,973（1,052个既有KU）、new=5,020／4,811组、conflict=9、excluded=100、undecided=5,305。S4由1,177组／1,365条映射增至1,181组／1,369条；待登记由3,634组／3,655条降至3,630组／3,651条。直接关系端点队列由1,879组／1,879条降至1,875组／1,875条，其中person由35／35降至31／31。KU=2,200；alignment行数=12,709，其中候选决定12,407、外部身份记录302。'''
    process_text = process_text.rstrip() + process_note

    updates = {
        alignment_path: write_csv(alignment_headers, alignments),
        manifest_path: write_csv(manifest_headers, manifest),
        accepted_path: accepted_text,
        PROCESS: process_text,
        **output_cards,
    }
    print(f"dry-run planned: 4 new person KUs; alignment rows={len(alignments)}; external identity row={external_id}; S4=1181/1369 registered, 3630/3651 pending; direct endpoints=1875/1875; no formal relations")
    if args.dry_run:
        return 0
    for path, text in updates.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        encoding = "utf-8-sig" if path == accepted_path else "utf-8"
        path.write_text(text, encoding=encoding, newline="\n")
    print(f"applied: files={len(updates)}; process_ref={PROCESS_REF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
