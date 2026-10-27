from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_REF = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp5-p137-campaigns-low-countries-20261027"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_iii.md"
SOURCE_ID = "haskell-1980-rev-ed"
EVENT_ID = "units/events/alessandro-farnese-campaigns-low-countries"
PLACE_ID = "units/places/low-countries"
EVENT_PATH = "04-knowledge/units/events/alessandro-farnese-campaigns-low-countries.md"
PLACE_PATH = "04-knowledge/units/places/low-countries.md"
STATEMENT_IDS = {
    "st-chp5-p137-de-bello-farnese-campaigns",
    "st-chp5-p137-miel-borgognone-strada-collaboration",
    "st-chp5-p137-miel-contributed-to-de-bello-illustrations",
    "st-chp5-p137-borgognone-contributed-to-de-bello-illustrations",
    "st-chp5-p137-unnamed-artists-contributed-to-de-bello-illustrations",
    "st-chp5-p137-de-bello-authored-by-famiano-strada",
    "st-chp5-p137-farnese-campaigns-were-on-behalf-of-spaniards",
    "st-chp5-p137-farnese-campaigns-in-low-countries",
    "st-chp5-p137-farnese-named-as-campaign-leader",
}

EVENT_CARD = '''---
title: "亚历山德罗·法尔内塞的低地国家战役（Alessandro Farnese’s campaigns in the Low Countries）"
name_en: "Alessandro Farnese’s campaigns in the Low Countries"
type: event
evidence_status: source_backed
sources:
  - citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).'
    location: '第5章，印刷页137 L72–73'
    sentence_summary: Haskell称《De Bello Belgico》第二卷颂扬Alessandro Farnese为西班牙一方在Low Countries进行的战役；原文未给战役日期或单场战役。
    original_quotes:
      - source_span: 'Chapter 5, printed p. 137 L72–73'
        text: |-
          the second volume of Famiano Strada’s De Bello Belgico, a celebration of Alessandro Farnese’s campaigns on behalf of the Spaniards in the Low
          Countries;
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/05_CHP-5_sec_iii.md
      source_span: 'Chapter 5, printed p. 137 L72–73'
created: '2026-10-27'
updated: '2026-10-27'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp5-p137-campaigns-low-countries-20261027
---

## 内容

### 描述
**中文：** 本卡记录Haskell在第5章p.137所称Alessandro Farnese在Low Countries为西班牙一方进行的战役组。原文将其作为《De Bello Belgico》第二卷所颂扬的对象，没有给出战役年代、起止范围或具体战役。段首的1647年对应插图合作，不作战役日期。中文标题为描述性译名。

**English:** This card records the campaign group Haskell describes on page 137 of chapter 5 as Alessandro Farnese’s campaigns on behalf of the Spaniards in the Low Countries. The passage names the campaigns as the subject celebrated by volume II of De Bello Belgico but gives no campaign dates, boundaries, or individual operations. The opening date 1647 belongs to the illustration collaboration, not to the campaigns. The Chinese title is descriptive.

### 时间、主体与内容
| 字段 | 内容 | 依据 |
|---|---|---|
| 事件类型 | 军事战役组；以Haskell所称Alessandro Farnese’s campaigns为限，不细分具体战役 | S1；第5章印刷页137 L72–73 |

## 关系与证据

### 身份与外部链接

本卡只登记书中可识别的战役组；未据此补入战役日期、具体行动或外部身份断言。

### 关系记录

正式关系由 relations.csv 生成并显示；待证关系及裁决理由见本批过程记录。
'''

