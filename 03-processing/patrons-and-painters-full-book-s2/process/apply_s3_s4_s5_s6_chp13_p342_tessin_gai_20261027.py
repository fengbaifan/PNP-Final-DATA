from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_FILE = "02-sources/02-Markdown/13_CHP-13_intro.md"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_CITATION = (
    "Francis Haskell, Patrons and Painters, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
TODAY = "2026-10-27"
ANCHOR = "s3-s4-s5-s6-chp13-p342-tessin-bathsheba-gai-20261027"
PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#"
    + ANCHOR
)

FIGURE = {
    "ku_id": "units/works/gai-venus-emerging-from-baths-for-tessin",
    "type": "work",
    "canonical_name": (
        "泰辛委托安东尼奥·盖伊创作的维纳斯形象（Figure Commissioned by Tessin "
        "from Antonio Gai, Intended as a Venus Emerging from the Baths）"
    ),
    "name_en": (
        "Figure Commissioned by Tessin from Antonio Gai, Intended as a Venus "
        "Emerging from the Baths"
    ),
    "card_path": (
        "04-knowledge/units/works/gai-venus-emerging-from-baths-for-tessin.md"
    ),
    "title": (
        "泰辛委托安东尼奥·盖伊创作的维纳斯形象（Figure Commissioned by Tessin "
        "from Antonio Gai, Intended as a Venus Emerging from the Baths）"
    ),
    "description_zh": (
        "本卡记录哈斯克尔所述泰辛经 Zanetti 之手委托雕塑家 Antonio Gai 制作的"
        "形象；原文说明其预期题材为“从浴池中走出的维纳斯”，并拟与一幅 Bathsheba "
        "同场出现。该段未说明形象是否完成或存世，也未给出媒材或正式题名；本卡题名"
        "为来源限定的描述性工作名。"
    ),
    "description_en": (
        "This card records the figure that Haskell says Tessin commissioned from "
        "sculptor Antonio Gai through Zanetti. Its intended subject was a Venus "
        "emerging from the Baths, and it was meant to appear with a Bathsheba. "
        "The passage does not say whether the figure was completed or survives, "
        "and supplies neither a medium nor a formal title; this is a source-local "
        "descriptive label."
    ),
    "quotes": [
        (
            "lines 101–101; printed p. 342",
            "used his good offices to commission a figure by the sculptor Gai",
        ),
        (
            "lines 101–101; printed p. 342",
            "The figure was, characteristically enough, to represent "
            "‘une Venus sortant des Bains pour figurer avec une Bathsheba de "
            "Giovanni da Bologna qui m’appartient’.",
        ),
    ],
    "facts": [
        (
            "来源所述作品类型",
            "受委托的形象；具体媒材未载",
            "S1；第13章，印刷页342，L101；statement=st-chp13-p342-zanetti-facilitated-gai-commission",
        ),
        (
            "预期题材",
            "从浴池中走出的维纳斯",
            "S1；第13章，印刷页342，L101；statement=st-chp13-p342-gai-figure-intended-to-pair-with-tessins-bathsheba",
        ),
        (
            "完成与存世状态",
            "该段报告委托及预期题材，未说明是否完成或存世",
            "S1；第13章，印刷页342，L101",
        ),
    ],
}

