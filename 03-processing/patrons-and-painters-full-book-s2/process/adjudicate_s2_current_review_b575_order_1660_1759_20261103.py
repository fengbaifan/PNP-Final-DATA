#!/usr/bin/env python3
"""Adjudicate the B575 continuous current-version S2 window (orders 1660-1759)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process"
RESULTS = ROOT / "03-processing/patrons-and-painters-full-book-s2/results"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ROSTER_PATH = PROCESS / "s2-current-review-roster.csv"
HISTORY_PATH = PROCESS / "s2-history-9622-review-events.csv"
STAGES_PATH = PROCESS / "stages.md"
RESULT_STAGES_PATH = RESULTS / "stages.md"
CURRENT_RESULT_PATH = ROOT / "04-knowledge/results/patrons-and-painters-full-book-s2.md"
SOURCE_PATH = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
PDF_PATH = ROOT / "02-sources/01-book/CHP-2.pdf"
MENTIONS_PATH = TABLES / "mentions.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
RELATIONS_PATH = TABLES / "relations.csv"

BASE_HEAD = "1efded0c9846c016fded669994cc537da2474f90"
PDF_SHA256 = "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e"
SOURCE_SHA256 = "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9"
HISTORY_SHA256 = "75ab12df478a816035929353565b0301d55959c6bb13d9b511af072c4c931c89"
BATCH_ID = "S2-B575-CH2-1660-1759"
STAGE_ID = "2026-11-03-s2-current-review-b575-order-1660-1759"
EVIDENCE_REF = f"stages.md#{STAGE_ID}"
WINDOW_START = 1660
WINDOW_END = 1759

PROMOTED = {
    "st-chp2-secii-l80-89-cardinal-acquired-titian-holy-family": (
        "S3 aln-0367 already maps cand-0032 to units/persons/pietro-aldobrandini. Updated the S2 qualification to reflect that existing same decision; the source-local acquisition claim and work/place mappings are supported.",
    ),
    "st-chp2-secii-l80-89-marcello-encouraged-copying": (
        "The claim is limited to Marcello encouraging Pietro to copy Raphael and Titian. The focal-point and Baroque-foundation interpretation remains separate in statement st-chp2-secii-l80-89-copying-as-baroque-foundation.",
    ),
    "st-chp2-secii-l91-104-urban-portrait-appearance-continues-at-l119": (
        "Added the already-existing exact mention mappings for the bust group and Urban VIII. The claim is limited to the explicit p.40 fragment; its link to L119 and the continuation statement remain intact.",
    ),
}
RETAINED = {
    "st-chp2-secii-l80-89-copying-as-baroque-foundation": (
        "Pending: the sentence links Marcello's encouragement, a focal-point judgment, and a separate foundation judgment about the combination of Raphael's design and Titian's colour. The source-defined combination has no safe candidate endpoint; no movement-origin fact is inferred.",
    ),
    "st-chp2-secii-l80-89-copying-as-training-generalization": (
        "Pending: the source generalizes about every artist, while the proposed artist-class candidate is typed as term and lacks a defensible group endpoint. Preserve Haskell's universal wording without forcing a candidate type.",
    ),
    "st-chp2-secii-l91-104-baroque-flattery-interpretation": (
        "Pending: the two adjacent sentences make distinct judgments about flattery as a Baroque ingredient and Urban VIII giving it scope. Keep the statements separate before passing the composite record; do not add a formal relation.",
    ),
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    return sha256(raw)


def read_jsonl(path: Path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    return ([json.loads(line) for line in text.splitlines() if line.strip()], raw,
            "\r\n" if "\r\n" in text else "\n", raw.startswith(b"\xef\xbb\xbf"))


def read_csv(path: Path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader), list(reader.fieldnames or []), raw, (
        "\r\n" if "\r\n" in text else "\n"), raw.startswith(b"\xef\xbb\xbf")


def render_changed_jsonl(raw: bytes, updated_rows: dict[str, dict]) -> bytes:
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    found = set()
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        row = json.loads(line)
        sid = row.get("statement_id")
        if sid in updated_rows:
            lines[index] = json.dumps(updated_rows[sid], ensure_ascii=False)
            found.add(sid)
    require(found == set(updated_rows), f"Statement line replacement mismatch: {found ^ set(updated_rows)}")
    rendered = eol.join(lines) + eol
    return (b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b"") + rendered.encode("utf-8")


def render_csv(rows, fields, eol: str, bom: bool) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator=eol,
                            extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + out.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the validated B575 changes")
    args = parser.parse_args()

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    require(head == BASE_HEAD, f"Unexpected baseline HEAD: {head}")
    require(sha256(PDF_PATH.read_bytes()) == PDF_SHA256, "Authoritative CHP-2.pdf hash changed")
    require(sha256(SOURCE_PATH.read_bytes()) == SOURCE_SHA256, "Chapter 2 section source hash changed")
    statements, statements_raw, statements_eol, statements_bom = read_jsonl(STATEMENTS_PATH)
    roster, roster_fields, roster_raw, roster_eol, roster_bom = read_csv(ROSTER_PATH)
    mentions, _, _, _, _ = read_csv(MENTIONS_PATH)
    alignments, _, _, _, _ = read_csv(ALIGNMENT_PATH)
    relations, _, relations_raw, _, _ = read_csv(RELATIONS_PATH)
    history_raw = HISTORY_PATH.read_bytes()
    require(sha256(history_raw) == HISTORY_SHA256, "Immutable H9622 history ledger hash changed")

    statement_by_id = {row["statement_id"]: row for row in statements}
    roster_by_id = {row["statement_id"]: row for row in roster}
    selected = sorted((row for row in roster if WINDOW_START <= int(row["current_order"]) <= WINDOW_END),
                      key=lambda row: int(row["current_order"]))
    require(len(selected) == 100, f"Expected 100 current IDs, found {len(selected)}")
    require([int(row["current_order"]) for row in selected] == list(range(WINDOW_START, WINDOW_END + 1)),
            "B575 roster window is not a continuous 100-ID span")
    require(set(PROMOTED).isdisjoint(RETAINED), "Promotion and retained sets overlap")
    require(set(PROMOTED) | set(RETAINED) == {
        row["statement_id"] for row in selected
        if row["current_review_status"] == "reviewed_current_pending"
    }, "The six current pending IDs changed")
    before_status = Counter(row["current_review_status"] for row in selected)
    require(before_status == Counter({"reviewed_current_pass": 94, "reviewed_current_pending": 6}),
            f"Unexpected status distribution: {dict(before_status)}")

    # Reuse PASS decisions only when the exact current statement and source fingerprints match.
    for row in selected:
        sid = row["statement_id"]
        require(sid in statement_by_id, f"Statement missing: {sid}")
        require(canonical_hash(statement_by_id[sid]) == row["current_statement_sha256"],
                f"Current statement hash mismatch: {sid}")
        require(row["source_asset_sha256"] == SOURCE_SHA256,
                f"Source asset version mismatch: {sid}")
    pending_before = {row["statement_id"] for row in selected
                      if row["current_review_status"] == "reviewed_current_pending"}
    require(pending_before == set(PROMOTED) | set(RETAINED), "Pending set changed")

    # Verify the original S3 same decision before updating the stale S2 qualification.
    aln = [row for row in alignments if row["alignment_id"] == "aln-0367"]
    require(len(aln) == 1 and aln[0]["candidate_id"] == "cand-0032"
            and aln[0]["ku_id"] == "units/persons/pietro-aldobrandini"
            and aln[0]["decision"] == "same", "Expected S3 same alignment aln-0367")

    # Assert exact spans for the existing source mentions used by the portrait fragment.
    lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(lines[90:104])
    mention_by_id = {row["mention_id"]: row for row in mentions}
    exact_mentions = {
        "m-chp2-secii-l91-104-0063": ("cand-4499", "them"),
        "m-chp2-secii-l91-104-0064": ("cand-0232", "the\nPope"),
    }
    for mid, (candidate_id, surface) in exact_mentions.items():
        row = mention_by_id.get(mid)
        require(row is not None and row["segment_id"] == "chp-2:02_CHP-2_sec_ii:l91-104"
                and row["candidate_id"] == candidate_id and row["surface_form"] == surface,
                f"Portrait mention mapping changed: {mid}")
        start, end = int(row["start_char"]), int(row["end_char"])
        require(segment_text[start:end] == surface, f"Mention span mismatch: {mid}")

    # The only formal edges anchored in this continuous source window are the three p.39 edges.
    selected_ids = {row["statement_id"] for row in selected}
    linked_relations = []
    for row in relations:
        marker = "statement="
        if marker not in row["source_span"]:
            continue
        linked_ids = row["source_span"].split(marker, 1)[1].replace(" ", "").split(",")
        if selected_ids.intersection(linked_ids):
            linked_relations.append(row)
    require({row["relation_id"] for row in linked_relations} == {"rel-2470", "rel-2471", "rel-2472"},
            f"Unexpected relation footprint: {[row['relation_id'] for row in linked_relations]}")
    require(all(row["status"] == "formal" for row in linked_relations),
            "A p.39 formal relation is no longer formal")

    # Prepare the two statement updates and retain the source continuation boundary.
    st_1661 = statement_by_id[next(s for s in PROMOTED if "cardinal-acquired" in s)]
    q1 = dict(st_1661.get("qualifiers") or {})
    q1["qualification"] = (
        "The source does not state when or by what transaction the acquisition occurred. "
        "S3 alignment aln-0367 matches the Cardinal Aldobrandini mention to Pietro Aldobrandini "
        "(units/persons/pietro-aldobrandini); the source-local work and Ferrara mappings remain distinct."
    )
    st_1661["qualifiers"] = q1

    st_1729 = statement_by_id[next(s for s in PROMOTED if "portrait-appearance-continues" in s)]
    q2 = dict(st_1729.get("qualifiers") or {})
    q2["claim"] = (
        "Haskell says the Pope appears exceedingly handsome and aristocratic in the busts, "
        "then begins a description of his long moustaches and beard."
    )
    q2["qualification"] = (
        "The source fragment ends at L104 and resumes at L119 after intervening caption segments. "
        "This claim is limited to the appearance elements explicit before the cutoff; the existing "
        "continuation link remains, and later text is not imported into this statement."
    )
    q2["mentioned_candidate_ids"] = ["cand-4499", "cand-0232"]
    require(q2.get("continues_to_segment_id") == "chp-2:02_CHP-2_sec_ii:l118-125"
            and q2.get("continues_at_line") == 119
            and q2.get("continued_by_statement_ids") == ["st-chp2-secii-l118-125-urban-portrait-appearance-continuation"],
            "Portrait continuation metadata changed")
    st_1729["qualifiers"] = q2

    # All current endpoints of promoted relation candidates must be represented in the mention map.
    for sid in PROMOTED:
        row = statement_by_id[sid]
        qualifiers = row.get("qualifiers") or {}
        require(qualifiers.get("relation_candidate") is True, f"Expected relation candidate: {sid}")
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint:
                require(endpoint in qualifiers.get("mentioned_candidate_ids", []),
                        f"Promoted endpoint omitted from mentioned_candidate_ids: {sid} -> {endpoint}")

    updated_statement_ids = {next(s for s in PROMOTED if "cardinal-acquired" in s),
                             next(s for s in PROMOTED if "portrait-appearance-continues" in s)}
    roster_after = [dict(row) for row in roster]
    roster_after_by_id = {row["statement_id"]: row for row in roster_after}
    old_refs = {row["statement_id"]: row.get("review_evidence_ref", "") for row in selected}
    for row in selected:
        sid = row["statement_id"]
        new = roster_after_by_id[sid]
        new["review_batch_id"] = BATCH_ID
        new["review_evidence_ref"] = EVIDENCE_REF
        if sid in PROMOTED:
            new["current_review_status"] = "reviewed_current_pass"
            new["review_outcome"] = "current_semantic_pass_after_targeted_claim_and_mapping_repair"
            detail = PROMOTED[sid][0]
        elif sid in RETAINED:
            new["current_review_status"] = "reviewed_current_pending"
            new["review_outcome"] = "current_pending_retained_after_claim_atomicity_or_endpoint_review"
            detail = RETAINED[sid][0]
        else:
            require(row["current_review_status"] == "reviewed_current_pass",
                    f"Unclassified non-PASS row: {sid}")
            new["current_review_status"] = "reviewed_current_pass"
            new["review_outcome"] = "reused_current_pass_after_B575_full_window_fingerprint_check"
            detail = "Existing current PASS reused after exact current ID, statement, source asset, segment, and mention fingerprint checks; prior source evidence remains applicable."
        previous = new.get("follow_up_note", "").strip()
        new["follow_up_note"] = f"B575: {detail} Prior current evidence: {old_refs[sid]}.\n{previous}".strip()

    for sid in updated_statement_ids:
        row = roster_after_by_id[sid]
        current_hash = canonical_hash(statement_by_id[sid])
        row["current_statement_sha256"] = current_hash
        if int(row.get("history_9622_event_count") or "0") > 0:
            row["history_9622_current_statement_match"] = (
                "exact" if row["history_9622_latest_statement_sha256"] == current_hash else "changed"
            )
            row["prior_review_match"] = (
                "exact_object_and_source_segment"
                if row["history_9622_current_statement_match"] == "exact"
                and row["history_9622_source_match"] == "true"
                else "historical_object_or_source_differs"
            )

    after_counts = Counter(row["current_review_status"] for row in roster_after)
    window_after = Counter(roster_after_by_id[row["statement_id"]]["current_review_status"] for row in selected)
    require(window_after == Counter({"reviewed_current_pass": 97, "reviewed_current_pending": 3}),
            f"Unexpected B575 window outcome: {dict(window_after)}")
    require(len(statements) == 15518, f"Unexpected current statement count: {len(statements)}")
    require(after_counts["reviewed_current_pass"] == 8794
            and after_counts["reviewed_current_pending"] == 6724,
            f"Unexpected full-book S2 status: {dict(after_counts)}")
    history_matches = Counter(row["history_9622_current_statement_match"] for row in roster_after
                              if int(row.get("history_9622_event_count") or "0") > 0)
    require(history_matches == Counter({"exact": 8833, "changed": 704}),
            f"Unexpected current H9622 hash mapping: {dict(history_matches)}")
    require(sum(int(row.get("history_9622_event_count") or "0") for row in selected) == 98,
            "Expected 98 mapped historical events in the window")
    require(sum(row.get("history_9622_source_match") == "true" for row in selected) == 98,
            "Expected all 98 source versions to match")
    require(sha256(RELATIONS_PATH.read_bytes()) == sha256(relations_raw), "Relation table changed during planning")

    statements_bytes = render_changed_jsonl(
        statements_raw,
        {sid: statement_by_id[sid] for sid in updated_statement_ids},
    )
    roster_bytes = render_csv(roster_after, roster_fields, roster_eol, roster_bom)

    pdf_hash = PDF_SHA256
    source_hash = SOURCE_SHA256
    percent_pass = 100 * after_counts["reviewed_current_pass"] / len(statements)
    percent_pending = 100 * after_counts["reviewed_current_pending"] / len(statements)
    changed_ids_in_history = sum(
        row["history_9622_current_statement_match"] == "changed"
        and row["statement_id"] in updated_statement_ids
        for row in roster_after
    )
    process_record = f"""

