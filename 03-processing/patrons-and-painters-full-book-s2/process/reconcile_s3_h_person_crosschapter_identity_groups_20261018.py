from __future__ import annotations

import argparse
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
ANCHOR = "s3-h-person-crosschapter-identity-groups-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"

REVIEWS = {
    "cand-1287": {
        "entry": "H.csv#2", "canonical": "Hamen, Juan van der", "decision": "new",
        "group": "new-person:der-hamen-juan-van-98401ebaa1",
        "review": "第20章后记p.400正文写Juan van der Hamen，索引H.csv#2给出同一全名；这是人物cand-1287的书内身份组。它只作为已佚Cardinal Barberini肖像的画家提及，不与作品候选cand-10952合并；无相同类型既有KU。",
    },
    "cand-1288": {
        "entry": "H.csv#3", "canonical": "Handel, George Frederick", "decision": "new",
        "group": "new-person:frederick-george-handel-b7a9ead66a",
        "review": "第10章p.281正文只用姓氏Handel；索引H.csv#3展开为George Frederick Handel。保留索引给出的书内身份形式，未据名字补写生平或外部标识；无相同类型既有KU。",
    },
    "cand-1291": {
        "entry": "H.csv#7", "canonical": "Harrach, Count", "decision": "undecided",
        "new_group": "new-person:aloys-thomas-raimund-harrach-20261018",
        "review": "第7章p.200的Count Harrach与Aloys Thomas Raimund Harrach相符：正文和注7均置于奥地利驻那不勒斯总督及那不勒斯艺术赞助语境。Deutsche Biographie《Aloys Graf von Harrach》列名变体Aloys Thomas Raimund Graf von Harrach及GND 132626748；Treccani《Harrach》条目记其为那不勒斯总督（1728–1733）。两处身份锚点吻合。现有KU中无该人物；改为独立new人物组，不与Harrach家族、收藏或作品对象合并。",
        "external": {
            "source": "GND (Deutsche Biographie)", "id": "132626748",
            "note": "Identity comparison only: Deutsche Biographie, ‘Harrach, Aloys Graf von,’ gives the name variant ‘Aloys Thomas Raimund Graf von Harrach,’ dates 1669–1742, and GND 132626748. Compared with Haskell ch.7 p.200, where Count Harrach is identified as an Austrian viceroy active after 1728; Treccani, ‘Harrach,’ specifies the Naples viceroyalty 1728–1733. Supports the person identity only, not Haskell’s patronage superlative or relation claims.",
        },
    },
    "cand-1293": {
        "entry": "H.csv#9", "canonical": "Helmbrecker, Theodor", "decision": "new",
        "group": "new-person:helmbrecker-theodor-5737710433",
        "review": "第6章p.158的正文全名为Theodor Helmbrecker，索引H.csv#9同列此名。Uffizi Galleries的《Rustic scene》记录用Theodor Helmbreker（少一个c），并称Monsù Teodoro；该记录还把作品的捐赠者记为Francesco Marucelli，与Haskell同页的人物语境吻合。保留Haskell拼写作书内锚点，在卡片中并列权威形式；无相同类型既有KU，且不与work候选cand-6414混合。外部记录只用于身份，不验证Haskell所述十六幅画及赞助关系。",
        "external": {
            "source": "Uffizi Galleries (artist named in work record)", "id": "https://www.uffizi.it/en/artworks/rustic-scene",
            "note": "Identity comparison only: the Uffizi record ‘Rustic scene’ names Theodor Helmbreker, called Monsù Teodoro, and identifies Francesco Marucelli as the donor of the painting. Compared with Haskell ch.6 p.158, which names Theodor Helmbrecker in Marucelli’s patronage context. The spelling variant is retained; this does not verify the separate sixteen-picture claim.",
        },
    },
    "cand-1294": {
        "entry": "H.csv#10", "canonical": "Henri III of France", "decision": "new",
        "group": "new-person:france-henri-iii-of-6f746d232e",
        "review": "第9章p.255正文及索引H.csv#10均称Henri III of France；语境明确为1574年到访Mira的法国国王。它与Henri IV候选cand-1295为不同君主；同段作品、事件和地点候选保持各自类型，不并入人物组。无同类型既有KU。",
    },
    "cand-1296": {
        "entry": "H.csv#12", "canonical": "Henrietta Maria, Queen of England", "decision": "new",
        "group": "new-person:england-henrietta-maria-of-b9baa37f48",
        "review": "第7章p.179正文在Charles之后以‘the Queen’指称人物；索引H.csv#12标为Henrietta Maria, Queen of England，S2提及也已将这些指代连到同一候选。保留索引名并以Charles的王后语境支持身份；不与未具名Cardinal Barberini候选cand-6757或Queen’s Chapel地点cand-6759合并。无同类型既有KU。",
    },
    "cand-1297": {
        "entry": "H.csv#13", "canonical": "Hervey, Sir Robert", "decision": "new",
        "group": "new-person:hervey-robert-b62bf2d0f9",
        "review": "第10章p.305正文称Sir Robert Hervey；索引H.csv#13将此人物定位于同页。Haskell同时提及Canaletto为他绘制的二十幅景观，但相应cand-9220是work类型且身份仍待证；人物和作品候选分开。与cand-1298的Lord Hervey不因同姓合并：本候选有不同给名与称谓，目前没有同一身份证据。无相同类型既有KU。",
    },
    "cand-1298": {
        "entry": "H.csv#14", "canonical": "Hervey, Lord", "decision": "undecided",
        "new_group": "new-person:john-hervey-2nd-baron-hervey-20261018",
        "review": "第14章p.349的Lord Hervey处于Algarotti 1736年赴伦敦后与其交往的语境。Westminster School Archive & Collections规范记录将John Hervey（1696–1743）列为该时期的Lord Hervey，记录其1723年起以Lord Hervey称呼，权威记录号GB-2014-WSA-00767；该年代与书内语境相合。现有KU中无该人物，改为new身份组，并与Sir Robert Hervey候选cand-1297分开，不将Haskell对交往的叙述当作外部证实。",
        "external": {
            "source": "Westminster School Archive & Collections",
            "id": "GB-2014-WSA-00767",
            "note": "Identity comparison only: authority record ‘Hervey, John, 2nd Baron Hervey of Ickworth, 1696–1743’ gives authorized name, dates, and records that he was styled Lord Hervey from 1723. Compared with Haskell ch.14 p.349, in the 1736 London context of Algarotti. The archive record supports the titleholder’s identity only, not Haskell’s characterization of their relationship.",
        },
    },
    "cand-1299": {
        "entry": "H.csv#15", "canonical": "Hildebrandt, Lucas von", "decision": "new",
        "group": "new-person:hildebrandt-lucas-von-425ee5c0e1",
        "review": "第7章p.201正文和索引H.csv#15称Lucas von Hildebrandt。MAK Collection Online人物记录规范名为Johann Lucas von Hildebrandt，姓名与时代相符；Haskell在此只把两座Belvederes归于Lucas von Hildebrandt。无相同类型既有KU；卡片保存书内称名及外部规范全名，不将外部生平资料扩展为本书断言。",
        "external": {
            "source": "MAK Collection Online",
            "id": "https://sammlung.mak.at/en/artist/hildebrandt-johann-lucas-von_30775",
            "note": "Identity comparison only: MAK artist record is headed ‘Hildebrandt, Johann Lucas von’ and gives dates 1668–1745. Compared with Haskell ch.7 p.201 and index H.csv#15, which use ‘Lucas von Hildebrandt.’ This identifies the person name only; it does not verify Haskell’s attribution of the Belvederes.",
        },
    },
    "cand-1300": {
        "entry": "H.csv#16", "canonical": "Hill, Samuel", "decision": "new",
        "group": "new-person:hill-samuel-3c347d356a",
        "review": "第10章pp.290n、304n共三处提及Samuel Hill，mention账本都映射至cand-1300；第10章p.304注2的S2候选记Smith向Samuel Hill发送Piazzetta作品。全名在原文注释中出现，索引H.csv#16汇总两页定位。无相同类型既有KU；所引Chaloner材料仍未独立查阅。",
    },
    "cand-1301": {
        "entry": "H.csv#17", "canonical": "Hogarth, William", "decision": "new",
        "group": "new-person:hogarth-william-51254bc070",
        "review": "第10章p.279正文以Hogarth姓氏提及画家；索引H.csv#17给出William Hogarth。保留索引身份形式，不从该短提及扩写事实；无相同类型既有KU。",
    },
    "cand-1302": {
        "entry": "H.csv#18", "canonical": "Honthorst, Gerrit van", "decision": "new",
        "group": "new-person:gerrit-honthorst-van-1acc9537ec",
        "review": "第4章p.95正文以Honthorst姓氏列入Giustiniani对直接使用模特画家的比较；索引H.csv#18展开为Gerrit van Honthorst。正文和索引共同支持书内身份组；无相同类型既有KU。",
    },
    "cand-1303": {
        "entry": "H.csv#19", "canonical": "Horace", "decision": "undecided",
        "new_group": "new-person:horace-roman-poet-20261018",
        "review": "第13章p.333以Horace的诗篇为古代作品范例，第14章p.360明确提及Horace的Non omnis moriar；两处跨章语境指向罗马诗人，而非既有Horace Walpole人物KU（units/persons/horace-walpole，cand-2798）。本候选没有相同类型既有KU，改为独立的Horace罗马诗人new组；不把诗句引述扩展为对纪念铭文的外部核实。",
    },
}

