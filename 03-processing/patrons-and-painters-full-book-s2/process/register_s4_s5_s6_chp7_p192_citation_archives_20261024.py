from __future__ import annotations
import argparse, csv, hashlib, io, json, re, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PROC=ROOT/"03-processing/patrons-and-painters-full-book-s2/process"
TABLES=ROOT/"04-knowledge/tables"
TASK="S4-S5-S6-chp7-p192-citation-archives-20261024"
ANCHOR="s4-s5-s6-chp7-p192-griseri-longhi-citations-20261024"
DATE="2026-10-24"
SOURCE_ID="haskell-1980-rev-ed"
CH7="02-sources/02-Markdown/07_CHP-7_sec_i.md"
BIB="02-sources/02-Markdown/21_CHP-21Bibliography.md"
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(PROC))
import register_s4_s5_s6_archive_citations_20261020 as card
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as h
from scripts import build_field_facts as facts
card.TASK="patrons-and-painters-full-book-s2"; card.DATE=DATE; card.ANCHOR=ANCHOR
card.BOOK_CITATION="Francis Haskell, Patrons and Painters, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SPECS=[
 {"candidate":"cand-7143","group":"archive-group-0b763e26ed55","ku":"units/archives/griseri-bozzetti-luca-giordano-escorial-1956","path":"04-knowledge/units/archives/griseri-bozzetti-luca-giordano-escorial-1956.md","zh":"卢卡·焦尔达诺为埃斯科里亚尔阶梯所作草图","en":"Luca Giordano’s Sketches for the Escorial Staircase","sub":"journal article; Haskell bibliography record",
  "citations":["st-chp7-p192-n2-cite-griseri"],
  "role":"第7章p.192注2的书目引文","scope":"只记录Haskell第7章p.192注2对该期刊论文及pp.33–39的引注；不表示论文或所引页已查阅。",
  "span":"Chapter 7, printed p.192 n.2, line 389; PDF physical p.30; statement=st-chp7-p192-n2-cite-griseri",
  "sources":[
   {"location":"第21章书目，印刷页424，Markdown L552–553。","summary":"书目列A. Griseri的期刊论文、Paragone、81、1956及pp.33–39。既有S2页图校读已区分页码结尾与下一条Griseri书目；论文及所引页未独立查阅。","source_file":BIB,"span":"lines 552–553; printed p.424","quotes":["Griseri, A.: ‘I bozzetti di Luca Giordano per l’Escaliera dell’Escorial’ in Paragone, 81, 1956,\nPP33-39"],"link":"[第21章p.424书目](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L552)"},
   {"location":"第7章印刷页192注2，Markdown L389，PDF物理页30。","summary":"注2引用Griseri 1956年论文pp.33–39；只记录Haskell的引注，不证明论文或被引页已阅读。","source_file":CH7,"span":"line 389; printed p.192 n.2; PDF physical p.30","quotes":["2 Griseri, 1956, pp. 33-9, and Longhi, 1954, pp. 28-39. Zanotti (I, pp. 247-8) says that Luca Giordano’s invitation followed a refusal by Marcantonio Franceschini to go to Spain."],"link":"[第7章p.192注2](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md#L389)"}],
  "fields":[("文献类型","期刊论文（Haskell书目记录）","S1；第21章印刷页424，L552–553"),("原题名","I bozzetti di Luca Giordano per l’Escaliera dell’Escorial","S1；第21章印刷页424，L552–553"),("作者（书目署名）","A. Griseri（照录书目形式）","S1；第21章印刷页424，L552"),("期刊","Paragone","S1；第21章印刷页424，L552–553"),("卷号","81","S1；第21章印刷页424，L552–553"),("出版年","1956","S1；第21章印刷页424，L552–553"),("页码","33–39（既有S2页图校读；原始OCR连写为PP33-39Griseri）","S1；第21章印刷页424，L553；校读依据见S2书目statement"),("Haskell书内引注","第7章p.192注2引pp.33–39；论文与被引页未独立查阅","S2；第7章印刷页192注2，L389")],
  "zhdesc":"登记Haskell第21章书目所列A. Griseri期刊论文。中文与英文显示名为描述性工作译名；意大利语原题保留在字段中。第7章p.192注2引用该文pp.33–39。论文及被引页未独立查阅；不扩写作者身份或作品内容。",
  "endesc":"This unit records the journal article by A. Griseri listed in Haskell’s chapter 21 bibliography. The Chinese and English display titles are descriptive working translations; the Italian title is retained in the bibliographic record. Chapter 7, p.192 n.2 cites pp.33–39. Neither the article nor its cited pages was independently consulted, and no author identity or article content is added."},
 {"candidate":"cand-7144","group":"archive-group-63ee5074760d","ku":"units/archives/longhi-il-goya-romano-1954","path":"04-knowledge/units/archives/longhi-il-goya-romano-1954.md","zh":"罗马的戈雅与“孔多蒂街文化”","en":"The Roman Goya and the “Via Condotti Culture”","sub":"journal article; Haskell bibliography record",
  "citations":["st-chp7-p192-n2-cite-longhi"],
  "role":"第7章p.192注2的书目引文","scope":"只记录Haskell第7章p.192注2对该期刊论文及pp.28–39的引注；不表示论文或所引页已查阅。",
  "span":"Chapter 7, printed p.192 n.2, line 389; PDF physical p.30; statement=st-chp7-p192-n2-cite-longhi",
  "sources":[
   {"location":"第21章书目，印刷页428，Markdown L705–706。","summary":"书目列R. Longhi的题名及Paragone、53、1954、pp.28–39。既有S2页图校读指出OCR中错置的Paragone标题属于该条目；论文未独立查阅。","source_file":BIB,"span":"lines 705–706; printed p.428","quotes":["Paragone,\nLonghi, R.: ‘Il Goya romano e la “cultura di Via Condotti” ’ in 53, 1954, pp. 28-39."],"link":"[第21章p.428书目](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L705)"},
   {"location":"第7章印刷页192注2，Markdown L389，PDF物理页30。","summary":"注2引用Longhi 1954年论文pp.28–39；只记录Haskell的引注，不证明论文或被引页已阅读。","source_file":CH7,"span":"line 389; printed p.192 n.2; PDF physical p.30","quotes":["2 Griseri, 1956, pp. 33-9, and Longhi, 1954, pp. 28-39. Zanotti (I, pp. 247-8) says that Luca Giordano’s invitation followed a refusal by Marcantonio Franceschini to go to Spain."],"link":"[第7章p.192注2](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md#L389)"}],
  "fields":[("文献类型","期刊论文（Haskell书目记录）","S1；第21章印刷页428，L705–706"),("原题名","Il Goya romano e la “cultura di Via Condotti”","S1；第21章印刷页428，L706"),("作者（书目署名）","R. Longhi（照录书目形式）","S1；第21章印刷页428，L706"),("期刊","Paragone（既有S2页图校读确认错置标题属于本条）","S1；第21章印刷页428，L705–706"),("卷号","53","S1；第21章印刷页428，L706"),("出版年","1954","S1；第21章印刷页428，L706"),("页码","28–39","S1；第21章印刷页428，L706"),("Haskell书内引注","第7章p.192注2引pp.28–39；论文与被引页未独立查阅","S2；第7章印刷页192注2，L389")],
  "zhdesc":"登记Haskell第21章书目所列R. Longhi期刊论文。中文与英文显示名为描述性工作译名；意大利语原题保留在字段中。第7章p.192注2引用该文pp.28–39。论文未独立查阅；作者姓名只保留书目形式，不据此补全人物身份。",
  "endesc":"This unit records the journal article by R. Longhi listed in Haskell’s chapter 21 bibliography. The Chinese and English display titles are descriptive working translations; the Italian title is retained in the bibliographic record. Chapter 7, p.192 n.2 cites pp.28–39. The article was not independently consulted, and the author’s initials are not expanded into a person identity."}
]

