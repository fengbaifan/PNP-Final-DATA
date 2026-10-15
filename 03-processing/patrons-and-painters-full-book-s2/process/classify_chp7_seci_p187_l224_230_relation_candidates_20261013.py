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
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_i.md"
SEGMENT = "chp-7:07_CHP-7_sec_i:l224-230"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p187-l224-230-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "9eb73cbc9ac99f2353280174eb2f3054fce211f8f0cdd8e258c9797d65b617f7",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p187-i01": "This records Haskell's claim that Fouquet was an enthusiastic collector of Italian art; both refers to Fouquet and Colbert across the page boundary.",
    "st-chp7-p187-i02": "This records Haskell's claim that Colbert was an enthusiastic collector of Italian art; both refers to Fouquet and Colbert across the page boundary.",
    "st-chp7-p187-i03": "This records Haskell's claim that Louis XIV sought Italian painters, sculptors, and architects for employment despite his patriotic ambitions; the group is not exhaustive.",
    "st-chp7-p187-i04": "This records Franceschini being commissioned to paint Fame carrying the King's Name to the Temple of Immortality; the commissioner is not named and the OCR correction is source-qualified.",
    "st-chp7-p187-i05": "This records Ciro Ferri working for Louis XIV in Rome; the note marker is retained for later footnote linkage.",
    "st-chp7-p187-i06": "This records Mola's invitation to Paris and offered stipend, followed by his death before departure; the inviter and amount remain unspecified.",
    "st-chp7-p187-i07": "This records Salvator Rosa refusing an invitation to Paris in 1665; the author's independent-minded characterization is not used as a cause.",
    "st-chp7-p187-i08": "This records Rosa's reported statement that French visitors sought to acquire his work; it remains nested quotation as reported by Haskell.",
    "st-chp7-p187-i09": "This records Haskell's interpretation that the Louvre plans marked the culmination and crisis of French enthusiasm for Italian artists; it does not assert a completed building.",
    "st-chp7-p187-i10": "This records Louis XIV and Colbert considering proposals for the royal palace's eastern front soon after Louis's rule began; both actors are retained.",
    "st-chp7-p187-i11": "This records Haskell's account of Colbert's hostility toward Le Vau and preserves Le Vau's separate prior role as Mazarin's principal architect.",
    "st-chp7-p187-i12": "This records Le Vau having served as Mazarin's principal architect; no term of appointment is inferred.",
    "st-chp7-p187-i13": "This records Colbert's unsuccessful search for French design alternatives and turn toward Italy; the source does not identify who compelled him.",
    "st-chp7-p187-i14": "This records Colbert's proposal to submit Le Vau's plans to some leading Roman architects; proposed submission is not treated as completed review.",
    "st-chp7-p187-i15": "This records Colbert asking Italian architects to send their own drawings; a request does not prove that every invitee submitted a design.",
    "st-chp7-p187-i16": "This records Haskell's report that writers had examined the Louvre episode in detail and his decision to discuss only its outline and significance; the writers and the episode remain unnamed at the entity level.",
    "st-chp7-p187-i17": "This preserves Haskell's causal claim that nationalism grew stronger through Richelieu's and, paradoxically, Mazarin's patriotic policies; the policies are not separately identified.",
    "st-chp7-p187-i18": "This records Haskell's claim that French hostility to Italian art was based on more than racial feeling; more than is preserved as a limit.",
    "st-chp7-p187-i19": "This records the reported criticism that the Italian architects' submitted plans paid no serious attention to French conditions; it is Haskell's report of criticism, not independent review.",
    "st-chp7-p187-i20": "This records the criticism that the submitted plans were too elaborate and Baroque for native taste; the evaluation is attributed to the reported critics.",
    "st-chp7-p187-i21": "This records a reported comparison of Pietro da Cortona's drawing with a temple rather than a palace; the critic and the typological referents remain unspecified.",
    "st-chp7-p187-i22": "This records the reported criticism describing Candiani's designs as extravagant; the critic is unnamed and Candiani remains unidentified.",
    "st-chp7-p187-i23": "This records the reported criticism describing Rainaldi's designs as bizarre and lacking a taste for beautiful, simple architecture; the critic is unnamed.",
    "st-chp7-p187-i24": "This records Haskell's claim that modern opinion endorsed most of the preceding criticisms; the scholars and the exact views endorsed are not itemized.",
    "st-chp7-p187-i25": "This records Haskell's claim that Bernini came nearest to imposing his taste on Paris through the King's personal support but ultimately failed; each qualification is retained.",
    "st-chp7-p187-i26": "This records Bernini's first Louvre plans being rejected; the rejecting actor and the date are not supplied here.",
    "st-chp7-p187-i27": "This records Bernini's later invitation to submit more plans and travel to Paris; it does not imply the new plans were adopted.",
    "st-chp7-p187-i28": "This records Bernini's introduction to Louis XIV on 4 June 1665 after his progress through the provinces; no route is inferred.",
    "st-chp7-p187-i29": "This records Bernini beginning a direct address to Louis XIV; the French quotation continues and closes on p.188.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p187-i04": "The commissioner is not identified; the work and artist are the grounded endpoints.",
    "st-chp7-p187-i06": "The inviter and stipend amount are unspecified; death occurred before Mola could set off.",
    "st-chp7-p187-i10": "Colbert is a co-actor retained in mentions; Louis XIV is the scalar subject endpoint for the shared proposal action.",
    "st-chp7-p187-i13": "The search outcome is a turn to Italy, while the scalar object currently represents the French alternatives considered; the specific Italian designers are not yet named.",
    "st-chp7-p187-i16": "The Louvre episode is described as a resulting tragicomedy and the writers are unnamed; this remains an open scholarly-reception relation.",
    "st-chp7-p187-i17": "The policies are summarized but not itemized as entities; Richelieu and Mazarin remain the named policy actors.",
    "st-chp7-p187-i21": "The temple and palace are generic architectural types in the quoted comparison, not separately identified buildings; the critic is unnamed.",
    "st-chp7-p187-i22": "The source reports an evaluation of the designs but does not identify the critic.",
    "st-chp7-p187-i23": "The source reports an evaluation of the designs but does not identify the critic.",
    "st-chp7-p187-i24": "Modern opinion is an unbounded and unnamed scholarly collective; Haskell says it endorsed most, not all, of the preceding views.",
    "st-chp7-p187-i26": "The rejecting actor and specific review process are not named.",
    "st-chp7-p187-i27": "The further plans are identified as a group in mentions while Paris is the travel endpoint; the invitation issuer is not stated in this sentence.",
    "st-chp7-p187-i29": "The quoted address continues to p.188 L233; only its opening is anchored here.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.187 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (223, "[Page 187]"),
        (224, "and both were enthusiastic collectors of Italian art"),
        (225, "Rome Ciro Ferri was also working for Louis XIV"),
        (226, "Soon after the onset of his rule Louis and Colbert"),
        (227, "plans to some of the leading Roman architects"),
        (228, "Arrogant nationalism had become very powerful"),
        (229, "Carlo Rainaldi and the unknown Candiani"),
        (231, "[Page 188]"),
        (232, "des princes souverains, qui se sont trouvés sur la route de Rome à Paris"),
    )
    if any(text not in source_lines[index] for index, text in required_source):
        raise SystemExit("p.187 source-line guards failed")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    expected_targets = set(TRUE_NOTES)
    if unset != expected_targets or len(unset) != 29:
        raise SystemExit(f"p.187 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 225 or end > 230 or start > end:
            raise SystemExit(f"invalid p.187 source anchor: {sid} {start}-{end}")
        refs = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing_refs = sorted({cid for cid in refs if cid and cid not in candidate_ids})
        if missing_refs:
            raise SystemExit(f"candidate reference missing for {sid}: {missing_refs}")

    for previous, successor in (
        ("st-chp7-p186-i19", "st-chp7-p187-i01"),
        ("st-chp7-p186-i20", "st-chp7-p187-i02"),
    ):
        q = by_id[previous].get("qualifiers") or {}
        if q.get("continuation_statement_id") != successor:
            raise SystemExit(f"cross-page continuation changed: {previous} -> {successor}")
    quote_target = by_id["st-chp7-p188-i01"].get("qualifiers") or {}
    if by_id["st-chp7-p188-i01"].get("segment_id") != "chp-7:07_CHP-7_sec_i:l232-241" or quote_target.get("source_line_start") != 233:
        raise SystemExit("p.188 quotation continuation target changed")
    if (by_id["st-chp7-p188-i01"].get("qualifiers") or {}).get("continuation_of_statement_id") != "st-chp7-p187-i29":
        raise SystemExit("p.188 quotation reciprocal link changed")

    for sid, note in TRUE_NOTES.items():
        q = by_id[sid].setdefault("qualifiers", {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        if sid in OPEN_ENDPOINTS:
            q["open_endpoint_reason"] = OPEN_ENDPOINTS[sid]
    for previous, successor in (
        ("st-chp7-p186-i19", "st-chp7-p187-i01"),
        ("st-chp7-p186-i20", "st-chp7-p187-i02"),
    ):
        q = by_id[successor].setdefault("qualifiers", {})
        q["continuation_of_statement_id"] = previous
        q["continuation_from_segment_id"] = "chp-7:07_CHP-7_sec_i:l215-222"
        q["continuation_status"] = "closed"
    quote_start = by_id["st-chp7-p187-i29"].setdefault("qualifiers", {})
    quote_start["continuation_to_segment_id"] = "chp-7:07_CHP-7_sec_i:l232-241"
    quote_start["continuation_status"] = "closed"
    quote_start["continuation_source_line_start"] = 233
    quote_start["continuation_source_line_end"] = 233

    output = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n"
    result = output.encode("utf-8")
    print(json.dumps({
        "mode": "apply" if args.apply else "dry_run",
        "segment": SEGMENT,
        "classified": len(unset),
        "relation_candidate_true": len(TRUE_NOTES),
        "relation_candidate_false": 0,
        "unset_in_segment": 0,
        "continuation_links": [
            "st-chp7-p186-i19 -> st-chp7-p187-i01",
            "st-chp7-p186-i20 -> st-chp7-p187-i02",
            "st-chp7-p187-i29 -> st-chp7-p188-i01",
        ],
        "before_sha256": digest(raw[STATEMENTS]),
        "after_sha256": digest(result),
    }, ensure_ascii=True))
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    atomic_write(STATEMENTS, result)
    print(f"backup={BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
