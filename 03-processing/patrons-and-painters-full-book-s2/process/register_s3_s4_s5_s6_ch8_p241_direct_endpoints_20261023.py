#!/usr/bin/env python3
"""Register the source-local endpoints cited or named on chapter 8 p.241."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import pathlib
import sys
import tempfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts import build_field_facts as field_facts
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-ch8-p241-direct-endpoints-20261023"
SOURCE8 = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE21 = "02-sources/02-Markdown/21_CHP-21Bibliography.md"


def read_csv(name: str):
    path = TABLES / name
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig" if bom else "utf-8")
    with io.StringIO(text, newline="") as stream:
        reader = csv.DictReader(stream)
        rows, fields = list(reader), list(reader.fieldnames or [])
    return path, rows, fields, bom, "\r\n" if b"\r\n" in raw else "\n"


def csv_bytes(rows, fields, bom, newline):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    data = stream.getvalue().encode("utf-8")
    return b"\xef\xbb\xbf" + data if bom else data


def read_segment(segment_id: str) -> str:
    for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["segment_id"] == segment_id:
            lines = (ROOT / row["source_file"]).read_text(encoding="utf-8").splitlines()
            return "\n".join(lines[row["line_start"] - 1:row["line_end"]])
    raise ValueError(f"missing segment: {segment_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the reviewed S3-S6 batch")
    args = parser.parse_args()

    segment_body = read_segment("chp-8:08_CHP-8_sec_ii:l361-370")
    segment_notes = read_segment("chp-8:08_CHP-8_sec_ii:l372-461")
    segment_article_bib = read_segment("chp-21:21_CHP-21Bibliography:l577-614")
    segment_sgrilli_bib = read_segment("chp-21:21_CHP-21Bibliography:l1102-1139")
    assert segment_body[460:484] == "Guido Cagnacci Magdalene"
    assert segment_body[518:546] == "Cassana Portrait of a Hunter"
    assert segment_article_bib[781:792] == "Haskell, F."
    assert segment_sgrilli_bib[448:473] == "Sgrilli, Bernardo Sansone"
    article_mention = "F. Haskell in Boll, dei Musei Civici Veneziani, i960"
    article_start = segment_notes.index(article_mention)

    cand_path, candidates, cand_fields, cand_bom, cand_nl = read_csv("entity-candidates.csv")
    aln_path, alignments, aln_fields, aln_bom, aln_nl = read_csv("alignment.csv")
    mention_path, mentions, mention_fields, mention_bom, mention_nl = read_csv("mentions.csv")
    manifest_path, manifest, manifest_fields, manifest_bom, manifest_nl = read_csv("ku-manifest.csv")
    relation_path, relations, relation_fields, relation_bom, relation_nl = read_csv("relations.csv")
    sources_path, sources, source_fields, source_bom, source_nl = read_csv("sources.csv")

    # Fixed IDs are guarded by the current maxima so the batch cannot overwrite another turn.
    assert max(int(r["candidate_id"][5:]) for r in candidates) == 12433
    assert max(int(r["alignment_id"][4:]) for r in alignments) == 12726
    assert max(int(r["relation_id"][4:]) for r in relations) == 1626
    assert not any(r["candidate_id"] in {"cand-12434", "cand-12435", "cand-12436"} for r in candidates)
    assert not any(r["alignment_id"] in {"aln-12727", "aln-12728", "aln-12729"} for r in alignments)

    candidates.extend([
        {"candidate_id":"cand-12434","index_entry_id":"","canonical_name":"Guido Cagnacci Magdalene","index_page_range":"","suggested_type":"work","status":"open","index_source_file":"","sub_entry":"","detail":"A painting named by Haskell on printed p.241; source-local work identity, with no external object identity asserted.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":"chp-8:08_CHP-8_sec_ii:l361-370#L363"},
        {"candidate_id":"cand-12435","index_entry_id":"","canonical_name":"Portrait of a Hunter by Niccolò Cassana","index_page_range":"","suggested_type":"work","status":"open","index_source_file":"","sub_entry":"","detail":"A painting named by Haskell on printed p.241; source-local work identity, with no external object identity asserted.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":"chp-8:08_CHP-8_sec_ii:l361-370#L363"},
        {"candidate_id":"cand-12436","index_entry_id":"","canonical_name":"Bernardo Sansone Sgrilli","index_page_range":"","suggested_type":"person","status":"open","index_source_file":"","sub_entry":"","detail":"Named as author in the Haskell bibliography entry for Descrizione della Regia Villa, Fontane e Fabbriche di Pratolino; no biography added.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":"chp-21:21_CHP-21Bibliography:l1102-1139#L1108"},
    ])

    new_mentions = [
        {"mention_id":"m-chp8-p241-work-cagnacci-magdalene","segment_id":"chp-8:08_CHP-8_sec_ii:l361-370","candidate_id":"cand-12434","surface_form":"Guido Cagnacci Magdalene","start_char":"460","end_char":"484","note":"Source-local work mention; artist name has its own overlapping person mention."},
        {"mention_id":"m-chp8-p241-creator-cagnacci","segment_id":"chp-8:08_CHP-8_sec_ii:l361-370","candidate_id":"cand-0478","surface_form":"Guido Cagnacci","start_char":"460","end_char":"474","note":"Painter name in the source-local work designation."},
        {"mention_id":"m-chp8-p241-work-cassana-hunter","segment_id":"chp-8:08_CHP-8_sec_ii:l361-370","candidate_id":"cand-12435","surface_form":"Cassana Portrait of a Hunter","start_char":"518","end_char":"546","note":"Source-local work mention."},
        {"mention_id":"m-chp8-p241-creator-cassana","segment_id":"chp-8:08_CHP-8_sec_ii:l361-370","candidate_id":"cand-0598","surface_form":"Cassana","start_char":"518","end_char":"525","note":"Painter surname in the source-local work designation."},
        {"mention_id":"m-chp8-p241-note5-haskell-article","segment_id":"chp-8:08_CHP-8_sec_ii:l372-461","candidate_id":"cand-8096","surface_form":article_mention,"start_char":str(article_start),"end_char":str(article_start+len(article_mention)),"note":"Haskell article named as further reading in note 5; bibliography provides exact article identity."},
        {"mention_id":"m-chp21-bib-haskell-article-author","segment_id":"chp-21:21_CHP-21Bibliography:l577-614","candidate_id":"cand-9423","surface_form":"Haskell, F.","start_char":"781","end_char":"792","note":"Author name nested in the bibliographic entry for the 1960 article."},
        {"mention_id":"m-chp21-bib-sgrilli-author","segment_id":"chp-21:21_CHP-21Bibliography:l1102-1139","candidate_id":"cand-12436","surface_form":"Sgrilli, Bernardo Sansone","start_char":"448","end_char":"473","note":"Author name in the bibliography entry for the Pratolino book."},
    ]
    existing_mentions = {r["mention_id"] for r in mentions}
    assert not (existing_mentions & {r["mention_id"] for r in new_mentions})
    for mention in new_mentions:
        seg = {
            "chp-8:08_CHP-8_sec_ii:l361-370":segment_body,
            "chp-8:08_CHP-8_sec_ii:l372-461":segment_notes,
            "chp-21:21_CHP-21Bibliography:l577-614":segment_article_bib,
            "chp-21:21_CHP-21Bibliography:l1102-1139":segment_sgrilli_bib,
        }[mention["segment_id"]]
        assert seg[int(mention["start_char"]):int(mention["end_char"])] == mention["surface_form"]
    mentions.extend(new_mentions)

    new_manifest = [
        {"ku_id":"units/works/guido-cagnacci-magdalene","type":"work","canonical_name":"《抹大拉的马利亚》（Guido Cagnacci Magdalene）","name_en":"Guido Cagnacci Magdalene","source_task":"patrons-and-painters-full-book-s2","card_path":"04-knowledge/units/works/guido-cagnacci-magdalene.md"},
        {"ku_id":"units/works/niccolo-cassana-portrait-of-a-hunter","type":"work","canonical_name":"《猎人肖像》（Portrait of a Hunter by Niccolò Cassana）","name_en":"Portrait of a Hunter by Niccolò Cassana","source_task":"patrons-and-painters-full-book-s2","card_path":"04-knowledge/units/works/niccolo-cassana-portrait-of-a-hunter.md"},
        {"ku_id":"units/archives/fogolari-letter-116-1705-10-17","type":"archive","canonical_name":"Fogolari（1937）所刊第116号信（Letter 116 cited through Fogolari (1937)）","name_en":"Letter 116 cited through Fogolari (1937)","source_task":"patrons-and-painters-full-book-s2","card_path":"04-knowledge/units/archives/fogolari-letter-116-1705-10-17.md"},
        {"ku_id":"units/archives/1767-florentine-exhibition-catalogue-introduction","type":"archive","canonical_name":"1767年佛罗伦萨展览目录序言（Introduction to the 1767 Florentine Exhibition Catalogue）","name_en":"Introduction to the 1767 Florentine Exhibition Catalogue","source_task":"patrons-and-painters-full-book-s2","card_path":"04-knowledge/units/archives/1767-florentine-exhibition-catalogue-introduction.md"},
        {"ku_id":"units/archives/descrizione-regia-villa-pratolino-sgrilli-1742","type":"archive","canonical_name":"《普拉托利诺王家别墅、喷泉与建筑志》（Descrizione della Regia Villa, Fontane e Fabbriche di Pratolino）","name_en":"Descrizione della Regia Villa, Fontane e Fabbriche di Pratolino","source_task":"patrons-and-painters-full-book-s2","card_path":"04-knowledge/units/archives/descrizione-regia-villa-pratolino-sgrilli-1742.md"},
        {"ku_id":"units/archives/haskell-artistic-contacts-florence-venice-1960","type":"archive","canonical_name":"《十八世纪佛罗伦萨与威尼斯之间的艺术联系札记》（A Note on Artistic Contacts between Florence and Venice in the 18th Century）","name_en":"A Note on Artistic Contacts between Florence and Venice in the 18th Century","source_task":"patrons-and-painters-full-book-s2","card_path":"04-knowledge/units/archives/haskell-artistic-contacts-florence-venice-1960.md"},
        {"ku_id":"units/persons/bernardo-sansone-sgrilli","type":"person","canonical_name":"贝尔纳多·桑索内·斯格里利（Bernardo Sansone Sgrilli）","name_en":"Bernardo Sansone Sgrilli","source_task":"patrons-and-painters-full-book-s2","card_path":"04-knowledge/units/persons/bernardo-sansone-sgrilli.md"},
    ]
    for row in new_manifest:
        assert (ROOT / row["card_path"]).is_file()

    ku_for = {
        "cand-7847":"units/archives/descrizione-regia-villa-pratolino-sgrilli-1742",
        "cand-8081":"units/archives/1767-florentine-exhibition-catalogue-introduction",
        "cand-8099":"units/archives/fogolari-letter-116-1705-10-17",
        "cand-8096":"units/archives/haskell-artistic-contacts-florence-venice-1960",
        "cand-10717":"units/archives/haskell-artistic-contacts-florence-venice-1960",
        "cand-12434":"units/works/guido-cagnacci-magdalene",
        "cand-12435":"units/works/niccolo-cassana-portrait-of-a-hunter",
        "cand-12436":"units/persons/bernardo-sansone-sgrilli",
    }
    groups = {
        "cand-7847":"archive-group-1589af96e895",
        "cand-8081":"archive-group-8439051bbadc",
        "cand-8099":"archive-group-bb048dac8882",
        "cand-8096":"archive-group-d7c396b7c646",
        "cand-10717":"archive-group-d7c396b7c646",
        "cand-12434":"workgrp-"+hashlib.sha256(b"Guido Cagnacci Magdalene|source-local").hexdigest()[:16],
        "cand-12435":"workgrp-"+hashlib.sha256(b"Portrait of a Hunter by Niccolo Cassana|source-local").hexdigest()[:16],
        "cand-12436":"person-group-bernardo-sansone-sgrilli",
    }
    aln_by_candidate = {r["candidate_id"]:r for r in alignments if r["candidate_id"] in ku_for}
    for cid in ("cand-7847","cand-8081","cand-8099","cand-8096"):
        row = aln_by_candidate[cid]
        assert row["decision"] == "new" and not row["ku_id"]
        row["ku_id"], row["process_ref"] = ku_for[cid], PROCESS
        row["resolution_note"] += f" S4 registration (2026-10-23): {groups[cid]} maps to {ku_for[cid]}; source-local identity, no external identity assertion."
    row = aln_by_candidate["cand-10717"]
    assert row["decision"] == "undecided" and not row["ku_id"]
    row.update(decision="new", ku_id=ku_for["cand-10717"], process_ref=PROCESS)
    row["resolution_note"] = (
        "source_ref=candidate_ref=chp-17:17_CHP-17_sec_ii:l7-17#L17 | mentions=m-chp21-bib-l577-614-008,m-chp21-bib-haskell-article-author | "
        "statements=st-chp21-bib-l577-614-entry-08,st-chp21-bib-l577-614-haskell-author,st-chp8-p241-note5-haskell-cites-article; "
        f"group={groups['cand-10717']}; S3 cross-chapter decision: Haskell's bibliography gives the exact title, journal, year, issue and pages of the same article cited in chapter 8 note 5 (cand-8096). The article itself was not consulted. "
        f"S4 registration maps this group to {ku_for['cand-10717']}."
    )
    for number, cid in zip((12727,12728,12729),("cand-12434","cand-12435","cand-12436")):
        source_ref = next(r["candidate_source_ref"] for r in candidates if r["candidate_id"] == cid)
        mention_refs = ",".join(m["mention_id"] for m in new_mentions if m["candidate_id"] == cid or (cid == "cand-12434" and m["candidate_id"] == "cand-0478") or (cid == "cand-12435" and m["candidate_id"] == "cand-0598"))
        statement_refs = {
            "cand-12434":"st-chp8-p241-additional-loans,st-chp8-p241-cagnacci-colour-description,st-chp8-p241-cagnacci-picture-at-pitti-75,st-chp8-p241-cagnacci-magdalene-created-by",
            "cand-12435":"st-chp8-p241-cassana-hunter-loan,st-chp8-p241-cassana-hunter-created-by",
            "cand-12436":"st-chp21-bib-l1102-1139-entry-04,st-chp21-bib-l1102-1139-sgrilli-author",
        }[cid]
        alignments.append({"alignment_id":f"aln-{number}","candidate_id":cid,"ku_id":ku_for[cid],"external_source":"","external_id":"","decision":"new","accessed_date":"","process_ref":PROCESS,"legacy_ku_id":"","resolution_note":f"source_ref=candidate_ref={source_ref} | mentions={mention_refs} | statements={statement_refs} | group={groups[cid]}; S3 new source-local identity. S4 maps this identity group to {ku_for[cid]}; no external identity verification is claimed."})

    statement_path = TABLES / "book-statements.jsonl"
    statement_rows = [json.loads(line) for line in statement_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_statement = {r["statement_id"]:r for r in statement_rows}
    assert len(by_statement) == len(statement_rows)

    def add_mentioned(qualifiers, candidate_ids):
        qualifiers["mentioned_candidate_ids"] = list(dict.fromkeys(list(qualifiers.get("mentioned_candidate_ids",[]))+candidate_ids))

    row=by_statement["st-chp8-p241-additional-loans"]; row["object_candidate_id"]="cand-12434"; add_mentioned(row["qualifiers"],["cand-12434"])
    row=by_statement["st-chp8-p241-cagnacci-colour-description"]; row["subject_candidate_id"]="cand-12434"; add_mentioned(row["qualifiers"],["cand-12434"])
    row=by_statement["st-chp8-p241-cagnacci-picture-at-pitti-75"]; row["subject_candidate_id"]="cand-12434"; row["qualifiers"]["mentioned_candidate_ids"]=["cand-12434","cand-1949"]
    row=by_statement["st-chp8-p241-cassana-hunter-loan"]; row["object_candidate_id"]="cand-12435"; add_mentioned(row["qualifiers"],["cand-12435","cand-0598"])
    row=by_statement["st-chp8-p241-note3-1767-catalogue"]; row["subject_candidate_id"]="cand-2962"; row["predicate"]="cites"; row["qualifiers"].update(claim="Haskell cites the introduction to the 1767 exhibition catalogue and gives its title.",relation_candidate=True,relation_candidate_note="The footnote cites a specific catalogue component; the catalogue itself was not independently consulted."); add_mentioned(row["qualifiers"],["cand-2962"])
    row=by_statement["st-chp8-p241-note4-sgrilli-locator"]; row["subject_candidate_id"]="cand-2962"; row["predicate"]="cites"; row["qualifiers"].update(claim="Haskell cites Sgrilli, page 3, for the mid-eighteenth-century praise quoted in the body.",relation_candidate=True,relation_candidate_note="Haskell explicitly cites the identified Sgrilli book; p.3 is a corrected locator, and the cited text was not independently read."); add_mentioned(row["qualifiers"],["cand-2962"])
    row=by_statement["st-chp8-p241-note5-gabburri-bottari-citation"]; row["predicate"]="cites"; row["qualifiers"]["claim"]="Haskell points to letters to Gabburri published in Bottari, volume II."; row["qualifiers"]["relation_candidate_note"]="The note cites the Bottari volume; the letters and cited volume were not independently consulted."
    row=by_statement["st-chp8-p241-note5-gerini-follower"]; row["object_candidate_id"]="cand-8101"; row["original_quote"]="Ferdinand’s patronage of contemporary Venetian art had at least one significant follower in eighteenth-century Florence: the Marchese Andrea Gerini"; row["qualifiers"]["claim"]="Haskell describes Andrea Gerini as a significant follower of Ferdinand’s patronage of contemporary Venetian art."; row["qualifiers"]["relation_candidate_note"]="The described endpoint is a source-local art-patronage practice; no controlled predicate currently represents following this practice, so no formal edge is asserted."; row["qualifiers"]["ocr_corrections"]=[x for x in row["qualifiers"].get("ocr_corrections",[]) if x.get("ocr")!="connoisssur"]
    row=by_statement["st-chp8-p241-portrait-as-patronage-signal"]; row["subject_candidate_id"]="cand-8071"; row["qualifiers"]["relation_candidate_note"]="The portrait, not Ferdinand, is the subject of this display interpretation. The source-local relation between portrait and exhibition has no suitable controlled predicate and remains pending."
    row=by_statement["st-chp8-p230-note2-sgrilli"]; row["subject_candidate_id"]="cand-2962"; row["object_candidate_id"]="cand-7847"; row["predicate"]="cites"; row["qualifiers"].update(claim="Haskell note 2 cites Sgrilli in the discussion of the Pratolino theatre.",relation_candidate=True,relation_candidate_note="The footnote cites the Sgrilli book; its p.230 citation shares the same book-to-book edge as p.241 note 4."); add_mentioned(row["qualifiers"],["cand-2962"])

    statement_rows.extend([
        {"statement_id":"st-chp8-p241-cagnacci-magdalene-created-by","segment_id":"chp-8:08_CHP-8_sec_ii:l361-370","subject_candidate_id":"cand-12434","object_candidate_id":"cand-0478","predicate":"created_by","qualifiers":{"source_line_start":363,"source_line_end":363,"printed_page":241,"pdf_physical_page":47,"claim":"Haskell names the Magdalene as a Guido Cagnacci painting.","speaker":"Haskell","text_layer":"body attribution","qualification":"The creator attribution is recorded as Haskell’s wording and is not independently authenticated.","mentioned_candidate_ids":["cand-12434","cand-0478"],"relation_candidate":True,"relation_candidate_note":"The source designation attributes the source-local Magdalene to Guido Cagnacci."},"original_quote":"his Guido Cagnacci Magdalene","origin":"book","source_file":SOURCE8},
        {"statement_id":"st-chp8-p241-cassana-hunter-created-by","segment_id":"chp-8:08_CHP-8_sec_ii:l361-370","subject_candidate_id":"cand-12435","object_candidate_id":"cand-0598","predicate":"created_by","qualifiers":{"source_line_start":363,"source_line_end":363,"printed_page":241,"pdf_physical_page":47,"claim":"Haskell names the Portrait of a Hunter as a Cassana painting.","speaker":"Haskell","text_layer":"body attribution","qualification":"The creator attribution is recorded as Haskell’s wording and is not independently authenticated.","mentioned_candidate_ids":["cand-12435","cand-0598"],"relation_candidate":True,"relation_candidate_note":"The source designation attributes the source-local portrait to Niccolò Cassana."},"original_quote":"his Cassana Portrait of a Hunter","origin":"book","source_file":SOURCE8},
        {"statement_id":"st-chp8-p241-note5-haskell-cites-article","segment_id":"chp-8:08_CHP-8_sec_ii:l372-461","subject_candidate_id":"cand-2962","object_candidate_id":"cand-8096","predicate":"cites","qualifiers":{"source_line_start":461,"source_line_end":461,"printed_page":241,"pdf_physical_page":47,"claim":"Haskell note 5 directs readers to his article on artistic contacts between Florence and Venice for further information about Gerini.","speaker":"Haskell","text_layer":"footnote citation","qualification":"The article title and exact issue/page range are identified from Haskell’s bibliography; the article itself was not independently consulted.","mentioned_candidate_ids":["cand-2962","cand-1143","cand-8096"],"footnote_marker":5,"linked_body_statement_ids":["st-chp8-p241-note5-gerini-follower"],"ocr_corrections":[{"source_line":461,"ocr":"sec F. Haskell","print":"see F. Haskell","basis":"CHP-8.pdf physical page 47"},{"source_line":461,"ocr":"i960","print":"1960","basis":"CHP-8.pdf physical page 47"}],"relation_candidate":True,"relation_candidate_note":"The note explicitly cites Haskell’s article as further reading on Gerini; the publication has a separate source-backed archive identity."},"original_quote":"for whom sec F. Haskell in Boll, dei Musei Civici Veneziani, i960","origin":"book","source_file":SOURCE8},
        {"statement_id":"st-chp21-bib-l577-614-haskell-author","segment_id":"chp-21:21_CHP-21Bibliography:l577-614","subject_candidate_id":"cand-10717","object_candidate_id":"cand-9423","predicate":"authored_by","qualifiers":{"source_line_start":588,"source_line_end":589,"printed_page":425,"claim":"Haskell’s bibliography identifies F. Haskell as author of the article on artistic contacts between Florence and Venice.","speaker":"Haskell","text_layer":"bibliography author attribution","qualification":"This is the author attribution in Haskell’s bibliography; the article itself was not consulted.","mentioned_candidate_ids":["cand-10717","cand-9423"],"relation_candidate":True,"relation_candidate_note":"Bibliography names Haskell as the article author."},"original_quote":"Haskell, F.: ‘A note on artistic contacts between Florence and Venice in the 18th century’","origin":"book","source_file":SOURCE21},
        {"statement_id":"st-chp21-bib-l1102-1139-sgrilli-author","segment_id":"chp-21:21_CHP-21Bibliography:l1102-1139","subject_candidate_id":"cand-7847","object_candidate_id":"cand-12436","predicate":"authored_by","qualifiers":{"source_line_start":1108,"source_line_end":1109,"printed_page":437,"claim":"Haskell’s bibliography identifies Bernardo Sansone Sgrilli as author of Descrizione della Regia Villa, Fontane e Fabbriche di Pratolino.","speaker":"Haskell","text_layer":"bibliography author attribution","qualification":"This records the bibliography attribution; the cited book was not independently consulted.","mentioned_candidate_ids":["cand-7847","cand-12436"],"relation_candidate":True,"relation_candidate_note":"The bibliography explicitly associates Sgrilli with the named book."},"original_quote":"Sgrilli, Bernardo Sansone: Descrizione della Regia Villa, Fontane e Fabbriche di Pratolino, Firenze 1742.","origin":"book","source_file":SOURCE21},
    ])
    assert len({r["statement_id"] for r in statement_rows}) == len(statement_rows)

    manifest_paths={r["card_path"] for r in manifest}
    assert not (manifest_paths & {r["card_path"] for r in new_manifest})
    manifest.extend(new_manifest)
    accepted_path=ROOT/"04-knowledge"/"accepted.yml"
    accepted_data=yaml.safe_load(accepted_path.read_text(encoding="utf-8-sig"))
    accepted=list(accepted_data["units"])
    new_paths=[r["card_path"] for r in new_manifest]
    assert not (set(accepted)&set(new_paths))

    # Extract only these seven cards into S5; preserve the full enrichment table unchanged otherwise.
    records, source_registry, warnings, _ = field_facts.extract_records(new_manifest)
    assert not warnings, warnings
    assert len(records)==14
    assert all(r["evidence_status"]=="source_backed" and r["source_ids"]==["haskell-1980-rev-ed"] for r in records)
    enrichment_path=TABLES/"enrichment.jsonl"
    existing_enrichment=[json.loads(line) for line in enrichment_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    field_facts.assign_ids(records,enrichment_path)
    assert not ({r["enrichment_id"] for r in records}&{r["enrichment_id"] for r in existing_enrichment})
    source_ids={r["source_id"] for r in sources}
    assert set(source_registry)<=source_ids
    enrichment_text=enrichment_path.read_text(encoding="utf-8")+"".join(json.dumps(r,ensure_ascii=False)+"\n" for r in records)

    # Eleven unique formal edges: reuse the p.240 attendance edge and merge both Sgrilli citations.
    specs=[
      ("units/archives/patrons-and-painters","units/archives/fogolari-letter-116-1705-10-17","cites","","Haskell书内脚注引用","p.241脚注1引用 Fogolari 1937 年第116号信；原信未独立查阅。","lines 457; printed p.241, note 1; st-chp8-p241-note1-fogolari-letter116",SOURCE8),
      ("units/archives/patrons-and-painters","units/archives/1767-florentine-exhibition-catalogue-introduction","cites","","Haskell书内脚注引用","p.241脚注3引用1767年展览目录序言；目录未独立查阅。","line 459; printed p.241, note 3; st-chp8-p241-note3-1767-catalogue",SOURCE8),
      ("units/archives/patrons-and-painters","units/archives/descrizione-regia-villa-pratolino-sgrilli-1742","cites","","Haskell书内脚注引用","p.230脚注2与p.241脚注4均引用同一 Sgrilli 著作；被引页未独立查阅。","lines 406 and 460; printed pp.230, 241; st-chp8-p230-note2-sgrilli,st-chp8-p241-note4-sgrilli-locator",SOURCE8),
      ("units/archives/patrons-and-painters","units/archives/haskell-artistic-contacts-florence-venice-1960","cites","","Haskell书内脚注引用","p.241脚注5指向 Haskell 的文章；文章本身未独立查阅。","line 461; printed p.241, note 5; st-chp8-p241-note5-haskell-cites-article",SOURCE8),
      ("units/archives/patrons-and-painters","units/archives/bottari-ticozzi-raccolta-vol-ii-1822","cites","","Haskell书内脚注引用","p.241脚注5指出 Gabburri 书信刊于 Bottari 第II卷；书信与该卷未独立查阅。","line 461; printed p.241, note 5; st-chp8-p241-note5-gabburri-bottari-citation",SOURCE8),
      ("units/works/guido-cagnacci-magdalene","units/persons/guido-cagnacci","created_by","","原书归属","Haskell 将该 Magdalene 称作 Guido Cagnacci 作品；记录其原书归属，不表示外部核验。","line 363; printed p.241; st-chp8-p241-cagnacci-magdalene-created-by",SOURCE8),
      ("units/works/guido-cagnacci-magdalene","units/places/palazzo-pitti","located_at","","Haskell报告的馆藏地点","Haskell p.241 note 1 报告该画当时在 Pitti、编号75；馆藏状态未独立核验。","line 457; printed p.241, note 1; st-chp8-p241-cagnacci-picture-at-pitti-75",SOURCE8),
      ("units/works/niccolo-cassana-portrait-of-a-hunter","units/persons/niccolo-cassana","created_by","","原书归属","Haskell 将该 Portrait of a Hunter 称作 Cassana 作品；记录其原书归属，不表示外部核验。","line 363; printed p.241; st-chp8-p241-cassana-hunter-created-by",SOURCE8),
      ("units/events/florentine-art-exhibition-1706","units/institutions/accademia-del-disegno-florence","has_participant","1706","展览庇护／组织机构","Haskell 称展览在 Accademia del Disegno 庇护下组织；不据此断言学院承担全部实际组织。","line 367; printed p.241; st-chp8-p241-academy-organized-exhibition",SOURCE8),
      ("units/archives/haskell-artistic-contacts-florence-venice-1960","units/persons/francis-haskell","authored_by","1960","书目所列作者","Haskell 书目列出 F. Haskell 为作者；关系依据书目归属，文章未独立查阅。","lines 588–589; printed p.425; st-chp21-bib-l577-614-haskell-author",SOURCE21),
      ("units/archives/descrizione-regia-villa-pratolino-sgrilli-1742","units/persons/bernardo-sansone-sgrilli","authored_by","1742","书目所列作者","Haskell 书目列出 Bernardo Sansone Sgrilli 为作者；被引书未独立查阅。","lines 1108–1109; printed p.437; st-chp21-bib-l1102-1139-sgrilli-author",SOURCE21),
    ]
    old_attendance=[r for r in relations if (r["subject_ku_id"],r["object_ku_id"],r["predicate"])==("units/events/florentine-art-exhibition-1706","units/persons/ferdinand-grand-prince-tuscany","has_participant")]
    assert len(old_attendance)==1 and old_attendance[0]["relation_id"]=="rel-1619"
    old_attendance[0]["source_span"] += "; Chapter 8, printed p.241; statement: st-chp8-p241-attendance-success-and-academy"
    old_attendance[0]["note"]="Source-local attendance relation. The p.240 account and p.241 statement support the same event/person edge; no duplicate relation was created. Scope and limits are recorded in the p.240 and p.241 process records."
    manifest_ids={r["ku_id"] for r in manifest}
    for i,spec in enumerate(specs,start=1627):
        subject,obj,predicate,when,role,scope,span,source_file=spec
        assert subject in manifest_ids and obj in manifest_ids
        assert not any((r["subject_ku_id"],r["object_ku_id"],r["predicate"])==(subject,obj,predicate) for r in relations)
        relations.append({"relation_id":f"rel-{i:04d}","subject_ku_id":subject,"object_ku_id":obj,"predicate":predicate,"time":when,"role":role,"scope":scope,"origin":"book","status":"formal","source_id":"haskell-1980-rev-ed","source_span":span,"source_file":source_file,"note":""})
    assert not any((r["subject_ku_id"],r["object_ku_id"],r["predicate"])==("units/events/florentine-art-exhibition-1706","units/persons/luca-giordano","has_participant") for r in relations)
    relations.append({"relation_id":"rel-1638","subject_ku_id":"units/events/florentine-art-exhibition-1706","object_ku_id":"units/persons/luca-giordano","predicate":"has_participant","time":"1706","role":"展览中显著出现；指人或其作品未定","scope":"Haskell p.241 says Luca Giordano was much in evidence but does not distinguish the painter from his works.","origin":"book","status":"pending","source_id":"haskell-1980-rev-ed","source_span":"line 366; printed p.241; st-chp8-p241-luca-giordano-presence","source_file":SOURCE8,"note":"Typed endpoint and controlled predicate are available, but the person-versus-works reading remains unresolved."})

    if not args.apply:
        print("Dry run: +3 candidates, +7 mentions, +7 KU cards, 8 registered candidate mappings, +5 S2 statements, 14 S5 source-backed fields, +11 formal relation rows, +1 pending relation row; reuse rel-1619 and adjudicate 44 S6 candidates.")
        print("S3 decision change: cand-10717 undecided -> new in cand-8096's existing archive group. No outside identity check or cited-work reading is claimed.")
        return 0

    statement_text="".join(json.dumps(r,ensure_ascii=False)+"\n" for r in statement_rows)
    accepted_path=ROOT/"04-knowledge"/"accepted.yml"
    accepted_raw=accepted_path.read_text(encoding="utf-8-sig")
    accepted=yaml.safe_load(accepted_raw)["units"]
    paths=[r["card_path"] for r in new_manifest]
    assert not (set(accepted)&set(paths))
    assert "claims:" in accepted_raw and accepted_raw.startswith("units:")
    unit_block, remainder=accepted_raw.split("claims:",1)
    accepted_text=unit_block+"".join(f"- {p}\n" for p in paths)+"claims:"+remainder
    writes={
      cand_path:csv_bytes(candidates,cand_fields,cand_bom,cand_nl),
      aln_path:csv_bytes(alignments,aln_fields,aln_bom,aln_nl),
      mention_path:csv_bytes(mentions,mention_fields,mention_bom,mention_nl),
      manifest_path:csv_bytes(manifest,manifest_fields,manifest_bom,manifest_nl),
      relation_path:csv_bytes(relations,relation_fields,relation_bom,relation_nl),
      TABLES/"book-statements.jsonl":statement_text.encode("utf-8"),
      TABLES/"enrichment.jsonl":enrichment_text.encode("utf-8"),
      accepted_path:accepted_text.encode("utf-8"),
    }
    temp_paths=[]
    try:
        for path,data in writes.items():
            fd,name=tempfile.mkstemp(prefix=path.name+".batch-",dir=path.parent)
            os.close(fd)
            temp=pathlib.Path(name); temp.write_bytes(data); temp_paths.append((temp,path))
        for temp,path in temp_paths:
            temp.replace(path)
    finally:
        for temp,_ in temp_paths:
            if temp.exists(): temp.unlink()
    print("Applied: 3 candidates, 7 mentions, 7 KU cards, 8 registered candidate mappings, 5 S2 statements, 14 S5 source-backed fields, 11 formal relation rows, 1 pending relation row; rel-1619 reused.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
