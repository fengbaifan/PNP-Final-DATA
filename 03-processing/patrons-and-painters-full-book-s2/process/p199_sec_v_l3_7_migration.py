"""Controlled S2 migration for the p.199 section V body segment.

Default invocation performs a read-only dry run. Use --apply only after
reviewing the semantic payload and the generated mention spans.
"""
import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_REL = "02-sources/02-Markdown/07_CHP-7_sec_v.md"
SOURCE_PATH = ROOT / SOURCE_REL
SEGMENT_ID = "chp-7:07_CHP-7_sec_v:l3-7"
NEXT_SEGMENT_ID = "chp-7:07_CHP-7_sec_v:l9-18"
LINE_START = 3
LINE_END = 7
PRINTED_PAGE = 199
PDF_PHYSICAL_PAGE = 37

CANDIDATE_PATH = TABLES / "entity-candidates.csv"
MENTION_PATH = TABLES / "mentions.csv"
STATEMENT_PATH = TABLES / "book-statements.jsonl"
COVERAGE_PATH = TABLES / "s2-coverage.csv"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
segment_record = next(
    json.loads(line)
    for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8").splitlines()
    if json.loads(line).get("segment_id") == SEGMENT_ID
)
if segment_record["source_file"] != SOURCE_REL:
    raise SystemExit("segment source_file differs from the current S0 record")
if segment_record["line_start"] != LINE_START or segment_record["line_end"] != LINE_END:
    raise SystemExit("segment bounds differ from the current S0 record")
if hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest() != segment_record["asset_sha256"]:
    raise SystemExit("source asset fingerprint changed; stop and review the affected source")
segment_text = "\n".join(source_lines[LINE_START - 1 : LINE_END])

candidate_fields, candidate_rows = read_csv(CANDIDATE_PATH)
mention_fields, mention_rows = read_csv(MENTION_PATH)
coverage_fields, coverage_rows = read_csv(COVERAGE_PATH)
statement_rows = [
    json.loads(line)
    for line in STATEMENT_PATH.read_text(encoding="utf-8").splitlines()
    if line
]

coverage = next((row for row in coverage_rows if row["segment_id"] == SEGMENT_ID), None)
if coverage is None or coverage["disposition"] != "queued":
    raise SystemExit(f"expected a queued coverage row for {SEGMENT_ID}")
if any(row["segment_id"] == SEGMENT_ID for row in mention_rows):
    raise SystemExit(f"mentions already exist for {SEGMENT_ID}; inspect before rerunning")
if any(row["segment_id"] == SEGMENT_ID for row in statement_rows):
    raise SystemExit(f"statements already exist for {SEGMENT_ID}; inspect before rerunning")


def candidate(candidate_id, name, entity_type, detail, line):
    return {
        "candidate_id": candidate_id,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": entity_type,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
    }


