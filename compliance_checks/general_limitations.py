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
        return self.limitations


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
            ("h2", "Limitations"),
        ]

        for hX, heading in combos:
            purpose_check = walk_to_next_heading(card, hX, heading)
            if purpose_check:
                return GeneralLimitationsResult(
                    status=True,
                )

        return GeneralLimitationsResult()
