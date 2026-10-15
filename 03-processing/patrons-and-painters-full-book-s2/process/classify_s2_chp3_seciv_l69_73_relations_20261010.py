from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE_DIR = ROOT / "04-knowledge/tables"
STATEMENTS = TABLE_DIR / "book-statements.jsonl"
CANDIDATES = TABLE_DIR / "entity-candidates.csv"
MENTIONS = TABLE_DIR / "mentions.csv"
COVERAGE = TABLE_DIR / "s2-coverage.csv"
SEGMENTS = TABLE_DIR / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
PDF = ROOT / "02-sources/01-book/CHP-3.pdf"
PAGE83 = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/.tmp_chp3_p83_phys25_20261010.png"

BODY_SEGMENT = "chp-3:03_CHP-3_sec_iv:l69-73"
NOTE_SEGMENT = "chp-3:03_CHP-3_sec_iv:l189-243"
BODY_IDS = {
    "st-chp3-seciv-l69-73-central-iconographic-groups",
    "st-chp3-seciv-l69-73-cortona-inspiration",
    "st-chp3-seciv-l69-73-cosmic-colour-drama",
    "st-chp3-seciv-l69-73-gaulli-four-figures-in-pendentives",
    "st-chp3-seciv-l69-73-ihs-radiance",
    "st-chp3-seciv-l69-73-light-strikes-damned-and-heretics",
    "st-chp3-seciv-l69-73-matter-spirit-and-missionary-emphasis",
    "st-chp3-seciv-l69-73-missionary-self-conception",
    "st-chp3-seciv-l69-73-nave-fresco-prominent",
    "st-chp3-seciv-l69-73-oliva-added-judges",
    "st-chp3-seciv-l69-73-prelude-to-tribune",
    "st-chp3-seciv-l69-73-regional-missionary-presence",
    "st-chp3-seciv-l69-73-roman-pendentive-custom",
    "st-chp3-seciv-l69-73-sixteen-stucco-figures",
    "st-chp3-seciv-l69-73-theme-urgency-molinos",
    "st-chp3-seciv-l69-73-vault-public-access-simpler-symbolism",
}

RELATION_NOTES = {
    "st-chp3-seciv-l69-73-central-iconographic-groups": "The fresco depicts several named iconographic groups and personifications; the Three Kings is the primary object endpoint, with the other cited figures retained in qualifiers.",
    "st-chp3-seciv-l69-73-cortona-inspiration": "Haskell explicitly attributes Gaulli's stylistic inspiration to Pietro da Cortona's Barberini ceiling; this remains Haskell's influence claim.",
    "st-chp3-seciv-l69-73-gaulli-four-figures-in-pendentives": "Haskell attributes the design solution for four figures in each pendentive to Gaulli; retain the group-level figure endpoint.",
    "st-chp3-seciv-l69-73-ihs-radiance": "The description explicitly makes the IHS emblem the source of light in the fresco's composition.",
    "st-chp3-seciv-l69-73-light-strikes-damned-and-heretics": "Haskell describes the light acting on two iconographic groups; the stated implication of movement into the church remains qualified.",
    "st-chp3-seciv-l69-73-matter-spirit-and-missionary-emphasis": "The stucco figures are explicitly said to emphasize Jesuit missionary power; the sentence's matter/spirit function remains part of Haskell's account.",
    "st-chp3-seciv-l69-73-missionary-self-conception": "Haskell says the Jesuits used the visual programme to display their missionary self-conception; the cited Bartoli reference is only a locator and was not independently consulted.",
    "st-chp3-seciv-l69-73-nave-fresco-prominent": "This is an explicit work-to-building description by Haskell, not a claim of independent evaluation.",
    "st-chp3-seciv-l69-73-oliva-added-judges": "Haskell explicitly attributes the decision to add the previously unrepresented Judges to Oliva; no wider historical priority is inferred.",
    "st-chp3-seciv-l69-73-prelude-to-tribune": "Haskell describes the original programme relationship between the nave fresco and the intended tribune climax; it does not state their final relative importance.",
    "st-chp3-seciv-l69-73-regional-missionary-presence": "Haskell says the figures represent regions where Jesuit disciples had a presence; the sentence does not map individual figures to particular regions.",
    "st-chp3-seciv-l69-73-sixteen-stucco-figures": "Haskell distinguishes Gaulli's design of the figures from their execution and placement by his followers.",
    "st-chp3-seciv-l69-73-theme-urgency-molinos": "Haskell links the growing controversy around Molinos's heresies to increased urgency of the missionary theme; retain his framing.",
    "st-chp3-seciv-l69-73-vault-public-access-simpler-symbolism": "Haskell explicitly links the vault's greater public accessibility than the dome to the simpler symbolism used for the message.",
}

