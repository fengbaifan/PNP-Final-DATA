from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_i.md"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SEGMENT_ID = "chp-3:03_CHP-3_sec_i:l35-43"
TABLE_SHA256 = "8509d4c990e8d093be1ac2544753c44b22b6fc381e60dfb9191586fe9836d06c"
CANDIDATES_SHA256 = "e55377108d52e28efbd476ee007a87dd4573cb9badedd452083e5958c8854c83"
SOURCE_SHA256 = "a18f48c7b8bf5b161fa13a7ce26ed2935e72d9a14d555f82dfc1d85f84314255"
SEGMENT_SHA256 = "ea302e3edf8ce7923e39f1ff72ffa23af95c6393df8b67fe554a0fac6c0acd7c"
FRIEDLAENDER_ID = "st-chp3-seci-l35-43-friedlaender-citation"
CLARETTA_ID = "st-chp3-seci-l35-43-claretta-citation"
COZZI_ID = "st-chp3-seci-l35-43-cozzi-rejection-citation"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp3-seci-l35-43-citation-endpoints-20261013")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Complete section I footnote citation candidates with their source-linked subject matter.")
    parser.add_argument("--apply", action="store_true", help="write changes after protected preview checks")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    if sha256(raw) != TABLE_SHA256:
        raise SystemExit("protected statements table changed")
    if sha256(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise SystemExit("protected S0 source changed")
    candidates_raw = CANDIDATES.read_bytes()
    if sha256(candidates_raw) != CANDIDATES_SHA256:
        raise SystemExit("protected candidate table changed")
    candidate_rows = csv.DictReader(io.StringIO(candidates_raw.decode("utf-8-sig"), newline=""))
    candidate_ids = {row.get("candidate_id") for row in candidate_rows}
    required_candidates = {"cand-4375", "cand-0544", "cand-4991", "cand-4995", "cand-1027"}
    if not required_candidates.issubset(candidate_ids):
        raise SystemExit("one or more citation endpoints are missing")
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("protected segment metadata changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    if sha256(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("protected source segment changed")
    if "1 Friedlaender, p. 123, and the forceful, but not necessarily decisive, rejection of this opinion by G. Cozzi, 1961, pp. 36 ss." not in segment_text:
        raise SystemExit("protected note 1 wording changed")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    row_map = {row.get("statement_id"): row for row in rows}
    if len(row_map) != len(rows) or COZZI_ID in row_map:
        raise SystemExit("statement IDs changed or Cozzi split already exists")
    if FRIEDLAENDER_ID not in row_map or CLARETTA_ID not in row_map:
        raise SystemExit("one or more citation rows are missing")

    friedlaender = row_map[FRIEDLAENDER_ID]
    if friedlaender.get("qualifiers", {}).get("relation_candidate") is not None or friedlaender.get("object_candidate_id") != "":
        raise SystemExit("Friedlaender citation is no longer in its expected unresolved state")
    friedlaender["object_candidate_id"] = "cand-0544"
    friedlaender["original_quote"] = "1 Friedlaender, p. 123,"
    fq = friedlaender["qualifiers"]
    fq["relation_candidate"] = True
    fq["relation_candidate_note"] = "The note cites Friedlaender, p. 123, in connection with the Caravaggio and Oratorian encouragement suggestion; the publication is not independently consulted. The Cozzi rejection in the same footnote is recorded separately."

    claretta = row_map[CLARETTA_ID]
    if claretta.get("qualifiers", {}).get("relation_candidate") is not None or claretta.get("object_candidate_id") != "":
        raise SystemExit("Claretta citation is no longer in its expected unresolved state")
    claretta["object_candidate_id"] = "cand-1027"
    cq = claretta["qualifiers"]
    cq["relation_candidate"] = True
    cq["relation_candidate_note"] = "The note cites Claretta, 1893, p. 33, in connection with the Duchess of Savoy and Ciro Ferri anecdote; Ferri is the endpoint anchor and the linked statements preserve the broader scope. The cited page was not independently consulted."

    cozzi_quote = "the forceful, but not necessarily decisive, rejection of this opinion by G. Cozzi, 1961, pp. 36 ss."
    cited_line = source_lines[35]
    if cozzi_quote not in cited_line:
        raise SystemExit("Cozzi quotation span is not exact")
    cozzi_row = {
        "statement_id": COZZI_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-4991",
        "object_candidate_id": "cand-0544",
        "predicate": "cited_in_connection_with",
        "qualifiers": {
            "source_line_start": 36,
            "source_line_end": 36,
            "claim": "Haskell says G. Cozzi, 1961, pp. 36 ss., forcefully but not decisively rejected the opinion that the Oratorians may have specially encouraged Caravaggio’s anti-conformist religious painting.",
            "speaker": "Haskell, in a footnote",
            "text_layer": "substantive footnote",
            "qualification": "This preserves Haskell’s characterization of Cozzi’s response; the publication title and edition remain unspecified, and its contents were not independently consulted.",
            "related_statement_ids": ["st-chp3-seci-l16-24-orat-caravaggio"],
            "footnote_marker": "1",
            "footnote_page": 64,
            "relation_candidate": True,
            "relation_candidate_note": "The footnote explicitly reports Cozzi's forceful but not necessarily decisive rejection of the preceding opinion; this records the cited argument without deciding the historical claim.",
        },
        "original_quote": cozzi_quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_i.md",
    }
    rows.append(cozzi_row)

    for statement_id in [FRIEDLAENDER_ID, CLARETTA_ID, COZZI_ID]:
        row = row_map.get(statement_id, cozzi_row if statement_id == COZZI_ID else None)
        q = row["qualifiers"]
        cited = " ".join(" ".join(source_lines[int(q["source_line_start"]) - 1:int(q["source_line_end"])]).split())
        quote = " ".join(row.get("original_quote", "").split())
        if quote not in cited:
            raise SystemExit(f"quote does not match cited source line: {statement_id}")
    rendered = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    if raw.startswith(b"\xef\xbb\xbf"):
        rendered = b"\xef\xbb\xbf" + rendered
    print("Chapter 3 section I L35–43 citation preview")
    print(f"{FRIEDLAENDER_ID}: true endpoints=cand-4375,cand-0544; quote narrowed to the Friedlaender portion of note 1")
    print(f"{COZZI_ID}: true endpoints=cand-4991,cand-0544; split from the same footnote using the existing Cozzi candidate and mention")
    print(f"{CLARETTA_ID}: true endpoints=cand-4995,cand-1027; related statement links preserve the Duchess and Ferri scope")
    print(f"book-statements.jsonl: {sha256(raw)} -> {sha256(rendered)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP.name}")
    shutil.copy2(TABLE, BACKUP)
    tmp = TABLE.with_name(TABLE.name + ".tmp-s2-chp3-seci-l35-43")
    tmp.write_bytes(rendered)
    tmp.replace(TABLE)
    print(f"mode=apply; backup={BACKUP.name}")


if __name__ == "__main__":
    main()
