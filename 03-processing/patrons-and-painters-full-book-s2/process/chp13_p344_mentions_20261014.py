#!/usr/bin/env python3
"""Restore p.344 source-segment entity mentions omitted from the earlier migration."""
from __future__ import annotations

import argparse,csv,hashlib,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
TABLES=ROOT/"04-knowledge"/"tables"
MENTIONS=TABLES/"mentions.csv"
CANDIDATES=TABLES/"entity-candidates.csv"
SOURCE=ROOT/"02-sources"/"02-Markdown"/"13_CHP-13_intro.md"
SEGMENT="chp-13:13_CHP-13_intro:l116-122"
SUFFIX=".bak-s2-ch13-p344-mentions-20261014"
EXPECTED="5ad71906d0a7ce6124152752638cff837c7b65e80ec38245fb117eb5c348e89d"

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def main()->None:
 ap=argparse.ArgumentParser();ap.add_argument("--apply",action="store_true");args=ap.parse_args()
 if sha(MENTIONS)!=EXPECTED:raise SystemExit(f"precondition failed: mentions.csv sha256={sha(MENTIONS)}")
 source=SOURCE.read_text(encoding="utf-8").splitlines()
 text="\n".join(source[115:122])
 with MENTIONS.open(encoding="utf-8-sig",newline="") as f:
  reader=csv.DictReader(f);headers=list(reader.fieldnames or []);rows=list(reader)
 if any(row.get("segment_id")==SEGMENT for row in rows):raise SystemExit("p.344 already has mention rows")
 with CANDIDATES.open(encoding="utf-8-sig",newline="") as f:
  candidates={row["candidate_id"] for row in csv.DictReader(f)}
 # (candidate, exact S0 surface, note, occurrence index or None for all occurrences)
 specs=[
  ("cand-10104","his plates","Anaphoric reference to the plates of Delle Antiche Statue Greche e Romane, named at the end of p.343.",None),
  ("cand-2838","he showed still further awareness","A. M. Zanetti is the subject carried over from the preceding page.",None),
  ("cand-2838","his own","Possessive reference to A. M. Zanetti before the collection description.",None),
  ("cand-10113","collection of-gems and medals","The source collection catalogued by the Dactyliotheca; retain the S0 OCR hyphen.",None),
  ("cand-10012","Dactyliotheca Ant. M. Zanetti","The 1749 illustrated catalogue named by Haskell.",None),
  ("cand-2838","Zanetti","Person named or referred to as the owner, author, or subject in this passage.",None),
  ("cand-10012","the catalogue","Anaphoric reference to the Dactyliotheca.",None),
  ("cand-0025","Albrizzi","Publisher named for the Dactyliotheca.",None),
  ("cand-1041","Florentine","Geographic adjective describing Francesco Gori.",None),
  ("cand-10105","Francesco Gori","Writer of the Latin commentary; identity remains pending.",None),
  ("cand-10012","an Italian translation","The translation provided for broader readership; no separate edition is identified.",None),
  ("cand-10012","the book","Anaphoric references to the Dactyliotheca in the dedication and purpose account.",None),
  ("cand-10106","the King of Poland","Unnamed dedicatee considered first; no identity is inferred.",None),
  ("cand-7492","Poland","Country in the unnamed king's title.",None),
  ("cand-10107","the Queen of Sweden","Unnamed dedicatee eventually chosen; the text does not establish a printed dedication.",None),
  ("cand-2838","Zanetti wrote","Attribution of the reported purpose statement.",None),
  ("cand-2838","his friends","Possessive reference to Zanetti's friends.",None),
  ("cand-4653","Paris","Place used in Haskell's comparison with the company Zanetti might have had there.",None),
  ("cand-2719","Venice","Place named in the quotation about foreigners unable to see Zanetti's medals.",None),
  ("cand-10113","medals","Objects in Zanetti's collection referred to in the quoted purpose statement.",None),
  ("cand-10012","the magnificent volume","Haskell's description of the Dactyliotheca.",None),
  ("cand-2838","at his own expense","Haskell's statement about Zanetti paying the publication expense.",None),
  ("cand-10012","sale catalogue","Haskell's interpretation of the volume's function.",None),
  ("cand-0789","Abbé Clement’s","Source OCR omits the accent in Clement; the print reads Clément.",None),
  ("cand-2838","Zanetti as","Subject of Clement's quoted description.",None),
  ("cand-2838","Zanetti himself","Person introduced as a painter and caricaturist.",None),
  ("cand-2838","his own pleasure","Purpose attributed to Zanetti's painting.",None),
  ("cand-10108","caricatures of the leading operatic figures of the day","Unnamed group of caricatures; individual sitters and titles are not supplied.",None),
  ("cand-2838","his revival of wood chiaroscuro","Practice attributed to Zanetti; linked to the process candidate from p.343.",None),
  ("cand-2852","revival of wood chiaroscuro","The process/technique candidate carried over from p.343.",None),
  ("cand-2838","him","Rosalba Carriera is reported to have learned much from Zanetti.",None),
  ("cand-0581","Rosalba Camera","S0 OCR reads Camera; the p.344 print reads Carriera.",None),
  ("cand-2838","important figure he must have been","Haskell's inference about Zanetti's importance to Tiepolo.",None),
  ("cand-10109","Vari Capriccj","S0 OCR reads Capriccj; the print reads Vari Capricci.",None),
  ("cand-2838","But as a patron Zanetti","Haskell's role-specific assessment of Zanetti.",None),
  ("cand-2877","Gaetano Zompini","Zompini as the person Zanetti employed and housed.",None),
  ("cand-2838","whom he took into his house","The referent is Zompini; subject is Zanetti.",None),
  ("cand-2874","Zompini","Use the second surname occurrence for the artist who engraved the series.",1),
  ("cand-10110","engraved","Action introducing the output print series by Zompini.",1),
  ("cand-2875","series","Index subentry candidate for the Zompini print series; same identity as the body-origin series remains for S3.",None),
  ("cand-11458","Castiglione drawings","The source drawings owned by Zanetti, distinct from the resulting engravings.",None),
  ("cand-2838","belonging to Zanetti","Owner named for the Castiglione source drawings.",None),
  ("cand-2876","his masterpiece","Index subentry context for the Le Arti work; the title itself has a separate body-origin candidate.",None),
  ("cand-10111","Le Arti che vanno per via nella Città di Venezia","Zompini's named 1753 work.",None),
  ("cand-2719","Venetian artist","Place adjective for the artist described in Haskell's assessment.",None),
  ("cand-2363","Félicita Sartori","Source form for Zanetti's employed engraver and former pupil of Rosalba.",None),
  ("cand-0581","Rosalba’s pupil","Carriera is the teacher identified in the linked employment statement.",None),
  ("cand-10112","a large collection of her work","Collection of Sartori's work owned by Zanetti.",None),
  ("cand-2363","her work","Sartori is the antecedent of 'her'.",None),
  ("cand-9279","Memorie","1843 publication cited by the p.344 note 5 continuation; it was not independently consulted.",None),
  ("cand-2838","Zanetti’s rôle","The printed p.344 spelling is rôle; the statement concerns Zanetti's role as a patron.",None),
  ("cand-3461","Italy","Geographic scope in Zanetti's 1752 quoted statement.",None),
 ]
 additions=[]
 for candidate,surface,note,occurrence in specs:
  if candidate not in candidates:raise ValueError(f"missing candidate {candidate} for {surface!r}")
  starts=[];pos=0
  while True:
   i=text.find(surface,pos)
   if i<0:break
   starts.append(i);pos=i+1
  if not starts:raise ValueError(f"surface not found in exact segment: {surface!r} ({candidate})")
  if occurrence is not None:
   if occurrence>=len(starts):raise ValueError(f"occurrence {occurrence} missing for {surface!r}")
   starts=[starts[occurrence]]
  for start in starts:
   additions.append({"mention_id":"","segment_id":SEGMENT,"candidate_id":candidate,"surface_form":surface,
                     "start_char":str(start),"end_char":str(start+len(surface)),"note":note})
 additions.sort(key=lambda r:(int(r["start_char"]),-int(r["end_char"]),r["candidate_id"]))
 # Keep the broadest same-candidate mention for a nested duplicate; reject exact
 # duplicate or crossing spans across candidates because each surface needs one mapping.
 filtered=[]
 for row in additions:
  start,end=int(row["start_char"]),int(row["end_char"])
  if any(p["candidate_id"]==row["candidate_id"] and int(p["start_char"])<=start and end<=int(p["end_char"]) for p in filtered):continue
  for p in filtered:
   a,b=int(p["start_char"]),int(p["end_char"])
   if start==a and end==b:raise ValueError(f"duplicate exact mention span: {row} vs {p}")
   if max(start,a)<min(end,b) and not ((start<=a and b<=end) or (a<=start and end<=b)):
    raise ValueError(f"crossing mention spans: {row} vs {p}")
  filtered.append(row)
 additions=filtered
 existing={row["mention_id"] for row in rows}
 for i,row in enumerate(additions,1):
  row["mention_id"]=f"m-s2-ch13-p344-{i:03d}"
  if row["mention_id"] in existing:raise ValueError(f"mention id collision: {row['mention_id']}")
  start,end=int(row["start_char"]),int(row["end_char"])
  if text[start:end]!=row["surface_form"]:raise ValueError(f"offset mismatch: {row}")
 rows.extend(additions)
 print(f"p344 mentions: 0 -> {len(additions)}; candidate references={len({r['candidate_id'] for r in additions})}; exact spans and non-crossing offsets pass")
 if not args.apply:
  print("DRY-RUN only; no tables changed");return
 backup=MENTIONS.with_name(MENTIONS.name+SUFFIX)
 if backup.exists():raise SystemExit(f"recovery copy exists: {backup.name}")
 shutil.copy2(MENTIONS,backup)
 from io import StringIO
 out=StringIO(newline="");writer=csv.DictWriter(out,fieldnames=headers,lineterminator="\n");writer.writeheader();writer.writerows(rows)
 MENTIONS.write_bytes(("\ufeff"+out.getvalue()).encode("utf-8"))
 print(f"wrote {MENTIONS.relative_to(ROOT)} sha256={sha(MENTIONS)}")
 print(f"recovery copy: {backup.name}")

if __name__=="__main__":main()
