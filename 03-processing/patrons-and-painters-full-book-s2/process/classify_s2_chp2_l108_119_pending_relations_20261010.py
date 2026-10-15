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
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_i.md"
SEGMENT = "chp-2:02_CHP-2_sec_i:l108-119"
EXPECTED_HASHES = {
    STATEMENTS.name: "33c48449209a733ec376552998667f6068430db62737a8a30b09a8317c0276e1",
    CANDIDATES.name: "b888e887179fcfeab5e94cf53537c8d190dfa4c1dc7d23243760e8fd5e917c4c",
    MENTIONS.name: "b06efbe0258fb9b7e25a83d28e909ca98ff73dec53c42ca6a2669ad55fbd7ad9",
}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp2-l108-119-pending-20261010"),
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + ".bak-s2-chp2-l108-119-pending-20261010"),
    MENTIONS: MENTIONS.with_name(MENTIONS.name + ".bak-s2-chp2-l108-119-pending-20261010"),
}

TRUE_NOTES = {
    "st-chp2-seci-l108-119-attention-focused-on-reformers":
        "The source says Giustiniani concentrated his attention on Caravaggio, the Carracci, and their followers. The primary endpoint and other_candidate_ids preserve the full stated scope.",
    "st-chp2-seci-l108-119-barberini-could-not-claim-elite-status":
        "This is Haskell's comparative assessment of the Barberini family's capacity to employ Bernini; it is not evidence of an actual commission or employment.",
    "st-chp2-seci-l108-119-david-self-portrait-reported":
        "The source attributes Bernini's own features to the David figure in a reported carving anecdote. Preserve the chapter 1 qualification; this is not an independently verified event.",
    "st-chp2-seci-l108-119-giustiniani-artistic-culture":
        "Haskell directly compares Giustiniani's artistic culture with Rubens as the stated exception. Retain the authorial ranking and footnote context.",
    "st-chp2-seci-l108-119-maffeo-appreciated-bernini":
        "The source says Maffeo recognized Bernini's talent; 'genius' remains Haskell's evaluation rather than an independently measured attribute.",
    "st-chp2-seci-l108-119-maffeo-bided-time":
        "The source relates Maffeo's constrained opportunity to Bernini's patronage. This is Haskell's retrospective account, not a precisely dated employment event.",
    "st-chp2-seci-l108-119-maffeo-held-mirror-for-david":
        "The reported action is Maffeo holding a mirror for Bernini. The object endpoint is corrected to Bernini; David remains a mentioned work in the source and in the separate self-portrait statement. Preserve the cross-chapter qualification; this remains an anecdote.",
    "st-chp2-seci-l108-119-maffeo-maintained-household":
        "This records Maffeo's maintenance of a household as reported. A passage-specific open candidate preserves the reference without assuming identity with the combined Barberini family-and-household KU.",
    "st-chp2-seci-l108-119-maffeo-wrote-epigrams":
        "The source says Maffeo wrote Latin epigrams on Bernini's group; the work endpoint is explicit, while no poems are named or quoted.",
    "st-chp2-seci-l108-119-mannerists-scarcely-represented":
        "The source says the older Mannerist artists were scarcely represented in Giustiniani's palace. Preserve the qualitative scope and unnamed group.",
    "st-chp2-seci-l108-119-paul-v-and-scipione-patronage":
        "A passage-specific collective subject preserves Paul V and Scipione Borghese as the source's grouped grammatical subject without assigning works to either individually. The later Ludovisi phase after 1621 is recorded separately.",
    "st-chp2-seci-l108-119-planned-future-use-inferred":
        "The source implies a future use of Bernini by Maffeo but marks it as Haskell's conjecture. Retain a source-derived relation candidate, not a verified plan.",
}
FALSE_NOTE = (
    "This evaluates the earlier works as pleasing yet minor; it does not state a relation between "
    "the two work candidates. They remain referents in the claim, but no binary S2 relation is asserted."
)
EXPECTED_FALSE = "st-chp2-seci-l108-119-earlier-works-evaluated"
HOUSEHOLD_MENTION_ID = "m-chp2-seci-l108-119-0027"
GROUP_MENTION_ID = "m-chp2-seci-l108-119-0072"
HOUSEHOLD_CANDIDATE = {
    "candidate_id": "cand-11581",
    "index_entry_id": "",
    "canonical_name": "Maffeo Barberini's household (membership and identity unresolved)",
    "index_page_range": "",
    "suggested_type": "institution",
    "status": "open",
    "index_source_file": "",
    "sub_entry": "",
    "detail": (
        "The passage says Maffeo Barberini maintained a great household but does not identify "
        "its membership, organization, or relation to the existing combined Barberini family-and-household KU."
    ),
    "exclude_reason": "",
    "candidate_origin": "body-mention",
    "candidate_source_ref": f"{SEGMENT}#L112",
}
PATRON_GROUP_CANDIDATE = {
    "candidate_id": "cand-11582",
    "index_entry_id": "",
    "canonical_name": "Pope Paul V and Scipione Borghese (collective Bernini patronage reference)",
    "index_page_range": "",
    "suggested_type": "",
    "status": "open",
    "index_source_file": "",
    "sub_entry": "",
    "detail": (
        "Source-defined collective reference to Pope Paul V (cand-0393) and Scipione Borghese "
        "(cand-0394) in the statement about Bernini's output. The passage does not allocate works "
        "between them or claim that they jointly commissioned individual works; it contrasts their "
        "period with the Ludovisi phase after 1621."
    ),
    "exclude_reason": "",
    "candidate_origin": "body-mention",
    "candidate_source_ref": f"{SEGMENT}#L116",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def csv_read(path: Path) -> tuple[list[dict], list[str], bytes]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or []), raw


