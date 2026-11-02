#!/usr/bin/env python3
"""Prepare/apply S2 repairs for the continuous current-order window 1432–1531."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import subprocess
import tempfile
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
MENTIONS_PATH = TABLES / "mentions.csv"
ROSTER_PATH = PROCESS / "s2-current-review-roster.csv"
COVERAGE_PATH = TABLES / "s2-coverage.csv"
SEGMENTS_PATH = TABLES / "segments.jsonl"
HISTORY_PATH = PROCESS / "s2-history-9622-review-events.csv"

BASE_HEAD = "791eb62b79b81e127cd3f98ac9db76cd1d7e30e3"
HISTORY_SHA256 = "75ab12df478a816035929353565b0301d55959c6bb13d9b511af072c4c931c89"
SOURCE_HASHES = {
    "02-sources/01-book/CHP-2.pdf": "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e",
    "02-sources/02-Markdown/02_CHP-2_sec_ii.md": "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9",
}
BATCH_ID = "S2-B573-CH2-1432-1531"
STAGE_ID = "2026-11-03-s2-current-review-b573-order-1432-1531"
EVIDENCE_REF = f"stages.md#{STAGE_ID}"

PENDING_TO_PASS = {
    "st-chp2-sec-ii-l3-8-taddeo-fortunes",
    "st-chp2-sec-ii-l3-8-family-art-patronage",
    "st-chp2-sec-ii-l3-8-family-wealth",
    "st-chp2-sec-ii-l3-8-treasury-income",
    "st-chp2-sec-ii-l3-8-urban-excess-reputation",
    "st-chp2-sec-ii-l3-8-witchcraft-plot",
    "st-chp2-sec-ii-l3-8-feudal-clans",
    "st-chp2-sec-ii-l3-8-palestrina-sale",
    "st-chp2-sec-ii-l10-18-feudal-families-social-role",
    "st-chp2-sec-ii-l10-18-papal-financial-patronage",
    "st-chp2-sec-ii-l10-18-urban-criticism-of-predecessor-spending",
    "st-chp2-sec-ii-l10-18-urban-followed-predecessors-example",
    "st-chp2-sec-ii-l10-18-urban-professed-wealth-policy",
    "st-chp2-sec-ii-l10-18-european-power-and-rome-prestige",
    "st-chp2-sec-ii-l10-18-contarini-state-and-rome-description",
    "st-chp2-sec-ii-l10-18-contarini-visitors-and-tribute",
    "st-chp2-sec-ii-l20-28-papacy-status-threats",
    "st-chp2-sec-ii-l20-28-protestant-advance-and-events",
    "st-chp2-sec-ii-l20-28-protestant-advance-battle-barrier",
    "st-chp2-sec-ii-l20-28-france-hapsburg-rivalry",
    "st-chp2-sec-ii-l20-28-urban-alliance-with-france",
    "st-chp2-sec-ii-l20-28-counter-reformation-and-spiritual-crisis",
    "st-chp2-sec-ii-l20-28-intellectual-changes-affect-papacy",
    "st-chp2-sec-ii-l20-28-architecture-decoration-and-persuasion",
    "st-chp2-sec-ii-l30-40-barberini-style-and-bernini",
}
KEEP_PENDING = {
    "st-chp2-seci-l124-157-colonna-sale-letter",
    "st-chp2-sec-ii-l3-8-sovereignty",
    "st-chp2-sec-ii-l3-8-nepotism-rationale",
    "st-chp2-sec-ii-l20-28-baroque-triumph-and-victories",
    "st-chp2-sec-ii-l20-28-urban-fortification-impact",
    "st-chp2-sec-ii-l20-28-richelieu-exploited-alliance",
    "st-chp2-sec-ii-l20-28-naude-french-quotation",
}
EXPECTED_PENDING = PENDING_TO_PASS | KEEP_PENDING

NEW_STATEMENTS = {
    "st-chp2-sec-ii-l3-8-nepotism-recognized-papal-system": {
        "template": "st-chp2-sec-ii-l3-8-nepotism-rationale",
        "before": "st-chp2-sec-ii-l3-8-witchcraft-plot",
        "subject_candidate_id": "cand-1734",
        "object_candidate_id": None,
        "predicate": "historical_interpretation",
        "quote": "Nepotism was a recognised feature of the papal system",
        "qualifiers": {
            "source_line_start": 6,
            "source_line_end": 6,
            "claim": "Haskell describes nepotism as a recognised feature of the papal system.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "qualification": "This records Haskell’s characterization of the system. The following reported witchcraft attempt is represented separately.",
            "print_page": 31,
            "relation_candidate": False,
            "mentioned_candidate_ids": ["cand-1734"],
        },
        "status": "reviewed_current_pass",
        "outcome": "new_statement_semantic_pass_after_source_and_candidate_span_check",
        "follow_up": "B573 adds this independently asserted source claim; it does not identify a specific adviser or establish any formal relation.",
    },
    "st-chp2-sec-ii-l10-18-contarini-papal-state-description": {
        "template": "st-chp2-sec-ii-l10-18-contarini-state-and-rome-description",
        "before": "st-chp2-sec-ii-l10-18-contarini-state-and-rome-description",
        "subject_candidate_id": "cand-0823",
        "object_candidate_id": "cand-1831",
        "predicate": "reported_ambassadorial_characterization",
        "quote": "the Pope owns a superb state with several cities well worthy of it",
        "qualifiers": {
            "source_line_start": 15,
            "source_line_end": 15,
            "claim": "Pietro Contarini describes the Pope’s state as superb and comprising several cities he considers worthy of it.",
            "speaker": "Pietro Contarini",
            "text_layer": "quoted ambassadorial observation",
            "qualification": "This is Contarini’s evaluative description of the Pope’s state; it is distinct from his following description of Rome. No ownership or administrative relation beyond the quoted wording is inferred.",
            "print_page": 32,
            "relation_candidate": False,
            "mentioned_candidate_ids": ["cand-0823", "cand-1831"],
        },
        "status": "reviewed_current_pass",
        "outcome": "new_statement_semantic_pass_after_source_scope_split",
        "follow_up": "B573 separates Contarini’s description of the Papal States from his separate characterization of Rome.",
    },
    "st-chp2-sec-ii-l20-28-protestant-advance-no-longer-immediate-problem": {
        "template": "st-chp2-sec-ii-l20-28-protestant-advance-and-events",
        "after": "st-chp2-sec-ii-l20-28-papacy-status-threats",
        "subject_candidate_id": "cand-4225",
        "object_candidate_id": None,
        "predicate": "historical_interpretation",
        "quote": "The immediate problem was no longer the Protestant advance which had caused so much trouble to his predecessors:",
        "qualifiers": {
            "source_line_start": 22,
            "source_line_end": 22,
            "claim": "Haskell says the Protestant advance, after causing much trouble to Urban VIII’s predecessors, was no longer the immediate problem in the situation he describes.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "qualification": "The predecessor group is left unnamed. This contextual statement is separate from the following two event-specific barrier claims.",
            "print_page": 33,
            "relation_candidate": False,
            "mentioned_candidate_ids": ["cand-4225"],
        },
        "status": "reviewed_current_pass",
        "outcome": "new_statement_semantic_pass_after_source_scope_split",
        "follow_up": "B573 records the missing contextual conclusion separately; it does not identify Urban VIII’s predecessors.",
    },
    "st-chp2-sec-ii-l20-28-french-cultural-aspects-reinforcement": {
        "template": "st-chp2-sec-ii-l20-28-urban-alliance-with-france",
        "after": "st-chp2-sec-ii-l20-28-urban-alliance-with-france",
        "subject_candidate_id": None,
        "object_candidate_id": "cand-4221",
        "predicate": "situation_reported_to_reinforce_french_cultural_aspects",
        "quote": "Though he tried to remain neutral, Urban was in fact compelled to lean much too heavily on his alliance with France—a situation that was eagerly turned to advantage by the unscrupulous Richelieu and that helped to reinforce the already strong French aspects of his culture.",
        "qualifiers": {
            "source_line_start": 25,
            "source_line_end": 25,
            "claim": "Haskell says the situation created by Urban VIII’s compelled reliance on France helped reinforce the already strong French aspects of his culture.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "qualification": "The clause ‘that helped to reinforce’ refers to the situation in the immediately preceding clause. The source-defined situation has no distinct candidate; the French cultural aspect remains distinct in meaning from a political action by France.",
            "print_page": 33,
            "relation_candidate": True,
            "relation_candidate_note": "The source leaves the situation as anaphoric context and does not name it as a distinct event. cand-4221 is provisionally mapped from the explicit phrase ‘French aspects’; its cultural scope/type remains open. Do not create a formal edge before resolving the candidate and open subject.",
            "open_endpoint_reason": "The source uses ‘a situation’ and ‘that’ for the context of Urban VIII’s compelled reliance on France; no distinct situation candidate is registered.",
            "mentioned_candidate_ids": ["cand-3104", "cand-2189", "cand-4221"],
        },
        "status": "reviewed_current_pending",
        "outcome": "new_statement_pending_open_context_endpoint_and_candidate_scope",
        "follow_up": "B573 records the missing cultural consequence but leaves the situation endpoint and the cand-4221 cultural/political scope unresolved.",
    },
}

STATEMENT_UPDATES = {
    "st-chp2-sec-ii-l3-8-family-art-patronage": {
        "claim": "Haskell says most of the male relations just named were fond of the arts and attributes some of Rome’s greatest achievements to their patronage.",
        "mentioned_candidate_ids": ["cand-12290", "cand-3126"],
    },
    "st-chp2-sec-ii-l3-8-family-wealth": {
        "claim": "Haskell links wealth and status, says the papal family’s enrichment was therefore viewed as inevitable if not desirable, and presents extreme wealth as ultimate security for those prepared to take office amid frequent shifts of power.",
        "mentioned_candidate_ids": ["cand-0198"],
    },
    "st-chp2-sec-ii-l3-8-treasury-income": {
        "claim": "Haskell says little distinction was made between the papal treasury and any pope’s personal income; the sentence does not identify who made that distinction.",
        "subject_candidate_id": None,
        "object_candidate_id": None,
        "mentioned_candidate_ids": [],
    },
    "st-chp2-sec-ii-l3-8-urban-excess-reputation": {
        "claim": "Despite the preceding discussion of family enrichment, status, wealth, and security, Haskell reports that Urban VIII was universally held by his contemporaries and successors to have exceeded all reasonable limits; ‘universally’ remains Haskell’s characterization, not an independently verified consensus.",
        "mentioned_candidate_ids": ["cand-12293", "cand-3104"],
    },
    "st-chp2-sec-ii-l3-8-witchcraft-plot": {
        "claim": "Haskell reports that in 1635 an unnamed ambitious nephew of a papabile cardinal was to use witchcraft in an attempt to remove Urban VIII and secure his own fortune.",
        "mentioned_candidate_ids": ["cand-12291", "cand-12292", "cand-3104"],
    },
    "st-chp2-sec-ii-l10-18-feudal-families-social-role": {
        "claim": "Haskell says that from then on the old feudal families’ only purpose was to provide suitably aristocratic wives for the upstarts who had taken their place in Rome’s government.",
        "mentioned_candidate_ids": ["cand-11876", "cand-11877"],
    },
    "st-chp2-sec-ii-l10-18-urban-criticism-of-predecessor-spending": {
        "claim": "Haskell reports, through an unnamed Venetian ambassadorial comment, that Urban VIII blamed a subset of his predecessors for consuming the Church’s inheritance on buildings and similar things.",
        "mentioned_candidate_ids": ["cand-3104", "cand-11878", "cand-3400", "cand-4217"],
        "speaker": "Unnamed Venetian ambassadorial source; the footnote chain does not identify an individual speaker.",
        "qualification": "This preserves the nested attribution: Haskell reports Urban VIII’s accusation through an unnamed Venetian ambassadorial source. Do not treat the accusation as independently verified or identify a single ambassador.",
    },
    "st-chp2-sec-ii-l10-18-urban-professed-wealth-policy": {
        "mentioned_candidate_ids": ["cand-3104", "cand-1831"],
    },
    "st-chp2-sec-ii-l10-18-european-power-and-rome-prestige": {
        "mentioned_candidate_ids": ["cand-4220", "cand-3126"],
    },
    "st-chp2-sec-ii-l10-18-contarini-state-and-rome-description": {
        "quote": "Rome especially, where the Popes usually live in recognition of her having formerly been mistress of the world, both for the ancient survivals of her past greatness and for the modern features which can be seen and which are cared for with perhaps equal attention, is a sort of emporium of the Universe.",
        "claim": "Pietro Contarini says Rome had formerly been mistress of the world and describes its ancient survivals and modern features, cared for with perhaps equal attention; he calls the city a kind of emporium of the Universe.",
        "mentioned_candidate_ids": ["cand-0823", "cand-3126"],
        "qualification": "This row records Contarini’s Rome-specific description and preserves ‘emporium of the Universe’ as his rhetoric. His preceding description of the Pope’s state and several cities is now a separate statement.",
    },
    "st-chp2-sec-ii-l10-18-contarini-visitors-and-tribute": {
        "claim": "Contarini says people have long come to Rome from every country to see its splendours; with the qualification that it would scarcely be an exaggeration, he says they come to pay tribute because Rome is as much a motherland to foreigners as to its own citizens.",
        "mentioned_candidate_ids": ["cand-11583", "cand-3126"],
        "qualification": "The source-defined visitors are not individually identified. ‘Tribute’ and Rome as a motherland are Contarini’s qualified rhetoric, not literal taxation or a legal nationality claim.",
    },
    "st-chp2-sec-ii-l3-8-sovereignty": {
        "mentioned_candidate_ids": ["cand-3104", "cand-1831"],
    },
    "st-chp2-sec-ii-l10-18-papal-financial-patronage": {
        "mentioned_candidate_ids": ["cand-3104", "cand-3114"],
    },
    "st-chp2-sec-ii-l10-18-urban-followed-predecessors-example": {
        "mentioned_candidate_ids": ["cand-3104", "cand-11878"],
    },
    "st-chp2-sec-ii-l20-28-papacy-status-threats": {
        "mentioned_candidate_ids": ["cand-3104", "cand-4223"],
    },
    "st-chp2-sec-ii-l20-28-protestant-advance-and-events": {
        "mentioned_candidate_ids": ["cand-11879", "cand-4225"],
    },
    "st-chp2-sec-ii-l20-28-protestant-advance-battle-barrier": {
        "mentioned_candidate_ids": ["cand-2810", "cand-4225"],
    },
    "st-chp2-sec-ii-l20-28-baroque-triumph-and-victories": {
        "mentioned_candidate_ids": ["cand-3993", "cand-11880"],
    },
    "st-chp2-sec-ii-l20-28-france-hapsburg-rivalry": {
        "claim": "Haskell says France and the Hapsburg Empire were traditional enemies; their jockeying for position and search for allies frequently threatened peace in Italy and the security of the Papal States.",
        "mentioned_candidate_ids": ["cand-4221", "cand-4222", "cand-3114", "cand-1831"],
        "qualification": "The source makes the France–Hapsburg enmity the direct relation; Italy’s peace and the Papal States’ security are the separate threatened contexts, not endpoints of that enmity. Preserve Haskell’s broad political characterization.",
    },
    "st-chp2-sec-ii-l20-28-urban-fortification-impact": {
        "mentioned_candidate_ids": ["cand-3104", "cand-3126"],
    },
    "st-chp2-sec-ii-l20-28-richelieu-exploited-alliance": {
        "quote": "Though he tried to remain neutral, Urban was in fact compelled to lean much too heavily on his alliance with France—a situation that was eagerly turned to advantage by the unscrupulous Richelieu",
        "claim": "Haskell says Richelieu eagerly turned to his advantage the situation created by Urban VIII’s compelled reliance on France.",
        "object_candidate_id": None,
        "mentioned_candidate_ids": ["cand-3104", "cand-4221", "cand-2189"],
        "open_endpoint_reason": "The object is the anaphoric ‘situation’ created by Urban VIII’s compelled reliance on France; no distinct situation/event candidate is registered.",
        "relation_candidate_note": "The source says Richelieu exploited a political situation, not Urban VIII as a person. cand-2189 identifies Richelieu; Urban and France provide the situation’s context. Keep the situation endpoint open and do not create a formal edge.",
        "qualification": "‘Unscrupulous’ is Haskell’s characterization. The object is the political situation in the preceding clause; it is not Urban VIII personally.",
    },
    "st-chp2-sec-ii-l20-28-urban-alliance-with-france": {
        "mentioned_candidate_ids": ["cand-3104", "cand-4221"],
        "qualification": "The source says Urban tried to remain neutral but was compelled to rely heavily on France. The following French cultural consequence is recorded separately; no cultural identity is inferred from the political alliance.",
    },
    "st-chp2-sec-ii-l20-28-counter-reformation-and-spiritual-crisis": {
        "mentioned_candidate_ids": ["cand-3396", "cand-4226"],
    },
    "st-chp2-sec-ii-l20-28-intellectual-changes-affect-papacy": {
        "claim": "Haskell says the old explanations no longer satisfied; instead, serious scientific experiments, abstruse metaphysical speculation, astrology, and cynical or frivolous disbelief emerged from the preceding silence, penetrated the core of Roman society, and affected the papacy. His evaluative descriptions remain his own.",
    },
    "st-chp2-sec-ii-l20-28-naude-french-quotation": {
        "mentioned_candidate_ids": ["cand-1726", "cand-3126", "cand-4223", "cand-4224", "cand-3114"],
        "qualification": "Naudé’s mediated quotation distinguishes Rome, the generic Pope, the Roman Court, and Italy. cand-4223 remains the generic Pope and is not Urban VIII. The observations remain source-attributed, not independently verified.",
    },
    "st-chp2-sec-ii-l20-28-architecture-decoration-and-persuasion": {
        "mentioned_candidate_ids": ["cand-3104", "cand-4227"],
    },
    "st-chp2-sec-ii-l30-40-barberini-style-and-bernini": {
        "mentioned_candidate_ids": ["cand-3046", "cand-4228"],
    },
}

NEW_MENTIONS = [
    ("chp-2:02_CHP-2_sec_ii:l3-8", "cand-1831", "the state", "Printed p.31 L3. Haskell’s phrase is provisionally mapped to the Papal States; the identity decision remains open."),
    ("chp-2:02_CHP-2_sec_ii:l3-8", "cand-0805", "a rich and aristocratic wife", "Printed p.31 L4. This prospective description resolves to Anna Colonna through the p.32 L11 selection; p.31 still records only a prospect, not a completed marriage."),
    ("chp-2:02_CHP-2_sec_ii:l3-8", "cand-11876", "great feudal clans", "Printed p.31 L7. Source-defined collective; the passage does not identify a complete membership list."),
    ("chp-2:02_CHP-2_sec_ii:l3-8", "cand-4241", "papal court", "Printed p.31 L7. Exact phrase anchoring the wealth said to flow into the Papal Court; no donor or transaction is inferred."),
    ("chp-2:02_CHP-2_sec_ii:l3-8", "cand-3239", "another branch of the family", "Printed p.31 L8. The preceding Colonna sale supplies the family antecedent, but this branch and its members remain unidentified."),
    ("chp-2:02_CHP-2_sec_ii:l10-18", "cand-11876", "Their", "Printed p.32 L11. The pronoun refers to the great feudal clans introduced on printed p.31; the collective remains unnamed."),
    ("chp-2:02_CHP-2_sec_ii:l10-18", "cand-11877", "upstarts", "Printed p.32 L11. Source-defined group of people who had taken the old families’ place in Rome’s government; no individuals are identified."),
    ("chp-2:02_CHP-2_sec_ii:l10-18", "cand-11878", "those of his predecessors", "Printed p.32 L14. Unnamed subset of Urban VIII’s predecessors; the cited criticism does not identify specific popes."),
    ("chp-2:02_CHP-2_sec_ii:l10-18", "cand-11583", "people come from every country", "Printed p.32 L15. Source-defined visitor group in Contarini’s quotation; the tribute and motherland language remains rhetorical."),
    ("chp-2:02_CHP-2_sec_ii:l20-28", "cand-11879", "reconciliation of Henri IV in 1593", "Printed p.33 L22–23. Haskell names this as one of two events he says proved barriers to Protestant advance."),
    ("chp-2:02_CHP-2_sec_ii:l20-28", "cand-11880", "these overwhelming victories", "Printed p.33 L23. Source-defined set referring to two distinct events, Henri IV’s reconciliation and the Battle of the White Hill; candidate type remains open."),
]

PENDING_DETAILS = {
    "st-chp2-seci-l124-157-colonna-sale-letter": "The note cites a letter announcing ‘the sale’, but the event endpoint is not registered; cand-4215 is the territory, not the transaction.",
    "st-chp2-sec-ii-l3-8-sovereignty": "The ‘the state’ mention is now anchored, but the claim still merges Urban VIII’s statement with an unnamed Venetian ambassador’s separate criticism of the cardinals; speaker and group scope need a separate statement/candidate decision.",
    "st-chp2-sec-ii-l3-8-nepotism-rationale": "The distinct recognized-feature claim is now recorded in B573. This remaining statement still refers to an unnamed close relative/adviser and has no identity-resolved adviser endpoint.",
    "st-chp2-sec-ii-l20-28-baroque-triumph-and-victories": "The event-set phrase now has a direct mention anchor and the two component events remain distinct. cand-11880’s source-defined set type/boundary remains a S3 candidate decision.",
    "st-chp2-sec-ii-l20-28-urban-fortification-impact": "Urban and Rome are mapped, but the statement still combines inside/outside fortifications, contemporary impact, and artistic recording without identified sites, works, or audience endpoints.",
    "st-chp2-sec-ii-l20-28-richelieu-exploited-alliance": "The object is corrected from Urban VIII to the source’s ‘situation’ and left open because no event/context candidate is registered. The separate French-cultural consequence is captured in a pending statement; both endpoints remain unresolved.",
    "st-chp2-sec-ii-l20-28-naude-french-quotation": "The generic Pope, Rome, Roman Court, and Italy are now mapped separately; the quoted observation still combines two geographic scopes and unnamed moral/religious groups, so it remains pending for claim separation and group coverage.",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: object) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def read_jsonl(path: Path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    return ([json.loads(line) for line in text.splitlines() if line.strip()], raw,
            "\r\n" if "\r\n" in text else "\n", raw.startswith(b"\xef\xbb\xbf"))


def read_csv(path: Path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return (list(reader), list(reader.fieldnames or []), raw,
            "\r\n" if "\r\n" in text else "\n", raw.startswith(b"\xef\xbb\xbf"))


def write_csv(rows, fields, eol, bom):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator=eol,
                            extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + out.getvalue().encode("utf-8")


def source_mentions_at(revision: str, segment_id: str):
    raw = subprocess.check_output(
        ["git", "show", f"{revision}:04-knowledge/tables/mentions.csv"], cwd=ROOT
    ).decode("utf-8-sig")
    return {
        row["mention_id"]: row
        for row in csv.DictReader(io.StringIO(raw, newline=""))
        if row["segment_id"] == segment_id
    }


def atomic_write(path: Path, data: bytes) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expect-plan", default="")
    args = parser.parse_args()

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                   text=True).strip()
    require(head == BASE_HEAD, f"Expected base HEAD {BASE_HEAD}; found {head}")
    for relative, expected in SOURCE_HASHES.items():
        require(sha256((ROOT / relative).read_bytes()) == expected,
                f"Source asset changed: {relative}")
    require(sha256(HISTORY_PATH.read_bytes()) == HISTORY_SHA256,
            "Immutable H9622 event ledger changed")

    statements, statements_raw, statements_eol, statements_bom = read_jsonl(STATEMENTS_PATH)
    mentions, mention_fields, _, mentions_eol, mentions_bom = read_csv(MENTIONS_PATH)
    roster, roster_fields, _, roster_eol, roster_bom = read_csv(ROSTER_PATH)
    coverage, coverage_fields, _, coverage_eol, coverage_bom = read_csv(COVERAGE_PATH)
    segments, _, _, _ = read_jsonl(SEGMENTS_PATH)

    statement_by_id = {row["statement_id"]: deepcopy(row) for row in statements}
    roster_by_id = {row["statement_id"]: dict(row) for row in roster}
    require(len(statements) == len(roster) == 15514,
            "Unexpected pre-stage statement/roster size")
    require(len(statement_by_id) == len(statements) and len(roster_by_id) == len(roster),
            "Duplicate statement or roster ID")
    require(set(statement_by_id) == set(roster_by_id),
            "Statement and roster ID sets differ")
    ordered_old = sorted(roster, key=lambda row: int(row["current_order"]))
    require([int(row["current_order"]) for row in ordered_old] == list(range(1, 15515)),
            "Pre-stage current order is not continuous")
    require(set(row["statement_id"] for row in ordered_old)
            == set(row["statement_id"] for row in statements),
            "Statement and roster ID sets differ")
    require(all(row["current_statement_sha256"] == canonical_hash(statement_by_id[row["statement_id"]])
                for row in ordered_old), "Pre-stage current statement fingerprint mismatch")

    selected = [row for row in ordered_old if 1432 <= int(row["current_order"]) <= 1531]
    require(len(selected) == 100, "Expected 100 original current-order rows")
    require(sum(row["current_review_status"] == "reviewed_current_pass" for row in selected) == 68,
            "Unexpected reusable PASS count")
    pending_ids = {row["statement_id"] for row in selected
                   if row["current_review_status"] == "reviewed_current_pending"}
    require(pending_ids == EXPECTED_PENDING,
            f"Pending set changed: {sorted(pending_ids ^ EXPECTED_PENDING)}")
    require(not any(row["review_batch_id"] == BATCH_ID for row in ordered_old),
            "B573 was already applied")

    source_file = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
    source_lines = source_file.read_text(encoding="utf-8-sig").splitlines()
    segment_by_id = {row["segment_id"]: row for row in segments}
    segment_text = {}
    for segment_id in {spec[0] for spec in NEW_MENTIONS}:
        segment = segment_by_id[segment_id]
        text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
        segment_text[segment_id] = text
        for mention in mentions:
            if mention["segment_id"] == segment_id:
                start, end = int(mention["start_char"]), int(mention["end_char"])
                require(text[start:end] == mention["surface_form"],
                        f"Existing mention source span mismatch: {mention['mention_id']}")

    mentions_after = list(mentions)
    mention_ids = {row["mention_id"] for row in mentions_after}
    prefix_by_segment = {
        "chp-2:02_CHP-2_sec_ii:l3-8": "m-chp2-secii-l3-8",
        "chp-2:02_CHP-2_sec_ii:l10-18": "m-chp2-secii-l10-18",
        "chp-2:02_CHP-2_sec_ii:l20-28": "m-chp2-secii-l20-28",
    }
    next_number = {}
    for segment_id, prefix in prefix_by_segment.items():
        nums = [int(suffix) for row in mentions_after
                if row["mention_id"].startswith(prefix + "-")
                for suffix in [row["mention_id"].rsplit("-", 1)[1]] if suffix.isdigit()]
        next_number[segment_id] = max(nums, default=0) + 1
    added_mention_ids = []
    for segment_id, candidate_id, surface, note in NEW_MENTIONS:
        text = segment_text[segment_id]
        first = text.find(surface)
        require(first >= 0 and text.find(surface, first + 1) < 0,
                f"Expected one exact source span for {surface!r} in {segment_id}")
        require(not any(m["segment_id"] == segment_id and m["candidate_id"] == candidate_id
                        and m["surface_form"] == surface for m in mentions_after),
                f"Mention already exists: {segment_id} / {candidate_id} / {surface}")
        mention_id = f"{prefix_by_segment[segment_id]}-{next_number[segment_id]:04d}"
        next_number[segment_id] += 1
        require(mention_id not in mention_ids, f"Duplicate mention ID: {mention_id}")
        mention_ids.add(mention_id)
        added_mention_ids.append(mention_id)
        mentions_after.append({
            "mention_id": mention_id,
            "segment_id": segment_id,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(first),
            "end_char": str(first + len(surface)),
            "note": note,
        })

    statement_by_id_after = deepcopy(statement_by_id)
    changed_statement_ids = set()
    for statement_id, update in STATEMENT_UPDATES.items():
        require(statement_id in statement_by_id_after,
                f"Missing update target: {statement_id}")
        row = statement_by_id_after[statement_id]
        for key, value in update.items():
            if key in {"claim", "mentioned_candidate_ids", "speaker", "qualification",
                       "open_endpoint_reason", "relation_candidate_note"}:
                row["qualifiers"][key] = value
            elif key == "quote":
                row["original_quote"] = value
            else:
                row[key] = value
        changed_statement_ids.add(statement_id)

    # Add source-anchored statements, preserving the existing data contract.
    for statement_id, spec in NEW_STATEMENTS.items():
        require(statement_id not in statement_by_id_after, f"New ID already exists: {statement_id}")
        new = deepcopy(statement_by_id[spec["template"]])
        new["statement_id"] = statement_id
        new["subject_candidate_id"] = spec["subject_candidate_id"]
        new["object_candidate_id"] = spec["object_candidate_id"]
        new["predicate"] = spec["predicate"]
        new["original_quote"] = spec["quote"]
        new["qualifiers"] = deepcopy(spec["qualifiers"])
        if statement_id == "st-chp2-sec-ii-l10-18-contarini-papal-state-description":
            template_qualifiers = statement_by_id[spec["template"]]["qualifiers"]
            for key in ("footnote_markers", "footnote_refs", "footnote_segment", "footnote_marker"):
                if key in template_qualifiers:
                    new["qualifiers"][key] = deepcopy(template_qualifiers[key])
        new["origin"] = "book"
        new["source_file"] = "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
        new["segment_id"] = statement_by_id[spec["template"]]["segment_id"]
        statement_by_id_after[statement_id] = new

    # Verify the two new quote spans against the source text before insertion.
    for statement_id, spec in NEW_STATEMENTS.items():
        sid = statement_by_id_after[statement_id]["segment_id"]
        segment = segment_by_id[sid]
        text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
        require(spec["quote"] in text, f"New statement quote is absent from S0 source: {statement_id}")

    original_window_ids = {row["statement_id"] for row in selected}
    require(PENDING_TO_PASS | KEEP_PENDING == pending_ids,
            "PASS/pending decision lists do not cover the original pending set")

    # Insert new rows adjacent to their source clauses.
    ids = [row["statement_id"] for row in ordered_old]
    for statement_id, spec in NEW_STATEMENTS.items():
        if "before" in spec:
            anchor = spec["before"]
            require(anchor in ids, f"Missing insertion anchor: {anchor}")
            ids.insert(ids.index(anchor), statement_id)
        else:
            anchor = spec["after"]
            require(anchor in ids, f"Missing insertion anchor: {anchor}")
            ids.insert(ids.index(anchor) + 1, statement_id)
    require(len(ids) == 15518 and set(ids) == set(statement_by_id_after),
            "Post-stage statement order or ID set is incomplete")

    mentions_by_segment = defaultdict(list)
    for mention in mentions_after:
        mentions_by_segment[mention["segment_id"]].append(mention)
    changed_segments = {segment_id for segment_id, *_ in NEW_MENTIONS}

    roster_by_id_after = {row["statement_id"]: dict(row) for row in roster}
    for statement_id, spec in NEW_STATEMENTS.items():
        template = roster_by_id[spec["template"]]
        statement = statement_by_id_after[statement_id]
        segment = segment_by_id[statement["segment_id"]]
        row = dict(template)
        row.update({
            "statement_id": statement_id,
            "snapshot_statement_sha256": "",
            "current_statement_sha256": canonical_hash(statement),
            "history_9622_membership": "not_in_reconstructed_count",
            "prior_review_match": "no_exact_review_mapping",
            "prior_review_ref": "",
            "current_review_status": spec["status"],
            "review_batch_id": BATCH_ID,
            "review_outcome": spec["outcome"],
            "review_evidence_ref": EVIDENCE_REF,
            "follow_up_note": spec["follow_up"],
            "history_9622_event_count": "0",
            "history_9622_latest_review_commit": "",
            "history_9622_latest_statement_sha256": "",
            "history_9622_current_statement_match": "",
            "history_9622_source_match": "",
            "history_9622_mention_delta": "",
            "history_9622_evidence_ref": "",
            "segment_sha256": segment["sha256"],
            "source_asset_sha256": segment.get("asset_sha256", ""),
            "source_file": segment["source_file"],
            "segment_id": statement["segment_id"],
            "source_id": segment["source_id"],
            "chapter": segment["chapter"],
            "section": segment["section"],
            "source_line_start": str(statement["qualifiers"]["source_line_start"]),
            "source_line_end": str(statement["qualifiers"]["source_line_end"]),
            "current_segment_mention_count": str(len(mentions_by_segment[statement["segment_id"]])),
        })
        roster_by_id_after[statement_id] = row

    prior_evidence_by_id = {row["statement_id"]: row["review_evidence_ref"] for row in selected}
    for statement_id in original_window_ids:
        row = roster_by_id_after[statement_id]
        old_ref = prior_evidence_by_id[statement_id]
        row["review_batch_id"] = BATCH_ID
        row["review_evidence_ref"] = EVIDENCE_REF
        if statement_id in PENDING_TO_PASS:
            row["current_review_status"] = "reviewed_current_pass"
            row["review_outcome"] = "current_statement_semantic_pass_after_source_and_mention_repair"
            detail = "Targeted correction applied from the prior printed-page finding; source quote and exact mention anchors now support the current claim."
        elif statement_id in KEEP_PENDING:
            row["current_review_status"] = "reviewed_current_pending"
            row["review_outcome"] = "current_pending_retained_after_targeted_source_and_endpoint_review"
            detail = PENDING_DETAILS[statement_id]
        elif row["current_review_status"] == "reviewed_current_pass":
            row["review_outcome"] = "reused_current_pass_after_full_stage_fingerprint_check"
            detail = "Existing current PASS reused after ID, statement, source, segment, and mention fingerprint checks; exact prior page evidence remains valid."
        else:
            raise SystemExit(f"Selected pending row has no B573 disposition: {statement_id}")
        row["follow_up_note"] = (
            f"B573: {detail} Prior current evidence: {old_ref}.\n" + row.get("follow_up_note", "")
        ).strip()

    # Current hashes are recalculated for every changed statement; H9622 event rows stay immutable.
    for statement_id, row in roster_by_id_after.items():
        if statement_id in statement_by_id_after:
            row["current_statement_sha256"] = canonical_hash(statement_by_id_after[statement_id])
    for statement_id in changed_statement_ids:
        row = roster_by_id_after[statement_id]
        if int(row.get("history_9622_event_count") or "0") > 0:
            row["history_9622_current_statement_match"] = (
                "exact" if row["history_9622_latest_statement_sha256"] == row["current_statement_sha256"]
                else "changed"
            )
            row["prior_review_match"] = (
                "exact_object_and_source_segment"
                if row["history_9622_current_statement_match"] == "exact"
                and row["history_9622_source_match"] == "true"
                else "historical_object_or_source_differs"
            )

    roster_after = [roster_by_id_after[statement_id] for statement_id in ids]
    for order, row in enumerate(roster_after, start=1):
        row["current_order"] = str(order)
    require([int(row["current_order"]) for row in roster_after] == list(range(1, 15519)),
            "Post-stage roster order is not continuous")
    require(set(row["statement_id"] for row in roster_after) == set(statement_by_id_after),
            "Post-stage roster and statement ID sets differ")

    mention_delta_cache = {}
    mention_hashes = {}
    for segment_id in changed_segments:
        seg_rows = sorted(mentions_by_segment[segment_id], key=lambda mention: mention["mention_id"])
        mention_hashes[segment_id] = canonical_hash(seg_rows)
    for row in roster_after:
        segment_id = row["segment_id"]
        if segment_id not in changed_segments:
            continue
        seg_rows = mentions_by_segment[segment_id]
        row["current_segment_mention_count"] = str(len(seg_rows))
        row["current_segment_mentions_sha256"] = mention_hashes[segment_id]
        if int(row.get("history_9622_event_count") or "0") <= 0:
            continue
        revision = row["history_9622_latest_review_commit"]
        cache_key = (revision, segment_id)
        if cache_key not in mention_delta_cache:
            old_mentions = source_mentions_at(revision, segment_id)
            current_mentions = {mention["mention_id"]: mention for mention in seg_rows}
            mention_delta_cache[cache_key] = {
                "changed": sorted(mid for mid in old_mentions.keys() & current_mentions.keys()
                                  if old_mentions[mid] != current_mentions[mid]),
                "removed": sorted(old_mentions.keys() - current_mentions.keys()),
                "added": sorted(current_mentions.keys() - old_mentions.keys()),
            }
        row["history_9622_mention_delta"] = json.dumps(
            mention_delta_cache[cache_key], ensure_ascii=False, separators=(",", ":")
        )

    # Add stage references to the four affected segment coverage rows.
    coverage_after = [dict(row) for row in coverage]
    coverage_notes = {
        "chp-2:02_CHP-2_sec_ii:l3-8": "B573: printed p.31 claim scope and source-defined group mentions repaired; 5 exact spans added. Open Papal States and adviser-speaker issues remain pending.",
        "chp-2:02_CHP-2_sec_ii:l10-18": "B573: printed p.32 claims and source-defined group mentions repaired; 4 exact spans added. Contarini’s state and Rome descriptions are separated.",
        "chp-2:02_CHP-2_sec_ii:l20-28": "B573: printed p.33 candidate mappings, event mentions, and claim scope repaired; 2 exact spans added. Event-set type, fortification scope, Richelieu situation endpoint, and Naude quotation boundaries remain pending.",
        "chp-2:02_CHP-2_sec_ii:l30-40": "B573: printed p.34 Bernini and Barberini-style candidate mapping verified against the exact existing segment mentions.",
    }
    for segment_id, note in coverage_notes.items():
        found = [row for row in coverage_after if row["segment_id"] == segment_id]
        require(len(found) == 1, f"Expected one S2 coverage row: {segment_id}")
        if "B573:" not in found[0]["note"]:
            found[0]["note"] = (found[0]["note"].rstrip() + " " + note).strip()

    # Render source statement table in the same source order with three new IDs inserted.
    statement_lines = statements_raw.decode("utf-8-sig").splitlines()
    insertion_before = {spec["before"]: sid for sid, spec in NEW_STATEMENTS.items() if "before" in spec}
    insertion_after = {spec["after"]: sid for sid, spec in NEW_STATEMENTS.items() if "after" in spec}
    rendered_statement_lines = []
    for raw_line in statement_lines:
        if not raw_line.strip():
            rendered_statement_lines.append(raw_line)
            continue
        original = json.loads(raw_line)
        sid = original["statement_id"]
        before_sid = insertion_before.get(sid)
        if before_sid:
            rendered_statement_lines.append(json.dumps(statement_by_id_after[before_sid], ensure_ascii=False, separators=(",", ":")))
        rendered_statement_lines.append(
            json.dumps(statement_by_id_after[sid], ensure_ascii=False, separators=(",", ":"))
            if sid in changed_statement_ids else raw_line
        )
        after_sid = insertion_after.get(sid)
        if after_sid:
            rendered_statement_lines.append(json.dumps(statement_by_id_after[after_sid], ensure_ascii=False, separators=(",", ":")))
    require(len(rendered_statement_lines) == len(statement_lines) + len(NEW_STATEMENTS),
            "Statement table rendering did not insert all new rows")
    statements_output = ((b"\xef\xbb\xbf" if statements_bom else b"")
                         + (statements_eol.join(rendered_statement_lines) + statements_eol).encode("utf-8"))
    mentions_output = write_csv(mentions_after, mention_fields, mentions_eol, mentions_bom)
    roster_output = write_csv(roster_after, roster_fields, roster_eol, roster_bom)
    coverage_output = write_csv(coverage_after, coverage_fields, coverage_eol, coverage_bom)

    statement_hashes = {sid: canonical_hash(row) for sid, row in statement_by_id_after.items()}
    require(all(row["current_statement_sha256"] == statement_hashes[row["statement_id"]]
                for row in roster_after), "Post-stage current statement fingerprint mismatch")
    require(sum(row["current_review_status"] == "reviewed_current_pass" for row in roster_after) == 8743,
            "Unexpected post-stage PASS count")
    require(sum(row["current_review_status"] == "reviewed_current_pending" for row in roster_after) == 6775,
            "Unexpected post-stage pending count")
    require(sum(int(row.get("history_9622_event_count") or "0") for row in roster_after) == 9620,
            "H9622 event-to-current mapping changed")
    require(len(mentions_after) == 27350, "Unexpected post-stage mention count")
    require(sha256(HISTORY_PATH.read_bytes()) == HISTORY_SHA256,
            "Immutable H9622 ledger changed during planning")

    history_counts = Counter(row["history_9622_current_statement_match"]
                             for row in roster_after if int(row.get("history_9622_event_count") or "0") > 0)
    relation_ids = [row["statement_id"] for row in selected]
    plan_files = {
        str(STATEMENTS_PATH.relative_to(ROOT)): statements_output,
        str(MENTIONS_PATH.relative_to(ROOT)): mentions_output,
        str(ROSTER_PATH.relative_to(ROOT)): roster_output,
        str(COVERAGE_PATH.relative_to(ROOT)): coverage_output,
    }
    plan = {
        "base_head": BASE_HEAD,
        "batch_id": BATCH_ID,
        "window": [1432, 1531],
        "original_rows": len(selected),
        "reused_pass": 68,
        "pending_to_pass": len(PENDING_TO_PASS),
        "pending_retained": len(KEEP_PENDING),
        "new_statements": len(NEW_STATEMENTS),
        "new_mentions": len(NEW_MENTIONS),
        "post_statement_count": len(statement_by_id_after),
        "post_mention_count": len(mentions_after),
        "post_pass": 8743,
        "post_pending": 6775,
        "historical_id_hash_status": dict(history_counts),
        "file_hashes": {name: sha256(data) for name, data in plan_files.items()},
        "history_sha256": HISTORY_SHA256,
    }
    plan_hash = sha256(json.dumps(plan, ensure_ascii=False, sort_keys=True,
                                  separators=(",", ":")).encode("utf-8"))
    print(json.dumps({"plan": plan, "plan_sha256": plan_hash}, ensure_ascii=False, indent=2))
    if not args.apply:
        print("DRY RUN: no project files written")
        return
    require(args.expect_plan == plan_hash,
            "Apply requires --expect-plan matching the dry-run plan hash")
    for relative, data in plan_files.items():
        atomic_write(ROOT / relative, data)
    print("APPLIED: statements, mentions, roster, and S2 coverage updated; documentation/commit remain stage-close actions")


if __name__ == "__main__":
    main()
