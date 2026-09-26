from scripts.audit_s2_candidate_surfaces import build_patterns, find_uncovered_spans


def test_candidate_surface_scan_maps_multiline_phrase_and_honors_mention_overlap():
    text = "Context: Northern Europe; later Northern\nEurope."
    patterns = build_patterns(
        [
            {"candidate_id": "cand-north", "canonical_name": "Northern Europe", "suggested_type": "place"},
        ]
    )
    covered_start = text.index("Northern Europe")
    hits = find_uncovered_spans(text, patterns, [(0, len("Northern Europe"))])

    assert len(hits) == 1
    assert hits[0]["surface_form"] == "Northern\nEurope"
    assert hits[0]["start_char"] == text.index("Northern\nEurope")
    assert hits[0]["end_char"] == len(text) - 1
    assert covered_start < hits[0]["start_char"]


def test_candidate_scan_omits_untyped_and_short_single_word_labels():
    patterns = build_patterns(
        [
            {"candidate_id": "generic", "canonical_name": "churches", "suggested_type": ""},
            {"candidate_id": "short", "canonical_name": "Pope", "suggested_type": "person"},
            {"candidate_id": "named", "canonical_name": "Mancini", "suggested_type": "person"},
        ]
    )
    hits = find_uncovered_spans("Pope and Mancini", patterns, [])

    assert [hit["surface_form"] for hit in hits] == ["Mancini"]
    assert hits[0]["candidate_matches"][0]["candidate_id"] == "named"


def test_identity_unresolved_office_candidate_does_not_match_same_title_elsewhere():
    patterns = build_patterns(
        [
            {
                "candidate_id": "unknown-pope",
                "canonical_name": "Pope",
                "suggested_type": "person",
                "candidate_origin": "body-mention",
                "candidate_source_ref": "chp-1:sec_ii:l168-239#L657",
                "detail": "The reported speaker is identified only by office; identity unresolved.",
            }
        ],
        min_single_word_chars=3,
    )

    assert find_uncovered_spans("the Pope spoke", patterns, [], segment_id="chp-1:sec_i:l15-24") == []
    source_hit = find_uncovered_spans(
        "the Pope spoke", patterns, [], segment_id="chp-1:sec_ii:l168-239"
    )
    assert len(source_hit) == 1
    assert source_hit[0]["candidate_matches"][0]["candidate_id"] == "unknown-pope"
