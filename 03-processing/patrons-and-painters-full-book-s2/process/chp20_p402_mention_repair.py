#!/usr/bin/env python3
"""Repair the p.402 Italian-art mention surfaced by the read-only locator."""
import argparse,csv,hashlib,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
T=ROOT/"04-knowledge"/"tables"
SRC=ROOT/"02-sources"/"02-Markdown"/"20_CHP-20Postscript.md"
P="chp-20:20_CHP-20Postscript:l98-108"
SID="st-chp20-p402-mazarin-art-policy-in-france"
MID="m-chp20-p402-039"
BACKUP=".bak-s2-chp20-p402-mention-repair-20261004"
parser=argparse.ArgumentParser()
parser.add_argument("--apply",action="store_true")
args=parser.parse_args()
def rcsv(p):
    with p.open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f);return r.fieldnames,list(r)
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
if hashlib.sha256(SRC.read_bytes()).hexdigest()!="e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90":
    raise SystemExit("source changed")
lines=SRC.read_text(encoding="utf-8-sig").splitlines()
segment="\n".join(lines[97:108])
if hashlib.sha256(segment.encode("utf-8")).hexdigest()!="64eb2299cfe55d839d396f3ac35f345ecc661c6ccde89528b08263d70b99e765":
    raise SystemExit("p.402 source segment changed")
line106=lines[105]
surface="Italian art"
within=line106.find(surface)
if within<0 or line106.find(surface,within+1)>=0:raise SystemExit("unique L106 surface changed")
offset=sum(len(x)+1 for x in lines[97:105])+within
if segment[offset:offset+len(surface)]!=surface:raise SystemExit("exact mention anchor failed")
cp,candidates=rcsv(T/"entity-candidates.csv")
mp,mentions=rcsv(T/"mentions.csv")
sp=T/"book-statements.jsonl"
statements=[json.loads(x) for x in sp.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
cb={r["candidate_id"]:r for r in candidates}
if cb.get("cand-4131",{}).get("status")!="open":raise SystemExit("Italian art candidate unavailable")
if any(r["mention_id"]==MID for r in mentions):raise SystemExit("repair mention ID already exists")
if any(r["segment_id"]==P and r["candidate_id"]=="cand-4131" and r["surface_form"]==surface for r in mentions):
    raise SystemExit("Italian art mention already exists")
target=next((r for r in statements if r["statement_id"]==SID),None)
if target is None:raise SystemExit("target statement missing")
ids=target["qualifiers"]["mentioned_candidate_ids"]
if "cand-4131" in ids:raise SystemExit("candidate already linked to target statement")
row={"mention_id":MID,"segment_id":P,"candidate_id":"cand-4131","surface_form":surface,
     "start_char":str(offset),"end_char":str(offset+len(surface)),
     "note":"The phrase refers to Mazarin's patronage and collecting of Italian art in France; reuse the existing open term candidate."}
ids.append("cand-4131")
paths=[T/"mentions.csv",sp]
backups=[p.with_name(p.name+BACKUP) for p in paths]
if args.apply:
    if any(p.exists() for p in backups):raise SystemExit("repair recovery backup already exists")
    for p,b in zip(paths,backups):shutil.copy2(p,b)
    wcsv(paths[0],mp,[*mentions,row]);wjson(paths[1],statements)
    print(f"applied p.402 mention repair; backup suffix {BACKUP}")
else:
    print("DRY RUN: no files written")
    print(f"one exact mention at L106 offset {offset}; target statement {SID}; candidate cand-4131")