new_candidates = [
    candidate(
        "cand-7272",
        "Italianising of Europe in Haskell's p.199 account",
        "term",
        "The source's qualitative description of a cultural process; Haskell says it had earlier been among the popes' aims. The precise policy, agents, and scope of Italianising are not specified.",
        4,
    ),
    candidate(
        "cand-7273",
        "Painters and artists in Haskell's late-seventeenth-century Italian patronage account (unnamed group)",
        "term",
        "Collective class used for the broad northward orientation and artists in the named provincial centres. No individual painter is inferred from the generalization.",
        3,
    ),
    candidate(
        "cand-7274",
        "Works sent abroad by artists in the named Italian centres (unspecified group)",
        "work",
        "Haskell refers collectively to works sent from Bologna, Venice, or Naples to distant cities; no individual work or one-to-one city-to-work mapping is identified.",
        4,
    ),
    candidate(
        "cand-7275",
        "Aspiring collectors in England and Germany (unnamed group)",
        "term",
        "A generalized class in Haskell's comparison; no individual collector or collection is named.",
        4,
    ),
    candidate(
        "cand-7276",
        "Several complex wars in Haskell's account of Italy's renewed political prominence",
        "event",
        "The source refers to a number of wars collectively but does not enumerate them in this segment; do not resolve the group to specific conflicts here.",
        6,
    ),
    candidate(
        "cand-7277",
        "Relative isolation of Italy in Haskell's late-seventeenth-century account",
        "term",
        "Source-derived concept attached to the phrase 'this isolation'; its precise antecedent and relation to the roughly 150-year status quo remain interpretive and should not be over-specified.",
        6,
    ),
    candidate(
        "cand-7278",
        "Venice as political actor in Haskell's 1684 Holy League account",
        "institution",
        "The source attributes joining an alliance to 'Venice', indicating a political actor. Its formal polity name is not supplied; keep distinct from the city candidate pending S3.",
        7,
    ),
    candidate(
        "cand-7279",
        "Holy League named in Haskell's account of 1684",
        "institution",
        "A political alliance joined by Venice, with the Holy Roman Empire and King of Poland named in the same sentence. No fuller formal title or organizational details are given.",
        7,
    ),
    candidate(
        "cand-7280",
        "King of Poland unnamed in Haskell's 1684 Holy League account",
        "person",
        "The ruler is referred to by title only. Do not merge with the index-seeded John Sobieski candidate or supply a personal name until S3 identity review.",
        7,
    ),
    candidate(
        "cand-7281",
        "Popes as an unnamed collective in Haskell's late-seventeenth-century patronage account",
        "term",
        "The source refers to popes in the plural and names no pontiff. Represent the collective officeholders in this authorial argument, not a single pope or a formal institution.",
        3,
    ),
]

new_candidate_ids = {row["candidate_id"] for row in new_candidates}
existing_candidate_ids = {row["candidate_id"] for row in candidate_rows}
if new_candidate_ids & existing_candidate_ids:
    raise SystemExit("one or more planned candidate IDs already exist")
if max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows) != 7271:
    raise SystemExit("candidate table advanced from the expected ID boundary; reassign new IDs")

