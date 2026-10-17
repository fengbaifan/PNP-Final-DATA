from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MENTIONS_PATH = TABLES / "mentions.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BAD_MENTION = "m-s2-ch13-p337-011"
PASQUALI_STATEMENT = "st-chp13-p337-smith-controlled-interest-in-pasquali-firm"

TARGETS = [
    {
        "candidate": "cand-9799",
        "group": "sg3-institution-cand-9799",
        "ku": "units/institutions/albrizziana-printing-house-venice",
        "card": "04-knowledge/units/institutions/albrizziana-printing-house-venice.md",
        "name_zh": "威尼斯阿尔布里齐印刷所",
        "name_en": "Albrizziana Printing House, Venice",
        "relations": [
            "st-chp13-p336-albrizzi-shop-flourishing-artistic-centre",
            "st-chp13-p336-longhi-provided-drawings-for-albrizzi-firm",
            "st-chp13-p336-novelli-provided-drawings-for-albrizzi-firm",
            "st-chp13-p336-zais-provided-drawings-for-albrizzi-firm",
        ],
    },
    {
        "candidate": "cand-9172",
        "group": "sg3-institution-cand-9172",
        "ku": "units/institutions/pasquali-venetian-publishing-firm",
        "card": "04-knowledge/units/institutions/pasquali-venetian-publishing-firm.md",
        "name_zh": "吉安巴蒂斯塔·帕斯夸利的威尼斯印刷所",
        "name_en": "Giambattista Pasquali's Venetian Publishing Firm",
        "relations": [
            "st-chp10-p299-pasquali-firm-launched",
            "st-chp10-p301-note1-grosley-quote",
            PASQUALI_STATEMENT,
        ],
    },
]


def source(citation_location: str, summary: str, quote: str, span: str, source_file: str) -> dict:
    return {
        "citation": BOOK_CITATION,
        "location": citation_location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": source_file, "source_span": span},
    }