PLACE_CARD = '''---
title: "低地国家（Low Countries）"
name_en: "Low Countries"
type: place
evidence_status: source_backed
sources:
  - citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).'
    location: '第2章，印刷页30 L111'
    sentence_summary: Haskell称Giustiniani于1606年游历Low Countries；此处仅记录其书内地区名。
    original_quotes:
      - source_span: 'Chapter 2, printed p. 30 L111'
        text: |-
          He himself had travelled in the Low Countries during a four-month trip to Northern Europe in 1606
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/02_CHP-2_sec_i.md
      source_span: 'Chapter 2, printed p. 30 L111'
  - citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).'
    location: '第5章，印刷页137 L72–73'
    sentence_summary: Haskell将Farnese战役置于Low Countries；不据此推定更窄边界。
    original_quotes:
      - source_span: 'Chapter 5, printed p. 137 L72–73'
        text: |-
          Alessandro Farnese’s campaigns on behalf of the Spaniards in the Low
          Countries;
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/05_CHP-5_sec_iii.md
      source_span: 'Chapter 5, printed p. 137 L72–73'
  - citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).'
    location: '第8章，印刷页205 L24–25、206 L38'
    sentence_summary: Haskell称Low Countries为Roomer的本土地区及其绘画贸易目的地；不据此确定边界。
    original_quotes:
      - source_span: 'Chapter 8, printed p. 205 L24–25'
        text: |-
          most of his business was carried on with his native
          Low Countries.
      - source_span: 'Chapter 8, printed p. 206 L38'
        text: |-
          sending Neapolitan paintings to the Low Countries (notably those of Ribera’s pupil, Bartolommeo Passante)
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: 02-sources/02-Markdown/08_CHP-8_sec_i.md
      source_span: 'Chapter 8, printed p. 205 L24–25; p. 206 L38'
created: '2026-10-27'
updated: '2026-10-27'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp5-p137-campaigns-low-countries-20261027
---

## 内容

### 描述
**中文：** 本卡记录Haskell在第2、5、8章使用的历史地区名“Low Countries”，本项目将其描述性译作“低地国家”。三章分别以此称谓记录Giustiniani的旅行、Alessandro Farnese战役所在地，以及Roomer的本土地区和贸易目的地。原书没有界定具体范围；本卡不将其等同于某个现代国家或特定政体。

**English:** This card records the historical regional name “Low Countries” as used by Haskell in chapters 2, 5, and 8; “低地国家” is a descriptive Chinese rendering. The three chapters refer to Giustiniani’s travel, the location of Alessandro Farnese’s campaigns, and Roomer’s native region and trade destination. Haskell does not define the boundaries, so this card does not equate the term with a modern country or a specific polity.

### 名称
| 字段 | 值 | 依据 |
|---|---|---|
| 原语地名 | Low Countries | S1；第2章印刷页30 L111；第5章印刷页137 L72–73；第8章印刷页205 L24–25、206 L38 |

### 基本信息
| 字段 | 值 | 依据 |
|---|---|---|
| 地点性质 | 历史地理区域名；原书未界定具体边界 | S1；第2章印刷页30 L111；第5章印刷页137 L72–73；第8章印刷页205 L24–25、206 L38 |

## 关系与证据

### 身份与外部链接

本卡按本书的地区称谓登记；未补入现代边界、坐标或政治实体对应。

### 关系记录

正式关系由 relations.csv 生成并显示；待证关系及裁决理由见本批过程记录。
'''

RELATION_SPECS = [
    ("units/archives/de-bello-belgico", "units/persons/michelangelo-cerquozzi", "contributed_by", "1647", "插图合作画家", "第二卷插图；1647为合作时间，不是出版年。", "st-chp5-p137-miel-borgognone-strada-collaboration"),
    ("units/archives/de-bello-belgico", "units/persons/jan-miel", "contributed_by", "1647", "插图合作画家", "第二卷插图；1647为合作时间，不是出版年。", "st-chp5-p137-miel-contributed-to-de-bello-illustrations"),
    ("units/archives/de-bello-belgico", "units/persons/jacques-courtois", "contributed_by", "1647", "插图合作画家；该段称Giacomo Borgognone", "第二卷插图；1647为合作时间，不是出版年。", "st-chp5-p137-borgognone-contributed-to-de-bello-illustrations"),
    ("units/archives/de-bello-belgico", "units/persons/famiano-strada", "authored_by", "", "作者", "Haskell称De Bello Belgico为Famiano Strada之作；不推出版时间。", "st-chp5-p137-de-bello-authored-by-famiano-strada"),
    (EVENT_ID, PLACE_ID, "occurred_at", "", "战役所在地区", "Haskell没有提供具体战役日期或更窄的地理边界。", "st-chp5-p137-farnese-campaigns-in-low-countries"),
    (EVENT_ID, "units/persons/alessandro-farnese-duke-of-parma", "has_participant", "", "原文以Alessandro Farnese’s campaigns指称该战役组；不补具体指挥头衔。", "来源关联到公爵，但没有列出单场战役或具体职衔。", "st-chp5-p137-farnese-named-as-campaign-leader"),
]

# rel-2449 was created by the first apply, then removed after strict audit showed
# that archive -> event is outside has_subject's allowed range. Keep the gap so
# the remaining batch relations retain their recorded IDs rel-2450 through rel-2455.
RELATION_ID_START = 2450


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def update_csv_rows_preserving_other_lines(path: Path, key: str, updates: dict[str, dict[str, str]]) -> None:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    header = next(csv.reader([lines[0].rstrip("\r\n")]))
    found: set[str] = set()
    for index in range(1, len(lines)):
        line = lines[index]
        ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        values = next(csv.reader([line.rstrip("\r\n")]))
        row = dict(zip(header, values))
        item = row.get(key, "")
        if item not in updates:
            continue
        for field, value in updates[item].items():
            row[field] = value
        buffer = io.StringIO(newline="")
        csv.writer(buffer, lineterminator="").writerow([row.get(column, "") for column in header])
        lines[index] = buffer.getvalue() + ending
        found.add(item)
    if found != set(updates):
        raise ValueError(f"alignment row mismatch: found {sorted(found)}")
    path.write_bytes(("\ufeff" if bom else "").encode("utf-8") + "".join(lines).encode("utf-8"))


