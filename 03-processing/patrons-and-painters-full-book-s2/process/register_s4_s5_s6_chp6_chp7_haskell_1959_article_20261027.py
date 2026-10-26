from __future__ import annotations

import argparse
import csv
import difflib
import io
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
CARD_REL = Path("04-knowledge/units/archives/haskell-market-for-italian-art-1959.md")
CARD = ROOT / CARD_REL
KU_ID = "units/archives/haskell-market-for-italian-art-1959"
PARENT_KU = "units/archives/patrons-and-painters"
PROCESS_REF = "S3-S4-S5-S6-full-book-2026-10-27"
SOURCE_ID = "haskell-1980-rev-ed"
AUTHOR_PERSON_KU = "units/persons/francis-haskell"
AUTHOR_CANDIDATE = "cand-9423"
PRIMARY_CANDIDATE = "cand-6240"
SHORT_CITATION_CANDIDATE = "cand-6606"
PRIMARY_STATEMENT = "st-chp6-p146-note2-haskell-1959-citation"
SHORT_STATEMENT = "st-chp7-p169-n2-cite"
BIB_STATEMENT = "st-chp21-bib-l577-614-entry-06"
AUTHOR_STATEMENT = "st-chp21-bib-l577-614-haskell-1959-authored-by"
AUTHOR_MENTION = "m-chp21-bib-haskell-1959-article-author"


def read_csv(name: str) -> tuple[list[str], list[dict[str, str]], bytes]:
    path = TABLES / name
    raw = path.read_bytes()
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    text = raw.decode("utf-8-sig")
    with io.StringIO(text, newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), bom


def render_csv(columns: list[str], rows: list[dict[str, str]], bom: bytes = b"") -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return bom + stream.getvalue().encode("utf-8")


def csv_row(columns: list[str], values: dict[str, str]) -> bytes:
    stream = io.StringIO(newline="")
    csv.DictWriter(stream, fieldnames=columns, lineterminator="\n", extrasaction="ignore").writerow(values)
    return stream.getvalue().encode("utf-8")


def unified(path: Path, before: bytes, after: bytes) -> str:
    old = before.decode("utf-8-sig").splitlines(keepends=True)
    new = after.decode("utf-8-sig").splitlines(keepends=True)
    relative = str(path.relative_to(ROOT))
    return "".join(difflib.unified_diff(old, new, fromfile=relative, tofile=relative + ".proposed"))


