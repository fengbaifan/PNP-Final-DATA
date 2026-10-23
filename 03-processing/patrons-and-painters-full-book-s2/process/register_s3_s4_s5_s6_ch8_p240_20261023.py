"""Review p.240 S2, group triggered identities, register endpoints and relations."""
from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import io
import json
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.build_field_facts import assign_ids, extract_records  # noqa: E402

TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_DIR = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
REVIEW_PATH = PROCESS_DIR / "s2-independent-review-chp8-p240-20261023.md"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
SOURCE_ID = "haskell-1980-rev-ed"
HASKELL_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
ANCHOR = "s3-s4-s5-s6-ch8-p240-exhibition-venues-and-citations-20261023"
PROCESS_REF = f"03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR}"
TODAY = "2026-10-23"

KU = {
    "event": "units/events/florentine-art-exhibition-1706",
    "saint": "units/persons/saint-luke",
    "piazza": "units/places/piazza-del-duomo-florence",
    "chapel": "units/places/annunziata-chapel-of-saint-luke",
    "cloister": "units/places/ss-annunziata-cloister-florence",
    "catalogue": "units/archives/nota-de-quadri-florence-1706",
    "hugford": "units/archives/ignazio-enrico-hugford-vita-gabbiani-1762",
    "fogolari": "units/archives/fogolari-lettere-pittoriche-1937",
    "letter12": "units/archives/fogolari-letter-12-1698-06-07",
    "flight": "units/works/a-d-gabbiani-flight-into-egypt",
}

DISPLAY_NAME = {
    "event": ("佛罗伦萨1706年圣路加节展览", "Florentine Exhibition on St Luke's Day, 1706"),
    "saint": ("圣路加", "St Luke"),
    "piazza": ("佛罗伦萨主教座堂广场", "Piazza del Duomo, Florence"),
    "chapel": ("圣母领报修道院回廊内的圣路加礼拜堂", "Chapel of St Luke in the Annunziata Cloister, Florence"),
    "cloister": ("佛罗伦萨圣母领报修道院回廊", "Cloister of the Monastery of the SS Annunziata, Florence"),
    "catalogue": (
        "《圣路加节展出绘画目录》（Nota de' Quadri che sono esposti per la festa di S. Luca …, Firenze 1706）",
        "Nota de' Quadri che sono esposti per la festa di S. Luca …, Firenze 1706",
    ),
    "hugford": (
        "《佛罗伦萨画家安东·多梅尼科·加比亚尼传》（Vita di Anton Domenico Gabbiani pittor fiorentino）",
        "Ignazio Enrico Hugford, Vita di Anton Domenico Gabbiani pittor fiorentino (Firenze 1762)",
    ),
    "fogolari": (
        "《托斯卡纳大亲王斐迪南致尼科洛·卡萨纳绘画书信》（Lettere pittoriche …, 1937）",
        "Gino Fogolari, Lettere pittoriche del Gran Principe Ferdinando di Toscana a Niccolò Cassana (1937)",
    ),
    "letter12": ("Fogolari所刊第12号信（1698年6月7日）", "Fogolari (1937), Letter 12 (7 June 1698)"),
    "flight": ("《逃往埃及》（安东·多梅尼科·加比亚尼）", "Flight into Egypt (by Anton Domenico Gabbiani)"),
}


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader), bom, newline


def render_csv(fields, rows, bom, newline):
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    payload = handle.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" if bom else b"") + payload


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def render_jsonl(rows, bom=False, newline="\n"):
    payload = newline.join(json.dumps(row, ensure_ascii=False) for row in rows) + newline
    encoded = payload.encode("utf-8")
    return (b"\xef\xbb\xbf" if bom else b"") + encoded


def atomic_write(path: Path, payload: bytes):
    temporary = path.with_name(path.name + ".codex-tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def primary_alignment(rows, candidate_id):
    matches = [row for row in rows if row["candidate_id"] == candidate_id and not row["external_source"]]
    if len(matches) != 1:
        raise ValueError(f"expected one primary alignment for {candidate_id}; found {len(matches)}")
    return matches[0]


def group_id(row):
    match = re.search(r"(?:^|;\s*)group=([^;]+)", row.get("resolution_note", ""))
    return match.group(1) if match else ""


def accepted_with(paths):
    path = ROOT / "04-knowledge" / "accepted.yml"
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "units:":
        raise ValueError("accepted.yml does not begin with units:")
    entries = {line.strip()[2:].strip() for line in lines if line.lstrip().startswith("-")}
    if any(path in entries for path in paths):
        raise ValueError("one or more new cards already appear in accepted.yml")
    for card_path in sorted(paths):
        insert_at = next(
            (i for i, line in enumerate(lines)
             if line.lstrip().startswith("-") and line.strip()[2:].strip() > card_path),
            next((i for i, line in enumerate(lines) if line.strip() == "claims:"), len(lines)),
        )
        lines.insert(insert_at, f"- {card_path}{newline}")
    return (b"\xef\xbb\xbf" if bom else b"") + "".join(lines).encode("utf-8")


def quote(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def source_block(location, summary, span, text, source_file=SOURCE_REL):
    return {
        "citation": HASKELL_CITATION,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": text}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": source_file, "source_span": span},
    }


def card_text(key, description_zh, description_en, fields, sources, relation_note):
    chinese, english = DISPLAY_NAME[key]
    frontmatter = {
        "title": f"{chinese}（{english}）",
        "name_en": english,
        "type": KU[key].split("/")[1][:-1] if KU[key].split("/")[1].endswith("s") else KU[key].split("/")[1],
        "evidence_status": "source_backed",
        "sources": sources,
        "created": TODAY,
        "updated": TODAY,
        "process_ref": PROCESS_REF,
    }
    if key == "catalogue":
        frontmatter["sub_type"] = "printed exhibition catalogue"
    if key in {"hugford", "fogolari", "letter12"}:
        frontmatter["sub_type"] = "book" if key == "hugford" else ("journal article" if key == "fogolari" else "letter citation locator")
    if key == "flight":
        frontmatter["evidence_status"] = "source_backed"
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=120)
    fm = "---\n" + fm.rstrip() + "\n---\n"
    body = [
        "",
        "## 内容",
        "",
        "### 描述",
        "",
        f"**中文：** {description_zh}",
        "",
        f"**English:** {description_en}",
    ]
    if fields:
        body += ["", "### 基本信息", "", "| 字段 | 内容 | 依据 |", "|---|---|---|"]
        for field, value, evidence in fields:
            body.append(f"| {field} | {value} | {evidence} |")
    body += ["", "## 关系与证据", "", relation_note, ""]
    return fm + "\n".join(body)