# surface, candidate ID, note, source line numbers
mention_specs = [
    ("Italy", "cand-3461", "地理实体；本段L3与L6分别指意大利的艺术赞助环境及其国际政治处境。", [3, 6]),
    ("Rome", "cand-4490", "城市；L3、L4均指罗马作为艺术中心。", [3, 4]),
    ("the popes", "cand-7281", "集体指称；原文为复数且未具名，不映射到具体教宗或制度实体。", [3]),
    ("their aims", "cand-7281", "the popes所述的历史目标；这一所有格回指未具名教宗群体。", [4]),
    ("Italianising of Europe", "cand-7272", "Haskell用于描述欧洲文化变化的过程概念；不转写为单一历史事件。", [4]),
    ("which had been one of their aims", "cand-7272", "关系从句回指Italianising of Europe；其中their指the popes。", [4]),
    ("Europe", "cand-3462", "被描述为受到意大利化影响的地理区域。", [4]),
    ("this loss of power", "cand-7281", "指前文教宗群体权力的衰退；属于Haskell的因果解释。", [4]),
    ("active ‘provincial’ centres", "cand-2066", "复用索引中的provincial centres of art patronage候选；Haskell的类别称呼，具体城市稍后列出。", [4]),
    ("Roman", "cand-4490", "Roman art指罗马艺术传统/中心，作为地点修饰语映射到Rome；不新建艺术风格实体。", [4]),
    ("Carlo Maratta", "cand-1526", "索引候选；身份和跨章同一性留待S3。", [4]),
    ("the aspiring collector", "cand-7275", "泛指英格兰与德国的潜在收藏者，不对应具体人物。", [4]),
    ("England", "cand-7200", "复用英格兰地点候选；句中为收藏者所在地域。", [4]),
    ("Germany", "cand-5529", "复用德国地点候选；句中为收藏者所在地域。", [4]),
    ("Bologna", "cand-3398", "复用已有地点候选；为收藏者可转向的意大利中心之一。", [4]),
    ("Venice", "cand-3401", "本次指城市/艺术中心Venice，不是L7的外交行动主体。", [4]),
    ("Naples", "cand-3534", "复用已有城市地点候选；为收藏者可转向的意大利中心之一。", [4]),
    ("these cities", "cand-2066", "指前文Bologna、Venice、Naples三城；不表示一个独立政治实体。", [4]),
    ("Artists in these cities", "cand-7273", "未具名艺术家群体；范围限于前述城市，不推出逐人逐城关联。", [4]),
    ("they", "cand-7273", "指artists in these cities。", [4]),
    ("their works", "cand-7274", "作品群未具名；所有格指artists in these cities，来源未给出单件作品或创作城市对应关系。", [4]),
    ("London", "cand-1422", "索引候选；此处为意大利艺术作品传播到达地之一。", [4]),
    ("Paris", "cand-4653", "复用城市地点候选；此处为传播到达地之一。", [4]),
    ("Vienna", "cand-2772", "索引候选；L4为作品传播到达地，L7为1683年事件所涉城市。", [4, 7]),
    ("Munich", "cand-7155", "复用城市地点候选；此处为传播到达地之一。", [4]),
    ("Stockholm", "cand-4790", "复用城市地点候选；此处为传播到达地之一。", [4]),
    ("Madrid", "cand-1481", "索引候选；此处为传播到达地之一。", [4]),
    ("Crespi", "cand-0871", "索引候选；原文仅用姓氏。", [4]),
    ("Francéschini", "cand-1069", "S0 OCR表面带重音；页图印本为Franceschini。按原S0跨度定位，校读只记S2。", [5]),
    ("Luca Giordano", "cand-1172", "索引候选；此处列入Haskell的欧洲受欢迎画家。", [5]),
    ("Solimena", "cand-2484", "索引候选；原文仅用姓氏。", [5]),
    ("Lazzarini", "cand-1368", "索引候选；原文仅用姓氏。", [5]),
    ("Sebastiano Ricci", "cand-2154", "索引候选；此处列入Haskell的欧洲受欢迎画家。", [5]),
    ("Maratta", "cand-1526", "承接L4 Carlo Maratta；此处仅用姓氏。", [6]),
    ("Trevisani", "cand-2650", "索引候选；原文仅用姓氏，身份留待S3。", [6]),
    ("this isolation", "cand-7277", "Haskell对意大利相对孤立状态的回指；其具体起点和范围未定义。", [6]),
    ("a number of complex wars", "cand-7276", "未具名的战争集合；本段不把其成员推定为单一战争。", [6]),
    ("European", "cand-3462", "地域形容词；Haskell对所列艺术家的概括性评价。", [6]),
    ("the Turks", "cand-7153", "复用既有集体候选；原书未说明具体军队、统帅或行动。", [7]),
    ("Venice", "cand-7278", "L7的外交行动主体，按政治实体候选记录；与L4城市提及分开。", [7]),
    ("a Holy League", "cand-7279", "原书只称a Holy League；联盟的具体正式身份不在S2作外部推定。", [7]),
    ("the Holy Roman Empire", "cand-6994", "复用既有政治实体候选；句中列为该联盟的伙伴。", [7]),
    ("the King of Poland", "cand-7280", "仅有王号，未给出姓名；与索引John Sobieski候选保持区分，待S3核对。", [7]),
]


def statement(statement_id, start, end, predicate, claim, qualification,
              subject=None, obj=None, mentioned=(), extra=None):
    qualifiers = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": PRINTED_PAGE,
        "pdf_physical_page": PDF_PHYSICAL_PAGE,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "body",
        "qualification": qualification,
        "mentioned_candidate_ids": list(mentioned),
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": "\n".join(source_lines[start - 1 : end]),
        "origin": "book",
        "source_file": SOURCE_REL,
    }


