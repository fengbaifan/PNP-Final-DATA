from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/07_CHP-7_sec_iv.md"
SEGMENT_ID = "chp-7:07_CHP-7_sec_iv:l77-87"
SUFFIX = "bak-s2-chp7-p198-open-endpoints-20261015"

CANDIDATES_TO_ADD = [
    {
        "candidate_id": "cand-12335",
        "canonical_name": "Unidentified studios visited by English milordi in Italian biographical accounts (p. 198)",
        "suggested_type": "place",
        "detail": "Haskell says Italian biographies vividly described English milordi visiting studios. No studio or city is individually named in this sentence.",
        "line": 81,
    },
    {
        "candidate_id": "cand-12336",
        "canonical_name": "Artists from the Italian peninsula invited by English milordi to settle in England (p. 198)",
        "suggested_type": "term",
        "detail": "Haskell cites Italian biographies describing English milordi inviting artists from across the peninsula to settle in England. The artists are unnamed; the destination is explicit.",
        "line": 81,
    },
    {
        "candidate_id": "cand-12337",
        "canonical_name": "English collecting as a historical domain in Haskell's account of Lord Exeter (p. 198)",
        "suggested_type": "term",
        "detail": "Haskell assesses Lord Exeter's significance in the history of English collecting. This term records the stated domain of that assessment; it is not a collection or institution.",
        "line": 80,
    },
    {
        "candidate_id": "cand-12338",
        "canonical_name": "Unidentified intellectual circles in Naples with which Shaftesbury mixed (p. 198)",
        "suggested_type": "term",
        "detail": "Haskell says Shaftesbury mixed in intellectual circles while in Naples. No individual members or named association are supplied.",
        "line": 84,
    },
    {
        "candidate_id": "cand-12339",
        "canonical_name": "Unidentified English friends for whom Shaftesbury bought pictures in Naples (p. 198)",
        "suggested_type": "term",
        "detail": "Haskell says Shaftesbury bought pictures for his English friends while in Naples. The friends are an explicit but unnamed group; no individual recipients are inferred.",
        "line": 84,
    },
    {
        "candidate_id": "cand-12340",
        "canonical_name": "Unidentified discouraging letter from John Closterman to Shaftesbury (p. 198)",
        "suggested_type": "archive",
        "detail": "Haskell says Closterman sent Shaftesbury a highly discouraging letter with drawings of Prudence and Justice. No date, title, or independent archival identity is supplied; Shaftesbury's endorsement remains Haskell's inference.",
        "line": 83,
    },
]

MENTIONS_TO_ADD = [
    {
        "mention_id": "m-chp7-p198-english-milordi-studios",
        "candidate_id": "cand-12335",
        "surface_form": "studios",
        "note": "The unnamed studios visited by English milordi in the Italian biographical accounts cited by Haskell.",
    },
    {
        "mention_id": "m-chp7-p198-english-milordi-invited-artists",
        "candidate_id": "cand-12336",
        "surface_form": "artists from all over the peninsula",
        "note": "Unidentified artists whom the cited biographies say English milordi invited to settle in England; the destination is recorded separately.",
    },
    {
        "mention_id": "m-chp7-p198-english-collecting-domain",
        "candidate_id": "cand-12337",
        "surface_form": "history of English collecting",
        "note": "The domain in which Haskell assesses Lord Exeter's significance.",
    },
    {
        "mention_id": "m-chp7-p198-shaftesbury-intellectual-circles",
        "candidate_id": "cand-12338",
        "surface_form": "intellectual circles",
        "note": "Unnamed circles in Naples with which Haskell says Shaftesbury mixed.",
    },
    {
        "mention_id": "m-chp7-p198-shaftesbury-english-friends",
        "candidate_id": "cand-12339",
        "surface_form": "his English friends",
        "note": "The unnamed recipients for whom Haskell says Shaftesbury bought pictures.",
    },
    {
        "mention_id": "m-chp7-p198-closterman-discouraging-letter",
        "candidate_id": "cand-12340",
        "surface_form": "highly discouraging letter",
        "note": "The unnamed letter whose endorsement Haskell infers; the inference remains attributed to Haskell.",
    },
]

