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
import register_s4_person_direct_endpoints_h_section_20261018 as template  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ENRICHMENT = TABLES / "enrichment.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-18"
ANCHOR = "s4-person-direct-endpoints-n-section-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"


def src(location: str, summary: str, quote: str, file: str, span: str) -> dict:
    return {"location": location, "summary": summary, "quote": quote, "file": file, "span": span}


TARGETS = [
    {
        "primary": "cand-1736", "members": ["cand-1736"], "expected_name": "Neumann, Balthasar", "expected_pages": "296",
        "group": "new-person:balthasar-neumann-de17cb965f", "ku": "units/persons/balthasar-neumann", "card": "04-knowledge/units/persons/balthasar-neumann.md",
        "name_zh": "巴尔塔萨·诺伊曼", "name_en": "Balthasar Neumann",
        "name_rows": [("索引名", "Neumann, Balthasar", "S1（索引N.csv#16）"), ("正文姓名形式", "Balthasar Neumann", "S2（第10章p.296）")],
        "sources": [src("第10章导论；印刷页296", "Haskell称维尔茨堡宫殿由Balthasar Neumann为前任建造。", "the magnificent palace that had been built by Balthasar Neumann for his predecessors.", "02-sources/02-Markdown/10_CHP-10_intro.md", "lines 320-321; print p.296")],
        "zh": "本卡登记索引N.csv#16所列Balthasar Neumann（中文显示名为本项目工作音译）。第10章p.296称维尔茨堡的宏伟宫殿由Neumann为Greiffenklau的前任建造。",
        "en": "This card registers Balthasar Neumann under index N.csv#16; the Chinese display name is a working transliteration. Chapter 10, p.296, says Neumann built the magnificent Würzburg palace for Greiffenklau’s predecessors.",
        "context_zh": "本段对应地点端点cand-2822映射到既有[维尔茨堡宫（Residenz, Würzburg）](../places/residenz-wurzburg.md)；建造关系留待S6。",
        "context_en": "The place endpoint cand-2822 in this passage maps to the existing [Residenz, Würzburg](../places/residenz-wurzburg.md); the building relation remains for S6.",
        "relations": ["st-chp10-p296-neumann-builds-residenz"],
        "endpoints": {"st-chp10-p296-neumann-builds-residenz": "the_wurzburg_residenz_was_built_by_balthasar_neumann_for_its_predecessors"},
    },
    {
        "primary": "cand-1764", "members": ["cand-1764"], "expected_name": "Noyers, François Sublet de", "expected_pages": "112",
        "group": "new-person:de-francois-noyers-sublet-c3e504e823", "ku": "units/persons/francois-sublet-de-noyers", "card": "04-knowledge/units/persons/francois-sublet-de-noyers.md",
        "name_zh": "弗朗索瓦·苏布莱·德·努瓦耶", "name_en": "François Sublet de Noyers",
        "name_rows": [("索引名", "Noyers, François Sublet de", "S1（索引N.csv#44）"), ("正文称谓", "M. de Noyers", "S2（第4章第II节p.112）")],
        "sources": [src("第4章第II节；印刷页112", "Haskell称Cassiano曾被法国王室建筑总监M. de Noyers赞为贤德人士中的领袖。", "M. de Noyers, Surintendant des Bâtiments of the King of France, ‘icy en un’estime singulière et tient lieu du chef des vertueux’.", "02-sources/02-Markdown/04_CHP-4_sec_ii.md", "lines 155-156; print p.112")],
        "zh": "本卡登记索引N.csv#44所列François Sublet de Noyers（中文显示名为本项目工作音译）。第4章p.112正文称M. de Noyers为法国国王的建筑总监，并转述其对Cassiano的评价；此处依据本书索引与正文，不补充外部身份信息。",
        "en": "This card registers François Sublet de Noyers under index N.csv#44; the Chinese display name is a working transliteration. Chapter 4, p.112, calls M. de Noyers superintendent of the King of France’s buildings and quotes his praise of Cassiano. The identification follows the book’s index and text; no external identity details are added.",
        "context_zh": "关系候选的另一端cand-2036映射到既有人物[Cassiano dal Pozzo](cassiano-dal-pozzo.md)；评价性引文及其关系类型留待S6。",
        "context_en": "The other endpoint, cand-2036, maps to the existing person [Cassiano dal Pozzo](cassiano-dal-pozzo.md); the evaluative quotation and relation type remain for S6.",
        "relations": ["st-chp4-sec-ii-p112-denoyers-assessment-of-cassiano"],
        "endpoints": {"st-chp4-sec-ii-p112-denoyers-assessment-of-cassiano": "described_cassiano_as_held_in_singular_esteem"},
    },
    {
        "primary": "cand-1742", "members": ["cand-1742"], "expected_name": "Noailles, Maréchal de", "expected_pages": "200",
        "group": "new-person:de-marechal-noailles-5dbb196acf", "ku": "units/persons/marechal-de-noailles", "card": "04-knowledge/units/persons/marechal-de-noailles.md",
        "name_zh": "诺阿耶元帅", "name_en": "Maréchal de Noailles",
        "name_rows": [("索引名", "Noailles, Maréchal de", "S1（索引N.csv#22）"), ("正文称谓", "the French Maréchal de Noailles", "S2（第7章第V节p.200）")],
        "sources": [src("第7章第V节；印刷页200", "Haskell称法国元帅Maréchal de Noailles抵达热那亚后说服Gregorio de Ferrari前往马赛为其作画。", "the French Maréchal de Noailles who arrived soon after and was more successful in persuading Gregorio de Ferrari to come to Marseilles and paint some pictures for him there", "02-sources/02-Markdown/07_CHP-7_sec_v.md", "line 11; print p.200")],
        "zh": "本卡按索引N.csv#22及第7章p.200登记书内称为Maréchal de Noailles的法国元帅（中文显示名为工作音译）。该段未提供其名字；本卡保留书内称谓，不对应到某一外部人物。",
        "en": "This card registers the French marshal called Maréchal de Noailles in index N.csv#22 and chapter 7, p.200; the Chinese display name is a working transliteration. The passage gives no given name, so the card preserves the book’s designation without matching him to an external individual.",
        "context_zh": "作品端点cand-7298仍为身份未定的画作组；不补作品名或外部人物身份。",
        "context_en": "The work endpoint cand-7298 remains an unidentified picture group; no title or external personal identity is supplied.",
        "relations": ["st-chp7-p200-v-noailles-secures-de-ferrari-at-marseilles"],
        "endpoints": {"st-chp7-p200-v-noailles-secures-de-ferrari-at-marseilles": "persuaded_artist_to_paint_for_him"},
        "s3_note": "S3 qualification (2026-10-18): the source identifies this person by the title Maréchal and surname Noailles in an event-specific context; it gives no given name. The new group is source-local and is not matched to an external individual.",
    },
    {
        "primary": "cand-1749", "members": ["cand-1749"], "expected_name": "Nomé, François ('Monsù Desiderio')", "expected_pages": "213",
        "group": "new-person:desiderio-monsu-francois-frenchman-nome-fr-31a920c8cc", "ku": "units/persons/francois-nome-monsu-desiderio", "card": "04-knowledge/units/persons/francois-nome-monsu-desiderio.md",
        "name_zh": "弗朗索瓦·诺梅", "name_en": "François Nomé (Monsù Desiderio)",
        "name_rows": [("索引名", "Nomé, François ('Monsù Desiderio')", "S1（索引N.csv#29）"), ("正文姓名与称号", "François Nome; Monsù Desiderio", "S2（第8章第I节p.213）")],
        "sources": [src("第8章第I节；印刷页213", "Haskell称François Nome通常被称为Monsù Desiderio，并在del Rosso家族收藏清单中被描述为Lorenese。", "Frenchman François Nome, generally known as ‘Monsù Desiderio’, and described in their inventory as ‘Lorenese’.", "02-sources/02-Markdown/08_CHP-8_sec_i.md", "line 111; print p.213")],
        "zh": "本卡将索引N.csv#29的Nomé, François（Monsù Desiderio）与第8章p.213的François Nome及称号按同一S3书内身份组登记。Haskell称其为Frenchman，并报告del Rosso收藏清单将其描述为Lorenese；这些称谓仅按本书记载保存。",
        "en": "This card registers the index form Nomé, François (Monsù Desiderio) with the François Nome and sobriquet in chapter 8, p.213, under the same S3 source-local identity group. Haskell calls him Frenchman and reports that the del Rosso inventory described him as Lorenese; these designations are retained as the book’s account.",
        "context_zh": "对应书目记录端点cand-7500已判为new但尚未登记；库存描述及其关系留待S6。",
        "context_en": "The corresponding bibliographic-record endpoint cand-7500 is decided new but not yet registered; the inventory description and relation remain for S6.",
        "relations": ["st-chp8-p213-nome-inventory-described-as-lorenese"],
        "endpoints": {"st-chp8-p213-nome-inventory-described-as-lorenese": "del_rosso_inventory_described_nome_as_lorenese"},
    },
    {
        "primary": "cand-1731", "members": ["cand-1731"], "expected_name": "Negri, Pietro", "expected_pages": "219, 294",
        "group": "new-person:negri-pietro-d97f9be175", "ku": "units/persons/pietro-negri", "card": "04-knowledge/units/persons/pietro-negri.md",
        "name_zh": "彼得罗·内格里", "name_en": "Pietro Negri",
        "name_rows": [("索引名", "Negri, Pietro", "S1（索引N.csv#11）"), ("正文姓名形式", "Pietro Negri", "S2（第8章p.219；第10章p.294）")],
        "sources": [
            src("第8章第II节；印刷页219", "Haskell称威尼斯画家Pietro Negri曾为San Rocco学校绘制纪念1630年瘟疫停止的作品，并参加1677年竞赛。", "Pietro Negri of Venice, who had followed Zanchi in painting for the Scuola di San Rocco a picture to commemorate the cessation of the plague of 1630", "02-sources/02-Markdown/08_CHP-8_sec_ii.md", "lines 88-89; print p.219"),
            src("第10章导论；印刷页294", "Haskell另称Pietro Negri为Zanchi的学生，并记述奥古斯都强者购藏其所作的第二个版本。", "another Venetian artist, Pietro Negri, a pupil of Zanchi", "02-sources/02-Markdown/10_CHP-10_intro.md", "lines 294-296; print p.294"),
        ],
        "zh": "本卡登记索引N.csv#11所列Pietro Negri（中文显示名为本项目工作音译）。第8章p.219将他称为威尼斯画家，并记其为San Rocco学校作画及参加1677年《挪亚献祭》竞赛；第10章p.294又称他为Zanchi学生。两章指称按S3身份组记录。",
        "en": "This card registers Pietro Negri under index N.csv#11; the Chinese display name is a working transliteration. Chapter 8, p.219, calls him a Venetian painter and records his work for the Scuola di San Rocco and his entry in the 1677 Sacrifice of Noah competition; chapter 10, p.294, also identifies him as a pupil of Zanchi. The chapter references follow the S3 identity group.",
        "context_zh": "cand-2351仍为待登记的新机构组，cand-7679仍为未决事件；两条关系候选留待S6。",
        "context_en": "cand-2351 remains an unregistered new institution group, and cand-7679 remains an undecided event; both relation candidates remain for S6.",
        "relations": ["st-chp8-p219-negri-san-rocco-picture", "st-chp8-p219-negri-enters-noah-competition"],
        "endpoints": {
            "st-chp8-p219-negri-san-rocco-picture": "painting_for_institution",
            "st-chp8-p219-negri-enters-noah-competition": "submitted_sketch_for_competition",
        },
    },
    {
        "primary": "cand-1735", "members": ["cand-1735"], "expected_name": "Neri, Vincenzo", "expected_pages": "136",
        "group": "new-person:neri-vincenzo-94f1ade31a", "ku": "units/persons/vincenzo-neri", "card": "04-knowledge/units/persons/vincenzo-neri.md",
        "name_zh": "温琴佐·内里", "name_en": "Vincenzo Neri",
        "name_rows": [("索引名", "Neri, Vincenzo", "S1（索引N.csv#15）"), ("正文姓名形式", "Vincenzo Neri", "S2（第5章第III节p.136）")],
        "sources": [src("第5章第III节；印刷页136", "Haskell称医生Vincenzo Neri与一群朋友被Cerquozzi绘入其一幅重要作品。", "the doctor Vincenzo Neri whom with a group of other friends he immortalised in one of his finest paintings (Plate 22a)", "02-sources/02-Markdown/05_CHP-5_sec_iii.md", "line 41; print p.136")],
        "zh": "本卡登记索引N.csv#15所列Vincenzo Neri（中文显示名为本项目工作音译）。第5章p.136称他为医生，并记Cerquozzi将他与其他朋友绘入一件作品（图版22a）。",
        "en": "This card registers Vincenzo Neri under index N.csv#15; the Chinese display name is a working transliteration. Chapter 5, p.136, identifies him as a doctor and says Cerquozzi depicted him with other friends in a painting (Plate 22a).",
        "context_zh": "作品端点cand-6137已有new身份组但尚未登记；作品归属表述留待S6。",
        "context_en": "Work endpoint cand-6137 has a new identity group but is not yet registered; the attribution remains for S6.",
        "relations": ["st-chp5-p136-neri-and-friends-immortalised-in-plate-22a"],
        "endpoints": {"st-chp5-p136-neri-and-friends-immortalised-in-plate-22a": "depicts"},
    },
    {
        "primary": "cand-1756", "members": ["cand-1756"], "expected_name": "Novelli, Francesco", "expected_pages": "371",
        "group": "new-person:francesco-novelli-ae0651e151", "ku": "units/persons/francesco-novelli", "card": "04-knowledge/units/persons/francesco-novelli.md",
        "name_zh": "弗朗切斯科·诺韦利", "name_en": "Francesco Novelli",
        "name_rows": [("索引名", "Novelli, Francesco", "S1（索引N.csv#36）"), ("正文姓名形式", "Francesco Novelli", "S2（第15章第II节p.371）")],
        "sources": [src("第15章第II节；印刷页371", "Haskell称Dominique De Non收藏Zanetti版画（包括伦勃朗版画），这些版画深刻影响了De Non及其主要学生Francesco Novelli的风格。", "He bought a large proportion of Zanetti’s prints, including the Rembrandts, which had a profound effect on his own style and that of his principal pupil Francesco Novelli.", "02-sources/02-Markdown/15_CHP-15_sec_ii.md", "lines 77-78; print p.371")],
        "zh": "本卡登记索引N.csv#36所列Francesco Novelli（中文显示名为本项目工作音译）。第15章p.371称他为Dominique De Non的主要学生，并说De Non收藏的Zanetti版画对其风格产生深刻影响。该影响叙述按Haskell原文保留。",
        "en": "This card registers Francesco Novelli under index N.csv#36; the Chinese display name is a working transliteration. Chapter 15, p.371, calls him Dominique De Non’s principal pupil and says prints collected by De Non profoundly affected his style. The account remains attributed to Haskell.",
        "context_zh": "相关作品端点cand-10580仍为未决集合型作品候选；影响关系及端点粒度留待S6。",
        "context_en": "The related work endpoint cand-10580 remains an undecided collection-level work candidate; the influence relation and endpoint granularity remain for S6.",
        "relations": ["st-chp15-p371-rembrandt-prints-influenced-novelli"],
        "endpoints": {"st-chp15-p371-rembrandt-prints-influenced-novelli": "rembrandt_prints_profoundly_influenced_novelli_style"},
    },
]

