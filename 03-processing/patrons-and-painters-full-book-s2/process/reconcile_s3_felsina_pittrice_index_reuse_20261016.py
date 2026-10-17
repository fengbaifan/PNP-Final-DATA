from __future__ import annotations

import argparse
import csv
import hashlib
import io
import shutil
from collections import Counter
from pathlib import Path


ROOT = Path.cwd()
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
PROCESS_REF = "S3-full-book-2026-10-16"
CANDIDATE = "cand-1502"
KU = "units/archives/felsina-pittrice-1678-work"


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
    primary_by_id = {row["candidate_id"]: row for row in primary}
    expected = Counter({"same": 1767, "new": 5008, "undecided": 5522, "excluded": 99, "conflict": 8})
    if len(primary) != 12404 or len(alignment) != 12619 or Counter(row["decision"] for row in primary) != expected:
        raise SystemExit("Unexpected S3 baseline; inspect before changing the candidate.")

    candidate = candidates.get(CANDIDATE)
    decision = primary_by_id.get(CANDIDATE)
    if not candidate or (candidate["suggested_type"], candidate["index_entry_id"], candidate["sub_entry"], candidate["index_page_range"]) != ("archive", "M.csv#39", "Felsina Pittrice", "189"):
        raise SystemExit("cand-1502 index identity changed.")
    if not decision or decision["decision"] != "undecided" or decision["ku_id"]:
        raise SystemExit("cand-1502 is no longer the expected undecided candidate.")
    manifest = read_csv(MANIFEST)[1]
    unit = next((row for row in manifest if row["ku_id"] == KU), None)
    if not unit or unit["type"] != "archive" or "Felsina Pittrice" not in unit["name_en"]:
        raise SystemExit("The existing 1678 Felsina Pittrice KU is missing or changed.")
    if f"- {unit['card_path']}" not in ACCEPTED.read_text(encoding="utf-8-sig"):
        raise SystemExit("The proposed target KU is not listed in accepted.yml.")
    body_decision = primary_by_id.get("cand-6933")
    if not body_decision or body_decision["decision"] != "new" or body_decision["ku_id"] != KU:
        raise SystemExit("The p.189 body candidate no longer routes to the expected KU.")
    edition_candidate = candidates.get("cand-11384")
    edition_decision = primary_by_id.get("cand-11384")
    if not edition_candidate or "1841" not in edition_candidate["canonical_name"] or edition_decision["decision"] != "undecided":
        raise SystemExit("The separately unresolved 1841 edition candidate changed; review before applying.")

    prior_note = decision["resolution_note"]
    updated = [dict(row) for row in alignment]
    by_id = {row["candidate_id"]: row for row in updated if not row["external_source"]}
    by_id[CANDIDATE].update(
        ku_id=KU,
        decision="same",
        process_ref=PROCESS_REF,
        resolution_note=(
            "source_ref=index_entry=M.csv#39;page=189; body_candidate=cand-6933; "
            "existing_source_ref=02-sources/02-Markdown/07_CHP-7_sec_i.md#L252-L253; existing_card_evidence=units/archives/felsina-pittrice-1678-work.md#p189; "
            f"same={KU}; The indexed p.189 subentry identifies Malvasia's Felsina Pittrice work explicitly dated 1678 in the body. "
            "The accepted archive KU already records this same p.189 title/year anchor, so reuse it rather than create another archive group. "
            "Keep distinct from cand-11384, the separately cited two-volume Bologna 1841 edition, which remains undecided; this index entry does not identify that edition. "
            f"prior_resolution_note={prior_note}"
        ),
    )

    result_text = RESULT.read_text(encoding="utf-8-sig")
    replacements = [
        ("same=1,767（指向1,026个既有 KU）", "same=1,768（指向1,026个既有 KU）"),
        ("undecided=5,522。S4 已登记281组、映射352条成员候选；尚待登记4,551组、4,656条映射。", "undecided=5,521。S4 已登记281组、映射352条成员候选；尚待登记4,551组、4,656条映射。"),
        ("| same | 1,767 | 指向 1,026 个既有 KU |", "| same | 1,768 | 指向 1,026 个既有 KU |"),
        ("| undecided | 5,522 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |", "| undecided | 5,521 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |"),
        ("| archive | 78→61 | 1,249／1,216 | 29／1,187；1,214 | 0 | 18 | 755 |", "| archive | 79→61 | 1,249／1,216 | 29／1,187；1,214 | 0 | 18 | 754 |"),
        ("| **合计** | **1,767→1,026** | **5,008／4,832** | **281／4,551；4,656** | **8** | **99** | **5,522** |", "| **合计** | **1,768→1,026** | **5,008／4,832** | **281／4,551；4,656** | **8** | **99** | **5,521** |"),
    ]
    for old, new in replacements:
        if result_text.count(old) != 1:
            raise SystemExit(f"Expected one result occurrence of {old!r}, found {result_text.count(old)}")
        result_text = result_text.replace(old, new, 1)
    section = (
        "### S3 archive：Malvasia《Felsina Pittrice》索引候选复用（2026-10-16）\n\n"
        f"- `cand-1502`（M.csv#39，p.189）由 `undecided` 改为 `same` → `{KU}`。索引子项与第7章 p.189 正文同名，正文明确将作品年代记为1678；既有卡已收录同一页的书名与年份证据，并在 `accepted.yml` 接收，故复用现有身份。\n"
        "- 边界：第21章书目所列两卷本 Bologna 1841 年版是另一版本候选 `cand-11384`，仍 undecided；本次不将其并入 1678 年作品，也不新增 archive 组或外部身份记录。"
    )
    marker = "### S4 按类型登记进度"
    if result_text.count(marker) != 1:
        raise SystemExit("Could not find the S4 type-progress insertion point.")
    result_text = result_text.replace(marker, section + "\n\n" + marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge_text += (
        "\n\n### S3 archive：Malvasia《Felsina Pittrice》索引候选复用（2026-10-16）\n\n"
        f"- `cand-1502`（M.csv#39，p.189）从 `undecided` 改为 `same` → `{KU}`。索引 subentry 与第7章 p.189 同名，正文明确将 *Felsina Pittrice* 记为1678年作品；现有接收卡 `04-knowledge/{unit['card_path']}` 已记录该原文锚点，第7章 Markdown 行252–253。正文候选 `cand-6933` 已映射至同一 KU。由页码、题名、年代与既有卡证据可直接复用，不另建组。\n"
        "- 版本边界：第21章 p.428 书目候选 `cand-11384` 指向 Bologna 1841 年两卷本，仍 undecided；索引 p.189 指向作品身份，不足以证明具体引用的是1841年印本，因此不把该版本并入本卡。此裁决未添加外部身份记录或新的 KU/card。"
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
    print(f"  same identity: {CANDIDATE} -> {KU}; no new group or external row")
    if not args.apply:
        print("Dry-run only; pass --apply to write the changes.")
        return

    for path in updates:
        backup = path.with_name(path.name + ".bak-s3-felsina-pittrice-20261016")
        if backup.exists():
            raise SystemExit(f"Recovery copy already exists: {backup}")
        shutil.copy2(path, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3-felsina-pittrice-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied the archive identity reuse and retained recovery copies.")


if __name__ == "__main__":
    main()