def card_specs():
    evidence = "S1；Haskell第8章印刷页240，PDF物理页46"
    note_evidence = "S1；Haskell第8章印刷页240注释，PDF物理页46"
    bib_evidence = "S1；Haskell第21章书目"
    return {
        "event": {
            "description_zh": "记录哈斯克尔所述佛罗伦萨1706年圣路加节绘画展览。第20章后记将其与1705年展览区分，并修正斐迪南在展览史中的先驱作用；本卡不把他写成唯一组织者。展览地点按书内称谓链接到[圣路加礼拜堂](../places/annunziata-chapel-of-saint-luke.md)及[圣母领报修道院回廊](../places/ss-annunziata-cloister-florence.md)。",
            "description_en": "This unit records Haskell's Florentine picture exhibition associated with St Luke's Day in 1706. The postscript distinguishes it from the 1705 exhibition and qualifies Ferdinand's pioneering role; this card does not make him its sole organizer. The reported venue is linked to the [Chapel of St Luke](../places/annunziata-chapel-of-saint-luke.md) and the [SS Annunziata cloister](../places/ss-annunziata-cloister-florence.md).",
            "fields": [
                ("日期", "1706年圣路加节（10月18日；年份由相邻的1706年展览叙述限定）", evidence + "；L357–359"),
                ("展出规模", "约250幅画作；哈斯克尔称其中几乎全部借自佛罗伦萨的大型收藏", evidence + "；L452"),
                ("来源限定", "哈斯克尔称展品没有来自大公收藏；保留为展览内容陈述，不把“大公”推定为具体借出关系端点", evidence + "；L452"),
            ],
            "sources": [
                source_block("第8章；印刷页240；L357–359, L452", "展览、日期、地点及展出规模。", "Chapter 8, printed p.240, L357–359 and L452", "by 1706 he had already organised something far grander. The exhibition was held on St Luke’s day (18 October) in the chapel dedicated to that saint in the cloisters of the Annunziata. About 250 pictures were shown"),
                source_block("第20章后记；印刷页404；L131", "哈斯克尔修正自己对斐迪南在展览史中作用的先前判断。", "Chapter 20, printed p.404, L131", "the Prince’s part in organising the one held in 1706 (though the discovery of a catalogue for the exhibition of 1705 shows that I somewhat exaggerated his role in inaugurating this aspect of the exhibition)"),
            ],
            "relation_note": "S6关系按 `relations.csv` 记录；位置、参与者及其范围均见对应关系行。第8章称斐迪南组织较大展览，第20章保留其参与而修正其先驱性，不推定唯一组织者。",
        },
        "saint": {
            "description_zh": "同一人物锚点在第1章节日语境、第3章福音书语境及第8章圣路加节／礼拜堂奉献语境中均称 St Luke。此处只合并书内同一圣徒指称，不补写传记或外部身份事实。",
            "description_en": "Haskell refers to St Luke in the chapter 1 feast-day context, chapter 3 Gospel context, and chapter 8 feast-day and chapel-dedication context. This unit groups the same saint named in the book and adds no biography or externally verified identity facts.",
            "fields": [("书内指称", "St Luke；第1章节日、第3章福音书及第8章节日／奉献语境", "S1；第1章L688、第3章L141–150、第8章p.240 L358–359及注5")],
            "sources": [
                source_block("第1章；L688", "节日语境中的St Luke。", "Chapter 1, L688", "St Luke", "02-sources/02-Markdown/01_CHP-1_sec_ii.md"),
                source_block("第3章；L141–150", "福音书语境中的St Luke。", "Chapter 3, L141–150", "St Luke", "02-sources/02-Markdown/03_CHP-3_sec_iv.md"),
                source_block("第8章；印刷页240；L358–359及注5", "圣路加节与奉献给该圣人的礼拜堂。", "Chapter 8, printed p.240, L358–359 and note 5", "St Luke’s day (18 October) in the chapel dedicated to that saint", SOURCE_REL),
            ],
            "relation_note": "未创建 chapel → Saint Luke 的正式关系：当前 `dedicated_to` 域值域只接受 work → person；来源中的礼拜堂奉献事实保留在地点卡字段，不绕过矩阵。",
        },
        "piazza": {
            "description_zh": "第8章把 Piazza del Duomo 记作 Ferdinand 将加比亚尼《逃往埃及》向公众展示的地点。仅记录哈斯克尔的书内称谓，不补充现代广场身份、建筑边界或展示日期。",
            "description_en": "Chapter 8 names the Piazza del Duomo as the place where Ferdinand put Gabbiani's Flight into Egypt on public view. This unit records Haskell's wording only and adds no modern site identification, architectural boundary, or display date.",
            "fields": [("书内地点称谓", "Piazza del Duomo；未由本书段落进一步限定现代地点身份", evidence + "；L356")],
            "sources": [source_block("第8章；印刷页240；L356", "Ferdinand公开展示加比亚尼《逃往埃及》的地点。", "Chapter 8, printed p.240, L356", "Gabbiani, whose Flight into Egypt he put on view to the public in the Piazza del Duomo", SOURCE_REL)],
            "relation_note": "S6记录该作品的书内报告展示地点；本卡不将“展出地点”扩展为永久安置或现存位置。",
        },
        "chapel": {
            "description_zh": "哈斯克尔称1706年展览在圣路加节举行于圣母领报修道院回廊内、奉献给圣路加的礼拜堂。对象范围限于书内所指礼拜堂，不与修道院整体或回廊合并。",
            "description_en": "Haskell places the 1706 St Luke's Day exhibition in a chapel dedicated to St Luke within the Annunziata cloisters. This unit is limited to the chapel named in the book and remains distinct from the monastery and its cloister.",
            "fields": [("空间称谓", "奉献给圣路加、位于圣母领报修道院回廊内的礼拜堂", evidence + "；L358–359"), ("地点边界", "内部礼拜堂；与修道院回廊作为不同建筑空间记录", evidence + "；L359及注5")],
            "sources": [source_block("第8章；印刷页240；L358–359及注5", "展览礼拜堂及其与Annunziata回廊的空间关系。", "Chapter 8, printed p.240, L358–359 and note 5", "in the chapel dedicated to that saint in the cloisters of the Annunziata", SOURCE_REL)],
            "relation_note": "与1706年展览的 `occurred_at` 关系见 `relations.csv`；礼拜堂奉献对象保留为书内字段。",
        },
        "cloister": {
            "description_zh": "哈斯克尔称礼拜堂位于Annunziata回廊，并称画作悬挂于回廊的lunettes。注5目录题名写作“Chiostro del Monastero de' Padri della SS. Nonziata di Firenze”；保留扫描可读拼写，不据外部资料校正。",
            "description_en": "Haskell locates the chapel in the Annunziata cloisters and says pictures were hung in the cloister lunettes. Note 5 gives the catalogue wording “Chiostro del Monastero de' Padri della SS. Nonziata di Firenze”; the scan's readable spelling is retained without external normalization.",
            "fields": [("书内称谓", "cloisters of the Annunziata；注5目录标题作 Chiostro del Monastero … della SS. Nonziata di Firenze", evidence + "；L359、L452、注5")],
            "sources": [source_block("第8章；印刷页240；L359、L452及注5", "展览所在回廊及目录标题中的空间称谓。", "Chapter 8, printed p.240, L359, L452 and note 5", "in the cloisters of the Annunziata", SOURCE_REL)],
            "relation_note": "与1706年展览在回廊内的活动关系见 `relations.csv`；回廊与内部礼拜堂保持为两个 place KU。",
        },
        "catalogue": {
            "description_zh": "记录哈斯克尔第8章注5所引的1706年佛罗伦萨印刷展览目录。意大利语题名按扫描可读文字保留；目录原件及外部书目未查。",
            "description_en": "This unit records the printed exhibition catalogue cited in Haskell's chapter 8 note 5 for the 1706 Florence exhibition. The Italian title follows the readable scan; neither the catalogue itself nor external catalogues were consulted.",
            "fields": [("意大利语题名", "Nota de’ Quadri che sono esposti per la festa di S. Luca dagli accademici del disegno nella loro cappella posta nel Chiostro del Monastero de' Padri della SS. Nonziata di Firenze l’Anno 1706", note_evidence + "；L456，按扫描校读 I’Anno→l’Anno"), ("出版项", "In Firenze 1706", note_evidence + "；L456")],
            "sources": [source_block("第8章；印刷页240；注5 L456", "目录题名与佛罗伦萨1706年出版项。", "Chapter 8, printed p.240, note 5, L456", "The catalogue is called Nota de’ Quadri che sono esposti per la festa di S. Luca dagli accademici del disegno nella loro cappella posta nel Chiostro del Monastero de' Padri della SS. Nonziata di Firenze l’Anno 1706. In Firenze 1706.", SOURCE_REL)],
            "relation_note": "Haskell《赞助人与画家》对该目录的书内引用记录为 `cites`；目录与展览的“可据以重建”陈述不另造未受控谓词。",
        },
        "hugford": {
            "description_zh": "记录哈斯克尔第8章注2所引的Hugford著作。第21章书目提供作者、意大利语题名及1762年佛罗伦萨出版项；注2定位第10页。该页及原书未独立查阅。",
            "description_en": "This unit records the Hugford work cited in Haskell's chapter 8 note 2. Chapter 21 supplies its author, Italian title, and Florence 1762 publication statement; note 2 locates page 10. The page and book were not independently consulted.",
            "fields": [("书目题名", "Ignazio Enrico Hugford, Vita di Anton Domenico Gabbiani pittor fiorentino", bib_evidence + "；L626"), ("出版项", "Firenze 1762；Haskell第8章注2另定位p.10", bib_evidence + "；L626；第8章p.240注2")],
            "sources": [source_block("第8章；印刷页240；注2 L454", "书内引注Hugford第10页。", "Chapter 8, printed p.240, note 2, L454", "Hugford, p. 10", SOURCE_REL), source_block("第21章书目；L626", "作者、题名及出版项。", "Chapter 21 bibliography, L626", "Hugford, Ignazio Enrico: Vita di Anton Domenico Gabbiani pittor fiorentino, Firenze 1762", "02-sources/02-Markdown/21_CHP-21Bibliography.md")],
            "relation_note": "本书对该书的引注由 `cites` 记录；不以被引关系声称已读Hugford第10页。",
        },
        "fogolari": {
            "description_zh": "记录哈斯克尔第8章注1所引的Gino Fogolari 1937年文章。第21章书目给出题名、期刊及145–186页；本卡只确认书目身份和书内引注，不声称读过该文章或其所引页。",
            "description_en": "This unit records Gino Fogolari's 1937 article cited in Haskell's chapter 8 note 1. Chapter 21 provides the title, journal, and pages 145–186. This card confirms the bibliographic identity and Haskell's citation only; it does not claim that the article or cited page was read.",
            "fields": [("书目题名", "Gino Fogolari, Lettere pittoriche del Gran Principe Ferdinando di Toscana a Niccolò Cassana (1698–1709)", bib_evidence + "；L485"), ("出版项", "Rivista del R. Istituto d’Archeologia e Storia dell’Arte, 1937, pp.145–186", bib_evidence + "；L485")],
            "sources": [source_block("第8章；印刷页240；注1 L453", "注1引Fogolari 1937第161页注43。", "Chapter 8, printed p.240, note 1, L453", "Fogolari, 1937, p. 161, note 43", SOURCE_REL), source_block("第21章书目；L485", "题名、期刊及页码。", "Chapter 21 bibliography, L485", "Fogolari, Gino: ‘Lettere pittoriche del Gran Principe Ferdinando di Toscana a Niccolò Cassana (1698-1709)’ in Rivista del R. Istituto d’Archeologia e Storia dell’Arte, 1937, pp. 145-186", "02-sources/02-Markdown/21_CHP-21Bibliography.md")],
            "relation_note": "Haskell对该文章的书内引注由 `cites` 记录；文章正文及注1所引页面未独立查阅。",
        },
        "letter12": {
            "description_zh": "记录哈斯克尔通过Fogolari 1937年文章定位的第12号信件（1698年6月7日）。身份仅限于这一书内引注对象；不据此推定原件馆藏、物理见证或已读刊本。",
            "description_en": "This unit records the Letter 12 locator dated 7 June 1698 that Haskell cites through Fogolari's 1937 publication. Its identity is limited to this in-book citation; no repository, physical witness, or consultation of the publication is inferred.",
            "fields": [("书内信件定位", "Fogolari (1937), Letter 12", note_evidence + "；L454"), ("书内所报日期", "1698年6月7日", note_evidence + "；L454")],
            "sources": [source_block("第8章；印刷页240；注3 L454", "给出Fogolari 1937第12号信及日期。", "Chapter 8, printed p.240, note 3, L454", "Fogolari, 1937, Letter 12 of 7 June 1698", SOURCE_REL)],
            "relation_note": "本书对该信件定位对象的引用由 `cites` 记录；其与Fogolari文章的出版关系不据此另建未经审查的边。",
        },
        "flight": {
            "description_zh": "记录哈斯克尔所称加比亚尼《逃往埃及》，并记其曾被Ferdinand公开展示于Piazza del Duomo。画作没有在此获得外部作品身份核验；展示日期也未由该句给出。",
            "description_en": "This unit records Haskell's Flight into Egypt associated with Gabbiani and reports that Ferdinand put it on public view at the Piazza del Duomo. No external object identity is verified here, and the sentence supplies no display date.",
            "fields": [("原文作品称谓", "Gabbiani’s Flight into Egypt", evidence + "；L356"), ("展示限定", "哈斯克尔称Ferdinand曾将其向公众展示于Piazza del Duomo；未给此展示的日期", evidence + "；L356")],
            "sources": [source_block("第8章；印刷页240；L355–356", "Ferdinand的展示政策及加比亚尼作品的公开展示地点。", "Chapter 8, printed p.240, L355–356", "Gabbiani, whose Flight into Egypt he put on view to the public in the Piazza del Duomo", SOURCE_REL)],
            "relation_note": "正式展示地点关系为书内报告的 `located_at`，不表示永久安置；作者归属按Haskell所用称谓保留。",
        },
    }


