from compliance_checks.base import ComplianceResult, ComplianceCheck, walk_to_next_heading
from bs4 import BeautifulSoup


class GeneralLimitationsResult(ComplianceResult):
    name = "General Limitations"

    def __init__(
            self,
            limitations: str = None,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.limitations = limitations

    def __eq__(self, other):
        if isinstance(other, GeneralLimitationsResult):
            if super().__eq__(other):
                try:
                    assert self.limitations == other.limitations
                    return True
                except AssertionError:
                    return False
        else:
            return False

    def to_string(self):
        if self.status:
            return """\
            It's important for model cards to document the model's general limitations! We found some documentation \
            for this in this model card. We look for this by searching for headings that say things like:
            - Bias, Risks, and Limitations
            - Intended uses & limitations
            - Limitations
            """
        else:
            return """\
            We weren't able to find a section in this model card for the model's limitations, but it's easy to \
            add one! You can add the following section to the model card and, once you fill in the \
            `[More Information Needed]` sections, the "General Limitations" check should pass 🤗

            ```md
            ## Bias, Risks, and Limitations
            
            <!-- This section is meant to convey both technical and sociotechnical limitations. -->
            
            [More Information Needed]
            
            ### Recommendations
            
            <!-- This section is meant to convey recommendations with respect to the bias, risk, and technical limitations. -->
            
            Users (both direct and downstream) should be made aware of the risks, biases and limitations of the model. More information needed for further recommendations.
            ```
            """


class GeneralLimitationsCheck(ComplianceCheck):
    name = "General Limitations"

    def run_check(self, card: BeautifulSoup):
        combos = [
            ("h1", "Bias, Risks, and Limitations"), ("h2", "Bias, Risks, and Limitations"),
            ("h2", "Intended uses & limitations"),
            ("h1", "Risks and Limitations"),
            ("h2", "Risks, Limitations and Biases"),
            ("h2", "Limitations and Bias"),
            ("h3", "Limitations and bias"),
            ("h1", "Limitations"), ("h2", "Limitations"),
        ]

        for hX, heading in combos:
            purpose_check = walk_to_next_heading(card, hX, heading)
            if purpose_check:
                return GeneralLimitationsResult(
                    status=True,
                )

        return GeneralLimitationsResult()