BATHSHEBA = {
    "ku_id": "units/works/tessins-bathsheba-giovanni-da-bologna",
    "type": "work",
    "canonical_name": (
        "泰辛称归其所有的《拔示巴》（Tessin’s Bathsheba, attributed in "
        "Haskell’s text to Giovanni da Bologna）"
    ),
    "name_en": (
        "Tessin’s Bathsheba, attributed in Haskell’s text to Giovanni da Bologna"
    ),
    "card_path": (
        "04-knowledge/units/works/tessins-bathsheba-giovanni-da-bologna.md"
    ),
    "title": (
        "泰辛称归其所有的《拔示巴》（Tessin’s Bathsheba, attributed in "
        "Haskell’s text to Giovanni da Bologna）"
    ),
    "description_zh": (
        "本卡记录哈斯克尔转引的泰辛书信中所称的一幅 Bathsheba。引文将其称为"
        "“Giovanni da Bologna”的作品，并由泰辛说“属于我”。此处只保留书内归属"
        "表述；“Giovanni da Bologna”的具体人物身份仍为 S3 待证，也未确认作品版本、"
        "媒材、日期、现存地点或正式题名。卡名为描述性工作名。"
    ),
    "description_en": (
        "This card records the Bathsheba named in the letter quoted by Haskell. "
        "The quotation calls it a work by Giovanni da Bologna and has Tessin say "
        "that it belongs to him. These are source-reported statements only: the "
        "identity behind Giovanni da Bologna remains undecided in S3, and the "
        "passage does not identify a physical version, medium, date, present "
        "location, or formal title. The card title is descriptive."
    ),
    "quotes": [
        (
            "lines 101–101; printed p. 342",
            "une Bathsheba de Giovanni da Bologna qui m’appartient",
        ),
    ],
    "facts": [
        (
            "来源称名",
            "Bathsheba",
            "S1；第13章，印刷页342，L101；statement=st-chp13-p342-tessin-owned-giovanni-da-bologna-bathsheba",
        ),
        (
            "来源归属用语",
            "Giovanni da Bologna",
            "S1；第13章，印刷页342，L101；statement=st-chp13-p342-bathsheba-attributed-to-giovanni-da-bologna",
        ),
    ],
}

NEW_STATEMENTS = [
    {
        "statement_id": "st-chp13-p342-venus-figure-attributed-to-gai",
        "segment_id": "chp-13:13_CHP-13_intro:l98-105",
        "subject_candidate_id": "cand-10082",
        "object_candidate_id": "cand-1099",
        "predicate": "was_attributed_to_sculptor_gai_in_commission_context",
        "qualifiers": {
            "source_line_start": 101,
            "source_line_end": 101,
            "printed_page": 342,
            "pdf_physical_page": 11,
            "claim": "Haskell reports the commissioned figure as a figure by sculptor Antonio Gai.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "qualification": (
                "This records Haskell’s source attribution in the commission context; "
                "it does not establish that the figure was executed or survives. "
                "Footnote 4 points to Tessin’s third letter, which was not independently consulted."
            ),
            "mentioned_candidate_ids": ["cand-10082", "cand-1099"],
            "ocr_corrections": [],
            "relation_candidate": True,
            "relation_candidate_note": (
                "Atomic work-to-person source attribution; completion is not asserted."
            ),
        },
        "original_quote": "a figure by the sculptor Gai",
        "origin": "book",
        "source_file": SOURCE_FILE,
    },
    {
        "statement_id": "st-chp13-p342-bathsheba-attributed-to-giovanni-da-bologna",
        "segment_id": "chp-13:13_CHP-13_intro:l98-105",
        "subject_candidate_id": "cand-10083",
        "object_candidate_id": "cand-10084",
        "predicate": "was_attributed_to_giovanni_da_bologna",
        "qualifiers": {
            "source_line_start": 101,
            "source_line_end": 101,
            "printed_page": 342,
            "pdf_physical_page": 11,
            "claim": (
                "The quoted wording attributes Tessin’s Bathsheba to Giovanni da Bologna."
            ),
            "speaker": "Tessin, quoted by Haskell",
            "text_layer": "embedded first-person quotation",
            "qualification": (
                "The named person’s identity remains unresolved in S3; no match to "
                "Giambologna or another person is asserted. Footnote 4 points to "
                "Tessin’s third letter, which was not independently consulted."
            ),
            "mentioned_candidate_ids": ["cand-10083", "cand-10084"],
            "ocr_corrections": [],
            "relation_candidate": True,
            "relation_candidate_note": (
                "Source attribution; person endpoint remains an undecided S3 candidate."
            ),
        },
        "original_quote": "une Bathsheba de Giovanni da Bologna",
        "origin": "book",
        "source_file": SOURCE_FILE,
    },
]


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
    entries: list[tuple[dict[str, str], str | None]] = []
    found: set[str] = set()
    for row in reader:
        end_line = reader.line_num
        normalized = {k: (v or "") for k, v in row.items() if k is not None}
        row_id = normalized.get(key, "")
        found.add(row_id)
        changed = dict(normalized)
        changed.update(updates.get(row_id, {}))
        raw = "".join(physical[previous_line:end_line])
        entries.append((changed, raw if row_id not in updates else None))
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