NEW_STATEMENT_IDS = [
    "st-chp7-p198-english-milordi-paid-fabulous-prices",
    "st-chp7-p198-english-milordi-invited-artists-to-england",
    "st-chp7-p198-shaftesbury-bought-pictures-for-english-friends",
    "st-chp7-p198-shaftesbury-applied-ideas-to-choice-of-hercules",
    "st-chp7-p198-shaftesbury-hostile-to-france",
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return raw, list(reader.fieldnames or []), list(reader)


def append_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"), extrasaction="raise").writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline
    return raw + stream.getvalue().encode("utf-8")


def update_claim(row: dict[str, object], *, object_id: str | None, predicate: str, claim: str, quote: str, mentioned: list[str], note: str, open_reason: str | None = None) -> None:
    q = row.setdefault("qualifiers", {})
    row["object_candidate_id"] = object_id
    row["predicate"] = predicate
    q["claim"] = claim
    q["mentioned_candidate_ids"] = mentioned
    q["relation_candidate_note"] = note
    if open_reason:
        q["open_endpoint_reason"] = open_reason
    else:
        q.pop("open_endpoint_reason", None)
    row["qualifiers"] = q
    row["original_quote"] = quote


def clone_statement(template: dict[str, object], statement_id: str) -> dict[str, object]:
    row = copy.deepcopy(template)
    row["statement_id"] = statement_id
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidate_rows = read_csv(CANDIDATES)
    mention_raw, mention_fields, mention_rows = read_csv(MENTIONS)
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    mention_ids = {row["mention_id"] for row in mention_rows}
    max_id = max(int(re.fullmatch(r"cand-(\d+)", cid).group(1)) for cid in candidate_ids)
    if max_id != 12334:
        raise ValueError(f"Candidate sequence changed: expected max 12334, got {max_id}")
    if {row["candidate_id"] for row in CANDIDATES_TO_ADD} & candidate_ids:
        raise ValueError("A planned candidate ID already exists")
    if {row["mention_id"] for row in MENTIONS_TO_ADD} & mention_ids:
        raise ValueError("A planned mention ID already exists")

    segment = next(json.loads(line) for line in SEGMENTS.open(encoding="utf-8") if json.loads(line).get("segment_id") == SEGMENT_ID)
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    added_mentions: list[dict[str, str]] = []
    for mention in MENTIONS_TO_ADD:
        phrase = mention["surface_form"]
        start = text.find(phrase)
        if start < 0 or text.find(phrase, start + 1) >= 0:
            raise ValueError(f"Source phrase missing or repeated for {mention['mention_id']}")
        added_mentions.append({
            "mention_id": mention["mention_id"], "segment_id": SEGMENT_ID,
            "candidate_id": mention["candidate_id"], "surface_form": phrase,
            "start_char": str(start), "end_char": str(start + len(phrase)),
            "note": mention["note"],
        })

    statement_raw = STATEMENTS.read_bytes()
    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines()]
    statement_index = {row["statement_id"]: i for i, row in enumerate(rows)}
    target_ids = {
        "st-chp7-p198-english-tourist-collecting",
        "st-chp7-p198-enthusiasm-and-shaftesbury-theory",
        "st-chp7-p198-exeter-collecting-role",
        "st-chp7-p198-haskell-on-shaftesbury-executant",
        "st-chp7-p198-shaftesbury-buys-pictures-for-friends",
        "st-chp7-p198-shaftesbury-endorsed-letter-inference",
        "st-chp7-p198-shaftesbury-political-sympathies",
    }
    if not target_ids <= statement_index.keys():
        raise ValueError("A target statement is missing")
    if any(sid in statement_index for sid in NEW_STATEMENT_IDS):
        raise ValueError("A planned statement ID already exists")

    before_open = sum(1 for row in rows if (row.get("qualifiers") or {}).get("relation_candidate") is True and (not row.get("subject_candidate_id") or not row.get("object_candidate_id")))
    templates = {sid: copy.deepcopy(rows[statement_index[sid]]) for sid in target_ids}

    for sid, expected_subject in {
        "st-chp7-p198-english-tourist-collecting": "cand-0973",
        "st-chp7-p198-enthusiasm-and-shaftesbury-theory": "cand-2426",
        "st-chp7-p198-exeter-collecting-role": "cand-0984",
        "st-chp7-p198-haskell-on-shaftesbury-executant": "cand-2426",
        "st-chp7-p198-shaftesbury-buys-pictures-for-friends": "cand-2426",
        "st-chp7-p198-shaftesbury-endorsed-letter-inference": "cand-2426",
        "st-chp7-p198-shaftesbury-political-sympathies": "cand-2426",
    }.items():
        row = rows[statement_index[sid]]
        q = row.get("qualifiers") or {}
        if row.get("segment_id") != SEGMENT_ID or row.get("subject_candidate_id") != expected_subject or q.get("relation_candidate") is not True:
            raise ValueError(f"Target statement identity or classification changed: {sid}")

    # English visitors: separate studio visits, unspecified high-price transactions, and artist invitations.
    visitor = rows[statement_index["st-chp7-p198-english-tourist-collecting"]]
    update_claim(
        visitor, object_id="cand-12335", predicate="visited_unnamed_studios",
        claim="Haskell cites Italian biographies' vivid accounts of English milordi visiting studios.",
        quote="the Italian biographies are full of vivid accounts of the English milordi visiting studios",
        mentioned=["cand-0973", "cand-12335"],
        note="The unnamed studios form a source-bounded place group. The coordinated high-price and artist-invitation claims are recorded separately.",
    )
    visitor_price = clone_statement(templates["st-chp7-p198-english-tourist-collecting"], NEW_STATEMENT_IDS[0])
    update_claim(
        visitor_price, object_id=None, predicate="paid_fabulous_prices",
        claim="Haskell cites Italian biographies' accounts of English milordi paying fabulous prices.",
        quote="paying fabulous prices", mentioned=["cand-0973"],
        note="The source reports high prices but identifies no individual transaction or purchased object; preserve that open boundary.",
        open_reason="The biographies are said to describe English milordi paying fabulous prices, but this passage identifies no purchase, transaction, or object of payment.",
    )
    visitor_invites = clone_statement(templates["st-chp7-p198-english-tourist-collecting"], NEW_STATEMENT_IDS[1])
    update_claim(
        visitor_invites, object_id="cand-12336", predicate="invited_artists_to_settle_in_england",
        claim="Haskell cites Italian biographies' accounts of English milordi inviting artists from across the peninsula to settle in England.",
        quote="inviting artists from all over the peninsula to come and settle in England",
        mentioned=["cand-0973", "cand-12336", "cand-8983"],
        note="The invited artists are an explicit unnamed group and England is the stated destination; preserve the biographies as Haskell's source layer.",
    )

    # Shaftesbury's theorising concerns English patronage; Haskell's causal interpretation remains explicit.
    enthusiasm = rows[statement_index["st-chp7-p198-enthusiasm-and-shaftesbury-theory"]]
    q = enthusiasm["qualifiers"]
    enthusiasm["object_candidate_id"] = "cand-0969"
    q["mentioned_candidate_ids"] = ["cand-2426", "cand-0969"]
    q["relation_candidate_note"] = "English patronage is the subject of Shaftesbury's theorising; Haskell's claim that indiscriminate enthusiasm led to it remains an attributed causal interpretation."
    q.pop("open_endpoint_reason", None)

    # Exeter's significance assessment has an explicit domain: the history of English collecting.
    exeter = rows[statement_index["st-chp7-p198-exeter-collecting-role"]]
    q = exeter["qualifiers"]
    exeter["object_candidate_id"] = "cand-12337"
    q["mentioned_candidate_ids"] = ["cand-0984", "cand-12337"]
    q["relation_candidate_note"] = "The object is the source-named historical domain of English collecting; Haskell's significance assessment remains qualitative, not quantified."
    q.pop("open_endpoint_reason", None)

    # The immediately preceding sentence identifies the actual creation in Haskell's assessment.
    executant = rows[statement_index["st-chp7-p198-haskell-on-shaftesbury-executant"]]
    q = executant["qualifiers"]
    executant["object_candidate_id"] = "cand-7245"
    q["mentioned_candidate_ids"] = ["cand-2426", "cand-7245"]
    q["relation_candidate_note"] = "The actual creation is the Choice of Hercules named in the preceding sentence. The application judgment remains Haskell's evaluation, not a direct statement by Shaftesbury."
    q.pop("open_endpoint_reason", None)

    # Split the mixed Naples sentence into intellectual circles, picture recipients, and the named experiment.
    mixed_template = templates["st-chp7-p198-shaftesbury-buys-pictures-for-friends"]
    mixed = rows[statement_index["st-chp7-p198-shaftesbury-buys-pictures-for-friends"]]
    update_claim(
        mixed, object_id="cand-12338", predicate="mixed_in_naples_intellectual_circles",
        claim="Haskell says Shaftesbury mixed in intellectual circles in Naples.",
        quote="There he mixed in intellectual circles", mentioned=["cand-2426", "cand-1722", "cand-12338"],
        note="The unnamed intellectual circles are a source-bounded group in Naples; no individual members or named association are inferred.",
    )
    friends = clone_statement(mixed_template, NEW_STATEMENT_IDS[2])
    update_claim(
        friends, object_id="cand-12339", predicate="bought_pictures_for_english_friends",
        claim="Haskell says Shaftesbury bought pictures for his English friends while in Naples.",
        quote="bought pictures for his English friends", mentioned=["cand-2426", "cand-12339"],
        note="The recipients are an explicit unnamed group; no individual friends or picture titles are inferred.",
    )
    ideas = clone_statement(mixed_template, NEW_STATEMENT_IDS[3])
    update_claim(
        ideas, object_id="cand-7245", predicate="decided_to_apply_aesthetic_ideas_to_choice_of_hercules",
        claim="Haskell says Shaftesbury decided to put his aesthetic ideas into practice; the next sentence identifies his experiment as the Choice of Hercules.",
        quote="decided to put his aesthetic ideas into practice", mentioned=["cand-2426", "cand-7245"],
        note="The next sentence names the Choice of Hercules as the experiment. This records Shaftesbury's intention as Haskell presents it and does not claim that the work realized every idea.",
    )
    ideas["qualifiers"]["related_statement_ids"] = ["st-chp7-p198-shaftesbury-de-matteis-choice-hercules"]

    # The letter is identified as the object; endorsement remains an authorial inference.
    endorsement = rows[statement_index["st-chp7-p198-shaftesbury-endorsed-letter-inference"]]
    update_claim(
        endorsement, object_id="cand-12340", predicate="must_have_endorsed_discouraging_letter",
        claim="Haskell infers that Shaftesbury must have endorsed Closterman's highly discouraging letter.",
        quote="Closterman sent him some drawings of Prudence and Justice by Domenico Guidi with a highly discouraging letter which Shaftesbury must have endorsed",
        mentioned=["cand-2426", "cand-0791", "cand-12340"],
        note="The letter itself is identified as the object. Whether Shaftesbury endorsed it remains Haskell's inference; no direct response is claimed.",
    )

    # Split the two political attitudes to retain their opposite directions and explicit endpoints.
    political_template = templates["st-chp7-p198-shaftesbury-political-sympathies"]
    holland = rows[statement_index["st-chp7-p198-shaftesbury-political-sympathies"]]
    update_claim(
        holland, object_id="cand-7238", predicate="described_as_sympathetic_to_holland",
        claim="Haskell describes Shaftesbury as an eager Whig intellectual, deeply sympathetic to Holland.",
        quote="an eager Whig intellectual, deeply sympathetic to Holland", mentioned=["cand-2426", "cand-7238"],
        note="Haskell's characterization of political sympathy is retained; no office, policy, or formal affiliation is inferred.",
    )
    france = clone_statement(political_template, NEW_STATEMENT_IDS[4])
    update_claim(
        france, object_id="cand-7223", predicate="described_as_hostile_to_france",
        claim="Haskell describes Shaftesbury as hostile to France.",
        quote="hostile to France", mentioned=["cand-2426", "cand-7223"],
        note="Haskell's characterization of hostility is retained; it does not specify a policy or formal affiliation.",
    )

    new_rows = [visitor_price, visitor_invites, friends, ideas, france]
    statement_after = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows + new_rows).encode("utf-8")
    added_candidates = [
        {
            "candidate_id": c["candidate_id"], "index_entry_id": "",
            "canonical_name": c["canonical_name"], "index_page_range": "",
            "suggested_type": c["suggested_type"], "status": "open",
            "index_source_file": "", "sub_entry": "", "detail": c["detail"],
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{c['line']}",
        }
        for c in CANDIDATES_TO_ADD
    ]
    candidate_after = append_csv(candidate_raw, candidate_fields, added_candidates)
    mention_after = append_csv(mention_raw, mention_fields, added_mentions)
    paths = {CANDIDATES: candidate_after, MENTIONS: mention_after, STATEMENTS: statement_after}
    backups = {path: path.with_name(f"{path.name}.{SUFFIX}") for path in paths}
    after_open_rows = [
        json.loads(line) for line in statement_after.decode("utf-8").splitlines()
        if json.loads(line).get("segment_id") == SEGMENT_ID
        and (json.loads(line).get("qualifiers") or {}).get("relation_candidate") is True
        and (not json.loads(line).get("subject_candidate_id") or not json.loads(line).get("object_candidate_id"))
    ]
    after_open = sum(
        1 for line in statement_after.decode("utf-8").splitlines()
        if (lambda row: (row.get("qualifiers") or {}).get("relation_candidate") is True and (not row.get("subject_candidate_id") or not row.get("object_candidate_id")))(json.loads(line))
    )
    print(f"candidate_rows={len(candidate_rows)}->{len(candidate_rows) + len(added_candidates)}")
    print(f"mention_rows={len(mention_rows)}->{len(mention_rows) + len(added_mentions)}")
    print(f"statement_rows={len(rows)}->{len(rows) + len(new_rows)}")
    print(f"open_endpoints={before_open}->{after_open}")
    print(f"segment_open={[row['statement_id'] for row in after_open_rows]}")
    for path, data in paths.items():
        print(f"{path.relative_to(ROOT)} {digest(path.read_bytes())}->{digest(data)}")
    if args.preview:
        return 0
    if any(path.exists() for path in backups.values()):
        raise FileExistsError("A recovery copy already exists; refusing to overwrite it")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    temps: dict[Path, Path] = {}
    try:
        for path, data in paths.items():
            temp = path.with_name(f"{path.name}.tmp-{SUFFIX}")
            if temp.exists():
                raise FileExistsError(f"Temporary file already exists: {temp}")
            temp.write_bytes(data)
            temps[path] = temp
        for path, temp in temps.items():
            temp.replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        raise
    for path, backup in backups.items():
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.relative_to(ROOT)}:{digest(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