def mention_row(mention_id, segment_id, candidate_id, line_number, surface, note, source_lines, segment_first):
    segment = "\n".join(source_lines[segment_first - 1:line_number])
    line_offset = sum(len(line) + 1 for line in source_lines[segment_first - 1:line_number - 1])
    line = source_lines[line_number - 1]
    idx = line.find(surface)
    if idx < 0 or line.find(surface, idx + 1) >= 0:
        raise ValueError(f"mention surface is absent or ambiguous on L{line_number}: {surface!r}")
    start = line_offset + idx
    return {
        "mention_id": mention_id,
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    }


def add_ocr(row, corrections):
    q = row.setdefault("qualifiers", {})
    existing = q.setdefault("ocr_corrections", [])
    for item in corrections:
        if item not in existing:
            existing.append(item)


def card_source_spans(key):
    return {
        "event": {"event_date": "L357–359", "exhibition_count": "L452", "source_limit": "L452", "role": "ch.20 L131"},
        "saint": {"identity": "ch.1 L688; ch.3 L141–150; ch.8 L358–359"},
        "piazza": {"location": "L356"},
        "chapel": {"space": "L358–359; n.5"},
        "cloister": {"name": "L359; L452; n.5"},
        "catalogue": {"title": "n.5 L456", "publication": "n.5 L456"},
        "hugford": {"bibliography": "ch.21 L626", "locator": "n.2 L454"},
        "fogolari": {"bibliography": "ch.21 L485", "locator": "n.1 L453"},
        "letter12": {"locator": "n.3 L454", "date": "n.3 L454"},
        "flight": {"title": "L356", "display": "L356"},
    }[key]


