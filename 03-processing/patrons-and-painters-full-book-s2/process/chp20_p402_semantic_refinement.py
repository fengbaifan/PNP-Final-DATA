#!/usr/bin/env python3
"""Refine two over-specific p.402 candidates and correct claim endpoints."""
import argparse,csv,hashlib,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
T=ROOT/"04-knowledge"/"tables"
SRC=ROOT/"02-sources"/"02-Markdown"/"20_CHP-20Postscript.md"
P="chp-20:20_CHP-20Postscript:l98-108"
TURNER="st-chp20-p402-turner-ferrante-carlo-bellori-lanfranco"
MAZARIN="st-chp20-p402-mazarin-art-policy-in-france"
REMOVE_MENTION="m-chp20-p402-029"
BACKUP=".bak-s2-chp20-p402-semantic-refinement-20261004"
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
cp,candidates=rcsv(T/"entity-candidates.csv")
mp,mentions=rcsv(T/"mentions.csv")
sp=T/"book-statements.jsonl"
statements=[json.loads(x) for x in sp.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
cb={r["candidate_id"]:r for r in candidates}
old_name="Italian Baroque artists introduced into France under Richelieu and Mazarin (unnamed group)"
removed_name="Finest examples of Italian Baroque art sought for France by Mazarin (unnamed group)"
if cb.get("cand-10986",{}).get("canonical_name")!=old_name:raise SystemExit("candidate cand-10986 changed")
if cb.get("cand-10987",{}).get("canonical_name")!=removed_name:raise SystemExit("candidate cand-10987 changed")
if cb["cand-10986"]["status"]!="open" or cb["cand-10987"]["status"]!="open":raise SystemExit("candidate status changed")
new_key=("italian baroque artists","term")
if any((r["canonical_name"].strip().casefold(),r["suggested_type"].strip().casefold())==new_key and r["candidate_id"]!="cand-10986" for r in candidates):
    raise SystemExit("natural-key collision for Italian Baroque artists")
candidate_refs=[r["candidate_id"] for r in mentions if r["candidate_id"]=="cand-10987"]
if candidate_refs!=["cand-10987"]:raise SystemExit("unexpected references to cand-10987 in mentions")
to_remove=next((r for r in mentions if r["mention_id"]==REMOVE_MENTION),None)
if not to_remove or to_remove["segment_id"]!=P or to_remove["candidate_id"]!="cand-10987":
    raise SystemExit("target unnamed-work mention changed")
if to_remove["surface_form"]!="finest examples of Italian Baroque art":raise SystemExit("mention surface changed")
target_turner=next((r for r in statements if r["statement_id"]==TURNER),None)
target_mazarin=next((r for r in statements if r["statement_id"]==MAZARIN),None)
if not target_turner or (target_turner["subject_candidate_id"],target_turner["object_candidate_id"])!=("cand-10984","cand-10983"):
    raise SystemExit("Turner claim endpoints changed")
if not target_mazarin or "cand-10987" not in target_mazarin["qualifiers"]["mentioned_candidate_ids"]:
    raise SystemExit("Mazarin statement no longer references unnamed-work candidate")
if any("cand-10987" in r.get("qualifiers",{}).get("mentioned_candidate_ids",[]) for r in statements if r["statement_id"]!=MAZARIN):
    raise SystemExit("unexpected statement reference to cand-10987")
cb["cand-10986"]["canonical_name"]="Italian Baroque artists"
cb["cand-10986"]["detail"]="The source uses this as a category of artists; it identifies no individual artists in this passage."
candidates=[r for r in candidates if r["candidate_id"]!="cand-10987"]
mentions=[r for r in mentions if r["mention_id"]!=REMOVE_MENTION]
target_turner["subject_candidate_id"]="cand-0272"
target_turner["predicate"]="bellori_lanfranco_comments_derived_from_ferrante_carlo"
target_turner["qualifiers"]["claim"]="Haskell reports Nicholas Turner's demonstration that some of Bellori's most famous critical comments on Lanfranco were very closely derived from Ferrante Carlo's writing; Haskell says he had not fully appreciated Carlo's significance when writing about him in chapter 5."
target_mazarin["qualifiers"]["mentioned_candidate_ids"].remove("cand-10987")
paths=[T/"entity-candidates.csv",T/"mentions.csv",sp]
backups=[p.with_name(p.name+BACKUP) for p in paths]
if args.apply:
    if any(p.exists() for p in backups):raise SystemExit("recovery backup already exists")
    for p,b in zip(paths,backups):shutil.copy2(p,b)
    wcsv(paths[0],cp,candidates);wcsv(paths[1],mp,mentions);wjson(paths[2],statements)
    print(f"applied p.402 semantic refinement; backup suffix {BACKUP}")
else:
    print("DRY RUN: no files written")
    print("retain cand-10986 as the general term Italian Baroque artists")
    print("remove the unnamed-work group candidate and its redundant mention")
    print("set the Turner-reported claim endpoints to Bellori and Ferrante Carlo")
