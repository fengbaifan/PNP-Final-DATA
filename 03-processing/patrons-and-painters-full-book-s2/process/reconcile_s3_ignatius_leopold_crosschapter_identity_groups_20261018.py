from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import register_s4_person_endpoints_assereto_barelli_baretti_bartoli_basadonna_bassi_20261017 as helper  # noqa: E402

sync = helper.base.sync
process_sync = helper.base.process_sync
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
ENTITY = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-18"
ANCHOR = "s3-ignatius-leopold-crosschapter-groups-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"

IGNATIUS_GROUP = "new-person:st-ignatius-jesuit-founder-20261018"
PIETRO_GROUP = "new-person:pietro-leopoldo-grand-duke-of-tuscany-20261018"
LEOPOLD_GROUP = "new-person:leopold-i-holy-roman-emperor-20261018"
OLD_PIETRO_GROUP = "new-person:1767-archduke-austria-catalogue-exhibition-64bf9475e7"

REVIEWS = {
    "cand-1309": {
        "decision": "undecided", "group": IGNATIUS_GROUP,
        "note": (
            "第3章p.64称Ignatius为两位耶稣会士之一；p.89–91反复称St Ignatius并明言礼拜堂供奉的是该运动的创立者；"
            "第20章后记p.399又称St Ignatius本人委托Nadal默想书。Vatican对耶稣会的说明将创立者称为St Ignatius of Loyola，"
            "与书内人物及跨章提及相符。无同类型既有KU，改为一个书内人物new组；外证仅用于身份消歧，不验证Haskell转述的委托或影响断言。"
        ),
        "external": {
            "source": "Vatican, Congregation for Catholic Education",
            "id": "https://www.vatican.va/roman_curia/congregations/ccatheduc/documents/rc_con_ccatheduc_doc_20021119_press-release_en.html",
            "note": (
                "Identity comparison only: the Vatican page identifies St Ignatius of Loyola as the founder of the Jesuits. "
                "Compared with Haskell ch.3 pp.64, 89–91 and ch.20 p.399, which refer to Ignatius/St Ignatius as a Jesuit "
                "and founder of the movement. This supports person identity only, not Haskell’s account of the Nadal book commission."
            ),
        },
    },
    "cand-1397": {
        "decision": "undecided", "group": PIETRO_GROUP,
        "note": (
            "第15章p.366在1777年及其后数年的Prato della Valle叙述中称出资者为Grand Duke of Tuscany；索引L.csv#54列作"
            "Leopold I, Grand Duke of Tuscany。第8章注3的1767年展览题名则写Pietro Leopoldo, Arciduca d’Austria。"
            "Treccani《意大利人传记辞典》确认Pietro Leopoldo自1765年任托斯卡纳大公，后为皇帝Leopold II；"
            "据此与cand-8097组成同一Pietro Leopoldo人物new组。与cand-1398所指1658–1705年在位的HRE Leopold I区分。"
            "无同类型既有KU；外证仅用于身份，不验证其资助雕像的书内断言。"
        ),
        "external": {
            "source": "Treccani, Dizionario Biografico degli Italiani",
            "id": "https://www.treccani.it/enciclopedia/pietro-leopoldo-d-asburgo-lorena-granduca-di-toscana-poi-imperatore-del-sacro-romano-impero-come-leopoldo-ii_%28Dizionario-Biografico%29/",
            "note": (
                "Identity comparison only: Treccani DBI identifies Pietro Leopoldo d’Asburgo-Lorena as Grand Duke of Tuscany, "
                "later Emperor Leopold II, and records his Tuscan reign from 1765. Compared with Haskell ch.15 p.366 and index "
                "L.csv#54, and ch.8 note 3’s 1767 catalogue title naming Pietro Leopoldo. This distinguishes him from the earlier "
                "Holy Roman Emperor Leopold I; it does not verify the statue-payment claim."
            ),
        },
    },
    "cand-1398": {
        "decision": "undecided", "group": LEOPOLD_GROUP,
        "note": (
            "第7章p.193正文称Emperor Leopold I，并明确记其统治期为1658–1705；索引L.csv#55将该全名定位于同页。"
            "Deutsche Biographie / GND 118571869记Leopold I生于1640年、卒于1705年，并任皇帝（1658–1705）。"
            "现有同类型KU中无此人，改为独立new人物组；他与托斯卡纳大公Pietro Leopoldo（cand-1397、cand-8097）分开。"
            "外证只支持身份消歧，不扩大Haskell的赞助或委托叙述。"
        ),
        "external": {
            "source": "Deutsche Biographie / GND",
            "id": "118571869",
            "note": (
                "Identity comparison only: Deutsche Biographie, ‘Leopold I,’ gives GND 118571869, dates 1640–1705, "
                "and Holy Roman Emperor 1658–1705. Compared with Haskell ch.7 p.193 and index L.csv#55. "
                "This record identifies the earlier Emperor Leopold I, not Pietro Leopoldo of Tuscany."
            ),
        },
    },
}


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False) as handle:
        temp = Path(handle.name)
        handle.write(content)
    try:
        temp.replace(path)
    finally:
        if temp.exists():
            temp.unlink()


