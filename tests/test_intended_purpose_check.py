import pytest

import markdown
from bs4 import BeautifulSoup
from compliance_checks.intended_purpose import (
    IntendedPurposeCheck, IntendedPurposeResult,
)

empty_template = """\
## Uses

<!-- Address questions around how the model is intended to be used, including the foreseeable users of the model and those affected by the model. -->
[More Information Needed]

### Direct Use

[More Information Needed]

<!-- This section is for the model use without fine-tuning or plugging into a larger ecosystem/app. -->

### Downstream Use [optional]

<!-- This section is for the model use when fine-tuned for a task, or when plugged into a larger ecosystem/app -->

[More Information Needed]

### Out-of-Scope Use

<!-- This section addresses misuse, malicious use, and uses that the model will not work well for. -->
[More Information Needed]
"""
model_card_template = """\
## Uses

Some info...

### Direct Use

Some more info.

### Downstream Use [optional]

[More Information Needed]

### Out-of-Scope Use

Here is some info about out-of-scope uses...
"""
albert_base_v2 = """\
# ALBERT Base v2

## Intended uses & limitations
Here is some info about direct uses...
"""
distilbert_base_cased_distilled_squad = """\
# DistilBERT base cased distilled SQuAD

## Uses

This model can be used for question answering.
"""
distilroberta_base = """\
# Model Card for DistilRoBERTa base

# Uses

You can use the raw model for masked language modeling, but it's mostly intended to be fine-tuned on a downstream task.
"""

clip = """\
# Model Card: CLIP

## Model Use
Stuff.

### Intended Use
Stuff.

#### Primary intended uses
Stuff.

### Out-of-Scope Use Cases
Stuff.
"""

sentence_transformers = """\
# all-MiniLM-L6-v2

## Intended uses

Our model is intented to be used as a sentence and short paragraph encoder.
"""

bloom = """\
# BLOOM  

## Intended Use
This model is being created in order to enable public research on large language models (LLMs).
"""

bleed_over = """\
## Uses
"""

success_result = IntendedPurposeResult(
    status=True
)


@pytest.mark.parametrize("card", [
    model_card_template,
    albert_base_v2,
    distilbert_base_cased_distilled_squad,
    distilroberta_base,
    clip,
    sentence_transformers,
    bloom,
])
def test_run_checks(card):
    model_card_html = markdown.markdown(card)
    card_soup = BeautifulSoup(model_card_html, features="html.parser")

    results = IntendedPurposeCheck().run_check(card_soup)

    assert results == success_result


def test_fail_on_empty_template():
    model_card_html = markdown.markdown(empty_template)
    card_soup = BeautifulSoup(model_card_html, features="html.parser")
    results = IntendedPurposeCheck().run_check(card_soup)
    assert results == IntendedPurposeResult()


def test_fail_on_bleed_over():
    model_card_html = markdown.markdown(bleed_over)
    card_soup = BeautifulSoup(model_card_html, features="html.parser")
    results = IntendedPurposeCheck().run_check(card_soup)
    assert results == IntendedPurposeResult()