def csv_bytes(raw,fields,rows):
    out=io.StringIO(newline="")
    writer=csv.DictWriter(out,fieldnames=fields,lineterminator="\n",extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    data=out.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b"")+data

def bom(path,text):
    return (b"\xef\xbb\xbf" if path.read_bytes().startswith(b"\xef\xbb\xbf") else b"")+text.encode("utf-8")

def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True); g.add_argument("--dry-run",action="store_true"); g.add_argument("--apply",action="store_true")
    args=ap.parse_args()
    p={"manifest":TABLES/"ku-manifest.csv","alignment":TABLES/"alignment.csv","relations":TABLES/"relations.csv","enrichment":TABLES/"enrichment.jsonl","accepted":ROOT/"04-knowledge/accepted.yml","process":PROC/"knowledge.md","result":ROOT/"04-knowledge/results/patrons-and-painters-full-book-s2.md"}
    mf,manifest=h.read_csv(p["manifest"]); af,align=h.read_csv(p["alignment"]); rf,rels=h.read_csv(p["relations"])
    _,cands=h.read_csv(TABLES/"entity-candidates.csv"); _,sources=h.read_csv(TABLES/"sources.csv")
    statements=h.load_statements(); bysid={r["statement_id"]:r for r in statements}; bycid={r["candidate_id"]:r for r in cands}
    prim={r["candidate_id"]:r for r in align if r.get("candidate_id") and not r.get("external_source")}
    process=p["process"].read_text(encoding="utf-8-sig"); result=p["result"].read_text(encoding="utf-8-sig"); accepted=p["accepted"].read_text(encoding="utf-8-sig")
    assert SOURCE_ID in {r["source_id"] for r in sources}
    assert ANCHOR not in process and ANCHOR not in result
    for s in SPECS:
        c=bycid[s["candidate"]]; a=prim[s["candidate"]]
        assert c["suggested_type"]=="archive" and a["decision"]=="new" and not a.get("ku_id")
        assert h.get_group(a.get("resolution_note",""))==s["group"]
        group_members=[r["candidate_id"] for r in align if r.get("candidate_id") and not r.get("external_source") and r.get("decision")=="new" and h.get_group(r.get("resolution_note",""))==s["group"]]
        assert group_members==[s["candidate"]]
        assert not (ROOT/s["path"]).exists() and s["path"] not in accepted
        assert not any(r["ku_id"]==s["ku"] or r["card_path"]==s["path"] for r in manifest)
        for sid in s["citations"]:
            st=bysid[sid]; assert st.get("predicate")=="cites" and st.get("qualifiers",{}).get("relation_candidate") is True
            assert st.get("subject_candidate_id")=="cand-2962" and st.get("object_candidate_id")==s["candidate"]
            assert sid not in process and not any(sid in r.get("source_span","") or sid in r.get("note","") for r in rels)
        for source in s["sources"]:
            text=(ROOT/source["source_file"]).read_text(encoding="utf-8-sig"); norm=" ".join(text.split())
            assert all(" ".join(q.split()) in norm for q in source["quotes"]),(s["candidate"],source["span"])
    start=max(int(r["relation_id"].split("-")[1]) for r in rels)+1
    planned_align=[dict(r) for r in align]; prim2={r["candidate_id"]:r for r in planned_align if r.get("candidate_id") and not r.get("external_source")}
    planned_manifest=list(manifest); cards={}
    for s in SPECS:
        row=prim2[s["candidate"]]; row["ku_id"]=s["ku"]; row["process_ref"]=f"03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR}"
        row["resolution_note"]+=f" S4 registration: {s['group']} maps to {s['ku']}; Haskell bibliographic identity only."
        planned_manifest.append({"ku_id":s["ku"],"type":"archive","canonical_name":s["zh"],"name_en":s["en"],"source_task":"patrons-and-painters-full-book-s2","card_path":s["path"]})
        spec={"candidate":s["candidate"],"group":s["group"],"ku_id":s["ku"],"type":"archive","sub_type":s["sub"],"name_zh":s["zh"],"name_en":s["en"],"card_path":s["path"],"sources":s["sources"],"fields":s["fields"],"paragraph_zh":s["zhdesc"],"paragraph_en":s["endesc"]}
        cards[ROOT/s["path"]]=card.make_archive_card(spec)
    accepted_new=card.insert_accepted_paths(accepted,[s["path"] for s in SPECS])
    added_rel=[]
    for i,s in enumerate(SPECS):
        added_rel.append({"relation_id":f"rel-{start+i:04d}","subject_ku_id":"units/archives/patrons-and-painters","object_ku_id":s["ku"],"predicate":"cites","time":"","role":s["role"],"scope":s["scope"],"origin":"book","status":"formal","source_id":SOURCE_ID,"source_span":s["span"],"source_file":CH7,"note":"S2 relation candidate: "+"; ".join(s["citations"])+". Bibliographic citation only; cited article and pages not independently consulted."})
    planned_rels=rels+added_rel
    keys=set()
    for r in planned_rels:
        k=(r["subject_ku_id"],r["predicate"],r["object_ku_id"],r["time"],r["role"],r["scope"]); assert k not in keys,k; keys.add(k)
    oldbase=facts.BASE
    try:
        with tempfile.TemporaryDirectory(prefix="pnp-p192-fields-") as td:
            facts.BASE=Path(td)
            for path,content in cards.items():
                dest=Path(td)/path.relative_to(ROOT); dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(content,encoding="utf-8-sig",newline="\n")
            selected=[r for r in planned_manifest if r["ku_id"] in {s["ku"] for s in SPECS}]
            fields,_,warnings,ncards=facts.extract_records(selected)
    finally: facts.BASE=oldbase
    assert not warnings,warnings
    assert ncards==2 and len(fields)==16,(ncards,len(fields))
    assert all(r["evidence_status"]=="source_backed" and r["origin"]=="book" and r["source_ids"]==[SOURCE_ID] for r in fields)
    facts.assign_ids(fields,p["enrichment"])
    raw=p["enrichment"].read_bytes(); old_fields=[json.loads(x) for x in raw.decode("utf-8-sig").splitlines() if x.strip()]
    append=(b"" if raw.endswith(b"\n") else b"\n")+b"".join(json.dumps(r,ensure_ascii=False,separators=(",",":")).encode("utf-8")+b"\n" for r in fields)
    s6=re.search(r"S6累计裁决([\d,]+)/([\d,]+)条关系候选（([\d,]+) formal、([\d,]+) pending、([\d,]+) rejected）",result)
    assert s6
    decided,total,formal,pending,rejected=[int(x.replace(",","")) for x in s6.groups()]
    entry=f"**第7章 p.192 注2书目端点批次（{DATE}）：** 沿用 cand-7143 与 cand-7144 的既有 S3 new 身份组，登记 Griseri 1956 与 Longhi 1954 两篇期刊论文 archive KU；新增16条 Haskell 来源 S5 字段。两条 cites 候选均 formal 裁决（rel-{start:04d}、rel-{start+1:04d}），只记录 Haskell 的引注和页码，不表示论文或所引页已查阅。未新增或重开 S3 决定、S2 statement 或独立复核分子。两张新卡与 Haskell 书目总卡定向渲染后复预览；详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR})。\n\n"
    marker="### 本轮进度与后续工作（2026-10-24）\n\n"; assert result.count(marker)==1
    result_new=result.replace(marker,marker+entry,1)
    process_note=f"""
\n\n<a id="{ANCHOR}"></a>

### S4/S5/S6：第7章 p.192 注2的 Griseri 与 Longhi 书目端点（{DATE}）

从当前关系候选队列选取能解锁明确 cites 关系的两个 archive 端点。候选在 S3 已分别判为 new，本批不更改身份决定；第21章书目与第7章注2相互定位到相同期刊论文记录。两篇论文及注释所列页码均未独立查阅。

| 候选 | S3身份组 | KU | 跨章证据与边界 |
|---|---|---|---|
| cand-7143 | archive-group-0b763e26ed55 | units/archives/griseri-bozzetti-luca-giordano-escorial-1956 | 第21章印刷页424书目及第7章p.192注2；意大利语原题保留；A. Griseri仅作书目署名。|
| cand-7144 | archive-group-63ee5074760d | units/archives/longhi-il-goya-romano-1954 | 第21章印刷页428书目及第7章p.192注2；R. Longhi仅作书目署名，不补全人物身份。|

S5新增16条source_backed字段，两张卡各8条，记录文献类型、原题名、书目署名、刊名、卷号、出版年、页码和Haskell引注位置。Griseri条目的OCR页码连写和Longhi条目的错置Paragone标题沿用既有S2页图校读；S0 OCR转录未改写。

S6逐项裁决：两项均符合archive到archive的cites类型和值域，只确认Haskell注2的书目引注及页码，不把被引内容视为已核实。

| statement_id | 裁决 |
|---|---|
| st-chp7-p192-n2-cite-griseri | formal rel-{start:04d} cites；p.192 n.2，1956，pp.33–39。|
| st-chp7-p192-n2-cite-longhi | formal rel-{start+1:04d} cites；p.192 n.2，1954，pp.28–39。|

本批新增2个S4映射、16条S5字段、2项S6 formal决定；S3决定数、S2 statement数和独立复核分子不变。
"""
    process_new=process.rstrip()+process_note
    writes={
      p["alignment"]:csv_bytes(p["alignment"].read_bytes(),af,planned_align),
      p["manifest"]:csv_bytes(p["manifest"].read_bytes(),mf,planned_manifest),
      p["relations"]:csv_bytes(p["relations"].read_bytes(),rf,planned_rels),
      p["enrichment"]:raw+append,
      p["accepted"]:bom(p["accepted"],accepted_new),
      p["process"]:bom(p["process"],process_new),
      p["result"]:bom(p["result"],result_new),
    }
    if args.dry_run:
        print("dry-run passed: two existing S3 new groups, two archive cards, 16 source-backed fields")
        print(f"S6: two formal cites decisions -> rel-{start:04d}, rel-{start+1:04d}; natural keys unique")
        print(f"S4: {sum(r.get('decision')=='new' and bool(r.get('ku_id')) and not r.get('external_source') for r in planned_align)}/{sum(r.get('decision')=='new' and not r.get('external_source') for r in planned_align)} new candidates mapped")
        print("writes: 2 cards; accepted.yml; alignment.csv; ku-manifest.csv; enrichment.jsonl; relations.csv; process and result")
        return 0
    recovery=ROOT/"06-runtime"/"recovery"/TASK; recovery.mkdir(parents=True,exist_ok=False)
    manifest={}
    for path in writes:
        raw0=path.read_bytes(); rel=path.relative_to(ROOT); dest=recovery/"original"/rel; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(raw0); manifest[rel.as_posix()]=hashlib.sha256(raw0).hexdigest()
    (recovery/"backup-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for path,content in cards.items(): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(content,encoding="utf-8-sig",newline="\n")
    for path,data in writes.items(): path.write_bytes(data)
    print(f"applied 2 S4 mappings, 16 S5 fields, 2 S6 formal decisions; recovery={recovery.relative_to(ROOT)}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
