import pytest

import markdown
from bs4 import BeautifulSoup
from compliance_checks import (
    GeneralLimitationsCheck, GeneralLimitationsResult,
)


model_card_template = """\
# Model Card for Sample Model

## Bias, Risks, and Limitations

<!-- This section is meant to convey both technical and sociotechnical limitations. -->

Hello world! These are some risks...
"""
albert_base_v2 = """\
# ALBERT Base v2

## Intended uses & limitations
You can use the raw model for either masked language modeling or next sentence prediction, but it's mostly intended to
be fine-tuned on a downstream task.
"""
distilbert_base_cased_distilled_squad = """\
# DistilBERT base cased distilled SQuAD

## Risks, Limitations and Biases

**CONTENT WARNING: Readers should be aware that language generated by this model can be disturbing or offensive to some and can propagate historical and current stereotypes.**

Significant research has explored bias and fairness issues with language models.
"""
gpt2 = """\
# GPT-2

### Limitations and bias

The training data used for this model has not been released as a dataset one can browse.
"""
clip = """\
# Model Card: CLIP

## Limitations

CLIP and our analysis of it have a number of limitations. CLIP currently struggles with respect to certain tasks such as fine grained classification and counting objects.

### Bias and Fairness

We find that the performance of CLIP - and the specific biases it exhibits - can depend significantly on class design and the choices one makes for categories to include and exclude.
"""
runway = """\
# Stable Diffusion v1-5 Model Card

## Limitations and Bias

### Limitations

- The model does not achieve perfect photorealism

### Bias

While the capabilities of image generation models are impressive, they can also reinforce or exacerbate social biases.
"""
distilroberta_base = """\
# Model Card for DistilRoBERTa base

# Bias, Risks, and Limitations

Significant research has explored bias and fairness issues with language models.
"""
bloom = """\
# BLOOM

# Risks and Limitations
*This section identifies foreseeable harms and misunderstandings.*
"""

success_result = GeneralLimitationsResult(
    status=True
)


@pytest.mark.parametrize("card", [
    model_card_template,
    albert_base_v2,
    distilbert_base_cased_distilled_squad,
    gpt2,
    clip,
    runway,
    distilroberta_base,
    bloom,
])
def test_run_checks(card):
    model_card_html = markdown.markdown(card)
    card_soup = BeautifulSoup(model_card_html, features="html.parser")

    results = GeneralLimitationsCheck().run_check(card_soup)

    assert results == success_result