def csv_serialize(path: Path, rows: list[dict], fields: list[str], raw: bytes) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    return prefix + output.getvalue().encode("utf-8")


def jsonl_read(path: Path) -> tuple[list[dict], bytes]:
    raw = path.read_bytes()
    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    return rows, raw


def jsonl_serialize(rows: list[dict], raw: bytes) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    prefix = "\ufeff" if raw.startswith(b"\xef\xbb\xbf") else ""
    return (prefix + "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + newline
                             for row in rows)).encode("utf-8")


def segment_text(source_lines: list[str]) -> str:
    return "\n".join(source_lines[107:119])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply the reviewed classifications and endpoint repairs")
    args = parser.parse_args()

    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        actual = sha256(path.read_bytes())
        require(actual == EXPECTED_HASHES[path.name], f"{path.name} changed since review: {actual}")
    for path, backup in BACKUPS.items():
        require(not backup.exists(), f"recovery backup already exists: {backup.name}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    require(len(source_lines) >= 119, "source segment is incomplete")
    require("Cardinal Barberini meanwhile maintained a great household" in source_lines[111],
            "household source line changed")
    group_surface = "the reigning Pope Paul V and his nephew Scipione Borghese"
    require(group_surface in source_lines[115], "collective patron source phrase changed")
    require("holding up the mirror for him to carve his own features as David" in source_lines[117],
            "mirror anecdote source line changed")

    statements, statement_raw = jsonl_read(STATEMENTS)
    candidates, candidate_fields, candidate_raw = csv_read(CANDIDATES)
    mentions, mention_fields, mention_raw = csv_read(MENTIONS)
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    require(len(statement_by_id) == len(statements), "duplicate statement_id")
    require(len(candidate_by_id) == len(candidates), "duplicate candidate_id")
    require(len(mention_by_id) == len(mentions), "duplicate mention_id")

    expected_ids = set(TRUE_NOTES) | {EXPECTED_FALSE}
    pending_bilateral = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT
        and row.get("subject_candidate_id") and row.get("object_candidate_id")
        and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    require(pending_bilateral == expected_ids,
            f"pending bilateral set changed: {sorted(pending_bilateral ^ expected_ids)}")
    require(max(int(row["candidate_id"].split("-")[1]) for row in candidates) == 11580,
            "candidate table changed since candidate allocation")
    require(HOUSEHOLD_MENTION_ID in mention_by_id, "household mention is missing")
    household_mention = mention_by_id[HOUSEHOLD_MENTION_ID]
    require(household_mention["candidate_id"] == "cand-2979"
            and household_mention["surface_form"] == "great household",
            "household mention mapping changed")
    require(GROUP_MENTION_ID not in mention_by_id, "group mention ID already exists")

    text = segment_text(source_lines)
    line_116_base = sum(len(source_lines[index - 1]) + 1 for index in range(108, 116))
    group_start = line_116_base + source_lines[115].index(group_surface)
    group_end = group_start + len(group_surface)
    require(text[group_start:group_end] == group_surface, "collective mention span does not match source")

    natural_keys = {
        (row["canonical_name"].casefold().strip(), row["suggested_type"].casefold().strip())
        for row in candidates
    }
    for candidate in (HOUSEHOLD_CANDIDATE, PATRON_GROUP_CANDIDATE):
        key = (candidate["canonical_name"].casefold().strip(), candidate["suggested_type"].casefold().strip())
        require(key not in natural_keys, f"candidate natural-key collision: {candidate['candidate_id']}")
        natural_keys.add(key)
    require("cand-11581" not in candidate_by_id and "cand-11582" not in candidate_by_id,
            "allocated candidate ID already exists")
    require(candidate_fields == list(HOUSEHOLD_CANDIDATE),
            "candidate field order differs from the reviewed record")

    new_group_mention = {
        "mention_id": GROUP_MENTION_ID,
        "segment_id": SEGMENT,
        "candidate_id": "cand-11582",
        "surface_form": group_surface,
        "start_char": str(group_start),
        "end_char": str(group_end),
        "note": (
            "Collective source phrase naming Pope Paul V and Scipione Borghese in the Bernini-output "
            "statement; it does not assign individual works or commissions."
        ),
    }
    require(mention_fields == list(new_group_mention),
            "mention field order differs from the reviewed record")

    for statement_id in TRUE_NOTES:
        row = statement_by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        start = qualifiers.get("source_line_start")
        end = qualifiers.get("source_line_end")
        require(row.get("segment_id") == SEGMENT, f"{statement_id} is outside the reviewed segment")
        require(isinstance(start, int) and isinstance(end, int) and 108 <= start <= end <= 119,
                f"{statement_id} has an invalid source anchor")
        anchor = "\n".join(source_lines[start - 1:end])
        require(row.get("original_quote") in anchor, f"{statement_id} quote no longer matches source")
        require(qualifiers.get("relation_candidate") is None, f"{statement_id} was already classified")
    false_row = statement_by_id[EXPECTED_FALSE]
    require((false_row.get("qualifiers") or {}).get("relation_candidate") is None,
            f"{EXPECTED_FALSE} was already classified")
    require(false_row.get("subject_candidate_id") == "cand-4349"
            and false_row.get("object_candidate_id") == "cand-3181",
            "earlier-works referents changed")
    require(statement_by_id["st-chp2-seci-l108-119-maffeo-held-mirror-for-david"].get("object_candidate_id") == "cand-3181",
            "mirror endpoint changed")
    require(statement_by_id["st-chp2-seci-l108-119-maffeo-maintained-household"].get("object_candidate_id") == "cand-2979",
            "household endpoint changed")
    require(statement_by_id["st-chp2-seci-l108-119-paul-v-and-scipione-patronage"].get("subject_candidate_id") == "cand-0393",
            "patron group endpoint changed")

    projected = json.loads(json.dumps(statements, ensure_ascii=False))
    projected_by_id = {row["statement_id"]: row for row in projected}
    for statement_id, note in TRUE_NOTES.items():
        row = projected_by_id[statement_id]
        qualifiers = dict(row.get("qualifiers") or {})
        qualifiers["relation_candidate"] = True
        qualifiers["relation_candidate_note"] = note
        row["qualifiers"] = qualifiers
    false_qualifiers = dict(projected_by_id[EXPECTED_FALSE].get("qualifiers") or {})
    false_qualifiers["relation_candidate"] = False
    false_qualifiers["relation_candidate_note"] = FALSE_NOTE
    projected_by_id[EXPECTED_FALSE]["qualifiers"] = false_qualifiers

    mirror = projected_by_id["st-chp2-seci-l108-119-maffeo-held-mirror-for-david"]
    mirror["object_candidate_id"] = "cand-0295"
    mirror_q = dict(mirror["qualifiers"])
    mirror_q.pop("artist_candidate_id", None)
    mirror_q["mentioned_candidate_ids"] = ["cand-0209", "cand-0295", "cand-3181"]
    mirror["qualifiers"] = mirror_q

    household_statement = projected_by_id["st-chp2-seci-l108-119-maffeo-maintained-household"]
    household_statement["object_candidate_id"] = "cand-11581"

    patron_statement = projected_by_id["st-chp2-seci-l108-119-paul-v-and-scipione-patronage"]
    patron_statement["subject_candidate_id"] = "cand-11582"
    patron_q = dict(patron_statement["qualifiers"])
    patron_q.pop("other_patron_candidate_id", None)
    patron_q["mentioned_candidate_ids"] = ["cand-0393", "cand-0394", "cand-11582", "cand-0295", "cand-4348"]
    patron_statement["qualifiers"] = patron_q

    projected_candidates = candidates + [HOUSEHOLD_CANDIDATE, PATRON_GROUP_CANDIDATE]
    projected_mentions = list(mentions)
    household_mention = next(row for row in projected_mentions if row["mention_id"] == HOUSEHOLD_MENTION_ID)
    household_mention["candidate_id"] = "cand-11581"
    household_mention["note"] = (
        "The passage says Maffeo maintained a great household. Keep this reference separate from the "
        "combined Barberini family-and-household KU pending identity and scope review."
    )
    projected_mentions.append(new_group_mention)
    for mention in projected_mentions:
        if mention.get("segment_id") == SEGMENT:
            start, end = int(mention["start_char"]), int(mention["end_char"])
            require(0 <= start < end <= len(text), f"invalid mention span: {mention['mention_id']}")
            require(text[start:end] == mention["surface_form"], f"mention/source mismatch: {mention['mention_id']}")
    for row in projected:
        if row.get("segment_id") == SEGMENT:
            for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
                require(not endpoint or endpoint in {item["candidate_id"] for item in projected_candidates},
                        f"missing endpoint after repair in {row['statement_id']}")

    before = {
        "relation_true_bilateral": sum(1 for row in statements if row.get("subject_candidate_id") and row.get("object_candidate_id") and (row.get("qualifiers") or {}).get("relation_candidate") is True),
        "relation_false_bilateral": sum(1 for row in statements if row.get("subject_candidate_id") and row.get("object_candidate_id") and (row.get("qualifiers") or {}).get("relation_candidate") is False),
        "unclassified_bilateral": sum(1 for row in statements if row.get("subject_candidate_id") and row.get("object_candidate_id") and (row.get("qualifiers") or {}).get("relation_candidate") is None),
    }
    after = {
        "relation_true_bilateral": sum(1 for row in projected if row.get("subject_candidate_id") and row.get("object_candidate_id") and (row.get("qualifiers") or {}).get("relation_candidate") is True),
        "relation_false_bilateral": sum(1 for row in projected if row.get("subject_candidate_id") and row.get("object_candidate_id") and (row.get("qualifiers") or {}).get("relation_candidate") is False),
        "unclassified_bilateral": sum(1 for row in projected if row.get("subject_candidate_id") and row.get("object_candidate_id") and (row.get("qualifiers") or {}).get("relation_candidate") is None),
    }
    require(before == {"relation_true_bilateral": 3969, "relation_false_bilateral": 449, "unclassified_bilateral": 4079},
            f"unexpected pre-write counts: {before}")
    require(after == {"relation_true_bilateral": 3981, "relation_false_bilateral": 450, "unclassified_bilateral": 4066},
            f"unexpected projected counts: {after}")

    payload = {
        STATEMENTS: jsonl_serialize(projected, statement_raw),
        CANDIDATES: csv_serialize(CANDIDATES, projected_candidates, candidate_fields, candidate_raw),
        MENTIONS: csv_serialize(MENTIONS, projected_mentions, mention_fields, mention_raw),
    }
    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "segment": SEGMENT,
        "classified_true": len(TRUE_NOTES),
        "classified_false": 1,
        "endpoint_repairs": {
            "mirror_object": ["cand-3181", "cand-0295"],
            "household_object": ["cand-2979", "cand-11581"],
            "patron_group_subject": ["cand-0393", "cand-11582"],
        },
        "new_candidates": ["cand-11581", "cand-11582"],
        "household_mention_retargeted": HOUSEHOLD_MENTION_ID,
        "new_mentions": [GROUP_MENTION_ID],
        "before": before,
        "after": after,
        "payload_sha256": {path.name: sha256(data) for path, data in payload.items()},
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write.")
        return

    originals = {path: path.read_bytes() for path in payload}
    written: list[Path] = []
    try:
        for path, backup in BACKUPS.items():
            shutil.copy2(path, backup)
        for path, data in payload.items():
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                handle.write(data)
                temp_path = Path(handle.name)
            os.replace(temp_path, path)
            written.append(path)
        actual_statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        actual_candidates, _, _ = csv_read(CANDIDATES)
        actual_mentions, _, _ = csv_read(MENTIONS)
        actual_by_id = {row["statement_id"]: row for row in actual_statements}
        require(len(actual_statements) == len(statements), "statement count changed")
        require(len(actual_candidates) == len(candidates) + 2, "candidate count did not increase by two")
        require(len(actual_mentions) == len(mentions) + 1, "mention count did not increase by one")
        require(all((actual_by_id[key].get("qualifiers") or {}).get("relation_candidate") is True for key in TRUE_NOTES),
                "one or more true classifications were not persisted")
        require((actual_by_id[EXPECTED_FALSE].get("qualifiers") or {}).get("relation_candidate") is False,
                "non-relation classification was not persisted")
        require(actual_by_id["st-chp2-seci-l108-119-maffeo-held-mirror-for-david"]["object_candidate_id"] == "cand-0295",
                "mirror endpoint repair was not persisted")
    except Exception:
        for path in written:
            path.write_bytes(originals[path])
        raise
    print(json.dumps({
        "result": "applied",
        "candidate_count": len(actual_candidates),
        "mention_count": len(actual_mentions),
        "statement_count": len(actual_statements),
        "sha256": {path.name: sha256(path.read_bytes()) for path in payload},
        "backups": [backup.name for backup in BACKUPS.values()],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
