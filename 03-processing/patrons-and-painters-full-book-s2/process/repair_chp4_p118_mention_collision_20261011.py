#!/usr/bin/env python3
"""Repair one exact-duplicate mention span found by the strict p.118 audit."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "04-knowledge" / "tables" / "mentions.csv"
EXPECTED_SHA256 = "dfc7d56bd05853ea6017d588c2f59eac0ca659bebf5f4c8ee223f14a1f290779"
REMAP_ID = "m-chp4-sec-ii-p118note-0015"
REMOVE_ID = "m-chp4-sec-ii-p118note-origin-subject"
BACKUP_SUFFIX = ".bak-s2-chp4-p118-mention-spanfix-20261011"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prepare() -> tuple[bytes, bytes]:
    original = PATH.read_bytes()
    actual = digest(original)
    if actual != EXPECTED_SHA256:
        raise SystemExit(f"mentions.csv SHA changed; expected {EXPECTED_SHA256}, got {actual}")
    has_bom = original.startswith(b"\xef\xbb\xbf")
    text = original.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    header = next(csv.reader([lines[0].rstrip("\r\n")]))
    id_i, candidate_i, surface_i, note_i = (header.index(k) for k in ("mention_id", "candidate_id", "surface_form", "note"))
    eol_text = "\r\n" if b"\r\n" in original else "\n"
    out = [lines[0]]
    found_remap = found_remove = False
    for raw in lines[1:]:
        ending = "\r\n" if raw.endswith("\r\n") else ("\n" if raw.endswith("\n") else "")
        values = next(csv.reader([raw.rstrip("\r\n")]))
        mid = values[id_i]
        if mid == REMOVE_ID:
            if found_remove or values[candidate_i] != "cand-11673" or values[surface_i] != "Origin of Coral":
                raise SystemExit("unexpected duplicate subject mention row")
            found_remove = True
            continue
        if mid == REMAP_ID:
            if found_remap or values[candidate_i] != "cand-5724" or values[surface_i] != "Origin of Coral":
                raise SystemExit("unexpected existing Cortona painting mention row")
            values[candidate_i] = "cand-11673"
            values[note_i] = "Surface identifies the Origin of Coral subject; the unspecified Cortona painting remains cand-5724 in the linked statement."
            found_remap = True
            buf = io.StringIO(newline="")
            csv.writer(buf, lineterminator=ending or eol_text).writerow(values)
            out.append(buf.getvalue())
        else:
            out.append(raw)
    if not found_remap or not found_remove:
        raise SystemExit(f"expected target rows not found: remap={found_remap}, remove={found_remove}")
    output = ("".join(out)).encode("utf-8")
    if has_bom:
        output = b"\xef\xbb\xbf" + output
    return original, output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply the strict-audit mention-span repair")
    args = parser.parse_args()
    original, output = prepare()
    print(f"mode={'apply' if args.apply else 'dry-run'} remap={REMAP_ID}: cand-5724 -> cand-11673; remove exact duplicate {REMOVE_ID}")
    print(f"prewrite_sha256={digest(original)} postwrite_sha256={digest(output)}")
    if not args.apply:
        return
    backup = PATH.with_name(PATH.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"recovery backup already exists: {backup.name}")
    shutil.copy2(PATH, backup)
    if backup.read_bytes() != original:
        raise SystemExit("recovery backup verification failed")
    PATH.write_bytes(output)
    if digest(PATH.read_bytes()) != digest(output):
        raise SystemExit("postwrite digest mismatch")
    print(f"applied; verified recovery copy {backup.name}")


if __name__ == "__main__":
    main()