statements = [
    statement(
        "st-chp7-p199-v-patronage-conditions-changed",
        3, 3, "patronage_conditions_changed",
        "Haskell states that conditions of art patronage in Italy had totally altered during the second half of the seventeenth century.",
        "This is a broad authorial synthesis; retain totally as Haskell's emphasis, not a measured quantity.",
        subject="cand-3461", mentioned=["cand-3461"],
    ),
    statement(
        "st-chp7-p199-v-painters-looked-north",
        3, 3, "painters_compelled_to_look_north",
        "Haskell says painters were compelled to look north rather than to Rome.",
        "The painters and northern destinations are not specified here; do not infer a migration route or individual careers.",
        obj="cand-4490", mentioned=["cand-7273", "cand-4490"],
    ),
    statement(
        "st-chp7-p199-v-papal-decline-and-italianising",
        3, 4, "declining_papal_prestige_linked_to_italianising",
        "Haskell presents the declining prestige of the popes as a paradoxical cause of the Italianising of Europe, which he says had earlier been among their aims.",
        "This is Haskell's causal interpretation and cultural characterization. Their refers to the popes collectively; no individual pope, policy, or precise meaning of Italianising is named.",
        subject="cand-7281", obj="cand-7272",
        mentioned=["cand-7281", "cand-7272", "cand-3462"],
    ),
    statement(
        "st-chp7-p199-v-papal-power-and-provincial-centres",
        4, 4, "loss_of_papal_power_indirectly_encouraged_provincial_centres",
        "Haskell argues that loss of papal power limited the concentration of artists in Rome and indirectly encouraged the growth of active provincial centres.",
        "Preserve indirectly and Haskell's quoted label provincial; the sentence does not yet identify those centres by name.",
        subject="cand-7281", obj="cand-2066",
        mentioned=["cand-7281", "cand-4490", "cand-2066", "cand-7273"],
    ),
    statement(
        "st-chp7-p199-v-roman-art-reputation",
        4, 4, "roman_art_retained_reputation_but_was_no_longer_unique",
        "Haskell says Roman art, represented above all by Carlo Maratta, continued to enjoy a great reputation but was no longer unique.",
        "This is a qualitative comparison in the author's account, not a measured ranking.",
        subject="cand-4490", obj="cand-1526",
        mentioned=["cand-4490", "cand-1526"],
    ),
    statement(
        "st-chp7-p199-v-collectors-alternative-centres",
        4, 4, "collectors_could_turn_to_other_italian_centres",
        "Haskell says aspiring collectors in England and Germany could, and often did, turn to Bologna, Venice, or Naples instead of Rome.",
        "Retain could and often did; this does not name collectors or assign a particular collector to a particular city.",
        subject="cand-7275",
        mentioned=["cand-7275", "cand-7200", "cand-5529", "cand-3398", "cand-3401", "cand-3534", "cand-4490"],
    ),
    statement(
        "st-chp7-p199-v-artists-sent-works-abroad",
        4, 4, "artists_sent_works_to_distant_cities",
        "Haskell says artists in Bologna, Venice, and Naples broke through the restrictive local regimes under which they lived and sent their works as far as London, Paris, Vienna, Munich, Stockholm, and Madrid.",
        "The statement is collective. It does not identify individual artists, particular works, or a one-to-one origin-and-destination mapping.",
        subject="cand-7273", obj="cand-7274",
        mentioned=["cand-7273", "cand-7274", "cand-2066", "cand-3398", "cand-3401", "cand-3534", "cand-1422", "cand-4653", "cand-2772", "cand-7155", "cand-4790", "cand-1481"],
    ),
    statement(
        "st-chp7-p199-v-artists-european-favourites",
        5, 6, "artists_described_as_european_favourites",
        "Haskell describes Crespi, Franceschini, Luca Giordano, Solimena, Lazzarini, and Sebastiano Ricci as European favourites just as much as Maratta and Trevisani.",
        "European favourites is Haskell's qualitative characterization, not an independently measured popularity claim. The OCR's Francéschini is corrected from the page image in this S2 record; S0 remains unchanged.",
        mentioned=["cand-0871", "cand-1069", "cand-1172", "cand-2484", "cand-1368", "cand-2154", "cand-1526", "cand-2650", "cand-3462"],
        extra={"ocr_corrections": [{"line": 5, "source_text": "Francéschini", "print_reading": "Franceschini", "basis": "CHP-7.pdf physical p.37"}]},
    ),
    statement(
        "st-chp7-p199-v-wars-renew-italys-politics",
        6, 6, "wars_brought_italy_into_international_politics",
        "Haskell says several complex wars brought Italy back to the forefront of international politics, broke down its isolation further, and disrupted a status quo that had remained largely unaltered for nearly 150 years.",
        "The antecedent and exact extent of this isolation and the status quo are not defined. Keep nearly 150 years approximate and do not enumerate the wars from this segment.",
        subject="cand-7276", obj="cand-3461",
        mentioned=["cand-7276", "cand-7277", "cand-3461"],
    ),
    statement(
        "st-chp7-p199-v-vienna-saved-1683",
        7, 7, "reported_saved_from",
        "Haskell states that Vienna was saved from the Turks in 1683.",
        "The agent, battle, and particular force responsible for saving Vienna are not identified in this sentence.",
        subject="cand-2772", obj="cand-7153", mentioned=["cand-2772", "cand-7153"],
    ),
    statement(
        "st-chp7-p199-v-venice-joined-league-1684",
        7, 7, "joined_alliance",
        "Haskell says Venice joined a Holy League in 1684.",
        "Venice is the political actor in this diplomatic context; the source does not give its formal polity name.",
        subject="cand-7278", obj="cand-7279",
        mentioned=["cand-7278", "cand-7279"],
    ),
    statement(
        "st-chp7-p199-v-league-with-holy-roman-empire",
        7, 7, "alliance_named_with",
        "Haskell names the Holy Roman Empire as a partner in the Holy League joined by Venice.",
        "Record the wording as an alliance-partner statement; do not infer a separate accession date or a more detailed treaty structure.",
        subject="cand-7279", obj="cand-6994",
        mentioned=["cand-7279", "cand-6994", "cand-7278"],
    ),
    statement(
        "st-chp7-p199-v-league-with-polish-king",
        7, 7, "alliance_named_with",
        "Haskell names the King of Poland as a partner in the Holy League joined by Venice.",
        "The monarch is named only by title here. Identity with an index candidate remains for S3.",
        subject="cand-7279", obj="cand-7280",
        mentioned=["cand-7279", "cand-7280", "cand-7278"],
    ),
    statement(
        "st-chp7-p199-v-open-then-came-the",
        7, 7, "open_chronological_continuation",
        "Haskell begins the next chronological clause with Then came the; its event name is not complete in this segment.",
        "Keep the clause open for the next source segment and do not create a completed event statement from this fragment.",
        extra={
            "continuation_status": "open",
            "continuation_expected_segment_id": NEXT_SEGMENT_ID,
            "continuation_note": "The next source segment begins with the completion of the open clause; process it in source order.",
        },
    ),
]