<a id="{STAGE_ID}"></a>
### 2026-11-03 S2 当前版逐ID语义复核阶段 B575（当前顺序1660–1759）

**范围与复用。** 连续核平100条当前statement，顺序1660–1759，覆盖第二章第二节p.38–41附近的来源段及图版题注。94条已有PASS在当前statement、来源资产、segment与mention指纹一致后复用；6条pending逐项回到已有原页finding和当前S3/mention状态，3条转为PASS，3条保持pending。复用PASS不重复视觉阅读，保留其原复核证据入口。

**原文、版本与历史核平。** 权威`CHP-2.pdf` SHA-256=`{pdf_hash}`；第二节Markdown SHA-256=`{source_hash}`。窗口100/100当前statement指纹与roster一致；H9622中98条事件均匹配当前来源版本，窗口原statement hash为41 exact、57 changed、2条无历史事件。p.39–40 finding复用B433对印刷页的逐页核读；本阶段依当前原文句段和既有扫描结论只处理未决ID，不重读已PASS页或复制相同finding。

**三条pending转PASS。** 顺序1661：S3既有`aln-0367=same`已把Cardinal Aldobrandini对应到Pietro Aldobrandini；修正S2 qualification中“身份仍待S3”的过期说明，保留作品与Ferrara端点边界，不改S3决定。顺序1664：claim仅记Marcello鼓励Pietro复制Raphael与Titian；与顺序1662的focal-point／Baroque解释分开，不宣称Marcello创立Baroque。顺序1729：portrait-group与Urban VIII映射已有精确原文mention；补入其`mentioned_candidate_ids`，claim只限p.40可见的外貌断句，保留L119续接segment/statement，不把后续页文字并入。

