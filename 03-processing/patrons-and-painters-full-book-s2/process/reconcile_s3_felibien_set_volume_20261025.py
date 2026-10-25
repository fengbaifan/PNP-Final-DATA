#!/usr/bin/env python3
"""Guarded S3 follow-up for a set-level and cited-volume candidate pair."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ALIGN_REL = "04-knowledge/tables/alignment.csv"
PROCESS_REL = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
CARD_REL = "04-knowledge/units/archives/felibien-entretiens-trevoux-1725-six-volume-edition.md"
RECOVERY_REL = "06-runtime/recovery/s3-followup-felibien-20261025"
ALIGNMENT_ID = "aln-11486"
CANDIDATE_ID = "cand-11323"
OTHER_CANDIDATE_ID = "cand-7077"
KU_ID = "units/archives/felibien-entretiens-trevoux-1725-six-volume-edition"
ANCHOR = "s3-followup-felibien-set-volume-identity-20261025"

EXPECTED_HASHES = {
    ALIGN_REL: "a5b168d520c51750b34e825d92f124171a332a569edafd176ca770140cd9813a",
    PROCESS_REL: "30ff83cfa78b692092fa0d654d9223cf81c2f6385e70f5f547be2d33d3842b08",
    CARD_REL: "0eaf7dc87a0c7c5108d46e3aa26497516a847148a17532d0dedeb453b7304e1f",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader), bom, newline


def write_csv(headers, rows, bom: bool, newline: str) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, extrasaction="ignore", lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    data = buffer.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if bom else data


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", delete=False) as f:
        temporary = Path(f.name)
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temporary, path)


def plan():
    for rel, expected in EXPECTED_HASHES.items():
        path = ROOT / rel
        if not path.exists() or sha(path.read_bytes()) != expected:
            raise SystemExit(f"baseline changed; refusing to apply: {rel}")

    align_path = ROOT / ALIGN_REL
    headers, alignments, bom, newline = read_csv(align_path)
    target_rows = [r for r in alignments if r.get("alignment_id") == ALIGNMENT_ID]
    other_rows = [r for r in alignments if r.get("candidate_id") == OTHER_CANDIDATE_ID]
    if len(target_rows) != 1 or len(other_rows) != 1:
        raise SystemExit("expected exactly one target alignment and one cited-volume alignment")
    target = target_rows[0]
    other = other_rows[0]
    if target.get("candidate_id") != CANDIDATE_ID or target.get("decision") != "undecided" or target.get("ku_id"):
        raise SystemExit("the set-level candidate is no longer the expected undecided record")
    if other.get("decision") != "new" or other.get("ku_id") != KU_ID:
        raise SystemExit("the cited-volume candidate no longer maps to the registered edition")
    if "set-level publication record" not in target.get("resolution_note", ""):
        raise SystemExit("the prior granularity question is missing")

    target["decision"] = "same"
    target["ku_id"] = KU_ID
    target["resolution_note"] += (
        " S3 follow-up after S4 registration (2026-10-25): same -> " + KU_ID
        + "; Chapter 21 bibliography at printed p.422, L466 identifies the six-volume nouvelle édition"
        + " at Trévoux in 1725; Chapter 7 printed p.182 note 2, L344 cites its volume III, p.530."
        + " The cited volume/page is a locator within the same edition, not a separately evidenced edition."
        + " The cited book and page were not independently consulted."
    )

    process_path = ROOT / PROCESS_REL
    process_raw = process_path.read_bytes()
    process_bom = process_raw.startswith(b"\xef\xbb\xbf")
    process_nl = "\r\n" if b"\r\n" in process_raw else "\n"
    process_text = process_raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    if f'<a id="{ANCHOR}"></a>' in process_text:
        raise SystemExit("S3 follow-up anchor already exists")
    if not process_text.endswith("\n"):
        process_text += "\n"
    process_text += f'''

<a id="{ANCHOR}"></a>

### S3定点复核：Félibien六卷本与第三卷引注的身份粒度（2026-10-25）

本次S4登记触发对既有未决候选`{CANDIDATE_ID}`的定点S3复核。`{OTHER_CANDIDATE_ID}`原为第7章注2的Félibien第三卷第530页书目引注候选；`{CANDIDATE_ID}`来自第21章p.422同一条目，表示“nouvelle édition, 6 vols., Trévoux 1725”的整套出版记录。两张页图分别确认第7章印刷页182注2（PDF物理页16）与第21章印刷页422书目（PDF物理页12）。

**身份粒度裁决。** 本批S4所建KU代表Trévoux 1725年六卷本版本；`{OTHER_CANDIDATE_ID}`中的“III, p.530”保留为`cites`关系的卷／页定位。两候选指向同一版本级书目实体，因此将`{ALIGNMENT_ID}`由`undecided`定点裁为`same`并映射至`{KU_ID}`。这不表示第三卷物理本与六卷集合是同一件馆藏实物；项目记录的是同一出版版本，卷页仅作引注定位。未查阅被引著作或该页，也未使用外部身份记录。

该决定只解决这两条书内候选的粒度差异；不改变其他Félibien候选、原书正文、S2 statement或统一独立复核分子。
'''
    process_bytes = process_text.replace("\n", process_nl).encode("utf-8")
    if process_bom:
        process_bytes = b"\xef\xbb\xbf" + process_bytes

    card_path = ROOT / CARD_REL
    card_raw = card_path.read_bytes()
    card_bom = card_raw.startswith(b"\xef\xbb\xbf")
    card_text = card_raw.decode("utf-8-sig")
    old = "S3身份组 `archive-group-b5989be79137` 将候选 `cand-7077` 对齐至本KU。第21章书目中的责任者形式与书内索引所列 André Félibien 对应；复用既有人物KU，不据此添加外部身份标识。未查阅书目以外的外部目录或该著作。"
    new = (
        "S3身份组 `archive-group-b5989be79137` 的 new 候选 `cand-7077` 映射至本KU；"
        "第21章p.422整套书目候选 `cand-11323` 经S3定点复核为 same，并映射至本KU。"
        "第7章所引第三卷第530页作为该版本的卷页定位，不另表示单独查核的物理卷册。"
        "书目责任者形式与书内索引所列 André Félibien 对应；复用既有人物KU，不添加外部身份标识。"
        "未查阅书目以外的外部目录或该著作。"
    )
    if old not in card_text:
        raise SystemExit("expected identity paragraph not found in the new archive card")
    card_text = card_text.replace(old, new, 1)
    card_bytes = card_text.encode("utf-8")
    if card_bom:
        card_bytes = b"\xef\xbb\xbf" + card_bytes

    return {
        align_path: write_csv(headers, alignments, bom, newline),
        process_path: process_bytes,
        card_path: card_bytes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    files = plan()
    print(f"S3 follow-up: {ALIGNMENT_ID}/{CANDIDATE_ID} undecided -> same -> {KU_ID}")
    print("basis: same Trévoux 1725 six-volume edition; volume III p.530 retained as citation locator")
    print(f"files planned: {len(files)}; no other candidate or S2 statement changes")
    if args.dry_run:
        print("DRY RUN passed; no files changed")
        return 0

    recovery_root = ROOT / RECOVERY_REL
    if recovery_root.exists():
        raise SystemExit(f"recovery path already exists; refusing to overwrite: {recovery_root}")
    recovery_root.mkdir(parents=True)
    backups = []
    try:
        for path in files:
            rel = path.relative_to(ROOT)
            backup = recovery_root / "original" / rel
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup)
            backups.append((path, backup))
        for path, data in files.items():
            atomic_write(path, data)
    except BaseException:
        for path, backup in reversed(backups):
            atomic_write(path, backup.read_bytes())
        raise
    print(f"APPLIED; recovery snapshot: {RECOVERY_REL}; backed up {len(backups)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
