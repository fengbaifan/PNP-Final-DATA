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
MANIFEST = TABLES / "ku-manifest.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
PROCESS_REF = "S3-full-book-2026-10-16"
GROUP = "archive-group-marino-adone-epic"


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
    expected = Counter({"same": 1768, "new": 5010, "undecided": 5519, "excluded": 99, "conflict": 8})
    if len(primary) != 12404 or len(alignment) != 12619 or len(external) != 215 or Counter(row["decision"] for row in primary) != expected:
        raise SystemExit("Unexpected S3 baseline; inspect before changing the candidate.")

    candidate = candidates.get("cand-1549")
    decision = primary_by_id.get("cand-1549")
    if not candidate or (candidate["suggested_type"], candidate["index_entry_id"], candidate["sub_entry"], candidate["index_page_range"]) != ("archive", "M.csv#88", "Adone", "115"):
        raise SystemExit("cand-1549 index identity changed.")
    if not decision or decision["decision"] != "undecided" or decision["ku_id"]:
        raise SystemExit("cand-1549 is no longer the expected undecided candidate.")
    if any(row["type"] == "archive" and "adone" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for row in read_csv(MANIFEST)[1]):
        raise SystemExit("A matching Adone archive KU now exists; compare it before deciding new.")
    if any(f"group={GROUP}" in row["resolution_note"] for row in primary):
        raise SystemExit("The proposed Adone group ID is already in use.")

    with MENTIONS.open("r", encoding="utf-8-sig", newline="") as stream:
        mentions = {row["mention_id"]: row for row in csv.DictReader(stream)}
    mention_id = "m-chp4-sec-ii-p115-0032"
    if mentions.get(mention_id, {}).get("candidate_id") != "cand-1549":
        raise SystemExit("The p.115 Adone mention no longer maps to cand-1549.")
    with STATEMENTS.open("r", encoding="utf-8-sig") as stream:
        statements = [json.loads(line) for line in stream if line.strip()]
    by_statement = {row["statement_id"]: row for row in statements}
    expected_statements = {"st-chp4-sec-ii-p115-drawings-adone", "st-chp4-sec-ii-p115-adone-created-by-marino"}
    if not expected_statements.issubset(by_statement):
        raise SystemExit("The p.115 Adone identity statements changed.")
    if any("cand-1549" not in by_statement[sid].get("qualifiers", {}).get("mentioned_candidate_ids", []) for sid in expected_statements):
        raise SystemExit("The p.115 statements no longer identify cand-1549.")

    prior_note = decision["resolution_note"]
    updated = [dict(row) for row in alignment]
    by_id = {row["candidate_id"]: row for row in updated if not row["external_source"]}
    by_id["cand-1549"].update(
        decision="new",
        process_ref=PROCESS_REF,
        resolution_note=(
            f"source_ref=index_entry=M.csv#88;page=115; mention={mention_id}; statements=st-chp4-sec-ii-p115-drawings-adone,st-chp4-sec-ii-p115-adone-created-by-marino; group={GROUP}. "
            "Haskell names the literary work Adone and explicitly attributes it to Giambattista Marino; the index subentry points to the same p.115 discussion. No matching archive KU exists, so this is one new archive literary-work identity pending S4. "
            "Keep distinct from the existing Marino person KU, the Poussin drawings inspired by episodes from Adone, and the separate index candidate cand-1551 for unspecified poems on works by leading artists. No edition or copy is asserted. "
            f"prior_resolution_note={prior_note}"
        ),
    )

    result_text = RESULT.read_text(encoding="utf-8-sig")
    replacements = [
        ("new=5,010（4,832个身份组）", "new=5,011（4,833个身份组）"),
        ("undecided=5,519。S4 已登记281组、映射352条成员候选；尚待登记4,551组、4,658条映射。", "undecided=5,518。S4 已登记281组、映射352条成员候选；尚待登记4,552组、4,659条映射。"),
        ("| new | 5,010 | 按 4,832 个当前身份组进入 S4；每组登记一个 KU |", "| new | 5,011 | 按 4,833 个当前身份组进入 S4；每组登记一个 KU |"),
        ("| undecided | 5,519 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |", "| undecided | 5,518 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |"),
        ("| archive | 79→61 | 1,251／1,216 | 29／1,187；1,216 | 0 | 18 | 752 |", "| archive | 79→61 | 1,252／1,217 | 29／1,188；1,217 | 0 | 18 | 751 |"),
        ("| **合计** | **1,768→1,026** | **5,010／4,832** | **281／4,551；4,658** | **8** | **99** | **5,519** |", "| **合计** | **1,768→1,026** | **5,011／4,833** | **281／4,552；4,659** | **8** | **99** | **5,518** |"),
    ]
    for old, new in replacements:
        if result_text.count(old) != 1:
            raise SystemExit(f"Expected one result occurrence of {old!r}, found {result_text.count(old)}")
        result_text = result_text.replace(old, new, 1)
    section = (
        "### S3 archive：Marino《Adone》文学作品身份裁决（2026-10-16）\n\n"
        f"- `cand-1549`（M.csv#88，p.115）由 `undecided` 改为 `new`，进入 `{GROUP}`，待 S4 登记。第4章 p.115 直接称 Marino 委托 Poussin 绘制受《Adone》启发的题材，并将《Adone》归于 Marino；索引子项定位至同页。现有 archive KU 中无同名对象。\n"
        "- 边界：该组表示文学作品本身，不含 Giambattista Marino 人物 KU，也不含据诗篇主题绘制的 Poussin 图画候选；Marino 的未具名诗作群候选 `cand-1551` 保持独立未决。原书未给出本次所引具体版次或馆藏本，本轮不据此声称某一印本。"
    )
    marker = "### S4 按类型登记进度"
    if result_text.count(marker) != 1:
        raise SystemExit("Could not find the S4 type-progress insertion point.")
    result_text = result_text.replace(marker, section + "\n\n" + marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge_text += (
        "\n\n### S3 archive：Marino《Adone》文学作品身份裁决（2026-10-16）\n\n"
        f"- `cand-1549`（M.csv#88，p.115）从 `undecided` 改为 `new`，身份组 `{GROUP}`，待 S4 登记。S2 mentions `{mention_id}` 与 statements `st-chp4-sec-ii-p115-drawings-adone`、`st-chp4-sec-ii-p115-adone-created-by-marino` 共同指向 Marino 的具名文学作品《Adone》。未找到既有 archive KU。\n"
        "- 类型按 literary work 登记为 archive。作品身份与 person `units/persons/giambattista-marino`、由该诗启发的 Poussin drawing candidates 及未具名诗作组 `cand-1551` 分开。原书没有指出本次引用的具体版次或单件；因此只登记作品身份候选，不主张印本、版本或藏本身份。"
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
    print(f"  identity group: cand-1549 -> {GROUP}; one new archive group and one pending member mapping")
    if not args.apply:
        print("Dry-run only; pass --apply to write the changes.")
        return

    for path in updates:
        backup = path.with_name(path.name + ".bak-s3-marino-adone-20261016")
        if backup.exists():
            raise SystemExit(f"Recovery copy already exists: {backup}")
        shutil.copy2(path, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3-marino-adone-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied the archive identity decision and retained recovery copies.")


if __name__ == "__main__":
    main()
