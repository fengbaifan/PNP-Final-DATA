#!/usr/bin/env python3
"""Repair the p.401 title mention surfaced by the read-only locator."""
import argparse, csv, hashlib, json, shutil, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
T=ROOT/"04-knowledge"/"tables"
SRC=ROOT/"02-sources"/"02-Markdown"/"20_CHP-20Postscript.md"
P="chp-20:20_CHP-20Postscript:l81-96"
ST="st-chp20-p401-humphris-bust-possession"
BACKUP=".bak-s2-chp20-p401-title-mention-repair-20261004"
parser=argparse.ArgumentParser()
parser.add_argument("--apply",action="store_true")
args=parser.parse_args()
def rcsv(p):
    with p.open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f); return r.fieldnames,list(r)
def wcsv(p,fields,rows):
    with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="",dir=p.parent,delete=False) as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n")
        w.writeheader();w.writerows(rows);tmp=Path(f.name)
    tmp.replace(p)
def wjson(p,rows):
    with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="",dir=p.parent,delete=False) as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n")
        tmp=Path(f.name)
    tmp.replace(p)
lines=SRC.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256(SRC.read_bytes()).hexdigest()!="e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90":
    raise SystemExit("source changed")
seg="\n".join(lines[80:96])
if "Duke of Bracciano" not in lines[85]: raise SystemExit("title surface changed")
cp,candidates=rcsv(T/"entity-candidates.csv")
mp,mentions=rcsv(T/"mentions.csv")
sp=T/"book-statements.jsonl"
statements=[json.loads(x) for x in sp.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
cb={r["candidate_id"]:r for r in candidates}
if cb.get("cand-3479",{}).get("status")!="open": raise SystemExit("title candidate is not open")
if any(r["segment_id"]==P and r["surface_form"]=="Duke of Bracciano" for r in mentions):
    raise SystemExit("title mention already exists")
needle="Duke of Bracciano"
offset=sum(len(x)+1 for x in lines[80:85])+lines[85].index(needle)
if seg[offset:offset+len(needle)]!=needle: raise SystemExit("exact title span failed")
row={"mention_id":"m-chp20-p401-035","segment_id":P,"candidate_id":"cand-3479",
     "surface_form":needle,"start_char":str(offset),"end_char":str(offset+len(needle)),
     "note":"The appositional title is a separate index candidate; retain its identity link to Paolo Giordano II for S3 alignment."}
if any(r["mention_id"]==row["mention_id"] for r in mentions): raise SystemExit("mention ID already exists")
target=next((r for r in statements if r["statement_id"]==ST),None)
if target is None: raise SystemExit("target statement missing")
ids=target["qualifiers"]["mentioned_candidate_ids"]
if "cand-3479" not in ids: ids.append("cand-3479")
pm=T/"mentions.csv"; backups=[p.with_name(p.name+BACKUP) for p in (pm,sp)]
if args.apply:
    if any(p.exists() for p in backups): raise SystemExit("repair backup already exists")
    for p,b in zip((pm,sp),backups):shutil.copy2(p,b)
    wcsv(pm,mp,[*mentions,row]);wjson(sp,statements)
    print("applied title mention repair with backups")
else:
    print("DRY RUN: no files written")
    print("one exact mention will map to the existing open Duke of Bracciano candidate")