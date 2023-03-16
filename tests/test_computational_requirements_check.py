import pytest

import markdown
from bs4 import BeautifulSoup
from compliance_checks import (
    ComputationalRequirementsCheck, ComputationalRequirementsResult,
)


expected_infrastructure = """\
Jean Zay Public Supercomputer, provided by the French government.\
Hardware\
384 A100 80GB GPUs (48 nodes)\
Software\
Megatron-DeepSpeed (Github link)\
"""


@pytest.fixture
def computational_requirements_model_card():
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
def bad_computational_requirements_model_card():
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
    (ComputationalRequirementsCheck(), "computational_requirements_model_card", ComputationalRequirementsResult(
        status=True,
        requirements=expected_infrastructure,
    )),
    (ComputationalRequirementsCheck(), "bad_computational_requirements_model_card", ComputationalRequirementsResult()),
])
def test_run_checks(check, card, expected, request):
    card = request.getfixturevalue(card)

    model_card_html = markdown.markdown(card)
    card_soup = BeautifulSoup(model_card_html, features="html.parser")

    results = check.run_check(card_soup)

    assert results == expected