NONRELATION_NOTES = {
    "st-chp3-seciv-l69-73-cosmic-colour-drama": "This is Haskell's scalar aesthetic description of the fresco's colour contrast and dramatic effect, with no second entity endpoint.",
    "st-chp3-seciv-l69-73-roman-pendentive-custom": "This is Haskell's general statement about customary Roman church decoration; the passage does not identify a particular church or a bounded relation instance.",
}

EXPECTED_HASHES = {
    STATEMENTS: "5c10eb9121824eba409a537321a603617e71049d8d12b54ad9f7e59d76735bd6",
    CANDIDATES: "ca85aa43d331b781ba67b855fcda8685763f202bc47f4976680014432655c3f5",
    MENTIONS: "47be7931df51220a6d7c6eac93c0f0607ebc05f829bbbcea2f91f3b3d42f7e61",
    COVERAGE: "e9c4b793d40f00d6d5cb0952413aae2e7c55787a5a820bfe9dcc27e9159b66cc",
    SOURCE: "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
    PAGE83: "49e3807be9c637004fc90ad94a3e4efac31759cd2be0f53b0ba87af955fc2c2f",
}
BACKUP = STATEMENTS.with_name(
    STATEMENTS.name + ".bak-s2-chp3-sec-iv-l69-73-relations-20261010"
)

