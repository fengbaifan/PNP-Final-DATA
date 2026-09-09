import unittest

from scripts import verify_collect_openlibrary as openlibrary


class VerifyCollectOpenLibraryTests(unittest.TestCase):
    def test_exact_title_and_matching_year_support_bibliographic_fact(self):
        docs = [{
            "key": "/works/OL1W",
            "title": "Osteographia",
            "author_name": ["William Cheselden"],
            "first_publish_year": 1733,
            "publisher": ["W. Bowyer"],
        }]
        best, _, blocking = openlibrary.evaluate_candidates("Osteographia, 1733", 1733, docs)
        self.assertIsNone(blocking)
        self.assertTrue(openlibrary.bibliographic_fact(best, 1733))

    def test_title_match_with_conflicting_year_is_blocked(self):
        docs = [{
            "key": "/works/OL1W",
            "title": "Osteographia",
            "author_name": ["William Cheselden"],
            "first_publish_year": 1968,
            "publisher": ["Scolar Press"],
        }]
        _, _, blocking = openlibrary.evaluate_candidates("Osteographia, 1733", 1733, docs)
        self.assertEqual(blocking, "publication_year_conflict")

    def test_same_title_different_authors_without_year_is_ambiguous(self):
        docs = [
            {"key": "/works/OL1W", "title": "Polychronicon", "author_name": ["Ranulf Higden"]},
            {"key": "/works/OL2W", "title": "Polychronicon", "author_name": ["Polly Fleck"]},
        ]
        _, _, blocking = openlibrary.evaluate_candidates("Polychronicon", None, docs)
        self.assertEqual(blocking, "ambiguous_bibliographic_identity")

    def test_missing_author_variant_does_not_create_false_ambiguity(self):
        docs = [
            {"key": "/works/OL1W", "title": "Atlas of the British flora", "author_name": ["Franklyn Perring"], "first_publish_year": 1962, "publisher": ["Nelson"]},
            {"key": "/works/OL2W", "title": "Atlas of the British flora", "author_name": [], "first_publish_year": 1962, "publisher": ["Nelson"]},
        ]
        best, _, blocking = openlibrary.evaluate_candidates("Atlas of the British Flora", 1962, docs)
        self.assertIsNone(blocking)
        self.assertEqual(best["authors"], ["Franklyn Perring"])

    def test_expanded_author_name_is_same_identity_for_ambiguity_check(self):
        docs = [
            {"key": "/works/OL1W", "title": "Atlas of the British flora", "author_name": ["Franklyn Perring"], "first_publish_year": 1962, "publisher": ["Nelson"]},
            {"key": "/works/OL2W", "title": "Atlas of the British flora", "author_name": ["Franklyn Hugh Perring"], "first_publish_year": 1962, "publisher": ["Nelson"]},
        ]
        _, _, blocking = openlibrary.evaluate_candidates("Atlas of the British Flora", 1962, docs)
        self.assertIsNone(blocking)

    def test_coverage_range_does_not_override_slug_publication_year(self):
        self.assertEqual(
            openlibrary.expected_year("", "Atlas of climatic types in the United States 1900-1939", "", "", "atlas-climatic-types-us-1941"),
            1941,
        )

    def test_query_title_removes_trailing_year_only(self):
        self.assertEqual(openlibrary.search_title("Osteographia, 1733"), "Osteographia")
        self.assertEqual(openlibrary.search_title("The Temple of Time (1846)"), "The Temple of Time")


if __name__ == "__main__":
    unittest.main()
