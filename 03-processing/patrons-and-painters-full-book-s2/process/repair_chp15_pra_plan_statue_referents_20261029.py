"""Apply reviewed S2/S3 referent corrections for the Prà della Valle batch."""
from __future__ import annotations

import codecs
import csv
import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[3]
TABLES = BASE / "04-knowledge" / "tables"
PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
    "#s3-s4-s6-pra-della-valle-plan-statue-scope-20261029"
)


def read_csv(name: str) -> tuple[list[str], list[dict[str, str]], bool, str]:
    path = TABLES / name
    raw = path.read_bytes()
    bom = raw.startswith(codecs.BOM_UTF8)
    newline = "\r\n" if b"\r\n" in raw else "\n"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)
    return fields, rows, bom, newline


def write_csv(
    name: str,
    fields: list[str],
    rows: list[dict[str, str]],
    bom: bool,
    newline: str,
) -> None:
    import io

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=fields, extrasaction="raise", lineterminator=newline
    )
    writer.writeheader()
    writer.writerows(rows)
    payload = buffer.getvalue().encode("utf-8")
    if bom:
        payload = codecs.BOM_UTF8 + payload
    (TABLES / name).write_bytes(payload)


def require_unique(rows: list[dict[str, str]], key: str, value: str) -> dict[str, str]:
    found = [row for row in rows if row.get(key) == value]
    if len(found) != 1:
        raise ValueError(f"expected exactly one {key}={value}, found {len(found)}")
    return found[0]


def replace_mention_candidate(
    qualifiers: dict, old: str = "cand-1650", new: str = "cand-12456"
) -> None:
    values = qualifiers.get("mentioned_candidate_ids", [])
    qualifiers["mentioned_candidate_ids"] = list(
        dict.fromkeys(new if value == old else value for value in values)
    )


# Candidate register: preserve the raw index anchor while correcting its object label.
fields, candidates, bom, newline = read_csv("entity-candidates.csv")
c1650 = require_unique(candidates, "candidate_id", "cand-1650")
if c1650["canonical_name"] != "Memmo, Andrea":
    raise ValueError("cand-1650 no longer has the expected pre-correction label")
c1650["canonical_name"] = "Andrea Memmo’s plan for Prà della Valle"
c1650["detail"] = (
    "Index subentry M.csv#190 identifies the Prà della Valle plan. This candidate "
    "denotes Memmo’s oval urban-planning conception, distinct from the physical square, "
    "the planned statue programme, and Subleyras’s drawings."
)
if any(row.get("candidate_id") == "cand-12456" for row in candidates):
    raise ValueError("cand-12456 already exists")
candidates.append(
    {
        "candidate_id": "cand-12456",
        "index_entry_id": "",
        "canonical_name": (
            "Andrea Memmo’s Prà della Valle statue programme "
            "(planned series of eighty-eight statues)"
        ),
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Source-defined statue programme centred on the proposed series around "
            "the island at Prà della Valle. Haskell says 88 statues were required; "
            "the passage does not give a complete membership list or establish that "
            "all were completed. Keep the compressed reference to another six in Rome "
            "separate and unresolved."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-15:15_CHP-15_sec_ii:l6-12#L9",
    }
)
write_csv("entity-candidates.csv", fields, candidates, bom, newline)


# Cross-chapter alignments: correct prior scope decisions and complete source-local KU mapping.
fields, alignments, bom, newline = read_csv("alignment.csv")
c1650a = require_unique(alignments, "candidate_id", "cand-1650")
c2769a = require_unique(alignments, "candidate_id", "cand-2769")
c5766a = require_unique(alignments, "candidate_id", "cand-5766")
if c1650a["decision"] != "undecided" or c2769a["decision"] != "new":
    raise ValueError("S3 rows differ from the reviewed pre-correction state")