existing_statement_ids = {row["statement_id"] for row in statement_rows}
planned_statement_ids = {row["statement_id"] for row in statements}
if len(planned_statement_ids) != len(statements) or planned_statement_ids & existing_statement_ids:
    raise SystemExit("statement IDs are duplicated")
available_candidate_ids = existing_candidate_ids | new_candidate_ids

line_offsets = {}
offset = 0
for number in range(LINE_START, LINE_END + 1):
    line_offsets[number] = offset
    offset += len(source_lines[number - 1]) + 1

new_mentions = []
for number, (surface, candidate_id, note, lines) in enumerate(mention_specs, 1):
    if candidate_id not in available_candidate_ids:
        raise SystemExit(f"mention references missing candidate: {surface!r} -> {candidate_id}")
    pattern = re.compile(r"(?<!\w)" + re.escape(surface) + r"(?!\w)", re.IGNORECASE)
    spans = []
    for line_number in lines:
        if line_number not in line_offsets:
            raise SystemExit(f"mention line outside segment: {surface!r}, L{line_number}")
        for match in pattern.finditer(source_lines[line_number - 1]):
            start = line_offsets[line_number] + match.start()
            end = line_offsets[line_number] + match.end()
            spans.append((start, end))
    if not spans:
        raise SystemExit(f"mention text not found: {surface!r} on lines {lines}")
    for occurrence, (start, end) in enumerate(spans, 1):
        mention_id = f"m-chp7-p199-v-{number:03d}-{occurrence:02d}"
        if any(row["mention_id"] == mention_id for row in mention_rows):
            raise SystemExit(f"mention ID already exists: {mention_id}")
        if segment_text[start:end].casefold() != surface.casefold():
            raise SystemExit(f"mention offsets do not recover source text: {surface!r}")
        new_mentions.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT_ID,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        })

