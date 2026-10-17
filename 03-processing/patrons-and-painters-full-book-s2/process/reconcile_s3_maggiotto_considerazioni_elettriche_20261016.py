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
GROUP = "archive-group-maggiotto-considerazioni-elettriche-1781"
TRECCANI_URL = "https://www.treccani.it/enciclopedia/fedeli-francesco-detto-il-maggiotto_(Dizionario-Biografico)/"


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
    expected = Counter({"same": 1767, "new": 5007, "undecided": 5523, "excluded": 99, "conflict": 8})
    if len(primary) != 12404 or len(alignment) != 12618 or len(external) != 214:
        raise SystemExit("Unexpected alignment shape; inspect the current S3 baseline.")
    if Counter(row["decision"] for row in primary) != expected:
        raise SystemExit("Unexpected S3 decisions; inspect the current baseline.")

    candidate = candidates.get("cand-1490")
    decision = primary_by_id.get("cand-1490")
    if not candidate or (candidate["suggested_type"], candidate["index_entry_id"], candidate["sub_entry"]) != ("archive", "M.csv#27", "Considerazioni elettriche"):
        raise SystemExit("cand-1490 no longer identifies the expected archive candidate.")
    if not decision or decision["decision"] != "undecided" or decision["ku_id"]:
        raise SystemExit("cand-1490 is no longer the expected undecided candidate.")
    if any(row["candidate_id"] == "cand-1490" and row["external_source"] for row in alignment):
        raise SystemExit("cand-1490 already has an external identity row; review before retrying.")
    if any(f"group={GROUP}" in row["resolution_note"] for row in primary):
        raise SystemExit("The proposed archive identity group already exists.")
    if any(row["type"] == "archive" and "considerazioni elettriche" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for row in read_csv(MANIFEST)[1]):
        raise SystemExit("A matching archive KU now exists; compare it before deciding new.")

    with MENTIONS.open("r", encoding="utf-8-sig", newline="") as stream:
        mentions = {row["mention_id"]: row for row in csv.DictReader(stream)}
    mention_id = "m-s2-ch10-p325-0047"
    if mentions.get(mention_id, {}).get("candidate_id") != "cand-1490":
        raise SystemExit("The direct p.325 title mention no longer maps to cand-1490.")
    with STATEMENTS.open("r", encoding="utf-8-sig") as stream:
        statements = [json.loads(line) for line in stream if line.strip()]
    body_id = "st-chp10-p325-maggiotto-scientific-invention-and-treatise"
    citation_id = "st-chp10-p325-n1-magggiotto-source-citations"
    by_statement = {row["statement_id"]: row for row in statements}
    if body_id not in by_statement or citation_id not in by_statement:
        raise SystemExit("The direct p.325 body/citation statements changed.")
    if "cand-1490" not in by_statement[body_id].get("qualifiers", {}).get("mentioned_candidate_ids", []) or "cand-1490" not in by_statement[citation_id].get("qualifiers", {}).get("mentioned_candidate_ids", []):
        raise SystemExit("The p.325 statements no longer identify cand-1490.")
    citation_json = json.dumps(by_statement[citation_id], ensure_ascii=False)
    if "Misc. 105113" not in citation_json:
        raise SystemExit("The Correr shelfmark locator changed.")

    prior_note = decision["resolution_note"]
    updated = [dict(row) for row in alignment]
    updated_by_id = {row["candidate_id"]: row for row in updated if not row["external_source"]}
    updated_by_id["cand-1490"].update(
        decision="new",
        process_ref=PROCESS_REF,
        resolution_note=(
            f"source_ref=index_entry=M.csv#27;page=325n; mention={mention_id}; statements={body_id},{citation_id}; "
            f"group={GROUP}; published_title=Considerazioni elettriche; author=Francesco Maggiotto; year=1781; "
            "Haskell's note cites a Correr copy under Misc. 105113 but supplies no date or publisher. Treccani DBI (Ettore Merkel, vol.45, 1995) separately lists Considerazioni elettriche, Venice 1781, among Maggiotto's printed booklets; the title and named author match. "
            "One new archive identity group, pending S4. Keep distinct from the 1882 Tessier article cand-9779 and from the other two 1781 electrical booklets listed by Treccani. The external source supports bibliographic identity only, not Haskell's account of the invention or any relation. "
            f"prior_resolution_note={prior_note}"
        ),
    )

    ids = [int(row["alignment_id"].split("-")[-1]) for row in updated if row["alignment_id"].startswith("aln-") and row["alignment_id"].split("-")[-1].isdigit()]
    external_alignment_id = f"aln-{max(ids) + 1:04d}"
    if any(row["alignment_id"] == external_alignment_id for row in updated):
        raise SystemExit(f"Alignment ID already exists: {external_alignment_id}")
    updated.append({
        "alignment_id": external_alignment_id,
        "candidate_id": "cand-1490",
        "ku_id": "",
        "external_source": "Treccani DBI (Ettore Merkel, vol.45, 1995)",
        "external_id": TRECCANI_URL,
        "decision": "new",
        "accessed_date": "2026-10-16",
        "process_ref": PROCESS_REF,
        "legacy_ku_id": "",
        "resolution_note": (
            f"Identity only: {TRECCANI_URL} names Considerazioni elettriche as a printed booklet by Francesco Fedeli, detto il Maggiotto, published in Venice in 1781. "
            "This confirms the indexed treatise's title, author, printed-publication status, and edition-year anchor; it does not verify the account of the electrical machine, the cited Correr copy's current custody, or relations."
        ),
    })

    result_text = RESULT.read_text(encoding="utf-8-sig")
    replacements = [
        ("new=5,007（4,831个身份组）", "new=5,008（4,832个身份组）"),
        ("undecided=5,523。S4 已登记281组、映射352条成员候选；尚待登记4,550组、4,655条映射。", "undecided=5,522。S4 已登记281组、映射352条成员候选；尚待登记4,551组、4,656条映射。"),
        ("12,618 条：12,404 条候选决定记录及 214 条外部身份记录", "12,619 条：12,404 条候选决定记录及 215 条外部身份记录"),
        ("214条外部身份记录单独保留", "215条外部身份记录单独保留"),
        ("| new | 5,007 | 按 4,831 个当前身份组进入 S4；每组登记一个 KU |", "| new | 5,008 | 按 4,832 个当前身份组进入 S4；每组登记一个 KU |"),
        ("| undecided | 5,523 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |", "| undecided | 5,522 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |"),
        ("| archive | 78→61 | 1,248／1,215 | 29／1,186；1,213 | 0 | 18 | 756 |", "| archive | 78→61 | 1,249／1,216 | 29／1,187；1,214 | 0 | 18 | 755 |"),
        ("| **合计** | **1,767→1,026** | **5,007／4,831** | **281／4,550；4,655** | **8** | **99** | **5,523** |", "| **合计** | **1,767→1,026** | **5,008／4,832** | **281／4,551；4,656** | **8** | **99** | **5,522** |"),
    ]
    for old, new in replacements:
        if result_text.count(old) != 1:
            raise SystemExit(f"Expected one result occurrence of {old!r}, found {result_text.count(old)}")
        result_text = result_text.replace(old, new, 1)
    section = (
        "### S3 archive：Maggiotto《Considerazioni elettriche》身份裁决（2026-10-16）\n\n"
        f"- `cand-1490`（M.csv#27，p.325n）由 `undecided` 改为 `new`，进入 `{GROUP}`，待 S4 登记。Haskell 正文称 Francesco Maggiotto 撰写电学论著；脚注给出题名、威尼斯 Biblioteca Correr 的 `Misc. 105113` 馆藏号，但未标年份或出版者。Treccani DBI（Ettore Merkel，vol.45，1995）将 Francesco Fedeli, detto il Maggiotto 的《Considerazioni elettriche》列为威尼斯1781年出版的小册子，足以支持题名、作者和版本身份。\n"
        "- 本组仅表示该书的书目身份。与1882年 Tessier 论文 `cand-9779` 分开；Treccani 同时列出的另外两种1781年电学小册子亦为不同题名，不合并。外部记录不证明发明叙述、Correr 当前馆藏或关系；一条直接关系候选留待 S6，不创建 KU、卡片或正式关系。"
    )
    marker = "### S4 按类型登记进度"
    if result_text.count(marker) != 1:
        raise SystemExit("Could not find the S4 type-progress insertion point.")
    result_text = result_text.replace(marker, section + "\n\n" + marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge_text += (
        "\n\n### S3 archive：Maggiotto《Considerazioni elettriche》身份裁决（2026-10-16）\n\n"
        f"- `cand-1490`（M.csv#27，索引子项 `Considerazioni elettriche`，p.325n）从 `undecided` 改为 `new`，身份组 `{GROUP}`，待 S4 登记。正文 statement `{body_id}` 将论著归于 Francesco Maggiotto；脚注 statement `{citation_id}` 给出书名及 Biblioteca Correr, Venice, `Misc. 105113` 馆藏号。脚注未标年份和出版者，因此补查 Treccani DBI：Ettore Merkel, vol.45 (1995), {TRECCANI_URL}，以 Francesco Fedeli, detto il Maggiotto 立目，并明确列《Considerazioni elettriche》为其1781年在威尼斯出版的小册子。标题、作者与索引/正文语境相合，支持新增一个 archive 身份组。\n"
        "- 本轮只使用该外部记录确认书目身份和版本锚点，不据此验证电学装置发明叙述、Correr 当前馆藏状态或关系。明确区分脚注同列的 Tessier 1882 论文候选 `cand-9779`，也不把 Treccani 所列另两种1781年电学小册子合并进来。该候选的一条直接 S2 关系候选留待 S6；无 KU、卡片、关系写回。\n"
        "- 外部身份对齐：Treccani DBI，Ettore Merkel，vol.45 (1995)，访问于2026-10-16；来源标识与身份范围见 `alignment.csv` 新增外部行。"
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
    print(f"  identity group: cand-1490 -> {GROUP}; external record {external_alignment_id}; S4 group and member counts +1")
    if not args.apply:
        print("Dry-run only; pass --apply to write the changes.")
        return

    for path in updates:
        backup = path.with_name(path.name + ".bak-s3-maggiotto-considerazioni-20261016")
        if backup.exists():
            raise SystemExit(f"Recovery copy already exists: {backup}")
        shutil.copy2(path, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3-maggiotto-considerazioni-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied the archive identity decision and retained recovery copies.")


if __name__ == "__main__":
    main()