c1650a["ku_id"] = "units/works/andrea-memmo-pra-della-valle-plan"
c1650a["decision"] = "new"
c1650a["process_ref"] = PROCESS_REF
c1650a["resolution_note"] += (
    " | S3 correction 2026-10-29: the earlier note ‘not a verifiable S2 body mention’ "
    "was erroneous. Chapter 10 p.325 n.3 points to Chapter 15, and Chapter 15 p.365 "
    "directly identifies Memmo’s oval plan. The indexed parent ‘Memmo, Andrea’ is not "
    "the object; retain this as the urban-planning scheme. It is distinct from the "
    "statue programme cand-12456, the place cand-3960, and Subleyras’s drawing group "
    "cand-10494. group=workgrp-andrea-memmo-pra-della-valle-plan; S4 mapped to "
    "units/works/andrea-memmo-pra-della-valle-plan; no external identity asserted."
)

c2769a["decision"] = "same"
c2769a["process_ref"] = PROCESS_REF
c2769a["resolution_note"] += (
    " | S3 correction 2026-10-29: the indexed candidate and all 12 cross-chapter "
    "mentions denote the city Vicenza, already represented by units/places/vicenza. "
    "The former new split was erroneous; reuse the existing city KU, not the separate "
    "Palazzo della Ragione or another Vicenza site. group=sg3-ku-units-places-vicenza."
)

c5766a["ku_id"] = "units/places/colosseum"
c5766a["process_ref"] = PROCESS_REF
c5766a["resolution_note"] += (
    " | S4 registration 2026-10-29: map the existing new place group "
    "sg3-place-cand-5766 to units/places/colosseum. Chapter 4 names the Colosseum "
    "in a quotation and Chapter 15 compares the oval plan to it; neither passage "
    "identifies a specific capriccio depiction."
)

if any(row.get("candidate_id") == "cand-12456" for row in alignments):
    raise ValueError("alignment for cand-12456 already exists")
next_alignment = max(
    int(row["alignment_id"].removeprefix("aln-"))
    for row in alignments
    if row["alignment_id"].startswith("aln-")
) + 1
if next_alignment != 12787:
    raise ValueError(f"unexpected next alignment ID: aln-{next_alignment}")
alignments.append(
    {
        "alignment_id": "aln-12787",
        "candidate_id": "cand-12456",
        "ku_id": "units/works/pra-della-valle-statue-series-88",
        "external_source": "",
        "external_id": "",
        "decision": "new",
        "accessed_date": "",
        "process_ref": PROCESS_REF,
        "legacy_ku_id": "",
        "resolution_note": (
            "group=workgrp-pra-della-valle-statue-series-88; source_ref=chp-15:"
            "15_CHP-15_sec_ii:l6-12#L9-L10, l14-28#L17-L23; source evidence defines "
            "a planned statue programme around the island and states that 88 statues "
            "were required. This is distinct from Memmo’s oval urban plan, the square, "
            "the Subleyras drawings, and any individual statue. The membership list is "
            "not closed and completion is not asserted. No same-type KU was found; "
            "source-local new decision, with no external identity claim. S4 mapped to "
            "units/works/pra-della-valle-statue-series-88."
        ),
    }
)
write_csv("alignment.csv", fields, alignments, bom, newline)


# Mentions: keep the plan's exact references; move statue-program references; remove properties.
fields, mentions, bom, newline = read_csv("mentions.csv")
move_ids = {
    "m-chp15-p365-memmo-0031",
    "m-chp15-p365-memmo-0034",
    "m-chp15-p365-memmo-0036",
    "m-chp15-p365-memmo-0043",
    "m-chp15-p366-memmo-0017",
    "m-chp15-p366-memmo-0034",
    "m-chp15-p366-memmo-0062",
    "m-chp15-p366-memmo-0063",
}
delete_ids = {
    "m-chp15-p365-memmo-0021",
    "m-chp15-p365-memmo-0022",
    "m-chp15-p365-memmo-0037",
    "m-chp15-p365-memmo-0038",
    "m-chp15-p366-memmo-0005",
    "m-chp15-p366-memmo-0007",
    "m-chp15-p366-memmo-0008",
    "m-chp15-p366-memmo-0009",
    "m-chp15-p366-memmo-0010",
    "m-chp15-p366-memmo-0011",
    "m-chp15-p366-memmo-0013",
    "m-chp15-p366-memmo-0014",
    "m-chp15-p366-memmo-0015",
    "m-chp15-p366-memmo-0016",
    "m-chp15-p366-memmo-0041",
    "m-chp15-p366-memmo-0043",
    "m-chp15-p366-memmo-0045",
    "m-chp15-p366-memmo-0051",
    "m-chp15-p366-memmo-0064",
    "m-chp15-p366-memmo-0066",
}
selected = [row for row in mentions if row["candidate_id"] == "cand-1650"]
found_ids = {row["mention_id"] for row in selected}
if len(selected) != 31 or not move_ids <= found_ids or not delete_ids <= found_ids:
    raise ValueError("cand-1650 mention set changed; refusing a broad rewrite")
