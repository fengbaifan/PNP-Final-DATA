import unittest

from scripts import verify_collect_openalex as openalex


def inverted(text: str) -> dict[str, list[int]]:
    result: dict[str, list[int]] = {}
    for index, word in enumerate(text.split()):
        result.setdefault(word, []).append(index)
    return result


class VerifyCollectOpenAlexTests(unittest.TestCase):
    def test_reconstruct_abstract_preserves_position_order(self):
        self.assertEqual(openalex.reconstruct_abstract({"chart": [2], "A": [0], "is": [1]}), "A is chart")

    def test_explicit_definition_is_semantic_candidate(self):
        docs = [{
            "id": "https://openalex.org/W1",
            "display_name": "Visual encoding in charts",
            "abstract_inverted_index": inverted("Visual encoding is defined as the mapping of data attributes to graphical properties."),
            "cited_by_count": 20,
            "authorships": [],
        }]
        best, _, blocking = openalex.evaluate_candidates("Visual Encoding", docs)
        self.assertIsNone(blocking)
        self.assertTrue(best["semantic_context"])

    def test_mention_without_semantic_cue_is_blocked(self):
        docs = [{
            "id": "https://openalex.org/W1",
            "display_name": "Visual encoding observations",
            "abstract_inverted_index": inverted("We observed visual encoding during three experiments."),
            "cited_by_count": 3,
            "authorships": [],
        }]
        _, _, blocking = openalex.evaluate_candidates("Visual Encoding", docs)
        self.assertEqual(blocking, "no_semantic_context")

    def test_candidate_without_abstract_is_blocked(self):
        docs = [{"id": "https://openalex.org/W1", "display_name": "Data Map", "cited_by_count": 10, "authorships": []}]
        _, _, blocking = openalex.evaluate_candidates("Data Map", docs)
        self.assertEqual(blocking, "no_abstract_candidates")

    def test_unrelated_abstract_is_weak_match(self):
        docs = [{
            "id": "https://openalex.org/W1",
            "display_name": "Unrelated history",
            "abstract_inverted_index": inverted("This method studies medieval manuscripts."),
            "cited_by_count": 10,
            "authorships": [],
        }]
        _, _, blocking = openalex.evaluate_candidates("Horizontal Bar Chart", docs)
        self.assertEqual(blocking, "weak_term_match")


if __name__ == "__main__":
    unittest.main()
