#!/usr/bin/env python3
"""Repair p.403 candidate source refs to the audit's segment#Lline contract."""
import argparse
import csv
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
SEGMENT = "chp-20:20_CHP-20Postscript:l110-121"
BACKUP = ".bak-s2-chp20-p403-source-ref-repair-20261004"
EXPECTED = {
    "cand-10995": ("Pierre Rosenberg", 113),
    "cand-10996": ("Prince of Liechtenstein (patron discussed through Lankheit's research)", 114),
    "cand-10997": ("Lankheit (scholar cited by surname on p.403)", 114),
    "cand-10998": ("English royal patronage of Italian painting in the seventeenth and eighteenth centuries", 115),
    "cand-10999": ("Michael Levey", 115),
    "cand-11000": ("Michael Levey's catalogue of later Italian pictures in the Queen's collection", 115),
    "cand-11001": ("Croft-Murray (scholar cited on p.403)", 115),
    "cand-11002": ("Croft-Murray's account of Antonio Verrio's career in England", 115),
    "cand-11003": ("Exhibition devoted to Sir Thomas Isham", 116),
    "cand-11004": ("Catalogue of the exhibition devoted to Sir Thomas Isham", 116),
    "cand-11005": ("Seventeenth-century Florentine art (Florentine Seicento)", 118),
    "cand-11006": ("Artisti alla Corte Granducale exhibition (1969)", 120),
    "cand-11007": ("Catalogue of the Artisti alla Corte Granducale exhibition (1969)", 120),
    "cand-11008": ("Marco Chiarini", 120),
    "cand-11009": ("Malcolm Campbell", 120),
    "cand-11010": ("Malcolm Campbell's article on Grand Duke Ferdinand II's decision (1966)", 120),
    "cand-11011": ("Malcolm Campbell's book on Florentine art and patronage (1977)", 120),
    "cand-11012": ("Provincial Florentine artists", 120),
    "cand-11013": ("Evelina Borea", 121),
    "cand-11014": ("Evelina Borea's catalogue of the exhibition devoted to Don Lorenzo de' Medici's collection", 121),
    "cand-11015": ("Florentine provincialism", 121),
    "cand-11016": ("Florentine culture", 121),
    "cand-11017": ("Italian painting", 115),
    "cand-11018": ("Restoration period patronage in England", 115),
    "cand-11019": ("Exhibition on seventeenth-century Florentine art in New York (1969)", 118),
    "cand-11020": ("Exhibition on seventeenth-century Florentine art in Florence (1965)", 118),
    "cand-11021": ("Exhibition on seventeenth-century Florentine art in Florence (1974)", 118),
    "cand-11022": ("Exhibition on seventeenth-century Florentine art in London (1979)", 118),
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
with TABLE.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    fields, rows = reader.fieldnames, list(reader)
by_id = {row["candidate_id"]: row for row in rows}
for candidate_id, (name, line_number) in EXPECTED.items():
    row = by_id.get(candidate_id)
    if not row or row["canonical_name"] != name or row["candidate_origin"] != "body-mention":
        raise SystemExit(f"candidate changed: {candidate_id}")
    if row["candidate_source_ref"] != f"{SEGMENT}#L110-L121":
        raise SystemExit(f"unexpected old source ref for {candidate_id}: {row['candidate_source_ref']!r}")
    row["candidate_source_ref"] = f"{SEGMENT}#L{line_number}"

if args.apply:
    backup = TABLE.with_name(TABLE.name + BACKUP)
    if backup.exists():
        raise SystemExit("source-ref repair backup already exists")
    shutil.copy2(TABLE, backup)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(TABLE)
    print(f"repaired {len(EXPECTED)} p.403 candidate refs; backup {backup.name}")
else:
    print(f"DRY RUN: {len(EXPECTED)} refs map to exact reviewed segment lines; no files written")