def make_card(target: dict) -> str:
    if target["candidate"] == "cand-9799":
        source_rows = [
            source(
                "第10章；印刷页326；OCR L220",
                "A pamphlet imprint names the Stamperia Albrizziana in Venice.",
                "Nella Stamperia Albrizziana.",
                "line 220",
                "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
            ),
            source(
                "第13章；印刷页336；OCR L46–48",
                "Haskell discusses Albrizzi's publishing firm and shop, and says it became an important artistic centre in Venice.",
                "Pietro Antonio Novelli, Giuseppe Zais and Alessandro Longhi all provided occasional drawings for the firm, and his shop became one of the most flourishing artistic centres in Venice",
                "lines 46–48",
                "02-sources/02-Markdown/13_CHP-13_intro.md",
            ),
        ]
        body = """## 内容

### 描述

**中文：** 本卡登记威尼斯的 Stamperia Albrizziana 印刷所。第10章一组庆贺 Giorgio Pisani 当选的印刷品，其一的刊印款识为 “Nella Stamperia Albrizziana”；第13章称 Albrizzi 的 firm/shop 位于威尼斯，并记录 Pietro Antonio Novelli、Giuseppe Zais 与 Alessandro Longhi 曾为其提供图稿。中文名为描述性译名。

**English:** This card records the Stamperia Albrizziana printing establishment in Venice. An imprint on one of the pamphlets celebrating Giorgio Pisani's election reads “Nella Stamperia Albrizziana.” Chapter 13 refers to Albrizzi's firm/shop in Venice and says Pietro Antonio Novelli, Giuseppe Zais, and Alessandro Longhi supplied drawings for it. The display name is descriptive.

### 身份边界

此 institution 由明确的印刷款识支持。与索引中的 Accademia Albrizziana 分开登记；不因名称相似而合并。第13章 p.337 所称 “the firm” 在上下文中指 Pasquali 的出版事业，提及映射已更正至独立候选 `cand-9172`。

The institution is supported by an explicit printing imprint. It remains separate from the indexed Accademia Albrizziana; similarity of names is not treated as identity. The p.337 phrase “the firm” refers in context to Pasquali's publishing venture, and that mention has been remapped to the separate candidate `cand-9172`.

## 关系与证据

4条直接 S2 `relation_candidate` 留待 S6：`st-chp13-p336-albrizzi-shop-flourishing-artistic-centre`, `st-chp13-p336-longhi-provided-drawings-for-albrizzi-firm`, `st-chp13-p336-novelli-provided-drawings-for-albrizzi-firm`, `st-chp13-p336-zais-provided-drawings-for-albrizzi-firm`。未新增正式关系。
"""
    else:
        source_rows = [
            source(
                "第10章；印刷页299；OCR L362–363",
                "Haskell says Smith launched a publishing firm for the young G. B. Pasquali in the early 1730s.",
                "Early in the 1730s he began to take an interest in publishing which he put into practice by launching the firm of a young man, G. B. Pasquali.",
                "lines 362–363",
                "02-sources/02-Markdown/10_CHP-10_intro.md",
            ),
            source(
                "第10章；印刷页301注1；OCR L589",
                "Haskell quotes Grosley referring to Jean-Baptiste Pasquali's printing establishment and its reliance on Joseph Smith's funds; the quoted work was not independently consulted.",
                "L'Imprimerie de Jean-Baptiste Pasquali",
                "line 589",
                "02-sources/02-Markdown/10_CHP-10_intro.md",
            ),
            source(
                "第13章；印刷页337；OCR L53",
                "In the paragraph about Pasquali, Haskell says his patron Joseph Smith retained a controlling interest in the firm.",
                "his patron Joseph Smith, who retained a controlling interest in the firm",
                "line 53",
                "02-sources/02-Markdown/13_CHP-13_intro.md",
            ),
        ]
        body = """## 内容

### 描述

**中文：** 本卡登记哈斯克尔所述吉安巴蒂斯塔·帕斯夸利在威尼斯的出版事业。第10章称 Joseph Smith 在18世纪30年代初为年轻的 G. B. Pasquali 创办了一家出版公司，并参与其学术工作；第301页注1又引述 Grosley 对 Jean-Baptiste Pasquali 印刷所的说法。第13章在帕斯夸利段落中继续称 Smith 对该公司保有控股权益。哈斯克尔没有给出该公司的正式商业名称，所引 Grosley 原文也未独立查阅；本卡按书内身份描述命名。

**English:** This card records the publishing venture associated with Giambattista Pasquali in Haskell's account. Chapter 10 says Joseph Smith launched a firm for the young G. B. Pasquali in the early 1730s and took part in its intellectual work; note 1 on p. 301 quotes Grosley referring to Jean-Baptiste Pasquali's printing establishment. Chapter 13, in its discussion of Pasquali, says Smith retained a controlling interest in the firm. Haskell does not give the venture's formal business name, and Grosley's cited text was not independently consulted; the card uses a descriptive identity label.

### 身份边界

此 institution 与人物 `units/persons/pasquali` 分立。第13章 p.337 的 “the firm” 指本卡对象，不是 p.336 所述 Albrizzi 印刷所；对应 S2 提及与 statement endpoint 已依段落语境改映至 `cand-9172`。不据 nested quotation 建立外部核实状态。

This institution remains distinct from the person `units/persons/pasquali`. In Chapter 13, p. 337, “the firm” refers to this unit, not Albrizzi's printing establishment discussed on p. 336; the S2 mention and statement endpoint have been remapped to `cand-9172` on contextual grounds. The nested quotation does not establish external verification.

## 关系与证据

3条直接 S2 `relation_candidate` 留待 S6：`st-chp10-p299-pasquali-firm-launched`, `st-chp10-p301-note1-grosley-quote`, `st-chp13-p337-smith-controlled-interest-in-pasquali-firm`。原书语境及嵌套引文身份均保留待审；本卡未新增正式关系。
"""
    fm = {
        "title": f"{target['name_zh']}（{target['name_en']}）",
        "name_en": target["name_en"],
        "type": "institution",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": PROCESS_REF,
    }
    return f"---\n{yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000)}---\n\n{body}"