def with_bom(text: str, original: bytes) -> bytes:
    raw = text.encode("utf-8")
    return b"\xef\xbb\xbf" + raw if original.startswith(b"\xef\xbb\xbf") else raw


def has_quote(file: str, quote: str) -> bool:
    source = (ROOT / file).read_text(encoding="utf-8-sig")
    return re.sub(r"\s+", " ", quote) in re.sub(r"\s+", " ", source)


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve three cross-chapter person identity groups for S3.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    fields, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    _, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    main_rows = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    manifest_by_ku = {row["ku_id"]: row for row in manifest}

    # Pin the source anchors, index assignments, and identity boundaries before changing rows.
    expected = {
        "cand-1309": ("I.csv#0", "Ignatius, St"),
        "cand-1397": ("L.csv#54", "Leopold I, Grand Duke of Tuscany"),
        "cand-1398": ("L.csv#55", "Leopold I, Holy Roman Emperor"),
        "cand-8097": ("", "Pietro Leopoldo, Archduke of Austria, named in the 1767 exhibition catalogue title"),
    }
    for candidate_id, (entry, canonical) in expected.items():
        candidate = candidate_by_id[candidate_id]
        assert candidate.get("suggested_type") == "person"
        assert candidate.get("index_entry_id", "") == entry
        assert candidate.get("canonical_name") == canonical
        assert candidate_id in main_rows

    assert main_rows["cand-1309"].get("decision") == "undecided" and not main_rows["cand-1309"].get("ku_id")
    assert main_rows["cand-1397"].get("decision") == "undecided" and not main_rows["cand-1397"].get("ku_id")
    assert main_rows["cand-1398"].get("decision") == "undecided" and not main_rows["cand-1398"].get("ku_id")
    assert main_rows["cand-8097"].get("decision") == "new" and not main_rows["cand-8097"].get("ku_id")
    assert sync.get_group(main_rows["cand-8097"].get("resolution_note", "")) == OLD_PIETRO_GROUP

    # No existing same-type KU represents these identities; the Cardinal Leopoldo de' Medici KU is distinct.
    person_kus = {row["ku_id"] for row in manifest if row.get("type") == "person"}
    assert "units/persons/leopoldo-de-medici" in person_kus
    for ku_id in ("units/persons/st-ignatius", "units/persons/ignatius-of-loyola",
                  "units/persons/pietro-leopoldo", "units/persons/leopold-i-holy-roman-emperor"):
        assert ku_id not in person_kus

    sources = [
        ("02-sources/02-Markdown/03_CHP-3_sec_i.md", "two great Jesuits, Ignatius and Francis Xavier"),
        ("02-sources/02-Markdown/03_CHP-3_sec_iv.md", "dedicated to the founder of the movement"),
        ("02-sources/02-Markdown/20_CHP-20Postscript.md", "which had been commissioned by St Ignatius himself"),
        ("02-sources/02-Markdown/15_CHP-15_sec_ii.md", "The Grand Duke of Tuscany paid for two—Petrarch and Galileo"),
        ("02-sources/02-Markdown/08_CHP-8_sec_ii.md", "Pietro Leopoldo Arciduca d'Austria"),
        ("02-sources/02-Markdown/07_CHP-7_sec_iv.md", "the Emperor Leopold I"),
        ("02-sources/02-Markdown/07_CHP-7_sec_iv.md", "Leopold, who ruled from 1658 to 1705"),
    ]
    assert all(has_quote(file, quote) for file, quote in sources)

    external_ids = {"cand-1309", "cand-1397", "cand-1398"}
    assert not any(row.get("candidate_id") in external_ids and row.get("external_source") for row in alignments)
    assert not any(row.get("candidate_id") == "cand-8097" and row.get("external_source") for row in alignments)

    statements = [
        json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct_relations = {
        row["statement_id"] for row in statements
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and row.get("subject_candidate_id") in {"cand-1309", "cand-1397", "cand-1398", "cand-8097"}
        or (row.get("qualifiers") or {}).get("relation_candidate") is True
        and row.get("object_candidate_id") in {"cand-1309", "cand-1397", "cand-1398", "cand-8097"}
    }
    assert len(direct_relations) == 14

    revised = [dict(row) for row in alignments]
    row_by_id = {row["candidate_id"]: row for row in revised if row.get("candidate_id") and not row.get("external_source")}
    group_for = {"cand-1309": IGNATIUS_GROUP, "cand-1397": PIETRO_GROUP, "cand-1398": LEOPOLD_GROUP}
    for candidate_id, review in REVIEWS.items():
        row = row_by_id[candidate_id]
        previous = row.get("resolution_note", "")
        group = review["group"]
        if candidate_id == "cand-1397":
            index_ref = "index_entry=L.csv#54;index_pages=366,371;"
        elif candidate_id == "cand-1398":
            index_ref = "index_entry=L.csv#55;index_pages=193;"
        else:
            index_ref = "index_entry=I.csv#0;index_pages=64;"
        row.update(
            decision="new", ku_id="", accessed_date=DATE, process_ref=PROCESS_REF,
            resolution_note=(
                f"source_ref=candidate={candidate_id};{index_ref}group={group}; "
                f"Prior S3 undecided note preserved: {previous} "
                f"S3 cross-chapter person identity review ({DATE}): {review['note']}"
            ),
        )

    # Merge the two Tuscany candidates into one active new group while preserving the earlier group token.
    pietro = row_by_id["cand-8097"]
    previous_pietro = pietro.get("resolution_note", "")
    pietro.update(
        accessed_date=DATE, process_ref=PROCESS_REF,
        resolution_note=(
            f"source_ref=entity-candidates.csv#cand-8097;candidate_source_ref=chp-8:08_CHP-8_sec_ii:l372-461#L459;"
            f"group={PIETRO_GROUP}; Prior S3 decision and group preserved after correction: {previous_pietro} "
            "S3 cross-chapter person identity review (2026-10-18): this catalogue-title candidate names Pietro Leopoldo, "
            "Archduke of Austria. Treccani DBI identifies Pietro Leopoldo as Grand Duke of Tuscany from 1765 and later Emperor "
            "Leopold II; the 1777–81 Grand Duke in cand-1397 is the same person. Keep separate from Emperor Leopold I (cand-1398)."
        ),
    )

    next_id = max(
        (int(match.group(1)) for row in revised if (match := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))),
        default=0,
    ) + 1
    for candidate_id in sorted(external_ids, key=lambda value: int(value.split("-")[1])):
        identity = REVIEWS[candidate_id]["external"]
        external_row = {field: "" for field in fields}
        external_row.update({
            "alignment_id": f"aln-{next_id:05d}", "candidate_id": candidate_id,
            "external_source": identity["source"], "external_id": identity["id"],
            "decision": "new", "accessed_date": DATE, "process_ref": PROCESS_REF,
            "resolution_note": identity["note"],
        })
        revised.append(external_row)
        next_id += 1

    decision_rows = [row for row in revised if not row.get("external_source")]
    stats = sync.summarize_by_type(candidates, decision_rows)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    before = sync.summarize_by_type(candidates, [row for row in alignments if not row.get("external_source")])
    before_totals = {key: sum(item[key] for item in before.values()) for key in next(iter(before.values()))}
    assert totals["new_candidates"] == before_totals["new_candidates"] + 3
    assert totals["new_groups"] == before_totals["new_groups"] + 2
    assert totals["undecided"] == before_totals["undecided"] - 3
    assert totals["pending_groups"] == before_totals["pending_groups"] + 2
    assert totals["pending_members"] == before_totals["pending_members"] + 3

    group_members = {}
    for row in decision_rows:
        if row.get("decision") == "new":
            group = sync.get_group(row.get("resolution_note", ""))
            if group:
                group_members.setdefault(group, []).append(row["candidate_id"])
    assert set(group_members[PIETRO_GROUP]) == {"cand-1397", "cand-8097"}
    assert group_members[IGNATIUS_GROUP] == ["cand-1309"]
    assert group_members[LEOPOLD_GROUP] == ["cand-1398"]
    assert all(candidate_by_id[cid].get("suggested_type") == "person"
               for group in (IGNATIUS_GROUP, PIETRO_GROUP, LEOPOLD_GROUP)
               for cid in group_members[group])

    process_text = process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    process_text = re.sub(r"^(更新日期：).*?$", rf"\g<1>{DATE}。", process_text, count=1, flags=re.M)
    expected_type_total = (
        f"| **合计** | **{sync.fmt(totals['total'])}** | **{sync.fmt(totals['same_candidates'])}** "
        f"| **{sync.fmt(totals['new_groups'])} / {sync.fmt(totals['new_candidates'])}** |"
    )
    assert expected_type_total in process_text
    current_summary = (
        "48 项 S1 明确排除均保留为 `excluded`（未分类 43、人物 3、作品 1、术语 1）；另有 52 项按 S3 的对象类型／独立性判断排除"
        "（档案文献 18、家族 1、人物 4、术语 1、作品 28）。曾有一条作品占位候选 `cand-10059` 在类型建议中误判为 `same`；"
        "合并时按其 S1 排除状态恢复为 `excluded`。其所指的真实作品由候选 `cand-4048` 承接。\n\n"
        f"人物冲突 {stats['person']['conflict']} 项、作品冲突 {stats['work']['conflict']} 项；冲突两侧和来源位置均留在候选行，不强选一方。"
        f"{sync.fmt(totals['undecided'])} 项 `undecided` 各自保留对象、版本、身份、类型或来源锚点不足的理由与后续去向；其中 "
        f"{sync.fmt(stats['未分类']['undecided'])} 项仍为未分类类型，等待类型证据，不强塞入现有类。所有 {sync.fmt(totals['total'])} 个候选各有且仅有一条 `external_source` 为空的当前决定；"
        f"{len(revised) - len(decision_rows)} 条外部身份记录另行保留。same 的 {sync.fmt(totals['same_candidates'])} 条候选指向 "
        f"{sync.fmt(totals['same_kus'])} 个既有 KU；new 候选组成 {sync.fmt(totals['new_groups'])} 个类型内身份组，共 "
        f"{sync.fmt(totals['new_candidates'])} 条映射。S4 按整组登记，当前没有组内部分登记或类型不符映射；未登记组保留在 S4 待办中。"
        "此处收口的是 S3 决定与可追溯去向，冲突和待证身份问题本身未解决。"
    )
    pattern = re.compile(r"48 项 S1 明确排除均保留为 `excluded`.*?此处收口的是 S3 决定与可追溯去向，冲突和待证身份问题本身未解决。", re.S)
    process_text, n = pattern.subn(current_summary, process_text, count=1)
    assert n == 1
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3人物跨章身份组：St Ignatius与两位Leopold（{DATE}）\n\n"
        "- cand-1309（I.csv#0，Ignatius, St）由undecided改为new，group=`new-person:st-ignatius-jesuit-founder-20261018`。"
        "第3章p.64、p.89–91将Ignatius置于耶稣会与其创立者语境，第20章后记p.399再次称St Ignatius；Vatican身份记录支持其为St Ignatius of Loyola。"
        "未发现同类型既有人物KU。\n"
        "- cand-1397（L.csv#54，Leopold I, Grand Duke of Tuscany）与cand-8097（第8章注3所引1767年展览题名中的Pietro Leopoldo）"
        "归为一个new人物组`new-person:pietro-leopoldo-grand-duke-of-tuscany-20261018`。第15章p.366的1777年后语境称Grand Duke of Tuscany；"
        "Treccani DBI记录Pietro Leopoldo自1765年任托斯卡纳大公、后来为皇帝Leopold II。该组与HRE Leopold I分开。\n"
        "- cand-1398（L.csv#55，Leopold I, Holy Roman Emperor）由undecided改为new，group=`new-person:leopold-i-holy-roman-emperor-20261018`。"
        "第7章p.193明确其1658–1705年统治期；Deutsche Biographie / GND 118571869身份吻合，现无同类型KU。\n\n"
        "外部身份来源："
        "[Vatican St Ignatius](https://www.vatican.va/roman_curia/congregations/ccatheduc/documents/rc_con_ccatheduc_doc_20021119_press-release_en.html)、"
        "[Treccani DBI Pietro Leopoldo](https://www.treccani.it/enciclopedia/pietro-leopoldo-d-asburgo-lorena-granduca-di-toscana-poi-imperatore-del-sacro-romano-impero-come-leopoldo-ii_%28Dizionario-Biografico%29/)、"
        "[Deutsche Biographie Leopold I](https://www.deutsche-biographie.de/gnd118571869.html?language=en)。外证仅用于身份消歧；14条直接S2关系候选留待S6；本批不新增KU或正式关系。"
    )

    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest))
    result_text = re.sub(r"^(更新日期：).*?$", rf"\g<1>{DATE}。", result_text, count=1, flags=re.M)
    alignment_total = len(revised)
    external_total = alignment_total - len(decision_rows)
    alignment_row = f"| [全书对齐](../tables/alignment.csv) | {sync.fmt(alignment_total)} 条：{sync.fmt(len(decision_rows))} 条候选决定记录及 {sync.fmt(external_total)} 条外部身份记录；候选决定数见下表 |"
    result_text, n = re.subn(r"^\| \[全书对齐\]\(\.\./tables/alignment\.csv\) \|.*$", alignment_row, result_text, count=1, flags=re.M)
    assert n == 1
    result_text += (
        f"\n\n### S3人物跨章身份组：St Ignatius与两位Leopold（{DATE}）\n\n"
        "cand-1309改为St Ignatius（耶稣会创立者）的new人物组；cand-1397与cand-8097合为Pietro Leopoldo（托斯卡纳大公）一个new组；"
        "cand-1398确定为另一位、1658–1705年在位的HRE Leopold I并建独立new组。新增3条外部身份记录；共14条直接S2关系候选仍待S6。"
        "身份来源和边界见[过程记录](../../03-processing/"
        f"{TASK}/process/knowledge.md#{ANCHOR})。未创建KU或正式关系。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s3-ignatius-leopold-") as temp_name:
        stage = Path(temp_name) / "alignment.csv"
        sync.write_csv(stage, fields, revised)
        writes = {
            ALIGNMENT: stage.read_bytes(),
            PROCESS: with_bom(process_text + "\n", PROCESS.read_bytes()),
            RESULT: with_bom(result_text + "\n", RESULT.read_bytes()),
        }
    if args.dry_run:
        print(
            f"S3 dry-run passed: candidate_decisions={len(decision_rows)}; new_candidates=+3; new_groups=+2; "
            f"undecided=-3; external_identity_rows=+3; direct_relation_candidates={len(direct_relations)} unchanged; "
            "formal_relations_added=0; KU_created=0."
        )
        print(
            f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])} groups; "
            f"undecided={sync.fmt(totals['undecided'])}; external_identity_rows={sync.fmt(external_total)}; no files changed"
        )
        return 0

    originals = {path: path.read_bytes() for path in writes}
    try:
        for path, content in writes.items():
            atomic_write(path, content)
    except Exception:
        for path, content in originals.items():
            atomic_write(path, content)
        raise
    print(
        f"applied: new_candidates={sync.fmt(totals['new_candidates'])}; new_groups={sync.fmt(totals['new_groups'])}; "
        f"undecided={sync.fmt(totals['undecided'])}; external_identity_rows={sync.fmt(external_total)}; "
        f"direct_relation_candidates={len(direct_relations)} unchanged; formal_relations_added=0; KU_created=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
