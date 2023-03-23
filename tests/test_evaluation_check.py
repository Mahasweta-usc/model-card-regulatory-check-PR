import pytest

import markdown
from bs4 import BeautifulSoup
from compliance_checks.evaluation import (
    EvaluationCheck, EvaluationResult,
)

empty_template = """\
## Evaluation

<!-- This section describes the evaluation protocols and provides the results. -->

### Testing Data, Factors & Metrics

#### Testing Data

<!-- This should link to a Data Card if possible. -->

[More Information Needed]

#### Factors

<!-- These are the things the evaluation is disaggregating by, e.g., subpopulations or domains. -->

[More Information Needed]

#### Metrics

<!-- These are the evaluation metrics being used, ideally with a description of why. -->

[More Information Needed]

### Results

[More Information Needed]

#### Summary

"""
model_card_template = """\
## Evaluation

Some info...

### Testing Data, Factors & Metrics

#### Testing Data

Some information here

#### Factors

Etc...

#### Metrics

There are some metrics listed out here

### Results

And some results

#### Summary

Summarizing everything up!
"""
albert = """\
# ALBERT Base v2

## Evaluation results

When fine-tuned on downstream tasks, the ALBERT models achieve the following results:
"""
helsinki = """\
### eng-spa

## Benchmarks

| testset               | BLEU  | chr-F |
|-----------------------|-------|-------|
| newssyscomb2009-engspa.eng.spa 	| 31.0 	| 0.583 |
| news-test2008-engspa.eng.spa 	| 29.7 	| 0.564 |
| newstest2009-engspa.eng.spa 	| 30.2 	| 0.578 |
| newstest2010-engspa.eng.spa 	| 36.9 	| 0.620 |
| newstest2011-engspa.eng.spa 	| 38.2 	| 0.619 |
| newstest2012-engspa.eng.spa 	| 39.0 	| 0.625 |
| newstest2013-engspa.eng.spa 	| 35.0 	| 0.598 |
| Tatoeba-test.eng.spa 	| 54.9 	| 0.721 |
"""
phil = """\
## Results

| key | value |
| --- | ----- |
| eval_rouge1 | 42.621 |
| eval_rouge2 | 21.9825 |
| eval_rougeL | 33.034 |
| eval_rougeLsum | 39.6783 |
"""
runway = """\
## Evaluation Results 
Evaluations with different classifier-free guidance scales (1.5, 2.0, 3.0, 4.0,
"""

success_result = EvaluationResult(
    status=True
)


@pytest.mark.parametrize("card", [
    model_card_template,
    albert,
    helsinki,
    phil,
    runway,
])
def test_run_checks(card):
    model_card_html = markdown.markdown(card)
    card_soup = BeautifulSoup(model_card_html, features="html.parser")

    results = EvaluationCheck().run_check(card_soup)

    assert results == success_result


def test_fail_on_empty_template():
    model_card_html = markdown.markdown(empty_template)
    card_soup = BeautifulSoup(model_card_html, features="html.parser")
    results = EvaluationCheck().run_check(card_soup)
    assert results == EvaluationResult()
