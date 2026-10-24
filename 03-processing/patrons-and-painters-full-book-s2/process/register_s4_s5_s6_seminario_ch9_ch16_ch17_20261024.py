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
TASK = "s4-s5-s6-seminario-patriarcale-ch9-ch16-ch17-20261024"
ANCHOR = TASK
PROCESS_REF = f"03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR}"
DATE = "2026-10-24"
SOURCE_ID = "haskell-1980-rev-ed"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)
TICK = chr(96)

UNITS = [
    {
        "candidate_id": "cand-6589",
        "group": "sg3-institution-cand-6589",
        "ku_id": "units/institutions/seminario-patriarcale-venice",
        "card_path": "04-knowledge/units/institutions/seminario-patriarcale-venice.md",
        "type": "institution",
        "canonical_name": "威尼斯宗主教神学院（Seminario Patriarcale, Venice）",
        "name_en": "Seminario Patriarcale, Venice",
    },
    {
        "candidate_id": "cand-10614",
        "group": "archive-group-ecd614e1ccea",
        "ku_id": "units/archives/armanni-sasso-letters-1783-1803-seminario-patriarcale",
        "card_path": "04-knowledge/units/archives/armanni-sasso-letters-1783-1803-seminario-patriarcale.md",
        "type": "archive",
        "canonical_name": "G. A. Armanni致G. M. Sasso的书信两卷（Two volumes of Lettere pittoriche di G. A. Armanni a G. M. Sasso）",
        "name_en": "Two volumes of Lettere pittoriche di G. A. Armanni a G. M. Sasso",
    },
    {
        "candidate_id": "cand-10689",
        "group": "archive-group-a178ede378fa",
        "ku_id": "units/archives/armanni-sasso-letter-1790-07-20",
        "card_path": "04-knowledge/units/archives/armanni-sasso-letter-1790-07-20.md",
        "type": "archive",
        "canonical_name": "G. A. Armanni致G. M. Sasso的信（20 July 1790）（Letter from G. A. Armanni to G. M. Sasso, 20 July 1790）",
        "name_en": "Letter from G. A. Armanni to Giuseppe Maria Sasso, 20 July 1790",
    },
]

SOURCES = {
    "institution": [
        ("第6章，印刷页165，注5，L68。", "02-sources/02-Markdown/06_CHP-6_sec_v.md", "line 68; print p. 165 n. 5", "Haskell cites the unpublished Zibaldone by Tommaso Temanza as MS. 796 in Seminario Patriarcale, Venice.", "5 See the unpublished Zibaldone by Tommaso Temanza—MS. 796 in Seminario Patriarcale, Venice."),
        ("第9章，印刷页261，注2，L405。", "02-sources/02-Markdown/09_CHP-9_intro.md", "line 405; print p. 261 n. 2", "Haskell locates MSS. 788.13, containing inventories drawn up by Pietro Edwards, among the manuscripts at Seminario Patriarcale.", "2 A number of Venetian inventories of the eighteenth century are included in C. A. Levi’s collection of 1900. Others are still unpublished in the Venetian archives, especially those of the Seminario Patriarcale, where MSS. 788.13 contains those drawn up by Pietro Edwards at the downfall of the Republic."),
        ("第13章，印刷页345，注3，L251。", "02-sources/02-Markdown/13_CHP-13_intro.md", "line 251; print p. 345 n. 3", "Haskell reports a manuscript life by P. A. Novelli at Seminario Patriarcale, Venice, MSS. 788.25; neither the manuscript nor Moschini was consulted in this pass.", "3 Toni is referred to in G. A. Moschini, 1924, p. 167, who derives all his information from a manuscript life by the artist P. A. Novelli which is now in the Seminario Patriarcale, Venice—MSS. 788. 25."),
        ("第16章，印刷页374，注3，L74。", "02-sources/02-Markdown/16_CHP-16_intro.md", "line 74; print p. 374 n. 3", "Haskell places two volumes of Armanni–Sasso letters in the Archivio of Seminario Patriarcale, Venice, MSS. 565 and 566.", "3 Two volumes of Lettere pittoriche di G. A. Armanni a G. M Sasso containing hundreds of letters arranged in the vaguest of chronological orders between 1783 and 1803 are in the Archivio of the Seminario Patriarcale, Venice—MSS. 565 and 566."),
        ("第17章，印刷页380，注1，L27。", "02-sources/02-Markdown/17_CHP-17_sec_i.md", "line 27; print p. 380 n. 1", "Haskell gives a manuscript locator for the letter of 20 July 1790 as Seminario Patriarcale, Venice, MSS. 566.", "1 Seminario Patriarcale, Venice—MSS. 566-Letter of 20 July 1790."),
        ("第17章，印刷页380，注5，L30。", "02-sources/02-Markdown/17_CHP-17_sec_i.md", "line 30; print p. 380 n. 5", "Haskell places the manuscript record of Manfrin’s gallery in Seminario Patriarcale, Venice, MSS. 788.13.", "5 The first record of Manfrin’s gallery was made by Pietro Edwards, his adviser, just before the end of the eighteenth century. It exists in manuscript in the Seminario Patriarcale, Venice—MSS. 788.13."),
    ],
    "collection": [
        ("第16章，印刷页374，注3，L74。", "02-sources/02-Markdown/16_CHP-16_intro.md", "line 74; print p. 374 n. 3", "Haskell describes two volumes containing hundreds of letters between Armanni and Sasso, dated 1783–1803 and arranged in a vague chronology, at Seminario Patriarcale MSS. 565 and 566.", "3 Two volumes of Lettere pittoriche di G. A. Armanni a G. M Sasso containing hundreds of letters arranged in the vaguest of chronological orders between 1783 and 1803 are in the Archivio of the Seminario Patriarcale, Venice—MSS. 565 and 566."),
    ],
    "letter": [
        ("第17章，印刷页380，注1，L27。", "02-sources/02-Markdown/17_CHP-17_sec_i.md", "line 27; print p. 380 n. 1", "Haskell identifies a letter from G. A. Armanni to Giuseppe Maria Sasso dated 20 July 1790 and gives the locator Seminario Patriarcale, Venice, MSS. 566; the manuscript was not consulted.", "1 Seminario Patriarcale, Venice—MSS. 566-Letter of 20 July 1790."),
    ],
}