def prepare() -> tuple[dict[Path, bytes], bytes | None]:
    files: dict[Path, bytes] = {}

    a_cols, alignments, a_bom = read_csv("alignment.csv")
    a_by_candidate = {row["candidate_id"]: row for row in alignments}
    assert a_by_candidate[PRIMARY_CANDIDATE]["decision"] == "new"
    assert a_by_candidate[PRIMARY_CANDIDATE]["ku_id"] == ""
    assert a_by_candidate[SHORT_CITATION_CANDIDATE]["decision"] == "undecided"
    assert a_by_candidate[AUTHOR_CANDIDATE]["decision"] == "same"
    assert a_by_candidate[AUTHOR_CANDIDATE]["ku_id"] == AUTHOR_PERSON_KU
    a_by_candidate[PRIMARY_CANDIDATE]["ku_id"] = KU_ID
    a_by_candidate[PRIMARY_CANDIDATE]["process_ref"] = PROCESS_REF
    a_by_candidate[PRIMARY_CANDIDATE]["resolution_note"] += (
        f" | S4=registered {KU_ID}; original bibliography group archive-group-a25e2f75ce65 retained."
    )
    a_by_candidate[SHORT_CITATION_CANDIDATE].update(
        decision="same",
        ku_id=KU_ID,
        process_ref=PROCESS_REF,
        resolution_note=(
            "source_ref=candidate_ref=chp-7:07_CHP-7_sec_i:l3-9#L9; "
            f"statement={SHORT_STATEMENT}; comparison={PRIMARY_STATEMENT}+{BIB_STATEMENT}. "
            "The p.169 n.2 short form ‘Haskell, 1959’ matches the book’s sole Haskell 1959 bibliography entry; "
            "the adjacent text concerns foreign patronage and the art market. The distinct L. Stone 1959 article "
            "has a different printed byline and is not this citation. Reuse the S4 identity for cand-6240; "
            "the cited article itself was not independently consulted."
        ),
    )
    files[TABLES / "alignment.csv"] = render_csv(a_cols, alignments, a_bom)

    m_cols, manifest, m_bom = read_csv("ku-manifest.csv")
    assert all(row["ku_id"] != KU_ID for row in manifest)
    manifest.append(
        {
            "ku_id": KU_ID,
            "type": "archive",
            "canonical_name": "F. Haskell, The market for Italian art in the 17th century (1959)",
            "name_en": "The market for Italian art in the 17th century",
            "source_task": "patrons-and-painters-full-book-s2",
            "card_path": CARD_REL.as_posix(),
        }
    )
    files[TABLES / "ku-manifest.csv"] = render_csv(m_cols, manifest, m_bom)

    statement_path = TABLES / "book-statements.jsonl"
    statement_raw = statement_path.read_bytes()
    statements = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line]
    assert all(row["statement_id"] != AUTHOR_STATEMENT for row in statements)
    assert any(row["statement_id"] == BIB_STATEMENT for row in statements)
    author_statement = {
        "statement_id": AUTHOR_STATEMENT,
        "segment_id": "chp-21:21_CHP-21Bibliography:l577-614",
        "subject_candidate_id": PRIMARY_CANDIDATE,
        "object_candidate_id": AUTHOR_CANDIDATE,
        "predicate": "authored_by",
        "qualifiers": {
            "source_line_start": 584,
            "source_line_end": 585,
            "printed_page": 425,
            "claim": "The bibliography names F. Haskell as the author of the article.",
            "speaker": "Haskell’s bibliography",
            "text_layer": "bibliographic entry",
            "qualification": "The entry prints initials; cand-9423 is the existing S3 same-person mapping to Francis Haskell. The article contents were not consulted.",
            "mentioned_candidate_ids": [PRIMARY_CANDIDATE, AUTHOR_CANDIDATE],
            "relation_candidate": True,
            "relation_candidate_note": "Bibliographic authorship only; no claim about the article’s contents.",
        },
        "original_quote": "Haskell, F.: ‘The market for Italian art in the 17th century’ in Past and Present, April 1959, .\npp. 48-59.",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
    }
    statement_lines = statement_raw.decode("utf-8").splitlines()
    insert_at = next(i for i, line in enumerate(statement_lines) if json.loads(line)["statement_id"] == BIB_STATEMENT) + 1
    statement_lines.insert(insert_at, json.dumps(author_statement, ensure_ascii=False, separators=(",", ":")))
    files[statement_path] = ("\n".join(statement_lines) + "\n").encode("utf-8")

    mention_cols, mentions, mention_bom = read_csv("mentions.csv")
    assert all(row["mention_id"] != AUTHOR_MENTION for row in mentions)
    assert any(row["mention_id"] == "m-chp21-bib-l577-614-006" for row in mentions)
    mention = {
        "mention_id": AUTHOR_MENTION,
        "segment_id": "chp-21:21_CHP-21Bibliography:l577-614",
        "candidate_id": AUTHOR_CANDIDATE,
        "surface_form": "Haskell, F.",
        "start_char": "570",
        "end_char": "581",
        "note": "Author form in the 1959 article entry; S3 identity reuses the Francis Haskell person KU.",
    }
    mention_path = TABLES / "mentions.csv"
    mention_raw = mention_path.read_bytes()
    with io.StringIO(newline="") as stream:
        csv.DictWriter(stream, fieldnames=mention_cols, lineterminator="\n", extrasaction="ignore").writerow(mention)
        appended_mention = stream.getvalue().encode("utf-8")
    files[mention_path] = mention_raw + (b"" if mention_raw.endswith((b"\n", b"\r")) else b"\n") + appended_mention

    relation_cols, relations, r_bom = read_csv("relations.csv")
    relation_ids = {row["relation_id"] for row in relations}
    relation_rows = [
        {
            "relation_id": "rel-2389",
            "subject_ku_id": PARENT_KU,
            "object_ku_id": KU_ID,
            "predicate": "cites",
            "time": "",
            "role": "Printed note 2",
            "scope": "Haskell’s p.146 n.2 says “See also Haskell, 1959”; the full bibliography identifies this article. Citation pointer only; the article contents were not consulted.",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": f"Chapter 6 printed p.146 n.2 L9; statement={PRIMARY_STATEMENT}",
            "source_file": "02-sources/02-Markdown/06_CHP-6_intro.md",
            "note": "S6 formal; in-book short citation resolved by the full Haskell 1959 bibliography entry.",
        },
        {
            "relation_id": "rel-2390",
            "subject_ku_id": PARENT_KU,
            "object_ku_id": KU_ID,
            "predicate": "cites",
            "time": "",
            "role": "Printed note 2",
            "scope": "Haskell’s p.169 n.2 gives the short form “Haskell, 1959”; the sole Haskell 1959 item in the book bibliography is this article. Citation pointer only; the article contents were not consulted.",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": f"Chapter 7 printed p.169 n.2 L9; statement={SHORT_STATEMENT}",
            "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
            "note": "S6 formal; the nearby passage concerns foreign patronage and the art market; the distinct L. Stone article is excluded from this mapping.",
        },
        {
            "relation_id": "rel-2391",
            "subject_ku_id": KU_ID,
            "object_ku_id": AUTHOR_PERSON_KU,
            "predicate": "authored_by",
            "time": "",
            "role": "Bibliographic author",
            "scope": "The Haskell bibliography prints F. Haskell as the author; the initials form maps through cand-9423 to Francis Haskell. This records bibliographic authorship only, not article claims.",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": f"Chapter 21 printed p.425 L584-L585; statement={AUTHOR_STATEMENT}",
            "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
            "note": "S6 formal; source supports the printed author attribution only; article contents were not consulted.",
        },
    ]
    assert not relation_ids.intersection(row["relation_id"] for row in relation_rows)
    next_relation = max(int(match.group(1)) for row in relations if (match := re.fullmatch(r"rel-(\d+)", row["relation_id"]))) + 1
    assert next_relation == 2389
    relations.extend(relation_rows)
    files[TABLES / "relations.csv"] = render_csv(relation_cols, relations, r_bom)

    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    accepted_raw = accepted_path.read_bytes()
    accepted_text = accepted_raw.decode("utf-8-sig")
    accepted_lines = accepted_text.splitlines()
    accepted_entry = f"- {CARD_REL.as_posix()}"
    assert accepted_entry not in accepted_lines
    claims_index = next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines))
    accepted_lines.insert(claims_index, accepted_entry)
    files[accepted_path] = ("\n".join(accepted_lines) + "\n").encode("utf-8")

    card_text = '''---
title: "《17世纪意大利艺术市场》（The market for Italian art in the 17th century）"
name_en: "The market for Italian art in the 17th century"
type: archive
sub_type: journal_article
evidence_status: source_backed
sources:
- citation: "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)."
  location: "第21章书目，印刷页425，Markdown行584–585；第6章印刷页146注2，行9；第7章印刷页169注2，行9。"
  sentence_summary: "第21章书目著录F. Haskell的论文题名、期刊、月份和页码；第6、7章注释以Haskell 1959为引文定位。"
  original_quotes:
  - source_span: "第21章印刷页425，Markdown行584–585。"
    text: |-
      Haskell, F.: ‘The market for Italian art in the 17th century’ in Past and Present, April 1959,
      pp. 48-59.
  - source_span: "第6章印刷页146注2，Markdown行9。"
    text: "See also Haskell, 1959."
  - source_span: "第7章印刷页169注2，Markdown行9。"
    text: "2 Haskell, 1959."
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: "02-sources/02-Markdown/21_CHP-21Bibliography.md"
    source_span: "Printed p.425, lines 584–585; ch. 6 p.146 n.2; ch. 7 p.169 n.2."
created: '2026-10-27'
updated: '2026-10-27'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp6-chp7-haskell-1959-article-20261027
---

## 内容

### 描述
**中文：** Haskell书目将该期刊论文著录为F. Haskell所作，题为“The market for Italian art in the 17th century”，刊于Past and Present，1959年4月，页48–59。

**English:** Haskell’s bibliography lists F. Haskell’s journal article “The market for Italian art in the 17th century” in *Past and Present*, April 1959, pages 48–59.

### 基本信息
| 字段 | 值 | 证据 |
|---|---|---|
| 期刊 | Past and Present | S1；第21章印刷页425，L584–585；statement=st-chp21-bib-l577-614-entry-06 |
| 出版时间 | 1959年4月 | S1；第21章印刷页425，L584–585；statement=st-chp21-bib-l577-614-entry-06 |
| 文章页码 | 48–59 | S1；第21章印刷页425，L584–585；statement=st-chp21-bib-l577-614-entry-06 |

## 关系与证据

### 身份与外部链接

身份与书目范围以Haskell书内书目为限；未据此声称查阅论文全文。

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|
'''
    assert not CARD.exists()
    files[CARD] = card_text.encode("utf-8")
    return files, appended_mention


