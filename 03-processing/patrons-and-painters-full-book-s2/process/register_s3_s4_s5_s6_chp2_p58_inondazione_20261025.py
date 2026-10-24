#!/usr/bin/env python3
"""Guarded S3/S4/S5/S6 registration and S2 correction for Bernini's Inondazione batch."""
from __future__ import annotations
import argparse, csv, hashlib, io, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
T = ROOT / "04-knowledge" / "tables"
PROC = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
ANCHOR = "s3-s4-s5-s6-chp2-p58-inondazione-20261025"
PREF = f"{PROC}#{ANCHOR}"
SRC = "02-sources/02-Markdown/02_CHP-2_sec_iv.md"
PERSON = "units/persons/gian-lorenzo-bernini"
PLACE = "units/places/bernini-provisional-theatre-outside-house"
WORK = "units/works/inondazione-del-tevere-bernini-play"
EVENT = "units/events/inondazione-del-tevere-performance-carnival-1638"
FLOOD = "units/events/prior-year-flood-said-to-inspire-bernini-play"
PLACE_CARD = "04-knowledge/units/places/bernini-provisional-theatre-outside-house.md"
WORK_CARD = "04-knowledge/units/works/inondazione-del-tevere-bernini-play.md"
RECOVERY = ROOT / "06-runtime/recovery/p58-inondazione-pre-apply-20261025"

def read_csv(path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    nl = "\r\n" if "\r\n" in text else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if not reader.fieldnames: raise SystemExit(f"missing CSV header: {path}")
    return list(reader.fieldnames), list(reader), bom, nl

def write_csv(headers, rows, bom, nl):
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=headers, extrasaction="ignore", lineterminator=nl)
    w.writeheader(); w.writerows(rows)
    data = buf.getvalue().encode("utf-8")
    return b"\xef\xbb\xbf" + data if bom else data

def make_statement(sid, subject, obj, predicate, claim, qualification, quote, start=186, end=186):
    return {
        "statement_id": sid, "segment_id": "chp-2:02_CHP-2_sec_iv:l181-188",
        "subject_candidate_id": subject, "object_candidate_id": obj, "predicate": predicate,
        "qualifiers": {
            "speaker": "Haskell, unless a nested speaker is specified", "text_layer": "authorial narrative",
            "print_page": 58, "pdf_physical_page": 47, "source_line_start": start, "source_line_end": end,
            "claim": claim, "qualification": qualification, "relation_candidate": True,
            "relation_candidate_note": "Source-supported relation candidate; S6 status and type are adjudicated in the linked process record."
        },
        "original_quote": quote, "origin": "book", "source_file": SRC
    }

def make_relation(rid, subject, predicate, obj, time, role, scope, statements, note):
    return {
        "relation_id": rid, "subject_ku_id": subject, "object_ku_id": obj, "predicate": predicate,
        "time": time, "role": role, "scope": scope, "origin": "book", "status": "formal",
        "source_id": "haskell-1980-rev-ed",
        "source_span": f"Chapter 2, printed p.58, L185–186; statements={';'.join(statements)}",
        "source_file": SRC, "note": note
    }

def make_card(text):
    return text.strip().encode("utf-8") + b"\n"

