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
TABLE_DIR = ROOT / "04-knowledge/tables"
STATEMENTS = TABLE_DIR / "book-statements.jsonl"
CANDIDATES = TABLE_DIR / "entity-candidates.csv"
MENTIONS = TABLE_DIR / "mentions.csv"
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
SEGMENT = "chp-2:02_CHP-2_sec_ii:l42-50"
EXPECTED_HASHES = {
    STATEMENTS.name: "afff0a6e96245c9f45265a83f6da1b5a59458533fbafe83c32d5aace6f9541e5",
    CANDIDATES.name: "f00f98b32a7e9f9d6e6f8594f1b427eb3014b12493d12782d35c28cb1100ac9b",
    MENTIONS.name: "85fdb58891333e4eb62f0dcd30db256fce1029cb81006128a86194e96fe3153a",
}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp2-sec-ii-l42-50-20261010"),
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + ".bak-s2-chp2-sec-ii-l42-50-20261010"),
    MENTIONS: MENTIONS.with_name(MENTIONS.name + ".bak-s2-chp2-sec-ii-l42-50-20261010"),
}
NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11585",
        "index_entry_id": "",
        "canonical_name": "Twisted-column architectural form in Haskell’s account",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell discusses the twisted column as an architectural form, reporting its supposed derivation "
            "from Solomon’s Temple, its use in screens of ancient basilicas, and Raphael’s admiration of the form. "
            "Keep this concept distinct from Bernini’s physical baldacchino columns (cand-4394) and the unnamed "
            "column said to be preserved at St Peter’s (cand-11586); the historical associations remain source-reported."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": SEGMENT + "#L45",
    },
    {
        "candidate_id": "cand-11586",
        "index_entry_id": "",
        "canonical_name": "Unnamed twisted column said to be preserved in St Peter’s",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell says one twisted column was preserved in St Peter’s itself and that Christ was supposed to "
            "have leaned against it. Its identity and the tradition are not independently verified. Keep this "
            "source-mentioned column distinct from Bernini’s baldacchino columns (cand-4394) and from the general "
            "twisted-column form (cand-11585)."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": SEGMENT + "#L45",
    },
]
TRUE_NOTES = {
    "st-chp2-secii-l42-50-barberini_bees_decoration":
        "Haskell describes the Barberini bees on the baldacchino's physical columns and cornice tassels. Preserve this as the author's visual description of the emblematic motif.",
    "st-chp2-secii-l42-50-barberini_history_linked_to_church":
        "This records Haskell's interpretation that the Barberini family history became indelibly linked with St Peter's; do not recast the interpretive phrase as a formal family or church relation.",
    "st-chp2-secii-l42-50-barberini_sun_decoration":
        "Haskell places the Barberini sun motif above the baldacchino's capitals; this is a source-reported visual description.",
    "st-chp2-secii-l42-50-column_preserved_at_st_peters":
        "Haskell refers to an unnamed twisted column said to be preserved in St Peter's and repeats a tradition that Christ leaned against it. Keep this object distinct from Bernini's baldacchino columns and preserve both 'supposed' qualifications.",
    "st-chp2-secii-l42-50-committee_decided_altars":
        "The passage explicitly reports the unnamed decoration committee's June 1627 decision to build special altars in the dome-support pillars' niches; the plan is later revised in the continuation.",
    "st-chp2-secii-l42-50-committee_nominal_control":
        "Haskell distinguishes the committee's nominal control of alterations from the Pope's decisive influence; retain 'nominally' and the unresolved identity of the committee.",
    "st-chp2-secii-l42-50-cost_reported":
        "Haskell reports the baldacchino's cost as 200,000 scudi, one tenth of the Papal States' annual income. Preserve the correction from OCR 'soldi' to the print reading 'scudi' and the unverified source attribution.",
    "st-chp2-secii-l42-50-cross_replaced_risen_christ":
        "Haskell reports a change from the planned Risen Christ statue to a Cross and interprets the shift as passion rather than triumph; neither design is treated as proof of a completed statue or separate Cross sculpture.",
    "st-chp2-secii-l42-50-epigram_followed_removal":
        "Haskell says Pantheon bronze removal led to a bitter epigram by Urban VIII's unnamed personal doctor. The note identifies a textual source, not independently verified authorship or motive.",
    "st-chp2-secii-l42-50-iconography_simple":
        "The assessment concerns this specific work's iconography; retain Haskell's comparison with most religious art of the period and do not treat 'relatively simple' as a formal classification.",
    "st-chp2-secii-l42-50-laurel_instead_of_vine":
        "Haskell infers from botanical knowledge that the column leaves are laurel, another Barberini emblem, rather than the traditional vine. Preserve the inference and visual contrast.",
    "st-chp2-secii-l42-50-pantheon_bronze_removed":
        "Haskell says bronze was removed from the Pantheon for the baldacchino at Bernini's suggestion; the source does not identify who carried out the removal or its amount.",
    "st-chp2-secii-l42-50-planned_risen_christ_statue":
        "Haskell reports the original plan to crown the baldacchino with a huge Risen Christ statue; retain that it was planned and do not imply it was executed.",
    "st-chp2-secii-l42-50-pope_deferred_choice_to_committee":
        "Haskell says Urban VIII saw the proposals and left selection to the committee. The accepted scheme and later altar revision occur in the continuation and remain separately recorded.",
    "st-chp2-secii-l42-50-pope_influence_decisive":
        "This preserves Haskell's explicit assessment that the Pope's influence over St Peter's decoration was decisive, while the same passage describes committee control as nominal.",
    "st-chp2-secii-l42-50-references_to_peter_and_papacy":
        "Haskell says references to St Peter and the establishment of the papacy were confined to small angels above the cornice; preserve the source's scope and keep Peter the person distinct from the basilica.",
    "st-chp2-secii-l42-50-solomon_temple_precedent":
        "Haskell says the architectural form was 'supposed to derive' from Solomon's Temple; this is a reported tradition, not verified architectural genealogy.",
    "st-chp2-secii-l42-50-twisted_column_basilica_screens":
        "This concerns the general twisted-column form in screens of many ancient basilicas, including St Peter's, not a claim that Bernini's specific baldacchino columns formed the basilica's screen.",
    "st-chp2-secii-l42-50-twisted_columns_admired_by_raphael":
        "Haskell reports Raphael's admiration of the twisted-column form; the claim concerns the form, not Raphael's admiration of Bernini's later physical columns.",
    "st-chp2-secii-l42-50-urban_ensured_identification":
        "Haskell says Urban ensured close identification with the iconographic scheme. Keep this distinct from the preceding statement that his direct role in outlining it was only probable.",
    "st-chp2-secii-l42-50-urban_role_in_scheme":
        "Haskell says Urban VIII probably played a direct part in outlining the baldacchino's iconographic scheme; preserve 'probably' and do not upgrade the conjecture.",
}
OLD_ENDPOINTS = {
    "st-chp2-secii-l42-50-barberini_bees_decoration": ("cand-4398", "cand-4394"),
    "st-chp2-secii-l42-50-barberini_history_linked_to_church": ("cand-3464", "cand-3135"),
    "st-chp2-secii-l42-50-barberini_sun_decoration": ("cand-4399", "cand-4234"),
    "st-chp2-secii-l42-50-column_preserved_at_st_peters": ("cand-4394", "cand-3135"),
    "st-chp2-secii-l42-50-committee_decided_altars": ("cand-4306", "cand-4403"),
    "st-chp2-secii-l42-50-committee_nominal_control": ("cand-4306", "cand-3135"),
    "st-chp2-secii-l42-50-cost_reported": ("cand-4234", "cand-1831"),
    "st-chp2-secii-l42-50-cross_replaced_risen_christ": ("cand-4392", "cand-4393"),
    "st-chp2-secii-l42-50-epigram_followed_removal": ("cand-4402", "cand-4401"),
    "st-chp2-secii-l42-50-iconography_simple": ("cand-4397", "cand-4234"),
    "st-chp2-secii-l42-50-laurel_instead_of_vine": ("cand-4400", "cand-4394"),
    "st-chp2-secii-l42-50-pantheon_bronze_removed": ("cand-4234", "cand-4236"),
    "st-chp2-secii-l42-50-planned_risen_christ_statue": ("cand-4234", "cand-4392"),
    "st-chp2-secii-l42-50-pope_deferred_choice_to_committee": ("cand-0209", "cand-4306"),
    "st-chp2-secii-l42-50-pope_influence_decisive": ("cand-0209", "cand-3135"),
    "st-chp2-secii-l42-50-references_to_peter_and_papacy": ("cand-4397", "cand-4231"),
    "st-chp2-secii-l42-50-solomon_temple_precedent": ("cand-4394", "cand-4395"),
    "st-chp2-secii-l42-50-twisted_column_basilica_screens": ("cand-4394", "cand-3135"),
    "st-chp2-secii-l42-50-twisted_columns_admired_by_raphael": ("cand-4394", "cand-2098"),
    "st-chp2-secii-l42-50-urban_ensured_identification": ("cand-0209", "cand-4397"),
    "st-chp2-secii-l42-50-urban_role_in_scheme": ("cand-0209", "cand-4397"),
}
FINAL_ENDPOINTS = dict(OLD_ENDPOINTS)
FINAL_ENDPOINTS.update({
    "st-chp2-secii-l42-50-column_preserved_at_st_peters": ("cand-11586", "cand-3135"),
    "st-chp2-secii-l42-50-solomon_temple_precedent": ("cand-11585", "cand-4395"),
    "st-chp2-secii-l42-50-twisted_column_basilica_screens": ("cand-11585", "cand-3135"),
    "st-chp2-secii-l42-50-twisted_columns_admired_by_raphael": ("cand-11585", "cand-2098"),
})
MENTION_RETARGETS = {
    "m-chp2-secii-l42-50-0019": ("cand-4394", "cand-11585"),
    "m-chp2-secii-l42-50-0022": ("cand-4394", "cand-11586"),
    "m-chp2-secii-l42-50-0026": ("cand-4394", "cand-11585"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return raw, list(reader.fieldnames or []), list(reader)


def append_csv_row(raw: bytes, headers: list[str], row: dict[str, str]) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    buffer = io.StringIO(newline="")
    csv.writer(buffer, lineterminator=newline).writerow([row.get(key, "") for key in headers])
    prefix = b"" if raw.endswith((b"\n", b"\r")) else newline.encode("ascii")
    return raw + prefix + buffer.getvalue().encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply reviewed S2 classifications and endpoint corrections")
    args = parser.parse_args()

    raw_statements = STATEMENTS.read_bytes()
    raw_candidates, candidate_headers, candidate_rows = read_csv(CANDIDATES)
    raw_mentions, mention_headers, mention_rows = read_csv(MENTIONS)
    actual_hashes = {
        STATEMENTS.name: hashlib.sha256(raw_statements).hexdigest(),
        CANDIDATES.name: hashlib.sha256(raw_candidates).hexdigest(),
        MENTIONS.name: hashlib.sha256(raw_mentions).hexdigest(),
    }
    require(actual_hashes == EXPECTED_HASHES, f"table hashes changed since review: {actual_hashes}")
    for backup in BACKUPS.values():
        require(not backup.exists(), f"recovery backup already exists: {backup.name}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for line_no, phrase in {
        43: "Artistically Bernini’s highly imaginative baldacchino",
        44: "a form much admired by Raphael",
        45: "the twisted column was supposed to derive from Solomon’s Temple",
        46: "Urban VIII probably played a direct part",
        47: "The Barberini bees crawl up the columns",
        48: "alterations were nominally controlled by a permanent committee",
        49: "under the chairmanship of Cardinal Ginnasi",
        50: "the committee decided to build spécial altars",
    }.items():
        require(line_no <= len(source_lines) and phrase in source_lines[line_no - 1],
                f"source line {line_no} changed: {phrase!r}")

    bom = raw_statements.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw_statements else b"\n"
    rows = [json.loads(line.decode("utf-8-sig")) for line in raw_statements.splitlines() if line.strip()]
    require(len({row["statement_id"] for row in rows}) == len(rows), "duplicate statement_id")
    by_id = {row["statement_id"]: row for row in rows}
    require(set(OLD_ENDPOINTS) <= set(by_id), "one or more expected statements are absent")
    pending = {
        row["statement_id"] for row in rows
        if row.get("segment_id") == SEGMENT
        and row.get("subject_candidate_id") and row.get("object_candidate_id")
        and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    require(pending == set(TRUE_NOTES), f"pending bilateral statement set changed: {sorted(pending ^ set(TRUE_NOTES))}")
    require(set(TRUE_NOTES) == set(OLD_ENDPOINTS), "classification and endpoint review sets differ")

    candidates_by_id = {row["candidate_id"]: row for row in candidate_rows}
    for new_candidate in NEW_CANDIDATES:
        require(new_candidate["candidate_id"] not in candidates_by_id, f"candidate ID exists: {new_candidate['candidate_id']}")
    require(max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows) == 11584,
            "candidate ID sequence changed")
    require("candidate_id" in candidate_headers, "candidate table schema changed")
    mentions_by_id = {row["mention_id"]: row for row in mention_rows}
    require(set(MENTION_RETARGETS) <= set(mentions_by_id), "one or more mentions to retarget are absent")
    require("mention_id" in mention_headers, "mention table schema changed")
    expected_mentions = {
        "m-chp2-secii-l42-50-0019": ("the twisted column", "1074", "1092"),
        "m-chp2-secii-l42-50-0022": ("one of them", "1164", "1175"),
        "m-chp2-secii-l42-50-0026": ("the twisted column", "1254", "1272"),
    }
    for mention_id, expected in expected_mentions.items():
        row = mentions_by_id[mention_id]
        require((row["surface_form"], row["start_char"], row["end_char"]) == expected,
                f"mention anchor changed: {mention_id}")
        require(row["candidate_id"] == "cand-4394", f"mention mapping changed: {mention_id}")

    for statement_id, old_endpoints in OLD_ENDPOINTS.items():
        row = by_id[statement_id]
        require(row.get("segment_id") == SEGMENT, f"{statement_id} is outside the reviewed segment")
        require((row.get("subject_candidate_id"), row.get("object_candidate_id")) == old_endpoints,
                f"{statement_id} endpoints changed")
        q = row.get("qualifiers") or {}
        require(q.get("relation_candidate") is None, f"{statement_id} is already classified")
        start_line, end_line = q.get("source_line_start"), q.get("source_line_end")
        require(isinstance(start_line, int) and isinstance(end_line, int) and 42 <= start_line <= end_line <= 50,
                f"{statement_id} has an invalid source anchor")
        anchor = "\n".join(source_lines[start_line - 1:end_line])
        require(row.get("original_quote") in anchor, f"{statement_id} quote no longer matches source")
        row["subject_candidate_id"], row["object_candidate_id"] = FINAL_ENDPOINTS[statement_id]
        q = dict(q)
        q["relation_candidate"] = True
        q["relation_candidate_note"] = TRUE_NOTES[statement_id]
        row["qualifiers"] = q

    for row in mention_rows:
        target = MENTION_RETARGETS.get(row["mention_id"])
        if target:
            require(row["candidate_id"] == target[0], f"mention mapping changed: {row['mention_id']}")
            row["candidate_id"] = target[1]

    candidate_payload = raw_candidates
    for new_candidate in NEW_CANDIDATES:
        candidate_payload = append_csv_row(candidate_payload, candidate_headers, new_candidate)
    mention_payload = raw_mentions
    # Rewrite the CSV so only the three reviewed candidate mappings change.
    mention_newline = "\r\n" if b"\r\n" in raw_mentions else "\n"
    mention_buffer = io.StringIO(newline="")
    mention_writer = csv.DictWriter(mention_buffer, fieldnames=mention_headers, lineterminator=mention_newline)
    mention_writer.writeheader()
    mention_writer.writerows(mention_rows)
    mention_bom = b"\xef\xbb\xbf" if raw_mentions.startswith(b"\xef\xbb\xbf") else b""
    mention_payload = mention_bom + mention_buffer.getvalue().encode("utf-8")

    statement_output = []
    for index, row in enumerate(rows):
        encoded = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            encoded = b"\xef\xbb\xbf" + encoded
        statement_output.append(encoded + newline)
    statement_payload = b"".join(statement_output)

    true_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                         and (row.get("qualifiers") or {}).get("relation_candidate") is True)
    false_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                          and (row.get("qualifiers") or {}).get("relation_candidate") is False)
    pending_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                            and (row.get("qualifiers") or {}).get("relation_candidate") is None)
    require((true_bilateral, false_bilateral, pending_bilateral) == (4032, 451, 4014),
            f"unexpected projected bilateral counts: {(true_bilateral, false_bilateral, pending_bilateral)}")

    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "classified_true": list(TRUE_NOTES),
        "classified_false": [],
        "endpoint_corrections": {
            statement_id: [OLD_ENDPOINTS[statement_id], FINAL_ENDPOINTS[statement_id]]
            for statement_id in OLD_ENDPOINTS if OLD_ENDPOINTS[statement_id] != FINAL_ENDPOINTS[statement_id]
        },
        "new_candidates": [row["candidate_id"] for row in NEW_CANDIDATES],
        "retargeted_mentions": {key: value[1] for key, value in MENTION_RETARGETS.items()},
        "after_bilateral": {"relation_true": true_bilateral, "relation_false": false_bilateral,
                            "unclassified": pending_bilateral},
        "payload_sha256": {
            STATEMENTS.name: hashlib.sha256(statement_payload).hexdigest(),
            CANDIDATES.name: hashlib.sha256(candidate_payload).hexdigest(),
            MENTIONS.name: hashlib.sha256(mention_payload).hexdigest(),
        },
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write.")
        return

    payloads = {STATEMENTS: statement_payload, CANDIDATES: candidate_payload, MENTIONS: mention_payload}
    created_backups: list[Path] = []
    temps: list[Path] = []
    try:
        for path, backup in BACKUPS.items():
            shutil.copy2(path, backup)
            created_backups.append(backup)
        for path, payload in payloads.items():
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                handle.write(payload)
                temps.append(Path(handle.name))
        for temp, path in zip(temps, payloads):
            os.replace(temp, path)

        written = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        written_by_id = {row["statement_id"]: row for row in written}
        require(all((written_by_id[key].get("qualifiers") or {}).get("relation_candidate") is True for key in TRUE_NOTES),
                "one or more classifications were not persisted")
        require(all((written_by_id[key].get("subject_candidate_id"), written_by_id[key].get("object_candidate_id")) == FINAL_ENDPOINTS[key]
                    for key in FINAL_ENDPOINTS), "one or more endpoint corrections were not persisted")
        with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
            persisted_candidates = {row["candidate_id"] for row in csv.DictReader(handle)}
        with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
            persisted_mentions = {row["mention_id"]: row for row in csv.DictReader(handle)}
        require(all(row["candidate_id"] in persisted_candidates for row in NEW_CANDIDATES),
                "new candidates were not persisted")
        require(all(persisted_mentions[key]["candidate_id"] == value[1] for key, value in MENTION_RETARGETS.items()),
                "mention retargeting was not persisted")
    except Exception:
        for temp in temps:
            if temp.exists():
                temp.unlink()
        for path, backup in BACKUPS.items():
            if backup in created_backups:
                shutil.copy2(backup, path)
        raise

    print(json.dumps({
        "result": "applied",
        "statement_count": len(written),
        "candidate_count": len(persisted_candidates),
        "mention_count": len(persisted_mentions),
        "sha256_after": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in payloads},
        "backups": [backup.name for backup in created_backups],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
