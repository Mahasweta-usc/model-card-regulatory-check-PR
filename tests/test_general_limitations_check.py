import pytest

import markdown
from bs4 import BeautifulSoup
from compliance_checks import (
    GeneralLimitationsCheck, GeneralLimitationsResult,
)


@pytest.fixture
def general_limitations_model_card():
    return """
# Model Card for Sample Model

## Some Random Header

## Bias, Risks, and Limitations

<!-- This section is meant to convey both technical and sociotechnical limitations. -->

Hello world! These are some risks...

## More Things
    """


@pytest.fixture
def bad_general_limitations_model_card():
    return """
# Model Card for Sample Model

## Some Random Header

## Bias, Risks, and Limitations

<!-- This section is meant to convey both technical and sociotechnical limitations. -->

[More Information Needed]

## More Things
    """


@pytest.mark.parametrize("check,card,expected", [
    (GeneralLimitationsCheck(), "general_limitations_model_card", GeneralLimitationsResult(
        status=True,
        limitations="Hello world! These are some risks..."
    )),
    (GeneralLimitationsCheck(), "bad_general_limitations_model_card", GeneralLimitationsResult()),
])
def test_run_checks(check, card, expected, request):
    card = request.getfixturevalue(card)

    model_card_html = markdown.markdown(card)
    card_soup = BeautifulSoup(model_card_html, features="html.parser")

    results = check.run_check(card_soup)

    assert results == expected