def update_schema(types, ranges):
    if not types.startswith("version: 3\n") or not ranges.startswith("version: 2\n"):
        raise SystemExit("relation schema version changed; inspect before applying")
    for ty in ("directed_by", "director_of", "has_performance", "performance_of", "inspired_by", "inspiration_for"):
        if f"  - {ty}\n" in types: raise SystemExit(f"relation type already exists: {ty}")
    types = types.replace("version: 3\n", "version: 4\n", 1)
    types = types.replace("  - designed_by\n", "  - designed_by\n  - directed_by\n  - director_of\n", 1)
    types = types.replace("  - has_participant\n", "  - has_participant\n  - has_performance\n", 1)
    types = types.replace("  - influenced_by\n", "  - influenced_by\n  - inspired_by\n  - inspiration_for\n", 1)
    types = types.replace("  - parent_of\n", "  - parent_of\n  - performance_of\n", 1)
    types = types.replace("  designed_by: designer_of\n", "  designed_by: designer_of\n  directed_by: director_of\n  director_of: directed_by\n", 1)
    types = types.replace("  influenced_by: influenced\n", "  influenced_by: influenced\n  has_performance: performance_of\n  performance_of: has_performance\n  inspired_by: inspiration_for\n  inspiration_for: inspired_by\n", 1)
    ranges = ranges.replace("version: 2\n", "version: 3\n", 1)
    ranges = ranges.replace("authority: relation-domain-range-v2", "authority: relation-domain-range-v3", 1)
    ranges = ranges.replace("status: draft-v2", "status: draft-v3", 1)
    ranges = ranges.replace("  designed_by:      {domain: [work], range: [person]}\n", "  designed_by:      {domain: [work], range: [person]}\n  directed_by:      {domain: [work], range: [person]}\n  director_of:      {domain: [person], range: [work]}\n", 1)
    ranges = ranges.replace("  erected_by:        {domain: [work], range: [person]}\n", "  erected_by:        {domain: [place, work], range: [person]}\n", 1)
    ranges = ranges.replace("  erector_of:        {domain: [person], range: [work]}\n", "  erector_of:        {domain: [person], range: [place, work]}\n", 1)
    ranges = ranges.replace("  has_participant:  {domain: [event], range: [institution, person]}\n", "  has_participant:  {domain: [event], range: [institution, person]}\n  has_performance:  {domain: [work], range: [event]}\n", 1)
    ranges = ranges.replace("  influenced_by:    {domain: [person, work], range: [person, term, work]}\n", "  influenced_by:    {domain: [person, work], range: [person, term, work]}\n  inspired_by:      {domain: [work], range: [event]}\n  inspiration_for:  {domain: [event], range: [work]}\n", 1)
    ranges = ranges.replace("  part_of:          {domain: [archive, institution, place, work], range: [archive, institution, place, work]}\n", "  part_of:          {domain: [archive, institution, place, work], range: [archive, institution, place, work]}\n  performance_of:   {domain: [event], range: [work]}\n", 1)
    for term in ("directed_by:", "director_of:", "has_performance:", "inspired_by:", "inspiration_for:", "performance_of:"):
        if term not in ranges: raise SystemExit(f"missing domain/range entry: {term}")
    return types, ranges

def insert_accepted(text, paths):
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    for path in paths:
        entry = f"- {path}"
        if entry in lines: raise SystemExit(f"accepted path already exists: {path}")
        i = next((i for i, line in enumerate(lines) if line.startswith("- ") and line[2:].casefold() > path.casefold()), len(lines))
        lines.insert(i, entry)
    return (nl.join(lines) + nl).encode("utf-8")

