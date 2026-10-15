"""Single-field line-boundary correction after p.371 semantic re-audit."""
import argparse, csv, hashlib, json, shutil, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PATH=ROOT/"04-knowledge/tables/book-statements.jsonl"
SOURCE=ROOT/"02-sources/02-Markdown/15_CHP-15_sec_ii.md"
EXPECTED_SHA="5b9ac1aae939b0813786417757a82c3b7f3b40d3420895536f0a04a177a01373"
SID="st-chp15-p371-pliny-recorded-apelles-composition"
QUOTE="composition of\nApelles as recorded by Pliny"
p=argparse.ArgumentParser(); p.add_argument("--apply",action="store_true"); a=p.parse_args()
if hashlib.sha256(PATH.read_bytes()).hexdigest()!=EXPECTED_SHA: raise SystemExit("book-statements changed after reviewed snapshot")
lines=SOURCE.read_text(encoding="utf-8-sig").splitlines()
if QUOTE not in "\n".join(lines[68:83]): raise SystemExit("quoted source changed")
rows=[json.loads(x) for x in PATH.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
found=[r for r in rows if r.get("statement_id")==SID]
if len(found)!=1: raise SystemExit("statement missing or duplicated")
r=found[0]; q=r.get("qualifiers",{})
if q.get("source_line_start")!=73 or q.get("source_line_end")!=73: raise SystemExit("unexpected current line range")
print({"mode":"apply" if a.apply else "dry-run","statement_id":SID,"old_lines":[73,73],"new_lines":[72,73]})
if not a.apply: raise SystemExit(0)
backup=PATH.with_name(PATH.name+".bak-s2-chp15-p371-linefix-20261009")
if backup.exists(): raise SystemExit(f"backup already exists: {backup}")
shutil.copy2(PATH,backup)
q["source_line_start"]=72; q["source_line_end"]=73
with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="",dir=PATH.parent,delete=False) as f:
    for row in rows: f.write(json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n")
    tmp=Path(f.name)
tmp.replace(PATH)
print("applied line-boundary correction; recovery copy created")