def make_card(ku: dict) -> bytes:
    quote_lines = []
    for span, quote in ku["quotes"]:
        quote_lines.extend(
            [
                f"      - source_span: {json.dumps(span, ensure_ascii=False)}",
                f"        text: {json.dumps(quote, ensure_ascii=False)}",
            ]
        )
    facts = ["### 来源所载字段", "", "| 字段 | 值 | 证据 |", "|---|---|---|"]
    facts.extend(
        f"| {field} | {value} | {evidence} |" for field, value, evidence in ku["facts"]
    )
    text = (
        "---\n"
        f"title: {json.dumps(ku['title'], ensure_ascii=False)}\n"
        f"name_en: {json.dumps(ku['name_en'], ensure_ascii=False)}\n"
        "type: work\n"
        "evidence_status: source_backed\n"
        "sources:\n"
        f"  - citation: {json.dumps(SOURCE_CITATION, ensure_ascii=False)}\n"
        f"    location: {json.dumps('第13章，印刷页342，L101；PDF物理页11。', ensure_ascii=False)}\n"
        f"    sentence_summary: {json.dumps(ku['description_zh'], ensure_ascii=False)}\n"
        "    original_quotes:\n"
        + "\n".join(quote_lines)
        + "\n"
        "    evidence_ref:\n"
        "      doc_id: patrons-and-painters\n"
        f"      source_file: {SOURCE_FILE}\n"
        "      source_span: \"Markdown lines 98–105; printed p. 342, line 101; PDF physical p. 11\"\n"
        f"created: '{TODAY}'\n"
        f"updated: '{TODAY}'\n"
        f"process_ref: {PROCESS_REF}\n"
        "---\n\n"
        "## 内容\n\n"
        "### 描述\n"
        f"**中文：** {ku['description_zh']}\n\n"
        f"**English:** {ku['description_en']}\n\n"
        + "\n".join(facts)
        + "\n\n## 关系与证据\n\n"
        "### 身份与外部链接\n\n"
        "本卡按 Haskell 第13章 p.342 的书内指称建立来源限定的作品身份；"
        "没有匹配外部作品记录，也不声称存在已完成或存世的实物版本。\n\n"
        "### 关系记录\n\n"
        "正式关系由 relations.csv 逐项裁决并定向生成；待证关系见本批过程记录。\n\n"
        "### 关系候选入口\n\n"
        f"[本批 S2、S3、S4、S5 与 S6 记录](../../../03-processing/"
        f"patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR})\n"
    )
    return text.encode("utf-8")


