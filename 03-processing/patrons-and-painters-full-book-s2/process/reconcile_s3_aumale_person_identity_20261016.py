from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import shutil
from pathlib import Path


ROOT = Path.cwd()
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
BACKUP_SUFFIX = ".bak-s3-aumale-person-identity-20261016"

CID = "cand-7090"
GROUP = "person-group-henri-dorleans-duc-aumale-1822-1897"
BNF_URL = "https://catalogue.bnf.fr/ark:/12148/cb12375307v"
OLD_NOTE = (
    "source_ref=candidate=cand-7090;candidate_source_ref=chp-7:07_CHP-7_sec_i:l293-389#L355;"
    "source_file=02-sources/02-Markdown/07_CHP-7_sec_i.md#L293-389;s2_mentions=none; "
    "Undecided: source form lacks a full name or contains initials/only one name token. No external identity source was accessed."
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
    parser = argparse.ArgumentParser(description="Resolve the Duc d'Aumale person candidate to Henri d'Orléans using the BnF authority record.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment_rows, alignment_bom = read_csv(ALIGNMENT)
    candidate_fields, candidate_rows, candidate_bom = read_csv(CANDIDATES)
    target_alignments = [row for row in alignment_rows if row.get("candidate_id") == CID and not row.get("external_source")]
    target_candidates = [row for row in candidate_rows if row.get("candidate_id") == CID]
    if len(target_alignments) != 1 or len(target_candidates) != 1:
        raise SystemExit("Expected exactly one S3 candidate and one primary alignment row for cand-7090.")
    if target_alignments[0].get("decision") != "undecided" or target_alignments[0].get("resolution_note") != OLD_NOTE:
        raise SystemExit("cand-7090 no longer has the expected undecided S3 record; inspect before changing it.")
    if target_candidates[0].get("suggested_type") != "person":
        raise SystemExit("cand-7090 is no longer typed as a person.")
    if any(row.get("external_source") == "BnF Catalogue général" and row.get("external_id") == BNF_URL for row in alignment_rows):
        raise SystemExit("The BnF person identity row is already present.")
    if any(row.get("ku_id") == "units/persons/henri-dorleans-duc-aumale" for row in alignment_rows):
        raise SystemExit("The target Henri d'Orléans person KU is already mapped.")
    bibliog = (ROOT / "02-sources" / "02-Markdown" / "21_CHP-21Bibliography.md").read_text(encoding="utf-8-sig")
    if "d’Aumale, duc:" not in bibliog or "Inventaire de tous les tneubles du Cardinal Mazarin" not in bibliog:
        raise SystemExit("The current Chapter 21 bibliography no longer supports the source form d’Aumale, duc.")
    existing_persons = [row for row in candidate_rows if row.get("suggested_type") == "person" and row.get("candidate_id") != CID
                        and ("Henri d’Orléans" in row.get("canonical_name", "") or "Henri d'Orleans" in row.get("canonical_name", ""))]
    if existing_persons:
        raise SystemExit(f"A potentially duplicate Henri d'Orléans person candidate exists: {[r['candidate_id'] for r in existing_persons]}")

    max_alignment_number = max(int(match.group(1)) for row in alignment_rows
                               if (match := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", ""))))
    new_alignment_id = f"aln-{max_alignment_number + 1:05d}"
    if new_alignment_id in {row.get("alignment_id") for row in alignment_rows}:
        raise SystemExit("The generated external alignment id is already in use.")

    new_note = (
        "source_ref=candidate=cand-7090;candidate_source_ref=chp-7:07_CHP-7_sec_i:l293-389#L355;"
        "source_file=02-sources/02-Markdown/07_CHP-7_sec_i.md#L293-389;s2_mentions=none; "
        "external_identity=BnF Catalogue général, notice de personne FRBNF12375307, " + BNF_URL + "; "
        f"identity_peers={CID}; group={GROUP}; "
        "The bibliography form ‘d’Aumale, duc’ identifies the author designation used for the 1861 Mazarin inventory edition. "
        "The BnF authority record identifies this form as Henri d’Orléans (1822–1897), duc d’Aumale. "
        "Create a distinct person identity; no biography beyond the authority name, title, and dates is inferred. "
        f"prior_resolution_note={OLD_NOTE}"
    )
    planned_alignment = [dict(row) for row in alignment_rows]
    target = next(row for row in planned_alignment if row.get("candidate_id") == CID and not row.get("external_source"))
    target.update({"decision": "new", "ku_id": "", "process_ref": "S3-full-book-2026-10-16", "resolution_note": new_note})
    planned_alignment.append({
        "alignment_id": new_alignment_id,
        "candidate_id": CID,
        "ku_id": "",
        "external_source": "BnF Catalogue général",
        "external_id": BNF_URL,
        "decision": "new",
        "accessed_date": "2026-10-16",
        "process_ref": "S3-full-book-2026-10-16",
        "legacy_ku_id": "",
        "resolution_note": (
            "Identity only: BnF person authority FRBNF12375307 identifies Aumale as Henri d’Orléans, duc d’Aumale, "
            "1822–1897. It resolves the bibliography form ‘d’Aumale, duc’; it does not supply or validate further biography."
        ),
    })

    planned_candidates = [dict(row) for row in candidate_rows]
    candidate = next(row for row in planned_candidates if row.get("candidate_id") == CID)
    candidate["detail"] = (
        "The Haskell citation uses the bibliographic author form ‘d’Aumale, duc’ for the 1861 Mazarin inventory edition. "
        "BnF person authority FRBNF12375307 identifies the person as Henri d’Orléans, duc d’Aumale (1822–1897). "
        "S3 registers one person identity; no additional biography is inferred."
    )

    process_text = (ROOT / "03-processing" / TASK / "process" / "knowledge.md").read_text(encoding="utf-8-sig")
    heading = "### S3 person：d’Aumale, duc 对齐至 Henri d’Orléans（2026-10-16）"
    if heading in process_text:
        raise SystemExit("The Henri d’Orléans S3 person reconciliation is already recorded.")
    process_text += (
        f"\n\n{heading}\n\n"
        "- `cand-7090`（第7章注2所引 `d’Aumale, p.8`，候选源行L355）原为undecided，原因是来源只给头衔形式且无S2人物提及。"
        "BnF Catalogue général的人物权威记录FRBNF12375307将该作者形式识别为Henri d’Orléans, duc d’Aumale（1822–1897）；"
        "第21章书目把同一责任形式用于1861年《Inventaire de tous les meubles du Cardinal Mazarin》。\n"
        f"- 现裁为`new`，身份组`{GROUP}`，待S4登记为独立人物KU；不是既有其他Henri d’Orléans候选或奥尔良家族KU。"
        "原undecided理由写入alignment的`prior_resolution_note`。身份记录只支持规范名、头衔和生卒年，不扩写传记；他与1861年刊本的正式作者关系留待S6。\n"
        f"- 新增外部身份行`{new_alignment_id}`（BnF FRBNF12375307）。候选决定new增至5,023个、4,840组，undecided降至5,499；"
        "S4待登记4,538组、4,630条成员候选；未创建KU或关系。\n"
    )

    result_text = (ROOT / "04-knowledge" / "results" / f"{TASK}.md").read_text(encoding="utf-8-sig")
    result_text = replace_once(result_text,
        "12,622 条：12,404 条候选决定记录及 218 条外部身份记录",
        "12,623 条：12,404 条候选决定记录及 219 条外部身份记录")
    result_text = replace_once(result_text,
        "new=5,022（4,839个身份组）、conflict=8、excluded=100、undecided=5,500。S4 已登记302组、映射393条成员候选；尚待登记4,537组、4,629条映射。",
        "new=5,023（4,840个身份组）、conflict=8、excluded=100、undecided=5,499。S4 已登记302组、映射393条成员候选；尚待登记4,538组、4,630条映射。")
    result_text = replace_once(result_text,
        "| new | 5,021 | 按 4,839 个当前身份组进入 S4；每组登记一个 KU |",
        "| new | 5,023 | 按 4,840 个当前身份组进入 S4；每组登记一个 KU |")
    result_text = replace_once(result_text, "| undecided | 5,501 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |",
                               "| undecided | 5,499 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |")
    result_text = replace_once(result_text,
        "| new | 5,021 | 按 4,839 个当前身份组进入 S4；每组登记一个 KU |",
        "| new | 5,023 | 按 4,840 个当前身份组进入 S4；每组登记一个 KU |") if "| new | 5,021 | 按 4,839 个当前身份组进入 S4；每组登记一个 KU |" in result_text else result_text
    result_text = replace_once(result_text,
        "| person | 1,004→387 | 1,176／1,083 | 88／995；1,040 | 3 | 7 | 1,274 |",
        "| person | 1,004→387 | 1,177／1,084 | 88／996；1,041 | 3 | 7 | 1,273 |")
    result_text = replace_once(result_text,
        "| **合计** | **1,774→1,026** | **5,022／4,839** | **302／4,537；4,629** | **8** | **100** | **5,500** |",
        "| **合计** | **1,774→1,026** | **5,023／4,840** | **302／4,538；4,630** | **8** | **100** | **5,499** |")
    result_text = replace_once(result_text, "## 未解决项与交接限制", f"{heading}\n\n"
        "- `cand-7090`由BnF人物权威记录FRBNF12375307识别为Henri d’Orléans, duc d’Aumale（1822–1897），现裁为单独new-person组。\n"
        "- new=5,023（4,840组），undecided=5,499；S4待登记4,538组、4,630条成员候选。详情见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)。\n\n"
        "## 未解决项与交接限制")

    updates = {
        ALIGNMENT: encode_csv(alignment_fields, planned_alignment, alignment_bom),
        CANDIDATES: encode_csv(candidate_fields, planned_candidates, candidate_bom),
        PROCESS: encode_text(PROCESS, process_text),
        RESULT: encode_text(RESULT, result_text),
    }
    print("DRY-RUN" if args.dry_run else "APPLY")
    for path, content in updates.items():
        print(f"  {path.relative_to(ROOT)}: {digest(path.read_bytes())} -> {digest(content)}")
    print(f"  cand-7090: undecided -> new; group={GROUP}; external identity={new_alignment_id}")
    print("  new=5,023/4,840 groups; undecided=5,499; pending S4=4,538/4,630")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in updates]
    if any(path.exists() for path in backups):
        raise SystemExit("An Aumale person S3 recovery copy already exists; inspect before applying.")
    for original, backup in zip(updates, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3-aumale-person-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied Henri d'Orléans S3 person alignment.")


if __name__ == "__main__":
    main()
