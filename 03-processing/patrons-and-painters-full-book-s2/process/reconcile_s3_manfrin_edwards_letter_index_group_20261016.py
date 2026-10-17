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
GROUP = "archive-group-4ec5e3284567"


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
    expected = Counter({"same": 1768, "new": 5009, "undecided": 5520, "excluded": 99, "conflict": 8})
    if len(primary) != 12404 or len(alignment) != 12619 or len(external) != 215 or Counter(row["decision"] for row in primary) != expected:
        raise SystemExit("Unexpected S3 baseline; inspect before changing the candidate.")

    index_candidate = candidates.get("cand-1515")
    letter_candidate = candidates.get("cand-10849")
    collection_candidate = candidates.get("cand-10605")
    index_decision = primary_by_id.get("cand-1515")
    letter_decision = primary_by_id.get("cand-10849")
    collection_decision = primary_by_id.get("cand-10605")
    if not index_candidate or (index_candidate["suggested_type"], index_candidate["index_entry_id"], index_candidate["sub_entry"], index_candidate["index_page_range"]) != ("archive", "M.csv#52", "letter to Pietro Edwards concerning formation of picture gallery", "395"):
        raise SystemExit("cand-1515 index identity changed.")
    if not index_decision or index_decision["decision"] != "undecided" or index_decision["ku_id"]:
        raise SystemExit("cand-1515 is no longer the expected undecided candidate.")
    if not letter_candidate or not letter_decision or letter_decision["decision"] != "new" or f"group={GROUP}" not in letter_decision["resolution_note"]:
        raise SystemExit("cand-10849 is no longer in the expected pending letter group.")
    if not collection_candidate or not collection_decision or collection_decision["decision"] != "new" or collection_decision["ku_id"]:
        raise SystemExit("The distinct Epistolario Moschini archive candidate changed.")

    with MENTIONS.open("r", encoding="utf-8-sig", newline="") as stream:
        mentions = {row["mention_id"]: row for row in csv.DictReader(stream)}
    expected_mentions = {"m-chp17-p380-manfrin-0023": "cand-1515", "m-chp19-p395-024": "cand-10849", "m-chp19-p395-028": "cand-10605"}
    if any(mentions.get(mid, {}).get("candidate_id") != cid for mid, cid in expected_mentions.items()):
        raise SystemExit("The p.380/p.395 letter and collection mention mappings changed.")
    with STATEMENTS.open("r", encoding="utf-8-sig") as stream:
        statements = [json.loads(line) for line in stream if line.strip()]
    by_statement = {row["statement_id"]: row for row in statements}
    expected_statements = {
        "st-chp17-p380-note6-edwards-letter-source",
        "st-chp19-p395-manfrin-edwards-letter-source",
        "st-chp19-p395-manfrin-selection-criteria-and-experts",
        "st-chp19-p395-manfrin-letter-closure-and-signature",
    }
    if not expected_statements.issubset(by_statement):
        raise SystemExit("The letter-source/transcription statements changed.")
    source = by_statement["st-chp19-p395-manfrin-edwards-letter-source"].get("qualifiers", {})
    if source.get("date") != "1793-12-03" or "Epistolario Moschini" not in source.get("claim", ""):
        raise SystemExit("Appendix 7 no longer identifies the date and manuscript collection.")
    if "published in full in Appendix 7" not in by_statement["st-chp17-p380-note6-edwards-letter-source"].get("qualifiers", {}).get("claim", ""):
        raise SystemExit("The p.380 note no longer cross-references the full letter.")

    prior_note = index_decision["resolution_note"]
    updated = [dict(row) for row in alignment]
    by_id = {row["candidate_id"]: row for row in updated if not row["external_source"]}
    by_id["cand-1515"].update(
        decision="new",
        process_ref=PROCESS_REF,
        resolution_note=(
            "source_ref=index_entry=M.csv#52;page=395; body_candidate=cand-10849; "
            "mentions=m-chp17-p380-manfrin-0023,m-chp19-p395-024; "
            "statements=st-chp17-p380-note6-edwards-letter-source,st-chp19-p395-manfrin-edwards-letter-source,st-chp19-p395-manfrin-selection-criteria-and-experts,st-chp19-p395-manfrin-letter-closure-and-signature; "
            f"identity_peer=cand-10849; group={GROUP}. Appendix 7 prints the letter in full and identifies Girolamo Manfrin to Pietro Edwards, dated 3 December 1793, concerning formation of Manfrin's picture gallery; the heading locates it in Biblioteca Correr, Epistolario Moschini, and ch.17 p.380 n.6 cross-references the same document. "
            "The index candidate and body candidate identify one letter and enter the same pending new archive group. Distinct from cand-10605, the Epistolario Moschini manuscript collection as an archival series; the letter is a document within that collection. The transcription, not the original manuscript, is the evidence consulted. "
            f"prior_resolution_note={prior_note}"
        ),
    )

    result_text = RESULT.read_text(encoding="utf-8-sig")
    replacements = [
        ("new=5,009（4,832个身份组）", "new=5,010（4,832个身份组）"),
        ("undecided=5,520。S4 已登记281组、映射352条成员候选；尚待登记4,551组、4,657条映射。", "undecided=5,519。S4 已登记281组、映射352条成员候选；尚待登记4,551组、4,658条映射。"),
        ("| new | 5,009 | 按 4,832 个当前身份组进入 S4；每组登记一个 KU |", "| new | 5,010 | 按 4,832 个当前身份组进入 S4；每组登记一个 KU |"),
        ("| undecided | 5,520 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |", "| undecided | 5,519 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |"),
        ("| archive | 79→61 | 1,250／1,216 | 29／1,187；1,215 | 0 | 18 | 753 |", "| archive | 79→61 | 1,251／1,216 | 29／1,187；1,216 | 0 | 18 | 752 |"),
        ("| **合计** | **1,768→1,026** | **5,009／4,832** | **281／4,551；4,657** | **8** | **99** | **5,520** |", "| **合计** | **1,768→1,026** | **5,010／4,832** | **281／4,551；4,658** | **8** | **99** | **5,519** |"),
    ]
    for old, new in replacements:
        if result_text.count(old) != 1:
            raise SystemExit(f"Expected one result occurrence of {old!r}, found {result_text.count(old)}")
        result_text = result_text.replace(old, new, 1)
    section = (
        "### S3 archive：Manfrin 致 Edwards 的 1793 年书信索引候选并组（2026-10-16）\n\n"
        f"- `cand-1515`（M.csv#52，p.395）由 `undecided` 改为 `new`，与正文候选 `cand-10849` 同入 `{GROUP}`，待 S4 登记一个 archive KU。附录7完整刊出 Girolamo Manfrin 致 Pietro Edwards、1793年12月3日书信，说明其关于组建 Manfrin 画廊的主题并定位至 Biblioteca Correr 的 Epistolario Moschini；第17章 p.380 注6交叉指向同一信件。\n"
        "- 文献边界：单封书信与其所在的 `Epistolario Moschini` 手稿系列候选 `cand-10605` 分开；索引候选、正文候选归同一 letter 组。当前依据为 Haskell 的完整刊布文本和档案定位，未独立查阅原件；本轮不登记 KU 或正式关系。"
    )
    marker = "### S4 按类型登记进度"
    if result_text.count(marker) != 1:
        raise SystemExit("Could not find the S4 type-progress insertion point.")
    result_text = result_text.replace(marker, section + "\n\n" + marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge_text += (
        "\n\n### S3 archive：Manfrin 致 Edwards 的 1793 年书信索引候选并组（2026-10-16）\n\n"
        f"- `cand-1515`（M.csv#52，索引子项为致 Pietro Edwards 的 gallery-formation letter，p.395）从 `undecided` 改为 `new`，与 `cand-10849` 同入 `{GROUP}`，待 S4 登记一个 archive KU。第17章 p.380 注6 statement `st-chp17-p380-note6-edwards-letter-source` 将引文定位至 Biblioteca Correr 的 Epistolario Moschini，并指向本书附录7全文；第19章 p.395 statement `st-chp19-p395-manfrin-edwards-letter-source` 记录完整标题、Girolamo Manfrin 为寄件人、Pietro Edwards 为收件人、1793-12-03 日期和同一手稿系列定位。对具体信件，日期、当事人、议题、内部交叉引用与全篇转录构成充分身份锚点。\n"
        "- 保持 `cand-10605` 为不同 archive 对象：Epistolario Moschini 手稿系列/档案集合，而非单封信；本轮不把 collection 当作 letter，也不从信件内容扩展关系。身份依据是 Haskell 在 Appendix 7 的全文转录与引用；原件未独立查阅。候选身份组和 S2 关系候选分开处理，未登记 KU、卡片或正式关系。"
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
    print(f"  identity group: cand-1515 + cand-10849 -> {GROUP}; group count unchanged, pending member mappings +1; cand-10605 stays separate")
    if not args.apply:
        print("Dry-run only; pass --apply to write the changes.")
        return

    for path in updates:
        backup = path.with_name(path.name + ".bak-s3-manfrin-edwards-letter-20261016")
        if backup.exists():
            raise SystemExit(f"Recovery copy already exists: {backup}")
        shutil.copy2(path, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3-manfrin-edwards-letter-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied the archive identity grouping and retained recovery copies.")


if __name__ == "__main__":
    main()