**三条继续pending。** 顺序1662：鼓励复制、历史focal point和“Raphael设计＋Titian色彩”作为Baroque foundation存在不同命题，后者缺少安全的来源限定组合端点；保留作者判断，不臆造movement起源。顺序1663：every artist为作者的普遍概括，候选群体目前suggested type=`term`且无稳妥群体端点；不强改类型。顺序1713：flattery是Baroque要素与Urban VIII给予表达机会是相邻的两项判断；先拆清原子性，暂不追加关系或端点。

| 当前范围 | 完成情况 |
|---|---:|
| 连续当前statement | 100（1660–1759） |
| 既有PASS指纹复用 | 94 |
| pending转PASS | 3 |
| 保留pending | 3（1662、1663、1713） |
| 新增statement／mention | 0／0 |
| statement字段修订 | 2 |

**关系与历史裁决影响。** 对照`relations.csv`中本窗口来源statement所支撑的`rel-2470`（p.39 L83 employed_by）、`rel-2471`（L85 designed_by）、`rel-2472`（L83 located_at）；三条均保持formal，端点、谓词、来源范围及状态不变，关联statement仍为PASS。无其他正式关系行以本窗口statement为来源；S6关系表、S3 alignment与候选表均未改。H9622历史事件账本保持9,622行、SHA-256=`{HISTORY_SHA256}`，历史review hash和裁决未回写；仅当前statement hash映射由窗口内两条statement更新为changed，窗口事件仍98/98来源匹配。

