from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
CARDINAL_CANDIDATE = "cand-0995"
DUKE_CANDIDATE = "cand-12426"
CARDINAL_GROUP = "new-person:alessandro-farnese-b829378191"
DUKE_GROUP = "new-person:alessandro-farnese-duke-of-parma-cand-12426"
CAMPAIGN_MENTION = "m-chp5-sec-iii-l70-80-007"
CAMPAIGN_STATEMENT = "st-chp5-p137-farnese-named-as-campaign-leader"
CAMPAIGN_STATEMENTS_WITH_MENTION = {
    "st-chp5-p137-de-bello-farnese-campaigns",
    CAMPAIGN_STATEMENT,
}
PROCESS_REF = "S3-full-book-2026-10-16"
ULAN_ID = "500121936"
ULAN_URL = "http://vocab.getty.edu/page/ulan/500121936"
TRECCANI_URL = "https://www.treccani.it/enciclopedia/alessandro-farnese-duca-di-parma-piacenza-e-castro_(Dizionario-Biografico)/"
GOOGLE_BOOKS_ID = "EO8WSCkK8NYC"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def decision_rows(rows):
    return [row for row in rows if row.get("candidate_id") and not row.get("external_source")]


def group_of(row):
    match = re.search(r"group=([^;| ]+)", row.get("resolution_note", ""))
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser(description="Split the Farnese Cardinal and Low Countries campaign identities")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidates_path = TABLES / "entity-candidates.csv"
    alignment_path = TABLES / "alignment.csv"
    mentions_path = TABLES / "mentions.csv"
    statements_path = TABLES / "book-statements.jsonl"
    backlog_path = TABLES / "candidate-backlog.csv"
    candidate_fields, candidates = read_csv(candidates_path)
    alignment_fields, alignments = read_csv(alignment_path)
    mention_fields, mentions = read_csv(mentions_path)
    backlog_fields, backlog = read_csv(backlog_path)
    decisions = decision_rows(alignments)

    assert len(candidates) == 12403
    assert len(alignments) == 12588
    assert len(backlog) == 1
    counts = Counter(row["decision"] for row in decisions)
    assert counts == Counter({"same": 1696, "new": 4987, "undecided": 5616, "excluded": 97, "conflict": 7}), counts
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in decisions}
    assert DUKE_CANDIDATE not in candidate_by_id and DUKE_CANDIDATE not in alignment_by_id
    cardinal = candidate_by_id[CARDINAL_CANDIDATE]
    cardinal_alignment = alignment_by_id[CARDINAL_CANDIDATE]
    assert cardinal["canonical_name"] == "Farnese, Cardinal Alessandro"
    assert cardinal["index_entry_id"] == "F.csv#10"
    assert cardinal["index_page_range"] == "65, 66, 69, 78, 84, 137, 398, 399, 400"
    assert cardinal_alignment["decision"] == "new" and group_of(cardinal_alignment) == CARDINAL_GROUP
    assert not cardinal_alignment.get("ku_id")
    assert sum(row.get("mention_id") == CAMPAIGN_MENTION for row in mentions) == 1
    mention = next(row for row in mentions if row.get("mention_id") == CAMPAIGN_MENTION)
    assert mention["candidate_id"] == CARDINAL_CANDIDATE

    source_path = ROOT / "02-sources" / "02-Markdown" / "05_CHP-5_sec_iii.md"
    source_text = source_path.read_text(encoding="utf-8-sig")
    assert "Alessandro Farnese’s campaigns on behalf of the Spaniards in the Low\nCountries" in source_text
    assert "the second volume of Famiano Strada’s De Bello Belgico" in source_text
    statements = [json.loads(line) for line in statements_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}
    assert CAMPAIGN_STATEMENT in statement_by_id
    assert statement_by_id[CAMPAIGN_STATEMENT]["object_candidate_id"] == CARDINAL_CANDIDATE
    assert CAMPAIGN_STATEMENTS_WITH_MENTION <= set(statement_by_id)
    for sid in CAMPAIGN_STATEMENTS_WITH_MENTION:
        assert CARDINAL_CANDIDATE in statement_by_id[sid].get("qualifiers", {}).get("mentioned_candidate_ids", [])

    new_candidate = {
        "candidate_id": DUKE_CANDIDATE,
        "index_entry_id": "",
        "canonical_name": "Farnese, Alessandro, Duke of Parma",
        "index_page_range": "",
        "suggested_type": "person",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell names Alessandro Farnese as the person whose Low Countries campaigns are celebrated in the second volume of De Bello Belgico. Treccani's DBI identifies the campaign figure as Alessandro Farnese, Duke of Parma; keep distinct from Cardinal Alessandro Farnese.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-5:05_CHP-5_sec_iii:l70-80#L72",
    }
    new_decision = {
        "alignment_id": "aln-12589",
        "candidate_id": DUKE_CANDIDATE,
        "ku_id": "",
        "external_source": "",
        "external_id": "",
        "decision": "new",
        "accessed_date": "",
        "process_ref": PROCESS_REF,
        "legacy_ku_id": "",
        "resolution_note": (
            "source_ref=candidate=cand-12426;source=chp-5:05_CHP-5_sec_iii:l70-80#L72;"
            f"s2_mentions={CAMPAIGN_MENTION}@02-sources/02-Markdown/05_CHP-5_sec_iii.md#L70-80[Alessandro Farnese];"
            f"group={DUKE_GROUP}; S3 split: Haskell's p.137 campaign figure is distinct from index candidate cand-0995, Cardinal Alessandro Farnese. "
            f"Treccani DBI identifies the Low Countries commander as Alessandro Farnese, Duke of Parma ({TRECCANI_URL}); "
            f"Famiano Strada's 1647 second-volume title names Alessandro Farnese, Duke of Parma, Piacenza and Castro, for 1578-1590 (Google Books ID {GOOGLE_BOOKS_ID}). "
            "Identity evidence only; the source's relation predicate remains separately grounded in Haskell."
        ),
    }

    planned_candidates = list(candidates) + [new_candidate]
    planned_mentions = [dict(row) for row in mentions]
    next(row for row in planned_mentions if row["mention_id"] == CAMPAIGN_MENTION)["candidate_id"] = DUKE_CANDIDATE
    next(row for row in planned_mentions if row["mention_id"] == CAMPAIGN_MENTION)["note"] = (
        "Body-anchored person candidate; the Low Countries campaign context distinguishes this Alessandro Farnese from the cardinal entry."
    )

    revised_alignments = [dict(row) for row in alignments]
    revised_cardinal = next(row for row in revised_alignments if row.get("candidate_id") == CARDINAL_CANDIDATE and not row.get("external_source"))
    token = f"{CAMPAIGN_MENTION}@02-sources/02-Markdown/05_CHP-5_sec_iii.md#L70-80[Alessandro Farnese;chars=279-297]"
    assert token in revised_cardinal["resolution_note"]
    revised_cardinal["resolution_note"] = revised_cardinal["resolution_note"].replace(token, "", 1).replace(",; group=", "; group=", 1)
    revised_cardinal["resolution_note"] += (
        f" Cross-chapter split: page 137 campaign mention reassigned to {DUKE_CANDIDATE}; the raw index still lists page 137 under F.csv#10, "
        "but that index page reference does not override the distinct person identities. Cardinal identity externally aligned to Getty ULAN 500121936."
    )
    revised_alignments.append(new_decision)
    revised_alignments.append({
        "alignment_id": "aln-12590", "candidate_id": CARDINAL_CANDIDATE, "ku_id": "",
        "external_source": "Getty ULAN", "external_id": ULAN_ID, "decision": "same",
        "accessed_date": "2026-10-16", "process_ref": PROCESS_REF, "legacy_ku_id": "",
        "resolution_note": f"Identity only: Getty ULAN identifies Cardinal Alessandro Farnese (1520-1589), distinct from the Duke of Parma; {ULAN_URL}.",
    })
    revised_alignments.append({
        "alignment_id": "aln-12591", "candidate_id": DUKE_CANDIDATE, "ku_id": "",
        "external_source": "Treccani DBI", "external_id": TRECCANI_URL, "decision": "same",
        "accessed_date": "2026-10-16", "process_ref": PROCESS_REF, "legacy_ku_id": "",
        "resolution_note": f"Identity only: Treccani identifies Alessandro Farnese, Duke of Parma, as commander in the Low Countries; corroborated by the 1647 De Bello Belgico volume title (Google Books ID {GOOGLE_BOOKS_ID}).",
    })

    planned_statements = [dict(row) for row in statements]
    target = next(row for row in planned_statements if row["statement_id"] == CAMPAIGN_STATEMENT)
    target["object_candidate_id"] = DUKE_CANDIDATE
    target["qualifiers"]["mentioned_candidate_ids"] = [DUKE_CANDIDATE if cid == CARDINAL_CANDIDATE else cid for cid in target["qualifiers"].get("mentioned_candidate_ids", [])]
    for sid in CAMPAIGN_STATEMENTS_WITH_MENTION - {CAMPAIGN_STATEMENT}:
        row = next(row for row in planned_statements if row["statement_id"] == sid)
        row["qualifiers"]["mentioned_candidate_ids"] = [DUKE_CANDIDATE if cid == CARDINAL_CANDIDATE else cid for cid in row["qualifiers"].get("mentioned_candidate_ids", [])]

    backlog_fields_expected = [
        "backlog_id", "canonical_name", "suggested_type", "status", "source_id", "source_ref",
        "statement_id", "endpoint_role", "candidate_id", "ku_id", "decision_note", "process_ref",
    ]
    assert backlog_fields == backlog_fields_expected, backlog_fields
    new_backlog = {
        "backlog_id": "bl-0002",
        "canonical_name": new_candidate["canonical_name"],
        "suggested_type": "person",
        "status": "pending",
        "source_id": "haskell-1980-rev-ed",
        "source_ref": new_candidate["candidate_source_ref"],
        "statement_id": CAMPAIGN_STATEMENT,
        "endpoint_role": "person identified as subject of the Low Countries campaigns",
        "candidate_id": DUKE_CANDIDATE,
        "ku_id": "",
        "decision_note": "Candidate separated from Cardinal Alessandro Farnese after identity review; S1 candidate and S3 new group created. Pending S4 registration as a separate person KU.",
        "process_ref": "S1-S3-full-book-2026-10-16",
    }
    planned_backlog = list(backlog) + [new_backlog]

    if args.dry_run:
        print(
            "dry-run passed: split cardinal vs duke; candidate=cand-12426; "
            "reassigned_mentions=1 relation_endpoint=1 mentioned_candidate_refs=2; "
            "new_decisions=1 external_identity_records=2 pending_backlog=1; no KU registered"
        )
        return 0

    write_csv(candidates_path, candidate_fields, planned_candidates)
    write_csv(mentions_path, mention_fields, planned_mentions)
    write_csv(alignment_path, alignment_fields, revised_alignments)
    statements_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in planned_statements) + "\n",
        encoding="utf-8-sig",
        newline="",
    )
    write_csv(backlog_path, backlog_fields, planned_backlog)
    print(
        "applied: Cardinal/Duke Alessandro Farnese split; candidate=cand-12426; "
        "reassigned_mentions=1 relation_endpoint=1 mentioned_candidate_refs=2; "
        "new S3 decision and 2 external identity records added; backlog pending S4"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
