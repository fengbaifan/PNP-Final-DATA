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
SEGMENT = "chp-2:02_CHP-2_sec_ii:l30-40"
EXPECTED_HASHES = {
    STATEMENTS.name: "c0225e1438119a5321de4f7f0a8cd29dced58e710a83e9aa02b23b2322642dbc",
    CANDIDATES.name: "1a27c9033338194ff974db22bc9ceef63d15e8361ea47b770563d3ef9033f9f1",
    MENTIONS.name: "a2b203b54cb0ab0dc24e9c83367182748286d6366f224f1fca708feb0578944c",
}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp2-sec-ii-l30-40-20261010"),
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + ".bak-s2-chp2-sec-ii-l30-40-20261010"),
    MENTIONS: MENTIONS.with_name(MENTIONS.name + ".bak-s2-chp2-sec-ii-l30-40-20261010"),
}
NEW_CANDIDATE = {
    "candidate_id": "cand-11584",
    "index_entry_id": "",
    "canonical_name": "Unnamed group of early Christian tombs threatened by the baldacchino foundations",
    "index_page_range": "",
    "suggested_type": "",
    "status": "open",
    "index_source_file": "",
    "sub_entry": "",
    "detail": (
        "Haskell identifies plural early Christian tombs at risk of irrevocable disturbance from the "
        "baldacchino foundations. No individual tombs, locations, number, or membership are supplied. "
        "This source-defined open group is distinct from the separately mentioned supposed tomb of St Peter."
    ),
    "exclude_reason": "",
    "candidate_origin": "body-mention",
    "candidate_source_ref": SEGMENT + "#L39",
}
NEW_MENTION = {
    "mention_id": "m-chp2-secii-l30-40-0043",
    "segment_id": SEGMENT,
    "candidate_id": "cand-11584",
    "surface_form": "early Christian tombs",
    "start_char": "2583",
    "end_char": "2604",
    "note": "原文指面临巴尔达基诺地基扰动风险的未具名早期基督教墓葬群；与前文“supposed tomb of St Peter”区分。",
}
TRUE_NOTES = {
    "st-chp2-sec-ii-l30-40-appeal-attributed-to-origin":
        "Haskell's 'Part ... must certainly be attributed to this' links Bernini's appeal to Urban VIII with the Florentine origin emphasized in the preceding sentence. Preserve this as the author's causal interpretation, not an independently established motive.",
    "st-chp2-sec-ii-l30-40-archaeological-investigation":
        "Haskell says archaeological investigation and artist records addressed the risk of foundations disturbing early Christian tombs. This unnamed tomb group is distinct from the 'supposed tomb of St Peter' mentioned earlier.",
    "st-chp2-sec-ii-l30-40-baldacchino-obstacles":
        "Haskell explicitly identifies two project obstacles, including the danger to early Christian tombs; the bronze shortage and its Pantheon source are separately captured in the adjacent statement. Do not conflate this tomb group with the supposed tomb of St Peter.",
    "st-chp2-sec-ii-l30-40-barberini-style-and-bernini":
        "Haskell attributes the Barberini style's grandeur, triumph, and persuasion largely to Bernini, identified by the immediate context. Retain 'largely' and the author's interpretive framing.",
    "st-chp2-sec-ii-l30-40-bernini-birthplace-and-mother":
        "Haskell reports through the hostile Passeri source that Bernini was born in Naples to a Neapolitan mother. The mother remains unnamed, and the report is not independently verified here.",
    "st-chp2-sec-ii-l30-40-bernini-father-origin":
        "Haskell reports through Passeri that Bernini's unnamed father was Florentine and that Bernini emphasized this origin. Florence is the father's reported origin, not Bernini's birthplace; retain the hostile-source qualification.",
    "st-chp2-sec-ii-l30-40-bronze-from-pantheon":
        "Haskell links the baldacchino columns' bronze shortage to despoiling the Pantheon. The source gives no quantity or exact components removed.",
    "st-chp2-sec-ii-l30-40-maderno-facade":
        "The source attributes erection of St Peter's façade to Carlo Maderno by 1612; this records Haskell's account and does not independently verify construction responsibility.",
    "st-chp2-sec-ii-l30-40-observers-on-facade-inscription":
        "Haskell reports unnamed malicious observers' criticism that Paul V's name received greater prominence than St Peter's. This is reported criticism, not verified evidence of the builders' intention.",
    "st-chp2-sec-ii-l30-40-passeri-bolognese-and-urban":
        "This preserves Passeri's retrospective quotation, transmitted by Haskell, about Urban VIII's Florentine identity and the Bolognese artists. It does not independently establish a general artistic shift.",
    "st-chp2-sec-ii-l30-40-uncertain-overall-plan":
        "Haskell explicitly says it is 'unlikely' that Urban VIII began with an overall plan for the area. Retain that uncertainty and do not convert it into a definite negative fact.",
    "st-chp2-sec-ii-l30-40-urban-and-st-peters-consecration":
        "Haskell reports Urban VIII's attention to St Peter's and says he was able to consecrate it in 1626; preserve the source's wording and date.",
    "st-chp2-sec-ii-l30-40-urban-favored-tuscan-artists":
        "Haskell says Urban repeatedly sought to give the best jobs to Tuscan artists, especially early in his pontificate. No specific appointment or artist is inferred.",
    "st-chp2-sec-ii-l30-40-urban-interior-patronage-and-decoration":
        "Haskell says Urban selected the central area under Michelangelo's dome for special patronage and that Urban and Bernini established its main decoration. Preserve the author's account and the area-specific scope.",
    "st-chp2-sec-ii-l30-40-urban-reported-praise":
        "This records Urban VIII's reported praise of Bernini, while retaining the text's hearsay wording and the later note that the exact words may be apocryphal.",
}
EXPECTED_ENDPOINTS = {
    "st-chp2-sec-ii-l30-40-appeal-attributed-to-origin": ("cand-3046", "cand-3104"),
    "st-chp2-sec-ii-l30-40-archaeological-investigation": ("cand-4234", "cand-11584"),
    "st-chp2-sec-ii-l30-40-baldacchino-obstacles": ("cand-4234", "cand-11584"),
    "st-chp2-sec-ii-l30-40-barberini-style-and-bernini": ("cand-3046", "cand-4228"),
    "st-chp2-sec-ii-l30-40-bernini-baldacchino-start": ("cand-3046", "cand-4234"),
    "st-chp2-sec-ii-l30-40-bernini-birthplace-and-mother": ("cand-3046", "cand-3534"),
    "st-chp2-sec-ii-l30-40-bernini-father-origin": ("cand-3046", "cand-3397"),
    "st-chp2-sec-ii-l30-40-bronze-from-pantheon": ("cand-4234", "cand-4236"),
    "st-chp2-sec-ii-l30-40-maderno-facade": ("cand-4232", "cand-1478"),
    "st-chp2-sec-ii-l30-40-observers-on-facade-inscription": ("cand-4232", "cand-3092"),
    "st-chp2-sec-ii-l30-40-passeri-bolognese-and-urban": ("cand-3104", "cand-4229"),
    "st-chp2-sec-ii-l30-40-uncertain-overall-plan": ("cand-3104", "cand-3135"),
    "st-chp2-sec-ii-l30-40-urban-and-st-peters-consecration": ("cand-3104", "cand-3135"),
    "st-chp2-sec-ii-l30-40-urban-favored-tuscan-artists": ("cand-3104", "cand-4230"),
    "st-chp2-sec-ii-l30-40-urban-interior-patronage-and-decoration": ("cand-3104", "cand-3046"),
    "st-chp2-sec-ii-l30-40-urban-reported-praise": ("cand-3104", "cand-3046"),
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
    parser.add_argument("--apply", action="store_true", help="apply the reviewed classifications and endpoint correction")
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
    require(len(source_lines) >= 40, "source segment lines are missing")
    source_text = "\n".join(source_lines[29:40])
    phrase = NEW_MENTION["surface_form"]
    start = source_text.index(phrase)
    require((start, start + len(phrase)) == (2583, 2604), "reviewed source mention span changed")
    for line_no, phrases in {
        31: ("The achievement of grandeur",),
        32: ("As Urban VIII was a Florentine", "Gian Lorenzo"),
        33: ("Part of the immense appeal", "quality of Bernini’s work"),
        34: ("first official post",),
        35: ("main attention was centred on St Peter’s",),
        36: ("Carlo Maderno by 1612",),
        38: ("unlikely that Urban had started with an overall plan",),
        39: ("danger that early Christian tombs", "despoiling of the Pantheon"),
        40: ("After nine years",),
    }.items():
        for phrase_check in phrases:
            require(phrase_check in source_lines[line_no - 1], f"source line {line_no} changed: {phrase_check!r}")

    bom = raw_statements.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw_statements else b"\n"
    rows = [json.loads(line.decode("utf-8-sig")) for line in raw_statements.splitlines() if line.strip()]
    require(len({row["statement_id"] for row in rows}) == len(rows), "duplicate statement_id")
    by_id = {row["statement_id"]: row for row in rows}
    require(set(EXPECTED_ENDPOINTS) <= set(by_id), "one or more expected statements are absent")
    pending = {
        row["statement_id"] for row in rows
        if row.get("segment_id") == SEGMENT
        and row.get("subject_candidate_id") and row.get("object_candidate_id")
        and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    require(pending == set(TRUE_NOTES), f"pending bilateral statement set changed: {sorted(pending ^ set(TRUE_NOTES))}")

    candidates_by_id = {row["candidate_id"]: row for row in candidate_rows}
    require("cand-11584" not in candidates_by_id, "new candidate ID already exists")
    require("candidate_id" in candidate_headers, "candidate table schema changed")
    mentions_by_id = {row["mention_id"]: row for row in mention_rows}
    require(NEW_MENTION["mention_id"] not in mentions_by_id, "new mention ID already exists")
    require("mention_id" in mention_headers, "mention table schema changed")
    require(NEW_MENTION["start_char"] == str(start), "mention start offset changed")
    require(source_text[start:start + len(phrase)] == phrase, "mention surface form does not match source")

    for statement_id, endpoints in EXPECTED_ENDPOINTS.items():
        row = by_id[statement_id]
        require(row.get("segment_id") == SEGMENT, f"{statement_id} is outside the reviewed segment")
        if statement_id in TRUE_NOTES:
            q = row.get("qualifiers") or {}
            require(q.get("relation_candidate") is None, f"{statement_id} is already classified")
            start_line, end_line = q.get("source_line_start"), q.get("source_line_end")
            require(isinstance(start_line, int) and isinstance(end_line, int) and 30 <= start_line <= end_line <= 40,
                    f"{statement_id} has an invalid source anchor")
            anchor = "\n".join(source_lines[start_line - 1:end_line])
            require(row.get("original_quote") in anchor, f"{statement_id} quote no longer matches source")
        else:
            require((row.get("qualifiers") or {}).get("relation_candidate") is True,
                    f"previously classified statement changed: {statement_id}")
        if statement_id in ("st-chp2-sec-ii-l30-40-archaeological-investigation",
                            "st-chp2-sec-ii-l30-40-baldacchino-obstacles"):
            require((row.get("subject_candidate_id"), row.get("object_candidate_id")) == ("cand-4234", "cand-4235"),
                    f"expected tomb endpoint correction changed for {statement_id}")
            row["object_candidate_id"] = "cand-11584"
        else:
            require((row.get("subject_candidate_id"), row.get("object_candidate_id")) == endpoints,
                    f"{statement_id} endpoints changed")
        if statement_id in TRUE_NOTES:
            q = dict(row.get("qualifiers") or {})
            q["relation_candidate"] = True
            q["relation_candidate_note"] = TRUE_NOTES[statement_id]
            row["qualifiers"] = q

    for statement_id, endpoints in EXPECTED_ENDPOINTS.items():
        row = by_id[statement_id]
        require((row.get("subject_candidate_id"), row.get("object_candidate_id")) == endpoints,
                f"post-review endpoint mismatch for {statement_id}")

    candidate_payload = append_csv_row(raw_candidates, candidate_headers, NEW_CANDIDATE)
    mention_payload = append_csv_row(raw_mentions, mention_headers, NEW_MENTION)
    output_lines = []
    for index, row in enumerate(rows):
        encoded = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            encoded = b"\xef\xbb\xbf" + encoded
        output_lines.append(encoded + newline)
    statement_payload = b"".join(output_lines)

    true_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                         and (row.get("qualifiers") or {}).get("relation_candidate") is True)
    false_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                          and (row.get("qualifiers") or {}).get("relation_candidate") is False)
    pending_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                            and (row.get("qualifiers") or {}).get("relation_candidate") is None)
    require((true_bilateral, false_bilateral, pending_bilateral) == (4011, 451, 4035),
            f"unexpected projected bilateral counts: {(true_bilateral, false_bilateral, pending_bilateral)}")
    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "classified_true": list(TRUE_NOTES),
        "classified_false": [],
        "endpoint_corrections": {
            "st-chp2-sec-ii-l30-40-archaeological-investigation": ["cand-4235", "cand-11584"],
            "st-chp2-sec-ii-l30-40-baldacchino-obstacles": ["cand-4235", "cand-11584"],
        },
        "new_candidate": NEW_CANDIDATE["candidate_id"],
        "new_mention": NEW_MENTION["mention_id"],
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
        require(all(written_by_id[key].get("object_candidate_id") == "cand-11584"
                    for key in ("st-chp2-sec-ii-l30-40-archaeological-investigation",
                                "st-chp2-sec-ii-l30-40-baldacchino-obstacles")),
                "corrected tomb endpoints were not persisted")
        with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
            written_candidates = {row["candidate_id"] for row in csv.DictReader(handle)}
        with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
            written_mentions = {row["mention_id"] for row in csv.DictReader(handle)}
        require("cand-11584" in written_candidates and NEW_MENTION["mention_id"] in written_mentions,
                "new candidate/mention rows were not persisted")
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
        "candidate_count": len(written_candidates),
        "mention_count": len(written_mentions),
        "sha256_after": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in payloads},
        "backups": [backup.name for backup in created_backups],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