def statement_file_with_local_correction(planned_statement: dict) -> bytes:
    raw = STATEMENTS_PATH.read_bytes()
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    text = raw.decode("utf-8-sig")
    output = []
    matches = 0
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        item = json.loads(body)
        if item.get("statement_id") == PASQUALI_STATEMENT:
            output.append(json.dumps(planned_statement, ensure_ascii=False) + ending)
            matches += 1
        else:
            output.append(line)
    assert matches == 1, f"expected one statement line, found {matches}"
    return bom + "".join(output).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(ENTITY_PATH)
    alignment_fields, alignment = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    mention_fields, mentions = sync.read_csv(MENTIONS_PATH)
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignment if not row.get("external_source")}
    manifest_by_id = {row["ku_id"]: row for row in manifest}

    targets_by_id = {target["candidate"]: target for target in TARGETS}
    for target in TARGETS:
        cid = target["candidate"]
        decision = alignment_by_id[cid]
        assert candidate_by_id[cid]["suggested_type"] == "institution"
        assert decision["decision"] == "new" and not decision.get("ku_id")
        assert sync.get_group(decision.get("resolution_note", "")) == target["group"]
        assert target["ku"] not in manifest_by_id and not (ROOT / target["card"]).exists()
        assert f"- {target['card']}" not in accepted_lines

    imprint_rows = [row for row in manifest if row["type"] == "institution" and "Albrizzi".casefold() in (row["canonical_name"] + row["name_en"]).casefold()]
    assert not imprint_rows, f"possible existing Albrizzi institution: {imprint_rows}"
    pasquali_rows = [row for row in manifest if row["type"] == "institution" and "Pasquali".casefold() in (row["canonical_name"] + row["name_en"]).casefold()]
    assert not pasquali_rows, f"possible existing Pasquali institution: {pasquali_rows}"

    bad_mention = next(row for row in mentions if row["mention_id"] == BAD_MENTION)
    assert bad_mention["candidate_id"] == "cand-9799" and bad_mention["surface_form"].casefold() == "the firm"
    statements = sync.load_statements()
    statement = next(row for row in statements if row["statement_id"] == PASQUALI_STATEMENT)
    assert statement["object_candidate_id"] == "cand-9799"
    assert "cand-9799" in statement.get("qualifiers", {}).get("mentioned_candidate_ids", [])
    assert "cand-9172" not in statement.get("qualifiers", {}).get("mentioned_candidate_ids", [])

    statement_by_id = {row["statement_id"]: row for row in statements}
    for target in TARGETS:
        for sid in target["relations"]:
            assert sid in statement_by_id, f"missing relation candidate: {sid}"
            row = statement_by_id[sid]
            assert row.get("qualifiers", {}).get("relation_candidate"), f"not a relation candidate: {sid}"
    assert statement_by_id["st-chp13-p336-albrizzi-shop-flourishing-artistic-centre"]["subject_candidate_id"] == "cand-9799"
    assert statement_by_id["st-chp10-p299-pasquali-firm-launched"]["object_candidate_id"] == "cand-9172"

    planned_mentions = [dict(row) for row in mentions]
    for row in planned_mentions:
        if row["mention_id"] == BAD_MENTION:
            row["candidate_id"] = "cand-9172"
            row["note"] = "In the p.337 paragraph the firm is Pasquali's publishing venture, not the Albrizziana press; corrected by immediate discourse context and aligned to S3 group sg3-institution-cand-9172."

    planned_statements = [dict(row) for row in statements]
    for row in planned_statements:
        if row["statement_id"] == PASQUALI_STATEMENT:
            row["object_candidate_id"] = "cand-9172"
            q = dict(row["qualifiers"])
            q["mentioned_candidate_ids"] = ["cand-9172" if cid == "cand-9799" else cid for cid in q["mentioned_candidate_ids"]]
            q["mentioned_candidate_ids"] = list(dict.fromkeys(q["mentioned_candidate_ids"]))
            q["qualification"] = (q.get("qualification", "") + " Contextual endpoint correction: 'the firm' belongs to Pasquali's publishing venture, distinct from Albrizzi's establishment on the preceding page.").strip()
            row["qualifiers"] = q
    planned_statement = next(row for row in planned_statements if row["statement_id"] == PASQUALI_STATEMENT)
    planned_statement_bytes = statement_file_with_local_correction(planned_statement)

    planned_alignment = [dict(row) for row in alignment]
    planned_manifest = [dict(row) for row in manifest]
    for target in TARGETS:
        for row in planned_alignment:
            if row.get("candidate_id") == target["candidate"] and not row.get("external_source"):
                row["ku_id"] = target["ku"]
                row["resolution_note"] = (row.get("resolution_note", "") +
                    f" S4 registration: mapped {target['group']} to {target['ku']}.")
        planned_manifest.append({
            "ku_id": target["ku"],
            "type": "institution",
            "canonical_name": target["name_zh"],
            "name_en": target["name_en"],
            "source_task": TASK,
            "card_path": target["card"],
        })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s4-albrizzi-and-pasquali-printing-institutions\"></a>\n\n"
        "### S4 institution：Albrizziana 与 Pasquali 两家印刷机构登记（2026-10-17）\n\n"
        "`cand-9799` 沿用 S3 组 `sg3-institution-cand-9799`，依据第10章 p.326 的 “Nella Stamperia Albrizziana” 印刷款识及第13章 p.336 对 Albrizzi firm/shop 的叙述登记；"
        "与索引 Accademia Albrizziana 保持区分。`cand-9172` 沿用 S3 组 `sg3-institution-cand-9172`，依据第10章 p.299、p.301 及第13章 p.337 登记为 Pasquali 出版事业；正式商号未见于书内。\n\n"
        "修正一处 S2 提及与关系端点错配：`m-s2-ch13-p337-011` 的 “the firm” 依 p.337 段落明确回指 Pasquali，故从 `cand-9799` 改至 `cand-9172`；"
        f"`{PASQUALI_STATEMENT}` 的 object_candidate_id 及 mentioned_candidate_ids 同步改至 `cand-9172`。这是局部上下文映射修正，不改变两组 S3 决定。"
        "Albrizzi 组4条、Pasquali 组3条直接 relation_candidate 留待 S6，未新增正式关系。"
        f"\n\nS4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 institution：Albrizziana 与 Pasquali 印刷机构登记（2026-10-17）\n\n"
        "`cand-9799` 登记为 [威尼斯阿尔布里齐印刷所](../units/institutions/albrizziana-printing-house-venice.md)；"
        "`cand-9172` 登记为 [吉安巴蒂斯塔·帕斯夸利的威尼斯印刷所](../units/institutions/pasquali-venetian-publishing-firm.md)。"
        "p.337 的 “the firm” 提及和 relation-candidate 端点已从 Albrizzi 候选更正至 Pasquali 机构候选。"
        "两组共7条关系候选留待 S6，未新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    for target in TARGETS:
        card = target["card"]
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > card),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {card}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print("S4 institution dry-run passed: groups=2; candidates=2; corrected mention and statement endpoint=1")
        print("Albrizziana and Pasquali presses distinct; Accademia Albrizziana kept separate; formal_relations_added=0")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    for target in TARGETS:
        (ROOT / target["card"]).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / target["card"]).write_text(make_card(target), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    sync.write_csv(MENTIONS_PATH, mention_fields, planned_mentions)
    STATEMENTS_PATH.write_bytes(planned_statement_bytes)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups=2; registered={sync.fmt(totals['registered_groups'])}/"
        f"{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/"
        f"{sync.fmt(totals['pending_members'])}; manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