def build_plan():
    plans: dict[Path, bytes] = {}

    candidates_path = TABLES / "entity-candidates.csv"
    candidate_fields, candidates, candidate_bom, candidate_nl = read_csv(candidates_path)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    required_candidates = {"cand-3564", "cand-7871", "cand-7894", "cand-7929", "cand-7977", "cand-8065", "cand-8066", "cand-8067", "cand-8068", "cand-8069", "cand-8071", "cand-8072", "cand-1093", "cand-1095", "cand-11046"}
    if required_candidates - candidate_by_id.keys():
        raise ValueError(f"missing S1 candidates: {sorted(required_candidates - candidate_by_id.keys())}")

    manifest_path = TABLES / "ku-manifest.csv"
    manifest_fields, manifest, manifest_bom, manifest_nl = read_csv(manifest_path)
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    for key, ku in KU.items():
        if ku in manifest_by_id or (ROOT / "04-knowledge" / f"{ku}.md").exists():
            raise ValueError(f"new KU target already exists: {ku}")

    alignment_path = TABLES / "alignment.csv"
    alignment_fields, alignments, alignment_bom, alignment_nl = read_csv(alignment_path)
    align_by_candidate = {c: primary_alignment(alignments, c) for c in required_candidates}
    expected_states = {
        "cand-3564": ("aln-3748", "undecided"),
        "cand-7871": ("aln-8046", "new"),
        "cand-7894": ("aln-8069", "new"),
        "cand-7929": ("aln-8104", "undecided"),
        "cand-7977": ("aln-8152", "undecided"),
        "cand-8065": ("aln-8240", "undecided"),
        "cand-8066": ("aln-8241", "new"),
        "cand-8067": ("aln-8242", "undecided"),
        "cand-8068": ("aln-8243", "undecided"),
        "cand-8069": ("aln-8244", "new"),
        "cand-8071": ("aln-8246", "undecided"),
        "cand-1093": ("aln-1428", "same"),
        "cand-1095": ("aln-1430", "undecided"),
    }
    for candidate_id, (alignment_id, decision) in expected_states.items():
        row = align_by_candidate[candidate_id]
        if row["alignment_id"] != alignment_id or row["decision"] != decision:
            raise ValueError(f"S3 state changed for {candidate_id}: {row['alignment_id']}:{row['decision']}")
    event_base = align_by_candidate.get("cand-11046")
    if not event_base or event_base["decision"] != "new" or group_id(event_base) != "sg3-event-florentine-art-exhibition-1706":
        raise ValueError("the existing cross-chapter event group cand-11046 is not in its expected S3 new state")
    if event_base["ku_id"]:
        raise ValueError("the event group was already registered; re-review before applying")
    if align_by_candidate["cand-8072"]["decision"] != "undecided":
        raise ValueError("aggregate picture candidate changed; re-review before applying")

    statements_path = TABLES / "book-statements.jsonl"
    statements_raw = statements_path.read_bytes()
    statements_bom = statements_raw.startswith(b"\xef\xbb\xbf")
    statements_newline = "\r\n" if b"\r\n" in statements_raw else "\n"
    statements = read_jsonl(statements_path)
    by_statement = {row["statement_id"]: row for row in statements}
    required_statements = {
        "st-chp8-p240-1706-exhibition-and-san-rocco",
        "st-chp8-p240-catalogue-and-reconstruction",
        "st-chp8-p240-exhibition-as-art-direction",
        "st-chp8-p240-exhibition-count-and-loan-sources",
        "st-chp8-p240-exhibition-date-and-venue",
        "st-chp8-p240-ferdinand-displays-gabbiani",
        "st-chp8-p240-lunette-display",
        "st-chp8-p240-no-pictures-from-grand-duke",
        "st-chp8-p240-note1-fogolari-mehus-acquisition",
        "st-chp8-p240-note2-hugford-locator",
        "st-chp8-p240-note3-fogolari-letter12",
        "st-chp8-p240-note4-fogolari-letter120",
        "st-chp8-p240-note5-catalogue-title",
        "st-chp8-p240-pictures-borrowed-from-florence",
        "st-chp8-p240-grand-prince-portrait-display-location",
    }
    if required_statements - by_statement.keys():
        raise ValueError(f"missing S2 statements: {sorted(required_statements - by_statement.keys())}")
    if any(row.get("qualifiers", {}).get("printed_page") == 240 for row in statements if row.get("statement_id") in {"st-chp8-p240-patronage-beyond-collecting", "st-chp8-p240-ferdinand-regular-display-policy"}):
        raise ValueError("one or more planned S2 statements already exist")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    body_segment = "chp-8:08_CHP-8_sec_ii:l350-359"
    note_segment = "chp-8:08_CHP-8_sec_ii:l372-461"
    new_mentions = [
        mention_row("m-chp8-p240-event-1706", body_segment, "cand-7977", 357, "something far grander", "Anaphoric reference to the larger exhibition dated in this paragraph to 1706; linked to the cross-chapter event candidate.", source_lines, 350),
        mention_row("m-chp8-p240-flight-title", body_segment, "cand-1095", 356, "Flight into Egypt", "Named work in Haskell's report of public display.", source_lines, 350),
        mention_row("m-chp8-p240-gabbiani-person", body_segment, "cand-1093", 356, "Gabbiani", "Artist named in connection with the Flight into Egypt; S3 maps to the existing person KU.", source_lines, 350),
        mention_row("m-chp8-p240-piazza", body_segment, "cand-8065", 356, "Piazza del Duomo", "Explicit public-display place named by Haskell.", source_lines, 350),
        mention_row("m-chp8-p240-saint-luke-day", body_segment, "cand-8066", 358, "St Luke’s day", "Feast-day name for the same St Luke referenced in chapters 1 and 3.", source_lines, 350),
        mention_row("m-chp8-p240-chapel", body_segment, "cand-8067", 359, "chapel dedicated to that saint", "Specific internal chapel; kept distinct from the surrounding cloister.", source_lines, 350),
        mention_row("m-chp8-p240-saint-luke-dedication", body_segment, "cand-8066", 359, "that saint", "Anaphoric dedication reference to St Luke's day in the preceding sentence.", source_lines, 350),
        mention_row("m-chp8-p240-cloisters", body_segment, "cand-8068", 359, "cloisters of the Annunziata", "Distinct parent architectural space named separately from the chapel.", source_lines, 350),
        mention_row("m-chp8-p240-note1-fogolari", note_segment, "cand-7894", 453, "Fogolari, 1937", "Cited article; the p.161 locator is recorded in the same footnote.", source_lines, 372),
        mention_row("m-chp8-p240-note2-hugford", note_segment, "cand-7871", 454, "Hugford", "Cited book and page 10 locator.", source_lines, 372),
        mention_row("m-chp8-p240-note3-letter12", note_segment, "cand-7929", 454, "Letter 12", "Specific letter locator and date in Haskell's citation.", source_lines, 372),
        mention_row("m-chp8-p240-note5-catalogue", note_segment, "cand-8069", 456, "Nota de’ Quadri", "Printed catalogue title named in footnote 5.", source_lines, 372),
        mention_row("m-chp8-p240-note5-saint-luke", note_segment, "cand-8066", 456, "S. Luca", "Italian feast-day name within the catalogue title.", source_lines, 372),
        mention_row("m-chp8-p240-note5-cloister", note_segment, "cand-8068", 456, "Chiostro del Monastero de' Padri della SS. Nonziata di Firenze", "Catalogue title's wording for the cloister; scan spelling retained.", source_lines, 372),
        mention_row("m-chp8-p240-note5-firenze-title", note_segment, "cand-1041", 456, "di Firenze", "Place wording at the end of the catalogue title.", source_lines, 372),
        mention_row("m-chp8-p240-note5-firenze-imprint", note_segment, "cand-1041", 456, "In Firenze", "Place wording in the imprint following the catalogue title.", source_lines, 372),
        mention_row("m-chp8-p240-picture-count", note_segment, "cand-8072", 452, "250 pictures", "Aggregate exhibition count; retained as an S1 mention anchor and excluded from KU identity because it is not an independently identifiable work.", source_lines, 372),
        mention_row("m-chp8-p240-portrait", note_segment, "cand-8071", 452, "a portrait of the Grand Prince", "Source-defined portrait identified by sitter and display position only; identity remains unresolved.", source_lines, 372),
    ]
    mentions_path = TABLES / "mentions.csv"
    mention_fields, mentions, mention_bom, mention_nl = read_csv(mentions_path)
    existing_mentions = {row["mention_id"] for row in mentions}
    if existing_mentions.intersection(row["mention_id"] for row in new_mentions):
        raise ValueError("one or more planned S2 mention IDs already exist")
    mentions.extend(new_mentions)
    plans[mentions_path] = render_csv(mention_fields, mentions, mention_bom, mention_nl)

    # Recheck the scan against S0 transcription without changing the source asset.
    add_ocr(by_statement["st-chp8-p240-exhibition-as-art-direction"], [
        {"source_line": 355, "ocr": "instrumentof", "print": "instrument of", "basis": "CHP-8.pdf physical page 46"},
    ])
    by_statement["st-chp8-p240-exhibition-as-art-direction"]["original_quote"] = (
        "He was also anxious to guide the whole direction taken by painters in the Florence of his day. "
        "For this purpose he took advantage of the still rudimentary instrumentof the art exhibition and used it in an entirely new way."
    )
    by_statement["st-chp8-p240-catalogue-and-reconstruction"]["original_quote"] = (
        "A printed catalogue was issued—and this in itself was an innovation for Italy.5 From this catalogue we can reconstruct the event."
    )
    by_statement["st-chp8-p240-catalogue-and-reconstruction"]["qualifiers"]["relation_candidate"] = False
    by_statement["st-chp8-p240-catalogue-and-reconstruction"]["qualifiers"]["relation_candidate_note"] = (
        "This is a source claim that the catalogue enabled reconstruction of the event. The bibliographic book-to-catalogue citation is separately represented by note 5 as a controlled cites relation; no unsupported event-to-catalogue predicate is emitted."
    )

    note1 = by_statement["st-chp8-p240-note1-fogolari-mehus-acquisition"]
    note1["subject_candidate_id"], note1["object_candidate_id"], note1["predicate"] = "cand-2962", "cand-7894", "cites"
    note1["original_quote"] = "1 Fogolari, 1937, p. l6l, note 43, for Ricci acquiring works by Mehus for Ferdinand."
    note1["qualifiers"].update({
        "claim": "Haskell note 1 cites Fogolari's 1937 article, page 161, note 43, concerning Ricci's acquisition of works by Mehus for Ferdinand.",
        "qualification": "Citation only; the article and cited page were not independently consulted.",
        "mentioned_candidate_ids": ["cand-2962", "cand-7894"],
        "relation_candidate": True,
        "relation_candidate_note": "The source explicitly cites the 1937 article; this records Haskell's bibliographic act, not the truth of the cited claim.",
    })
    add_ocr(note1, [{"source_line": 453, "ocr": "p. l6l", "print": "p. 161", "basis": "CHP-8.pdf physical page 46"}])

    note2 = by_statement["st-chp8-p240-note2-hugford-locator"]
    note2["subject_candidate_id"], note2["object_candidate_id"], note2["predicate"] = "cand-2962", "cand-7871", "cites"
    note2["original_quote"] = "2 Hugford, p. 10."
    note2["qualifiers"].update({
        "claim": "Haskell note 2 cites Hugford, page 10, in support of the Gabbiani display passage.",
        "qualification": "Citation only; Hugford's page 10 and the cited book were not independently consulted.",
        "mentioned_candidate_ids": ["cand-2962", "cand-7871"],
        "relation_candidate": True,
        "relation_candidate_note": "The citation is explicit; independent consultation is not required to record the book-to-book cites relation.",
    })

    note3 = by_statement["st-chp8-p240-note3-fogolari-letter12"]
    note3["subject_candidate_id"], note3["object_candidate_id"], note3["predicate"] = "cand-2962", "cand-7929", "cites"
    note3["original_quote"] = "3 Fogolari, 1937, Letter 12 of 7 June 1698."
    note3["qualifiers"].update({
        "mentioned_candidate_ids": ["cand-2962", "cand-7894", "cand-7929"],
        "qualification": "Haskell cites the letter through Fogolari's 1937 publication; neither the publication nor an original witness was independently consulted.",
        "relation_candidate": True,
        "relation_candidate_note": "The letter number and date identify a distinct source-local citation locator; physical witness and repository remain unspecified.",
    })

    note5 = by_statement["st-chp8-p240-note5-catalogue-title"]
    note5["subject_candidate_id"], note5["object_candidate_id"], note5["predicate"] = "cand-2962", "cand-8069", "cites"
    note5["qualifiers"].update({
        "claim": "Haskell note 5 cites the catalogue by its Italian title and gives the Firenze 1706 imprint; the title names the St Luke's Day display in the Annunziata cloister.",
        "qualification": "The scan reads l’Anno 1706; the catalogue itself and external catalogues were not consulted. The printed title spelling Nonziata is retained.",
        "mentioned_candidate_ids": ["cand-2962", "cand-8069", "cand-7977", "cand-8068", "cand-1041", "cand-3461", "cand-8066"],
        "relation_candidate": True,
        "relation_candidate_note": "The footnote is an explicit book-to-catalogue citation; the event-to-catalogue descriptive statement is not treated as a separate controlled edge.",
    })
    add_ocr(note5, [{"source_line": 456, "ocr": "I’Anno", "print": "l’Anno", "basis": "CHP-8.pdf physical page 46"}])

    gabbiani = by_statement["st-chp8-p240-ferdinand-displays-gabbiani"]
    gabbiani["subject_candidate_id"], gabbiani["object_candidate_id"] = "cand-1095", "cand-8065"
    gabbiani["predicate"] = "publicly_displayed_at_piazza_del_duomo_by_ferdinand"
    gabbiani["original_quote"] = "Gabbiani, whose Flight into Egypt he put on view to the public in the Piazza del Duomo."
    gabbiani["qualifiers"].update({
        "claim": "Haskell says Ferdinand put Gabbiani's Flight into Egypt on public view at the Piazza del Duomo.",
        "qualification": "The work attribution and display are Haskell's report; this sentence gives no display date and does not establish permanent location.",
        "mentioned_candidate_ids": ["cand-1093", "cand-1095", "cand-1609", "cand-8065"],
        "relation_candidate": True,
        "relation_candidate_note": "A specific work and public display place are named; S6 records only the source-reported physical display location.",
    })

    portrait = by_statement["st-chp8-p240-grand-prince-portrait-display-location"]
    portrait["object_candidate_id"] = "cand-8067"
    portrait["qualifiers"]["mentioned_candidate_ids"] = ["cand-8071", "cand-8067", "cand-8068"]
    portrait["qualifiers"]["qualification"] = "The portrait is placed above the chapel door; the chapel is within the Annunziata cloister. Work identity remains limited to sitter and display position."

    count = by_statement["st-chp8-p240-exhibition-count-and-loan-sources"]
    count["subject_candidate_id"], count["object_candidate_id"] = "cand-7977", None
    count["predicate"] = "exhibited_about_250_pictures"
    count["qualifiers"].update({"mentioned_candidate_ids": ["cand-7977"], "relation_candidate": False, "relation_candidate_note": "Approximate number of pictures is an event-content field, not a distinct work or KU-to-KU relation."})
    borrow = by_statement["st-chp8-p240-pictures-borrowed-from-florence"]
    borrow["subject_candidate_id"], borrow["object_candidate_id"] = "cand-7977", None
    borrow["predicate"] = "pictures_borrowed_mostly_from_florentine_collections"
    borrow["qualifiers"].update({"mentioned_candidate_ids": ["cand-7977", "cand-1041"], "relation_candidate": False, "relation_candidate_note": "This describes the exhibition's aggregate sources; no individual lending collection or endpoint is identified, so retain as an event field."})
    grand_duke = by_statement["st-chp8-p240-no-pictures-from-grand-duke"]
    grand_duke["subject_candidate_id"], grand_duke["object_candidate_id"] = "cand-7977", None
    grand_duke["predicate"] = "no_pictures_from_the_grand_dukes_collection"
    grand_duke["qualifiers"].update({"mentioned_candidate_ids": ["cand-7977", "cand-8073"], "relation_candidate": False, "relation_candidate_note": "Negative source statement retained as exhibition content; it does not create a positive edge or identify the unnamed Grand Duke as a relation endpoint."})

    # Candidate 8072 was an aggregate count, not an independently identifiable artwork group.
    candidate_by_id["cand-8072"]["status"] = "excluded"
    candidate_by_id["cand-8072"]["exclude_reason"] = "The approximately 250 pictures are an event-level count and aggregate source description, not an independently identifiable work KU; those source claims remain on the exhibition statement/card."
    # The S1 index sub-entry is a named work, not a second person candidate.
    candidate_by_id["cand-1095"]["canonical_name"] = "Flight into Egypt by Anton Domenico Gabbiani"
    candidate_by_id["cand-1095"]["detail"] = "Work sub-entry in G.csv#2; p.240 names the Flight into Egypt associated with Gabbiani and reports its public display at Piazza del Duomo."

    new_statements = [
        {
            "statement_id": "st-chp8-p240-patronage-beyond-collecting",
            "segment_id": body_segment,
            "subject_candidate_id": "cand-1609",
            "object_candidate_id": None,
            "predicate": "patronage_extended_beyond_collecting_and_favourite_artists",
            "qualifiers": {
                "source_line_start": 355, "source_line_end": 355, "printed_page": 240, "pdf_physical_page": 46,
                "claim": "Haskell says Ferdinand's patronage was not confined to increasing his own collection or supporting artists who took his fancy.",
                "speaker": "Haskell", "text_layer": "body",
                "qualification": "This is a narrative characterization of patronage scope; the following sentence separately identifies exhibition use as a means of guiding Florentine painting.",
                "mentioned_candidate_ids": ["cand-1609"], "relation_candidate": False,
                "relation_candidate_note": "Characterization of one person's patronage scope, not a KU-to-KU relation.",
                "ocr_corrections": [{"source_line": 355, "ocr": "confmed", "print": "confined", "basis": "CHP-8.pdf physical page 46"}],
            },
            "original_quote": "But Ferdinand’s activities as patron were not confmed to increasing his own collection or supporting those particular artists who took his fancy.",
            "origin": "book", "source_file": SOURCE_REL,
        },
        {
            "statement_id": "st-chp8-p240-ferdinand-regular-display-policy",
            "segment_id": body_segment,
            "subject_candidate_id": "cand-1609",
            "object_candidate_id": None,
            "predicate": "regularly_showed_works_of_artists_he_approved",
            "qualifiers": {
                "source_line_start": 355, "source_line_end": 355, "printed_page": 240, "pdf_physical_page": 46,
                "claim": "Haskell says Ferdinand regularly showed works painted for him by artists of whom he approved.",
                "speaker": "Haskell", "text_layer": "body",
                "qualification": "General display practice; the Gabbiani example and its physical display site are recorded separately.",
                "mentioned_candidate_ids": ["cand-1609", "cand-1093"], "relation_candidate": False,
                "relation_candidate_note": "General practice statement, not a specific KU-to-KU relation.",
            },
            "original_quote": "and Ferdinand regularly showed works painted for him by those artists of whom he approved, such as",
            "origin": "book", "source_file": SOURCE_REL,
        },
    ]
    statements.extend(new_statements)
    plans[statements_path] = render_jsonl(statements, statements_bom, statements_newline)
    plans[candidates_path] = render_csv(candidate_fields, candidates, candidate_bom, candidate_nl)

    # S2 row-level report. Every existing p.240 statement is listed and the materially changed rows are explained.
    p240_rows = [row for row in statements if (row.get("qualifiers") or {}).get("printed_page") == 240]
    if len(p240_rows) != 40:
        raise ValueError(f"expected 40 p.240 statements after two atomized additions; found {len(p240_rows)}")
    review_notes = {
        "st-chp8-p240-patronage-beyond-collecting": "新增：补录 patronage 不限于收藏及偏好艺术家的独立断言；扫描校正 confmed→confined。",
        "st-chp8-p240-exhibition-as-art-direction": "保留：展览被用于引导佛罗伦萨绘画；扫描校正 instrumentof→instrument of。",
        "st-chp8-p240-ferdinand-regular-display-policy": "新增：将一般展示政策从Gabbiani具体作品及地点中拆开。",
        "st-chp8-p240-ferdinand-displays-gabbiani": "修订：subject改为Flight into Egypt作品、object改为Piazza del Duomo；仅记公开展示地点，日期未给。",
        "st-chp8-p240-catalogue-and-reconstruction": "修订引文跨度；保留目录用于重建活动的书内断言，关系候选撤出，书目引用单独由注5记录。",
        "st-chp8-p240-exhibition-count-and-loan-sources": "保留为展览约250幅画作的内容字段；取消虚构的独立作品组端点。",
        "st-chp8-p240-pictures-borrowed-from-florence": "保留为展览展品来源概述；未指明单一借出机构，不建边。",
        "st-chp8-p240-no-pictures-from-grand-duke": "保留否定性展览内容；不创建正向关系或未具名大公端点。",
        "st-chp8-p240-exhibition-date-and-venue": "保留：事件日期与礼拜堂端点明确；与外层回廊分列。",
        "st-chp8-p240-lunette-display": "保留：画作陈列于回廊lunettes的空间表述。",
        "st-chp8-p240-note1-fogolari-mehus-acquisition": "修订：分离脚注引文并记录Haskell book→Fogolari article的cites候选；扫描校正p. l6l→p. 161。",
        "st-chp8-p240-note2-hugford-locator": "修订：从合并的注2/3引文中仅保留注2；标为Haskell cites Hugford。",
        "st-chp8-p240-note3-fogolari-letter12": "修订：仅保留注3原文；以第12号信及日期作为书内引注对象。",
        "st-chp8-p240-note4-fogolari-letter120": "保留：注4的Letter 120沿用p.234既有身份与formal cites边。",
        "st-chp8-p240-note5-catalogue-title": "修订：脚注主客体改为Haskell book→目录的cites；扫描校正I’Anno→l’Anno，保留印刷题名Nonziata。",
        "st-chp8-p240-grand-prince-portrait-display-location": "修订：上方门楣所指端点为chapel，而非外层cloister；作品身份仍只据坐者和位置。",
        "st-chp8-p240-1706-exhibition-and-san-rocco": "保留：斐迪南与1706活动的组织参与；“可能受S. Rocco启发”不纳入同一正式边。",
        "st-chp8-p240-ferdinand-displays-sacconi-and-cassana": "保留：书内报告1707通信、赞语和拟展计划；计划不等于实际展出。",
        "st-chp8-p240-cook-intended-for-florence": "保留：Cassana作品的未来展示意图；不扩写为已经展出。",
        "st-chp8-p240-mehus-death-and-patronage": "保留Haskell反事实推断及1691年限定；不转换为正式师承或创作关系。",
        "st-chp8-p240-mehus-collection": "保留：约三十件Mehus作品属Ferdinand；数量和对象范围按Haskell限定。",
        "st-chp8-p240-ferdinand-collected-mehus-canvases": "保留：Ferdinand积极收集Mehus画布的叙述。",
        "st-chp8-p240-ferdinand-mehus-canvases-and-son": "保留：Mehus之子未具名，维持待证人物端点，不扩名。",
        "st-chp8-p240-room-and-ricci": "保留为指代未定的Ricci作品候选；“this”不强解为房间或某件已识别作品。",
        "st-chp8-p240-special-room-at-poggio-a-caiano": "保留：Poggio a Caiano的特殊房间与小幅范例收藏，空间和作品组分开。",
        "st-chp8-p240-collections-at-pratolino-and-castello": "保留：Pratolino收藏地点及原文范围。",
        "st-chp8-p240-collections-at-villa-di-castello": "保留：Villa di Castello另列；不把收藏事实改写成所有权。",
        "st-chp8-p240-corpus-domini-exhibitions": "保留：Corpus Domini节期佛罗伦萨及意大利其他城市展画的背景陈述。",
        "st-chp8-p240-venetian-pictures-ten-titian-attributions": "保留：约十幅归为Titian名下的收藏内容，不将归属限定升级为确定作者。",
        "st-chp8-p240-other-flemish-works-in-collection": "保留：Flemish作品作为收藏组成概述。",
        "st-chp8-p240-contemporary-roman-painting-scarce": "保留：当代罗马绘画在收藏中的比例极少。",
        "st-chp8-p240-florentine-school-one-artist-in-bulk": "保留：佛罗伦萨画派作品中仅Mehus以较大数量出现的范围限定。",
        "st-chp8-p240-mehus-most-venetian-in-entourage": "保留：这是Haskell的比较性判断，不另建人物间关系。",
        "st-chp8-p240-mehus-appeal": "保留：活力与略带不安的情色性使Mehus吸引Ferdinand；不升级为formal patronage edge。",
        "st-chp8-p240-lunette-display": "保留：展品以每组约八至十幅挂在回廊lunettes。",
        "st-chp8-p240-twelve-ferdinand-pictures-first-lunette": "保留：十二幅为来源定义的借展小组；作品身份及边类型待进一步处理。",
        "st-chp8-p240-grand-prince-portrait-sitter": "保留：肖像坐者为Grand Prince Ferdinand；画作本身仍未识别。",
        "st-chp8-p240-ferdinand-admired-cassana-portrait-cook": "保留：赞语来自书内报告的信件，不据此判定现存作品版本。",
        "st-chp8-p240-exhibition-as-art-direction": "保留：Ferdinand使用展览引导本地绘画的目的与方式。",
    }
    # Keep the report exhaustive even if future S2 rows are added to the same printed page.
    report_rows = []
    for row in sorted(p240_rows, key=lambda r: (r["qualifiers"].get("source_line_start", 0), r["statement_id"])):
        sid = row["statement_id"]
        detail = review_notes.get(sid, "保留：逐项核对claim、端点、引文跨度、时间／语气和关系候选状态；无新增事实。")
        report_rows.append(f"| `{sid}` | {detail} |")
    true_count = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in p240_rows)
    false_count = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in p240_rows)
    review_text = f'''# 第八章 p.240 S2 独立语义复核与跨章端点裁决

更新：2026-10-23。范围为扫描 PDF 物理页46、印刷页240：正文转录 L351–359、L452（该段在注释容器中保存）及本页注1–5（L453–456）。对照扫描图 `tmp-review-ch8-page-46.png`；只校读来源转录，未改写 S0 来源资产。现有38条 statement 加2条独立断言后，共复核40条。该复核记录不并入统一 S2 独立复核分子；统一台账仍须按当前 statement ID 和来源版本核平。

## 逐条复核

| statement_id | 语义判断与处理 |
|---|---|
{chr(10).join(report_rows)}

## 扫描校读与S2结构修订

- L355 `confmed` 校读为 `confined`；`instrumentof` 校读为 `instrument of`。修订只写入 statement 的扫描校读证据，不改S0转录。
- L453 `p. l6l` 校读为 `p. 161`；L456 `I’Anno` 校读为 `l’Anno`。L456印刷题名中的 `Nonziata` 按扫描保留，不作外部规范化。
- catalogue-and-reconstruction 只保留目录如何帮助重建展览的S2内容断言。正式引用由注5单独表达为《赞助人与画家》 `cites` 目录；不建立无受控谓词的 event↔archive 边。
- 约250幅、展品多借自佛罗伦萨大型收藏、无画作来自大公收藏，均保留为展览内容字段；`cand-8072` 的“250幅画”不是独立 work KU，S3裁为 `excluded`。未具名大公不作关系端点。
- Gabbiani 的《逃往埃及》与 Piazza del Duomo 作为有名作品及直接展示地点分别映射；不为展示补造日期或永久收藏地点。
- 肖像所在位置从 `cand-8068` 外层回廊改指 `cand-8067` 内部礼拜堂。礼拜堂与回廊分别保留为 place KU。
- 两个新 statement 拆开 Patronage 范围判断与一般展示政策，避免与特定作品、地点关系混在一行。

## 跨章S3与登记结果

- 1706年佛罗伦萨展览 `cand-7977` 复用既有跨章组 `sg3-event-florentine-art-exhibition-1706`，映射到由 `cand-11046` 建立的 event KU。第8章p.240与第20章p.404指同一1706活动；与1705年展览保持区分，Ferdinand的先驱角色沿用后记修正。
- `cand-3564`（第1、3章 St Luke）作为 source-local person 新组，`cand-8066`（第8章圣路加节及奉献语境）复用同一KU。单名是圣徒常用称谓；不补写传记。
- `cand-8065` Piazza del Duomo、`cand-8067`圣路加礼拜堂、`cand-8068` SS Annunziata回廊分别新建 place KU，不并入Florence城市或彼此合并。
- `cand-8069`目录、`cand-7871` Hugford著作、`cand-7894` Fogolari文章沿用各自既有S3 new组；`cand-7929`作为“Fogolari 1937所引第12号信（1698-06-07）”的新 archive 引注身份登记。后者不代表原件、保管地点或刊本已查。
- `cand-1095` 是 G.csv#2 的作品子项，依据p.240明确标题写为 Flight into Egypt work 候选；与已登记的加比亚尼人物KU分离。`cand-8071`肖像仍 `undecided`：来源只给坐者与门上方位置，当前不能排除与其他同坐者肖像身份重叠。

**S3范围边界与后续候选。** 本批只裁决与本批新端点及直接S6关系所需的身份，不构成p.240全页S3收口。其余29个主决定仍为 `undecided`：person `cand-8059/8073/8074`；place `cand-8062/8064`；work `cand-8060/8061/8063/8070/8071/8075/8076/8077/8082–8093`；event `cand-8079`；term `cand-8095/8102/8103`。另有 `cand-8078`（family）和 `cand-8104`（term）已有 `new` 身份决定，尚未S4登记。它们按类型及是否阻断直接关系端点进入后续批次。

## S6关系裁决

| S2候选 | 决定 | 关系与限制 |
|---|---|---|
| `st-chp8-p240-1706-exhibition-and-san-rocco`；`st-chp20-p404-1706-role-corrected-by-1705-catalogue` | formal | event `has_participant` Ferdinand，角色为参与组织；保留第20章对其先驱作用的修正。“可能受S. Rocco启发”不在该边内。 |
| `st-chp8-p240-exhibition-date-and-venue` | formal | event `occurred_at` 圣路加礼拜堂；日期限定1706圣路加节（10月18日），范围限于Haskell报告。 |
| `st-chp8-p240-lunette-display` | formal | event `occurred_at` Annunziata回廊；范围仅记录lunette陈列空间，不将回廊与礼拜堂合并。 |
| `st-chp8-p240-ferdinand-displays-gabbiani` | formal | Flight into Egypt `located_at` Piazza del Duomo；角色为书内报告的公开展示地，未给日期，不表示永久安置。 |
| `st-chp8-p240-note1-fogolari-mehus-acquisition` | formal | Haskell archive `cites` Fogolari 1937文章；未读文章或p.161。 |
| `st-chp8-p240-note2-hugford-locator` | formal | Haskell archive `cites` Hugford 1762著作；未读p.10。 |
| `st-chp8-p240-note3-fogolari-letter12` | formal | Haskell archive `cites` Fogolari所定位第12号信；原件及刊本未查。 |
| `st-chp8-p240-note5-catalogue-title` | formal | Haskell archive `cites` 1706佛罗伦萨目录；目录原件未查。 |

注4的Letter 120引用复用既有 `rel-1525 cites` 记录，不新增重复边。chapter20角色修正与chapter8事件候选绑定同一活动。地点奉献事实写入place内容；当前域值域矩阵的 `dedicated_to` 只允许 work→person，因此不创建 chapel→Saint Luke 关系。扫描校读、书目身份确认不等于引用内容已独立查阅。

本批40条statement中 `relation_candidate=true` {true_count} 条、`false` {false_count} 条。未处理的S6候选及肖像待决继续保留在各自阶段记录，不因本批收口而宣称p.240全页关系阶段完成。

本页27条relation candidates中，`relations.csv`现有formal行覆盖12条（本批新增8条、沿用既有4条）；另15条目前没有formal/pending表行，后续需先核对既有过程裁决，再逐项补足去向。
'''
    if REVIEW_PATH.exists():
        raise FileExistsError(f"review report already exists: {REVIEW_PATH}")
    plans[REVIEW_PATH] = review_text.encode("utf-8")

    # Cross-chapter S3 outcomes and S4 registrations.
    group_event = "sg3-event-florentine-art-exhibition-1706"
    group_saint = "sg3-person-saint-luke"
    new_group = {
        "cand-3564": ("new", "person-group-saint-luke", KU["saint"], "source_ref=chp-1:L688;chp-3:L141-150; S2 mentions=m-chp1-secii-0596,m-chp3-seciv-l141-150-0050; same one-name saint in feast-day and Gospel-source contexts; source-local identity only; no external biography asserted."),
        "cand-7871": ("new", "archive-group-a11c8f674d46", KU["hugford"], "S3 new bibliographic identity from Hugford, Vita di Anton Domenico Gabbiani pittor fiorentino, Firenze 1762; ch.8 p.240 n.2 and ch.21 bibliography L626; source-local citation only; book and cited p.10 not independently consulted."),
        "cand-7894": ("new", "archive-group-d7f94f641843", KU["fogolari"], "S3 new bibliographic identity from ch.21 bibliography L485 and p.240 n.1; preserves the 1937 article separately from its cited letter locators; article not independently consulted."),
        "cand-7929": ("new", "archive-group-fogolari-letter-12-1698-06-07", KU["letter12"], "source_ref=chp-8 p.240 n.3 L454; Haskell identifies Fogolari (1937), Letter 12, dated 7 June 1698. New archive identity is limited to this cited letter locator; no witness or repository is asserted."),
        "cand-8065": ("new", "place-group-piazza-del-duomo-florence", KU["piazza"], "source_ref=chp-8 p.240 L356; exact public-display place name; no further modern site identification or architectural boundary asserted."),
        "cand-8067": ("new", "place-group-annunziata-chapel-of-saint-luke", KU["chapel"], "source_ref=chp-8 p.240 L358-359; explicit internal chapel dedicated to St Luke; kept distinct from outer cloister and Florence city."),
        "cand-8068": ("new", "place-group-ss-annunziata-cloister-florence", KU["cloister"], "source_ref=chp-8 p.240 L359,L452,n.5; Haskell's Annunziata cloisters and the catalogue's Chiostro wording identify one source-local cloister; printed spelling Nonziata retained."),
        "cand-8069": ("new", "archive-group-8b0253784943", KU["catalogue"], "source_ref=chp-8 p.240 n.5 L456; specific printed catalogue title and Firenze 1706 imprint; catalogue itself not consulted."),
        "cand-1095": ("new", "work-group-a-d-gabbiani-flight-into-egypt", KU["flight"], "source_ref=G.csv#2 sub-entry Flight into Egypt and chp-8 p.240 L356; no same Gabbiani Flight into Egypt KU exists in the manifest; source-local work identity, not external object verification."),
    }
    same_group = {
        "cand-7977": (KU["event"], group_event, "same as registered cand-11046 event group: ch.8 p.240 L357-359 and ch.20 p.404 L131 describe the same Florentine 1706 exhibition; keep distinct from 1705 and later exhibitions."),
        "cand-8066": (KU["saint"], group_saint, "same as cand-3564: ch.1 L688, ch.3 L141-150, and ch.8 p.240 L358-359/n.5 use St Luke in compatible saint, feast-day, and Gospel-source contexts; no biography or external identity asserted."),
    }
    align_by_candidate["cand-3564"].update({"decision": "new", "ku_id": KU["saint"], "process_ref": PROCESS_REF, "resolution_note": f"group={group_saint}; {new_group['cand-3564'][3]}"})
    align_by_candidate["cand-8066"].update({"decision": "same", "ku_id": KU["saint"], "process_ref": PROCESS_REF, "resolution_note": f"group={group_saint}; {same_group['cand-8066'][2]}"})
    align_by_candidate["cand-7977"].update({"decision": "same", "ku_id": KU["event"], "process_ref": PROCESS_REF, "resolution_note": f"group={group_event}; {same_group['cand-7977'][2]}"})
    align_by_candidate["cand-8072"].update({
        "decision": "excluded", "ku_id": "", "process_ref": PROCESS_REF,
        "resolution_note": "S3 excluded: the approximately 250 pictures are an aggregate count and event-level content, not an independently identifiable work or work group; retain the source claim on the exhibition statement and event card.",
    })
    align_by_candidate["cand-8071"].update({
        "process_ref": PROCESS_REF,
        "resolution_note": "source_ref=chp-8 p.240 L452; S2 mention=m-chp8-p240-portrait. The source identifies this portrait by sitter and position above the chapel door only; without title, maker, or another distinguishing object feature, it cannot yet be safely separated from other portraits of Ferdinand. Retain undecided pending additional identity evidence.",
    })
    for candidate_id, (decision, group, ku, rationale) in new_group.items():
        row = align_by_candidate[candidate_id]
        row.update({"decision": decision, "ku_id": ku, "process_ref": PROCESS_REF, "resolution_note": f"group={group}; {rationale}"})
    # The existing event group is registered through its primary candidate from chapter 20.
    align_by_candidate["cand-11046"]["ku_id"] = KU["event"]
    align_by_candidate["cand-11046"]["process_ref"] = PROCESS_REF
    align_by_candidate["cand-11046"]["resolution_note"] += " S4 registered in p.240 cross-chapter endpoint batch; chapter 8 p.240 is explicitly mapped to this event."
    plans[alignment_path] = render_csv(alignment_fields, alignments, alignment_bom, alignment_nl)

    # S4 manifest and accepted paths.
    card_paths = {key: f"04-knowledge/{ku}.md" for key, ku in KU.items()}
    add_to_manifest = []
    for key, ku in KU.items():
        canonical, english = DISPLAY_NAME[key]
        add_to_manifest.append({"ku_id": ku, "type": ku.split("/")[1][:-1] if ku.split("/")[1].endswith("s") else ku.split("/")[1], "canonical_name": canonical, "name_en": english, "source_task": "patrons-and-painters-full-book-s2", "card_path": card_paths[key]})
    manifest.extend(add_to_manifest)
    plans[manifest_path] = render_csv(manifest_fields, manifest, manifest_bom, manifest_nl)
    plans[ROOT / "04-knowledge" / "accepted.yml"] = accepted_with(list(card_paths.values()))

    specs = card_specs()
    for key, spec in specs.items():
        text = card_text(key, spec["description_zh"], spec["description_en"], spec["fields"], spec["sources"], spec["relation_note"])
        card_path = ROOT / card_paths[key]
        temp_path = card_path.with_name(card_path.name + ".codex-preview")
        if temp_path.exists():
            raise FileExistsError(f"refusing to overwrite preview {temp_path}")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            temp_path.write_text(text, encoding="utf-8", newline="\n")
            rows, source_ids, warnings, table_count = extract_records([{"ku_id": KU[key], "card_path": temp_path.relative_to(ROOT).as_posix()}])
        finally:
            temp_path.unlink(missing_ok=True)
        if warnings or table_count != (1 if spec["fields"] else 0) or set(source_ids) != {SOURCE_ID}:
            raise ValueError(f"S5 extraction failed for {key}: tables={table_count}; warnings={warnings}; sources={source_ids}")
        if any(row["evidence_status"] != "source_backed" for row in rows):
            raise ValueError(f"S5 rows for {key} are not all source_backed")
        spec["card_text"] = text
        spec["field_rows"] = rows
        plans[card_path] = text.encode("utf-8")

    enrichment_path = TABLES / "enrichment.jsonl"
    existing_enrichments = read_jsonl(enrichment_path)
    field_rows = [row for spec in specs.values() for row in spec["field_rows"]]
    assign_ids(field_rows, enrichment_path)
    old_ids = {row.get("enrichment_id") for row in existing_enrichments}
    old_occurrences = {row.get("occurrence_id") for row in existing_enrichments}
    if any(row.get("enrichment_id") in old_ids or row.get("occurrence_id") in old_occurrences for row in field_rows):
        raise ValueError("S5 identifier or occurrence collision")
    raw_enrichment = enrichment_path.read_bytes()
    newline = b"\r\n" if b"\r\n" in raw_enrichment else b"\n"
    if raw_enrichment and not raw_enrichment.endswith((b"\n", b"\r")):
        raw_enrichment += newline
    plans[enrichment_path] = raw_enrichment + newline.join(json.dumps(row, ensure_ascii=False).encode("utf-8") for row in field_rows) + newline

    # Formal S6 edges use the controlled vocabulary and domain/range matrix.
    relations_path = TABLES / "relations.csv"
    relation_fields, relations, relation_bom, relation_nl = read_csv(relations_path)
    max_relation_id = max((int(match.group(1)) for row in relations if (match := re.fullmatch(r"rel-(\d+)", row["relation_id"]))), default=0)
    if max_relation_id != 1618:
        raise ValueError(f"relation ID baseline changed ({max_relation_id}); re-evaluate before applying")
    source_spans = "\n".join(row.get("source_span", "") for row in relations)
    if any(sid in source_spans for sid in [
        "st-chp8-p240-1706-exhibition-and-san-rocco", "st-chp8-p240-exhibition-date-and-venue",
        "st-chp8-p240-lunette-display", "st-chp8-p240-ferdinand-displays-gabbiani",
        "st-chp8-p240-note1-fogolari-mehus-acquisition", "st-chp8-p240-note2-hugford-locator",
        "st-chp8-p240-note3-fogolari-letter12", "st-chp8-p240-note5-catalogue-title",
    ]):
        raise ValueError("one or more planned p.240 S6 candidates already have relation rows")
    domain_range = yaml.safe_load((ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8"))["domain_range"]
    type_by_ku = {row["ku_id"]: row["type"] for row in manifest}
    formal_specs = [
        (KU["event"], "has_participant", "units/persons/ferdinand-grand-prince-tuscany", "1706", "参与组织者（范围按第20章后记限定）", "第8章称其组织较大展览；第20章称其参与组织并修正其先驱作用，不推定唯一组织者。", "st-chp8-p240-1706-exhibition-and-san-rocco; st-chp20-p404-1706-role-corrected-by-1705-catalogue"),
        (KU["event"], "occurred_at", KU["chapel"], "1706-10-18", "书内报告的活动场所", "第8章称展览于1706年圣路加节（10月18日）在Annunziata回廊内的圣路加礼拜堂举行；仅记录书内报告。", "st-chp8-p240-exhibition-date-and-venue"),
        (KU["event"], "occurred_at", KU["cloister"], "1706", "展品陈列所在的回廊空间", "第8章称画作悬挂于回廊lunettes；与内部礼拜堂分列，不表示回廊和礼拜堂为同一空间。", "st-chp8-p240-lunette-display"),
        (KU["flight"], "located_at", KU["piazza"], "", "哈斯克尔所报告的公开展示地点", "第8章称Ferdinand将该画向公众展示于Piazza del Duomo；未给日期，不表示永久安置。", "st-chp8-p240-ferdinand-displays-gabbiani"),
        ("units/archives/patrons-and-painters", "cites", KU["fogolari"], "", "书内脚注引注", "Haskell第8章注1引Fogolari 1937文章p.161注43；文章与所引页未独立查阅。", "st-chp8-p240-note1-fogolari-mehus-acquisition"),
        ("units/archives/patrons-and-painters", "cites", KU["hugford"], "", "书内脚注引注", "Haskell第8章注2引Hugford第10页；原书及该页未独立查阅。", "st-chp8-p240-note2-hugford-locator"),
        ("units/archives/patrons-and-painters", "cites", KU["letter12"], "1698-06-07", "通过Fogolari 1937所列的书信定位", "记录Haskell脚注所引Letter 12及日期；不推定原件、馆藏地点或已读刊本。", "st-chp8-p240-note3-fogolari-letter12"),
        ("units/archives/patrons-and-painters", "cites", KU["catalogue"], "1706", "书内脚注引注", "Haskell第8章注5给出目录题名及Firenze 1706出版项；目录原件未查。", "st-chp8-p240-note5-catalogue-title"),
    ]
    for i, (subject, predicate, obj, time, role, scope, statement_ids) in enumerate(formal_specs, start=1619):
        if predicate not in domain_range:
            raise ValueError(f"controlled relation {predicate} missing from matrix")
        pair = domain_range[predicate]
        if type_by_ku.get(subject) not in pair["domain"] or type_by_ku.get(obj) not in pair["range"]:
            raise ValueError(f"illegal {predicate} endpoints: {subject} ({type_by_ku.get(subject)}) -> {obj} ({type_by_ku.get(obj)})")
        relations.append({
            "relation_id": f"rel-{i}", "subject_ku_id": subject, "object_ku_id": obj,
            "predicate": predicate, "time": time, "role": role, "scope": scope,
            "origin": "book", "status": "formal", "source_id": SOURCE_ID,
            "source_span": f"Chapter 8, printed p.240; statements: {statement_ids}",
            "source_file": SOURCE_REL, "note": "Source-local relation; exact evidence and limits are recorded in the p.240 S2 review and process record.",
        })
    plans[relations_path] = render_csv(relation_fields, relations, relation_bom, relation_nl)

    # Append the process decision once, retaining prior decision records.
    process_raw = PROCESS_PATH.read_bytes()
    process_text = process_raw.decode("utf-8-sig")
    if ANCHOR in process_text:
        raise ValueError(f"process anchor already exists: {ANCHOR}")
    process_newline = "\r\n" if b"\r\n" in process_raw else "\n"
    process_addition = f'''

<a id="{ANCHOR}"></a>

### 第八章 p.240 跨章身份、S4端点与S6引用（{TODAY}）

**S2复核。** 对照扫描页46复核印刷页240正文L351–359、L452及注1–5（L453–456）。新增两条独立断言，修订Gabbiani作品端点、肖像空间端点和展览级统计字段；扫描校读为L355 `confmed`→`confined`、`instrumentof`→`instrument of`，L453 `p. l6l`→`p. 161`，L456 `I’Anno`→`l’Anno`。S0来源未改写。完整40条逐条复核见[s2-independent-review-chp8-p240-20261023.md](s2-independent-review-chp8-p240-20261023.md)。

**S3跨章裁决。** `cand-11046`沿用`sg3-event-florentine-art-exhibition-1706`登记为单一1706年佛罗伦萨展览；`cand-7977`由p240正文锚点复用该KU。事件与1705年活动及后续展览保持区分。`cand-3564`和`cand-8066`统一为source-local St Luke人物组，依据第1章节日、第3章福音书及第8章节日／奉献语境；不补写传记。`cand-8065`广场、`cand-8067`礼拜堂、`cand-8068`回廊是不同地点；`cand-8069`展览目录、`cand-7871`Hugford著作、`cand-7894`Fogolari文章、`cand-7929`第12号信定位分别建组。`cand-1095`明确为Gabbiani名下Flight into Egypt作品候选。`cand-8072`的约250幅仅为事件计数，不构成独立work KU，S3裁为`excluded`并保留事件字段。`cand-8071`肖像仍`undecided`：仅知坐者与陈列位置，尚不能排除与其他同坐者肖像为同一对象。

本批未覆盖p.240全页S3。仍为`undecided`的候选按类型为：person `cand-8059/8073/8074`；place `cand-8062/8064`；work `cand-8060/8061/8063/8070/8071/8075/8076/8077/8082–8093`；event `cand-8079`；term `cand-8095/8102/8103`。`cand-8078`（family）和`cand-8104`（term）已有`new`决定，仍待S4。p.240的S2提及和身份边界需在后续按候选类型及直接关系端点逐批收口。

**S4登记。** 本批新增10个KU组：事件、人物St Luke、Piazza del Duomo、圣路加礼拜堂、SS Annunziata回廊、1706印刷目录、Hugford 1762著作、Fogolari 1937文章、Fogolari Letter 12 locator、Gabbiani《逃往埃及》。event/place/archive/work等类型分别登记，均限于书内身份；未声称外部核验或阅读被引文献。候选到KU映射见`alignment.csv`，有效卡片见`ku-manifest.csv`与`accepted.yml`。

**S5字段。** 新卡字段均为`source_backed`，分别记录展览日期和约250幅规模、礼拜堂／回廊空间称谓、目录题名与出版项、书目信息及信件编号日期、作品称谓与书内展示地点。负面展品来源、日期缺项、目录拼写和未展开身份均保留原有限定。

**S6裁决。** 新增8条formal关系：event `has_participant` Ferdinand；event `occurred_at` 礼拜堂与回廊；Flight into Egypt `located_at` Piazza del Duomo；Haskell书籍分别`cites` Fogolari文章、Hugford著作、Letter 12与展览目录。Letter 120沿用既有`rel-1525`，未重复建边。目录“用于重建活动”的陈述不另建无受控类型边；chapel→St Luke因`dedicated_to`域值域不允许place→person，不创建正式边。全页27条`relation_candidate=true`中，`relations.csv`现有formal行覆盖12条（本批新增8条，既有4条沿用）；另15条目前没有formal/pending表行，需先核对已有过程裁决，再逐项补齐S6去向。
'''
    process_payload = process_raw
    if not process_payload.endswith((b"\n", b"\r")):
        process_payload += process_newline.encode("ascii")
    process_payload += process_addition.replace("\n", process_newline).encode("utf-8")
    plans[PROCESS_PATH] = process_payload

    # Build a review table for per-row traceability; caller will update summary snapshots after applying.
    if any(path.exists() and path.suffix == ".codex-preview" for path in plans):
        raise ValueError("preview file unexpectedly included in plan")
    return plans, field_rows, formal_specs, p240_rows


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Review and register p.240 exhibition endpoints.")
    parser.add_argument("--apply", action="store_true", help="apply the reviewed batch; default previews planned diffs")
    parser.add_argument("--quiet", action="store_true", help="print only the plan summary")
    args = parser.parse_args()
    plans, field_rows, relations, reviewed = build_plan()
    print(f"mode={'apply' if args.apply else 'preview'} files={len(plans)} s2_reviewed={len(reviewed)} s5_fields={len(field_rows)} s6_formal={len(relations)} s4_groups={len(KU)}")
    if not args.quiet:
        for path, payload in plans.items():
            old = path.read_bytes() if path.exists() else b""
            before = old.decode("utf-8-sig", errors="replace").splitlines(keepends=True)
            after = payload.decode("utf-8-sig", errors="replace").splitlines(keepends=True)
            diff = difflib.unified_diff(before, after, fromfile=str(path.relative_to(ROOT)), tofile=str(path.relative_to(ROOT)))
            print("".join(diff), end="")
    if args.apply:
        for path, payload in plans.items():
            atomic_write(path, payload)
        print("apply_complete=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