CORRECTIONS = [
    {
        "candidate": "cand-1741",
        "existing_candidate": "cand-3732",
        "ku": "units/persons/benedict-nicolson",
        "statement_id": "st-chp4-intro-notes-03-nicolson-hypothesis",
        "predicate": "reported_copyist_hypothesis",
        "source_file": "02-sources/02-Markdown/04_CHP-4_intro.md",
        "source_span": "footnote 3; print p.94 n.3",
        "quote": "Benedict Nicolson plausibly suggested to me (verbally) that the error arose through a copyist substituting Romanelli for the similar word Roncalli (i.e. Pomarancio).",
        "note": "S3 correction (2026-10-18): same -> units/persons/benedict-nicolson. The indexed full/common name and p.94 n.3 source refer to the already registered Benedict Nicolson; existing same candidate cand-3732 maps his preface mentions to this KU. The prior new proposal is retained as history. The hypothesis relation remains for S6 because archive endpoint cand-5507 is undecided.",
    },
]


def make_batch_card(target: dict) -> str:
    card = template.make_card(target)
    relations = ", ".join(target["relations"])
    if relations:
        zh_display = f"直接S2候选（待S6）：{relations}。"
        en_display = f"Direct S2 relation candidates pending individual review in S6: {relations}."
    else:
        zh_display = "当前未有直接S2关系候选映射到此人物端点。"
        en_display = "S2 does not currently map this person as a direct relation-candidate endpoint."
    old = f"**English:** {zh_display}\n"
    new = f"**English:** {en_display}\n"
    assert old in card
    return card.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Correct the Nicolson identity and register seven new N-section person groups.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--refresh-cards", action="store_true")
    args = parser.parse_args()
    template.TARGETS = TARGETS
    template.DATE, template.ANCHOR, template.PROCESS_REF = DATE, ANCHOR, PROCESS_REF
    sync = template.helper.base.sync
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    main_rows = [r for r in alignments if r.get("candidate_id") and not r.get("external_source")]
    main_by_id = {r["candidate_id"]: r for r in main_rows}
    manifest_by_ku = {r["ku_id"]: r for r in manifest}
    accepted_lines = ACCEPTED.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]

    for correction in CORRECTIONS:
        row = main_by_id[correction["candidate"]]
        existing = main_by_id[correction["existing_candidate"]]
        assert row.get("decision") == "new" or (row.get("decision") == "same" and row.get("ku_id") == correction["ku"])
        assert existing.get("decision") == "same" and existing.get("ku_id") == correction["ku"]
        assert correction["ku"] in manifest_by_ku
        assert "- 04-knowledge/units/persons/benedict-nicolson.md" in accepted_lines
        existing_card = ROOT / "04-knowledge/units/persons/benedict-nicolson.md"
        assert existing_card.exists() and "Benedict Nicolson" in existing_card.read_text(encoding="utf-8-sig")
        candidate = candidate_by_id[correction["candidate"]]
        assert candidate.get("canonical_name") == "Nicolson, Benedict" and candidate.get("index_page_range") == "94n"
        source_text = (ROOT / correction["source_file"]).read_text(encoding="utf-8-sig")
        assert re.sub(r"\s+", " ", correction["quote"]) in re.sub(r"\s+", " ", source_text)
        direct = {r["statement_id"]: r for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and (r.get("subject_candidate_id") == correction["candidate"] or r.get("object_candidate_id") == correction["candidate"])}
        assert set(direct) == {correction["statement_id"]}
        assert direct[correction["statement_id"]].get("predicate") == correction["predicate"]
        if row.get("decision") == "same":
            assert correction["note"] in row.get("resolution_note", "")

    for target in TARGETS:
        candidate = candidate_by_id[target["primary"]]
        target["entry"], target["index_name"], target["pages"] = candidate["index_entry_id"], candidate["canonical_name"], candidate["index_page_range"]
        assert candidate.get("suggested_type") == "person"
        assert (candidate.get("canonical_name"), candidate.get("index_page_range")) == (target["expected_name"], target["expected_pages"])
        row = main_by_id[target["primary"]]
        assert row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == target["group"]
        assert not row.get("ku_id") or row.get("ku_id") == target["ku"]
        members = [r["candidate_id"] for r in main_rows if r.get("decision") == "new" and sync.get_group(r.get("resolution_note", "")) == target["group"]]
        assert members == target["members"]
        index_file, _ = target["entry"].split("#", 1)
        index_hits = [r for r in template.helper.base.read_index_rows(index_file) if r.get("Main Entry") == target["index_name"] and r.get("Page Numbers") == target["pages"] and not r.get("Sub-entry")]
        assert len(index_hits) == 1
        direct = {r["statement_id"]: r for r in statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and (r.get("subject_candidate_id") == target["primary"] or r.get("object_candidate_id") == target["primary"])}
        assert set(direct) == set(target["endpoints"]), (target["primary"], sorted(direct), sorted(target["endpoints"]))
        for statement_id, predicate in target["endpoints"].items():
            assert direct[statement_id].get("predicate") == predicate
        for item in target["sources"]:
            source_text = (ROOT / item["file"]).read_text(encoding="utf-8-sig")
            assert re.sub(r"\s+", " ", item["quote"]) in re.sub(r"\s+", " ", source_text), (target["primary"], item["span"])
        path = ROOT / target["card"]
        mapped = row.get("ku_id") == target["ku"]
        assert (target["ku"] in manifest_by_ku) == (target["card"] in accepted_paths) == path.exists() == mapped

    cards = {target["card"]: make_batch_card(target) for target in TARGETS}
    all_registered = (
        all(main_by_id[target["primary"]].get("ku_id") == target["ku"] for target in TARGETS)
        and all(main_by_id[correction["candidate"]].get("decision") == "same" and main_by_id[correction["candidate"]].get("ku_id") == correction["ku"] for correction in CORRECTIONS)
    )
    if all_registered:
        if args.refresh_cards:
            for target in TARGETS:
                template.atomic_write(ROOT / target["card"], template.with_bom(cards[target["card"]]))
            print("refreshed person cards: removed repeated S6 context and restored English relation summaries")
            return 0
        for target in TARGETS:
            assert (ROOT / target["card"]).read_text(encoding="utf-8-sig") == cards[target["card"]]
        print("ALREADY REGISTERED: all person groups and their source-backed name fields are recorded.")
        return 0
    assert not any(main_by_id[target["primary"]].get("ku_id") for target in TARGETS), "partial registration requires explicit reconciliation"

    before = sync.summarize_by_type(candidates, alignments)
    before_totals = {key: sum(row[key] for row in before.values()) for key in next(iter(before.values()))}
    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignments if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest, planned_accepted = list(manifest), list(accepted_lines)
    corrections_to_apply = 0
    for correction in CORRECTIONS:
        row = planned_by_id[correction["candidate"]]
        if row.get("decision") == "new":
            row["decision"], row["ku_id"], row["process_ref"] = "same", correction["ku"], PROCESS_REF
            row["resolution_note"] += " " + correction["note"]
            corrections_to_apply += 1
        else:
            assert row.get("decision") == "same" and row.get("ku_id") == correction["ku"]
    for target in TARGETS:
        row = planned_by_id[target["primary"]]
        row["ku_id"], row["process_ref"] = target["ku"], PROCESS_REF
        if target.get("s3_note"):
            row["resolution_note"] += " " + target["s3_note"]
        row["resolution_note"] += f" S4 registration ({DATE}): group {target['group']} -> {target['ku']}; source-backed person identity registration; direct S2 relation candidates remain for S6."
        planned_manifest.append({"ku_id": target["ku"], "type": "person", "canonical_name": target["name_zh"], "name_en": target["name_en"], "source_task": TASK, "card_path": target["card"]})
        planned_accepted = template.helper.base.insert_accepted(planned_accepted, target["card"])

    planned_manifest.sort(key=lambda row: row["ku_id"])
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    batch_size = len(TARGETS)
    assert totals["registered_groups"] == before_totals["registered_groups"] + batch_size
    assert totals["registered_members"] == before_totals["registered_members"] + batch_size
    assert totals["same_candidates"] == before_totals["same_candidates"] + corrections_to_apply
    assert totals["new_candidates"] == before_totals["new_candidates"] - corrections_to_apply
    assert totals["pending_groups"] == before_totals["pending_groups"] - batch_size - corrections_to_apply
    assert totals["pending_members"] == before_totals["pending_members"] - batch_size - corrections_to_apply
    assert len(planned_manifest) == len(manifest) + batch_size

    additions, card_tables = template.extract_card_fields(cards)
    name_fields = sum(len(target["name_rows"]) for target in TARGETS)
    assert card_tables == batch_size and len(additions) == name_fields and all(row.get("evidence_status") == "source_backed" for row in additions)
    enrichment_text = ENRICHMENT.read_text(encoding="utf-8-sig")
    existing = [json.loads(line) for line in enrichment_text.splitlines() if line.strip()]
    natural_keys = {(row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id", "")) for row in existing}
    existing_ids = {row.get("enrichment_id", "") for row in existing}
    max_id = max((int(match.group(1)) for value in existing_ids if (match := re.fullmatch(r"enr-(\d+)", value))), default=0)
    for i, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id+i:05d}"
        assert (row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id", "")) not in natural_keys
        assert row["enrichment_id"] not in existing_ids
    planned_enrichment = enrichment_text.rstrip("\n") + "\n" + "\n".join(json.dumps(row, ensure_ascii=False) for row in additions) + "\n"

    process_text = template.helper.base.process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3复核与S4人物直接端点登记：N索引组（{DATE}）\n\n"
    for correction in CORRECTIONS:
        process_text += f"- S3更正：`{correction['candidate']}`（索引N.csv#21，Benedict Nicolson）由new改为same → [Lionel Benedict Nicolson](../../../04-knowledge/units/persons/benedict-nicolson.md)。现有same候选`{correction['existing_candidate']}`已映射到该KU；第4章注3的姓名和语境与章前相同。原new判断及理由留在alignment行历史；直接候选`{correction['statement_id']}`仍待S6，因书信端点`cand-5507`未决。\n"
    for target in TARGETS:
        process_text += f"- `{target['primary']}`（`{target['group']}`）→ [{target['name_zh']}（{target['name_en']}）](../../../04-knowledge/{target['ku']}.md)。索引{target['entry']}（页码{target['pages']}）与对应书内页段支持source-local人物登记；直接S2关系候选{', '.join(target['relations'])}留待S6逐条裁决，不登记正式关系。\n"
    process_text += (
        f"本批S4登记{batch_size}个S3 new人物组、{batch_size}条候选映射和{name_fields}条source_backed名称字段；"
        f"{sum(len(target['relations']) for target in TARGETS) + len(CORRECTIONS)}条直接S2关系候选留待S6。"
        "Noailles按书内称谓保留为source-local身份，未补给名或外部人物匹配；Nomé称号和Negri跨章姓名按原书语境记录。"
        "本批未新增外部身份行、正式关系、来源登记或S2断言。\n\n"
        f"登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S3复核与S4人物直接端点登记：N索引组（{DATE}）\n\n"
        f"Benedict Nicolson候选cand-1741由new更正为same，复用既有Lionel Benedict Nicolson KU。另登记Balthasar Neumann、François Sublet de Noyers、Maréchal de Noailles、François Nomé、Pietro Negri、Vincenzo Neri与Francesco Novelli七个人物组；"
        f"本批{batch_size}条new候选映射、{name_fields}条source_backed名称字段及{sum(len(target['relations']) for target in TARGETS) + len(CORRECTIONS)}条直接S2关系候选。"
        f"关系均留待S6，未新增正式边；中文显示名均为工作音译。KU={len(planned_manifest)}；详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    with tempfile.TemporaryDirectory(prefix="pnp-s4-n-section-persons-") as td:
        temp = Path(td)
        alignment_stage, manifest_stage = temp / "alignment.csv", temp / "ku-manifest.csv"
        sync.write_csv(alignment_stage, alignment_fields, planned_alignments)
        sync.write_csv(manifest_stage, manifest_fields, planned_manifest)
        writes = {
            ALIGNMENT: alignment_stage.read_bytes(), MANIFEST: manifest_stage.read_bytes(),
            ENRICHMENT: template.with_bom(planned_enrichment, ENRICHMENT.read_bytes()),
            ACCEPTED: template.with_bom("\n".join(planned_accepted) + "\n", ACCEPTED.read_bytes()),
            PROCESS: template.with_bom(process_text + "\n", PROCESS.read_bytes()),
            RESULT: template.with_bom(result_text + "\n", RESULT.read_bytes()),
        }
        for target in TARGETS:
            writes[ROOT / target["card"]] = template.with_bom(cards[target["card"]])

    if args.dry_run:
        relation_count = sum(len(target["relations"]) for target in TARGETS) + len(CORRECTIONS)
        print(f"S4 dry-run passed: new_groups={batch_size}; new_candidate_mappings={batch_size}; s3_same_corrections={len(CORRECTIONS)}; name_fields={name_fields}; direct_relation_candidates={relation_count}.")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; KU={len(planned_manifest)}")
        print("formal_relations_added=0; candidate_backlog_changed=0; sources_registry_changed=0; no files changed")
        return 0

    originals = {path: path.read_bytes() if path.exists() else None for path in writes}
    try:
        for path, content in writes.items():
            template.atomic_write(path, content)
    except Exception:
        for path, content in originals.items():
            if content is None:
                if path.exists():
                    path.unlink()
            else:
                template.atomic_write(path, content)
        raise
    print(f"applied: new_groups={batch_size}; new_candidate_mappings={batch_size}; s3_same_corrections={corrections_to_apply}; name_fields={name_fields}; relation_candidates={sum(len(target['relations']) for target in TARGETS) + len(CORRECTIONS)}; KU={len(planned_manifest)}; formal_relations_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
