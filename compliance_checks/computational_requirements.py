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
        return self.requirements


class ComputationalRequirementsCheck(ComplianceCheck):
    name = "Computational Requirements"

    def run_check(self, card: BeautifulSoup):
        check = walk_to_next_heading(card, "h2", "Technical Specifications")

        return ComputationalRequirementsResult(
            status=check,
            # requirements=content,
        )
