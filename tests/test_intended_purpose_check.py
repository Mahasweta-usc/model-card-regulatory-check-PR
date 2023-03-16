import pytest

import markdown
from bs4 import BeautifulSoup
from compliance_checks import (
    IntendedPurposeCheck, IntendedPurposeResult,
)


@pytest.fixture
def intended_purpose_model_card():
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
def bad_intended_purpose_model_card():
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


@pytest.mark.parametrize("check,card,expected", [
    (IntendedPurposeCheck(), "intended_purpose_model_card", IntendedPurposeResult(
        status=True,
        direct_use="Here is some info about direct uses...",
        downstream_use=None,
        out_of_scope_use="Here is some info about out-of-scope uses...",
    )),
    (IntendedPurposeCheck(), "bad_intended_purpose_model_card", IntendedPurposeResult()),
])
def test_run_checks(check, card, expected, request):
    card = request.getfixturevalue(card)

    model_card_html = markdown.markdown(card)
    card_soup = BeautifulSoup(model_card_html, features="html.parser")

    results = check.run_check(card_soup)

    assert results == expected
