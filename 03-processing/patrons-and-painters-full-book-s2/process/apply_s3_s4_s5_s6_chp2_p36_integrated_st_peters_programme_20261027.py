from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
TODAY = "2026-10-27"
ANCHOR = "s3-s4-s5-s6-chp2-p36-integrated-st-peters-programme-20261027"
PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    + ANCHOR
)

KU_ID = "units/terms/st-peters-integrated-decorative-programme-haskell-account"
CARD_PATH = "04-knowledge/units/terms/st-peters-integrated-decorative-programme-haskell-account.md"
NAME_EN = "Haskell’s Account of the Integrated Decorative Programme at St Peter’s Basilica"
TITLE = "哈斯克尔所述圣彼得大殿整体装饰方案（" + NAME_EN + "）"
DESCRIPTION_ZH = (
    "本卡记录哈斯克尔对圣彼得大殿整体装饰方案的解释：他认为完成后的方案使整座教堂获得新意义，"
    "各要素在风格与主题上相互呼应，并联结宗教意象、教宗权势与巴贝里尼家族。此为来源限定的"
    "解释性概念，不等同于巴尔达基诺等单件作品，也不将作者阐释提升为独立核实事实。"
)
DESCRIPTION_EN = (
    "This unit records Haskell’s interpretation of the integrated decorative programme at St Peter’s Basilica: "
    "he says the completed scheme gave the whole church new meaning, its elements echoed one another in style "
    "and theme, and the ensemble joined religious imagery with papal and Barberini themes. This is a source-local "
    "interpretive concept, distinct from individual works such as the baldacchino; it does not present Haskell’s "
    "interpretation as independently verified fact."
)
DEFINITION = (
    "哈斯克尔对圣彼得大殿整体装饰方案的解释：完成后的方案使整座教堂获得新意义，各要素在风格与主题上相互呼应，"
    "并成为宗教意象与教宗及巴贝里尼家族主题的整体表达。"
)


def csv_bytes(
    path: Path,
    updates: dict[str, dict],
    additions: list[dict],
    key: str,
) -> bytes:
    original = path.read_bytes()
    bom = original.startswith(b"\xef\xbb\xbf")
    text = original.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    physical = text.splitlines(keepends=True)
    reader = csv.DictReader(io.StringIO(text, newline=""))
    fields = reader.fieldnames
    if not fields:
        raise ValueError(f"Missing CSV header: {path}")
    previous_line = reader.line_num
    entries: list[tuple[dict, str | None]] = []
    found: set[str] = set()
    for row in reader:
        row_id = row.get(key, "")
        if row_id in updates:
            row.update(updates[row_id])
            found.add(row_id)
        end_line = reader.line_num
        raw = "".join(physical[previous_line:end_line])
        entries.append((row, raw if row_id not in updates else None))
        previous_line = end_line
    missing = set(updates) - found
    if missing:
        raise ValueError(f"CSV update target not found: {path}: {sorted(missing)}")
    existing_ids = {row.get(key, "") for row, _ in entries}
    for row in additions:
        row_id = row.get(key, "")
        if row_id in existing_ids:
            raise ValueError(f"Duplicate {key} in {path}: {row_id}")
        existing_ids.add(row_id)

    def serialize(row: dict) -> str:
        out = io.StringIO(newline="")
        csv.writer(out, lineterminator=newline).writerow(
            [row.get(field, "") for field in fields]
        )
        return out.getvalue()

    body = "".join(raw if raw is not None else serialize(row) for row, raw in entries)
    body += "".join(serialize(row) for row in additions)
    result = (physical[0] + body).encode("utf-8")
    return (b"\xef\xbb\xbf" + result) if bom else result


def accepted_bytes(add_paths: list[str]) -> bytes:
    path = ROOT / "04-knowledge" / "accepted.yml"
    original = path.read_bytes()
    bom = original.startswith(b"\xef\xbb\xbf")
    text = original.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    newline = "\r\n" if "\r\n" in text else "\n"
    unit_start = next(i for i, line in enumerate(lines) if line.strip() == "units:")
    unit_end = next(
        (
            i
            for i in range(unit_start + 1, len(lines))
            if lines[i] and not lines[i][0].isspace() and not lines[i].startswith("-")
        ),
        len(lines),
    )
    present = {
        line.strip()[2:].strip()
        for line in lines[unit_start + 1 : unit_end]
        if line.lstrip().startswith("- ")
    }
    for path_value in sorted(add_paths):
        if path_value in present:
            raise ValueError(f"Accepted card path already present: {path_value}")
        insert_at = unit_end
        for i in range(unit_start + 1, unit_end):
            existing = lines[i].lstrip()[2:].strip() if lines[i].lstrip().startswith("- ") else ""
            if existing and existing > path_value:
                insert_at = i
                break
        lines.insert(insert_at, f"- {path_value}{newline}")
        unit_end += 1
        present.add(path_value)
    result = "".join(lines).encode("utf-8")
    return b"\xef\xbb\xbf" + result if bom else result


