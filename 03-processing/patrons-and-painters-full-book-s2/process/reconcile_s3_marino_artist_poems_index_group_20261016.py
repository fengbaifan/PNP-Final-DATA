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
MANIFEST = TABLES / "ku-manifest.csv"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
PROCESS_REF = "S3-full-book-2026-10-16"
GROUP = "archive-group-c659964650de"


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
    expected = Counter({"same": 1768, "new": 5011, "undecided": 5518, "excluded": 99, "conflict": 8})
    if len(primary) != 12404 or len(alignment) != 12619 or len(external) != 215 or Counter(row["decision"] for row in primary) != expected:
        raise SystemExit("Unexpected S3 baseline; inspect before changing the candidate.")

    index_candidate = candidates.get("cand-1551")
    body_candidate = candidates.get("cand-4464")
    index_decision = primary_by_id.get("cand-1551")
    body_decision = primary_by_id.get("cand-4464")
    if not index_candidate or (index_candidate["suggested_type"], index_candidate["index_entry_id"], index_candidate["sub_entry"], index_candidate["index_page_range"]) != ("archive", "M.csv#90", "poems on works by leading artists", "38"):
        raise SystemExit("cand-1551 index identity changed.")
    if not index_decision or index_decision["decision"] != "undecided" or index_decision["ku_id"]:
        raise SystemExit("cand-1551 is no longer the expected undecided candidate.")
    if not body_candidate or not body_decision or body_decision["decision"] != "new" or f"group={GROUP}" not in body_decision["resolution_note"] or body_decision["ku_id"]:
        raise SystemExit("cand-4464 is no longer in the expected pending new group.")
    if any(row["type"] == "archive" and "poems on works by leading artists" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for row in read_csv(MANIFEST)[1]):
        raise SystemExit("A matching archive KU now exists; compare it before extending the group.")

    with MENTIONS.open("r", encoding="utf-8-sig", newline="") as stream:
        mentions = {row["mention_id"]: row for row in csv.DictReader(stream)}
    mention_id = "m-chp2-secii-l71-78-0065"
    if mentions.get(mention_id, {}).get("candidate_id") != "cand-4464":
        raise SystemExit("The ch.2 p.38 plural-poem mention no longer maps to cand-4464.")
    with STATEMENTS.open("r", encoding="utf-8-sig") as stream:
        statements = [json.loads(line) for line in stream if line.strip()]
    statement_id = "st-chp2-secii-l71-78-marino-poems-and-pagan-qualities"
    by_statement = {row["statement_id"]: row for row in statements}
    if statement_id not in by_statement or "cand-4464" not in by_statement[statement_id].get("qualifiers", {}).get("mentioned_candidate_ids", []):
        raise SystemExit("The direct source statement for cand-4464 changed.")
    if by_statement[statement_id].get("qualifiers", {}).get("print_page") not in ("38", 38):
        raise SystemExit("The body statement no longer anchors to printed page 38.")

    prior_note = index_decision["resolution_note"]
    updated = [dict(row) for row in alignment]
    by_id = {row["candidate_id"]: row for row in updated if not row["external_source"]}
    by_id["cand-1551"].update(
        decision="new",
        process_ref=PROCESS_REF,
        resolution_note=(
            "source_ref=index_entry=M.csv#90;page=38; body_candidate=cand-4464; mention=m-chp2-secii-l71-78-0065; "
            f"statement={statement_id}; identity_peer=cand-4464; group={GROUP}. The index subentry 'poems on works by leading artists' and the ch.2 p.38 passage's exact description of Marino's series of very popular poems on works by leading artists identify the same plural literary-work group. "
            "The body candidate already has a pending new archive group; attach this index slice to that one group. The individual poems are not named here, and no individual title, edition, or copy is asserted. "
            "Keep distinct from the separate untitled song dedicated to Marcello Sacchetti (cand-4463) and Marino's individually titled Adone (cand-1549). "
            f"prior_resolution_note={prior_note}"
        ),
    )

    result_text = RESULT.read_text(encoding="utf-8-sig")
    replacements = [
        ("new=5,011（4,833个身份组）", "new=5,012（4,833个身份组）"),
        ("undecided=5,518。S4 已登记281组、映射352条成员候选；尚待登记4,552组、4,659条映射。", "undecided=5,517。S4 已登记281组、映射352条成员候选；尚待登记4,552组、4,660条映射。"),
        ("| new | 5,011 | 按 4,833 个当前身份组进入 S4；每组登记一个 KU |", "| new | 5,012 | 按 4,833 个当前身份组进入 S4；每组登记一个 KU |"),
        ("| undecided | 5,518 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |", "| undecided | 5,517 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |"),
        ("| archive | 79→61 | 1,252／1,217 | 29／1,188；1,217 | 0 | 18 | 751 |", "| archive | 79→61 | 1,253／1,217 | 29／1,188；1,218 | 0 | 18 | 750 |"),
        ("| **合计** | **1,768→1,026** | **5,011／4,833** | **281／4,552；4,659** | **8** | **99** | **5,518** |", "| **合计** | **1,768→1,026** | **5,012／4,833** | **281／4,552；4,660** | **8** | **99** | **5,517** |"),
    ]
    for old, new in replacements:
        if result_text.count(old) != 1:
            raise SystemExit(f"Expected one result occurrence of {old!r}, found {result_text.count(old)}")
        result_text = result_text.replace(old, new, 1)
    section = (
        "### S3 archive：Marino 未具名名画题咏诗组索引候选并组（2026-10-16）\n\n"
        f"- `cand-1551`（M.csv#90，p.38）由 `undecided` 改为 `new`，与正文候选 `cand-4464` 同入 `{GROUP}`，待 S4 登记一个 archive KU。索引子项与第2章 p.38 对 Marino 所作“一系列描写名家作品的流行诗”的正文措辞对应，指向同一未具名诗作群。\n"
        "- 本组表示多个未具名文学作品的聚合身份；不拆造诗名或版次。与献给 Marcello Sacchetti 的单首未具名歌诗 `cand-4463`、以及单独具名的《Adone》`cand-1549` 区分。"
    )
    marker = "### S4 按类型登记进度"
    if result_text.count(marker) != 1:
        raise SystemExit("Could not find the S4 type-progress insertion point.")
    result_text = result_text.replace(marker, section + "\n\n" + marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge_text += (
        "\n\n### S3 archive：Marino 未具名名画题咏诗组索引候选并组（2026-10-16）\n\n"
        f"- `cand-1551`（M.csv#90，p.38）从 `undecided` 改为 `new`，并入 `cand-4464` 的 `{GROUP}`。第2章 p.38 S2 mention `m-chp2-secii-l71-78-0065` 与 statement `{statement_id}` 记录 Marino 写有“一系列非常流行的、题咏知名艺术家作品的诗”，题材描述、作者和页码均与索引子项一致，属于同一诗作群候选。\n"
        "- 维持聚合粒度：没有单首诗的名字、出版物或版次，故不再拆分或推定具体作品。与同段另外的单首未具名 song `cand-4463`（献给 Marcello Sacchetti）及《Adone》`cand-1549` 分开。该组仍待 S4，不因作者相同合并其他作品。"
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
    print(f"  identity group: cand-1551 + cand-4464 -> {GROUP}; group count unchanged, pending member mappings +1")
    if not args.apply:
        print("Dry-run only; pass --apply to write the changes.")
        return

    for path in updates:
        backup = path.with_name(path.name + ".bak-s3-marino-artist-poems-20261016")
        if backup.exists():
            raise SystemExit(f"Recovery copy already exists: {backup}")
        shutil.copy2(path, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3-marino-artist-poems-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied the archive identity grouping and retained recovery copies.")


if __name__ == "__main__":
    main()
