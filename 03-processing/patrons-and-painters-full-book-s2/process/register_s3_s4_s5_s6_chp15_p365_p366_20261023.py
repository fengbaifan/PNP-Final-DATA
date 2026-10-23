#!/usr/bin/env python3
"""Apply the reviewed S3-S6 endpoint batch for chapter 15 pp.365-366."""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import pathlib
import sys
import tempfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp15-p365-p366-20261023"
SOURCE15 = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
SOURCE21 = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
TASK = "patrons-and-painters-full-book-s2"


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


def latest_alignment(rows, candidate_id):
    matches = [r for r in rows if r["candidate_id"] == candidate_id and not r["external_source"]]
    if not matches:
        raise AssertionError(f"missing internal S3 row for {candidate_id}")
    return max(matches, key=lambda r: int(r["alignment_id"][4:]))


def load_segment(segment_id):
    for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["segment_id"] == segment_id:
            lines = (ROOT / row["source_file"]).read_text(encoding="utf-8").splitlines()
            return "\n".join(lines[row["line_start"] - 1:row["line_end"]])
    raise AssertionError(f"missing source segment {segment_id}")


def write_bundle(writes):
    originals = {path: path.read_bytes() for path in writes}
    staged = []
    replaced = []
    try:
        for path, data in writes.items():
            fd, name = tempfile.mkstemp(prefix=path.name + ".batch-", dir=path.parent)
            os.close(fd)
            temp = pathlib.Path(name)
            temp.write_bytes(data)
            staged.append((temp, path))
        for temp, path in staged:
            temp.replace(path)
            replaced.append(path)
        for path, data in writes.items():
            if path.read_bytes() != data:
                raise IOError(f"post-write byte verification failed: {path}")
    except Exception:
        for path in reversed(replaced):
            fd, name = tempfile.mkstemp(prefix=path.name + ".rollback-", dir=path.parent)
            os.close(fd)
            temp = pathlib.Path(name)
            temp.write_bytes(originals[path])
            temp.replace(path)
        raise
    finally:
        for temp, _ in staged:
            if temp.exists():
                temp.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the reviewed endpoint batch")
    args = parser.parse_args()

    cand_path, candidates, cand_fields, cand_bom, cand_nl = read_csv("entity-candidates.csv")
    aln_path, alignments, aln_fields, aln_bom, aln_nl = read_csv("alignment.csv")
    mention_path, mentions, mention_fields, mention_bom, mention_nl = read_csv("mentions.csv")
    manifest_path, manifest, manifest_fields, manifest_bom, manifest_nl = read_csv("ku-manifest.csv")
    relation_path, relations, relation_fields, relation_bom, relation_nl = read_csv("relations.csv")
    sources_path, sources, source_fields, source_bom, source_nl = read_csv("sources.csv")

    source_id = "haskell-1980-rev-ed"
    assert any(row["source_id"] == source_id for row in sources)
    expected = {
        "cand-0981": "undecided", "cand-10478": "new", "cand-10486": "new",
        "cand-10491": "new", "cand-10492": "new", "cand-10494": "undecided",
        "cand-10495": "new", "cand-11526": "undecided",
    }
    for candidate_id, decision in expected.items():
        assert latest_alignment(alignments, candidate_id)["decision"] == decision

    new_manifest = [
        {"ku_id":"units/persons/azzo-marchese-deste-paduan-citizen","type":"person","canonical_name":"阿佐·德埃斯特侯爵（Azzo, Marchese d’Este）","name_en":"Azzo, Marchese d’Este","source_task":TASK,"card_path":"04-knowledge/units/persons/azzo-marchese-deste-paduan-citizen.md"},
        {"ku_id":"units/works/subleyras-pra-della-valle-plan-drawings","type":"work","canonical_name":"朱塞佩·苏布莱拉斯为梅莫普拉广场方案绘制的图稿组（Plans for Andrea Memmo’s Prà della Valle scheme by Giuseppe Subleyras）","name_en":"Plans for Andrea Memmo’s Prà della Valle scheme by Giuseppe Subleyras","source_task":TASK,"card_path":"04-knowledge/units/works/subleyras-pra-della-valle-plan-drawings.md"},
        {"ku_id":"units/archives/radicchio-descrizione-general-idea-pra-1786","type":"archive","canonical_name":"普拉广场方案说明（1786）（Description of the general idea for the Prà della Valle scheme, 1786）","name_en":"Description of the general idea for the Prà della Valle scheme, 1786","source_task":TASK,"card_path":"04-knowledge/units/archives/radicchio-descrizione-general-idea-pra-1786.md"},
        {"ku_id":"units/works/statue-of-azzo-marchese-deste-pra-della-valle","type":"work","canonical_name":"阿佐·德埃斯特侯爵纪念像（Statue of Azzo, Marchese d’Este）","name_en":"Statue of Azzo, Marchese d’Este","source_task":TASK,"card_path":"04-knowledge/units/works/statue-of-azzo-marchese-deste-pra-della-valle.md"},
        {"ku_id":"units/places/constantinople","type":"place","canonical_name":"君士坦丁堡（Constantinople）","name_en":"Constantinople","source_task":TASK,"card_path":"04-knowledge/units/places/constantinople.md"},
        {"ku_id":"units/events/andrea-memmo-constantinople-ambassadorship-1777","type":"event","canonical_name":"安德烈亚·梅莫驻君士坦丁堡大使任期（Andrea Memmo’s Constantinople ambassadorship）","name_en":"Andrea Memmo’s Constantinople ambassadorship","source_task":TASK,"card_path":"04-knowledge/units/events/andrea-memmo-constantinople-ambassadorship-1777.md"},
        {"ku_id":"units/works/piranesi-engraving-after-subleyras-pra-drawing","type":"work","canonical_name":"弗朗切斯科·皮拉内西所刻普拉广场图稿版画（Francesco Piranesi’s engraving after Subleyras’s drawing）","name_en":"Francesco Piranesi’s engraving after Subleyras’s drawing","source_task":TASK,"card_path":"04-knowledge/units/works/piranesi-engraving-after-subleyras-pra-drawing.md"},
    ]
    new_kus = {row["ku_id"] for row in new_manifest}
    assert len(new_kus) == len(new_manifest)
    assert not ({row["ku_id"] for row in manifest} & new_kus)
    for row in new_manifest:
        assert (ROOT / row["card_path"]).is_file(), row["card_path"]
    assert not any(row["type"] == "place" and ("Constantinople" in row["canonical_name"] or "君士坦丁堡" in row["canonical_name"]) for row in manifest)
    assert not any(row["type"] == "person" and "Azzo, Marchese d’Este" in row["name_en"] for row in manifest)
    assert not any(row["type"] == "work" and "Subleyras’s Prà della Valle scheme" in row["name_en"] for row in manifest)

    ku_for = {
        "cand-0981":"units/persons/azzo-marchese-deste-paduan-citizen",
        "cand-10478":"units/archives/radicchio-descrizione-general-idea-pra-1786",
        "cand-10486":"units/works/statue-of-azzo-marchese-deste-pra-della-valle",
        "cand-10491":"units/places/constantinople",
        "cand-10492":"units/events/andrea-memmo-constantinople-ambassadorship-1777",
        "cand-10494":"units/works/subleyras-pra-della-valle-plan-drawings",
        "cand-10495":"units/works/piranesi-engraving-after-subleyras-pra-drawing",
        "cand-11526":"units/archives/radicchio-descrizione-general-idea-pra-1786",
    }
    groups = {
        "cand-0981":"person-group-azzo-marchese-deste",
        "cand-10478":"archive-group-b70c266dc21d",
        "cand-10486":"workgrp-b448d6cbf81db1",
        "cand-10491":"sg3-place-cand-10491",
        "cand-10492":"sg3-event-cand-10492",
        "cand-10494":"workgrp-subleyras-pra-plan-group",
        "cand-10495":"workgrp-b5cac8fea2fa65",
    }
    for candidate_id, target in ku_for.items():
        row = latest_alignment(alignments, candidate_id)
        row["ku_id"] = target
        row["process_ref"] = PROCESS
        if candidate_id in ("cand-0981", "cand-10494"):
            old = row["resolution_note"]
            row.update(decision="new", resolution_note=(
                f"Previous S3 decision undecided; revised after source-context comparison for the registered relation endpoint. "
                f"source_ref=chp-15:15_CHP-15_sec_ii:l14-28; group={groups[candidate_id]}; "
                f"evidence=st-chp15-p366-azzo-statue-subject,st-chp15-p366-subleyras-drew-pra-plans,"
                f"st-chp15-p366-piranesi-engraves-subleyras-drawing; source-local identity only; "
                f"no ordinal, individual drawing, or external identity asserted. Prior note: {old}"
            ))
        elif candidate_id == "cand-11526":
            row.update(decision="same", resolution_note=(
                "S3 cross-chapter identity match: the p.366 account and the p.435 bibliography entry name Don Vincenzo "
                "Radicchio, date the work to 1786, and concern the same Prà della Valle project; p.365 note 2 cites "
                "Radicchio, 1786 for that project’s history. Map to the archive KU for cand-10478. This is an internal "
                "book-evidence match; the publication was not independently consulted."
            ))
        else:
            row["resolution_note"] += f" S4 registered in the p.365-366 endpoint batch: {groups[candidate_id]} maps to {target}; source-local scope only."

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_by_id["cand-0981"]["detail"] = "Haskell identifies Azzo, Marchese d’Este, and describes him as a Paduan citizen and originator of the House of Brunswick. Record a source-local person group only; no fuller name, ordinal, or external identity is asserted."
    candidate_by_id["cand-10478"]["detail"] = "Haskell’s p.365 note 2 cites Radicchio, 1786 for Prà della Valle history; the p.435 bibliography supplies the printed title, author, and Rome 1786. The p.366 account is matched to this work by author, year, and same project subject; the publication was not independently consulted."
    candidate_by_id["cand-10494"]["detail"] = "Source-local group of the plans that Haskell says Subleyras drew for Memmo’s Prà scheme. The passage supplies no count, title, or individual sheet identity; the later singular drawing is not identified as a specific group member."
    candidate_by_id["cand-10495"].update(canonical_name="Francesco Piranesi’s engraving after Giuseppe Subleyras’s drawing", detail="Haskell says Piranesi engraved Subleyras’s drawing. In the sentence, 1786 dates Radicchio’s account, not the engraving; no engraving date, title, or edition details are supplied.")
    candidate_by_id["cand-11526"]["detail"] = "S3 matched Haskell’s p.366 account to the full p.435 bibliography entry for Radicchio’s 1786 Prà della Valle publication by author, year, and subject. No independent publication consultation or physical inclusion with the engraving is claimed."

    manifest.extend(new_manifest)

    statements_path = TABLES / "book-statements.jsonl"
    statement_lines = statements_path.read_text(encoding="utf-8").splitlines()
    existing_statements = {json.loads(line)["statement_id"] for line in statement_lines if line.strip()}
    new_statements = [
        {
            "statement_id":"st-chp15-p366-memmo-ambassadorship-occurred-at-constantinople",
            "segment_id":"chp-15:15_CHP-15_sec_ii:l14-28",
            "subject_candidate_id":"cand-10492",
            "predicate":"ambassadorship_occurred_at_constantinople",
            "object_candidate_id":"cand-10491",
            "origin":"book",
            "qualifiers":{"source_line_start":20,"source_line_end":20,"printed_page":366,"pdf_physical_page":6,"claim":"Haskell locates Memmo’s ambassadorship in Constantinople.","speaker":"Haskell","text_layer":"authorial report","mentioned_candidate_ids":["cand-10492","cand-10491"],"qualification":"The source names the place in the office description; no modern geographic equivalence or exact dates are added.","relation_candidate":True},
            "original_quote":"as Ambassador in Constantinople",
            "source_file":SOURCE15,
        },
        {
            "statement_id":"st-chp15-p366-piranesi-engraving-derived-from-subleyras-drawing",
            "segment_id":"chp-15:15_CHP-15_sec_ii:l14-28",
            "subject_candidate_id":"cand-10495",
            "predicate":"piranesi_engraving_derived_from_subleyras_drawing",
            "object_candidate_id":"cand-10494",
            "origin":"book",
            "qualifiers":{"source_line_start":22,"source_line_end":22,"printed_page":366,"pdf_physical_page":6,"claim":"Haskell says Piranesi engraved a drawing by Subleyras.","speaker":"Haskell","text_layer":"authorial report","mentioned_candidate_ids":["cand-10495","cand-10494"],"qualification":"The preceding passage names Subleyras’s plans in the Prà scheme, but Haskell does not identify which individual sheet was engraved; keep the group-level identity and exact source-sheet relation distinct.","relation_candidate":True},
            "original_quote":"Francesco Piranesi engraved Subleyras’s drawing",
            "source_file":SOURCE15,
        },
    ]
    assert not (existing_statements & {row["statement_id"] for row in new_statements})
    # Confirm the endpoint names already have exact S2 mention anchors in the segment.
    segment = load_segment("chp-15:15_CHP-15_sec_ii:l14-28")
    mention_by_id = {row["mention_id"]: row for row in mentions}
    for mention_id in ("m-chp15-p366-memmo-0037", "m-chp15-p366-memmo-0059", "m-chp15-p366-memmo-0058"):
        row = mention_by_id[mention_id]
        assert row["candidate_id"] in {"cand-10491", "cand-10494", "cand-10495"}
        assert segment[int(row["start_char"]):int(row["end_char"])] == row["surface_form"]
    statement_lines.extend(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in new_statements)

    new_edges = [
        ("units/archives/patrons-and-painters","units/archives/radicchio-descrizione-general-idea-pra-1786","cites","","bibliographic citation","Haskell’s p.365 note 2 citation, identified by the p.435 bibliography; cited publication not independently consulted","formal","Chapter 15, printed p.365 note 2, L92; statement=st-chp15-p365-note2-radicchio-1786; Chapter 21, printed p.435, L1026",SOURCE15,"Haskell cites Radicchio, 1786 for the history of Prà della Valle. The chapter 21 bibliography supplies the cited title and printed author; this edge records citation only."),
        ("units/works/statue-of-azzo-marchese-deste-pra-della-valle","units/persons/william-henry-duke-of-gloucester","erected_by","by October 1777","erector","Haskell’s source-local Azzo statue at Prà della Valle","formal","Chapter 15, printed p.366, L18 and note 1 L27; statements=st-chp15-p366-duke-gloucester-azzo-statue,st-chp15-p366-note1-azzo-statue-erected-by-1777",SOURCE15,"Haskell says the Duke erected the statue; note 1 reports it had been erected by October 1777. The cited letter was not independently consulted; no exact installation date or present survival is inferred."),
        ("units/works/statue-of-azzo-marchese-deste-pra-della-valle","units/persons/azzo-marchese-deste-paduan-citizen","has_subject","","depicted person","Haskell’s statue of Azzo, Marchese d’Este","formal","Chapter 15, printed p.366, L18; statement=st-chp15-p366-azzo-statue-subject",SOURCE15,"The statue is explicitly described as a statue of Azzo, Marchese d’Este. The person unit preserves Haskell’s source-local name and does not assign an ordinal or external identity."),
        ("units/works/statue-of-azzo-marchese-deste-pra-della-valle","units/places/pra-della-valle","located_at","by October 1777","reported location","Haskell’s note 1 describes the statue as in the Prato della Valle","formal","Chapter 15, printed p.366, note 1 L27; statement=st-chp15-p366-note1-azzo-statue-erected-by-1777",SOURCE15,"Haskell’s note reports a drawing request for the statue in the Prato della Valle and says it had been erected by October 1777. The cited correspondence was not independently consulted."),
        ("units/events/andrea-memmo-constantinople-ambassadorship-1777","units/persons/andrea-memmo","has_participant","1777 departure; four-year duration as reported","ambassador in Constantinople","Haskell’s description of Memmo’s diplomatic posting","formal","Chapter 15, printed p.366, L20; statement=st-chp15-p366-memmo-left-as-ambassador-1777",SOURCE15,"Haskell identifies Memmo as the ambassador and reports a 1777 departure and four-year duration; exact start and end dates are not supplied."),
        ("units/events/andrea-memmo-constantinople-ambassadorship-1777","units/places/constantinople","occurred_at","reported four-year period","ambassadorial location","Haskell’s description of the Constantinople posting","formal","Chapter 15, printed p.366, L20; statement=st-chp15-p366-memmo-ambassadorship-occurred-at-constantinople",SOURCE15,"The source names Constantinople in the office description; no modern place-name equivalence or exact dates are inferred."),
        ("units/works/subleyras-pra-della-valle-plan-drawings","units/persons/giuseppe-subleyras","created_by","","draughtsman","Haskell’s plans for Memmo’s Prà scheme","formal","Chapter 15, printed p.366, L20–21; statement=st-chp15-p366-subleyras-drew-pra-plans",SOURCE15,"Haskell says Subleyras drew the plans. The KU represents the source-defined plan group; no count, title, or individual sheet is claimed."),
        ("units/works/piranesi-engraving-after-subleyras-pra-drawing","units/persons/francesco-piranesi","created_by","","engraver","Haskell’s account of the engraving","formal","Chapter 15, printed p.366, L22; statement=st-chp15-p366-piranesi-engraves-subleyras-drawing",SOURCE15,"Haskell explicitly names Francesco Piranesi as the engraver. The nearby 1786 date belongs to Radicchio’s account, not a verified engraving date."),
        ("units/archives/radicchio-descrizione-general-idea-pra-1786","units/persons/don-vincenzo-radicchio","authored_by","","author","The 1786 Radicchio account matched to the chapter 21 bibliography","formal","Chapter 15, printed p.366, L22; Chapter 21, printed p.435, L1026; statement=st-chp15-p366-radicchio-account-authored-by",SOURCE15,"Haskell names Radicchio as the account’s author. The book bibliography records the same author, year, and Prà project publication; no independent consultation is claimed."),
        ("units/archives/radicchio-descrizione-general-idea-pra-1786","units/works/piranesi-engraving-after-subleyras-pra-drawing","part_of","","described as an accompanying account","Haskell’s account/engraving description; physical or publishing relationship not verified","pending","Chapter 15, printed p.366, L22; statement=st-chp15-p366-radicchio-account-accompanies-engraving",SOURCE15,"Haskell says the account was written to accompany the engraving, but this does not establish that the account was included in the same edition or physically formed part of it. Keep part_of pending."),
        ("units/persons/azzo-marchese-deste-paduan-citizen","units/places/pra-della-valle","located_at","","citizen (not residence)","Haskell describes Azzo as a Paduan citizen; citizenship is not treated as residence or physical location","pending","Chapter 15, printed p.366, L18; statement=st-chp15-p366-azzo-described-as-paduan-citizen",SOURCE15,"The source calls Azzo a Paduan citizen. This does not establish residence or a physical location; located_at remains pending and is not formalized."),
        ("units/works/piranesi-engraving-after-subleyras-pra-drawing","units/works/subleyras-pra-della-valle-plan-drawings","derived_from","","source drawing; exact sheet unresolved","Haskell’s singular drawing and preceding plural plan group","pending","Chapter 15, printed p.366, L20–22; statement=st-chp15-p366-piranesi-engraving-derived-from-subleyras-drawing",SOURCE15,"Haskell says Piranesi engraved a Subleyras drawing after describing Subleyras’s plans, but does not identify the exact sheet; derived_from remains pending at this group granularity."),
    ]
    relation_id_max = max(int(row["relation_id"][4:]) for row in relations)
    existing_keys = {(r["subject_ku_id"],r["predicate"],r["object_ku_id"],r["time"],r["role"],r["scope"]) for r in relations}
    appended_relations = []
    for index, edge in enumerate(new_edges, 1):
        subject, obj, predicate, time, role, scope, status, span, source_file, note = edge
        natural_key = (subject,predicate,obj,time,role,scope)
        assert natural_key not in existing_keys, f"duplicate relation edge: {natural_key}"
        existing_keys.add(natural_key)
        appended_relations.append({"relation_id":f"rel-{relation_id_max+index}","subject_ku_id":subject,"object_ku_id":obj,"predicate":predicate,"time":time,"role":role,"scope":scope,"origin":"book","status":status,"source_id":source_id,"source_span":span,"source_file":source_file,"note":note})
    relations.extend(appended_relations)

    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    accepted_raw = accepted_path.read_text(encoding="utf-8-sig")
    accepted_data = yaml.safe_load(accepted_raw)
    accepted_units = accepted_data["units"]
    paths = [row["card_path"] for row in new_manifest]
    assert not (set(accepted_units) & set(paths))
    assert "claims:" in accepted_raw and accepted_raw.startswith("units:")
    unit_block, remainder = accepted_raw.split("claims:", 1)
    accepted_text = unit_block + "".join(f"- {path}\n" for path in paths) + "claims:" + remainder

    statement_bytes = ("\n".join(statement_lines) + "\n").encode("utf-8")
    writes = {
        cand_path: csv_bytes(candidates, cand_fields, cand_bom, cand_nl),
        aln_path: csv_bytes(alignments, aln_fields, aln_bom, aln_nl),
        manifest_path: csv_bytes(manifest, manifest_fields, manifest_bom, manifest_nl),
        relation_path: csv_bytes(relations, relation_fields, relation_bom, relation_nl),
        statements_path: statement_bytes,
        accepted_path: accepted_text.encode("utf-8"),
    }
    print("Reviewed batch plan: S3 undecided→new: cand-0981,cand-10494; cand-11526 undecided→same cand-10478; S4 new KU: 7; S2 relation statements added: 2; S6 relations: 9 formal, 3 pending; 2 additional pending outcomes remain in process log because no accurate controlled predicate/destination is available.")
    if not args.apply:
        print("Dry run only; no files written. Pass --apply to write this exact batch.")
        return 0
    write_bundle(writes)
    print("Applied and byte-verified: entity-candidates.csv, alignment.csv, ku-manifest.csv, relations.csv, book-statements.jsonl, accepted.yml.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
