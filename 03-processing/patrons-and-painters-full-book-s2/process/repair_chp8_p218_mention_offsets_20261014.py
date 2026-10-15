"""Guarded correction of p.218 mention offsets to include the segment's page header."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import shutil
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
TABLE=ROOT/"04-knowledge/tables/mentions.csv"
SEGMENTS=ROOT/"04-knowledge/tables/segments.jsonl"
SOURCE=ROOT/"02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SEGMENT_ID="chp-8:08_CHP-8_sec_ii:l78-84"
INPUT_SHA="d6219aaf3fd9593191b7bf583c2c73cdefecfbf9c368f988b22afbb009dbf955"
EXPECTED={
 "m-chp8-p218-side-door-picture":("1675","1686","1686","1697","the picture"),
 "m-chp8-p218-three-pictures":("1902","1939","1913","1950","Three pictures remained to be painted"),
 "m-chp8-p218-smaller-inner-wall-picture":("1988","2009","1999","2020","one, slightly smaller"),
 "m-chp8-p218-zanchi-venetian":("2190","2198","2201","2209","Venetian"),
}
BACKUP=TABLE.with_name(TABLE.name+".bak-s2-chp8-p218-mention-offset-repair-20261014")

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def run(apply):
 if digest(TABLE)!=INPUT_SHA: raise SystemExit("mentions.csv changed since the guarded correction was prepared")
 import json
 segments={json.loads(line)["segment_id"]:json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()}
 seg=segments.get(SEGMENT_ID)
 if not seg: raise SystemExit("segment missing")
 lines=SOURCE.read_text(encoding="utf-8-sig").splitlines()
 text="\n".join(lines[int(seg["line_start"])-1:int(seg["line_end"])])
 with TABLE.open(encoding="utf-8-sig",newline="") as f:
  reader=csv.DictReader(f); fields=list(reader.fieldnames or []); rows=list(reader); bom=TABLE.read_bytes().startswith(b"\xef\xbb\xbf")
 by_id={r["mention_id"]:r for r in rows}
 for mid,(old_start,old_end,new_start,new_end,surface) in EXPECTED.items():
  r=by_id.get(mid)
  if not r or (r["start_char"],r["end_char"],r["surface_form"])!=(old_start,old_end,surface): raise SystemExit(f"unexpected current mention state: {mid}")
  if text[int(new_start):int(new_end)]!=surface: raise SystemExit(f"corrected span does not match source text: {mid}")
  r["start_char"],r["end_char"]=new_start,new_end
 out=io.StringIO(newline=""); writer=csv.DictWriter(out,fieldnames=fields,extrasaction="ignore",lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
 data=out.getvalue().encode("utf-8")
 if bom:data=b"\xef\xbb\xbf"+data
 print(f"mode={'apply' if apply else 'dry-run'} corrected_mentions={len(EXPECTED)}")
 if not apply:return
 if BACKUP.exists():
  if BACKUP.read_bytes()!=TABLE.read_bytes(): raise SystemExit("existing backup differs from input")
 else:shutil.copy2(TABLE,BACKUP)
 if digest(BACKUP)!=INPUT_SHA: raise SystemExit("backup checksum mismatch")
 with tempfile.NamedTemporaryFile("wb",dir=TABLE.parent,delete=False,suffix=".tmp") as f:f.write(data); tmp=Path(f.name)
 tmp.replace(TABLE)
 print("written_sha256="+digest(TABLE))

if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--apply",action="store_true");a=p.parse_args();run(a.apply)
