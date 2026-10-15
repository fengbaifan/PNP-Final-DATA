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


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
PDF = ROOT / "02-sources/01-book/CHP-3.pdf"
PAGE80 = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/.tmp_chp3_p80_phys22_20261010.png"
PAGE81 = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/.tmp_chp3_p81_phys23_20261010.png"
SEGMENT = "chp-3:03_CHP-3_sec_iv:l35-46"

EXPECTED = {
    TABLE: "653c64406d0ea35e6c6f0e7e259faf0c387438f621232c0625becad12cf35486",
    CANDIDATES: "72e1c6f689b7e4777e7a462273366f82dbc4852bf15bb879dd486e30abed7a17",
    MENTIONS: "44a32c4259a41f2dca4a6a94415cb3bbec7b171dc73ef25d3286b3250ffac1e9",
    COVERAGE: "e9c4b793d40f00d6d5cb0952413aae2e7c55787a5a820bfe9dcc27e9159b66cc",
    SOURCE: "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
    PAGE80: "4771b6ae63677a9357e6f1d51aecc40c27e9487d468b2e9cf512a4b2b123703c",
    PAGE81: "9eaecbbb9be2701cbdd62450c83c4c701203bf5903ab4565f0f6bd02a1c6dcd0",
}

BACKUPS = {
    TABLE: TABLE.with_name(TABLE.name + ".bak-s2-chp3-sec-iv-l35-46-relations-20261010"),
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + ".bak-s2-chp3-sec-iv-l35-46-audience-groups-20261010"),
    MENTIONS: MENTIONS.with_name(MENTIONS.name + ".bak-s2-chp3-sec-iv-l35-46-audience-groups-20261010"),
}

KEEP_TRUE = {
    "st-chp3-seciv-l35-46-considers-brandi",
    "st-chp3-seciv-l35-46-considers-ferri",
    "st-chp3-seciv-l35-46-considers-maratta",
    "st-chp3-seciv-l35-46-scope-includes-dome",
    "st-chp3-seciv-l35-46-scope-includes-main-vault",
    "st-chp3-seciv-l35-46-scope-includes-transept-vaults",
}