def statement_bytes(path: Path, additions: list[dict]) -> bytes:
    original = path.read_bytes()
    lines = original.decode("utf-8").splitlines()
    existing_ids = {json.loads(line)["statement_id"] for line in lines if line.strip()}
    for item in additions:
        if item["statement_id"] in existing_ids:
            raise ValueError(f"Duplicate statement ID: {item['statement_id']}")
    rendered = lines + [json.dumps(item, ensure_ascii=False) for item in additions]
    return ("\n".join(rendered) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the bounded changes; without this flag only preflight.",
    )
    args = parser.parse_args()

    alignment_path = TABLES / "alignment.csv"
    candidate_path = TABLES / "entity-candidates.csv"
    manifest_path = TABLES / "ku-manifest.csv"
    relation_path = TABLES / "relations.csv"
    statement_path = TABLES / "book-statements.jsonl"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"

    alignment_rows = list(csv.DictReader(alignment_path.open(encoding="utf-8-sig", newline="")))
    candidate_rows = list(csv.DictReader(candidate_path.open(encoding="utf-8-sig", newline="")))
    manifest_rows = list(csv.DictReader(manifest_path.open(encoding="utf-8-sig", newline="")))
    relation_rows = list(csv.DictReader(relation_path.open(encoding="utf-8-sig", newline="")))
    alignment_by_id = {row["alignment_id"]: row for row in alignment_rows}
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    manifest_ids = {row["ku_id"] for row in manifest_rows}
    relation_ids = {row["relation_id"] for row in relation_rows}
    existing_statement_ids = {
        json.loads(line)["statement_id"]
        for line in statement_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }

    if alignment_by_id["aln-10254"]["decision"] != "undecided" or alignment_by_id["aln-10254"]["ku_id"]:
        raise ValueError("Unexpected starting state for aln-10254")
    if alignment_by_id["aln-10255"]["decision"] != "new" or alignment_by_id["aln-10255"]["ku_id"]:
        raise ValueError("Unexpected starting state for aln-10255")
    if alignment_by_id["aln-10256"]["decision"] != "undecided" or alignment_by_id["aln-10256"]["ku_id"]:
        raise ValueError("Unexpected starting state for aln-10256")
    if candidate_by_id["cand-10082"]["suggested_type"] != "work":
        raise ValueError("cand-10082 is no longer a work candidate")
    if candidate_by_id["cand-10083"]["suggested_type"] != "work":
        raise ValueError("cand-10083 is no longer a work candidate")
    if candidate_by_id["cand-10084"]["suggested_type"] != "person":
        raise ValueError("cand-10084 is no longer a person candidate")
    if any(ku["ku_id"] in manifest_ids or (ROOT / ku["card_path"]).exists() for ku in (FIGURE, BATHSHEBA)):
        raise ValueError("A planned KU or card path already exists")
    if set(item["statement_id"] for item in NEW_STATEMENTS) & existing_statement_ids:
        raise ValueError("A planned S2 statement ID already exists")

    next_number = max(int(row["relation_id"].split("-")[1]) for row in relation_rows) + 1
    if next_number != 2427 or any(f"rel-{n:04d}" in relation_ids for n in range(2427, 2431)):
        raise ValueError("Unexpected next relation IDs")

    alignment_updates = {
        "aln-10254": {
            "decision": "new",
            "ku_id": FIGURE["ku_id"],
            "process_ref": PROCESS_REF,
            "resolution_note": (
                alignment_by_id["aln-10254"]["resolution_note"]
                + " | S3 re-opened by direct-endpoint registration (2026-10-27): "
                "the source identifies a distinct commissioned figure by Antonio Gai "
                "with an intended Venus subject; planned or unrealized work can retain "
                "a source-local work identity. group=sg3-work-cand-10082; distinct "
                "from cand-10083 Bathsheba; mapped to "
                + FIGURE["ku_id"]
                + ". Completion, survival, exact medium and external object identity "
                "remain unasserted."
            ),
        },
        "aln-10255": {
            "ku_id": BATHSHEBA["ku_id"],
            "process_ref": PROCESS_REF,
            "resolution_note": (
                alignment_by_id["aln-10255"]["resolution_note"]
                + " | S4 mapped existing new identity group "
                "workgrp-5a34e5c0b4f7fc to "
                + BATHSHEBA["ku_id"]
                + "; kept distinct from the planned Gai figure. The attribution "
                "name and Tessin ownership wording are recorded only as reported by Haskell."
            ),
        },
        "aln-10256": {
            "process_ref": PROCESS_REF,
            "resolution_note": (
                alignment_by_id["aln-10256"]["resolution_note"]
                + " | S6 endpoint review (2026-10-27): Haskell’s quoted attribution "
                "names Giovanni da Bologna, but no accepted person KU establishes "
                "whether this form is the Giambologna index candidate cand-1160. "
                "Keep undecided with no KU; reopen only when authority evidence "
                "directly supports that identity match."
            ),
        },
    }

    relation_additions = [
        {
            "relation_id": "rel-2427",
            "subject_ku_id": FIGURE["ku_id"],
            "object_ku_id": "units/persons/carl-gustav-tessin",
            "predicate": "commissioned_by",
            "time": "Date not stated in Haskell’s p.342 passage.",
            "role": "Commissioner",
            "scope": (
                "Haskell reports that Tessin commissioned this figure through Zanetti’s "
                "good offices. This records the source-local commission; it does not "
                "claim the figure was executed or survives."
            ),
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": (
                "Chapter 13, printed p.342 L101; "
                "statement=st-chp13-p342-zanetti-facilitated-gai-commission"
            ),
            "source_file": SOURCE_FILE,
            "note": "S6 formal; preserve commissioned status and unknown realization.",
        },
        {
            "relation_id": "rel-2428",
            "subject_ku_id": FIGURE["ku_id"],
            "object_ku_id": "units/persons/antonio-gai",
            "predicate": "created_by",
            "time": "Date not stated in Haskell’s p.342 passage.",
            "role": "Source-reported sculptor attribution",
            "scope": (
                "Haskell calls the commissioned figure one by sculptor Gai. This edge "
                "records the source’s creator attribution in the commission context; "
                "it does not establish execution or survival."
            ),
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": (
                "Chapter 13, printed p.342 L101; "
                "statement=st-chp13-p342-venus-figure-attributed-to-gai"
            ),
            "source_file": SOURCE_FILE,
            "note": "S6 formal with source-attribution and realization limits in scope.",
        },
        {
            "relation_id": "rel-2429",
            "subject_ku_id": FIGURE["ku_id"],
            "object_ku_id": BATHSHEBA["ku_id"],
            "predicate": "pendant_of",
            "time": "Intended pairing reported in Haskell’s p.342 passage; date not stated.",
            "role": "Intended companion work",
            "scope": (
                "Haskell says the commissioned figure was intended to figure with "
                "Tessin’s Bathsheba. This records the stated pairing intention only; "
                "it does not establish completion or actual joint display."
            ),
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": (
                "Chapter 13, printed p.342 L101; "
                "statement=st-chp13-p342-gai_figure_intended_to_pair_with_tessins_bathsheba"
            ),
            "source_file": SOURCE_FILE,
            "note": "S6 formal; intended pairing is explicit, physical display is not asserted.",
        },
        {
            "relation_id": "rel-2430",
            "subject_ku_id": BATHSHEBA["ku_id"],
            "object_ku_id": "units/persons/carl-gustav-tessin",
            "predicate": "owned_by",
            "time": "At the time of the third Tessin letter cited by Haskell; date not stated.",
            "role": "Owner as claimed by Tessin",
            "scope": (
                "Haskell quotes Tessin saying qui m’appartient. This records Tessin’s "
                "own ownership claim in that letter context; the legal scope, exact "
                "date, and later ownership are not established."
            ),
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": (
                "Chapter 13, printed p.342 L101; "
                "statement=st-chp13-p342-tessin_owned_giovanni_da_bologna_bathsheba"
            ),
            "source_file": SOURCE_FILE,
            "note": "S6 formal as a source-reported historical ownership claim only.",
        },
    ]

    manifest_additions = [
        {
            "ku_id": ku["ku_id"],
            "type": ku["type"],
            "canonical_name": ku["canonical_name"],
            "name_en": ku["name_en"],
            "source_task": "patrons-and-painters-full-book-s2",
            "card_path": ku["card_path"],
        }
        for ku in (FIGURE, BATHSHEBA)
    ]
    writes = {
        TABLES / "alignment.csv": csv_bytes(
            alignment_path, alignment_updates, [], "alignment_id"
        ),
        TABLES / "ku-manifest.csv": csv_bytes(
            manifest_path, {}, manifest_additions, "ku_id"
        ),
        TABLES / "relations.csv": csv_bytes(
            relation_path, {}, relation_additions, "relation_id"
        ),
        statement_path: statement_bytes(statement_path, NEW_STATEMENTS),
        accepted_path: accepted_bytes([ku["card_path"] for ku in (FIGURE, BATHSHEBA)]),
    }
    for ku in (FIGURE, BATHSHEBA):
        writes[ROOT / ku["card_path"]] = make_card(ku)

    print(
        "Preflight: S3 cand-10082 -> new; S4 maps cand-10082/cand-10083; "
        "cand-10084 remains undecided with an explicit reopen condition."
    )
    print(
        "S6: 4 formal relations will be recorded; 2 additional source claims "
        "(Tessin’s assessment and Giovanni da Bologna attribution) remain pending in the process log."
    )
    print(f"Prepared {len(writes)} bounded writes; no file has been changed.")
    for path, content in writes.items():
        current_size = path.stat().st_size if path.exists() else 0
        print(f"  {path.relative_to(ROOT)}: {current_size} -> {len(content)} bytes")
    if not args.apply:
        print("Dry run only. Review the bounded changes, then pass --apply to write.")
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
