from compliance_checks.base import ComplianceResult, ComplianceCheck, walk_to_next_heading
from bs4 import BeautifulSoup


class EvaluationResult(ComplianceResult):
    name = "Evaluation and Metrics"

    def __init__(
            self,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)

    def __eq__(self, other):
        if isinstance(other, EvaluationResult):
            if super().__eq__(other):
                try:
                    return True
                except AssertionError:
                    return False
        else:
            return False

    def to_string(self):
        if self.status:
            return """\
            It looks like this model card has some documentation for how the model was evaluated! We look for this by \
            searching for headings that say things like:
            - Evaluation
            - Evaluation results
            - Benchmarks
            - Results
            """
        else:
            return """\
            We weren't able to find a section in this model card that reports the evaluation process, but it's easy to \
            add one! You can add the following section to the model card and, once you fill in the \
            `[More Information Needed]` sections, the "Evaluation and Metrics" check should pass 🤗
            
            ```md
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
            
            [More Information Needed]
            ```
            """


class EvaluationCheck(ComplianceCheck):
    name = "Evaluation and Metrics"

    def run_check(self, card: BeautifulSoup):
        combos = [
            ("h1", "Evaluation"), ("h2", "Evaluation"),
            ("h2", "Evaluation results"), ("h2", "Evaluation Results"),
            ("h2", "Benchmarks"),
            ("h2", "Results"),
        ]

        for hX, heading in combos:
            purpose_check = walk_to_next_heading(card, hX, heading)
            if purpose_check:
                return EvaluationResult(
                    status=True,
                )

        return EvaluationResult()
