#!/usr/bin/env python3
"""Classify and atomize p.114 S2 statements against the printed page."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
SOURCE_REL = "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l172-178"
PREVIOUS_SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l161-170"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_SHA256 = "9dda5638df8194e1c909fae78e71a2a9126168ebb261abdd9cdab03f24a4c59f"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "dbd5f9c3f9afc44df9f069bb0e449bd0a5569b56ec374c4a64833169ffc2c9a3",
    "entity-candidates.csv": "01eaae9a76cc32c5a12e78820594517a3382bbea6ac9447c121cd57bd141b1a2",
    "mentions.csv": "1300136c3dd1173dcb91c1ca44ae5556709ba1f08f7cea41c0987fbb4dddacea",
}
BACKUP_SUFFIX = "bak-s2-chp4-sec-ii-l172-178-relations-20261011"
ORIGINAL_IDS = {
    "st-chp4-sec-ii-p114-angeloni-friend-role",
    "st-chp4-sec-ii-p114-angeloni-position",
    "st-chp4-sec-ii-p114-angloni-objects",
    "st-chp4-sec-ii-p114-austerity-speculation",
    "st-chp4-sec-ii-p114-bellori-felibien",
    "st-chp4-sec-ii-p114-cassiano-inspiration",
    "st-chp4-sec-ii-p114-castiglione-drawings",
    "st-chp4-sec-ii-p114-classical-taste",
    "st-chp4-sec-ii-p114-classical-theorist",
    "st-chp4-sec-ii-p114-collection-fifty-poussins",
    "st-chp4-sec-ii-p114-heroic-copies",
    "st-chp4-sec-ii-p114-ideas-without-direct-interest",
    "st-chp4-sec-ii-p114-massimi-pictures",
    "st-chp4-sec-ii-p114-mola-titian",
    "st-chp4-sec-ii-p114-moses-title",
    "st-chp4-sec-ii-p114-next-generation",
    "st-chp4-sec-ii-p114-other-amateurs",
    "st-chp4-sec-ii-p114-poussin-debt",
    "st-chp4-sec-ii-p114-poussin-lustre",
    "st-chp4-sec-ii-p114-tempest-assessment",
    "st-chp4-sec-ii-p114-tempest-commission",
    "st-chp4-sec-ii-p114-workload-speculation",
}
NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11649",
        "canonical_name": "Approximately fifty Poussin paintings in Cassiano dal Pozzo’s collection",
        "suggested_type": "work",
        "detail": "Haskell reports ‘fifty or so Poussins’ in Cassiano’s collection; the count is approximate and individual paintings are not identified.",
        "candidate_source_ref": f"{SEGMENT_ID}#L173",
    },
    {
        "candidate_id": "cand-11650",
        "canonical_name": "Unidentified Roman group that had discovered the beauties of Titian",
        "suggested_type": "",
        "detail": "Haskell identifies Cassiano as part of a group in Rome but does not name or bound its other members; ‘discovered’ is the author’s characterization.",
        "candidate_source_ref": f"{SEGMENT_ID}#L174",
    },
    {
        "candidate_id": "cand-11651",
        "canonical_name": "Unnamed other amateur collectors who owned fine paintings",
        "suggested_type": "",
        "detail": "The source describes a collective of other amateurs but supplies no names or bounded membership.",
        "candidate_source_ref": f"{SEGMENT_ID}#L173",
    },
    {
        "candidate_id": "cand-11652",
        "canonical_name": "Unidentified fine paintings by Vouet, Pietro da Cortona, and Testa in amateur collections",
        "suggested_type": "work",
        "detail": "The passage refers to an unspecified group of fine paintings by the three named artists; no titles, count, or individual collection is identified.",
        "candidate_source_ref": f"{SEGMENT_ID}#L173",
    },
]
NEW_STATEMENT_IDS = {
    "st-chp4-sec-ii-p114-angeloni-carracci-drawings-owned",
    "st-chp4-sec-ii-p114-carracci-created-angeloni-drawings",
    "st-chp4-sec-ii-p114-cassiano-admired-sacraments",
    "st-chp4-sec-ii-p114-felibien-codified-enthusiasm",
    "st-chp4-sec-ii-p114-felibien-classical-theorist",
    "st-chp4-sec-ii-p114-contemporary-art-showing-without-poussin",
    "st-chp4-sec-ii-p114-cassiano-in-roman-titian-discovery-group",
    "st-chp4-sec-ii-p114-roman-group-discovered-titian",
    "st-chp4-sec-ii-p114-poussin-created-fifty-paintings",
    "st-chp4-sec-ii-p114-amateur-paintings-by-vouet",
    "st-chp4-sec-ii-p114-amateur-paintings-by-cortona",
    "st-chp4-sec-ii-p114-amateur-paintings-by-testa",
}
UPDATES = {
    "st-chp4-sec-ii-p114-angeloni-friend-role": {
        "relation": True,
        "predicate": "friend_of",
        "note": "The phrase explicitly identifies Angeloni as Cassiano’s friend; archaeologist is a separate role description, not an edge.",
    },
    "st-chp4-sec-ii-p114-angeloni-position": {"relation": False},
    "st-chp4-sec-ii-p114-angloni-objects": {
        "relation": True,
        "object": "cand-5931",
        "predicate": "had_medal_collection",
        "quote": "with his large collection of medals",
        "claim": "Haskell says Francesco Angeloni had a large collection of medals.",
        "mentioned": ["cand-0107", "cand-5931"],
        "qualification": "The collection’s type is unspecified; Carracci’s drawings are recorded in a separate ownership and authorship statement.",
        "note": "The source explicitly attributes a large medal collection to Angeloni.",
    },
    "st-chp4-sec-ii-p114-austerity-speculation": {
        "relation": True,
        "note": "Haskell’s question and ‘not altogether’ preserve speculation about Cassiano’s view of Poussin’s figure painting.",
    },
    "st-chp4-sec-ii-p114-bellori-felibien": {
        "relation": True,
        "note": "The source explicitly names Bellori and Félibien as codifying their enthusiasm for Poussin; this row is scoped to Bellori and a parallel row records Félibien.",
    },
    "st-chp4-sec-ii-p114-cassiano-inspiration": {
        "relation": True,
        "note": "Haskell’s ‘perhaps’ and ‘could’ preserve the qualified claim that Cassiano’s beliefs and culture inspired Poussin.",
    },
    "st-chp4-sec-ii-p114-castiglione-drawings": {
        "relation": True,
        "predicate": "derived_from",
        "note": "Haskell infers that Castiglione’s drawings derive from Cassiano’s paper museum; ‘must surely’ remains an authorial inference, not a commission or ownership claim.",
    },
    "st-chp4-sec-ii-p114-classical-taste": {"relation": False},
    "st-chp4-sec-ii-p114-classical-theorist": {
        "relation": True,
        "note": "Haskell says the critics focused on Poussin as a classical theorist; this row is scoped to Bellori and a parallel row records Félibien.",
    },
    "st-chp4-sec-ii-p114-collection-fifty-poussins": {
        "relation": True,
        "subject": "cand-5921",
        "object": "cand-11649",
        "predicate": "contains",
        "quote": "Without the fifty or so Poussins",
        "claim": "Haskell reports that Cassiano’s painting collection included approximately fifty Poussin pictures.",
        "mentioned": ["cand-2036", "cand-5921", "cand-11649", "cand-1984"],
        "qualification": "‘Fifty or so’ is approximate; ‘Poussins’ means paintings, not the artist. The following evaluation of contemporary art is a separate scalar statement.",
        "note": "The sentence presupposes the paintings’ presence in Cassiano’s collection; the count is approximate and no individual work is named.",
    },
    "st-chp4-sec-ii-p114-heroic-copies": {
        "relation": True,
        "subject": "cand-5935",
        "object": "cand-2036",
        "predicate": "owned_by",
        "note": "The source says Cassiano owned copies of two or three Poussin landscapes; the work group is the owned object and its count and quoted category remain qualified.",
    },
    "st-chp4-sec-ii-p114-ideas-without-direct-interest": {
        "relation": True,
        "open_reason": "The inspired artists are described only as ‘many artists’; the passage does not identify or bound the group.",
        "note": "Keep Haskell’s inspiration claim and the limit ‘not known to have taken a direct interest’; the artist-group endpoint remains open.",
    },
    "st-chp4-sec-ii-p114-massimi-pictures": {
        "relation": True,
        "predicate": "painted_for",
        "note": "Haskell explicitly says Poussin painted two pictures for Massimi after returning from Paris; the titles continue on p.115.",
    },
    "st-chp4-sec-ii-p114-mola-titian": {
        "relation": False,
        "object": None,
        "predicate": "landscapes_recall_roman_discovery",
        "qualification": "The comparison is authorial interpretation, not a direct relation between Mola and Titian. Cassiano’s membership in the unnamed Roman group and the group’s characterization are recorded separately.",
    },
    "st-chp4-sec-ii-p114-moses-title": {
        "relation": False,
        "object": None,
        "predicate": "named_work_title",
    },
    "st-chp4-sec-ii-p114-next-generation": {"relation": False},
    "st-chp4-sec-ii-p114-other-amateurs": {
        "relation": True,
        "subject": "cand-11652",
        "object": "cand-11651",
        "predicate": "owned_by",
        "mentioned": ["cand-11652", "cand-11651", "cand-2792", "cand-0342", "cand-2556"],
        "qualification": "The paintings and owners are unnamed groups; the named artists identify the makers represented in the work group, not individual paintings.",
        "note": "The passage states that other amateurs owned the described group of fine paintings; neither individual works nor owners are identified.",
    },
    "st-chp4-sec-ii-p114-poussin-debt": {
        "relation": True,
        "note": "Haskell reports Poussin’s acknowledged debt to Cassiano without identifying a specific letter or statement.",
    },
    "st-chp4-sec-ii-p114-poussin-lustre": {
        "relation": True,
        "note": "Retain Haskell’s figurative assessment that Poussin gave lustre to Cassiano’s painting collection.",
    },
    "st-chp4-sec-ii-p114-tempest-assessment": {"relation": False},
    "st-chp4-sec-ii-p114-tempest-commission": {
        "relation": True,
        "subject": "cand-5923",
        "object": "cand-2036",
        "predicate": "commissioned_by",
        "note": "Cassiano commissioned the Tempest from Poussin; the work is the commissioned object.",
    },
    "st-chp4-sec-ii-p114-workload-speculation": {
        "relation": True,
        "note": "Retain Haskell’s explicit speculation that Poussin’s workload may explain Cassiano’s relative neglect after Paris.",
    },
    "st-chp4-sec-ii-p113-taste-currents-fragment": {
        "open_reason": "The p.114 continuation completes the contrast with Court and religious Orders but still describes only abstract currents of taste and does not identify a bounded target group.",
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def segment_counts(rows: list[dict]) -> dict[str, int]:
    segment = [row for row in rows if row.get("segment_id") == SEGMENT_ID]
    dual = [row for row in segment if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    return {
        "statements": len(segment),
        "dual": len(dual),
        "relation_true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in segment),
        "relation_false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in segment),
        "dual_true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in dual),
        "dual_false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in dual),
        "open_relation": sum(
            row.get("qualifiers", {}).get("relation_candidate") is True
            and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
            for row in segment
        ),
        "unclassified": sum("relation_candidate" not in row.get("qualifiers", {}) for row in segment),
    }


def new_statement(statement_id: str, subject: str | None, predicate: str, object_: str | None,
                  quote: str, claim: str, line_start: int, line_end: int,
                  mentioned: list[str], relation: bool, qualification: str,
                  note: str | None = None) -> dict:
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "pdf_physical_page": 25,
        "printed_page_locator": "p.114",
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "mentioned_candidate_ids": mentioned,
        "qualification": qualification,
        "relation_candidate": relation,
    }
    if note:
        qualifiers["relation_candidate_note"] = note
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL,
    }


def make_new_statements(segment_text: str) -> list[dict]:
    quote_codified = "Both the Italian critic Bellori and the French historian Felibien codified their enthusiasm for Poussin into a dogma."
    quote_theorist = "They paid attention only to the classical theorist and tended increasingly to ignore the other sides to him which had been appreciated by Cassiano."
    quote_other_amateurs = "many other amateurs owned fine paintings by Vouet, Pietro da Cortona and Testa."
    quotes = [
        "his drawings by Annibale Carracci",
        "drawings by Annibale Carracci",
        "his special admiration of the Sacraments",
        quote_codified,
        quote_theorist,
        "contemporary art would certainly not have made a specially good showing there",
        "Cassiano was among that group in Rome",
        "that group in Rome which had ‘discovered’ the beauties of Titian",
        "fifty or so Poussins",
        "fine paintings by Vouet, Pietro da Cortona and Testa",
    ]
    for quote in quotes:
        if quote not in segment_text:
            raise SystemExit(f"preflight failed: new quote not found in source segment: {quote!r}")
    return [
        new_statement(
            "st-chp4-sec-ii-p114-angeloni-carracci-drawings-owned", "cand-5932", "owned_by", "cand-0107",
            "his drawings by Annibale Carracci", "Haskell describes the Carracci drawings as Angeloni’s.",
            173, 173, ["cand-5932", "cand-0107"], True,
            "The drawing group is attributed to Annibale Carracci in the immediately following phrase.",
            "Haskell explicitly associates the drawings with Angeloni’s collection.",
        ),
        new_statement(
            "st-chp4-sec-ii-p114-carracci-created-angeloni-drawings", "cand-5932", "created_by", "cand-0576",
            "drawings by Annibale Carracci", "Haskell identifies the drawings in Angeloni’s collection as by Annibale Carracci.",
            173, 173, ["cand-5932", "cand-0576"], True,
            "The passage identifies a group of drawings but does not identify individual sheets.",
            "The phrase ‘drawings by Annibale Carracci’ directly states authorship at group level.",
        ),
        new_statement(
            "st-chp4-sec-ii-p114-cassiano-admired-sacraments", "cand-2036", "admired", "cand-5789",
            "his special admiration of the Sacraments", "Haskell says Cassiano had special admiration for Poussin’s Sacraments series.",
            176, 176, ["cand-2036", "cand-5789"], True,
            "This is Haskell’s account of Cassiano’s response to the series, not an independently documented statement by Cassiano.",
            "The passage explicitly attributes special admiration of the Sacraments to Cassiano.",
        ),
        new_statement(
            "st-chp4-sec-ii-p114-felibien-codified-enthusiasm", "cand-1015", "codified_enthusiasm_into_dogma", "cand-1984",
            quote_codified, "Haskell says Félibien codified his enthusiasm for Poussin into dogma.",
            175, 175, ["cand-1015", "cand-1984"], True,
            "The shared source sentence names Bellori and Félibien; this row isolates Félibien’s stated role.",
            "The sentence explicitly attributes codification to Félibien as one of the two named critics.",
        ),
        new_statement(
            "st-chp4-sec-ii-p114-felibien-classical-theorist", "cand-1015", "focused_on_classical_theorist", "cand-1984",
            quote_theorist, "Haskell says Félibien focused on Poussin as a classical theorist and increasingly ignored other sides appreciated by Cassiano.",
            176, 176, ["cand-1015", "cand-1984", "cand-2036"], True,
            "‘They’ refers to Bellori and Félibien; this row isolates Félibien’s stated role.",
            "The source attributes the critical focus to both previously named critics, including Félibien.",
        ),
        new_statement(
            "st-chp4-sec-ii-p114-contemporary-art-showing-without-poussin", "cand-5921", "would_have_shown_poorly_without", None,
            "contemporary art would certainly not have made a specially good showing there",
            "Haskell judges that contemporary art in the collection would have shown poorly without the approximately fifty Poussin paintings.",
            173, 173, ["cand-5921", "cand-11649"], False,
            "This is Haskell’s evaluative counterfactual, separate from the collection-content relation.",
        ),
        new_statement(
            "st-chp4-sec-ii-p114-cassiano-in-roman-titian-discovery-group", "cand-2036", "member_of", "cand-11650",
            "Cassiano was among that group in Rome", "Haskell places Cassiano among an unnamed Roman group that had discovered the beauties of Titian.",
            174, 174, ["cand-2036", "cand-11650", "cand-4490"], True,
            "The other group members are not identified; ‘discovered’ is Haskell’s characterization.",
            "The phrase explicitly says Cassiano was among the group.",
        ),
        new_statement(
            "st-chp4-sec-ii-p114-roman-group-discovered-titian", "cand-11650", "discovered_the_beauties_of", "cand-2630",
            "that group in Rome which had ‘discovered’ the beauties of Titian",
            "Haskell characterizes an unnamed Roman group as having discovered the beauties of Titian.",
            174, 174, ["cand-11650", "cand-4490", "cand-2630"], True,
            "‘Discovered’ is retained as Haskell’s account of aesthetic reception, not a claim of first contact with Titian’s works.",
            "The clause explicitly attributes this aesthetic reception to the unnamed group.",
        ),
        new_statement(
            "st-chp4-sec-ii-p114-poussin-created-fifty-paintings", "cand-11649", "created_by", "cand-1984",
            "fifty or so Poussins", "Haskell’s plural ‘Poussins’ refers to approximately fifty paintings by Nicolas Poussin in Cassiano’s collection.",
            173, 173, ["cand-11649", "cand-1984"], True,
            "‘Fifty or so’ is approximate; the individual paintings are not identified.",
            "The plural surname identifies the paintings as works by Poussin.",
        ),
        new_statement(
            "st-chp4-sec-ii-p114-amateur-paintings-by-vouet", "cand-11652", "includes_works_by", "cand-2792",
            "fine paintings by Vouet, Pietro da Cortona and Testa", "The unnamed painting group includes fine paintings by Simon Vouet, according to Haskell.",
            173, 173, ["cand-11652", "cand-2792"], True,
            "The source names no individual painting; the group-level relation does not assert that every work was by Vouet.",
            "The source explicitly includes paintings by Vouet in the group owned by other amateurs.",
        ),
        new_statement(
            "st-chp4-sec-ii-p114-amateur-paintings-by-cortona", "cand-11652", "includes_works_by", "cand-0342",
            "fine paintings by Vouet, Pietro da Cortona and Testa", "The unnamed painting group includes fine paintings by Pietro da Cortona, according to Haskell.",
            173, 173, ["cand-11652", "cand-0342"], True,
            "The source names no individual painting; the group-level relation does not assert that every work was by Pietro da Cortona.",
            "The source explicitly includes paintings by Pietro da Cortona in the group owned by other amateurs.",
        ),
        new_statement(
            "st-chp4-sec-ii-p114-amateur-paintings-by-testa", "cand-11652", "includes_works_by", "cand-2556",
            "fine paintings by Vouet, Pietro da Cortona and Testa", "The unnamed painting group includes fine paintings by Pietro Testa, according to Haskell.",
            173, 173, ["cand-11652", "cand-2556"], True,
            "The source names no individual painting; the group-level relation does not assert that every work was by Testa.",
            "The source explicitly includes paintings by Testa in the group owned by other amateurs.",
        ),
    ]


def csv_bytes(path: Path, rows: list[dict]) -> bytes:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        fields = next(csv.reader([handle.readline().lstrip("\ufeff")]))
    import io
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def canonicalize_current(paths: dict[str, Path]) -> None:
    expected = {
        "book-statements.jsonl": "019861df5cc78faac93ffa1c3703a9f5cf23cf7327e984a0a637fdc9afd98e6f",
        "entity-candidates.csv": "e58dc895ff143d6aa8f04e9205afc0cbfa7556d9ceab0afa803ab9212bfb8a5d",
        "mentions.csv": "cde2f213f816368f177678867fbbfe37a1d4f3b35cb98ee2bd649cd7529ed398",
    }
    for name, path in paths.items():
        if sha(path.read_bytes()) != expected[name]:
            raise SystemExit(f"canonicalization refused: unexpected current {name} SHA-256")
    statements = read_jsonl(paths["book-statements.jsonl"])
    with paths["entity-candidates.csv"].open(encoding="utf-8-sig", newline="") as handle:
        candidates = list(csv.DictReader(handle))
    with paths["mentions.csv"].open(encoding="utf-8-sig", newline="") as handle:
        mentions = list(csv.DictReader(handle))
    if len(statements) != 13044 or len(candidates) != 11630 or len(mentions) != 27568:
        raise SystemExit("canonicalization refused: current logical table totals changed")
    if segment_counts(statements) != {
        "statements": 34, "dual": 27, "relation_true": 27, "relation_false": 7,
        "dual_true": 26, "dual_false": 1, "open_relation": 1, "unclassified": 0,
    }:
        raise SystemExit("canonicalization refused: p.114 statement content changed")
    outputs = {
        paths["book-statements.jsonl"]: ("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in statements)).encode("utf-8"),
        paths["entity-candidates.csv"]: csv_bytes(paths["entity-candidates.csv"], candidates),
        paths["mentions.csv"]: csv_bytes(paths["mentions.csv"], mentions),
    }
    backups = {path: path.with_name(f"{path.name}.bak-s2-chp4-p114-formatfix-20261011") for path in outputs}
    temps = {path: path.with_name(f"{path.name}.p114-canonical.tmp") for path in outputs}
    if any(path.exists() for path in [*backups.values(), *temps.values()]):
        raise SystemExit("canonicalization refused: recovery or temporary file already exists")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    try:
        for path, data in outputs.items():
            temps[path].write_bytes(data)
        for path in outputs:
            os.replace(temps[path], path)
        written_statements = read_jsonl(paths["book-statements.jsonl"])
        with paths["entity-candidates.csv"].open(encoding="utf-8", newline="") as handle:
            written_candidates = list(csv.DictReader(handle))
        with paths["mentions.csv"].open(encoding="utf-8", newline="") as handle:
            written_mentions = list(csv.DictReader(handle))
        if (written_statements, written_candidates, written_mentions) != (statements, candidates, mentions):
            raise RuntimeError("canonicalization changed logical table values")
        if any(path.read_bytes().startswith(b"\xef\xbb\xbf") for path in (paths["entity-candidates.csv"], paths["mentions.csv"])):
            raise RuntimeError("canonical CSV must preserve the no-BOM source format")
    except Exception:
        for path, backup in backups.items():
            if backup.exists():
                shutil.copy2(backup, path)
        for temp in temps.values():
            temp.unlink(missing_ok=True)
        raise
    print(json.dumps({
        "canonicalization": "success",
        "logical_rows_unchanged": True,
        "sha256": {path.name: sha(path.read_bytes()) for path in outputs},
        "recovery_copies": [path.name for path in backups.values()],
    }, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the validated p.114 statement, candidate, and mention changes")
    parser.add_argument("--canonicalize-current", action="store_true", help="restore canonical table serialization after a validated p.114 write")
    args = parser.parse_args()
    paths = {
        "book-statements.jsonl": TABLES / "book-statements.jsonl",
        "entity-candidates.csv": TABLES / "entity-candidates.csv",
        "mentions.csv": TABLES / "mentions.csv",
    }
    if args.canonicalize_current:
        if args.apply:
            raise SystemExit("choose only one of --apply and --canonicalize-current")
        canonicalize_current(paths)
        return
    for name, path in paths.items():
        if sha(path.read_bytes()) != EXPECTED_SHA256[name]:
            raise SystemExit(f"preflight failed: unexpected {name} SHA-256")
    if sha(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise SystemExit("preflight failed: source file changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[171:178])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("preflight failed: p.114 segment changed")
    manifests = read_jsonl(TABLES / "segments.jsonl")
    manifest = [row for row in manifests if row.get("segment_id") == SEGMENT_ID]
    if len(manifest) != 1 or manifest[0].get("sha256") != SEGMENT_SHA256:
        raise SystemExit("preflight failed: segment manifest changed")

    statement_path, candidate_path, mention_path = paths.values()
    statements = read_jsonl(statement_path)
    with candidate_path.open(encoding="utf-8-sig", newline="") as handle:
        candidates = list(csv.DictReader(handle))
    with mention_path.open(encoding="utf-8-sig", newline="") as handle:
        mentions = list(csv.DictReader(handle))
    current = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(current) != 22 or {row["statement_id"] for row in current} != ORIGINAL_IDS:
        raise SystemExit("preflight failed: p.114 statement set changed")
    if len(statements) != 13032 or len(candidates) != 11626 or len(mentions) != 27565:
        raise SystemExit("preflight failed: unexpected table totals")
    if any(row.get("original_quote") not in segment_text for row in current):
        raise SystemExit("preflight failed: a current p.114 quote is not exact in the source segment")
    current_mentions = [row for row in mentions if row["segment_id"] == SEGMENT_ID]
    if len(current_mentions) != 43 or any(
        segment_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]
        for row in current_mentions
    ):
        raise SystemExit("preflight failed: p.114 mention set or spans changed")

    candidate_ids = {row["candidate_id"] for row in candidates}
    if max(int(value.removeprefix("cand-")) for value in candidate_ids) != 11648:
        raise SystemExit("preflight failed: candidate ID sequence changed")
    new_candidate_ids = {row["candidate_id"] for row in NEW_CANDIDATES}
    if candidate_ids.intersection(new_candidate_ids):
        raise SystemExit("preflight failed: a new candidate ID already exists")
    candidate_rows = []
    for entry in NEW_CANDIDATES:
        candidate_rows.append({
            "candidate_id": entry["candidate_id"], "index_entry_id": "",
            "canonical_name": entry["canonical_name"], "index_page_range": "",
            "suggested_type": entry["suggested_type"], "status": "open",
            "index_source_file": "", "sub_entry": "", "detail": entry["detail"],
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": entry["candidate_source_ref"],
        })

    by_id = {row["statement_id"]: row for row in statements}
    for statement_id, change in UPDATES.items():
        if statement_id not in by_id:
            raise SystemExit(f"preflight failed: missing statement {statement_id}")
        row = by_id[statement_id]
        if statement_id.startswith("st-chp4-sec-ii-p114-"):
            q = row["qualifiers"]
            q["relation_candidate"] = change["relation"]
            for key in ("subject", "object", "predicate", "quote", "claim"):
                if key not in change:
                    continue
                field = {"subject": "subject_candidate_id", "object": "object_candidate_id", "quote": "original_quote"}.get(key, key)
                if key == "claim":
                    q["claim"] = change[key]
                else:
                    row[field] = change[key]
            if "mentioned" in change:
                q["mentioned_candidate_ids"] = change["mentioned"]
            if "qualification" in change:
                q["qualification"] = change["qualification"]
            if change.get("relation") and "note" in change:
                q["relation_candidate_note"] = change["note"]
            if "open_reason" in change:
                q["open_endpoint_reason"] = change["open_reason"]
            elif "open_endpoint_reason" in q:
                del q["open_endpoint_reason"]
        else:
            row["qualifiers"]["open_endpoint_reason"] = change["open_reason"]

    id_to_candidate = {row["candidate_id"]: row for row in candidate_rows}
    new_statements = make_new_statements(segment_text)
    if {row["statement_id"] for row in new_statements} != NEW_STATEMENT_IDS:
        raise SystemExit("preflight failed: unexpected new statement identifiers")
    if any(row["statement_id"] in by_id for row in new_statements):
        raise SystemExit("preflight failed: a new statement ID already exists")
    for row in new_statements:
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_ids and endpoint not in new_candidate_ids:
                raise SystemExit(f"preflight failed: unresolved endpoint {endpoint}")
        for candidate_id in row["qualifiers"]["mentioned_candidate_ids"]:
            if candidate_id not in candidate_ids and candidate_id not in new_candidate_ids:
                raise SystemExit(f"preflight failed: unresolved mentioned candidate {candidate_id}")

    # Repair the plural-as-person mapping for the approximately fifty paintings.
    plural_mention = [row for row in current_mentions if row["mention_id"] == "m-chp4-sec-ii-p114-0042"]
    if len(plural_mention) != 1 or plural_mention[0]["candidate_id"] != "cand-5921":
        raise SystemExit("preflight failed: expected ‘fifty or so Poussins’ mention mapping changed")
    plural_mention[0]["candidate_id"] = "cand-11649"
    plural_mention[0]["note"] = "Metonym for approximately fifty Poussin paintings in Cassiano’s collection, not the artist or the collection itself."
    new_mention_specs = [
        ("m-chp4-sec-ii-p114-0044", "cand-11650", "that group in Rome", "Unnamed collective; nested Rome mention is retained."),
        ("m-chp4-sec-ii-p114-0045", "cand-11651", "many other amateurs", "Unnamed collective of amateur owners."),
        ("m-chp4-sec-ii-p114-0046", "cand-11652", "fine paintings by Vouet, Pietro da Cortona and Testa", "Unidentified work group; named makers remain separately mentioned."),
    ]
    for mention_id, candidate_id, surface, note in new_mention_specs:
        if any(row["mention_id"] == mention_id for row in mentions):
            raise SystemExit(f"preflight failed: mention ID already exists: {mention_id}")
        start = segment_text.find(surface)
        if start < 0 or segment_text.find(surface, start + 1) >= 0:
            raise SystemExit(f"preflight failed: mention surface missing or ambiguous: {surface!r}")
        mentions.append({
            "mention_id": mention_id, "segment_id": SEGMENT_ID, "candidate_id": candidate_id,
            "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note,
        })
    candidates.extend(candidate_rows)

    positions = [i for i, row in enumerate(statements) if row.get("segment_id") == SEGMENT_ID]
    statements[max(positions) + 1:max(positions) + 1] = new_statements
    # Keep added mentions alongside the existing p.114 mention block.
    mention_positions = [i for i, row in enumerate(mentions) if row["segment_id"] == SEGMENT_ID]
    block = [row for row in mentions if row["segment_id"] == SEGMENT_ID]
    mentions = [row for row in mentions if row["segment_id"] != SEGMENT_ID]
    # Restore the block at its original location, preserving all other table order.
    original_first = next(i for i, row in enumerate(list(csv.DictReader(mention_path.open(encoding="utf-8-sig", newline="")))) if row["segment_id"] == SEGMENT_ID)
    mentions[original_first:original_first] = block

    expected_counts = {
        "statements": 34, "dual": 27, "relation_true": 27, "relation_false": 7,
        "dual_true": 26, "dual_false": 1, "open_relation": 1, "unclassified": 0,
    }
    counts = segment_counts(statements)
    if counts != expected_counts:
        raise SystemExit(f"preflight failed: unexpected p.114 counts {counts}")
    if len(statements) != 13044 or len(candidates) != 11630 or len(mentions) != 27568:
        raise SystemExit("preflight failed: unexpected resulting table totals")
    if len({row["statement_id"] for row in statements}) != len(statements):
        raise SystemExit("preflight failed: duplicate statement IDs")
    if len({row["candidate_id"] for row in candidates}) != len(candidates):
        raise SystemExit("preflight failed: duplicate candidate IDs")
    if len({row["mention_id"] for row in mentions}) != len(mentions):
        raise SystemExit("preflight failed: duplicate mention IDs")
    if any(segment_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"] for row in mentions if row["segment_id"] == SEGMENT_ID):
        raise SystemExit("preflight failed: resulting p.114 mention span mismatch")
    if any(row.get("original_quote") not in segment_text for row in statements if row.get("segment_id") == SEGMENT_ID):
        raise SystemExit("preflight failed: resulting p.114 quote mismatch")

    outputs = {
        paths["book-statements.jsonl"]: ("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in statements)).encode("utf-8"),
        paths["entity-candidates.csv"]: csv_bytes(paths["entity-candidates.csv"], candidates),
        paths["mentions.csv"]: csv_bytes(paths["mentions.csv"], mentions),
    }
    plan = {
        "mode": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "source_sha256": SOURCE_SHA256,
        "segment_sha256": SEGMENT_SHA256,
        "original_statements": len(ORIGINAL_IDS),
        "new_statements": len(new_statements),
        "new_candidates": [row["candidate_id"] for row in candidate_rows],
        "new_mentions": new_mention_specs,
        "resulting_segment_counts": counts,
        "table_totals": {"statements": len(statements), "candidates": len(candidates), "mentions": len(mentions)},
        "classification_plan": [
            {
                "statement_id": row["statement_id"], "subject": row.get("subject_candidate_id"),
                "predicate": row.get("predicate"), "object": row.get("object_candidate_id"),
                "relation_candidate": row.get("qualifiers", {}).get("relation_candidate"),
                "open_endpoint_reason": row.get("qualifiers", {}).get("open_endpoint_reason"),
            }
            for row in statements if row.get("segment_id") == SEGMENT_ID
        ],
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups = {path: path.with_name(f"{path.name}.{BACKUP_SUFFIX}") for path in outputs}
    temps = {path: path.with_name(f"{path.name}.p114.tmp") for path in outputs}
    if any(path.exists() for path in [*backups.values(), *temps.values()]):
        raise SystemExit("apply refused: p.114 recovery or temporary file already exists")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    try:
        for path, data in outputs.items():
            temps[path].write_bytes(data)
        for path in outputs:
            os.replace(temps[path], path)
        if len(read_jsonl(paths["book-statements.jsonl"])) != 13044:
            raise RuntimeError("post-write statement count failed")
        with paths["entity-candidates.csv"].open(encoding="utf-8-sig", newline="") as handle:
            written_candidates = list(csv.DictReader(handle))
        with paths["mentions.csv"].open(encoding="utf-8-sig", newline="") as handle:
            written_mentions = list(csv.DictReader(handle))
        written_statements = read_jsonl(paths["book-statements.jsonl"])
        if len(written_candidates) != 11630 or len(written_mentions) != 27568 or segment_counts(written_statements) != expected_counts:
            raise RuntimeError("post-write table validation failed")
    except Exception:
        for path, backup in backups.items():
            if backup.exists():
                shutil.copy2(backup, path)
        for temp in temps.values():
            temp.unlink(missing_ok=True)
        raise
    print(json.dumps({
        "write": "success",
        "sha256": {path.name: sha(path.read_bytes()) for path in outputs},
        "recovery_copies": [path.name for path in backups.values()],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