def card_bytes() -> bytes:
    quote = lambda value: json.dumps(value, ensure_ascii=False)
    lines = [
        "---",
        f"title: {quote(TITLE)}",
        f"name_en: {quote(NAME_EN)}",
        "type: term",
        "evidence_status: source_backed",
        "sources:",
        f"  - citation: {quote(SOURCE_CITATION)}",
        f"    location: {quote('第2章，印刷页36，L57–58；PDF物理页17。')}",
        f"    sentence_summary: {quote(DESCRIPTION_ZH)}",
        "    original_quotes:",
        f"      - source_span: {quote('lines 57–58; printed p. 36; PDF physical p. 17')}",
        f"        text: {quote('When the scheme was eventually complete it was apparent that the Pope and Bernini had given new meaning to the whole church.')}",
        f"      - source_span: {quote('line 58; printed p. 36; PDF physical p. 17')}",
        f"        text: {quote('All the elements echoed each other in style and theme')}",
        f"      - source_span: {quote('line 58; printed p. 36; PDF physical p. 17')}",
        f"        text: {quote('a passionate reminder of the overwhelming glories of the papacy and of his own house')}",
        "    evidence_ref:",
        "      doc_id: patrons-and-painters",
        f"      source_file: {SOURCE_FILE}",
        f"      source_span: {quote('lines 57–58; printed p. 36; PDF physical p. 17')}",
        f"created: '{TODAY}'",
        f"updated: '{TODAY}'",
        f"process_ref: {PROCESS_REF}",
        "---",
        "",
        "## 内容",
        "",
        "### 描述",
        f"**中文：** {DESCRIPTION_ZH}",
        "",
        f"**English:** {DESCRIPTION_EN}",
        "",
        "### 名称",
        "",
        "| 字段 | 值 | 证据 |",
        "|---|---|---|",
        f"| 描述性名称 | {TITLE} | 原书未给正式名称；本卡按第2章印刷页36 L57–58的来源限定对象拟名 |",
        "",
        "### 基本信息",
        "",
        "| 字段 | 值 | 证据 |",
        "|---|---|---|",
        f"| 定义 | {DEFINITION} | S1；第2章印刷页36 L57–58；statement=st-chp2-secii-l52-60-completed-scheme-new-meaning, st-chp2-secii-l52-60-papacy-and-house-reminder |",
        "",
        "### 本章相关内容",
        "",
        "本术语表示哈斯克尔对圣彼得大殿跨作品整体装饰的解释。巴尔达基诺作品本体及其图像方案分别保留为独立知识元；本卡不将整体方案等同于任何一件作品。有关方案时长的表述保留在 S2 时间限定中，不作为人物关系边。",
        "",
        "## 关系与证据",
        "",
        "### 身份与外部链接",
        "",
        "本卡记录 Haskell 书内的来源限定概念；未查找或声称存在一个外部统一命名的实体。",
        "",
        "### 关系记录",
        "",
        "| 方向与关系 | 关联知识元 | 语境与证据 |",
        "|---|---|---|",
        "| → 呈现于（`manifested_at`） | [圣彼得大殿](../places/st-peters-basilica.md) | Haskell 将完成后的整体方案与整座教堂相联系；本边记录其来源所述呈现地点，不表示每件组成作品的物理位置。S2 statement: st-chp2-secii-l52-60-completed-scheme-new-meaning。 |",
        "",
        "两项关于巴贝里尼家族／教宗意涵及宗教赞颂的候选暂不写成正式边；逐项裁决与受控关系类型限制见[本批过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#" + ANCHOR + ").",
        "",
    ]
    return ("\n".join(lines)).encode("utf-8")


