import pytest

import markdown
from bs4 import BeautifulSoup
from compliance_checks import (
    ComputationalRequirementsCheck, ComputationalRequirementsResult,
)


empty_template = """\
## Technical Specifications [optional]

### Compute Infrastructure

[More Information Needed]

#### Hardware

[More Information Needed]

#### Software

[More Information Needed]
"""
model_card_template = """\
# Model Card for Sample Model

## Technical Specifications

### Compute infrastructure
Jean Zay Public Supercomputer, provided by the French government.

#### Hardware

* 384 A100 80GB GPUs (48 nodes)

#### Software

* Megatron-DeepSpeed ([Github link](https://github.com/bigscience-workshop/Megatron-DeepSpeed))
</details>
"""


success_result = ComputationalRequirementsResult(
    status=True
)


@pytest.mark.parametrize("card", [
    model_card_template,
])
def test_run_checks(card):
    model_card_html = markdown.markdown(card)
    card_soup = BeautifulSoup(model_card_html, features="html.parser")

    results = ComputationalRequirementsCheck().run_check(card_soup)

    assert results == success_result


def test_fail_on_empty_template():
    model_card_html = markdown.markdown(empty_template)
    card_soup = BeautifulSoup(model_card_html, features="html.parser")
    results = ComputationalRequirementsCheck().run_check(card_soup)
    assert results == ComputationalRequirementsResult()