def source_rows(kind: str) -> list[dict]:
    return [
        {
            "citation": BOOK,
            "location": location,
            "sentence_summary": summary,
            "original_quotes": [{"source_span": span, "text": quote}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": source_file, "source_span": span},
        }
        for location, source_file, span, summary, quote in SOURCES[kind]
    ]


def card_bytes(unit: dict) -> bytes:
    if unit["candidate_id"] == "cand-6589":
        sources = source_rows("institution")
        table = (
            "| 字段 | 内容 | 依据 |\n|---|---|---|\n"
            "| 原书机构称谓 | Seminario Patriarcale, Venice | S1–S6；第6、9、13、16、17章相应注释 |\n"
            "| 书内定位功能 | Haskell将该名称用于多条手稿／档案定位；本卡只记录书内称谓，不确认现行馆藏状态或组织沿革 | S1–S6 |\n"
            "| 书内提及的馆藏号 | MSS. 796、788.13、788.25、565、566 | S1–S6 |\n"
        )
        description_zh = "本卡按既有 S3 `new` 身份组，记录 Haskell 将 Seminario Patriarcale 称为多份手稿／档案的保管机构。中文名称为便于阅读的描述性译名，原书称谓保留为规范检索名；本卡不确认机构现行正式名称、组织沿革、建筑位置或当前馆藏状态。不同手稿及卷册仍分别登记为 archive，不与机构合并。"
        description_en = "This card follows the existing S3 `new` identity group and records Haskell’s use of Seminario Patriarcale as the repository named for several manuscripts and archival records. The Chinese rendering is descriptive; the source form remains the retrieval name. This card does not establish the institution’s current official name, organizational history, building location, or present holdings. The cited manuscripts and volumes remain separate archive units."
        relation_text = (
            "本批登记3条直接关系候选；均保留为 pending。受控类型 `located_at` 的当前语义标记为 `needs_split`，而 `held_by` 的域值域不包含 archive→institution；在仓储保管与物理位置谓词明确区分前，不新增 formal 边。详见[本批过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#" + ANCHOR + ")."
        )
    elif unit["candidate_id"] == "cand-10614":
        sources = source_rows("collection")
        table = (
            "| 字段 | 内容 | 依据 |\n|---|---|---|\n"
            "| 原书文献称谓 | Lettere pittoriche di G. A. Armanni a G. M. Sasso | S1；第16章，印刷页374，注3，L74 |\n"
            "| 文献范围 | 两卷；数百封信；Haskell称排列次序仅大略按年代，涵盖1783–1803 | S1；第16章，印刷页374，注3，L74 |\n"
            "| 书内档案号 | MSS. 565、566 | S1；第16章，印刷页374，注3，L74 |\n"
        )
        description_zh = "本卡记录 Haskell 第16章注3所称 G. A. Armanni 与 G. M. Sasso 之间的两卷书信材料，时间范围据该注为1783–1803，馆藏号为MSS. 565、566。中文标题为描述性译名；`Lettere pittoriche` 保留作来源称谓，不冒称经目录确认的原件题名。手稿未独立查阅。该对象是未刊／档案卷册，不同于既有 Vincenzo Armanni 17世纪刊本《Delle lettere...》。"
        description_en = "This card records the two-volume correspondence described in Haskell, Chapter 16, note 3, between G. A. Armanni and G. M. Sasso. The note gives 1783–1803, a broadly chronological arrangement, and shelfmarks MSS. 565 and 566. The Chinese title is descriptive; `Lettere pittoriche` is retained as Haskell’s wording, not asserted as a catalog-verified manuscript title. The manuscripts were not independently consulted. This archival corpus is distinct from the existing seventeenth-century printed collection by Vincenzo Armanni, *Delle lettere...*."
        relation_text = "该卷册与单封1790年信件分别保留不同文献粒度；两者是否构成可记录的部分—整体关系，本批不由相同MSS号推定。仓储定位候选的裁决见[本批过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#" + ANCHOR + ")."
    else:
        sources = source_rows("letter")
        table = (
            "| 字段 | 内容 | 依据 |\n|---|---|---|\n"
            "| 文献描述 | G. A. Armanni致Giuseppe Maria Sasso的信 | S1；第17章，印刷页380，注1，L27 |\n"
            "| 日期 | 20 July 1790 | S1；第17章，印刷页380，注1，L27 |\n"
            "| 书内档案号 | MSS. 566 | S1；第17章，印刷页380，注1，L27 |\n"
        )
        description_zh = "本卡按 Haskell 第17章注1描述一封 G. A. Armanni 致 Giuseppe Maria Sasso 的信，日期为1790年7月20日，书内定位为Seminario Patriarcale, Venice, MSS. 566。中文题名为描述性工作标题，不是原件题名；原信未查阅，馆藏现状亦未独立核验。"
        description_en = "This card records the letter identified in Haskell, Chapter 17, note 1, from G. A. Armanni to Giuseppe Maria Sasso, dated 20 July 1790, with the book’s locator Seminario Patriarcale, Venice, MSS. 566. The title is a descriptive working label, not an original title. The letter was not consulted, and its present holding was not independently verified."
        relation_text = "信件与MSS. 565–566两卷书信材料保持不同的对象粒度；是否构成部分—整体关系留待直接目录或手稿证据。本批仓储定位候选的裁决见[本批过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#" + ANCHOR + ")."
    fm = {
        "title": unit["canonical_name"],
        "name_en": unit["name_en"],
        "type": unit["type"],
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    if unit["type"] == "archive":
        fm["sub_type"] = "correspondence_collection" if unit["candidate_id"] == "cand-10614" else "letter"
    body = (
        "## 内容\n\n### 描述\n\n"
        f"**中文：** {description_zh}\n\n"
        f"**English:** {description_en}\n\n"
        "### 书内名称与定位\n\n" + table + "\n"
        "## 关系与证据\n\n### 关系记录\n\n" + relation_text + "\n"
    )
    fm_text = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    return ("---\n" + fm_text + "---\n\n" + body).encode("utf-8-sig")


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str], bool]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or []), raw.startswith(b"\xef\xbb\xbf")


