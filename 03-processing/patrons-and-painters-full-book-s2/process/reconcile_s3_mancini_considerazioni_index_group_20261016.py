from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from collections import Counter
from pathlib import Path


ROOT = Path.cwd()
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
PROCESS_REF = "S3-full-book-2026-10-16"
GROUP = "archive-group-fb110b11a649"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), had_bom


def encode_csv(headers: list[str], rows: list[dict[str, str]], had_bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=headers, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    text = stream.getvalue()
    return ("\ufeff" + text if had_bom else text).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not (ROOT / "04-knowledge" / "accepted.yml").exists():
        raise SystemExit("Run this script from the project root.")

    alignment_headers, alignment, alignment_bom = read_csv(ALIGNMENT)
    _, candidate_rows, _ = read_csv(CANDIDATES)
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    primary = [row for row in alignment if not row["external_source"]]
    external = [row for row in alignment if row["external_source"]]
    primary_by_id = {row["candidate_id"]: row for row in primary}
    expected = Counter({"same": 1768, "new": 5008, "undecided": 5521, "excluded": 99, "conflict": 8})
    if len(primary) != 12404 or len(alignment) != 12619 or len(external) != 215 or Counter(row["decision"] for row in primary) != expected:
        raise SystemExit("Unexpected S3 baseline; inspect before changing the candidate.")

    index_candidate = candidates.get("cand-1508")
    body_candidate = candidates.get("cand-6089")
    index_decision = primary_by_id.get("cand-1508")
    body_decision = primary_by_id.get("cand-6089")
    if not index_candidate or (index_candidate["suggested_type"], index_candidate["index_entry_id"], index_candidate["sub_entry"]) != ("archive", "M.csv#45", "Considerazioni sulla Pittura"):
        raise SystemExit("cand-1508 index identity changed.")
    if not index_decision or index_decision["decision"] != "undecided" or index_decision["ku_id"]:
        raise SystemExit("cand-1508 is no longer the expected undecided candidate.")
    if not body_candidate or body_candidate["suggested_type"] != "archive" or not body_decision or body_decision["decision"] != "new" or f"group={GROUP}" not in body_decision["resolution_note"]:
        raise SystemExit("cand-6089 is no longer in the expected pending archive group.")

    with MENTIONS.open("r", encoding="utf-8-sig", newline="") as stream:
        mentions = {row["mention_id"]: row for row in csv.DictReader(stream)}
    expected_mentions = {"m-chp5-p120-note-0011": "cand-1508", "m-chp5-p124-0001": "cand-1508", "m-chp21-bib-l701-754-027": "cand-6089"}
    if any(mentions.get(mid, {}).get("candidate_id") != cid for mid, cid in expected_mentions.items()):
        raise SystemExit("A p.120/p.124/bibliography mention mapping changed.")
    with STATEMENTS.open("r", encoding="utf-8-sig") as stream:
        statements = [json.loads(line) for line in stream if line.strip()]
    by_statement = {row["statement_id"]: row for row in statements}
    expected_statements = {
        "st-chp5-p120-note3-mancini-locator",
        "st-chp21-bib-l701-754-entry-27",
        "st-chp5-note-p123-n4-critical-edition",
    }
    if not expected_statements.issubset(by_statement):
        raise SystemExit("The direct-edition and bibliography statements changed.")
    locator = by_statement["st-chp5-p120-note3-mancini-locator"]
    if locator.get("qualifiers", {}).get("citation_locator") != "volume I, p. 249" or "1956" not in locator.get("qualifiers", {}).get("qualification", ""):
        raise SystemExit("The note citation no longer points to the bibliography-identified 1956 edition.")
    bib = by_statement["st-chp21-bib-l701-754-entry-27"].get("qualifiers", {}).get("bibliographic_record", {})
    if (bib.get("title_as_printed"), bib.get("record_kind"), bib.get("printed_page")) != ("Considerazioni sulla Pittura", "critical edition", 428) or "Roma 1956" not in bib.get("publication_details_as_printed", ""):
        raise SystemExit("The bibliography no longer identifies the 1956 critical edition.")

    prior_note = index_decision["resolution_note"]
    updated = [dict(row) for row in alignment]
    by_id = {row["candidate_id"]: row for row in updated if not row["external_source"]}
    by_id["cand-1508"].update(
        decision="new",
        process_ref=PROCESS_REF,
        resolution_note=(
            "source_ref=index_entry=M.csv#45;pages=124,130; mentions=m-chp5-p120-note-0011,m-chp5-p124-0001; "
            "statements=st-chp5-p120-note3-mancini-locator,st-chp5-p124-mancini-treatise-knowledge,st-chp21-bib-l701-754-entry-27,st-chp5-note-p123-n4-critical-edition; "
            f"identity_peer=cand-6089; group={GROUP}. The p.120 note cites Mancini, vol.I, p.249; Haskell's bibliography identifies the referenced critical edition as Considerazioni sulla Pittura, published by Adriana Marucchi with Luigi Salerno's commentary, two volumes, Rome 1956. "
            "The title, volume locator, and edition record support one bibliographic identity group; index candidate and body/bibliography candidate remain new members of this unregistered group pending S4. The generic p.124 word 'Treatise' is not treated as a separate titled work. "
            f"prior_resolution_note={prior_note}"
        ),
    )

    result_text = RESULT.read_text(encoding="utf-8-sig")
    replacements = [
        ("new=5,008（4,832个身份组）", "new=5,009（4,832个身份组）"),
        ("undecided=5,521。S4 已登记281组、映射352条成员候选；尚待登记4,551组、4,656条映射。", "undecided=5,520。S4 已登记281组、映射352条成员候选；尚待登记4,551组、4,657条映射。"),
        ("| new | 5,008 | 按 4,832 个当前身份组进入 S4；每组登记一个 KU |", "| new | 5,009 | 按 4,832 个当前身份组进入 S4；每组登记一个 KU |"),
        ("| undecided | 5,521 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |", "| undecided | 5,520 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |"),
        ("| archive | 79→61 | 1,249／1,216 | 29／1,187；1,214 | 0 | 18 | 754 |", "| archive | 79→61 | 1,250／1,216 | 29／1,187；1,215 | 0 | 18 | 753 |"),
        ("| **合计** | **1,768→1,026** | **5,008／4,832** | **281／4,551；4,656** | **8** | **99** | **5,521** |", "| **合计** | **1,768→1,026** | **5,009／4,832** | **281／4,551；4,657** | **8** | **99** | **5,520** |"),
    ]
    for old, new in replacements:
        if result_text.count(old) != 1:
            raise SystemExit(f"Expected one result occurrence of {old!r}, found {result_text.count(old)}")
        result_text = result_text.replace(old, new, 1)
    section = (
        "### S3 archive：Mancini《Considerazioni sulla Pittura》索引候选并组（2026-10-16）\n\n"
        f"- `cand-1508`（M.csv#45，pp.124、130）由 `undecided` 改为 `new`，与正文/书目候选 `cand-6089` 同入 `{GROUP}`，待 S4 登记一个 archive KU。第5章 p.120 注3引用 Mancini 卷I、p.249；第21章书目将该书具体著录为 Adriana Marucchi 编、Luigi Salerno 注释、罗马1956年两卷本。标题与卷页引文对应，版次缺口解除。\n"
        "- 边界：p.124 正文中的泛称“Treatise”不是另一个具名文献；本轮不把 Mancini 人物、原作抽象身份或笼统著述清单并入版次身份，也未登记 KU 或关系。"
    )
    marker = "### S4 按类型登记进度"
    if result_text.count(marker) != 1:
        raise SystemExit("Could not find the S4 type-progress insertion point.")
    result_text = result_text.replace(marker, section + "\n\n" + marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge_text += (
        "\n\n### S3 archive：Mancini《Considerazioni sulla Pittura》索引候选并组（2026-10-16）\n\n"
        f"- `cand-1508`（M.csv#45，pp.124、130）从 `undecided` 改为 `new`，与 `cand-6089` 同属 `{GROUP}`，作为一个待 S4 登记的 archive 身份组。第5章 p.120 注3 statement `st-chp5-p120-note3-mancini-locator` 引用 *Considerazioni sulla Pittura*, vol.I, p.249；同书第21章书目 statement `st-chp21-bib-l701-754-entry-27` 给出题名、Adriana Marucchi 首次刊行、Luigi Salerno 注释、两卷、Roma 1956；第5章 p.123 注4 亦称1956年批判版。版本、题名和卷页相互吻合，足以将索引候选并入正文/书目候选的 pending new 组。\n"
        "- 第5章 p.124 泛称的“a learned and most valuable artistic Treatise”未具名，不单独建组或仅凭上下文判定它属于哪一具体版次。人物 `Giulio Mancini` 保持既有人物 KU；本轮无外部身份行、KU、卡片或正式关系写入。citation statement 仍留待 S6 审查关系类型与方向。"
    )

    updates = {
        ALIGNMENT: encode_csv(alignment_headers, updated, alignment_bom),
        RESULT: ("\ufeff" + result_text).encode("utf-8"),
        KNOWLEDGE: ("\ufeff" + knowledge_text).encode("utf-8"),
    }
    print("PREVIEW" if not args.apply else "APPLY")
    for path, content in updates.items():
        print(f"  {path.relative_to(ROOT)}: {sha256(path.read_bytes())} -> {sha256(content)}")
    print("  S3 decisions:", dict(Counter(row["decision"] for row in primary)), "->", dict(Counter(row["decision"] for row in updated if not row["external_source"])))
    print(f"  identity group: cand-1508 + cand-6089 -> {GROUP}; group count unchanged, pending member mappings +1")
    if not args.apply:
        print("Dry-run only; pass --apply to write the changes.")
        return

    for path in updates:
        backup = path.with_name(path.name + ".bak-s3-mancini-considerazioni-20261016")
        if backup.exists():
            raise SystemExit(f"Recovery copy already exists: {backup}")
        shutil.copy2(path, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3-mancini-considerazioni-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied the archive identity grouping and retained recovery copies.")


if __name__ == "__main__":
    main()
