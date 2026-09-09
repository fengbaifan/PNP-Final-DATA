import unittest

from scripts import audit_system_upgrade_chain


class SystemUpgradeChainExitTests(unittest.TestCase):
    def test_fail_count_returns_nonzero_exit_code(self):
        self.assertEqual(audit_system_upgrade_chain.exit_code_for_summary({"fail": 1}), 1)

    def test_zero_fail_count_returns_zero_exit_code(self):
        self.assertEqual(audit_system_upgrade_chain.exit_code_for_summary({"fail": 0}), 0)

    def test_current_upgrade_contract_passes_behavioral_checks(self):
        failures = [
            item for item in audit_system_upgrade_chain.run_checks()
            if item.status == "fail"
        ]
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
