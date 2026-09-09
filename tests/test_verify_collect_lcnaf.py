import unittest

from scripts import verify_collect_lcnaf as lcnaf


def hit(label, rdf_type, **more):
    metadata = {"rdftypes": [rdf_type, "Name", "Authority"], **more}
    return {"suggestLabel": label, "uri": "http://id.loc.gov/authorities/names/test", "more": metadata}


class VerifyCollectLcnafTests(unittest.TestCase):
    def test_person_heading_can_support_basic_fact_scope(self):
        candidate = hit(
            "Minard, Charles Joseph, 1781-1870",
            "PersonalName",
            birthdates=["1781"],
            deathdates=["1870"],
            occupations=["Civil engineers", "Cartographers"],
        )
        best, _, blocking = lcnaf.evaluate_candidates("Charles Joseph Minard", "person", [candidate])
        self.assertIsNone(blocking)
        self.assertEqual(best["match_quality"], "strong")
        self.assertTrue(lcnaf.basic_fact_scope("person", best["verified_fields"], "strong"))

    def test_type_mismatch_is_not_identity_evidence(self):
        candidate = hit("Rand McNally", "PersonalName")
        best, _, blocking = lcnaf.evaluate_candidates("Rand McNally", "institution", [candidate])
        self.assertIsNone(best)
        self.assertEqual(blocking, "no_type_compatible_candidate")

    def test_same_acronym_authorities_are_blocked_as_ambiguous(self):
        candidates = [
            hit("NASA (USE National Association of Student Anthropologists)", "CorporateName"),
            {**hit("NASA (USE National Association of Students of Architecture)", "CorporateName"), "uri": "http://id.loc.gov/authorities/names/other"},
        ]
        best, _, blocking = lcnaf.evaluate_candidates("NASA", "institution", candidates)
        self.assertEqual(best["match_quality"], "strong")
        self.assertEqual(blocking, "ambiguous_authority_heading")

    def test_institution_identity_does_not_become_basic_fact_automatically(self):
        fields = ["authority_heading", "entity_type", "corporate_identity", "authority_source_note"]
        self.assertFalse(lcnaf.basic_fact_scope("institution", fields, "strong"))


if __name__ == "__main__":
    unittest.main()
