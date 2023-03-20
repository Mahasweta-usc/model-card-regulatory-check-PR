from compliance_checks.base import ComplianceResult, ComplianceCheck, walk_to_next_heading
from bs4 import BeautifulSoup


class ComputationalRequirementsResult(ComplianceResult):
    name = "Computational Requirements"

    def __init__(
            self,
            requirements: str = None,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.requirements = requirements

    def __eq__(self, other):
        if isinstance(other, ComputationalRequirementsResult):
            if super().__eq__(other):
                try:
                    # TODO: Do I want to do a deep equal?
                    # assert self.requirements == other.requirements
                    return True
                except AssertionError:
                    return False
        else:
            return False

    def to_string(self):
        if self.status:
            return """\
            In order for users to know what kind of hardware and software they need to run a model, a model card \
            should have information about the model's computational requirements. We found some documentation \
            for this in this model card. We look for this by searching for a heading called "Technical Specifications".
            """
        else:
            return """\
            We weren't able to find a section in this model card for the model's computational requirements, but it's \
            easy to add one! You can add the following section to the model card and, once you fill in the \
            `[More Information Needed]` sections, the "Computational Requirements" check should pass 🤗

            ```md
            ## Technical Specifications [optional]
            
            ### Compute Infrastructure
            
            [More Information Needed]
            
            #### Hardware
            
            [More Information Needed]
            
            #### Software
            
            [More Information Needed]
            ```
            """


class ComputationalRequirementsCheck(ComplianceCheck):
    name = "Computational Requirements"

    def run_check(self, card: BeautifulSoup):
        combos = [
            ("h2", "Technical Specifications"),
            ("h2", "Technical Specifications [optional]"),
        ]

        for hX, heading in combos:
            purpose_check = walk_to_next_heading(card, hX, heading)
            if purpose_check:
                return ComputationalRequirementsResult(
                    status=True,
                )

        return ComputationalRequirementsResult()