def fix_source_quote() -> None:
    path = TABLES / "book-statements.jsonl"
    source = (ROOT / "02-sources/02-Markdown/21_CHP-21Bibliography.md").read_text(encoding="utf-8").splitlines()
    exact_quote = "\n".join(source[583:585])
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    found = False
    changed = False
    for i, line in enumerate(lines):
        row = json.loads(line)
        if row.get("statement_id") != AUTHOR_STATEMENT:
            continue
        found = True
        if row.get("original_quote") != exact_quote:
            row["original_quote"] = exact_quote
            lines[i] = json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            changed = True
        break
    assert found, f"missing {AUTHOR_STATEMENT}"
    if changed:
        path.write_text("".join(lines), encoding="utf-8", newline="")
        print(f"Corrected {AUTHOR_STATEMENT} original_quote to exact cited source lines 584-585.")
    else:
        print(f"{AUTHOR_STATEMENT} original_quote already matches lines 584-585.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the Haskell 1959 article endpoint and adjudicate its linked relations.")
    parser.add_argument("--apply", action="store_true", help="write after reviewing the default dry-run diff")
    parser.add_argument("--fix-source-quote", action="store_true", help="repair the applied S2 statement to match the exact source lines")
    args = parser.parse_args()
    if args.fix_source_quote:
        fix_source_quote()
        return
    files, appended_mention = prepare()
    print("Batch: Haskell 1959 article; S3 cand-6606 -> same; S4 cand-6240 -> new KU; S5 three fields via card table; S6 rel-2389..2391 formal.")
    for path, after in files.items():
        before = path.read_bytes() if path.exists() else b""
        print(unified(path, before, after), end="")
    if not args.apply:
        print("DRY RUN ONLY; no files written.")
        return
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print(f"Applied {len(files)} files. Appended mention bytes={len(appended_mention)}.")


if __name__ == "__main__":
    main()
