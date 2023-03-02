import pytest
from unittest.mock import MagicMock

import markdown
from bs4 import BeautifulSoup, Comment
from compliance_checks import ComplianceSuite, ModelProviderIdentityCheck, IntendedPurposeCheck


class TestComplianceCheck:
    @pytest.fixture
    def provider_identity_model_card(self):
        return """
# Model Card for Sample Model

Some random info...

## Model Details

### Model Description

<!-- Provide a longer summary of what this model is. -->

- **Developed by:** Nima Boscarino
- **Model type:** Yada yada yada
        """

    @pytest.fixture
    def bad_provider_identity_model_card(self):
        return """
# Model Card for Sample Model

Some random info...

## Model Details

### Model Description

- **Developed by:** [More Information Needed]
- **Model type:** Yada yada yada
        """

    @pytest.fixture
    def intended_purpose_model_card(self):
        return """
# Model Card for Sample Model

Some random info...

## Uses

<!-- Address questions around how the model is intended to be used, including the foreseeable users of the model and those affected by the model. -->

### Direct Use

<!-- This section is for the model use without fine-tuning or plugging into a larger ecosystem/app. -->

Here is some info about direct uses...

### Downstream Use [optional]

<!-- This section is for the model use when fine-tuned for a task, or when plugged into a larger ecosystem/app -->

[More Information Needed]

### Out-of-Scope Use

<!-- This section addresses misuse, malicious use, and uses that the model will not work well for. -->

[More Information Needed]

## Bias, Risks, and Limitations

<!-- This section is meant to convey both technical and sociotechnical limitations. -->

[More Information Needed]        
        """

    @pytest.fixture
    def bad_intended_purpose_model_card(self):
        return """
# Model Card for Sample Model

Some random info...

## Uses

<!-- Address questions around how the model is intended to be used, including the foreseeable users of the model and those affected by the model. -->

### Direct Use

<!-- This section is for the model use without fine-tuning or plugging into a larger ecosystem/app. -->

[More Information Needed]

### Downstream Use [optional]

<!-- This section is for the model use when fine-tuned for a task, or when plugged into a larger ecosystem/app -->

[More Information Needed]

### Out-of-Scope Use

<!-- This section addresses misuse, malicious use, and uses that the model will not work well for. -->

[More Information Needed]

## Bias, Risks, and Limitations

<!-- This section is meant to convey both technical and sociotechnical limitations. -->

[More Information Needed]
        """

    @pytest.mark.parametrize("check, card,check_passed,values", [
        (ModelProviderIdentityCheck(), "provider_identity_model_card", True, "Nima Boscarino"),
        (ModelProviderIdentityCheck(), "bad_provider_identity_model_card", False, None),
        (IntendedPurposeCheck(), "intended_purpose_model_card", True, None),
        (IntendedPurposeCheck(), "bad_intended_purpose_model_card", False, None),
    ])
    def test_run_model_provider_identity_check(self, check, card, check_passed, values, request):
        card = request.getfixturevalue(card)

        model_card_html = markdown.markdown(card)
        card_soup = BeautifulSoup(model_card_html, features="html.parser")

        results_check_passed, results_values = check.run_check(card_soup)

        assert results_check_passed == check_passed
        assert results_values == values


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


class TestEndToEnd:
    @pytest.mark.parametrize("card", [
        ("""
# Model Card for Sample Model

Some random info...

## Model Details

### Model Description

- **Developed by:** Nima Boscarino
- **Model type:** Yada yada yada
        """)
    ])
    def test_end_to_end_compliance_suite(self, card):
        suite = ComplianceSuite(checks=[
            ModelProviderIdentityCheck(),
            IntendedPurposeCheck(),
        ])

        suite.run(card)