def statement_bytes(path: Path, statement_id: str) -> bytes:
    original = path.read_bytes()
    bom = original.startswith(b"\xef\xbb\xbf")
    text = original.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    found = 0
    rendered = []
    for line in lines:
        raw = line.rstrip("\r\n")
        if not raw.strip():
            rendered.append(line)
            continue
        item = json.loads(raw)
        if item.get("statement_id") == statement_id:
            found += 1
            if item.get("subject_candidate_id") != "cand-4433" or item.get("object_candidate_id") != "cand-0209":
                raise ValueError("The programme-duration statement has changed unexpectedly")
            qualifiers = item.setdefault("qualifiers", {})
            if qualifiers.get("relation_candidate") is not True:
                raise ValueError("The programme-duration statement is no longer an S6 candidate")
            item["object_candidate_id"] = None
            qualifiers["duration"] = "A large number of years; no exact duration is stated."
            qualifiers["relation_candidate"] = False
            qualifiers["relation_candidate_note"] = (
                "This is a claim about the programme’s duration, not an inter-entity relation. "
                "Keep ‘a large number of years’ and ‘almost until the end of Urban VIII’s pontificate’ "
                "as temporal qualifiers; cand-0209 remains a contextual person mention, not the duration endpoint."
            )
            newline = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
            rendered.append(
                json.dumps(item, ensure_ascii=False, separators=(",", ":")) + newline
            )
        else:
            rendered.append(line)
    if found != 1:
        raise ValueError(f"Expected one programme-duration statement, found {found}")
    result = "".join(rendered).encode("utf-8")
    return b"\xef\xbb\xbf" + result if bom else result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply the bounded change set.")
    args = parser.parse_args()

    alignment_path = TABLES / "alignment.csv"
    candidate_path = TABLES / "entity-candidates.csv"
    manifest_path = TABLES / "ku-manifest.csv"
    relation_path = TABLES / "relations.csv"
    statement_path = TABLES / "book-statements.jsonl"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    card_path = ROOT / CARD_PATH

    alignments = list(csv.DictReader(alignment_path.open(encoding="utf-8-sig", newline="")))
    candidates = list(csv.DictReader(candidate_path.open(encoding="utf-8-sig", newline="")))
    manifest = list(csv.DictReader(manifest_path.open(encoding="utf-8-sig", newline="")))
    relations = list(csv.DictReader(relation_path.open(encoding="utf-8-sig", newline="")))
    alignment = next((r for r in alignments if r["alignment_id"] == "aln-4616"), None)
    candidate = next((r for r in candidates if r["candidate_id"] == "cand-4433"), None)
    if not alignment or alignment["decision"] != "new" or alignment["ku_id"]:
        raise ValueError("aln-4616 is no longer the expected unmapped new decision")
    if not candidate or candidate["suggested_type"] != "term":
        raise ValueError("cand-4433 is no longer the expected term candidate")
    if "group=sg3-term-cand-4433" not in alignment["resolution_note"]:
        raise ValueError("The expected S3 identity group is absent")
    if any(r["ku_id"] == KU_ID for r in manifest) or card_path.exists():
        raise ValueError("The planned term KU is already registered")
    next_relation = max(int(r["relation_id"].split("-")[1]) for r in relations) + 1
    if next_relation != 2431:
        raise ValueError(f"Unexpected next relation id: rel-{next_relation:04d}")

    alignment_update = {
        "aln-4616": {
            "ku_id": KU_ID,
            "process_ref": PROCESS_REF,
            "resolution_note": alignment["resolution_note"]
            + " | S3 type/identity recheck triggered by direct-endpoint registration (2026-10-27): "
            "read Haskell print p.36/PDF physical p.17; the source-defined overall scheme is an "
            "interpretive term, distinct from the baldacchino work and its iconographic-scheme term. "
            "Retain new identity group=sg3-term-cand-4433 and map it to "
            + KU_ID
            + "; no external identity or independent iconographic fact is asserted.",
        }
    }
    relation_addition = {
        "relation_id": f"rel-{next_relation:04d}",
        "subject_ku_id": KU_ID,
        "object_ku_id": "units/places/st-peters-basilica",
        "predicate": "manifested_at",
        "time": "",
        "role": "",
        "scope": (
            "Haskell’s account of the integrated programme as manifested across St Peter’s Basilica; "
            "this records the source-reported site, not the physical location of every component or "
            "an independently measured change in the church’s meaning."
        ),
        "origin": "book",
        "status": "formal",
        "source_id": SOURCE_ID,
        "source_span": (
            "Chapter 2, printed p.36 L57–58; PDF physical p.17; "
            "statement=st-chp2-secii-l52-60-completed-scheme-new-meaning"
        ),
        "source_file": SOURCE_FILE,
        "note": "S6 formal; exact source interpretation and site scope are retained.",
    }
    manifest_addition = {
        "ku_id": KU_ID,
        "type": "term",
        "canonical_name": TITLE,
        "name_en": NAME_EN,
        "source_task": "patrons-and-painters-full-book-s2",
        "card_path": CARD_PATH,
    }

    writes = {
        alignment_path: csv_bytes(alignment_path, alignment_update, [], "alignment_id"),
        manifest_path: csv_bytes(manifest_path, {}, [manifest_addition], "ku_id"),
        relation_path: csv_bytes(relation_path, {}, [relation_addition], "relation_id"),
        statement_path: statement_bytes(
            statement_path, "st-chp2-secii-l52-60-programme-duration"
        ),
        accepted_path: accepted_bytes([CARD_PATH]),
        card_path: card_bytes(),
    }

    print("Preflight: retain cand-4433 as source-local S3 new term; register its direct S4 endpoint.")
    print("S2: detach cand-0209 from the duration statement; preserve duration and pontificate as qualifiers; set relation_candidate=false.")
    print("S6: rel-2431 manifested_at formal; papacy/house and hymn interpretations pending in process record.")
    print(f"Prepared {len(writes)} bounded writes; no file has been changed.")
    for path, content in writes.items():
        current_size = path.stat().st_size if path.exists() else 0
        print(f"  {path.relative_to(ROOT)}: {current_size} -> {len(content)} bytes")
    if not args.apply:
        print("Dry run only. Review the bounded change set, then pass --apply to write.")
        return 0

    before = {path: path.read_bytes() if path.exists() else None for path in writes}
    try:
        for path, content in writes.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            temp = path.with_name(path.name + ".codex-tmp")
            temp.write_bytes(content)
            temp.replace(path)
    except Exception:
        for path, content in before.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)
        raise
    print(f"Applied {len(writes)} bounded writes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