def csv_bytes(fields: list[str], rows: list[dict[str, str]], bom: bool) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + output.getvalue().encode("utf-8")


def text_bytes(path: Path, text: str) -> bytes:
    bom = path.exists() and path.read_bytes().startswith(b"\xef\xbb\xbf")
    return (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")


def replace_once(text: str, before: str, after: str, label: str) -> str:
    count = text.count(before)
    if count != 1:
        raise ValueError(f"expected one baseline for {label}; found {count}")
    return text.replace(before, after, 1)


def update_accepted(text: str, card_paths: list[str]) -> str:
    lines = text.splitlines()
    claim_pos = next((i for i, line in enumerate(lines) if line.strip() == "claims:"), None)
    if claim_pos is None:
        raise ValueError("accepted.yml has no units/claims boundary")
    for card_path in card_paths:
        addition = f"- {card_path}"
        if addition in lines[:claim_pos]:
            raise ValueError(f"card already appears in accepted.yml: {card_path}")
        insert_at = next(
            (i for i, line in enumerate(lines[:claim_pos]) if line.startswith("- 04-knowledge/units/") and line[2:] > card_path),
            claim_pos,
        )
        lines.insert(insert_at, addition)
        claim_pos += 1
    return "\n".join(lines) + "\n"


def build_outputs() -> tuple[dict[Path, bytes], dict[Path, bytes], dict]:
    paths = {
        "alignment": TABLES / "alignment.csv",
        "manifest": TABLES / "ku-manifest.csv",
        "enrichment": TABLES / "enrichment.jsonl",
        "sources": TABLES / "sources.csv",
        "statements": TABLES / "book-statements.jsonl",
        "accepted": ROOT / "04-knowledge" / "accepted.yml",
        "process": ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md",
        "result": ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md",
        "agents": ROOT / "AGENTS.md",
    }
    if any(not p.is_file() for p in paths.values()):
        raise FileNotFoundError("a required S4/S5/S6 input is missing")
    alignment, alignment_fields, alignment_bom = read_csv(paths["alignment"])
    manifest, manifest_fields, manifest_bom = read_csv(paths["manifest"])
    sources, _, _ = read_csv(paths["sources"])
    statements = [json.loads(line) for line in paths["statements"].read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    enrichment = [json.loads(line) for line in paths["enrichment"].read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    accepted_text = paths["accepted"].read_text(encoding="utf-8-sig")
    process_text = paths["process"].read_text(encoding="utf-8-sig")
    result_text = paths["result"].read_text(encoding="utf-8-sig")
    agents_text = paths["agents"].read_text(encoding="utf-8-sig")

    if len(statements) != 15333 or sum(s.get("qualifiers", {}).get("relation_candidate") is True for s in statements) != 10547:
        raise ValueError("S2/S6 baseline changed; re-audit before applying this batch")
    if len(enrichment) != 13143:
        raise ValueError(f"unexpected S5 baseline: {len(enrichment)}")
    if ANCHOR in process_text:
        raise ValueError("this batch already appears in process/knowledge.md")
    if not any(row.get("source_id") == SOURCE_ID for row in sources):
        raise ValueError(f"missing source registry entry {SOURCE_ID}")
    for unit_sources in SOURCES.values():
        for _, source_file, _, _, _ in unit_sources:
            if not (ROOT / source_file).is_file():
                raise FileNotFoundError(f"missing source file: {source_file}")

    main = [r for r in alignment if r.get("candidate_id") and not r.get("external_source") and not r.get("external_id")]
    main_by_candidate = {r["candidate_id"]: r for r in main}
    if len(main_by_candidate) != len(main):
        raise ValueError("primary S3 candidate rows are not unique")
    if sum(r.get("decision") == "new" and bool(r.get("ku_id")) for r in main) != 2032:
        raise ValueError("S4 mapped baseline changed")
    if sum(r.get("decision") == "new" for r in main) != 5071:
        raise ValueError("S3 new count changed")
    endpoint_ids = {
        cid
        for s in statements
        if s.get("qualifiers", {}).get("relation_candidate") is True
        for cid in (s.get("subject_candidate_id"), s.get("object_candidate_id"))
        if cid
    }
    endpoint_pending = sum(cid in endpoint_ids and r.get("decision") == "new" and not r.get("ku_id") for cid, r in main_by_candidate.items())
    if endpoint_pending != 1319:
        raise ValueError(f"S4 direct-endpoint baseline changed: {endpoint_pending}")

    for unit in UNITS:
        row = main_by_candidate.get(unit["candidate_id"])
        if not row or row.get("decision") != "new" or row.get("ku_id") or unit["group"] not in row.get("resolution_note", ""):
            raise ValueError(f"S3 decision/group changed for {unit['candidate_id']}")
        if unit["candidate_id"] not in endpoint_ids:
            raise ValueError(f"not a current direct S6 endpoint: {unit['candidate_id']}")
        if any(r.get("ku_id") == unit["ku_id"] or r.get("card_path") == unit["card_path"] for r in manifest):
            raise ValueError(f"KU already exists: {unit['ku_id']}")
        if (ROOT / unit["card_path"]).exists() or unit["card_path"] in accepted_text:
            raise ValueError(f"card already exists: {unit['card_path']}")
    if any(r.get("ku_id") == "units/archives/pietro-edwards-inventories-seminario-patriarcale-ms-788-13" for r in manifest) is False:
        raise ValueError("existing MSS. 788.13 archive endpoint is missing")
    if any(r.get("type") == "institution" and r.get("name_en", "").casefold() == "seminario patriarcale, venice" for r in manifest):
        raise ValueError("possible exact institution identity collision")

    target_sids = {
        "st-chp9-p261-note2-seminario-edwards-inventories": {"cand-6589", "cand-8534"},
        "st-chp16-p374-note3-armanni-sasso-letters-and-poore": {"cand-10614", "cand-6589"},
        "st-chp17-p380-note1-armanni-sasso-letter-locator": {"cand-6589", "cand-10689"},
    }
    statement_by_id = {s["statement_id"]: s for s in statements}
    if len(statement_by_id) != len(statements):
        raise ValueError("duplicate S2 statement IDs")
    for sid, expected_endpoints in target_sids.items():
        s = statement_by_id.get(sid)
        if not s or s.get("qualifiers", {}).get("relation_candidate") is not True:
            raise ValueError(f"missing direct S6 candidate: {sid}")
        endpoints = {s.get("subject_candidate_id"), s.get("object_candidate_id")}
        if endpoints != expected_endpoints:
            raise ValueError(f"S2 endpoints changed for {sid}: {endpoints}")
        if re.search(rf"(?m)^\|\s*{re.escape(TICK + sid + TICK)}\s*\|\s*(formal|pending|rejected)\s*\|", process_text):
            raise ValueError(f"S6 disposition already exists: {sid}")

    planned_manifest = list(manifest)
    alignment_after = [dict(r) for r in alignment]
    for unit in UNITS:
        planned_manifest.append({
            "ku_id": unit["ku_id"],
            "type": unit["type"],
            "canonical_name": unit["canonical_name"],
            "name_en": unit["name_en"],
            "source_task": TASK,
            "card_path": unit["card_path"],
        })
        alignment_row = main_by_candidate[unit["candidate_id"]]
        for row in alignment_after:
            if row.get("alignment_id") == alignment_row.get("alignment_id"):
                row["ku_id"] = unit["ku_id"]
                row["process_ref"] = "S3-full-book-2026-10-15"
                row["resolution_note"] += f" S4 registration: mapped existing group {unit['group']} to {unit['ku_id']}; no S3 identity decision was reopened."

    card_bytes_by_path = {u["card_path"]: card_bytes(u) for u in UNITS}
    from scripts import build_field_facts as field_facts
    original_base = field_facts.BASE
    try:
        with tempfile.TemporaryDirectory(prefix="pnp-seminario-preview-") as temp_dir:
            temp_root = Path(temp_dir)
            for card_path, content in card_bytes_by_path.items():
                target = temp_root / card_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            field_facts.BASE = temp_root
            fields, source_registry, warnings, cards_with_tables = field_facts.extract_records(planned_manifest[-len(UNITS):])
    finally:
        field_facts.BASE = original_base
    if warnings or cards_with_tables != 3 or len(fields) != 9:
        raise ValueError(f"S5 extraction mismatch: cards={cards_with_tables}, fields={len(fields)}, warnings={warnings}")
    field_facts.assign_ids(fields, paths["enrichment"])
    if any(r.get("source_ids") != [SOURCE_ID] or r.get("evidence_status") != "source_backed" for r in fields):
        raise ValueError("one or more S5 rows lacks Haskell source support")
    enrichment_after = enrichment + fields

    accepted_after = update_accepted(accepted_text, [u["card_path"] for u in UNITS])
    process_note = (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        f"### 第9、16、17章 Seminario Patriarcale 机构与 Armanni–Sasso 档案端点批次（{DATE}）\n\n"
        "#### S3 身份组与 S4 登记\n\n"
        "沿用既有 S3 `new` 决定：`cand-6589`（`sg3-institution-cand-6589`）登记为来源所称 Seminario Patriarcale 机构；`cand-10614`（`archive-group-ecd614e1ccea`）登记为1783–1803年 Armanni–Sasso 两卷书信材料；`cand-10689`（`archive-group-a178ede378fa`）登记为1790年7月20日单封信。三者映射到各自 KU，不重开 S3。两卷文献集合与单封信保持不同粒度；来源共同出现 MSS. 566 不足以追加 part_of 边。既有 `armanni-delle-lettere` 卡记录的是 Vincenzo Armanni 17世纪刊本，作者、年代、题名及载体不同，不与本批 archive 合并。\n\n"
        "#### S5 来源字段\n\n"
        f"新增{len(fields)}条 Haskell `source_backed` 字段：机构的原书称谓、书内定位功能和被引用馆藏号；两卷文献的原书称谓、范围/时间及馆藏号；单封信的文献描述、日期及馆藏号。所列手稿均未独立查阅，馆藏现状不作外部确认。\n\n"
        "#### S6 逐项裁决\n\n"
        "三条直接关系候选均记为 pending，未新增 `relations.csv` formal 边。现行 `located_at` 虽覆盖 archive→institution 域值，但被项目记录为 `needs_split`；`held_by` 的受控域值不允许 archive→institution。为避免把仓储保管与物理位置混为一边，三项均等待关系谓词边界澄清：\n\n"
        "| statement_id | status | decision / evidence boundary |\n|---|---|---|\n"
        "| `st-chp9-p261-note2-seminario-edwards-inventories` | pending | Haskell注2称MSS. 788.13收有Pietro Edwards编制的库存，位于Seminario Patriarcale档案范围；来源支持书内保管定位，但当前 `located_at` 为 `needs_split`，暂不转为formal。 |\n"
        "| `st-chp16-p374-note3-armanni-sasso-letters-and-poore` | pending | Haskell注3明确称MSS. 565、566的两卷书信在该机构Archivio；关系事实有书内依据，但保管与位置谓词边界未拆分。 |\n"
        "| `st-chp17-p380-note1-armanni-sasso-letter-locator` | pending | Haskell注1给出机构名、MSS. 566与1790-07-20信件的定位式引注；原件未查阅，且 `located_at` 为 `needs_split`。 |\n\n"
        "本批不改 S2 statements、mentions 或独立复核分子。关系解除条件为关系类型对 archive→repository custody 提供不与物理位置混用的受控谓词；待S6后续按类型治理记录衔接。"
    )
    process_after = process_text.rstrip() + process_note + "\n"

    result_marker = "### 本轮进度与后续工作（2026-10-24）"
    if result_text.count(result_marker) != 1:
        raise ValueError("current result marker changed")
    summary = (
        f"**第9、16、17章 Seminario Patriarcale 与 Armanni–Sasso 档案端点批次（{DATE}）：** 沿用3个既有 S3 `new` 组，登记1个institution与2个archive KU并映射3条候选；新增{len(fields)}条 Haskell `source_backed` S5字段。3条直接 S6 候选均 pending：受控 `located_at` 仍为 `needs_split`，`held_by` 不允许 archive→institution；没有新增 formal 边。MSS.565–566两卷材料与1790年单封信保持不同粒度；与既有Vincenzo Armanni刊本分开。S2记录和独立复核分子不变。详见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR})。"
    )
    result_after = result_text.replace(result_marker, result_marker + "\n\n" + summary, 1)
    metric_pairs = [
        ("S4已映射2,032/5,071条new候选，待登记3,039条，其中1,319条触及关系端点；当前KU共2,819个。", "S4已映射2,035/5,071条new候选，待登记3,036条，其中1,316条触及关系端点；当前KU共2,822个。"),
        ("S5字段13,143条，1,634条unverified。", "S5字段13,152条，1,634条unverified。"),
        ("累计逐项裁决1,182条（676 formal、399 pending、107 rejected），尚有9,365条未裁决。", "累计逐项裁决1,185条（676 formal、402 pending、107 rejected），尚有9,362条未裁决。"),
        ("另有1,371个孤立KU", "另有1,374个孤立KU"),
        ("S4已映射2,032/5,071条new候选，待映射3,039条，其中1,319条触及关系端点；", "S4已映射2,035/5,071条new候选，待映射3,036条，其中1,316条触及关系端点；"),
        ("S5有13,143条字段、1,634条unverified", "S5有13,152条字段、1,634条unverified"),
        ("S6已逐项裁决1,182/10,547条，尚余9,365条", "S6已逐项裁决1,185/10,547条，尚余9,362条"),
        ("S6余下9,365条按端点齐备", "S6余下9,362条按端点齐备"),
    ]
    for before, after in metric_pairs:
        if before in result_after:
            result_after = result_after.replace(before, after)
    agents_after = replace_once(
        agents_text,
        "S4已映射2,032/5,071条new候选，待映射3,039条，其中1,319条触及关系端点。",
        "S4已映射2,035/5,071条new候选，待映射3,036条，其中1,316条触及关系端点。",
        "AGENTS S4",
    )
    agents_after = replace_once(agents_after, "S5字段13,143条（1,634条unverified）。", "S5字段13,152条（1,634条unverified）。", "AGENTS S5")
    agents_after = replace_once(
        agents_after,
        "S6已裁决1,182/10,547条（676 formal、399 pending、107 rejected），尚余9,365条；",
        "S6已裁决1,185/10,547条（676 formal、402 pending、107 rejected），尚余9,362条；",
        "AGENTS S6",
    )

    alignment_raw = csv_bytes(alignment_fields, alignment_after, alignment_bom)
    manifest_after = csv_bytes(manifest_fields, planned_manifest, manifest_bom)
    enrich_raw = paths["enrichment"].read_bytes()
    ending = b"" if enrich_raw.endswith((b"\n", b"\r")) else b"\n"
    enrich_after = enrich_raw + ending + b"".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n" for r in fields)
    outputs = {
        paths["alignment"]: alignment_raw,
        paths["manifest"]: manifest_after,
        paths["enrichment"]: enrich_after,
        paths["accepted"]: text_bytes(paths["accepted"], accepted_after),
        paths["process"]: text_bytes(paths["process"], process_after),
        paths["result"]: text_bytes(paths["result"], result_after),
        paths["agents"]: text_bytes(paths["agents"], agents_after),
    }
    outputs.update({ROOT / path: content for path, content in card_bytes_by_path.items()})
    before = {path: path.read_bytes() for path in outputs if path.exists()}
    meta = {
        "task": TASK,
        "candidates": [u["candidate_id"] for u in UNITS],
        "kus_added": len(UNITS),
        "fields_added": len(fields),
        "s2_statements_unchanged": len(statements),
        "direct_s6_statements": len(target_sids),
        "s4_mapped_after": 2035,
        "s4_pending_after": 3036,
        "s4_direct_endpoint_pending_after": 1316,
        "s5_fields_after": len(enrichment) + len(fields),
        "s6_decisions_after": 1185,
        "s6_pending_after": 402,
        "s6_undecided_after": 9362,
        "outputs": [str(p.relative_to(ROOT)) for p in outputs],
    }
    return outputs, before, meta


def main() -> int:
    parser = argparse.ArgumentParser(description="Register source-supported Seminario and Armanni-Sasso relation endpoints.")
    parser.add_argument("--apply", action="store_true", help="write the reviewed batch; default prints a dry run")
    args = parser.parse_args()
    outputs, before, meta = build_outputs()
    if not args.apply:
        print(json.dumps(meta, ensure_ascii=False, indent=2))
        return 0
    backup = ROOT / "06-runtime" / "recovery" / "S4-S5-S6-Seminario-2026-10-24"
    backup.mkdir(parents=True, exist_ok=True)
    for path, content in before.items():
        target = backup / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    (backup / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    written: list[Path] = []
    try:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            temp = path.with_suffix(path.suffix + ".tmp")
            temp.write_bytes(content)
            temp.replace(path)
            written.append(path)
    except Exception:
        for path in written:
            if path in before:
                path.write_bytes(before[path])
            else:
                path.unlink(missing_ok=True)
        raise
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"backup: {backup.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