new_mentions.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"]), row["candidate_id"]))
for number, row in enumerate(new_mentions, 1):
    row["mention_id"] = f"m-chp7-p199-v-{number:03d}"
    if any(existing["mention_id"] == row["mention_id"] for existing in mention_rows):
        raise SystemExit(f"mention ID already exists: {row['mention_id']}")

# No two candidate links may claim the exact same surface span. Nested spans
# are allowed when a full phrase and its independently meaningful entity occur.
claimed_spans = {}
for row in new_mentions:
    span = (row["start_char"], row["end_char"])
    prior = claimed_spans.get(span)
    if prior and prior != row["candidate_id"]:
        raise SystemExit(f"one exact span maps to two candidates: {span}, {prior}, {row['candidate_id']}")
    claimed_spans[span] = row["candidate_id"]

for row in statements:
    q = row["qualifiers"]
    excerpt = "\n".join(source_lines[q["source_line_start"] - 1 : q["source_line_end"]])
    if row["original_quote"] not in excerpt:
        raise SystemExit(f"statement quote does not occur in source excerpt: {row['statement_id']}")
    for candidate_id in q.get("mentioned_candidate_ids", []):
        if candidate_id not in available_candidate_ids:
            raise SystemExit(f"statement references missing candidate: {row['statement_id']} -> {candidate_id}")

updated_coverage = []
for row in coverage_rows:
    row = dict(row)
    if row["segment_id"] == SEGMENT_ID:
        row.update({
            "disposition": "reviewed",
            "migration_status": "partial",
            "source_line_ranges": "L3-7",
            "note": "p.199 section V body read against CHP-7.pdf physical p.37 and migrated. Page image confirms Franceschini where S0 OCR reads Francéschini; source unchanged. Final clause Then came the remains open for the next source segment L9-18.",
        })
    updated_coverage.append(row)

preview = {
    "mode": "dry-run",
    "segment": SEGMENT_ID,
    "next_segment": NEXT_SEGMENT_ID,
    "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions),
    "new_statements": len(statements),
    "coverage": "reviewed/partial",
    "ocr_correction": "Francéschini -> Franceschini, S2 note only",
    "statement_ids": [row["statement_id"] for row in statements],
    "mention_preview": [
        {"surface": row["surface_form"], "candidate_id": row["candidate_id"], "start_char": row["start_char"], "end_char": row["end_char"]}
        for row in new_mentions
    ],
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
if not parser.parse_args().apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

backup_suffix = ".bak-s2-chp7-p199-sec-v-l3-7-20260930"
for path in (CANDIDATE_PATH, MENTION_PATH, STATEMENT_PATH, COVERAGE_PATH):
    backup = path.with_name(path.name + backup_suffix)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)


def write_csv_atomic(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


candidate_rows.extend(new_candidates)
mention_rows.extend(new_mentions)
statement_rows.extend(statements)
write_csv_atomic(CANDIDATE_PATH, candidate_fields, candidate_rows)
write_csv_atomic(MENTION_PATH, mention_fields, mention_rows)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=STATEMENT_PATH.parent, delete=False, suffix=".tmp") as stream:
    for row in statement_rows:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    temporary = Path(stream.name)
temporary.replace(STATEMENT_PATH)
write_csv_atomic(COVERAGE_PATH, coverage_fields, updated_coverage)

preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
