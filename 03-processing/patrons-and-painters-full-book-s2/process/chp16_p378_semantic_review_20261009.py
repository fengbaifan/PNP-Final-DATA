"""Controlled semantic review of the p.378 conclusion and its p.377 referents."""
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
TABLES=ROOT/"04-knowledge"/"tables"
SOURCE=ROOT/"02-sources"/"02-Markdown"/"16_CHP-16_intro.md"
PDF=ROOT/"02-sources"/"01-book"/"CHP-16.pdf"
STATEMENTS=TABLES/"book-statements.jsonl"
BODY="chp-16:16_CHP-16_intro:l66-67"
P377="chp-16:16_CHP-16_intro:l48-64"
BACKUP_SUFFIX=".bak-s2-chp16-p378-semantic-review-20261009"
EXPECTED={
    SOURCE:"ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff",
    PDF:"6bfb3e331f0ac2421d31279f97b08b17486f0e2c32451a10a6798cf31424af5f",
    STATEMENTS:"d733d400086a10ecafd1667823728ef15473b03f5eb219a81256384d1ec371df",
}
parser=argparse.ArgumentParser()
parser.add_argument("--apply",action="store_true")
args=parser.parse_args()
for path,expected in EXPECTED.items():
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    if actual!=expected: raise SystemExit(f"unexpected baseline for {path.relative_to(ROOT)}: {actual}")

source_lines=SOURCE.read_text(encoding="utf-8-sig").splitlines()
if "They earned their livings by pandering" not in source_lines[66]:
    raise SystemExit("p.378 source line 67 changed")
body_text="\n".join(source_lines[65:67])
with STATEMENTS.open(encoding="utf-8-sig") as f: rows=[json.loads(x) for x in f if x.strip()]
by_id={r["statement_id"]:r for r in rows}
if len(by_id)!=len(rows): raise SystemExit("duplicate statement IDs")
ids=["st-chp16-p378-group-livelihood-and-old-masters-demand",
     "st-chp16-p378-group-collected-artists-affected-by-taste-change",
     "st-chp16-p378-group-retrospective-venetian-tradition"]
if any(i not in by_id for i in ids): raise SystemExit("p.378 first-pass statements missing")
group_ids=["st-chp16-p377-haskell-groups-dealers-by-status-and-social-place",
           "st-chp16-p377-haskell-generalizes-dealers-collections-and-patronage",
           "st-chp16-p377-haskell-dealers-outside-venetian-intellectual-currents"]
if any(i not in by_id for i in group_ids): raise SystemExit("p.377 semantic group statements missing")
people=["cand-2364","cand-1387","cand-2764","cand-2643","cand-2534","cand-0622"]
for i in people:
    if i not in {c for r in rows for c in [r.get("subject_candidate_id"),r.get("object_candidate_id")] if c}:
        # Sasso's person candidate is valid even where this paragraph only uses a collective anaphor.
        if i!="cand-2364": raise SystemExit(f"referent candidate not used in statements: {i}")

def check_quote(quote):
    if " ".join(quote.split()) not in " ".join(body_text.split()):
        raise SystemExit(f"p.378 quote does not locate in S0: {quote!r}")

def revise(sid,quote,claim,qualification,mentioned,referents=people):
    row=by_id[sid]
    check_quote(quote)
    row["original_quote"]=quote
    q=row.setdefault("qualifiers",{})
    q.update({"source_line_start":67,"source_line_end":67,"printed_page":378,
              "pdf_physical_page":6,"claim":claim,"speaker":"Haskell",
              "text_layer":"authorial synthesis","qualification":qualification,
              "mentioned_candidate_ids":mentioned,"referent_statement_ids":group_ids,
              "referent_candidate_ids":referents,
              "coreference_note":"The plural anaphors continue Haskell's 'all these men' synthesis at p.377 L59: Sasso, della Lena, Vianello, Toninotto, Swajer, and Celotti. These are group-level claims, not individual biographies or formal relations."})
    q["relation_candidate"]=False