kept_mentions: list[dict[str, str]] = []
for row in mentions:
    if row["mention_id"] in delete_ids:
        continue
    if row["mention_id"] in move_ids:
        row["candidate_id"] = "cand-12456"
        row["note"] = (
            "S3/S2 referent correction 2026-10-29: this phrase denotes the planned "
            "Prà statue programme, not Memmo’s oval urban-planning scheme."
        )
    elif row["mention_id"] == "m-s2-ch10-p325-0054":
        row["note"] = (
            "The definite referent ‘the one he was calling for’ points to the Chapter 15 "
            "Prà plan via p.325 n.3. The 1782 scheme is described as similar; the source "
            "does not say it is the same scheme."
        )
    kept_mentions.append(row)
if len(kept_mentions) != len(mentions) - 20:
    raise ValueError("unexpected mention deletion count")
write_csv("mentions.csv", fields, kept_mentions, bom, newline)


# S2 statement referents. Source text and original quotations remain unchanged.
statements_path = TABLES / "book-statements.jsonl"
raw_lines = statements_path.read_text(encoding="utf-8").splitlines()
statements = [json.loads(line) for line in raw_lines]
by_id = {row["statement_id"]: row for row in statements}
if len(by_id) != len(statements):
    raise ValueError("duplicate statement IDs")

move_subject = {
    "st-chp15-p365-statue-foundations-strengthen-canal-banks",
    "st-chp15-p365-statues-as-civic-virtue-gallery",
    "st-chp15-p365-eighty-eight-statues-and-conditions",
    "st-chp15-p365-scheme-rationale-for-inclusion",
    "st-chp15-p365-lodoli-plan-functional-commercial",
    "st-chp15-p365-conditions-limit-venetian-enlightenment",
    "st-chp15-p365-memmo-representation-eligibility-partial",
    "st-chp15-p365-statue-donor-choice",
    "st-chp15-p366-eligible-presenters",
    "st-chp15-p366-eligible-churchmen",
    "st-chp15-p366-eligible-old-professions",
    "st-chp15-p366-quality-committee-and-stone",
    "st-chp15-p366-latin-inscriptions-pedestals",
    "st-chp15-p366-1777-progress-and-ambassadorship",
    "st-chp15-p366-statues-promised-and-in-situ-1786",
    "st-chp15-p366-general-appearance-mattered",
    "st-chp15-p366-uniform-stone-required",
    "st-chp15-p366-pedestal-space-limited-inscriptions",
    "st-chp15-p367-patronage-and-speed-caused-variation",
}
move_object = {
    "st-chp15-p365-subscriptions-for-statue-series",
    "st-chp15-p366-pope-and-visitors-contribute",
    "st-chp15-p366-poland-sweden-subscriptions",
    "st-chp15-p366-committee-appointed-for-quality",
    "st-chp15-p366-king-of-sweden-subscribed",
    "st-chp15-p366-memmo-spread-ideas",
}
required_statement_ids = move_subject | move_object | {
    "st-chp15-p367-results-difficult-to-assess",
    "st-chp15-p365-memmo-central-island-for-traders",
    "st-chp15-p365-memmo-oval-plan-colosseum",
    "st-chp15-p365-pra-plan-inspired-by-bologna-vicenza",
    "st-chp15-p365-plan-inspired-by-vicenza",
    "st-chp15-p366-another-six-in-rome-ambiguous",
    "st-chp15-p366-councillors-objected-to-expense",
    "st-chp15-p366-memmo-urges-friends-for-statues",
    "st-chp15-p366-memmo-proposed-subjects-to-friends",
    "st-chp15-p365-commercial-not-religious-or-family-glory-motive",
    "st-chp15-p365-pra-opposition-negotiation",
    "st-chp15-p365-pra-fundraising-required",
    "st-chp15-p367-prato-utilitarian-basis-tribute-to-lodoli",
    "st-chp15-p367-memmo-dissatisfied-with-progress",
    "st-chp15-p365-memmo-summoned-cerato-to-implement-plan",
    "st-chp15-p366-memmo-offers-antenor-statue",
    "st-chp15-p366-antenor-statue-made-by-andreosi",
    "st-chp15-p366-antenor-statue-depicts-antenor",
    "st-chp15-p366-padua-offers-memmo-ancestor-statue",
    "st-chp15-p366-third-statue-depicts-memmo-ancestor",
}
missing = required_statement_ids - by_id.keys()
if missing:
    raise ValueError(f"required statements missing: {sorted(missing)}")

