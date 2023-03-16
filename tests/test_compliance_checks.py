import pytest
from unittest.mock import MagicMock

import markdown
from bs4 import BeautifulSoup
from compliance_checks import (
    ComplianceSuite,
    ModelProviderIdentityCheck, ModelProviderIdentityResult,
    IntendedPurposeCheck, IntendedPurposeResult,
    GeneralLimitationsCheck, GeneralLimitationsResult,
    ComputationalRequirementsCheck, ComputationalRequirementsResult,
)


expected_infrastructure = """\
Jean Zay Public Supercomputer, provided by the French government.\
Hardware\
384 A100 80GB GPUs (48 nodes)\
Software\
Megatron-DeepSpeed (Github link)\
"""


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

Here is some info about direct uses...

### Downstream Use [optional]

<!-- This section is for the model use when fine-tuned for a task, or when plugged into a larger ecosystem/app -->

[More Information Needed]

### Out-of-Scope Use

<!-- This section addresses misuse, malicious use, and uses that the model will not work well for. -->

Here is some info about out-of-scope uses...

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

    @pytest.fixture
    def general_limitations_model_card(self):
        return """
# Model Card for Sample Model

## Some Random Header

## Bias, Risks, and Limitations

<!-- This section is meant to convey both technical and sociotechnical limitations. -->

Hello world! These are some risks...

## More Things
        """

    @pytest.fixture
    def bad_general_limitations_model_card(self):
        return """
# Model Card for Sample Model

## Some Random Header

## Bias, Risks, and Limitations

<!-- This section is meant to convey both technical and sociotechnical limitations. -->

[More Information Needed]

## More Things
        """

    @pytest.fixture
    def computational_requirements_model_card(self):
        # Adapted from: https://huggingface.co/bigscience/bloom/blob/main/README.md
        return """
# Model Card for Sample Model

## Some Random Header

## Technical Specifications

### Compute infrastructure
Jean Zay Public Supercomputer, provided by the French government.

#### Hardware

* 384 A100 80GB GPUs (48 nodes)

#### Software

* Megatron-DeepSpeed ([Github link](https://github.com/bigscience-workshop/Megatron-DeepSpeed))
</details>

## Intended Use

Etc..
"""

    @pytest.fixture
    def bad_computational_requirements_model_card(self):
        # Adapted from: https://huggingface.co/bigscience/bloom/blob/main/README.md
        return """
# Model Card for Sample Model

## Some Random Header

## Technical Specifications

### Compute infrastructure
[More Information Needed]

## Intended Use

Etc..
"""

    @pytest.mark.parametrize("check,card,expected", [
        (ModelProviderIdentityCheck(), "provider_identity_model_card", ModelProviderIdentityResult(
            status=True,
            provider="Nima Boscarino",
        )),
        (ModelProviderIdentityCheck(), "bad_provider_identity_model_card", ModelProviderIdentityResult()),
        (IntendedPurposeCheck(), "intended_purpose_model_card", IntendedPurposeResult(
            status=True,
            direct_use="Here is some info about direct uses...",
            downstream_use=None,
            out_of_scope_use="Here is some info about out-of-scope uses...",
        )),
        (IntendedPurposeCheck(), "bad_intended_purpose_model_card", IntendedPurposeResult()),
        (GeneralLimitationsCheck(), "general_limitations_model_card", GeneralLimitationsResult(
            status=True,
            limitations="Hello world! These are some risks..."
        )),
        (GeneralLimitationsCheck(), "bad_general_limitations_model_card", GeneralLimitationsResult()),
        (ComputationalRequirementsCheck(), "computational_requirements_model_card", ComputationalRequirementsResult(
            status=True,
            requirements=expected_infrastructure,
        )),
        (ComputationalRequirementsCheck(), "bad_computational_requirements_model_card", ComputationalRequirementsResult()),
    ])
    def test_run_checks(self, check, card, expected, request):
        card = request.getfixturevalue(card)

        model_card_html = markdown.markdown(card)
        card_soup = BeautifulSoup(model_card_html, features="html.parser")

        results = check.run_check(card_soup)

        assert results == expected


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