FOOTNOTE_BODY_UPDATES = {
    "st-chp3-seciv-l69-73-missionary-self-conception": (
        "Footnote 1 is linked to note L205; the cited Bartoli frontispiece is recorded as a locator only and was not independently consulted. "
        "This remains Haskell's reading of the visual programme."
    ),
    "st-chp3-seciv-l69-73-central-iconographic-groups": (
        "Footnote 2 is linked to note L206; the Lanckoronska citation is recorded as a locator only and was not independently consulted. "
        "The Church remains an untyped personification."
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(rows: list[dict]) -> bytes:
    return "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows).encode("utf-8")


def by_id(rows: list[dict], key: str, value: str) -> dict:
    found = [row for row in rows if row.get(key) == value]
    if len(found) != 1:
        raise ValueError(f"expected one {key}={value}, found {len(found)}")
    return found[0]


def source_segment(segment_id: str) -> tuple[dict, str]:
    segment = by_id(read_jsonl(SEGMENTS), "segment_id", segment_id)
    source_path = ROOT / segment["source_file"]
    source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != segment["sha256"]:
        raise ValueError(f"S0 segment text hash mismatch: {segment_id}")
    return segment, text


def preflight() -> None:
    for path, expected in EXPECTED_HASHES.items():
        actual = digest(path)
        if actual != expected:
            raise ValueError(f"preflight hash mismatch for {path.relative_to(ROOT)}: {actual}")
    if BACKUP.exists() and digest(BACKUP) != EXPECTED_HASHES[STATEMENTS]:
        raise ValueError(f"existing recovery copy differs from the expected prewrite file: {BACKUP.name}")

    _, body = source_segment(BODY_SEGMENT)
    _, notes = source_segment(NOTE_SEGMENT)
    for exact in (
        "It was usual in Roman churches",
        "Pietro da Cortona’s daring and revolutionary ceiling",
        "Everything radiates from the golden circle of light",
        "the overwhelming power of the Jesuit missionaries",
        "the like1 :",
        "emotionaTcontact",
    ):
        if exact not in body:
            raise ValueError(f"unexpected OCR/source segment text; missing {exact!r}")
    if "Damello Bartoli: De//a vita e dell istituto" not in notes or "2 Lanckoronska." not in notes:
        raise ValueError("expected p.83 footnote OCR strings changed")
    if body.count("[Page 83]") != 1 or "p83" not in PAGE83.name:
        raise ValueError("unexpected source page boundary")

    coverage = read_jsonl(COVERAGE) if COVERAGE.suffix == ".jsonl" else None
    if coverage is not None:
        raise ValueError("coverage file unexpectedly changed format")
    import csv
    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    row = by_id(rows, "segment_id", BODY_SEGMENT)
    if row.get("disposition") != "reviewed" or row.get("migration_status") != "complete":
        raise ValueError("body segment coverage is not reviewed/complete")

    _, body_text = source_segment(BODY_SEGMENT)
    mentions = [r for r in csv.DictReader(MENTIONS.open(encoding="utf-8-sig", newline="")) if r.get("segment_id") == BODY_SEGMENT]
    if len(mentions) != 47:
        raise ValueError(f"expected 47 existing body mentions, found {len(mentions)}")
    for mention in mentions:
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if body_text[start:end] != mention["surface_form"]:
            raise ValueError(f"mention span mismatch: {mention['mention_id']}")


def build_changes() -> tuple[bytes, list[dict], list[dict]]:
    statements = read_jsonl(STATEMENTS)
    original = copy.deepcopy(statements)
    if len({r["statement_id"] for r in statements}) != len(statements):
        raise ValueError("duplicate statement IDs before write")
    segment_rows = [r for r in statements if r.get("segment_id") == BODY_SEGMENT]
    if len(segment_rows) != 16 or {r["statement_id"] for r in segment_rows} != BODY_IDS:
        raise ValueError(f"unexpected statement inventory for body segment: {len(segment_rows)}")

    for statement_id, note in RELATION_NOTES.items():
        row = by_id(statements, "statement_id", statement_id)
        qualifiers = row.setdefault("qualifiers", {})
        if qualifiers.get("relation_candidate") is not None:
            raise ValueError(f"{statement_id} already classified")
        qualifiers["relation_candidate"] = True
        qualifiers["relation_candidate_note"] = note
    for statement_id, note in NONRELATION_NOTES.items():
        row = by_id(statements, "statement_id", statement_id)
        qualifiers = row.setdefault("qualifiers", {})
        if qualifiers.get("relation_candidate") is not None:
            raise ValueError(f"{statement_id} already classified")
        qualifiers["relation_candidate"] = False
        qualifiers["relation_candidate_note"] = note

    for statement_id, qualification in FOOTNOTE_BODY_UPDATES.items():
        row = by_id(statements, "statement_id", statement_id)
        qualifiers = row["qualifiers"]
        if qualifiers.get("footnote_pending") not in (None, False):
            raise ValueError(f"footnote status unexpectedly pending for {statement_id}")
        old = qualifiers.get("qualification", "")
        if "pending" not in old.lower():
            raise ValueError(f"expected stale pending qualification for {statement_id}")
        qualifiers["qualification"] = qualification
        qualifiers["footnote_pending"] = False

    return write_jsonl(statements), original, statements


def validate(rows: list[dict]) -> dict:
    if len(rows) != 12791:
        raise ValueError(f"statement count differs: {len(rows)}")
    body = [r for r in rows if r.get("segment_id") == BODY_SEGMENT]
    true_ids = {r["statement_id"] for r in body if r.get("qualifiers", {}).get("relation_candidate") is True}
    false_ids = {r["statement_id"] for r in body if r.get("qualifiers", {}).get("relation_candidate") is False}
    if true_ids != set(RELATION_NOTES) or false_ids != set(NONRELATION_NOTES):
        raise ValueError(f"body classification mismatch: true={true_ids}, false={false_ids}")
    for statement_id, qualification in FOOTNOTE_BODY_UPDATES.items():
        q = by_id(rows, "statement_id", statement_id)["qualifiers"]
        if q.get("qualification") != qualification or q.get("footnote_pending") is not False:
            raise ValueError(f"linked footnote qualification did not update: {statement_id}")

    bilateral = [r for r in rows if r.get("subject_candidate_id") and r.get("object_candidate_id")]
    relation_candidates = [r for r in rows if r.get("qualifiers", {}).get("relation_candidate") is True]
    open_relations = [r for r in relation_candidates if not r.get("subject_candidate_id") or not r.get("object_candidate_id")]
    bilateral_true = sum(r.get("qualifiers", {}).get("relation_candidate") is True for r in bilateral)
    bilateral_false = sum(r.get("qualifiers", {}).get("relation_candidate") is False for r in bilateral)
    bilateral_unclassified = sum(r.get("qualifiers", {}).get("relation_candidate") is None for r in bilateral)
    summary = {
        "statements": len(rows),
        "bilateral": len(bilateral),
        "bilateral_relation_candidates": bilateral_true,
        "bilateral_nonrelations": bilateral_false,
        "bilateral_unclassified": bilateral_unclassified,
        "relation_candidates": len(relation_candidates),
        "open_relation_candidates": len(open_relations),
        "body_relation_candidates": len(true_ids),
        "body_nonrelations": len(false_ids),
    }
    expected = {
        "statements": 12791,
        "bilateral": 8586,
        "bilateral_relation_candidates": 4970,
        "bilateral_nonrelations": 479,
        "bilateral_unclassified": 3137,
        "relation_candidates": 5022,
        "open_relation_candidates": 52,
        "body_relation_candidates": 14,
        "body_nonrelations": 2,
    }
    if summary != expected:
        raise ValueError(f"global postwrite counts differ: {summary!r}")
    return summary


def show_preview(before: list[dict], after: list[dict], summary: dict) -> None:
    print("DRY-RUN: no table files written")
    print("summary:", json.dumps(summary, ensure_ascii=False, sort_keys=True))
    print("relation candidates:", ", ".join(sorted(RELATION_NOTES)))
    print("nonrelations:", ", ".join(sorted(NONRELATION_NOTES)))
    print("corrected linked-footnote qualification:", ", ".join(sorted(FOOTNOTE_BODY_UPDATES)))
    old = {r["statement_id"]: r for r in before}
    new = {r["statement_id"]: r for r in after}
    changed = sorted(key for key in BODY_IDS | set(FOOTNOTE_BODY_UPDATES) if old[key] != new[key])
    print("changed statements:", len(changed), changed)


def apply_changes(data: bytes, expected_summary: dict) -> None:
    if digest(STATEMENTS) != EXPECTED_HASHES[STATEMENTS]:
        raise ValueError("write-time statement hash mismatch")
    if not BACKUP.exists():
        shutil.copy2(STATEMENTS, BACKUP)
    if digest(BACKUP) != EXPECTED_HASHES[STATEMENTS]:
        raise ValueError(f"backup verification failed: {BACKUP.name}")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", prefix=STATEMENTS.name + ".tmp-", dir=STATEMENTS.parent, delete=False) as handle:
            handle.write(data)
            temp_path = Path(handle.name)
        temp_path.replace(STATEMENTS)
        post_hash = digest(STATEMENTS)
        actual = read_jsonl(STATEMENTS)
        actual_summary = validate(actual)
        if actual_summary != expected_summary:
            raise ValueError("postwrite summary differs from dry-run")
        print("APPLY SUCCEEDED")
        print("statements sha256:", post_hash)
        print("recovery copy:", BACKUP.relative_to(ROOT), digest(BACKUP))
        print("postwrite summary:", json.dumps(actual_summary, ensure_ascii=False, sort_keys=True))
    except Exception:
        if BACKUP.exists() and digest(BACKUP) == EXPECTED_HASHES[STATEMENTS]:
            shutil.copy2(BACKUP, STATEMENTS)
        raise
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after source, table, and span preflights")
    args = parser.parse_args()
    preflight()
    data, before, after = build_changes()
    summary = validate(after)
    show_preview(before, after, summary)
    if args.apply:
        apply_changes(data, summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