DECISIONS: dict[str, tuple[bool, str]] = {
    "st-chp3-seciv-l35-46-bernini-employed-gaulli": (
        True,
        "Haskell directly reports Bernini's earlier employment of Gaulli on decorative work; retain the artist-to-artist employment relation.",
    ),
    "st-chp3-seciv-l35-46-bernini-enthusiastic": (
        True,
        "Bernini's enthusiasm is explicitly about Gaulli as a possible painter; preserve the evaluation as Haskell's report.",
    ),
    "st-chp3-seciv-l35-46-commission-at-own-expense": (
        True,
        "The agreement assigns the painting and gilding expenses for Gaulli's specified commission to Gaulli himself.",
    ),
    "st-chp3-seciv-l35-46-conditional-fee-and-scaffolding": (
        True,
        "The fee and scaffolding expenses are conditional on the work going well; do not turn the terms into a payment already made.",
    ),
    "st-chp3-seciv-l35-46-confessor-condemns-nudity": (
        True,
        "The unnamed Jesuit confessor explicitly judges the figures' nudity lascivious; the quoted judgment is not independently verified.",
    ),
    "st-chp3-seciv-l35-46-confessor-of-prince": (
        True,
        "The source explicitly identifies the confessor through his relation to Prince Pamfili; both remain unidentified beyond the text.",
    ),
    "st-chp3-seciv-l35-46-contract-deadlines": (
        False,
        "The two deadlines describe the schedule attached to the commission, not a relation between the commission and a second entity.",
    ),
    "st-chp3-seciv-l35-46-contract-signed-1672": (
        True,
        "Haskell reports that Oliva and Gaulli signed a contract in August 1672; preserve the date and the source's report.",
    ),
    "st-chp3-seciv-l35-46-de-vecchi-pendentives": (
        True,
        "The sentence explicitly attributes the previously frescoed Gesu pendentives to Giovanni de' Vecchi.",
    ),
    "st-chp3-seciv-l35-46-dome-ready-april-1675": (
        False,
        "Readiness by April 1675 is a completion status and date for the dome, rather than a relation between two entities.",
    ),
    "st-chp3-seciv-l35-46-experts-unenthusiastic-private-showing": (
        True,
        "The invited experts are the unnamed evaluators of Gaulli's work. Their membership is unspecified, so use a source-limited open group candidate; the private showing remains context.",
    ),
    "st-chp3-seciv-l35-46-figures-hurriedly-clothed": (
        False,
        "This records the figures' resulting state after the confessor's judgment; it does not assert another entity relation.",
    ),
    "st-chp3-seciv-l35-46-futile-negotiations": (
        True,
        "The negotiations explicitly connect Oliva and the Duke of Parma; futile characterizes the negotiations and remains attributed to Haskell.",
    ),
    "st-chp3-seciv-l35-46-gaulli-born-1639": (
        False,
        "The reported birth year is a person attribute, not a relation candidate.",
    ),
    "st-chp3-seciv-l35-46-main-vault-completed-four-years-later": (
        False,
        "This is a relative completion-time status of the vault, not a relation between the commission and a second entity.",
    ),
    "st-chp3-seciv-l35-46-no-charge-corrections": (
        True,
        "Gaulli undertook to correct the commission without charge if experts found it imperfect; retain the condition and do not imply that corrections occurred.",
    ),
    "st-chp3-seciv-l35-46-oliva-ambitions-grow": (
        True,
        "Haskell explicitly relates the growth of Oliva's ambitions to the progress of the Gesu decoration; preserve it as an authorial interpretation, not a claim about a specified new plan.",
    ),
    "st-chp3-seciv-l35-46-oliva-and-gaulli-from-genoa": (
        False,
        "Retain the comparative source statement as context, but do not model a relation between Oliva and Gaulli. Split the explicit person-to-place claims into two scalar statements using the shared Genoa mention.",
    ),
    "st-chp3-seciv-l35-46-oliva-praises-gaulli": (
        True,
        "Oliva's praise in negotiation is directed at Gaulli's Gesu work. Point to the work candidate, not to Gaulli as a person; preserve the persuasive purpose and quoted-letter context.",
    ),
    "st-chp3-seciv-l35-46-oliva-resumes-tribune-negotiations": (
        True,
        "Oliva resumes negotiations with the Duke of Parma about the Gesu tribune decoration; the desired work remains uncompleted.",
    ),
    "st-chp3-seciv-l35-46-oliva-september-1679-letter-fragment": (
        True,
        "Haskell quotes the beginning of Oliva's September 1679 letter to the Duke about the Gesu and its tribune; the excerpt continues on the next printed page.",
    ),
    "st-chp3-seciv-l35-46-portrait-reputation": (
        False,
        "The portrait-painter reputation is an attributed description of Gaulli, not a relation candidate.",
    ),
    "st-chp3-seciv-l35-46-prince-pamfili-patron": (
        True,
        "The wording identifies Prince Pamfili as Gaulli's patron; it does not identify the prince further.",
    ),
    "st-chp3-seciv-l35-46-public-admires-painting-and-stucco": (
        True,
        "Haskell reports the general public's admiration of the painting and stucco arrangement. Add a source-limited audience group because the audience has no membership or boundary in the text.",
    ),
    "st-chp3-seciv-l35-46-s-agnese-work-caused-trouble": (
        True,
        "The decorative work caused difficulty for Gaulli. Reverse the endpoints to match that direction and retain the specific S. Agnese episode as context.",
    ),
    "st-chp3-seciv-l35-46-seeks-artist-for-jesuit-controlled-parts": (
        True,
        "During the negotiations Oliva sought another painter for the parts of the Gesu under Jesuit authority; the church part is the stated work context.",
    ),
    "st-chp3-seciv-l35-46-sees-s-marta-frescoes-and-adds-gaulli": (
        True,
        "After seeing Gaulli's S. Marta frescoes, Oliva explicitly added him to the possible-painter list.",
    ),
    "st-chp3-seciv-l35-46-strange-beginning-commission": (
        True,
        "The later commission was entrusted by the Jesuits to Gaulli. Set Gaulli as the recipient and retain the commission as the work context.",
    ),
    "st-chp3-seciv-l35-46-styles-no-preconceived-ideas": (
        False,
        "Haskell infers Oliva's lack of a preconceived style from the diversity of the painters; this is an attributed interpretation of Oliva, not a relation to a second entity.",
    ),
    "st-chp3-seciv-l35-46-tribune-vault-reserved": (
        True,
        "The commission excludes the tribune vault from Gaulli's scope. Separate the clause that the vault was being kept for Borgognone into its own scalar relation.",
    ),
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str], bytes]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader), list(reader.fieldnames or []), raw


def encode_jsonl(rows: list[dict], raw: bytes) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return prefix + b"".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + newline
        for row in rows
    )


