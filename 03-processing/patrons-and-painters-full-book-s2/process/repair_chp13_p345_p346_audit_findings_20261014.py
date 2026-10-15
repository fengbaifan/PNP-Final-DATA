#!/usr/bin/env python3
"""Repair exact-span duplicate and candidate source-anchor format from p.345-346."""
from __future__ import annotations

import argparse,csv,hashlib,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
TABLES=ROOT/"04-knowledge"/"tables"
CANDIDATES=TABLES/"entity-candidates.csv"
MENTIONS=TABLES/"mentions.csv"
EXPECTED={
 CANDIDATES:"0159438ae1dd0053adab905bc04652287b42edefa5b711c360868cc2b067919c",
 MENTIONS:"962ac7e5ae8f96dc60410a473388e95158fb21637c592fee93c42f4210b1e88f",
}
SUFFIX=".bak-s2-ch13-p345-p346-audit-repair-20261014"

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->None:
 ap=argparse.ArgumentParser();ap.add_argument("--apply",action="store_true");a=ap.parse_args()
 for p,h in EXPECTED.items():
  if sha(p)!=h:raise SystemExit(f"precondition failed: {p.name} sha256={sha(p)}")
 with CANDIDATES.open(encoding="utf-8-sig",newline="") as f:
  cr=csv.DictReader(f);ch=list(cr.fieldnames or []);candidates=list(cr)
 c=next(r for r in candidates if r["candidate_id"]=="cand-12181")
 c["candidate_source_ref"]="chp-13:13_CHP-13_intro:l173-177#L174"
 with MENTIONS.open(encoding="utf-8-sig",newline="") as f:
  mr=csv.DictReader(f);mh=list(mr.fieldnames or []);mentions=list(mr)
 duplicate=[r for r in mentions if r["mention_id"]=="m-s2-ch13-p345-057"]
 if len(duplicate)!=1:raise SystemExit(f"expected one duplicate mention row, found {len(duplicate)}")
 del mentions[mentions.index(duplicate[0])]
 print("candidate source anchor normalized to L174; duplicate p345 mention removed; no statement change")
 if not a.apply:
  print("DRY-RUN only; no tables changed");return
 for p in (CANDIDATES,MENTIONS):
  b=p.with_name(p.name+SUFFIX)
  if b.exists():raise SystemExit(f"recovery copy already exists: {b.name}")
  shutil.copy2(p,b)
 from io import StringIO
 out=StringIO(newline="");w=csv.DictWriter(out,fieldnames=ch,lineterminator="\n");w.writeheader();w.writerows(candidates)
 CANDIDATES.write_bytes(("\ufeff"+out.getvalue()).encode("utf-8"))
 out=StringIO(newline="");w=csv.DictWriter(out,fieldnames=mh,lineterminator="\n");w.writeheader();w.writerows(mentions)
 MENTIONS.write_bytes(("\ufeff"+out.getvalue()).encode("utf-8"))
 for p in (CANDIDATES,MENTIONS):print(f"wrote {p.relative_to(ROOT)} sha256={sha(p)}")
 print(f"recovery copies created with suffix {SUFFIX}")
if __name__=="__main__":main()