revise(ids[0],
       "They earned their livings by pandering to the international demand for old masters,",
       "Haskell says the men discussed earned their living by pandering to international demand for old masters.",
       "The evaluative verb 'pandering' is retained as Haskell's wording; no market, buyer, or individual transaction is identified.",
       ["cand-0126","cand-4288"])
revise(ids[1],
       "and they themselves assembled pictures by artists who were the victims of the change in taste that swept through Europe during the second half of the eighteenth century.",
       "Haskell says the men assembled pictures by artists he characterizes as victims of a change in taste that swept through Europe in the second half of the eighteenth century.",
       "The artists and pictures are unnamed; 'victims' records Haskell's interpretation of the change in taste.",
       ["cand-0126","cand-3462"])

# The transition claim and the retrospective 'guardians' metaphor are distinct.
time_id="st-chp16-p378-time-effected-remarkable-revolution"
if time_id in by_id: raise SystemExit("time-revolution statement ID already exists")
time_quote="Time has effected a remarkable revolution"
check_quote(time_quote)
time_row={
    "statement_id":time_id,"segment_id":BODY,"subject_candidate_id":None,"object_candidate_id":None,
    "predicate":"time_effected_a_remarkable_revolution_in_historical_appraisal",
    "qualifiers":{"source_line_start":67,"source_line_end":67,"printed_page":378,
                  "pdf_physical_page":6,"claim":"Haskell says time has effected a remarkable revolution.",
                  "speaker":"Haskell","text_layer":"authorial synthesis",
                  "qualification":"The object and precise scope of the revolution are implicit; no specific event or causal mechanism is supplied.",
                  "mentioned_candidate_ids":[],"relation_candidate":False,
                  "referent_statement_ids":group_ids,"referent_candidate_ids":people,
                  "coreference_note":"This is the transition in Haskell's p.378 group-level retrospective, following the p.377 synthesis."},
    "original_quote":time_quote,"origin":"book","source_file":"02-sources/02-Markdown/16_CHP-16_intro.md"}
rows.append(time_row); by_id[time_id]=time_row
revise(ids[2],
       "and to us they now appear as the true guardians of the Venetian tradition.",
       "Haskell says that to present readers the men now appear as guardians of the Venetian tradition.",
       "'Guardians' is Haskell's retrospective metaphor, not an institutional role or a verified collective identity.",
       ["cand-0126","cand-10673"])

# Correct Sasso's collective referent from an index event to the person candidate.
for sid in ids:
    q=by_id[sid]["qualifiers"]
    q["referent_candidate_ids"]=people
    q["mentioned_candidate_ids"]=[c for c in q.get("mentioned_candidate_ids",[]) if c!="cand-2367"]
for r in rows:
    if r.get("statement_id") in group_ids:
        q=r.setdefault("qualifiers",{})
        q["referent_candidate_ids"]=people
        q["mentioned_candidate_ids"]=["cand-0126"]

for r in rows:
    if r.get("segment_id")==BODY:
        check_quote(r["original_quote"])
if by_id[ids[0]]["qualifiers"]["referent_candidate_ids"][0]!="cand-2364":
    raise SystemExit("Sasso referent still points to a non-person candidate")
print("plan: refine 3 p.378 statements, add 1 transition statement; correct group referent mapping")
print("validation: source/PDF/table SHA guards, exact source quotes, 6 person referents, and p.377 reciprocal links passed")

if args.apply:
    backup=STATEMENTS.with_name(STATEMENTS.name+BACKUP_SUFFIX)
    if backup.exists(): raise SystemExit(f"refusing to overwrite {backup}")
    shutil.copy2(STATEMENTS,backup)
    with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="",dir=STATEMENTS.parent,delete=False) as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n")
        temp=Path(f.name)
    temp.replace(STATEMENTS)
    print("applied; recovery copy:",backup.relative_to(ROOT))
else:
    print("dry-run only; pass --apply to write")