def encode_csv(rows: list[dict[str, str]], fields: list[str], raw: bytes) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    prefix = "\ufeff" if raw.startswith(b"\xef\xbb\xbf") else ""
    return (prefix + stream.getvalue()).encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    temp: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as stream:
            stream.write(payload)
            temp = Path(stream.name)
        os.replace(temp, path)
    finally:
        if temp and temp.exists():
            temp.unlink()


def normalized(text: str) -> str:
    return " ".join(text.split())


def mark_relation(row: dict, flag: bool, note: str) -> None:
    qualifiers = dict(row.get("qualifiers") or {})
    qualifiers["relation_candidate"] = flag
    qualifiers["relation_candidate_note"] = note
    row["qualifiers"] = qualifiers


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify and atomize S2 statements for printed p.80, L36-46.")
    parser.add_argument("--apply", action="store_true", help="Write only after fixed preflight checks pass; default is dry-run.")
    args = parser.parse_args()

    for path, expected in EXPECTED.items():
        require(path.exists() and digest(path) == expected, f"preflight hash changed: {path.relative_to(ROOT)}")
    require(all(not path.exists() for path in BACKUPS.values()), "one or more recovery backups already exist")

    raw_table = TABLE.read_bytes()
    statements = read_jsonl(TABLE)
    require(len(statements) == 12777, "statement count changed")
    require(len({row["statement_id"] for row in statements}) == len(statements), "statement IDs are not unique")
    by_id = {row["statement_id"]: row for row in statements}
    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    target_ids = set(DECISIONS) | KEEP_TRUE
    require(len(segment_rows) == 36, "segment statement count changed")
    require({row["statement_id"] for row in segment_rows} == target_ids, "segment statement set changed")
    require(
        {row["statement_id"] for row in segment_rows if (row.get("qualifiers") or {}).get("relation_candidate") is True} == KEEP_TRUE,
        "preclassified relation statements changed",
    )
    require(
        all((by_id[sid].get("qualifiers") or {}).get("relation_candidate") is None for sid in DECISIONS),
        "one or more target statements already has a decision",
    )

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    # Match the table audit's source span: segments.jsonl lines are inclusive,
    # and the segment begins with the printed-page marker at source line 35.
    segment_text = "\n".join(source_lines[34:46])
    for sid in target_ids:
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        require(isinstance(start, int) and isinstance(end, int), f"source line anchor missing: {sid}")
        span = "\n".join(source_lines[start - 1:end])
        require(normalized(row.get("original_quote", "")) in normalized(span), f"quote/source mismatch: {sid}")

    candidates, candidate_fields, raw_candidates = read_csv(CANDIDATES)
    mentions, mention_fields, raw_mentions = read_csv(MENTIONS)
    require(len(candidates) == 11579 and len(mentions) == 27520, "candidate or mention row count changed")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    require(max(int(row["candidate_id"].split("-")[1]) for row in candidates) == 11601, "candidate ID cursor changed")
    segment_mentions = [row for row in mentions if row["segment_id"] == SEGMENT]
    require(max(int(row["mention_id"].rsplit("-", 1)[1]) for row in segment_mentions) == 57, "mention ID cursor changed")

    audience_id = "cand-11602"
    experts_id = "cand-11603"
    audience_mention_id = "m-chp3-seciv-l35-46-0058"
    experts_mention_id = "m-chp3-seciv-l35-46-0059"
    new_statement_ids = {
        "st-chp3-seciv-l35-46-gaulli-from-genoa",
        "st-chp3-seciv-l35-46-oliva-from-genoa",
        "st-chp3-seciv-l35-46-tribune-vault-reserved-for-borgognone",
    }
    require(audience_id not in candidate_by_id and experts_id not in candidate_by_id, "a planned group candidate ID already exists")
    require(not ({audience_mention_id, experts_mention_id} & mention_by_id.keys()), "a planned mention ID already exists")
    require(not (new_statement_ids & by_id.keys()), "a planned statement ID already exists")
    require(
        not any(row["canonical_name"] in {
            "General public responding to Gaulli's Gesu painting and stucco",
            "Experts invited to Gaulli's Gesu private showing",
        } for row in candidates),
        "a source-specific audience candidate already exists",
    )

    require(
        mention_by_id["m-chp3-seciv-l35-46-0014"]["candidate_id"] == "cand-1771"
        and mention_by_id["m-chp3-seciv-l35-46-0015"]["candidate_id"] == "cand-1131"
        and mention_by_id["m-chp3-seciv-l35-46-0015"]["surface_form"] == "Genoa",
        "Oliva or Genoa mention mapping changed",
    )
    cov_rows, _, _ = read_csv(COVERAGE)
    cov = next((row for row in cov_rows if row["segment_id"] == SEGMENT), None)
    require(
        cov is not None
        and cov["disposition"] == "reviewed"
        and cov["migration_status"] == "complete"
        and cov["source_line_ranges"] == "L36-46"
        and "Footnotes 1-6 are migrated and linked to notes L197-199." in cov["note"],
        "coverage status or footnote linkage changed",
    )

    candidate_additions = [
        {
            "candidate_id": audience_id,
            "index_entry_id": "",
            "canonical_name": "General public responding to Gaulli's Gesu painting and stucco",
            "index_page_range": "",
            "suggested_type": "",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell reports that the general public admired the painting and stucco arrangement in this passage. Audience membership and boundaries are unspecified; keep distinct from public or audience groups in other passages.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT}#L45",
        },
        {
            "candidate_id": experts_id,
            "index_entry_id": "",
            "canonical_name": "Experts invited to Gaulli's Gesu private showing",
            "index_page_range": "",
            "suggested_type": "",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell reports that invited experts were not enthusiastic at a private showing of Gaulli's Gesu work. The experts are unnamed and their membership is unspecified.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT}#L45",
        },
    ]
    candidates.extend(candidate_additions)

    mention_additions = []
    for mention_id, candidate_id, surface, note in [
        (
            audience_mention_id,
            audience_id,
            "the general public",
            "The unnamed audience group whose admiration of Gaulli's Gesu painting and stucco arrangement Haskell reports.",
        ),
        (
            experts_mention_id,
            experts_id,
            "The experts",
            "The unnamed invited evaluators at the private showing; group membership is not supplied.",
        ),
    ]:
        start = segment_text.index(surface)
        mention_additions.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(start + len(surface)),
            "note": note,
        })
    mentions.extend(mention_additions)

    for sid, (is_relation, note) in DECISIONS.items():
        mark_relation(by_id[sid], is_relation, note)

    origin = by_id["st-chp3-seciv-l35-46-oliva-and-gaulli-from-genoa"]
    require(
        origin.get("subject_candidate_id") == "cand-1771"
        and origin.get("object_candidate_id") == "cand-1117"
        and origin["qualifiers"].get("place_candidate_id") == "cand-1131",
        "shared-origin endpoints changed",
    )
    shared_q = dict(origin["qualifiers"])
    shared_q["claim"] = "Haskell states that Oliva and Gaulli both came from Genoa; retain this comparative statement as context for the two person-to-place claims."
    shared_q["relation_candidate_note"] = DECISIONS[origin["statement_id"]][1]
    origin["qualifiers"] = shared_q

    origin_quote = "Like Oliva he came from Genoa."
    require(normalized(origin_quote) in normalized("\n".join(source_lines[38:39])), "Genoa sentence changed")
    origin_base = {
        "segment_id": SEGMENT,
        "subject_candidate_id": "",
        "object_candidate_id": "cand-1131",
        "predicate": "came_from",
        "qualifiers": {
            "source_line_start": 39,
            "source_line_end": 39,
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "print_page": 80,
            "pdf_physical_page": 22,
            "place_candidate_id": "cand-1131",
            "qualification": "This is Haskell's biographical claim; external verification is deferred.",
        },
        "original_quote": origin_quote,
        "origin": "book",
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }
    gaulli_origin = dict(origin_base)
    gaulli_origin.update({
        "statement_id": "st-chp3-seciv-l35-46-gaulli-from-genoa",
        "subject_candidate_id": "cand-1117",
        "qualifiers": {
            **origin_base["qualifiers"],
            "claim": "Haskell says Gaulli came from Genoa.",
            "relation_candidate": True,
            "relation_candidate_note": "The pronoun 'he' refers to Gaulli. Reuse the single Genoa mention and keep the person-to-place claim distinct from the comparative sentence.",
        },
    })
    oliva_origin = dict(origin_base)
    oliva_origin.update({
        "statement_id": "st-chp3-seciv-l35-46-oliva-from-genoa",
        "subject_candidate_id": "cand-1771",
        "qualifiers": {
            **origin_base["qualifiers"],
            "claim": "Haskell also says Oliva came from Genoa, as indicated by 'Like Oliva'.",
            "relation_candidate": True,
            "relation_candidate_note": "The comparison explicitly attributes the same place of origin to Oliva; record a separate person-to-place claim without inferring a relation between Oliva and Gaulli.",
        },
    })

    expert_row = by_id["st-chp3-seciv-l35-46-experts-unenthusiastic-private-showing"]
    expert_row["subject_candidate_id"] = experts_id
    expert_row["object_candidate_id"] = "cand-5232"
    expert_row["predicate"] = "experts_reported_unenthusiastic_at_private_showing"
    expert_q = dict(expert_row["qualifiers"])
    expert_q["claim"] = "Haskell reports that the invited experts were not enthusiastic about Gaulli's Gesu work at a private showing."
    expert_q["showing_candidate_id"] = "cand-5239"
    expert_row["qualifiers"] = expert_q

    public_row = by_id["st-chp3-seciv-l35-46-public-admires-painting-and-stucco"]
    public_row["object_candidate_id"] = audience_id
    public_q = dict(public_row["qualifiers"])
    public_q["claim"] = "Haskell reports that the general public admired the beauty of Gaulli's Gesu painting and the arrangement of its stucco."
    public_row["qualifiers"] = public_q

    trouble = by_id["st-chp3-seciv-l35-46-s-agnese-work-caused-trouble"]
    trouble["subject_candidate_id"] = "cand-5231"
    trouble["object_candidate_id"] = "cand-1117"
    trouble["predicate"] = "caused_difficulty_for"
    trouble_q = dict(trouble["qualifiers"])
    trouble_q["claim"] = "Haskell says Gaulli's only important decorative work, the S. Agnese episode, caused difficulty for him."
    trouble["qualifiers"] = trouble_q

    entrusted = by_id["st-chp3-seciv-l35-46-strange-beginning-commission"]
    entrusted["subject_candidate_id"] = "cand-3403"
    entrusted["object_candidate_id"] = "cand-1117"
    entrusted["predicate"] = "entrusted_commission_to_artist"
    entrusted_q = dict(entrusted["qualifiers"])
    entrusted_q["claim"] = "Haskell contrasts the S. Agnese controversy with the Jesuits' later entrusting Gaulli with an exceptionally elaborate commission in Rome."
    entrusted_q["artist_candidate_id"] = "cand-1117"
    entrusted_q["work_candidate_id"] = "cand-5232"
    entrusted["qualifiers"] = entrusted_q

    praise = by_id["st-chp3-seciv-l35-46-oliva-praises-gaulli"]
    praise["object_candidate_id"] = "cand-5232"
    praise["predicate"] = "praised_work_in_negotiation"
    praise_q = dict(praise["qualifiers"])
    praise_q["claim"] = "In negotiations with the Duke, Oliva spoke with fervent admiration of Gaulli's Gesu work and used it to press his argument."
    praise_q["work_candidate_id"] = "cand-5232"
    praise["qualifiers"] = praise_q

    reserved = by_id["st-chp3-seciv-l35-46-tribune-vault-reserved"]
    reserved["predicate"] = "excluded_from_commission_scope"
    reserved_q = dict(reserved["qualifiers"])
    reserved_q["claim"] = "Gaulli's Gesu commission excluded the tribune vault from his scope."
    reserved_q["reserved_for_candidate_id"] = "cand-0399"
    reserved_q["relation_candidate_note"] = "This row records only the exclusion of the vault from Gaulli's scope; the separate reservation for Borgognone is represented by a companion scalar statement."
    reserved["qualifiers"] = reserved_q

    reservation = dict(reserved)
    reservation.update({
        "statement_id": "st-chp3-seciv-l35-46-tribune-vault-reserved-for-borgognone",
        "subject_candidate_id": "cand-5223",
        "object_candidate_id": "cand-0399",
        "predicate": "reserved_for",
        "qualifiers": {
            **reserved_q,
            "claim": "The Gesu tribune vault was being kept for Borgognone.",
            "relation_candidate": True,
            "relation_candidate_note": "The source explicitly says the tribune vault was being kept for Borgognone; preserve this reservation without inferring that he completed it.",
        },
    })

    for row in (gaulli_origin, oliva_origin, reservation):
        statements.append(row)
    by_id = {row["statement_id"]: row for row in statements}
    after_segment = [row for row in statements if row.get("segment_id") == SEGMENT]
    require(len(after_segment) == 39, "planned atomization did not produce 39 segment statements")
    require(
        sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in after_segment) == 31
        and sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in after_segment) == 8
        and all((row.get("qualifiers") or {}).get("relation_candidate") is not None for row in after_segment),
        "segment decisions do not close at 31 relations and 8 nonrelations",
    )
    require(
        by_id["st-chp3-seciv-l35-46-experts-unenthusiastic-private-showing"]["subject_candidate_id"] == experts_id
        and by_id["st-chp3-seciv-l35-46-experts-unenthusiastic-private-showing"]["object_candidate_id"] == "cand-5232"
        and by_id["st-chp3-seciv-l35-46-public-admires-painting-and-stucco"]["object_candidate_id"] == audience_id,
        "audience endpoints are incomplete",
    )
    require(
        by_id["st-chp3-seciv-l35-46-strange-beginning-commission"]["object_candidate_id"] == "cand-1117"
        and by_id["st-chp3-seciv-l35-46-s-agnese-work-caused-trouble"]["subject_candidate_id"] == "cand-5231"
        and by_id["st-chp3-seciv-l35-46-s-agnese-work-caused-trouble"]["object_candidate_id"] == "cand-1117",
        "corrected relation endpoints are inconsistent",
    )

    payloads = {
        TABLE: encode_jsonl(statements, raw_table),
        CANDIDATES: encode_csv(candidates, candidate_fields, raw_candidates),
        MENTIONS: encode_csv(mentions, mention_fields, raw_mentions),
    }
    bilateral = [row for row in statements if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    relation_total = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements)
    bilateral_relations = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in bilateral)
    bilateral_nonrelations = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in bilateral)
    bilateral_pending = sum((row.get("qualifiers") or {}).get("relation_candidate") is None for row in bilateral)
    open_relations = relation_total - bilateral_relations
    require(
        (len(statements), len(candidates), len(mentions), len(bilateral), relation_total, bilateral_relations, bilateral_nonrelations, bilateral_pending, open_relations)
        == (12780, 11581, 27522, 8574, 4957, 4905, 479, 3190, 52),
        "planned global counts do not match the reviewed decisions",
    )

    print(
        "DRY_RUN" if not args.apply else "APPLY",
        "segment_statements=39 relation_candidates=31 nonrelations=8 unresolved=0",
    )
    print(
        f"new_candidates=2 new_mentions=2 new_statements=3 bilateral={len(bilateral)} "
        f"bilateral_relations={bilateral_relations} bilateral_nonrelations={bilateral_nonrelations} "
        f"bilateral_pending={bilateral_pending} total_relation_candidates={relation_total} open_endpoint_relation_candidates={open_relations}"
    )
    print("endpoint_repairs=5 scalar_splits=3 source_coverage=unchanged footnotes=1-6 linked")
    for sid, (flag, note) in DECISIONS.items():
        print(f"  {sid}: relation_candidate={str(flag).lower()} | {note}")

    if not args.apply:
        return

    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    for path, payload in payloads.items():
        atomic_write(path, payload)

    written_statements = read_jsonl(TABLE)
    written_by_id = {row["statement_id"]: row for row in written_statements}
    written_candidates, _, _ = read_csv(CANDIDATES)
    written_mentions, _, _ = read_csv(MENTIONS)
    written_segment = [row for row in written_statements if row.get("segment_id") == SEGMENT]
    require(
        len(written_statements) == 12780 and len(written_candidates) == 11581 and len(written_mentions) == 27522,
        "postwrite table row count mismatch",
    )
    require(
        sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in written_segment) == 31
        and sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in written_segment) == 8,
        "postwrite segment classification mismatch",
    )
    require(
        written_by_id["st-chp3-seciv-l35-46-gaulli-from-genoa"]["subject_candidate_id"] == "cand-1117"
        and written_by_id["st-chp3-seciv-l35-46-gaulli-from-genoa"]["object_candidate_id"] == "cand-1131"
        and written_by_id["st-chp3-seciv-l35-46-oliva-from-genoa"]["subject_candidate_id"] == "cand-1771"
        and written_by_id["st-chp3-seciv-l35-46-oliva-from-genoa"]["object_candidate_id"] == "cand-1131",
        "postwrite origin endpoints mismatch",
    )
    require(
        all(digest(backup) for backup in BACKUPS.values()),
        "a recovery backup is missing",
    )
    print("POSTWRITE_OK", "statements=12780 candidates=11581 mentions=27522")
    for path in (TABLE, CANDIDATES, MENTIONS):
        print("SHA256", digest(path), path.relative_to(ROOT))


if __name__ == "__main__":
    main()
