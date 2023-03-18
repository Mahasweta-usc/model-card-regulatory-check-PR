import pytest
from unittest.mock import MagicMock

from compliance_checks import (
    ComplianceSuite,
    IntendedPurposeCheck,
    GeneralLimitationsCheck,
    ComputationalRequirementsCheck,
)


class TestComplianceSuite:
    @pytest.fixture
    def mock_compliance_check(self):
        mockComplianceCheck = MagicMock()
        mockComplianceCheck.run_check = MagicMock(return_value=True)

        return mockComplianceCheck

    @pytest.fixture
    def empty_compliance_suite(self):
        return ComplianceSuite(
            checks=[]
        )

    @pytest.fixture
    def compliance_suite(self, mock_compliance_check):
        return ComplianceSuite(
            checks=[mock_compliance_check]
        )

    @pytest.fixture
    def empty_compliance_results(self):
        return []

    @pytest.fixture
    def compliance_results(self):
        return [True]

    def test_create_empty_compliance_suite(self, empty_compliance_suite):
        assert len(empty_compliance_suite.checks) == 0

    def test_create_compliance_suite(self, compliance_suite):
        assert len(compliance_suite.checks) == 1

    @pytest.mark.parametrize("suite,results", [
        ("empty_compliance_suite", "empty_compliance_results"),
        ("compliance_suite", "compliance_results")
    ])
    def test_run_compliance_suite(self, suite, results, request):
        suite: ComplianceSuite = request.getfixturevalue(suite)
        results: list = request.getfixturevalue(results)
        assert suite.run("") == results

        for check in suite.checks:
            check.run_check.assert_called_once()


def test_end_to_end_compliance_suite(real_model_card, expected_check_results):
    suite = ComplianceSuite(checks=[
        IntendedPurposeCheck(),
        GeneralLimitationsCheck(),
        ComputationalRequirementsCheck()
    ])

    results = suite.run(real_model_card)

    assert all([r.status == e for r, e in zip(results, expected_check_results)])