EXTERNAL_CANDIDATES = {"cand-1291", "cand-1293", "cand-1298", "cand-1299"}


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False) as handle:
        tmp = Path(handle.name)
        handle.write(content)
    try:
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink()


def with_bom(text: str, original: bytes) -> bytes:
    raw = text.encode("utf-8")
    return b"\xef\xbb\xbf" + raw if original.startswith(b"\xef\xbb\xbf") else raw


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve and document the next cross-chapter H-section person identity groups.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    fields, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    revised_rows = [dict(row) for row in alignments]
    main_rows = {
        row["candidate_id"]: row for row in revised_rows
        if row.get("candidate_id") in REVIEWS and not row.get("external_source")
    }
    assert len(main_rows) == len(REVIEWS)

    for candidate_id, review in REVIEWS.items():
        candidate = candidate_by_id[candidate_id]
        target = main_rows[candidate_id]
        assert candidate.get("suggested_type") == "person"
        assert candidate.get("index_entry_id") == review["entry"]
        assert candidate.get("canonical_name") == review["canonical"]
        assert target.get("decision") == review["decision"], (candidate_id, target.get("decision"))
        assert not target.get("ku_id"), (candidate_id, target.get("ku_id"))

        if review["decision"] == "new":
            assert sync.get_group(target.get("resolution_note", "")) == review["group"]
            target["resolution_note"] += f" S3 cross-chapter person identity review ({DATE}): {review['review']}"
        else:
            old_note = target.get("resolution_note", "")
            target["decision"] = "new"
            target["resolution_note"] = (
                f"source_ref=candidate={candidate_id};index_entry={review['entry']}; "
                f"Prior S3 undecided note preserved: {old_note} "
                f"group={review['new_group']}; S3 cross-chapter person identity review ({DATE}): {review['review']}"
            )
        target.update(process_ref=PROCESS_REF, accessed_date=DATE)

    for candidate_id in EXTERNAL_CANDIDATES:
        assert not any(row.get("candidate_id") == candidate_id and row.get("external_source") for row in alignments)

    # Add separate external identity rows; S4 will map them to the same KU as each new person group.
    next_id = max(int(match.group(1)) for row in revised_rows if (match := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))) + 1
    for candidate_id in sorted(EXTERNAL_CANDIDATES, key=lambda cid: int(cid.split("-")[1])):
        external = REVIEWS[candidate_id]["external"]
        row = {field: "" for field in fields}
        row.update({
            "alignment_id": f"aln-{next_id:04d}",
            "candidate_id": candidate_id,
            "external_source": external["source"],
            "external_id": external["id"],
            "decision": "new",
            "accessed_date": DATE,
            "process_ref": PROCESS_REF,
            "resolution_note": external["note"],
        })
        revised_rows.append(row)
        next_id += 1

    decision_rows = [row for row in revised_rows if not row.get("external_source")]
    decision_stats = sync.summarize_by_type(candidates, decision_rows)
    totals = {key: sum(value[key] for value in decision_stats.values()) for key in next(iter(decision_stats.values()))}
    before_stats = sync.summarize_by_type(candidates, [row for row in alignments if not row.get("external_source")])
    before_totals = {key: sum(value[key] for value in before_stats.values()) for key in next(iter(before_stats.values()))}
    assert totals["new_candidates"] == before_totals["new_candidates"] + 3
    assert totals["undecided"] == before_totals["undecided"] - 3
    assert sum(1 for row in decision_rows if row.get("candidate_id") in REVIEWS) == len(REVIEWS)

    process_text = process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), decision_stats)
    if f'<a id="{ANCHOR}"></a>' not in process_text:
        bullets = []
        for candidate_id, review in REVIEWS.items():
            disposition = "原new组复核" if review["decision"] == "new" else "undecided改为new"
            group = review.get("group", review.get("new_group"))
            bullets.append(f"- {candidate_id}（{review['entry']}；{candidate_by_id[candidate_id]['canonical_name']}）：{disposition}，group=`{group}`。{review['review']}")
        process_text = process_text.rstrip() + (
            f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3人物：H段跨章身份组复核（{DATE}）\n\n"
            + "\n".join(bullets)
            + "\n\n"
            + "外部身份比较仅用于消歧，未据此核实S2断言或建立正式关系："
            + "[Deutsche Biographie / GND Harrach](https://www.deutsche-biographie.de/sfz26099.html)，"
            + "[Treccani Harrach](https://www.treccani.it/enciclopedia/harrach/)，"
            + "[Uffizi Theodor Helmbreker](https://www.uffizi.it/en/artworks/rustic-scene)，"
            + "[Westminster School Archive John Hervey](https://collections.westminster.org.uk/index.php/hervey-john-hervey-baron-1696-1743)，"
            + "[MAK Johann Lucas von Hildebrandt](https://sammlung.mak.at/en/artist/hildebrandt-johann-lucas-von_30775)。\n\n"
            + "本组13个候选均为new人物组；其中9条直接S2关系候选仍待S6，cand-1297对应的work候选cand-9220仍为独立待证对象。新增4条外部身份记录，待S4与各自人物KU映射；本批无正式关系。"
        )

    result_text = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"),
        decision_stats,
        totals,
        len(sync.read_csv(MANIFEST)[1]),
    )
    result_heading = "S3人物：H段跨章身份组复核"
    if result_heading not in result_text:
        result_text = result_text.rstrip() + (
            f"\n\n### {result_heading}（{DATE}）\n\n"
            "复核cand-1287、1288、1291、1293、1294、1296–1303共13个人物候选，均有可追溯的new身份组；其中Count Harrach、Lord Hervey和Horace由undecided改为new。Count Harrach映射至Aloys Thomas Raimund Harrach，Lord Hervey映射至John Hervey, 2nd Baron Hervey；Horace指罗马诗人，与Horace Walpole分开。新增4条外部身份记录，来源只用于身份消歧。13个new组待S4登记；9条直接S2关系候选仍待S6，cand-9220作品组继续单独待证。"
        )

    with tempfile.TemporaryDirectory(prefix="pnp-s3-h-person-groups-") as temp_name:
        stage = Path(temp_name) / "alignment.csv"
        sync.write_csv(stage, fields, revised_rows)
        writes = {
            ALIGNMENT: stage.read_bytes(),
            PROCESS: with_bom(process_text + "\n", PROCESS.read_bytes()),
            RESULT: with_bom(result_text + "\n", RESULT.read_bytes()),
        }

    if args.dry_run:
        print("S3 dry-run passed: 13 person decisions are traceable; 3 undecided items move to new; 4 external identity rows are prepared; no KU or S6 relation is created.")
        return 0

    originals = {path: path.read_bytes() for path in writes}
    try:
        for path, content in writes.items():
            atomic_write(path, content)
    except Exception:
        for path, content in originals.items():
            atomic_write(path, content)
        raise
    print("applied: 13 H-section person identity reviews and four external identity rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
