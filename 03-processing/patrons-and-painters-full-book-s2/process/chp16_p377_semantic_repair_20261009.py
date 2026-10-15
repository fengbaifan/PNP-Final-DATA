"""Repair three mechanical anchor issues found by the first strict audit of p.377."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
TABLES=ROOT/"04-knowledge"/"tables"
SOURCE=ROOT/"02-sources"/"02-Markdown"/"16_CHP-16_intro.md"
STATEMENTS=TABLES/"book-statements.jsonl"
CANDIDATES=TABLES/"entity-candidates.csv"
MENTIONS=TABLES/"mentions.csv"
BODY="chp-16:16_CHP-16_intro:l48-64"
NOTES="chp-16:16_CHP-16_intro:l69-89"
SUFFIX=".bak-s2-chp16-p377-semantic-repair-before-20261009"
EXPECTED={
    STATEMENTS:"6bda79563e9c18cdfa6535ca0b3be59c92abd8ab00252cec32af2610974ac8c1",
    CANDIDATES:"2537214e17c0ccbf40d20112bbd956440b5a07fddd53a57148d5213f3aa0090f",
    MENTIONS:"d9417f310c8288c8924f66a7a702c76c1644b0dec879d08a7d91cdd95cf08f52",
}
parser=argparse.ArgumentParser()
parser.add_argument("--apply",action="store_true")
args=parser.parse_args()
for path,expected in EXPECTED.items():
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    if actual!=expected: raise SystemExit(f"unexpected baseline for {path.relative_to(ROOT)}: {actual}")

source=SOURCE.read_text(encoding="utf-8-sig").splitlines()
body="\n".join(source[47:64])
notes="\n".join(source[68:89])
with STATEMENTS.open(encoding="utf-8-sig") as f: statements=[json.loads(x) for x in f if x.strip()]
with CANDIDATES.open(encoding="utf-8-sig",newline="") as f:
    cr=csv.DictReader(f); candidate_fields=cr.fieldnames; candidates=list(cr)
with MENTIONS.open(encoding="utf-8-sig",newline="") as f:
    mr=csv.DictReader(f); mention_fields=mr.fieldnames; mentions=list(mr)
S={x["statement_id"]:x for x in statements}
C={x["candidate_id"]:x for x in candidates}
M={x["mention_id"]:x for x in mentions}

sid="st-chp16-p377-swajer-in-touch-with-gian-domenico-tiepolo"
if S[sid]["qualifiers"]["source_line_end"]!=49:
    raise SystemExit("unexpected Gian Domenico statement line range")
S[sid]["qualifiers"]["source_line_end"]=50
if "Gian\nDomenico" not in body: raise SystemExit("two-line name anchor changed")

cid="cand-11552"
if C[cid]["candidate_source_ref"]!=f"{BODY}#L57-L58":
    raise SystemExit("unexpected group-candidate source reference")
C[cid]["candidate_source_ref"]=f"{BODY}#L57"

mid="m-chp16-p377-celotti-0068"
m=M[mid]
old=(m["surface_form"],m["start_char"],m["end_char"])
surface="also Piazzettas"
positions=[i for i in range(len(notes)) if notes.startswith(surface,i)]
if len(positions)!=1: raise SystemExit(f"expected one group phrase, found {len(positions)}")
start=positions[0]
m.update({"surface_form":surface,"start_char":str(start),"end_char":str(start+len(surface))})

for row in statements:
    if row.get("statement_id")==sid:
        if row["original_quote"] not in body:
            if " ".join(row["original_quote"].split()) not in " ".join(body.split()):
                raise SystemExit("Gian Domenico quote no longer matches p.377 source")
for row in mentions:
    if row.get("segment_id") not in (BODY,NOTES): continue
    text=body if row["segment_id"]==BODY else notes
    a,b=int(row["start_char"]),int(row["end_char"])
    if text[a:b]!=row["surface_form"]: raise SystemExit(f"mention span mismatch: {row['mention_id']}")
if C[cid]["candidate_source_ref"] not in (f"{BODY}#L57",f"{BODY}#L57-L58"):
    raise SystemExit("candidate source reference did not resolve")
print("repair plan: source line 49-50, candidate anchor L57, nested phrase mention 'also Piazzettas'")
print("mention prior span:",old)
print("mention corrected span:",(m["surface_form"],m["start_char"],m["end_char"]))
print("all p.377 mention spans now match source text")

def write_csv(path,fields,rows):
    with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="",dir=path.parent,delete=False) as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n")
        w.writeheader(); w.writerows(rows); tmp=Path(f.name)
    tmp.replace(path)

if args.apply:
    backups=[]
    for path in (STATEMENTS,CANDIDATES,MENTIONS):
        backup=path.with_name(path.name+SUFFIX)
        if backup.exists(): raise SystemExit(f"refusing to overwrite {backup}")
        shutil.copy2(path,backup); backups.append(backup)
    with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="",dir=STATEMENTS.parent,delete=False) as f:
        for row in statements: f.write(json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n")
        tmp=Path(f.name)
    tmp.replace(STATEMENTS)
    write_csv(CANDIDATES,candidate_fields,candidates)
    write_csv(MENTIONS,mention_fields,mentions)
    print("applied; recovery copies:")
    for backup in backups: print(backup.relative_to(ROOT))
else:
    print("dry-run only; pass --apply to write")
