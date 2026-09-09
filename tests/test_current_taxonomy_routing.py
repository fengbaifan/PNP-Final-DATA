import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts import audit_unverified_queue
from scripts import verify_collect_wikidata
from scripts import verify_collect_wikipedia


class CurrentTaxonomyRoutingTests(unittest.TestCase):
    def test_archive_matcher_does_not_reject_unclassified_unpublished_document(self):
        entity = {"claims": {"P31": [{"mainsnak": {"datavalue": {"value": {"id": "unknown-document-kind"}}}}]}}
        score, maximum, matched = verify_collect_wikidata.match_archive(entity, "An unpublished letter")
        self.assertEqual((score, maximum), (0, 2))
        self.assertEqual(matched[0]["result"], "none")
        self.assertEqual(matched[0]["expected"], "archive")
        self.assertEqual(verify_collect_wikidata.infer_claim_scope("archive", "weak"), "bibliographic_hint")

    def test_wikidata_matchers_cover_current_eight_types(self):
        self.assertEqual(
            set(verify_collect_wikidata.TYPE_MATCHER),
            {"person", "institution", "place", "work", "archive", "term", "procedure", "event"},
        )

    def test_claim_scope_uses_current_term_and_event_types(self):
        self.assertEqual(verify_collect_wikidata.infer_claim_scope("term", "strong"), "term_existence")
        self.assertEqual(verify_collect_wikidata.infer_claim_scope("event", "strong"), "event_identity_only")
        self.assertEqual(verify_collect_wikidata.infer_claim_target("procedure", "term_existence"), "term")

    def test_wikipedia_scope_uses_current_eight_type_taxonomy(self):
        self.assertEqual(
            set(verify_collect_wikipedia.TYPE_ALIASES.values()),
            {"person", "institution", "place", "work", "archive", "term", "procedure", "event"},
        )
        self.assertEqual(verify_collect_wikipedia.infer_claim_scope("term"), "term_existence")
        self.assertEqual(verify_collect_wikipedia.infer_claim_scope("procedure"), "term_existence")
        self.assertEqual(verify_collect_wikipedia.infer_claim_scope("event"), "event_identity_only")
        self.assertEqual(verify_collect_wikipedia.infer_claim_target("event"), "event_name")

    def test_wikipedia_rate_limit_retry_is_bounded(self):
        class RateLimitedResponse:
            status_code = 429

        class RateLimitedRequests:
            calls = 0

            @classmethod
            def get(cls, *args, **kwargs):
                cls.calls += 1
                return RateLimitedResponse()

        with patch.object(verify_collect_wikipedia, "requests", RateLimitedRequests), patch.object(
            verify_collect_wikipedia.time, "sleep"
        ):
            self.assertEqual(verify_collect_wikipedia.fetch_summary("Treemap"), {})

        self.assertEqual(
            RateLimitedRequests.calls,
            verify_collect_wikipedia.MAX_RATE_LIMIT_RETRIES + 1,
        )

    def test_wikidata_candidate_selection_preserves_earlier_rank_on_ties(self):
        self.assertFalse(verify_collect_wikidata.is_better_match("medium", 0.67, "medium", 0.67))
        self.assertTrue(verify_collect_wikidata.is_better_match("medium", 0.75, "medium", 0.67))
        self.assertTrue(verify_collect_wikidata.is_better_match("strong", 0.75, "medium", 1.0))

    def test_wikidata_exact_namesake_does_not_displace_earlier_search_result(self):
        exact = [{"field": "label_match", "result": "pass"}]
        self.assertFalse(
            verify_collect_wikidata.should_replace_best_match(
                "strong", 1.0, exact, "medium", 0.6, exact
            )
        )

    def test_wikidata_concept_candidate_displaces_nonconcept_exact_namesake(self):
        nonconcept = [
            {"field": "instance_of_only (P31)", "result": "none"},
            {"field": "label_match", "result": "pass"},
        ]
        concept = [
            {"field": "subclass_of (P279)", "result": "pass"},
            {"field": "label_match", "result": "pass"},
        ]

        self.assertTrue(
            verify_collect_wikidata.should_replace_best_match(
                "medium", 0.67, concept, "weak", 0.33, nonconcept
            )
        )

    def test_wikidata_bare_instance_claim_is_not_term_type_evidence(self):
        entity = {
            "claims": {"P31": [{"mainsnak": {"datavalue": {"value": {"id": "Q7889"}}}}]},
        }

        score, maximum, matched = verify_collect_wikidata.match_concept_entity(
            entity, "Pareidolia"
        )

        self.assertEqual((score, maximum), (0, 2))
        self.assertEqual(matched[0]["field"], "instance_of_only (P31)")
        self.assertEqual(matched[0]["result"], "none")

    def test_wikidata_person_score_cannot_exceed_one(self):
        time_claim = {"mainsnak": {"datavalue": {"value": {"time": "+1900-01-01T00:00:00Z"}}}}
        qid_claim = lambda qid: {"mainsnak": {"datavalue": {"value": {"id": qid}}}}
        entity = {
            "labels": {"en": {"value": "Example Person"}},
            "aliases": {"en": []},
            "claims": {
                "P31": [qid_claim("Q5")],
                "P106": [qid_claim("Q215627")],
                "P569": [time_claim],
                "P570": [time_claim],
            },
        }

        quality, score, _ = verify_collect_wikidata.match_score(
            {}, entity, "Example Person", "person"
        )

        self.assertEqual(quality, "strong")
        self.assertEqual(score, 1.0)

    def test_wikidata_generic_term_does_not_match_longer_article_title(self):
        entity = {
            "labels": {
                "en": {
                    "value": "Anatomical visualization of neural course and distribution of anterior ascending aortic plexus"
                }
            },
            "aliases": {"en": []},
            "claims": {"P31": [{}]},
        }

        quality, score, matched = verify_collect_wikidata.match_score(
            {}, entity, "Anatomical Visualization", "term"
        )

        self.assertEqual(quality, "weak")
        self.assertEqual(score, 0.0)
        self.assertEqual(matched[-1]["field"], "label_match")
        self.assertEqual(matched[-1]["result"], "fail")

    def test_wikidata_api_failure_is_not_reported_as_a_weak_semantic_match(self):
        self.assertTrue(verify_collect_wikidata.match_has_api_error({"matched_fields": ["api_error"]}))
        self.assertFalse(
            verify_collect_wikidata.match_has_api_error(
                {"matched_fields": [{"field": "label_match", "result": "fail"}]}
            )
        )

    def test_wikidata_retry_is_bounded_and_recovers_from_rate_limit(self):
        class Response:
            headers = {}

            def __init__(self, status_code, payload):
                self.status_code = status_code
                self.payload = payload

            def json(self):
                return self.payload

        class Requests:
            calls = 0

            @classmethod
            def get(cls, *args, **kwargs):
                cls.calls += 1
                if cls.calls <= verify_collect_wikidata.MAX_API_RETRIES:
                    return Response(429, {})
                return Response(200, {"search": []})

        with patch.object(verify_collect_wikidata, "requests", Requests), patch.object(
            verify_collect_wikidata.time, "sleep"
        ), patch.object(verify_collect_wikidata, "MIN_REQUEST_INTERVAL", 0):
            data, error = verify_collect_wikidata.request_json(
                verify_collect_wikidata.WIKIDATA_API,
                stage="search",
            )

        self.assertEqual(data, {"search": []})
        self.assertIsNone(error)
        self.assertEqual(Requests.calls, verify_collect_wikidata.MAX_API_RETRIES + 1)

    def test_wikidata_exhausted_retry_has_structured_error(self):
        class Response:
            status_code = 503
            headers = {}

        class Requests:
            calls = 0

            @classmethod
            def get(cls, *args, **kwargs):
                cls.calls += 1
                return Response()

        with patch.object(verify_collect_wikidata, "requests", Requests), patch.object(
            verify_collect_wikidata.time, "sleep"
        ), patch.object(verify_collect_wikidata, "MIN_REQUEST_INTERVAL", 0):
            data, error = verify_collect_wikidata.request_json(
                verify_collect_wikidata.WIKIDATA_API,
                stage="entity_batch",
            )

        self.assertIsNone(data)
        self.assertEqual(
            error,
            {
                "stage": "entity_batch",
                "kind": "http_retry_exhausted",
                "http_status": 503,
                "attempts": verify_collect_wikidata.MAX_API_RETRIES + 1,
                "retryable": True,
            },
        )
        self.assertEqual(Requests.calls, verify_collect_wikidata.MAX_API_RETRIES + 1)

    def test_wikidata_entities_are_fetched_in_one_batch_request(self):
        class Response:
            status_code = 200
            headers = {}

            def json(self):
                return {"entities": {"Q1": {"id": "Q1"}, "Q2": {"id": "Q2"}}}

        class Requests:
            calls = []

            @classmethod
            def get(cls, *args, **kwargs):
                cls.calls.append(kwargs.get("params"))
                return Response()

        with patch.object(verify_collect_wikidata, "requests", Requests), patch.object(
            verify_collect_wikidata, "MIN_REQUEST_INTERVAL", 0
        ):
            entities = verify_collect_wikidata.get_entities(["Q1", "Q2", "Q1"])

        self.assertEqual(set(entities), {"Q1", "Q2"})
        self.assertEqual(len(Requests.calls), 1)
        self.assertEqual(Requests.calls[0]["action"], "wbgetentities")
        self.assertEqual(Requests.calls[0]["ids"], "Q1|Q2")

    def test_unverified_queue_routes_current_direct_and_semantic_types(self):
        self.assertEqual(
            audit_unverified_queue.recommended_action("terms", "no_wiki_page"),
            "llm_internal_semantic_review",
        )
        self.assertEqual(
            audit_unverified_queue.recommended_action("events", "needs_direct_verification"),
            "event_secondary_source_check",
        )

    def test_confidence_audit_reports_debt_without_changing_status(self):
        unit = audit_unverified_queue.Unit(
            path=audit_unverified_queue.ROOT / "04-knowledge/units/terms/example.md",
            type_name="terms",
            title="Example",
            confidence="medium",
            consensus="tentative",
            source_count=1,
            evidence_status="source_backed",
            verification_level="L1",
            last_verified="2026-08-01",
            review_due="2027-08-01",
            conflicts=(),
            source_family="other/unknown",
            unverified_notes=(),
            isolated_from_structure_and_relation_graph=False,
        )

        row = audit_unverified_queue.assess(unit, date(2026, 8, 3))

        self.assertEqual(row["priority"], "P2")
        self.assertEqual(row["reasons"], ["single_source", "tentative_or_missing_consensus"])
        self.assertEqual(row["evidence_status"], "source_backed")

    def test_confidence_audit_routes_status_conflict_to_p0(self):
        unit = audit_unverified_queue.Unit(
            path=audit_unverified_queue.ROOT / "04-knowledge/units/works/example.md",
            type_name="works",
            title="Example",
            confidence="high",
            consensus="confirmed",
            source_count=1,
            evidence_status="unverified",
            verification_level="L1",
            last_verified="2026-08-01",
            review_due="2027-08-01",
            conflicts=(),
            source_family="other/unknown",
            unverified_notes=(),
            isolated_from_structure_and_relation_graph=False,
        )

        row = audit_unverified_queue.assess(unit, date(2026, 8, 3))

        self.assertEqual(row["priority"], "P0")
        self.assertIn("high_confidence_but_unverified", row["status_conflicts"])

    def test_confidence_summary_reports_actual_isolation_count(self):
        rows = [
            {
                "priority": "P2",
                "reasons": ["isolated_from_structure_and_relation_graph"],
                "status_conflicts": [],
            }
        ]
        with TemporaryDirectory() as directory:
            output = Path(directory) / "summary.md"
            audit_unverified_queue.write_summary(rows, output, "test-scope")
            summary = output.read_text(encoding="utf-8")

        self.assertIn("本次识别 1 个", summary)
        self.assertNotIn("本次范围内的 KU 已具有 Topic 连接", summary)