**批后状态与下一批。** 全书当前statement {len(statements):,}条、mention {len(mentions):,}条；PASS {after_counts['reviewed_current_pass']:,}（{percent_pass:.2f}%），pending {after_counts['reviewed_current_pending']:,}（{percent_pending:.2f}%）。H9622当前ID级statement hash为exact {history_matches['exact']:,}、changed {history_matches['changed']:,}。下一连续窗口为1760–1859；全书仍有{after_counts['reviewed_current_pending']:,}条pending。修订针对当前版，并非独立复核已修订版本。
""".strip()

    result_index = (
        f"\n\n### 2026-11-03 S2 current semantic review stage B575 (1660–1759)\n\n"
        f"Reviewed 100 continuous current statements: reused 94 current PASS, promoted 3 pending to PASS, and retained 3 pending. "
        f"Updated 2 statements, adding no statements or mentions. Current full-book totals: {len(statements)} statements, {len(mentions)} mentions, "
        f"{after_counts['reviewed_current_pass']} PASS, {after_counts['reviewed_current_pending']} pending. "
        f"S3 alignments, formal relations, and immutable H9622 outcomes were preserved. See [B575 process record](../process/stages.md#{STAGE_ID}).\n"
    )

    stages_text = STAGES_PATH.read_text(encoding="utf-8-sig")
    result_stages_text = RESULT_STAGES_PATH.read_text(encoding="utf-8-sig")
    require(STAGE_ID not in stages_text and STAGE_ID not in result_stages_text, "B575 stage already recorded")
    stages_text = stages_text.rstrip() + "\n\n" + process_record + "\n"
    result_stages_text = result_stages_text.rstrip() + result_index
    current_result_text = CURRENT_RESULT_PATH.read_text(encoding="utf-8-sig")
    current_lines = current_result_text.splitlines()
    status_line_idx = next((i for i, line in enumerate(current_lines)
                            if line.startswith("**后续顺序（逐阶段执行）：**")), None)
    require(status_line_idx is not None, "Unexpected current-result status line")
    current_lines[status_line_idx] = (
        f"**后续顺序（逐阶段执行）：** **S1 → S2 → S3 → S4 → S5 → S6 → S7。** "
        f"S1索引、图版、书目及当前候选来源映射复核通过；候选12,456项。S2当前版本为{len(statements):,}条statement、{len(mentions):,}条mention；"
        f"逐ID清单{len(roster_after):,}/{len(roster_after):,}均有当前决定：PASS {after_counts['reviewed_current_pass']:,}（{percent_pass:.2f}%）、"
        f"pending {after_counts['reviewed_current_pending']:,}（{percent_pending:.2f}%），尚未全书独立语义接收。H9622历史事件账本9,622行保持不变；"
        f"当前roster映射9,620条事件至9,537个ID（含83条重复审读，另2个旧ID各有撤销/拆分去向），当前ID级statement hash为"
        f"{history_matches['exact']:,} exact、{history_matches['changed']:,} changed。B575连续复核当前顺序1660–1759共100条：94条PASS复用、"
        f"3条pending转PASS、3条保留pending。全书S2仍有{after_counts['reviewed_current_pending']:,}条pending；下一连续窗口1760–1859。"
        f"S3–S6需逐类收口，S7待前序阶段收口后开展。"
    )
    current_result_text = "\n".join(current_lines) + "\n"

    planned = {
        "batch": BATCH_ID,
        "window": [WINDOW_START, WINDOW_END],
        "promoted": sorted(PROMOTED),
        "retained": sorted(RETAINED),
        "statement_hashes": {sid: canonical_hash(statement_by_id[sid]) for sid in sorted(updated_statement_ids)},
        "status": dict(after_counts),
        "history_hashes": dict(history_matches),
        "relations": [row["relation_id"] for row in linked_relations],
        "history_ledger_sha256": HISTORY_SHA256,
    }
    plan_hash = canonical_hash(planned)
    print(json.dumps({"mode": "apply" if args.apply else "dry-run", "plan_sha256": plan_hash,
                      "window_count": len(selected), "before_window": dict(before_status),
                      "after_window": dict(window_after), "after_global": dict(after_counts),
                      "h9622_exact_changed": dict(history_matches), "relations_checked": [r["relation_id"] for r in linked_relations],
                      "modified_statement_ids": sorted(updated_statement_ids), "added_mentions": 0},
                     ensure_ascii=True, sort_keys=True))
    if not args.apply:
        return

    current_result_raw = CURRENT_RESULT_PATH.read_bytes()
    stages_raw = STAGES_PATH.read_bytes()
    result_stages_raw = RESULT_STAGES_PATH.read_bytes()
    for path, data in ((STATEMENTS_PATH, statements_bytes), (ROSTER_PATH, roster_bytes)):
        atomic_write(path, data)
    for path, text, raw in ((STAGES_PATH, stages_text, stages_raw),
                            (RESULT_STAGES_PATH, result_stages_text, result_stages_raw),
                            (CURRENT_RESULT_PATH, current_result_text, current_result_raw)):
        bom = raw.startswith(b"\xef\xbb\xbf")
        atomic_write(path, (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))
    print(f"applied={BATCH_ID}")


if __name__ == "__main__":
    main()