def preflight():
    source = (ROOT / SRC).read_text(encoding="utf-8-sig")
    for fragment in ("the provisional theatre which", "Bernini erected outside his own house",
                     "the most famous of which was L'Inondazione del Tevere given during the carnival of 1638",
                     "inspired by a flood of the year before"):
        if fragment not in source: raise SystemExit(f"source evidence changed: {fragment}")

    cp = T / "entity-candidates.csv"
    ch, candidates, cbom, cnl = read_csv(cp)
    c = {r["candidate_id"]: r for r in candidates}
    expected = {"cand-4819": "place", "cand-4820": "archive", "cand-4821": "archive", "cand-4824": "archive"}
    for cid, typ in expected.items():
        if cid not in c or c[cid]["suggested_type"] != typ: raise SystemExit(f"candidate changed: {cid}")
    ap = T / "alignment.csv"
    ah, alignments, abom, anl = read_csv(ap)
    a = {r["candidate_id"]: r for r in alignments}
    if a["cand-4819"]["decision"] != "undecided" or a["cand-4819"]["ku_id"]: raise SystemExit("cand-4819 alignment changed")
    if a["cand-4821"]["decision"] != "new" or a["cand-4821"]["ku_id"]: raise SystemExit("cand-4821 alignment changed")
    if a["cand-4820"]["decision"] != "undecided" or a["cand-4824"]["decision"] != "undecided": raise SystemExit("pending candidate decision changed")
    for cid, ku in {"cand-0296": PERSON, "cand-4822": EVENT, "cand-4823": FLOOD}.items():
        if not a.get(cid) or a[cid]["ku_id"] != ku: raise SystemExit(f"existing endpoint missing: {cid}")
    mp = T / "ku-manifest.csv"
    mh, manifest, mbom, mnl = read_csv(mp)
    if any(r["ku_id"] in (PLACE, WORK) for r in manifest): raise SystemExit("target KU already in manifest")
    if (ROOT/PLACE_CARD).exists() or (ROOT/WORK_CARD).exists(): raise SystemExit("target card already exists")

    sp = T / "book-statements.jsonl"
    raw = sp.read_bytes(); sbom = raw.startswith(b"\xef\xbb\xbf")
    stxt = raw.decode("utf-8-sig"); snl = "\r\n" if "\r\n" in stxt else "\n"
    slines = stxt.splitlines()
    parsed = [json.loads(x) for x in slines if x.strip()]
    s = {r["statement_id"]: r for r in parsed}
    built_id = "st-chp2-seciv-l181-188-bernini-built-provisional-theatre"
    group_id = "st-chp2-seciv-l181-188-bernini-wrote-and-directed-play-group"
    spectator_id = "st-chp2-seciv-l181-188-anonymous-spectator-describes-staged-flood"
    perf_id = "st-chp2-seciv-l181-188-inondazione-performed-carnival-1638"
    inspired_id = "st-chp2-seciv-l181-188-play-inspired-by-prior-year-flood"
    accounts_id = "st-chp2-seciv-l181-188-spectator-accounts-used-because-no-drawings-survive"
    originals = {built_id, group_id, spectator_id, perf_id, inspired_id, accounts_id}
    if not originals.issubset(s): raise SystemExit("p.58 source statements changed")
    new_ids = [
        "st-chp2-seciv-l181-188-bernini-wrote-play-group",
        "st-chp2-seciv-l181-188-bernini-often-acted-in-play-group",
        "st-chp2-seciv-l181-188-bernini-authored-inondazione",
        "st-chp2-seciv-l181-188-bernini-directed-inondazione",
        "st-chp2-seciv-l181-188-inondazione-performance-at-provisional-theatre",
    ]
    if any(i in s for i in new_ids): raise SystemExit("planned S2 statement already exists")
    if s[spectator_id]["object_candidate_id"] != "cand-4817": raise SystemExit("anonymous spectator object changed")

    replacements = {}
    built = dict(s[built_id]); q = dict(built["qualifiers"])
    q.update({"claim":"Haskell says Bernini erected a provisional theatre outside his own house.",
              "qualification":"The house and exact site are unnamed; this claim records the venue's construction only.",
              "source_line_start":185,"source_line_end":186})
    built["qualifiers"] = q; built["original_quote"] = "the provisional theatre which Bernini erected outside his own house"
    replacements[built_id] = built

    group = dict(s[group_id]); q = dict(group["qualifiers"])
    q.update({"claim":"Haskell says Bernini directed plays at the provisional theatre outside his house.",
              "qualification":"This statement covers directing only; authorship and acting are represented separately. The group has no complete title or membership boundary.",
              "relation_candidate_note":"The generic group candidate has no bounded title list; keep S6 pending unless its identity and scope are resolved."})
    group.update({"qualifiers":q,"predicate":"directed-plays-at-provisional-theatre","original_quote":"Here he directed plays"})
    replacements[group_id] = group

    spectator = dict(s[spectator_id])
    spectator["object_candidate_id"] = "cand-4822"
    q = dict(spectator["qualifiers"])
    q.update({"claim":"An unnamed contemporary spectator describes the staged flood effects in the Carnival 1638 performance of L’Inondazione del Tevere.",
              "qualification":"The Tiber rising, dyke failures and water approaching the auditorium are theatrical effects, not a real flood or actual danger.",
              "relation_candidate_note":"The quoted spectator account is not independently identified; the represented scene belongs to the 1638 performance event, not S. Alessio's scenic tableaux."})
    spectator["qualifiers"] = q; replacements[spectator_id] = spectator

    additions = [
        make_statement(new_ids[0],"cand-0296","cand-4820","wrote-plays-in-group","Haskell says Bernini wrote the plays later directed at the provisional theatre.","The statement concerns an unbounded group; titles and full membership are not supplied.","plays written (and often acted) by himself"),
        make_statement(new_ids[1],"cand-0296","cand-4820","often-acted-in-plays-in-group","Haskell says Bernini often acted in the plays he directed; this does not attribute acting in every individual play.","The statement concerns an unbounded group; titles and full membership are not supplied.","plays written (and often acted) by himself"),
        make_statement(new_ids[2],"cand-0296","cand-4821","authored-this-play","By 'the most famous of which', Haskell identifies L’Inondazione del Tevere as one of the plays Bernini wrote.","The work's authorship follows the antecedent 'plays written ... by himself'; no edition or surviving copy is identified.","Here he directed plays written (and often acted) by himself, the most famous of which was L'Inondazione del Tevere"),
        make_statement(new_ids[3],"cand-0296","cand-4821","directed-this-play","By 'the most famous of which', Haskell identifies L’Inondazione del Tevere as one of the plays Bernini directed.","The source identifies this title within the plays Bernini directed; it does not identify another performance date beyond Carnival 1638.","Here he directed plays written (and often acted) by himself, the most famous of which was L'Inondazione del Tevere"),
        make_statement(new_ids[4],"cand-4822","cand-4819","performed-at-provisional-theatre","The contextual 'Here' places the Carnival 1638 performance of L’Inondazione del Tevere in Bernini’s provisional theatre.","The source gives the venue as outside Bernini’s own house but does not identify the house or exact site.","Here he directed plays written (and often acted) by himself, the most famous of which was L'Inondazione del Tevere given during the carnival of 1638",185,186),
    ]
    byid = {json.loads(line)["statement_id"]:(i,json.loads(line)) for i,line in enumerate(slines) if line.strip()}
    out_lines=[]; inserted=set()
    for line in slines:
        if not line.strip(): out_lines.append(line); continue
        row=json.loads(line); sid=row["statement_id"]
        if sid in replacements:
            out_lines.append(json.dumps(replacements[sid],ensure_ascii=False))
            if sid==group_id:
                out_lines.extend(json.dumps(x,ensure_ascii=False) for x in additions[:4])
                inserted.update(x["statement_id"] for x in additions[:4])
        elif sid==perf_id:
            out_lines.append(line); out_lines.append(json.dumps(additions[4],ensure_ascii=False)); inserted.add(new_ids[4])
        else: out_lines.append(line)
    if inserted != set(new_ids): raise SystemExit("statement insertion did not complete")

    c["cand-4820"]["canonical_name"]="Plays written and directed by Bernini at the provisional theatre (unbounded group)"
    c["cand-4820"]["suggested_type"]="work"
    c["cand-4820"]["detail"]="Haskell refers to plays Bernini wrote and directed at the provisional theatre; the named titles and complete group boundary are not supplied here."
    c["cand-4821"]["suggested_type"]="work"
    c["cand-4821"]["detail"]="Named theatrical play by Bernini, identified by Haskell as the most famous of the plays at the provisional theatre; performed during Carnival 1638 and said to have been inspired by a flood of the previous year."

    old=a["cand-4819"]["resolution_note"]
    a["cand-4819"].update({"decision":"new","ku_id":PLACE,"process_ref":PREF,
        "resolution_note":f"prior_resolution_note={old}; S3 endpoint decision 2026-10-25: new place identity sg3-place-cand-4819. Haskell names Bernini's provisional theatre erected outside his own house; the place identity is source-bounded although the house and exact site are unknown. No matching place KU exists. S4 registration: mapped to {PLACE}."})
    old=a["cand-4821"]["resolution_note"]
    if "archive-group-d21473654a30" not in old: raise SystemExit("prior group token changed")
    a["cand-4821"].update({"ku_id":WORK,"process_ref":PREF,
        "resolution_note":f"prior_resolution_note={old}; S3 type correction and identity decision 2026-10-25: new work identity work-group-d21473654a30. The named object is Bernini's play, distinct from performance event cand-4822 and prior-year flood event cand-4823; no same work KU exists. S4 registration: mapped to {WORK}. Prior group token corrected from archive-group-d21473654a30 to work-group-d21473654a30 because this is a play, not a publication."})
    old=a["cand-4820"]["resolution_note"]
    a["cand-4820"]["resolution_note"]=f"prior_resolution_note={old}; S3 type clarification 2026-10-25: provisional type work; decision remains undecided because the group has no supplied title list, stable membership boundary, or complete identity. S4 is withheld; resolve only if a bounded play group can be identified."
    old=a["cand-4824"]["resolution_note"]
    a["cand-4824"]["resolution_note"]=f"prior_resolution_note={old}; S3 remains undecided 2026-10-25: Haskell quotes an unnamed contemporary spectator and footnote 3 points to Fraschetti p.264, but does not establish that Fraschetti's book is the original witness or identify the quoted document's author, title, carrier, or holding. Keep the account distinct from Fraschetti's book; S4 is withheld until the original account identity or a defensible source-local account boundary is established."

    mh, manifest, mbom, mnl = read_csv(T/"ku-manifest.csv")
    if any(r["ku_id"] in (PLACE,WORK) for r in manifest): raise SystemExit("target KU already exists in manifest")
    manifest.extend([
      {"ku_id":PLACE,"type":"place","canonical_name":"Bernini’s provisional theatre outside his house","name_en":"Provisional Theatre outside Bernini’s House","source_task":"patrons-and-painters-full-book-s2","card_path":PLACE_CARD},
      {"ku_id":WORK,"type":"work","canonical_name":"L’Inondazione del Tevere","name_en":"L’Inondazione del Tevere","source_task":"patrons-and-painters-full-book-s2","card_path":WORK_CARD},
    ])

    rh, relations, rbom, rnl = read_csv(T/"relations.csv")
    formal=[
      make_relation("rel-1967",PERSON,"erector_of",PLACE,"","建造者（Haskell称由Bernini搭建）","临时剧场位于Bernini自宅之外；自宅与确切地点不详，不表示剧场现存。",[built_id],"S2 claim narrowed to the theatre's construction; no house or exact site is inferred."),
      make_relation("rel-1968",WORK,"created_by",PERSON,"","编剧／创作者（Haskell所述）","Haskell以“the most famous of which”将该剧指认为Bernini所写剧目之一；未识别版本或存世副本。",[new_ids[2]],"The author relation follows the grammatical antecedent; it does not identify an edition or surviving copy."),
      make_relation("rel-1969",WORK,"directed_by",PERSON,"","导演（Haskell所述）","该剧被指认为Bernini在自宅外临时剧场执导的剧目中最著名者。",[new_ids[3]],"The source supports directing this named play; the separate generic group remains unbounded."),
      make_relation("rel-1970",WORK,"has_performance",EVENT,"1638年狂欢节期间","演出作品","作品与该次演出是不同对象；Haskell称该剧于此时上演。",["st-chp2-seciv-l181-188-inondazione-performed-carnival-1638"],"The event is the 1638 performance, not the play itself."),
      make_relation("rel-1971",WORK,"inspired_by",FLOOD,"相对时间：演出前一年","创作灵感来源（Haskell所述）","原文只称“前一年”的一次洪水；未明确河流或精确日期。",["st-chp2-seciv-l181-188-play-inspired-by-prior-year-flood"],"Preserves the source's relative date and does not infer that the flood was the Tiber."),
      make_relation("rel-1972",EVENT,"occurred_at",PLACE,"1638年狂欢节期间","演出场所","“Here”回指Bernini在自宅外搭建的临时剧场；具体宅邸与演出空间位置未明。",[new_ids[4]],"The venue is established contextually in the same sentence; no exact address is inferred."),
    ]
    if any(r["relation_id"] in {x["relation_id"] for x in formal} for r in relations): raise SystemExit("planned relation ID already exists")
    natural={tuple(r.get(k,"").strip() for k in ("subject_ku_id","predicate","object_ku_id","time","role","scope")) for r in relations}
    for x in formal:
        key=tuple(x[k].strip() for k in ("subject_ku_id","predicate","object_ku_id","time","role","scope"))
        if key in natural: raise SystemExit(f"duplicate relation key: {x['relation_id']}")
        natural.add(key)
    relations.extend(formal)

    bh, backlog, bbom, bnl = read_csv(T/"candidate-backlog.csv")
    if any(r["candidate_id"] in ("cand-4820","cand-4824") for r in backlog): raise SystemExit("blocked candidate already in backlog")
    backlog.extend([
      {"backlog_id":"bl-0035","canonical_name":c["cand-4820"]["canonical_name"],"suggested_type":"work","status":"undecided","source_id":"haskell-1980-rev-ed","source_ref":"chp-2:02_CHP-2_sec_iv:l181-188#L186","statement_id":f"{group_id};{new_ids[0]};{new_ids[1]}","endpoint_role":"unbounded group of plays (directing, authorship, acting)","candidate_id":"cand-4820","ku_id":"","decision_note":"S3 undecided: no title list or stable group boundary. Three group-level S6 statements remain pending; no archive or work-group KU is fabricated.","process_ref":PREF},
      {"backlog_id":"bl-0036","canonical_name":c["cand-4824"]["canonical_name"],"suggested_type":"archive","status":"undecided","source_id":"haskell-1980-rev-ed","source_ref":"chp-2:02_CHP-2_sec_iv:l181-188#L186","statement_id":f"{spectator_id};st-chp2-seciv-l181-188-spectator-accounts-used-because-no-drawings-survive","endpoint_role":"anonymous contemporary spectator's quoted account","candidate_id":"cand-4824","ku_id":"","decision_note":"S3 undecided: footnote 3 cites Fraschetti p.264 but does not identify the original quoted document. Keep the account distinct from Fraschetti's book; the two related S6 candidates remain pending.","process_ref":PREF},
    ])

    tp=ROOT/".agents/skills/ingest/references/relation-types.yml"
    dp=ROOT/"01-domain/relation-domain-range.yml"
    types,ranges=update_schema(tp.read_text(encoding="utf-8"),dp.read_text(encoding="utf-8"))
    clp=ROOT/"06-runtime/governance/CHANGELOG.md"
    changelog=clp.read_text(encoding="utf-8")
    if "## 2026-10-25\n" in changelog: raise SystemExit("CHANGELOG already has 2026-10-25; integrate manually")
    entry=("## 2026-10-25\n\n"
      "### 为剧目、演出与临时场所补充关系表达\n\n"
      "为第2章 p.58 的有据关系新增 directed_by／director_of、has_performance／performance_of、inspired_by／inspiration_for，分别表达导演、剧目与演出、作品受事件启发；将 erected_by／erector_of 的场所端点纳入域值域。关系仍须逐条以原文和可识别端点支持。过程依据见 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp2-p58-inondazione-20261025。\n\n")
    changelog=changelog.replace("# 规则变更日志\n","# 规则变更日志\n\n"+entry,1)

    accepted=ROOT/"04-knowledge/accepted.yml"; raw=accepted.read_bytes()
    abom=raw.startswith(b"\xef\xbb\xbf"); atxt=raw.decode("utf-8-sig")
    accepted_bytes=insert_accepted(atxt,[PLACE_CARD,WORK_CARD])
    if abom: accepted_bytes=b"\xef\xbb\xbf"+accepted_bytes

    place_card=make_card("""---
title: "贝尔尼尼自宅外临时剧场（Provisional Theatre outside Bernini’s House）"
name_en: "Provisional Theatre outside Bernini’s House"
type: place
evidence_status: source_backed
sources:
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)'
  location: 第2章；印刷页58；OCR L185–186
  sentence_summary: Bernini erected a provisional theatre outside his own house and directed plays there.
  original_quotes:
  - source_span: OCR L185–186; print p.58
    text: "the provisional theatre which Bernini erected outside his own house"
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/02_CHP-2_sec_iv.md
    source_span: OCR L185–186; print p.58
created: '2026-10-25'
updated: '2026-10-25'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp2-p58-inondazione-20261025
---

## 内容

### 描述

**中文：** 哈斯克尔称，贝尔尼尼在自己住宅外搭建临时剧场，并在那里执导其自写剧目。住宅未具名；本卡只按书内描述限定该演出场所，不补确切地址、存续时长或现存状态。

**English:** Haskell says Bernini erected a provisional theatre outside his own house and directed plays he had written there. The house is unnamed; this card records the source-bounded venue without inferring an exact address, duration, or survival.

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 地点性质 | 临时剧场 | S1：Haskell，第2章印刷页58，OCR L185–186。 |
| 用途 | 戏剧演出场所 | S1：Haskell，第2章印刷页58，OCR L186。 |
| 相对位置 | Bernini自宅之外；住宅未具名 | S1：Haskell，第2章印刷页58，OCR L185–186。 |

## 关系与证据

### 身份与外部链接

未登记外部身份标识；本卡身份限定于 Haskell 的书内指称。

### 关系记录

""")
    work_card=make_card("""---
title: "《台伯河洪水》（L’Inondazione del Tevere）"
name_en: "L’Inondazione del Tevere"
type: work
evidence_status: source_backed
sources:
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)'
  location: 第2章；印刷页58；OCR L186
  sentence_summary: Haskell names Bernini’s play and reports its 1638 Carnival performance and inspiration by a flood in the previous year.
  original_quotes:
  - source_span: OCR L186; print p.58
    text: "the most famous of which was L'Inondazione del Tevere given during the carnival of 1638 and inspired by a flood of the year before"
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/02_CHP-2_sec_iv.md
    source_span: OCR L186; print p.58
created: '2026-10-25'
updated: '2026-10-25'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp2-p58-inondazione-20261025
---

## 内容

### 描述

**中文：** 哈斯克尔称《L’Inondazione del Tevere》是贝尔尼尼在自宅外临时剧场执导的剧目中最著名的一部，于1638年狂欢节期间上演，并受到“前一年”一次洪水启发。中文题名为描述性暂译；本卡与演出事件及前一年洪水事件分开，不指称某个版本或存世副本。

**English:** Haskell identifies L’Inondazione del Tevere as the most famous of the plays Bernini directed at the provisional theatre outside his house. It was given during Carnival 1638 and was said to have been inspired by a flood “of the year before.” The Chinese title is a descriptive translation; this card distinguishes the play from its performance event and the prior-year flood, and does not identify an edition or surviving copy.

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 作品类型 | 戏剧（play） | S1：Haskell，第2章印刷页58，OCR L186。 |
| 原语题名 | L’Inondazione del Tevere | S1：Haskell，第2章印刷页58，OCR L186。 |

## 关系与证据

### 身份与外部链接

未登记外部身份标识；本卡身份限定于 Haskell 的书内指称。

### 关系记录

""")
    outputs={
      cp:write_csv(ch,candidates,cbom,cnl), ap:write_csv(ah,alignments,abom,anl),
      mp:write_csv(mh,manifest,mbom,mnl), T/"relations.csv":write_csv(rh,relations,rbom,rnl),
      T/"candidate-backlog.csv":write_csv(bh,backlog,bbom,bnl),
      sp:(b"\xef\xbb\xbf" if sbom else b"")+(snl.join(out_lines)+snl).encode("utf-8"),
      tp:types.encode("utf-8"),dp:ranges.encode("utf-8"),clp:changelog.encode("utf-8"),
      accepted:accepted_bytes,ROOT/PLACE_CARD:place_card,ROOT/WORK_CARD:work_card
    }
    preview={
      "s3":{"cand-4819":"new place sg3-place-cand-4819","cand-4821":"new work work-group-d21473654a30; previous archive group corrected","cand-4820":"undecided work group; unbounded","cand-4824":"undecided archive; original quote unidentified"},
      "s2":{"new_statements":new_ids,"updated":[built_id,group_id,spectator_id],"statement_delta":5},
      "s4":{"new_kus":[PLACE,WORK]},
      "s5":{"card_fields_to_extract":5},
      "s6_formal":formal,
      "s6_pending":[group_id,new_ids[0],new_ids[1],spectator_id,"st-chp2-seciv-l181-188-spectator-accounts-used-because-no-drawings-survive"],
      "backlog_added":["bl-0035","bl-0036"],
      "outputs":{str(p.relative_to(ROOT)):{"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()} for p,b in outputs.items()}
    }
    return outputs,preview

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True);g.add_argument("--dry-run",action="store_true");g.add_argument("--apply",action="store_true")
    args=p.parse_args();outputs,preview=preflight()
    if args.dry_run: print(json.dumps(preview,ensure_ascii=False,indent=2));return
    if RECOVERY.exists(): raise SystemExit(f"recovery path exists: {RECOVERY}")
    RECOVERY.mkdir(parents=True)
    for path in outputs:
        if path.exists(): shutil.copy2(path,RECOVERY/(path.name+".before"))
    staged={}
    for path,data in outputs.items():
        path.parent.mkdir(parents=True,exist_ok=True)
        tmp=path.with_name(path.name+".p58tmp");tmp.write_bytes(data);staged[path]=tmp
    for path,tmp in staged.items(): tmp.replace(path)
    print(json.dumps({"applied":True,"recovery":str(RECOVERY.relative_to(ROOT)),"preview":preview},ensure_ascii=False,indent=2))

if __name__=="__main__": main()