def append_csv_rows(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    raw = path.read_bytes()
    ending = "\r\n" if raw.endswith(b"\r\n") else "\n"
    if raw and not raw.endswith((b"\n", b"\r")):
        with path.open("a", encoding="utf-8", newline="") as handle:
            handle.write(ending)
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator=ending)
        writer.writerows(rows)


def build_relation_rows(existing_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for offset, (subject, object_, predicate, time, role, scope, statement_id) in enumerate(RELATION_SPECS, 1):
        rows.append({
            "relation_id": f"rel-{RELATION_ID_START + offset - 1:04d}",
            "subject_ku_id": subject,
            "object_ku_id": object_,
            "predicate": predicate,
            "time": time,
            "role": role,
            "scope": scope,
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": "Chapter 5, printed p. 137 L72–73",
            "source_file": SOURCE_FILE,
            "note": f"S2 statement: {statement_id}; source-limited disposition in {PROCESS_REF}.",
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the chapter 5 p. 137 campaign and Low Countries endpoints.")
    parser.add_argument("--apply", action="store_true", help="apply the preflighted S2/S3/S4/S5/S6 batch")
    args = parser.parse_args()

    mentions_path = TABLES / "mentions.csv"
    alignment_path = TABLES / "alignment.csv"
    manifest_path = TABLES / "ku-manifest.csv"
    relations_path = TABLES / "relations.csv"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    statements_path = TABLES / "book-statements.jsonl"
    candidates_path = TABLES / "entity-candidates.csv"
    source_path = ROOT / SOURCE_FILE
    cards = [(ROOT / EVENT_PATH, EVENT_CARD), (ROOT / PLACE_PATH, PLACE_CARD)]

    segment_text = "\n".join(source_path.read_text(encoding="utf-8").splitlines()[69:80])
    assert segment_text[279:309] == "Alessandro Farnese’s campaigns"
    assert segment_text[172:182] == "and others"
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == "9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a"

    _, candidates = read_csv(candidates_path)
    candidate_rows = {row["candidate_id"]: row for row in candidates}
    _, alignment_rows = read_csv(alignment_path)
    primary = {row["candidate_id"]: row for row in alignment_rows if not row.get("external_source", "")}
    assert primary["cand-11927"]["decision"] == "undecided" and not primary["cand-11927"]["ku_id"]
    assert primary["cand-11928"]["decision"] == "undecided" and not primary["cand-11928"]["ku_id"]
    assert primary["cand-11930"]["decision"] == "undecided" and not primary["cand-11930"]["ku_id"]
    assert primary["cand-4342"]["decision"] == "new" and not primary["cand-4342"]["ku_id"]
    expected_mapped = {
        "cand-2515": "units/archives/de-bello-belgico",
        "cand-3084": "units/persons/michelangelo-cerquozzi",
        "cand-1662": "units/persons/jan-miel",
        "cand-0399": "units/persons/jacques-courtois",
        "cand-2514": "units/persons/famiano-strada",
        "cand-12426": "units/persons/alessandro-farnese-duke-of-parma",
    }
    for candidate_id, ku_id in expected_mapped.items():
        assert primary[candidate_id]["ku_id"] == ku_id
    assert candidate_rows["cand-11927"]["suggested_type"] == "event"
    assert candidate_rows["cand-4342"]["suggested_type"] == "place"
    assert not (ROOT / EVENT_PATH).exists() and not (ROOT / PLACE_PATH).exists()

    with statements_path.open(encoding="utf-8") as handle:
        statements = {item["statement_id"]: item for item in map(json.loads, handle)}
    assert STATEMENT_IDS.issubset(statements)
    assert all(statements[item]["qualifiers"].get("relation_candidate") is True for item in STATEMENT_IDS)

    _, mentions = read_csv(mentions_path)
    assert not any(row["candidate_id"] in {"cand-11927", "cand-11930"} and row["segment_id"] == "chp-5:05_CHP-5_sec_iii:l70-80" for row in mentions)
    new_mentions = [
        {"mention_id": "m-chp5-sec-iii-l70-80-048", "segment_id": "chp-5:05_CHP-5_sec_iii:l70-80", "candidate_id": "cand-11927", "surface_form": "Alessandro Farnese’s campaigns", "start_char": "279", "end_char": "309", "note": "Direct S2 anchor for the campaign group named in the De Bello Belgico and location statements; no campaign date or individual battle is implied."},
        {"mention_id": "m-chp5-sec-iii-l70-80-049", "segment_id": "chp-5:05_CHP-5_sec_iii:l70-80", "candidate_id": "cand-11930", "surface_form": "and others", "start_char": "172", "end_char": "182", "note": "Direct S2 span for the additional unnamed collaborators; the referent remains an open-ended, untyped group."},
    ]
    mention_headers, _ = read_csv(mentions_path)
    assert all(row["mention_id"] not in {item["mention_id"] for item in mentions} for row in new_mentions)

    _, manifest = read_csv(manifest_path)
    manifest_ids = {row["ku_id"] for row in manifest}
    assert EVENT_ID not in manifest_ids and PLACE_ID not in manifest_ids
    manifest_rows = [
        {"ku_id": EVENT_ID, "type": "event", "canonical_name": "亚历山德罗·法尔内塞的低地国家战役", "name_en": "Alessandro Farnese’s campaigns in the Low Countries", "source_task": "patrons-and-painters-full-book-s2", "card_path": EVENT_PATH},
        {"ku_id": PLACE_ID, "type": "place", "canonical_name": "低地国家", "name_en": "Low Countries", "source_task": "patrons-and-painters-full-book-s2", "card_path": PLACE_PATH},
    ]
    manifest_headers, _ = read_csv(manifest_path)

    with accepted_path.open(encoding="utf-8-sig") as handle:
        accepted_text = handle.read()
    assert EVENT_PATH not in accepted_text and PLACE_PATH not in accepted_text

    _, sources = read_csv(TABLES / "sources.csv")
    assert any(row["source_id"] == SOURCE_ID for row in sources)
    relation_headers, relation_rows = read_csv(relations_path)
    new_relations = build_relation_rows(relation_rows)
    old_keys = {(r["subject_ku_id"], r["object_ku_id"], r["predicate"], r.get("time", ""), r.get("role", ""), r.get("scope", "")) for r in relation_rows}
    new_keys = [(r["subject_ku_id"], r["object_ku_id"], r["predicate"], r["time"], r["role"], r["scope"]) for r in new_relations]
    assert all(key not in old_keys for key in new_keys) and len(set(new_keys)) == len(new_keys)

    alignment_updates = {
        "cand-11927": {
            "decision": "new", "ku_id": EVENT_ID, "process_ref": PROCESS_REF,
            "resolution_note": "group=sg3-event-cand-11927; source_ref=chp-5:05_CHP-5_sec_iii:l70-80#L72; S2 mention m-chp5-sec-iii-l70-80-048 directly anchors Alessandro Farnese’s campaigns. Register this source-defined campaign group; distinct from the person KU and De Bello Belgico archive; Haskell supplies no campaign dates or individual battles.",
        },
        "cand-4342": {
            "ku_id": PLACE_ID, "process_ref": PROCESS_REF,
            "resolution_note": primary["cand-4342"]["resolution_note"] + " S4 registered as a place KU using the repeated source name across chapters 2, 5, and 8; boundaries remain unspecified.",
        },
    }

    print("Preflight passed. Planned changes:")
    print("  S2 mentions: +2 direct spans; no statement or independent-review count change")
    print("  S3: cand-11927 undecided -> new; cand-11928 and cand-11930 remain undecided")
    print("  S4: register event and place KUs; existing person/archive endpoints reused")
    print("  S5: 3 source-backed fields from Haskell; no external facts")
    print("  S6: 6 formal rows, 3 pending decisions retained in process record")
    print("  relation IDs:", new_relations[0]["relation_id"], "through", new_relations[-1]["relation_id"])
    if not args.apply:
        print("Dry run only; rerun with --apply to write.")
        return 0

    update_csv_rows_preserving_other_lines(alignment_path, "candidate_id", alignment_updates)
    append_csv_rows(mentions_path, new_mentions, mention_headers)
    append_csv_rows(manifest_path, manifest_rows, manifest_headers)
    raw_accepted = accepted_path.read_bytes()
    accepted_line_ending = "\r\n" if b"\r\n" in raw_accepted else "\n"
    accepted_lines = raw_accepted.decode("utf-8-sig").splitlines(keepends=True)
    claims_index = next((i for i, line in enumerate(accepted_lines) if line.strip() == "claims:"), None)
    if claims_index is None:
        raise ValueError("accepted.yml has no claims section; refusing to insert unit paths")
    accepted_lines[claims_index:claims_index] = [
        f"- {EVENT_PATH}{accepted_line_ending}",
        f"- {PLACE_PATH}{accepted_line_ending}",
    ]
    accepted_path.write_bytes(("\ufeff" if raw_accepted.startswith(b"\xef\xbb\xbf") else "").encode("utf-8") + "".join(accepted_lines).encode("utf-8"))
    for path, card_content in cards:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(card_content, encoding="utf-8", newline="\n")
    append_csv_rows(relations_path, new_relations, relation_headers)
    print("Applied; review the worktree diff and run the targeted field/card projections and audits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
