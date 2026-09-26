import csv
from functools import lru_cache
from pathlib import Path

import pytest

from scripts.build_cards import card_key, load_inputs, read_card, render_card
from scripts.build_relation_views import relation_view_layout


BASE = Path(__file__).resolve().parents[1]
PREVIEW_SAMPLES = {
    "archive": "units/archives/accademia-statutes-confirmed-1621",
    "event": "units/events/accademia-tax-privilege-1633",
    "family": "units/families/aldobrandini-family",
    "institution": "units/institutions/a-villani-e-figli",
    "person": "units/persons/abate-lancellotti",
    "place": "units/places/bologna",
    "procedure": "units/procedures/artist-title-conferral",
    "term": "units/terms/altarpiece",
    "work": "units/works/barberini-salone-bozzetto-disputed",
}


@lru_cache(maxsize=1)
def _inputs():
    return load_inputs()


@lru_cache(maxsize=1)
def _manifest_by_id():
    with (BASE / "04-knowledge/tables/ku-manifest.csv").open(encoding="utf-8-sig", newline="") as handle:
        return {row["ku_id"]: row for row in csv.DictReader(handle)}


@pytest.mark.parametrize("entity_type,ku_id", PREVIEW_SAMPLES.items())
def test_card_preview_is_idempotent_and_preserves_description(entity_type, ku_id):
    manifest, enrichments, projected = _inputs()
    row = _manifest_by_id()[ku_id]
    assert row["type"] == entity_type
    key = card_key(row["card_path"])
    source = read_card(BASE / row["card_path"])

    preview = render_card(source, ku_id, enrichments.get(ku_id, []), projected.get(key, []))
    repeated = render_card(preview, ku_id, enrichments.get(ku_id, []), projected.get(key, []))

    assert repeated == preview
    assert relation_view_layout(source) == relation_view_layout(preview)
    assert source.split("## 内容", 1)[1].split("## 关系与证据", 1)[0] == preview.split("## 内容", 1)[1].split("## 关系与证据", 1)[0]


def test_preview_is_idempotent_for_cards_without_relation_rows():
    manifest, enrichments, projected = _inputs()
    ku_id = "units/archives/gerusalemme-liberata-illustrations-1745"
    row = _manifest_by_id()[ku_id]
    key = card_key(row["card_path"])
    source = read_card(BASE / row["card_path"])

    assert projected.get(key, []) == []
    preview = render_card(source, ku_id, enrichments.get(ku_id, []), projected.get(key, []))
    repeated = render_card(preview, ku_id, enrichments.get(ku_id, []), projected.get(key, []))

    assert repeated == preview


def test_preview_preserves_legacy_relation_heading_and_header():
    manifest, enrichments, projected = _inputs()
    ku_id = "units/persons/maria-ruffo-guercino-commissioner"
    row = _manifest_by_id()[ku_id]
    key = card_key(row["card_path"])
    source = read_card(BASE / row["card_path"])
    layout = relation_view_layout(source)

    preview = render_card(source, ku_id, enrichments[ku_id], projected.get(key, []))

    assert layout[0] == "### 关系记录"
    assert layout[1][0] == "| 方向与关系 | 关联知识元 | 语境 |"
    assert relation_view_layout(preview) == layout


def test_preview_rejects_a_table_layout_without_a_matching_structured_record():
    manifest, enrichments, projected = _inputs()
    row = _manifest_by_id()[PREVIEW_SAMPLES["archive"]]
    key = card_key(row["card_path"])
    source = read_card(BASE / row["card_path"])
    lines = source.splitlines()
    header_index = next(
        index for index, line in enumerate(lines[:-1])
        if line.startswith("|") and lines[index + 1].startswith("|---")
    )
    cells = lines[header_index].split("|")
    cells[1] += " UNKNOWN_LAYOUT"
    lines[header_index] = "|".join(cells)

    with pytest.raises(ValueError, match="no table rows in enrichment|absent card table"):
        render_card("\n".join(lines) + "\n", row["ku_id"], enrichments[row["ku_id"]], projected.get(key, []))


def test_preview_rebuilds_changed_cells_from_enrichment_without_writing():
    manifest, enrichments, projected = _inputs()
    row = _manifest_by_id()[PREVIEW_SAMPLES["archive"]]
    ku_id = row["ku_id"]
    key = card_key(row["card_path"])
    source = (BASE / row["card_path"]).read_text(encoding="utf-8-sig")
    records = [dict(record, cells=list(record["cells"])) for record in enrichments[ku_id]]
    marker = "preview-only rebuilt cell"
    records[0]["cells"][1] = marker

    preview = render_card(source, ku_id, records, projected.get(key, []))
    next_preview = render_card(preview, ku_id, records, projected.get(key, []))

    assert marker in preview
    assert next_preview == preview
    assert marker not in source
    source_prose = [line for line in source.splitlines() if not line.lstrip().startswith("|")]
    preview_prose = [line for line in preview.splitlines() if not line.lstrip().startswith("|")]
    assert preview_prose == source_prose


def test_preview_preserves_bom_and_crlf_line_endings():
    manifest, enrichments, projected = _inputs()
    row = _manifest_by_id()[PREVIEW_SAMPLES["person"]]
    key = card_key(row["card_path"])
    source = "\ufeff" + read_card(BASE / row["card_path"]).replace("\n", "\r\n")

    preview = render_card(source, row["ku_id"], enrichments[row["ku_id"]], projected.get(key, []))

    assert preview.startswith("\ufeff---\r\n")
    assert "\n" not in preview.replace("\r\n", "")
    assert relation_view_layout(source) == relation_view_layout(preview)