for statement_id in move_subject:
    row = by_id[statement_id]
    if row.get("subject_candidate_id") != "cand-1650":
        raise ValueError(f"unexpected old subject for {statement_id}")
    row["subject_candidate_id"] = "cand-12456"
    replace_mention_candidate(row["qualifiers"])
for statement_id in move_object:
    row = by_id[statement_id]
    if row.get("object_candidate_id") != "cand-1650":
        raise ValueError(f"unexpected old object for {statement_id}")
    row["object_candidate_id"] = "cand-12456"
    replace_mention_candidate(row["qualifiers"])

# The civic-virtue claim was incorrectly attached to the Enlightenment candidate.
civic = by_id["st-chp15-p365-statues-as-civic-virtue-gallery"]
civic["object_candidate_id"] = None
civic["qualifiers"]["open_endpoint_reason"] = (
    "The source describes civic virtue as the statues’ pedagogical aim and separately "
    "mentions the Enlightenment; cand-8107 is not the civic-virtue object. Retain the "
    "claim, but leave it process-only pending a faithful concept and relation type."
)

by_id["st-chp15-p367-results-difficult-to-assess"]["subject_candidate_id"] = "cand-3960"
by_id["st-chp15-p367-results-difficult-to-assess"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-3960"]

pending_reasons = {
    "st-chp15-p365-memmo-oval-plan-colosseum": (
        "The Colosseum endpoint is a place; the controlled inspired_by type is restricted "
        "to work→event. Preserve Haskell’s comparison without projecting an incompatible edge."
    ),
    "st-chp15-p365-subscriptions-for-statue-series": (
        "The statue programme and intended site are now mapped; the invitation to subscribe "
        "does not identify subscribers or establish completed contributions."
    ),
    "st-chp15-p365-statue-foundations-strengthen-canal-banks": (
        "The statue programme is mapped, but the canal-bank feature has no independent "
        "endpoint candidate and no controlled predicate expresses the stated strengthening."
    ),
    "st-chp15-p365-pra-plan-inspired-by-bologna-vicenza": (
        "Bologna is a resolved city, but Haskell refers to its architectural example in the "
        "town, not the city as a work endpoint; no compatible example-work endpoint is registered."
    ),
    "st-chp15-p365-plan-inspired-by-vicenza": (
        "Vicenza now reuses the existing city KU; the source’s architectural example is not "
        "identified as a work endpoint, so no city-level inspired_by edge is asserted."
    ),
    "st-chp15-p365-memmo-central-island-for-traders": (
        "The central island is a project feature and cand-12228 traders remains S3 undecided; "
        "no faithful formal edge is written before the endpoint/type boundary is resolved."
    ),
    "st-chp15-p366-another-six-in-rome-ambiguous": (
        "The phrase ‘another six in Rome’ does not resolve whether these works belong to the "
        "Prà series or form a separate group; retain cand-10498 as undecided."
    ),
    "st-chp15-p366-pope-and-visitors-contribute": (
        "The programme is mapped, but the visitors are an unidentified collective and the "
        "individual contributed statue is not identified; retain the relation as pending."
    ),
    "st-chp15-p366-poland-sweden-subscriptions": (
        "The persons are aligned, but subscribing does not establish a completed contribution "
        "or a specific individual statue; preserve the prior S6 pending decision."
    ),
    "st-chp15-p366-committee-appointed-for-quality": (
        "The statue programme is mapped, but the unnamed committee cand-12234 remains S3 "
        "undecided and no faithful controlled predicate is established."
    ),
    "st-chp15-p366-councillors-objected-to-expense": (
        "The councillors cand-11529 remain unidentified and the source reports an objection, "
        "not a controlled project relation; keep pending."
    ),
    "st-chp15-p366-memmo-urges-friends-for-statues": (
        "The friends endpoint cand-11527 remains unclassified and S3 undecided; preserve the "
        "source claim but do not formalize an unidentified collective contribution relation."
    ),
    "st-chp15-p366-memmo-proposed-subjects-to-friends": (
        "The friends endpoint cand-11527 remains unclassified and S3 undecided; the source "
        "does not identify recipients, so retain this relation candidate as pending."
    ),
    "st-chp15-p366-king-of-sweden-subscribed": (
        "Gustav III is now aligned, but subscription alone does not establish a completed "
        "contribution or identify a particular statue; preserve the prior S6 pending decision."
    ),
    "st-chp15-p365-memmo-summoned-cerato-to-implement-plan": (
        "The endpoint cand-0623 remains S3 undecided; no KU or formal implementation edge is "
        "created until the source-local person identity and compatible predicate are resolved."
    ),
    "st-chp15-p366-memmo-offers-antenor-statue": (
        "The planned statue cand-10484 remains S3 undecided; offering is not upgraded to a "
        "formal commission or completed contribution."
    ),
    "st-chp15-p366-antenor-statue-made-by-andreosi": (
        "The maker cand-0104 is mapped, but the planned work cand-10484 remains S3 undecided; "
        "do not create a work edge without its KU."
    ),
    "st-chp15-p366-antenor-statue-depicts-antenor": (
        "Both the planned work cand-10484 and source-local person cand-10483 remain S3 undecided; "
        "no depicted-person edge is written."
    ),
    "st-chp15-p366-padua-offers-memmo-ancestor-statue": (
        "The civic-body endpoint is registered, but the proposed work cand-10488 remains S3 "
        "undecided; offering does not establish commission or completion."
    ),
    "st-chp15-p366-third-statue-depicts-memmo-ancestor": (
        "The proposed work cand-10488 and unnamed ancestor cand-10487 remain S3 undecided; "
        "retain the source claim without formalizing a depiction edge."
    ),
}
for statement_id, reason in pending_reasons.items():
    by_id[statement_id]["qualifiers"]["open_endpoint_reason"] = reason

# The two royal S6 statements were historically pending; update stale S3 wording only.
poland = by_id["st-chp15-p366-poland-sweden-subscriptions"]["qualifiers"]
poland["qualification"] = (
    "The page gives royal titles; the index anchors them to Stanislas Poniatowski and "
    "Gustavus III, and both candidates now resolve to their person KUs. The source reports "
    "subscriptions but does not establish completed payment or a specific statue."
)
sweden = by_id["st-chp15-p366-king-of-sweden-subscribed"]["qualifiers"]
sweden["qualification"] = (
    "The page gives the title; the p.366 index identifies Gustavus III, now aligned to the "
    "existing person KU. The source reports a subscription but does not establish completed "
    "payment or a specific statue."
)

statements_path.write_text(
    "\n".join(json.dumps(row, ensure_ascii=False) for row in statements)
    + "\n",
    encoding="utf-8",
    newline="",
)


# Record unresolved direct endpoints in the existing backlog contract.
fields, backlog, bom, newline = read_csv("candidate-backlog.csv")
next_backlog = max(
    int(row["backlog_id"].removeprefix("bl-"))
    for row in backlog
    if row["backlog_id"].startswith("bl-")
) + 1
if next_backlog != 70:
    raise ValueError(f"unexpected next backlog ID: bl-{next_backlog:04d}")
backlog_specs = [
    ("cand-0623", "person", "chp-15:15_CHP-15_sec_ii:l6-12#L8", "st-chp15-p365-memmo-summoned-cerato-to-implement-plan", "object", "Abate Cerato is not fully resolved to a source-local person KU; keep the plan-implementation relation pending."),
    ("cand-10484", "work", "chp-15:15_CHP-15_sec_ii:l14-28#L17", "st-chp15-p366-memmo-offers-antenor-statue", "object", "The proposed Antenor statue remains S3 undecided; offer, maker and subject relations stay pending until its work identity is resolved."),
    ("cand-10483", "person", "chp-15:15_CHP-15_sec_ii:l14-28#L18", "st-chp15-p366-antenor-statue-depicts-antenor", "object", "The source-local Antenor identity remains S3 undecided; do not merge a legendary figure to an external person without evidence."),
    ("cand-10488", "work", "chp-15:15_CHP-15_sec_ii:l14-28#L19", "st-chp15-p366-padua-offers-memmo-ancestor-statue", "object", "The proposed ancestor statue remains S3 undecided; the source does not confirm completion or installation."),
    ("cand-10487", "person", "chp-15:15_CHP-15_sec_ii:l14-28#L19", "st-chp15-p366-third-statue-depicts-memmo-ancestor", "object", "The unnamed fourteenth-century ancestor remains source-local and S3 undecided; no person KU is created."),
    ("cand-10498", "work", "chp-15:15_CHP-15_sec_ii:l14-28#L20", "st-chp15-p366-another-six-in-rome-ambiguous", "object", "The six-in-Rome phrase is syntactically compressed; its membership and relation to the Prà series remain unresolved."),
    ("cand-11528", "", "chp-15:15_CHP-15_sec_ii:l14-28#L21", "st-chp15-p366-pope-and-visitors-contribute", "subject", "The visitors are an unidentified collective with no resolved taxonomy or person KU; keep the contribution relation pending."),
    ("cand-11529", "", "chp-15:15_CHP-15_sec_ii:l14-28#L20", "st-chp15-p366-councillors-objected-to-expense", "subject", "The councillors’ names and civic body are not identified; do not merge them with the City of Padua institution."),
    ("cand-11527", "", "chp-15:15_CHP-15_sec_ii:l14-28#L20-L21", "st-chp15-p366-memmo-urges-friends-for-statues", "object", "The source names only Memmo’s friends as a collective; their identities and taxonomy remain unresolved, so keep both contribution and proposed-subject relations pending."),
    ("cand-12234", "institution", "chp-15:15_CHP-15_sec_ii:l14-28#L16", "st-chp15-p366-committee-appointed-for-quality", "subject", "The unnamed quality committee has no established institutional identity or affiliation; keep its relation pending."),
    ("cand-12228", "term", "chp-15:15_CHP-15_sec_ii:l6-12#L8", "st-chp15-p365-memmo-central-island-for-traders", "object", "The source-defined trader class and central-island feature remain unresolved endpoints; no KU or formal relation is created."),
]
for offset, (candidate_id, entity_type, source_ref, statement_id, endpoint_role, note) in enumerate(backlog_specs):
    backlog_id = f"bl-{next_backlog + offset:04d}"
    if any(row.get("backlog_id") == backlog_id for row in backlog):
        raise ValueError(f"backlog ID already exists: {backlog_id}")
    candidate = require_unique(candidates, "candidate_id", candidate_id)
    backlog.append(
        {
            "backlog_id": backlog_id,
            "canonical_name": candidate["canonical_name"],
            "suggested_type": entity_type or candidate["suggested_type"],
            "status": "undecided",
            "source_id": "haskell-1980-rev-ed",
            "source_ref": source_ref,
            "statement_id": statement_id,
            "endpoint_role": endpoint_role,
            "candidate_id": candidate_id,
            "ku_id": "",
            "decision_note": note,
            "process_ref": PROCESS_REF,
        }
    )
write_csv("candidate-backlog.csv", fields, backlog, bom, newline)


# KU manifest rows for three source-local registrations.
fields, manifest, bom, newline = read_csv("ku-manifest.csv")
new_manifest = [
    ("units/works/andrea-memmo-pra-della-valle-plan", "work", "Andrea Memmo’s plan for Prà della Valle", "Andrea Memmo’s Prà della Valle plan", "04-knowledge/units/works/andrea-memmo-pra-della-valle-plan.md"),
    ("units/works/pra-della-valle-statue-series-88", "work", "Andrea Memmo’s Prà della Valle statue programme", "Andrea Memmo’s Prà della Valle statue programme", "04-knowledge/units/works/pra-della-valle-statue-series-88.md"),
    ("units/places/colosseum", "place", "罗马斗兽场", "Colosseum", "04-knowledge/units/places/colosseum.md"),
]
for ku_id, entity_type, canonical_name, name_en, card_path in new_manifest:
    if any(row.get("ku_id") == ku_id for row in manifest):
        raise ValueError(f"KU manifest entry already exists: {ku_id}")
    manifest.append(
        {
            "ku_id": ku_id,
            "type": entity_type,
            "canonical_name": canonical_name,
            "name_en": name_en,
            "source_task": "patrons-and-painters-full-book-s2",
            "card_path": card_path,
        }
    )
write_csv("ku-manifest.csv", fields, manifest, bom, newline)


# Mark the current S2 versions for follow-up independent review without changing the old ledger.
fields, coverage, bom, newline = read_csv("s2-coverage.csv")
coverage_notes = {
    "chp-10:10_CHP-10_sec_ii:l203-208": (
        " 2026-10-29 referent correction: the note-3 cross-reference anchors cand-1650 to "
        "‘the one he was calling for’; the scheme being implemented in 1782 is only called "
        "similar. This edited current version is not independently reviewed or counted in the 9,622 ledger."
    ),
    "chp-15:15_CHP-15_sec_ii:l6-12": (
        " 2026-10-29 referent correction: keep the oval/Memmo urban plan as cand-1650; route "
        "the fundraising/statue-program references to cand-12456. Current assignments require "
        "independent review and do not change the 9,622 reviewed-item count."
    ),
    "chp-15:15_CHP-15_sec_ii:l14-28": (
        " 2026-10-29 referent correction: statue-series rules, named progress counts and the "
        "mapped Azzo statue’s programme membership are separated from the urban plan; unresolved "
        "works and collective actors remain pending. This current version is not independently reviewed."
    ),
    "chp-15:15_CHP-15_sec_ii:l30-36": (
        " 2026-10-29 referent correction: the variation claim points to the statue programme "
        "cand-12456; the final-results sentence names the physical Prà place cand-3960. This current "
        "version is not independently reviewed or counted in the 9,622 ledger."
    ),
}
for segment_id, addition in coverage_notes.items():
    row = require_unique(coverage, "segment_id", segment_id)
    if "2026-10-29 referent correction" not in row["note"]:
        row["note"] = row["note"].rstrip() + addition
write_csv("s2-coverage.csv", fields, coverage, bom, newline)

print(
    json.dumps(
        {
            "candidate_added": "cand-12456",
            "candidate_decisions_changed": ["cand-1650", "cand-2769"],
            "ku_mappings_added_or_completed": ["cand-1650", "cand-12456", "cand-5766"],
            "same_decision": "cand-2769",
            "mentions_moved": len(move_ids),
            "mentions_removed": len(delete_ids),
            "backlog_added": len(backlog_specs),
            "coverage_segments_updated": len(coverage_notes),
            "statements_edited": len(required_statement_ids),
        },
        ensure_ascii=False,
    )
)
