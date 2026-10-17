from __future__ import annotations

import argparse
import csv
import hashlib
import io
import shutil
from pathlib import Path


ROOT = Path.cwd()
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
BACKUP_SUFFIX = ".bak-s3-brienne-bibliography-candidate-20261016"

CID = "cand-11265"
GROUP = "archive-group-brienne-memoires-1916-1919"
BNF_URL = "https://catalogue.bnf.fr/ark:/12148/cb340193395"
SOURCE_QUOTE = "Brienne, Louis-Henri de Loménie Comte de: Mémoires, publiés par Paul Bonnefon, 3 vols., Paris 1916-19."
OLD_ALIGNMENT_NOTE = (
    "source_ref=candidate_ref=chp-21:21_CHP-21Bibliography:l243-293#L254 | mentions=m-chp21-bib-l243-293-007 | "
    "statements=st-chp21-bib-l243-293-entry-07; 身份或粒度未定：The bibliography identifies a three-volume edition. "
    "Keep distinct from volume-specific citation candidates pending S3 identity review; contents were not independently consulted."
)


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), bom


def encode_csv(fields: list[str], rows: list[dict[str, str]], bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    text = stream.getvalue()
    return ("\ufeff" + text if bom else text).encode("utf-8")


def encode_text(path: Path, text: str) -> bytes:
    bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    return ("\ufeff" + text if bom else text).encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one occurrence of {old!r}, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve the Brienne bibliography candidate into the existing S3 archive group.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment_rows, alignment_bom = read_csv(ALIGNMENT)
    candidate_fields, candidate_rows, candidate_bom = read_csv(CANDIDATES)
    alignment_matches = [row for row in alignment_rows if row.get("candidate_id") == CID and not row.get("external_source")]
    candidate_matches = [row for row in candidate_rows if row.get("candidate_id") == CID]
    if len(alignment_matches) != 1 or len(candidate_matches) != 1:
        raise SystemExit("Expected exactly one candidate and one primary alignment row for cand-11265.")
    if alignment_matches[0].get("decision") != "undecided" or alignment_matches[0].get("resolution_note") != OLD_ALIGNMENT_NOTE:
        raise SystemExit("cand-11265 no longer has the expected undecided S3 record; inspect before changing it.")
    if candidate_matches[0].get("suggested_type") != "archive":
        raise SystemExit("cand-11265 is no longer typed as archive.")
    source_text = " ".join((ROOT / "02-sources" / "02-Markdown" / "21_CHP-21Bibliography.md").read_text(encoding="utf-8-sig").split())
    if SOURCE_QUOTE not in source_text:
        raise SystemExit("The current Chapter 21 bibliography no longer supports the expected edition record.")
    peer_rows = [row for row in alignment_rows if row.get("candidate_id") in {"cand-1596", "cand-7071", "cand-7100"} and not row.get("external_source")]
    if len(peer_rows) != 3 or any(row.get("decision") != "new" or GROUP not in row.get("resolution_note", "") for row in peer_rows):
        raise SystemExit("The three expected Brienne volume/index peers are no longer in the S3 identity group.")

    new_note = (
        "source_ref=candidate_ref=chp-21:21_CHP-21Bibliography:l243-293#L254 | "
        "mentions=m-chp21-bib-l243-293-007 | statements=st-chp21-bib-l243-293-entry-07; "
        "identity_peers=cand-11265,cand-1596,cand-7071,cand-7100; "
        f"group={GROUP}; external_identity=BnF Catalogue général FRBNF34019339, {BNF_URL}; "
        "The Chapter 21 bibliography candidate identifies the complete three-volume Mémoires edition edited by Paul Bonnefon, Paris 1916-19. "
        "It is the same publication identity as the volume-I and volume-III citation candidates, not a separate edition or physical volume. "
        "The cited memoir pages were not independently consulted. "
        f"prior_resolution_note={OLD_ALIGNMENT_NOTE}"
    )
    planned_alignment = [dict(row) for row in alignment_rows]
    target_alignment = next(row for row in planned_alignment if row.get("candidate_id") == CID and not row.get("external_source"))
    target_alignment.update({"decision": "new", "ku_id": "", "process_ref": "S3-full-book-2026-10-16", "resolution_note": new_note})

    planned_candidates = [dict(row) for row in candidate_rows]
    target_candidate = next(row for row in planned_candidates if row.get("candidate_id") == CID)
    target_candidate["detail"] = (
        "Chapter 21 bibliography candidate for the complete three-volume edition of Mémoires, edited by Paul Bonnefon, Paris 1916-19. "
        "S3 groups it with the volume-I and volume-III citation candidates and the index subentry; this is one publication identity. "
        "The cited memoir pages were not independently consulted."
    )

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    heading = "### S3 archive：Brienne《Mémoires》书目候选并入三卷本身份组（2026-10-16）"
    if heading in process_text:
        raise SystemExit("Brienne bibliography reconciliation is already recorded.")
    process_text += (
        f"\n\n{heading}\n\n"
        "- `cand-11265`（第21章书目候选，`st-chp21-bib-l243-293-entry-07`）原因未决而与卷级候选分开。复核书目原文："
        "`Brienne, Louis-Henri de Loménie Comte de: Mémoires, publiés par Paul Bonnefon, 3 vols., Paris 1916-19.`。"
        "该条目给出完整三卷版身份，与`cand-7071`（卷I locator）、`cand-7100`（卷III locator）相合；BnF FRBNF34019339为这组候选提供同一三卷版目录身份依据。\n"
        f"- `cand-11265`现裁为`new`并进入`{GROUP}`，与`cand-1596`、`cand-7071`、`cand-7100`共用一个archive身份组；不是第四种出版物，也不把卷册等同为同一物理对象。"
        "旧的‘与卷级候选区分、等待S3’说明保留在alignment的`prior_resolution_note`及本记录；回忆录卷内页未独立查阅。\n"
        "- 本次改变1条既有候选决定；new候选总数增至5,022，身份组数仍为4,839，undecided降至5,500。S4待登记组仍为4,538，成员候选映射增至4,633；未创建KU、卡片或关系。\n"
    )

    result_text = RESULT.read_text(encoding="utf-8-sig")
    result_text = replace_once(
        result_text,
        "new=5,021（4,839个身份组）、conflict=8、excluded=100、undecided=5,501。S4 已登记301组、映射389条成员候选；尚待登记4,538组、4,632条映射。",
        "new=5,022（4,839个身份组）、conflict=8、excluded=100、undecided=5,500。S4 已登记301组、映射389条成员候选；尚待登记4,538组、4,633条映射。",
    )
    result_text = replace_once(
        result_text,
        "| archive | 79→61 | 1,258／1,220 | 41／1,179；1,198 | 0 | 18 | 745 |",
        "| archive | 79→61 | 1,258／1,220 | 41／1,179；1,199 | 0 | 18 | 745 |",
    )
    result_text = replace_once(
        result_text,
        "| **合计** | **1,774→1,026** | **5,021／4,839** | **301／4,538；4,632** | **8** | **100** | **5,501** |",
        "| **合计** | **1,774→1,026** | **5,022／4,839** | **301／4,538；4,633** | **8** | **100** | **5,500** |",
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", f"{heading}\n\n"
        "- `cand-11265`的第21章书目条目明确列Brienne《Mémoires》Paul Bonnefon编、3 vols.、Paris 1916-19；现并入已由BnF FRBNF34019339支持的卷I／卷III引文身份组。\n"
        "- new=5,022（4,839个身份组），undecided=5,500；S4待登记4,538组、4,633条成员候选。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)。\n\n"
        "## 未解决项与交接限制")

    updates = {
        ALIGNMENT: encode_csv(alignment_fields, planned_alignment, alignment_bom),
        CANDIDATES: encode_csv(candidate_fields, planned_candidates, candidate_bom),
        PROCESS: encode_text(PROCESS, process_text),
        RESULT: encode_text(RESULT, result_text),
    }
    print("DRY-RUN" if args.dry_run else "APPLY")
    for path, content in updates.items():
        old_hash = digest(path.read_bytes())
        print(f"  {path.relative_to(ROOT)}: {old_hash} -> {digest(content)}")
    print(f"  cand-11265: undecided -> new; group={GROUP}; candidates=4; new groups remain 4,839")
    print("  undecided=5,501 -> 5,500; S4 pending mappings=4,632 -> 4,633")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in updates]
    if any(path.exists() for path in backups):
        raise SystemExit("A Brienne S3 recovery copy already exists; inspect before applying.")
    for original, backup in zip(updates, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3-brienne-bibliography-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied Brienne bibliography S3 identity reconciliation.")


if __name__ == "__main__":
    main()
