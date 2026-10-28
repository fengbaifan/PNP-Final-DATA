#!/usr/bin/env python3
"""Guarded S3 identity repair and S4/S6 registration for the Parma dukes batch.

Default mode is read-only. Use --apply only after reviewing the planned rows.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
BATCH = "s4-s5-s6-parma-dukes-letter-20261028"
RECOVERY = ROOT / "06-runtime" / "recovery" / BATCH

ARCHIVE_KU = "units/archives/oliva-letter-to-ranuccio-parma-september-1679-excerpt"
ARCHIVE_CARD = "04-knowledge/units/archives/oliva-letter-to-ranuccio-parma-september-1679-excerpt.md"
ODOARDO_KU = "units/persons/odoardo-farnese-duke-of-parma"
ODOARDO_CARD = "04-knowledge/units/persons/odoardo-farnese-duke-of-parma.md"
RANUCCIO_KU = "units/persons/duke-parma-ghezzi"
GESU_KU = "units/places/gesu-rome"
WAR_KU = "units/events/first-war-of-castro"
OLIVA_KU = "units/persons/gian-paolo-oliva"
SOURCE_ID = "haskell-1980-rev-ed"

RELATIONS_TO_ADD = [
    {
        "relation_id": "rel-2503",
        "subject_ku_id": ARCHIVE_KU,
        "object_ku_id": OLIVA_KU,
        "predicate": "authored_by",
        "time": "September 1679 (Haskell's report)",
        "role": "Author named by Haskell",
        "scope": "Records the author attribution of the letter excerpt quoted by Haskell; the manuscript and any complete version are not identified.",
        "origin": "book",
        "status": "formal",
        "source_id": SOURCE_ID,
        "source_span": "Chapter 3, printed p.80, line 46; PDF physical p.22; statement=st-chp3-seciv-l35-46-oliva-september-1679-letter-fragment",
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
        "note": "Haskell says Oliva wrote the quoted letter in September 1679. This is a source-bounded author attribution, not a claim that the manuscript was consulted.",
    },
    {
        "relation_id": "rel-2504",
        "subject_ku_id": ARCHIVE_KU,
        "object_ku_id": RANUCCIO_KU,
        "predicate": "addressed_to",
        "time": "September 1679 (Haskell's report)",
        "role": "Addressee",
        "scope": "Records the Duke of Parma addressed in Oliva's quoted letter; the letter excerpt is not represented as a complete document.",
        "origin": "book",
        "status": "formal",
        "source_id": SOURCE_ID,
        "source_span": "Chapter 3, printed pp.80-81, lines 46 and 49; PDF physical pp.22-23; statements=st-chp3-seciv-l35-46-oliva-september-1679-letter-fragment,st-chp3-seciv-l48-56-letter-foundation-claim",
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
        "note": "The passage addresses the Duke of Parma; Haskell's text names Ranuccio's reaction immediately after the quotation, and index F.csv#12 locates Ranuccio II at pp.80-81.",
    },
    {
        "relation_id": "rel-2505",
        "subject_ku_id": ARCHIVE_KU,
        "object_ku_id": GESU_KU,
        "predicate": "has_subject",
        "time": "September 1679 (Haskell's report)",
        "role": "Church and tribune described in the letter",
        "scope": "Records the Gesù and its unfinished tribune as subjects of the quoted letter; claims about foundation rights remain Oliva's rhetorical appeal, not independently verified facts.",
        "origin": "book",
        "status": "formal",
        "source_id": SOURCE_ID,
        "source_span": "Chapter 3, printed p.81, line 49; PDF physical p.23; statement=st-chp3-seciv-l48-56-letter-foundation-claim",
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
        "note": "Haskell quotes Oliva describing the Gesù and its tribune. The edge concerns the letter's subject matter, not independent confirmation of its claims.",
    },
    {
        "relation_id": "rel-2506",
        "subject_ku_id": WAR_KU,
        "object_ku_id": ODOARDO_KU,
        "predicate": "has_participant",
        "time": "",
        "role": "Party to the dispute named by Haskell",
        "scope": "Records only Haskell's characterization of the War of Castro as a dispute with the Duke of Parma; it does not assign military command, excommunication, occupation, territorial authority, or ownership to Odoardo.",
        "origin": "book",
        "status": "formal",
        "source_id": SOURCE_ID,
        "source_span": "Chapter 2, printed p.58, line 3; PDF physical p.47; statement=st-chp2-secvii-l3-3-parma-consequences-fragment",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_vii.md",
        "note": "Haskell introduces the War of Castro in 1641 and calls it a dispute with the Duke of Parma. Index F.csv#11 identifies the duke at p.58 as Odoardo; this edge preserves only the stated dispute role.",
    },
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    if not reader.fieldnames:
        raise SystemExit(f"missing CSV header: {path}")
    return list(reader.fieldnames), list(reader), bom, newline


def write_csv(headers, rows, bom: bool, newline: str) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, extrasaction="ignore", lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    payload = buffer.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + payload) if bom else payload


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def unique_row(rows: list[dict[str, str]], field: str, value: str) -> dict[str, str]:
    matches = [row for row in rows if row.get(field) == value]
    if len(matches) != 1:
        raise SystemExit(f"expected exactly one {field}={value}; found {len(matches)}")
    return matches[0]


def insert_accepted(text: str, paths: list[str]) -> str:
    lines = text.splitlines()
    for path in paths:
        if any(line.strip() == f"- {path}" for line in lines):
            raise SystemExit(f"accepted.yml already contains {path}")
    for path in sorted(paths):
        candidates = [i for i, line in enumerate(lines)
                      if line.startswith("- 04-knowledge/units/") and line[2:] > path]
        at = candidates[0] if candidates else next(
            (i for i, line in enumerate(lines) if line in {"claims:", "redirects:"}), len(lines)
        )
        lines.insert(at, f"- {path}")
    return "\n".join(lines) + "\n"


def make_card(title: str, name_en: str, type_name: str, card_source_file: str,
              source_entries: list[dict], body: str, process_ref: str) -> str:
    sources = yaml.safe_dump(source_entries, allow_unicode=True, sort_keys=False).rstrip()
    return (
        "---\n"
        f"title: {json.dumps(title, ensure_ascii=False)}\n"
        f"name_en: {json.dumps(name_en, ensure_ascii=False)}\n"
        f"type: {type_name}\n"
        "created: '2026-10-28'\n"
        "updated: '2026-10-28'\n"
        "evidence_status: source_backed\n"
        "sources:\n"
        + "\n".join("  " + line for line in sources.splitlines())
        + "\n"
        f"process_ref: {process_ref}\n"
        "---\n\n"
        + body
    )


def update_jsonl(path: Path, expected_updates: dict[str, dict]) -> bytes:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    output: list[str] = []
    seen: set[str] = set()
    for line in text.splitlines(keepends=True):
        ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        payload = line[:-len(ending)] if ending else line
        if not payload.strip():
            output.append(line)
            continue
        row = json.loads(payload)
        statement_id = row.get("statement_id")
        if statement_id in expected_updates:
            seen.add(statement_id)
            changes = expected_updates[statement_id]
            for key, value in changes.items():
                if key == "qualifiers":
                    row.setdefault("qualifiers", {}).update(value)
                else:
                    row[key] = value
            payload = json.dumps(row, ensure_ascii=False, separators=(",", ":"))
            ending = ending or newline
            output.append(payload + ending)
        else:
            output.append(line)
    if seen != set(expected_updates):
        raise SystemExit(f"statement update set mismatch; missing={sorted(set(expected_updates)-seen)}")
    result = "".join(output).encode("utf-8")
    return (b"\xef\xbb\xbf" + result) if bom else result


def validate_and_plan():
    candidate_path = TABLES / "entity-candidates.csv"
    candidate_fields, candidates, candidate_bom, candidate_nl = read_csv(candidate_path)
    cand_0996 = unique_row(candidates, "candidate_id", "cand-0996")
    cand_0998 = unique_row(candidates, "candidate_id", "cand-0998")
    cand_4905 = unique_row(candidates, "candidate_id", "cand-4905")
    cand_5238 = unique_row(candidates, "candidate_id", "cand-5238")
    if cand_0996["canonical_name"] != "Farnese, Odoardo, Duke of Parma":
        raise SystemExit("cand-0996 source identity changed")
    if cand_0998.get("sub_entry") != "and Gesù" or cand_0998["suggested_type"] != "place":
        raise SystemExit("cand-0998 is no longer the Gesù place index sub-entry")
    if cand_4905["candidate_source_ref"] != "chp-2:02_CHP-2_sec_vii:l3-3#L3":
        raise SystemExit("cand-4905 candidate scope changed")
    if cand_5238["suggested_type"] != "archive":
        raise SystemExit("cand-5238 is no longer an archive candidate")
    unique_row(candidates, "candidate_id", "cand-6788")
    cand_0996["detail"] = (
        "Haskell index F.csv#11 names Odoardo Farnese, Duke of Parma, at printed pp.58 and 146; "
        "the title-only references at those locators are aligned to this person."
    )
    cand_0998["detail"] = (
        "Index sub-entry 'and Gesù' under Ranuccio II; at pp.79-81 it points to the Church of the Gesù, "
        "not to a separate person or a relation object."
    )
    cand_4905["detail"] = (
        "Haskell names only the office/title in the p.91 passage. The p.58 title-only mention maps to "
        "Odoardo by F.csv#11 and the p.92 mentions map to Ranuccio II by F.csv#12; the p.91 mention "
        "has no direct index locator, so its personal identity remains unresolved."
    )
    cand_4905["candidate_source_ref"] = "chp-3:03_CHP-3_sec_iv:l152-163#L162"
    cand_5238["canonical_name"] = (
        "Haskell-quoted excerpt from Gian Paolo Oliva's September 1679 letter to the Duke of Parma"
    )
    cand_5238["detail"] = (
        "Source-bounded letter excerpt quoted across printed pp.80-81. The quoted text is not the complete "
        "letter and no manuscript, edition, repository, or original title is identified."
    )
    cand_5238["candidate_source_ref"] = "chp-3:03_CHP-3_sec_iv:l35-46#L46"
    candidate_bytes = write_csv(candidate_fields, candidates, candidate_bom, candidate_nl)

    align_path = TABLES / "alignment.csv"
    align_fields, alignments, align_bom, align_nl = read_csv(align_path)
    changes = {
        "aln-1331": {
            "ku_id": ODOARDO_KU,
            "decision": "new",
            "resolution_note": (
                "source_ref=candidate=cand-0996;index_entry=F.csv#11;index_pages=58,146;"
                "s2_mentions=m-chp2-secvii-l3-19-0004@02-sources/02-Markdown/02_CHP-2_sec_vii.md#L3[Duke of Parma],"
                "m-chp6-p146-025@02-sources/02-Markdown/06_CHP-6_sec_i.md#L3-11[Duke of Parma],"
                "m-chp6-p146-027[the Duke];group=sg3-person-cand-0996; "
                "New: the index explicitly identifies Odoardo Farnese at both source page locators. "
                "The separate Ranuccio II index entry does not include p.58 or p.146. "
                f"S4 registered as {ODOARDO_KU}; no external identity source was used."
            ),
        },
        "aln-1332": {
            "ku_id": RANUCCIO_KU,
            "decision": "same",
            "resolution_note": (
                "source_ref=candidate=cand-0997;index_entry=F.csv#12;index_pages=19,84,92;"
                "explicit_name=m-chp3-seciv-l75-81-0048[Duke Ranuccio];"
                "title_only_mentions=m-chp1-secii-0209@print_p.19,m-chp3-seciv-l35-46-0001,"
                "m-chp3-seciv-l35-46-0053,m-chp3-seciv-l165-177-0018,m-chp3-seciv-l165-177-0019;"
                "matched_manifest=units/persons/duke-parma-ghezzi;"
                "group=sg3-ku-units-persons-duke-parma-ghezzi; "
                "Same: Haskell index F.csv#12 explicitly names Ranuccio II at pp.19,84,92; the p.84 "
                "passage names him directly and the p.19 Ghezzi honor passage is the title-only reference "
                "listed under the same indexed person. The p.92 title references are in the same chapter "
                "episode and indexed under him. The stable KU path is retained; the grant date remains unknown."
            ),
        },
        "aln-1333": {
            "ku_id": GESU_KU,
            "decision": "same",
            "resolution_note": (
                "source_ref=F.csv#13;parent=F.csv#12 Ranuccio II, Duke of Parma;"
                "sub_entry=and Gesù;index_pages=79,80,81;"
                "matched_manifest=units/places/gesu-rome;group=sg3-ku-units-places-gesu-rome; "
                "Same: the sub-entry's 'and Gesù' refers to the Church of the Gesù explicitly named in "
                "the p.79-81 passage; reuse the existing same-type place KU. This index sub-entry is not "
                "a separate person or a formal relation assertion."
            ),
        },
        "aln-0104": {
            "ku_id": RANUCCIO_KU,
            "decision": "same",
            "resolution_note": (
                "source_ref=candidate=cand-3027;candidate_source_ref=04-knowledge/units/persons/duke-parma-ghezzi.md;"
                "s2_mention=m-chp1-secii-0209@02-sources/02-Markdown/01_CHP-1_sec_ii.md#L132-133[Duke of Parma];"
                "existing_KU_card=04-knowledge/units/persons/duke-parma-ghezzi.md;"
                "index_crosswalk=F.csv#12 Ranuccio II, Duke of Parma, p.19;"
                "group=sg3-ku-units-persons-duke-parma-ghezzi; "
                "Same: the title-only Duke who granted Ghezzi gentiluomo d'onore is the person indexed "
                "as Ranuccio II at p.19. No grant date is inferred; no new external source was accessed."
            ),
        },
        "aln-5088": {
            "ku_id": "",
            "decision": "undecided",
            "resolution_note": (
                "source_ref=candidate=cand-4905;candidate_source_ref=chp-3:03_CHP-3_sec_iv:l152-163#L162;"
                "remaining_mention=m-chp3-seciv-l152-163-0066@print_p.91[Duke of Parma];"
                "other_mentions_reassigned=m-chp2-secvii-l3-19-0004->cand-0996(F.csv#11,p.58),"
                "m-chp3-seciv-l165-177-0018,m-chp3-seciv-l165-177-0019->cand-0997(F.csv#12,p.92);"
                "group=sg3-person-cand-4905; "
                "Undecided: the title-only reference at p.91 is not itself listed in either index page locator, "
                "and the adjacent p.92 locator does not prove this earlier mention has the same referent. "
                "Do not merge without direct source evidence."
            ),
        },
        "aln-6964": {
            "ku_id": "",
            "decision": "undecided",
            "resolution_note": (
                "source_ref=candidate=cand-6788;candidate_source_ref=chp-7:07_CHP-7_sec_i:l150-158#L154;"
                "s2_mention=m-chp7-p182-b-019@02-sources/02-Markdown/07_CHP-7_sec_i.md#L150-158[Duke of Parma];"
                "group=sg3-person-cand-6788; "
                "Undecided: Haskell supplies only the title and 1645 episode; neither F.csv#11 nor #12 "
                "lists p.182. No direct personal identity is given, so do not infer Odoardo or Ranuccio."
            ),
        },
        "aln-5421": {
            "ku_id": ARCHIVE_KU,
            "decision": "new",
            "resolution_note": (
                "source_ref=candidate_ref=chp-3:03_CHP-3_sec_iv:l35-46#L46;"
                "continuation=chp-3:03_CHP-3_sec_iv:l48-56#L49;"
                "statements=st-chp3-seciv-l35-46-oliva-september-1679-letter-fragment,"
                "st-chp3-seciv-l48-56-letter-foundation-claim;"
                "group=archive-group-35967258e350; "
                "New: register only Haskell's quoted September 1679 letter excerpt; do not imply a complete "
                "letter, manuscript, edition, repository, or original title. "
                f"S4 registered as {ARCHIVE_KU}."
            ),
        },
    }
    for alignment_id, expected in {
        "aln-1331": ("cand-0996", "same", RANUCCIO_KU),
        "aln-1332": ("cand-0997", "same", RANUCCIO_KU),
        "aln-1333": ("cand-0998", "undecided", ""),
        "aln-0104": ("cand-3027", "same", RANUCCIO_KU),
        "aln-5088": ("cand-4905", "same", RANUCCIO_KU),
        "aln-6964": ("cand-6788", "same", RANUCCIO_KU),
        "aln-5421": ("cand-5238", "new", ""),
    }.items():
        row = unique_row(alignments, "alignment_id", alignment_id)
        if (row.get("candidate_id"), row.get("decision"), row.get("ku_id")) != expected:
            raise SystemExit(f"unexpected baseline alignment row: {alignment_id}")
        row.update(changes[alignment_id])
    # Existing group rows are checked explicitly to prevent accidental group fan-out.
    if sum("group=sg3-ku-units-persons-duke-parma-ghezzi" in r.get("resolution_note", "")
           for r in alignments if r.get("decision") == "same") < 2:
        raise SystemExit("Ranuccio same-group candidates are incomplete")
    alignment_bytes = write_csv(align_fields, alignments, align_bom, align_nl)

    mention_path = TABLES / "mentions.csv"
    mention_fields, mentions, mention_bom, mention_nl = read_csv(mention_path)
    mention_changes = {
        "m-chp2-secvii-l3-19-0004": (
            "cand-4905", "cand-0996",
            "Title-only Duke of Parma; Haskell index F.csv#11 identifies Odoardo Farnese at printed p.58."
        ),
        "m-chp3-seciv-l165-177-0018": (
            "cand-4905", "cand-0997",
            "Title-only Duke of Parma; Haskell index F.csv#12 identifies Ranuccio II at printed p.92."
        ),
        "m-chp3-seciv-l165-177-0019": (
            "cand-4905", "cand-0997",
            "Title-only Duke of Parma; Haskell index F.csv#12 identifies Ranuccio II at printed p.92."
        ),
        "m-chp6-p146-025": (
            "cand-0996", "cand-0996",
            "Haskell index F.csv#11 identifies the title-only Duke at printed p.146 as Odoardo Farnese."
        ),
    }
    for mention_id, (old_candidate, new_candidate, note) in mention_changes.items():
        row = unique_row(mentions, "mention_id", mention_id)
        if row.get("candidate_id") != old_candidate:
            raise SystemExit(f"unexpected baseline candidate for {mention_id}")
        row["candidate_id"] = new_candidate
        row["note"] = note
    mention_bytes = write_csv(mention_fields, mentions, mention_bom, mention_nl)

    statement_updates = {
        "st-chp2-secvii-l3-3-parma-consequences-fragment": {
            "object_candidate_id": "cand-0996",
        },
        "st-chp3-seciv-l165-177-duke-refused-tribune-permission": {
            "subject_candidate_id": "cand-0997",
            "qualifiers": {
                "qualification": (
                    "Haskell index F.csv#12 identifies the title-only Duke on printed p.92 as Ranuccio II; "
                    "the decision's date and legal scope are not specified."
                )
            },
        },
        "st-chp3-seciv-l165-177-letters-carried-complaints-to-duke": {
            "object_candidate_id": "cand-0997",
            "qualifiers": {
                "qualification": (
                    "The title-only Duke maps to Ranuccio II via Haskell index F.csv#12, p.92. The source "
                    "does not identify who informed him or say the earlier signed and anonymous letters "
                    "were the source of these allegations; the subject endpoint remains open."
                ),
                "mentioned_candidate_ids": ["cand-0997", "cand-5200"],
            },
        },
        "st-chp6-p146-castro-location": {
            "qualifiers": {
                "qualification": (
                    "The Haskell index F.csv#11 identifies the Duke at p.146 as Odoardo Farnese. The source "
                    "states ducal belonging; the relation still cannot distinguish historical territorial "
                    "authority from ownership."
                )
            }
        },
    }
    statements_path = TABLES / "book-statements.jsonl"
    statements_bytes = update_jsonl(statements_path, statement_updates)

    manifest_path = TABLES / "ku-manifest.csv"
    manifest_fields, manifest, manifest_bom, manifest_nl = read_csv(manifest_path)
    for ku_id, card_path in ((ARCHIVE_KU, ARCHIVE_CARD), (ODOARDO_KU, ODOARDO_CARD)):
        if any(row.get("ku_id") == ku_id or row.get("card_path") == card_path for row in manifest):
            raise SystemExit(f"target manifest entry already exists: {ku_id}")
        if (ROOT / card_path).exists():
            raise SystemExit(f"target card already exists: {card_path}")
    if any(row.get("name_en", "").casefold() == name.casefold()
           for row in manifest
           for name in ("Excerpt from Gian Paolo Oliva's letter to Ranuccio II, Duke of Parma (September 1679)",
                        "Odoardo Farnese, Duke of Parma")
           if row.get("type") in {"archive", "person"}):
        raise SystemExit("a matching archive or person KU name already exists")
    unique_row(manifest, "ku_id", RANUCCIO_KU)["canonical_name"] = "帕尔马公爵拉努乔二世·法尔内塞"
    unique_row(manifest, "ku_id", RANUCCIO_KU)["name_en"] = "Ranuccio II Farnese, Duke of Parma"
    manifest.extend([
        {
            "ku_id": ARCHIVE_KU,
            "type": "archive",
            "canonical_name": "吉安·保罗·奥利瓦致帕尔马公爵拉努乔二世书信节录",
            "name_en": "Excerpt from Gian Paolo Oliva's letter to Ranuccio II, Duke of Parma (September 1679)",
            "source_task": "patrons-and-painters-full-book-s2",
            "card_path": ARCHIVE_CARD,
        },
        {
            "ku_id": ODOARDO_KU,
            "type": "person",
            "canonical_name": "帕尔马公爵奥多阿尔多·法尔内塞",
            "name_en": "Odoardo Farnese, Duke of Parma",
            "source_task": "patrons-and-painters-full-book-s2",
            "card_path": ODOARDO_CARD,
        },
    ])
    manifest_bytes = write_csv(manifest_fields, manifest, manifest_bom, manifest_nl)

    relations_path = TABLES / "relations.csv"
    relation_fields, relations, relation_bom, relation_nl = read_csv(relations_path)
    if [row.get("relation_id") for row in RELATIONS_TO_ADD] != [
        f"rel-{number:04d}" for number in range(2503, 2507)
    ]:
        raise SystemExit("unexpected reserved relation IDs")
    if any(row.get("relation_id") in {r["relation_id"] for r in RELATIONS_TO_ADD} for row in relations):
        raise SystemExit("one or more reserved relation IDs already exist")
    old_honour = unique_row(relations, "relation_id", "rel-0081")
    if (old_honour.get("subject_ku_id"), old_honour.get("object_ku_id"),
            old_honour.get("predicate")) != (RANUCCIO_KU, "units/persons/giuseppe-ghezzi", "honourer_of"):
        raise SystemExit("unexpected baseline Ranuccio/Ghezzi relation")
    old_honour.update({
        "scope": "Haskell's index identifies the title-only Duke on p.19 as Ranuccio II; the grant date remains unspecified.",
        "source_span": "Chapter 1, printed p.19, lines 132-133; Haskell index F.csv#12, Ranuccio II entry including p.19",
        "source_file": "02-sources/02-Markdown/01_CHP-1_sec_ii.md",
        "note": "Haskell says the Duke of Parma made Giuseppe Ghezzi a gentiluomo d’onore; index F.csv#12 identifies the p.19 Duke as Ranuccio II. No grant date is inferred.",
    })
    for new_row in RELATIONS_TO_ADD:
        duplicate = [
            row for row in relations
            if (row.get("subject_ku_id"), row.get("predicate"), row.get("object_ku_id"),
                row.get("time"), row.get("scope"))
            == (new_row["subject_ku_id"], new_row["predicate"], new_row["object_ku_id"],
                new_row["time"], new_row["scope"])
        ]
        if duplicate:
            raise SystemExit(f"natural-key duplicate for {new_row['relation_id']}: {duplicate[0]['relation_id']}")
        relations.append(new_row)
    type_registry = yaml.safe_load(
        (ROOT / ".agents" / "skills" / "ingest" / "references" / "relation-types.yml").read_text(encoding="utf-8")
    )
    ranges = yaml.safe_load((ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8"))
    controlled = set(type_registry.get("types", []))
    ku_types = {row["ku_id"]: row["type"] for row in manifest}
    for row in RELATIONS_TO_ADD:
        if row["predicate"] not in controlled:
            raise SystemExit(f"uncontrolled predicate: {row['predicate']}")
        domain_type = ku_types[row["subject_ku_id"]]
        range_type = ku_types[row["object_ku_id"]]
        specification = (ranges.get("domain_range") or {}).get(row["predicate"])
        if specification and (
            domain_type not in specification.get("domain", [])
            or range_type not in specification.get("range", [])
        ):
            raise SystemExit(
                f"domain/range mismatch for {row['predicate']}: {domain_type}->{range_type}"
            )
    relation_bytes = write_csv(relation_fields, relations, relation_bom, relation_nl)

    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    accepted_bytes = insert_accepted(
        accepted_path.read_text(encoding="utf-8-sig"),
        [ARCHIVE_CARD, ODOARDO_CARD],
    ).encode("utf-8")

    paths = {
        candidate_path: candidate_bytes,
        align_path: alignment_bytes,
        mention_path: mention_bytes,
        statements_path: statements_bytes,
        manifest_path: manifest_bytes,
        relations_path: relation_bytes,
        accepted_path: accepted_bytes,
    }
    print("planned structured changes:")
    for path, data in paths.items():
        old = path.read_bytes()
        print(f"- {path.relative_to(ROOT)}: {digest(old)[:12]} -> {digest(data)[:12]}")
    print("- candidate decisions: cand-0996 new; cand-0997 same; cand-0998 same; cand-4905 undecided; cand-6788 undecided; cand-5238 new")
    print("- new KU mappings: 2; new formal relations: 4; existing formal relation rel-0081 retained and re-scoped")
    print("- mentions reassigned: 3; statement versions revised: 4")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed changes")
    args = parser.parse_args()
    paths = validate_and_plan()
    if not args.apply:
        print("dry-run only; no files written")
        return
    RECOVERY.mkdir(parents=True, exist_ok=False)
    for path in paths:
        backup = RECOVERY / "original" / path.relative_to(ROOT)
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)
    for path, data in paths.items():
        atomic_write(path, data)
    print(f"applied; original bytes saved under {RECOVERY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
