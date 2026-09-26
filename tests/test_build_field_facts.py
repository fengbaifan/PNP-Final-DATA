import json
from collections import deque

from scripts.build_field_facts import citation_urls, load_existing_ids


def test_existing_enrichment_ids_accept_utf8_bom(tmp_path):
    path = tmp_path / "enrichment.jsonl"
    record = {
        "enrichment_id": "enr-42",
        "ku_id": "units/persons/example",
        "field": "occupation",
        "value": "painter",
        "source_id": "source-1",
        "occurrence_id": "occ-1",
    }
    path.write_text("\ufeff" + json.dumps(record) + "\n", encoding="utf-8")

    by_occurrence, by_natural_key, max_id = load_existing_ids(path)

    assert by_occurrence["occ-1"] == deque(["enr-42"])
    assert by_natural_key[("units/persons/example", "occupation", "painter", "source-1")] == deque(["enr-42"])
    assert max_id == 42


def test_citation_url_parser_preserves_balanced_parentheses_and_trims_punctuation():
    citation = (
        "Treccani https://www.treccani.it/enciclopedia/bonatti_(Dizionario-Biografico)/. "
        "Wikipedia https://en.wikipedia.org/wiki/Caravaggio_(Caravaggio). "
        "Wrapped https://example.org/page(foo)). "
        "Markdown [object](https://example.org/item/42)；后续文字"
    )

    assert citation_urls(citation) == [
        "https://www.treccani.it/enciclopedia/bonatti_(Dizionario-Biografico)/",
        "https://en.wikipedia.org/wiki/Caravaggio_(Caravaggio)",
        "https://example.org/page(foo)",
        "https://example.org/item/42",
    ]
